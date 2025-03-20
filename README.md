# 🌩️ GCP Calculator

<div align="center">

![GCP Calculator](https://img.shields.io/badge/GCP-Calculator-blue?style=for-the-badge&logo=google-cloud)
[![Python](https://img.shields.io/badge/Python-3.x-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-lightgrey?style=for-the-badge&logo=flask)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

A powerful automation tool for calculating Google Cloud Platform (GCP) pricing across Compute Engine and Cloud SQL services.

</div>

## 📖 Overview

The GCP Calculator is a Flask-based web application that automates the process of retrieving pricing information from Google Cloud Platform's pricing calculator. It supports both Compute Engine and Cloud SQL services, providing detailed pricing comparisons across different commitment terms.

## ✨ Features

### 🖥️ Compute Engine Pricing

- Calculates pricing for:
  - 💰 On-Demand instances
  - 🔄 Sustained Use Discount (SUD)
  - 📅 1-Year commitment
  - 📆 3-Year commitment
- Supports various configurations:
  - 🔧 Multiple machine families
  - ⚙️ Custom machine types
  - 🐧 Different OS options
  - 🌍 Various regions
  - 💾 Storage options
  - 🔄 High availability configurations

### 🗄️ Cloud SQL Pricing

- Calculates pricing for:
  - 📊 Different SQL types (MySQL, PostgreSQL, SQL Server)
  - 🏢 Enterprise and Enterprise Plus editions
  - 💻 Various instance types
  - 🔄 High Availability configurations
  - 💽 Storage options (SSD/HDD)
  - 📦 Backup configurations

### 🎯 Additional Features

- 📊 Automated Google Sheet processing
- 📑 Result export to Excel
- ☁️ Google Drive integration
- 📧 Email notifications
- 👥 Multi-user sharing capabilities

## 📋 Prerequisites

- 🐍 Python 3.x
- 🌐 Google Chrome browser
- 🚗 ChromeDriver
- 🔑 Google Cloud Platform service account credentials

## 📦 Required Python Packages

```bash
selenium==4.16.0
pandas==2.1.4
Flask==3.0.0
beautifulsoup4==4.12.2
google-api-python-client==2.108.0
pyautogui==0.9.54
requests==2.31.0
pyperclip==1.8.2
openpyxl==3.1.2
google-auth==2.23.4
google-auth-oauthlib==1.1.0
google-auth-httplib2==0.1.1
python-dotenv==1.0.0
Werkzeug==3.0.1
urllib3==2.1.0
PyYAML==6.0.1
```

## 🚀 Installation

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

- 📁 Place your Google Cloud service account JSON file in the `assets` directory
- 🔄 Update the service account file path in the code if necessary

## 📂 Project Structure

```
GCP_Calculator/
├── 📁 assets/
│   ├── 📄 index.json
│   ├── 📄 knowledge_base.json
│   └── 🔑 service-account.json
├── 📁 data/
│   └── 📊 (Generated files)
├── 📜 main.py
├── 🌐 index.html
├── 📋 requirements.txt
└── 📖 README.md
```

## 🚀 Usage

1. Start the application:

```bash
python main.py
```

2. Open your web browser and navigate to:

```
http://localhost:5000
```

The application will open with the calculator interface ready to use. You can:

- Enter your Google Sheet URL
- Add email addresses for sharing results
- Click Calculate to start the process

The results will be displayed directly in the interface and shared via email with the specified recipients.

## 📝 Input Sheet Format

### 💻 Compute Engine Tab

Required columns:

- 🖥️ OS with version
- 🔢 No. of Instances
- ⏰ Avg no. of hrs
- 🏭 Machine Family
- 📊 Series
- 💻 Machine Type
- 🔄 vCPUs
- 💾 RAM
- 💿 BootDisk Capacity
- 🌍 Datacenter Location
- 🏷️ Machine Class

### 🗄️ Cloud SQL Tab

Required columns:

- 📊 SQL Type
- 🌍 Datacenter Location
- 🏢 Cloud SQL Edition
- 🔢 No. of Instances
- ⏰ Avg no. of hrs
- 💻 Instance Type
- 🔄 HA/Non-HA
- 💽 Disk Type
- 💾 Storage Amt
- 📦 Backup
- 🔄 vCPUs
- 💾 RAM

## 📤 Output

The tool generates:

1. 📊 Excel files with detailed pricing information
2. 📑 Converts results to Google Sheets
3. 📧 Shares the sheet with specified email addresses
4. 🔗 Returns the Google Sheet URL for accessing results

## ⚠️ Error Handling

- ✅ Validates input data before processing
- 🔍 Handles missing required fields
- ❌ Provides detailed error messages
- 🔄 Continues processing valid rows when encountering errors

## ⚡ Limitations

- 🌐 Requires Chrome browser and ChromeDriver
- 🔄 Depends on Google Cloud Platform's pricing calculator UI
- ⏱️ Processing time increases with number of configurations
- 📊 Rate limits may apply for Google Drive API usage

## 📝 TODO

### Vertical Processing Optimization

- 🚀 Implement parallel processing for multiple instances
- ⚡ Add batch processing for similar configurations
- 🔄 Optimize database queries for vertical scaling
- 📊 Implement queue-based task processing
- 🎯 Add load balancing for multiple requests
- 💾 Implement caching for repeated calculations
- 🔍 Optimize memory usage during processing
- 📈 Add performance monitoring and metrics

### Speed Improvements

- ⚡ Reduce browser automation overhead
- 🔄 Implement asynchronous processing
- 💨 Optimize Selenium operations
- 🚀 Add request pooling for concurrent processing
- ⌛ Reduce API call latency
- 🔧 Optimize data structure usage
- 📊 Implement efficient data caching
- 🎯 Add smart request batching

### Core Improvements

- 🔐 Implement user authentication system
- 🌐 Add support for multiple browsers
- 📊 Add interactive pricing charts
- 📱 Add responsive design for mobile
- 🔒 Enhance security features
- 📦 Create Docker container
- 🤖 Add CI/CD pipeline
- 📚 Add API documentation

### Documentation

- 📖 Add performance tuning guide
- 🎥 Create optimization tutorials
- 📝 Document scaling strategies
- 🔧 Add benchmarking guide
- 📊 Add performance metrics guide
- 💡 Document best practices for large-scale usage

## 🤝 Contributing

1. 🔱 Fork the repository
2. 🌿 Create your feature branch
3. 💾 Commit your changes
4. 🚀 Push to the branch
5. 📬 Create a new Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 💬 Support

For support, please open an issue in the GitHub repository or contact the maintainers.

---

<div align="center">
Made with ❤️ by Srujan Rai
</div>
