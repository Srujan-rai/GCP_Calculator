# GCP Calculator

A powerful automation tool for calculating Google Cloud Platform (GCP) pricing across Compute Engine and Cloud SQL services.

## Overview

The GCP Calculator is a Flask-based web application that automates the process of retrieving pricing information from Google Cloud Platform's pricing calculator. It supports both Compute Engine and Cloud SQL services, providing detailed pricing comparisons across different commitment terms.

## Features

### Compute Engine Pricing

- Calculates pricing for:
  - On-Demand instances
  - Sustained Use Discount (SUD)
  - 1-Year commitment
  - 3-Year commitment
- Supports various configurations:
  - Multiple machine families
  - Custom machine types
  - Different OS options
  - Various regions
  - Storage options
  - High availability configurations

### Cloud SQL Pricing

- Calculates pricing for:
  - Different SQL types (MySQL, PostgreSQL, SQL Server)
  - Enterprise and Enterprise Plus editions
  - Various instance types
  - High Availability configurations
  - Storage options (SSD/HDD)
  - Backup configurations

### Additional Features

- Automated Google Sheet processing
- Result export to Excel
- Google Drive integration
- Email notifications
- Multi-user sharing capabilities

## Prerequisites

- Python 3.x
- Google Chrome browser
- ChromeDriver
- Google Cloud Platform service account credentials

## Required Python Packages

```bash
selenium==4.x.x
pandas==1.x.x
Flask==2.x.x
beautifulsoup4==4.x.x
google-api-python-client==2.x.x
pyautogui==0.x.x
```

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Srujan-rai/GCP_Calculator.git
cd GCP_Calculator
```

2. Install required packages:

```bash
pip install -r requirements.txt
```

3. Set up service account:

- Place your Google Cloud service account JSON file in the `assets` directory
- Update the service account file path in the code if necessary

## Project Structure

```
GCP_Calculator/
├── assets/
│   ├── index.json
│   ├── knowledge_base.json
│   └── service-account.json
├── data/
│   └── (Generated files)
├── main.py
├── index.html
├── requirements.txt
└── README.md
```

## Usage

1. Start the Flask server:

```bash
python main.py
```

2. Open the web interface:

```bash
# Open index.html in your web browser
# You can do this by double-clicking the file or using the following command:
open index.html  # On macOS
xdg-open index.html  # On Linux
start index.html  # On Windows
```

3. Using the Web Interface:

- Enter the Google Sheet URL containing your configuration
- Add email addresses for sharing results
- Click "Calculate" to start the process
- Wait for the process to complete and receive the results

4. Alternative: API Usage
   Make a POST request to `/calculate` endpoint with:
   - `sheet`: Google Sheet URL containing configuration details
   - `emails[]`: List of email addresses for sharing results

Example curl request:

```bash
curl -X POST http://localhost:5000/calculate \
  -F "sheet=https://docs.google.com/spreadsheets/d/your-sheet-id" \
  -F "emails[]=user1@example.com" \
  -F "emails[]=user2@example.com"
```

## Input Sheet Format

### Compute Engine Tab

Required columns:

- OS with version
- No. of Instances
- Avg no. of hrs
- Machine Family
- Series
- Machine Type
- vCPUs
- RAM
- BootDisk Capacity
- Datacenter Location
- Machine Class

### Cloud SQL Tab

Required columns:

- SQL Type
- Datacenter Location
- Cloud SQL Edition
- No. of Instances
- Avg no. of hrs
- Instance Type
- HA/Non-HA
- Disk Type
- Storage Amt
- Backup
- vCPUs
- RAM

## Output

The tool generates:

1. Excel files with detailed pricing information
2. Converts results to Google Sheets
3. Shares the sheet with specified email addresses
4. Returns the Google Sheet URL for accessing results

## Error Handling

- Validates input data before processing
- Handles missing required fields
- Provides detailed error messages
- Continues processing valid rows when encountering errors

## Limitations

- Requires Chrome browser and ChromeDriver
- Depends on Google Cloud Platform's pricing calculator UI
- Processing time increases with number of configurations
- Rate limits may apply for Google Drive API usage

## Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers.
