#!/bin/bash

# Enable debugging mode (comment this out if not needed)
set -x

# Output JSON files
OUTPUT_FILE="redshift_metadata.json"
TABLES_FILE="redshift_tables.json"

# AWS Region
REGION="us-east-1"

# Check if AWS CLI and jq are installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Install it and try again."
    exit 1
fi
if ! command -v jq &> /dev/null; then
    echo "❌ jq is not installed. Install it using 'sudo apt-get install jq' or 'brew install jq'."
    exit 1
fi

# Function to execute a query and wait for results
execute_query() {
    local query="$1"

    # Execute query and capture the statement ID
    local statement_id=$(aws redshift-data execute-statement \
        --cluster-identifier "$CLUSTER_IDENTIFIER" \
        --database "$DATABASE" \
        --db-user "$DB_USER" \
        --sql "$query" \
        --region "$REGION" \
        --output json | jq -r '.Id')

    if [[ -z "$statement_id" || "$statement_id" == "null" ]]; then
        echo "❌ Failed to execute query: $query"
        exit 1
    fi

    # Wait for the query to complete
    while true; do
        STATUS=$(aws redshift-data describe-statement --id "$statement_id" --region "$REGION" | jq -r '.Status')
        if [[ "$STATUS" == "FINISHED" ]]; then
            break
        elif [[ "$STATUS" == "FAILED" ]]; then
            echo "❌ Query failed: $query"
            exit 1
        fi
        sleep 1
    done

    # Fetch results
    aws redshift-data get-statement-result --id "$statement_id" --region "$REGION"
}

echo "🔎 Checking region: $REGION"

# List Redshift clusters in the region
CLUSTERS=$(aws redshift describe-clusters --region "$REGION" --query "Clusters[].ClusterIdentifier" --output text)

if [[ -z "$CLUSTERS" ]]; then
    echo "❌ No clusters found in region: $REGION"
    exit 1
fi

