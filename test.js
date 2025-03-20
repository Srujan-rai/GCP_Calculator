// Function to fetch HubSpot deal details using OAuth2 Bearer token
function getHubSpotDealDetails(dealId, accessToken) {
    try {
      const url = `https://api.hubapi.com/crm/v3/objects/deals/${dealId}`;
  
      const response = UrlFetchApp.fetch(url, {
        method: "get",
        headers: {
          "Authorization": `Bearer ${accessToken}`  // Use OAuth2 Bearer token
        }
      });
  
      const dealData = JSON.parse(response.getContentText());
      console.log(dealData);
  
      if (dealData.properties) {
        const pipelineId = dealData.properties.pipeline;  // The pipeline ID associated with the deal
        const dealStageId = dealData.properties.dealstage;  // The numeric deal stage ID
  
        // Fetch deal stages for the pipeline and map the deal stage ID to stage name
        const dealStageName = getDealStageName(pipelineId, dealStageId, accessToken);
  
        // Add the deal stage name to the properties
        dealData.properties.dealstage = dealStageName;
      }
  
      return dealData;
  
    } catch (err) {
      console.error("Failed to fetch HubSpot deal details:", err.message);
      return null;
    }
  }
  
  // Function to get the deal stage name by ID
  function getDealStageName(pipelineId, dealStageId, accessToken) {
    try {
      // Fetch the stages for the specified pipeline
      const url = `https://api.hubapi.com/crm/v3/pipelines/deals/${pipelineId}/stages`;
  
      const response = UrlFetchApp.fetch(url, {
        method: "get",
        headers: {
          "Authorization": `Bearer ${accessToken}`
        }
      });
  
      const stagesData = JSON.parse(response.getContentText());
  
      // Find the stage name that matches the deal stage ID
      const stage = stagesData.results.find(stage => stage.id === dealStageId);
      
      if (stage) {
        return stage.label;  // Return the stage name (label)
      }
  
      return "Unknown Stage";  // Return a default value if stage is not found
  
    } catch (err) {
      console.error("Failed to fetch deal stages:", err.message);
      return "Unknown Stage";  // Default value in case of error
    }
  }
  