for CLUSTER in $CLUSTERS; do
    echo "✅ Found cluster: $CLUSTER in region: $REGION"
    
    # Automatically use the first found cluster
    CLUSTER_IDENTIFIER="$CLUSTER"
    
    # Prompt user for database and user
    read -p "Enter the database name for $CLUSTER_IDENTIFIER: " DATABASE
    read -p "Enter the database user for $CLUSTER_IDENTIFIER: " DB_USER

    # Step 1: Count schemas
    SCHEMAS_QUERY="SELECT COUNT(*) FROM information_schema.schemata;"
    SCHEMAS_RESULT=$(execute_query "$SCHEMAS_QUERY")
    SCHEMA_COUNT=$(echo "$SCHEMAS_RESULT" | jq -r '.Records[0][0] | (.longValue // .doubleValue // .stringValue // "0") | tonumber')

    # Step 2: Count tables and distinct schemas
    TABLES_COUNT_QUERY="SELECT COUNT(*), COUNT(DISTINCT table_schema) FROM information_schema.tables WHERE table_type = 'BASE TABLE';"
    TABLES_COUNT_RESULT=$(execute_query "$TABLES_COUNT_QUERY")
    TABLE_COUNT=$(echo "$TABLES_COUNT_RESULT" | jq -r '.Records[0][0] | (.longValue // .doubleValue // .stringValue // "0") | tonumber')
    SCHEMA_TABLE_COUNT=$(echo "$TABLES_COUNT_RESULT" | jq -r '.Records[0][1] | (.longValue // .doubleValue // .stringValue // "0") | tonumber')

    # Step 3: Extract table names in batches
    echo "[" > "$TABLES_FILE"

    OFFSET=0
    LIMIT=1000 # Fetch 1000 tables at a time

    while [[ $OFFSET -lt $TABLE_COUNT ]]; do
        TABLES_QUERY="SELECT table_schema, table_name FROM information_schema.tables WHERE table_type = 'BASE TABLE' ORDER BY table_schema, table_name LIMIT $LIMIT OFFSET $OFFSET;"
        TABLES_RESULT=$(execute_query "$TABLES_QUERY")
        
        TABLES_JSON=$(echo "$TABLES_RESULT" | jq -r '[.Records[] | {"schema": .[0].stringValue, "table": .[1].stringValue}]')

        # Append results to file
        if [[ "$OFFSET" -ne 0 ]]; then
            echo "," >> "$TABLES_FILE"
        fi
        echo "$TABLES_JSON" | jq -r '.[]' >> "$TABLES_FILE"

        OFFSET=$((OFFSET + LIMIT))
    done

    echo "]" >> "$TABLES_FILE"

    # Step 4: Count stored procedures
    STORED_PROCEDURES_QUERY="SELECT COUNT(*) FROM information_schema.routines WHERE routine_type = 'PROCEDURE';"
    STORED_PROCEDURES_RESULT=$(execute_query "$STORED_PROCEDURES_QUERY")
    STORED_PROCEDURES_COUNT=$(echo "$STORED_PROCEDURES_RESULT" | jq -r '.Records[0][0] | tonumber')

    # Step 5: Count views
    VIEWS_QUERY="SELECT COUNT(*) FROM information_schema.views;"
    VIEWS_RESULT=$(execute_query "$VIEWS_QUERY")
    VIEW_COUNT=$(echo "$VIEWS_RESULT" | jq -r '.Records[0][0] | tonumber')

    # Step 6: Count user-defined functions
    FUNCTIONS_QUERY="SELECT COUNT(*) FROM information_schema.routines WHERE routine_type = 'FUNCTION' AND specific_schema NOT IN ('pg_catalog', 'information_schema') AND routine_name NOT LIKE 'aws_%' AND routine_name NOT LIKE '_%';"
    FUNCTIONS_RESULT=$(execute_query "$FUNCTIONS_QUERY")
    FUNCTION_COUNT=$(echo "$FUNCTIONS_RESULT" | jq -r '.Records[0][0] | tonumber')

    # Step 7: Count triggers
    TRIGGERS_QUERY="SELECT COUNT(*) FROM information_schema.triggers;"
    TRIGGERS_RESULT=$(execute_query "$TRIGGERS_QUERY")
    TRIGGER_COUNT=$(echo "$TRIGGERS_RESULT" | jq -r '.Records[0][0] | tonumber')

    echo "📊 Calculating dataset size..."

    # Step 8: Dataset size query
    DATASET_SIZE_QUERY="SELECT COALESCE(pg_size_pretty(SUM(pg_total_relation_size(table_schema || '.' || table_name::text))), '0 bytes') FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog', 'information_schema', 'sys', 'awsdatacatalog');"
    
    DATASET_SIZE_RESULT=$(execute_query "$DATASET_SIZE_QUERY")
    DATASET_SIZE=$(echo "$DATASET_SIZE_RESULT" | jq -r '.Records[0][0] | (.stringValue // "0 bytes")')

    echo "✅ Final dataset size: $DATASET_SIZE"

    # Step 9: Save metadata to JSON
    cat <<EOF >"$OUTPUT_FILE"
{
    "region": "$REGION",
    "cluster_identifier": "$CLUSTER_IDENTIFIER",
    "schema_count": $SCHEMA_COUNT,
    "table_count": $TABLE_COUNT,
    "schema_table_count": $SCHEMA_TABLE_COUNT,
    "stored_procedures_count": $STORED_PROCEDURES_COUNT,
    "views_count": $VIEW_COUNT,
    "functions_count": $FUNCTION_COUNT,
    "triggers_count": $TRIGGER_COUNT,
    "dataset_size": "$DATASET_SIZE",
    "tables_file": "$TABLES_FILE"
}
EOF

    echo "✅ Metadata collected and saved to $OUTPUT_FILE."
    echo "✅ Table names saved to $TABLES_FILE."
    break 
done
