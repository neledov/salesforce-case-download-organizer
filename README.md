# Salesforce Case Download Organizer

```              
                  +  \\||/
                +  . |||| +
                   + \|||| .
                     \||/
                      JJ
         _________    ||
        /________/|   || 
       /________/ |   || 
      /________/  |   ||
    //|  SCDO  | =====@B  
   // |  0  0  |  |   ||
    \\| \____/ | /        
     @|________|/
         \\    \\                             
        _|_|  _|_| 
        SWEEPING CHAOS 
          SO YOU DON'T HAVE TO!
```

**Author:** Anton Neledov  
**Repository:** [GitHub - neledov/salesforce-case-download-organizer](https://github.com/neledov/salesforce-case-download-organizer)

## Table of Contents

- [Motivation](#motivation)
- [Overview](#overview)
- [Key Features](#key-features)
- [How It Works](#how-it-works)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installation Steps](#installation-steps)
    - [Windows](#windows)
    - [macOS](#macos)
    - [Linux](#linux)
  - [Configuration](#configuration)
- [Usage Recommendations](#usage-recommendations)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Motivation

In many corporate environments, **unpacked browser extensions are not permitted** due to security policies. This restriction makes it challenging to deploy traditional extensions for tasks like organizing Salesforce downloads. To overcome this, the **Salesforce Case Download Organizer (SCDO)** combines a **Tampermonkey userscript** with a **local executable HTTP server**, providing a solution for managing your downloaded files.

## Overview

The **Salesforce Case Download Organizer** (SCDO) automatically organizes your downloaded files based on active Salesforce cases and associated companies. It keeps your downloads folder tidy, ensuring that your files are easily accessible and well-organized without manual intervention.

## Key Features

- **Real-Time Integration:** Sends active Salesforce case information directly from your browser.
- **Automatic File Monitoring:** Continuously watches your Downloads folder and organizes new files instantly.
- **Customizable Rules:** Define how files are categorized based on file types and keywords.
- **Cross-Platform Executables:** Available for both Windows and macOS, eliminating the need for a Python environment.
- **Optional File Cleanup:** Automatically removes old files based on your settings to maintain an organized directory.

## How It Works

```
+---------------------+
| Tampermonkey Script |
+----------+----------+
           |
           | HTTP POST
           |
+----------v----------+
|    Local Server     |
+----------+----------+
           | ^
           | | Disk Operations
           | |
           v |
+----------+----------+
|   Downloads Folder  |                     
+---------------------+
```

1. **Tampermonkey Script:** Captures active Salesforce case details from your browser and sends them to the local executable.
2. **Local Server:** Receives case information, monitors the Downloads folder, and organizes files based on predefined rules.
3. **Cleanup Scheduler (Optional):** Periodically deletes files older than a specified threshold to keep your Downloads folder uncluttered.

## Installation

### Prerequisites

- **Tampermonkey Extension:** Install Tampermonkey in your preferred browser:
  - [Chrome](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
  - [Firefox](https://addons.mozilla.org/firefox/addon/tampermonkey/)
  - [Edge](https://microsoftedge.microsoft.com/addons/detail/tampermonkey/)
  - [Safari](https://www.tampermonkey.net/?browser=safari)

### Installation Steps

#### Windows

1. **Download the Executable:**
   - Visit the [Releases](https://github.com/neledov/salesforce-case-download-organizer/releases) page.
   - Download the latest `tm_sf_server-windows.exe` from the **Assets** section.

2. **Configure the Application:**
   - **Place Files Together:** Ensure `tm_sf_server-windows.exe` and `config.json.example` are in the same folder.
   - **Set Up Configuration:**
     - Copy [`config.json.example`](https://github.com/neledov/salesforce-case-download-organizer/blob/main/config.json.example) and rename the copy to `config.json`.
     - **Edit `config.json`:**
       - Open `config.json` with a text editor like Notepad or Visual Studio Code.
       - Set your Downloads directory path. Example:
         ```json
         "downloads_dir": "C:\\Users\\YourUsername\\Downloads"
         ```

3. **Run the Executable:**
   - Double-click `tm_sf_server-windows.exe`.
   - The console will display an ASCII art logo indicating the server is running.

4. **Install the Tampermonkey Script:**
   - Open Tampermonkey in your browser.
   - Create a new script and paste the contents of `tm_sf_listener.js`.
   - Save the script.

#### macOS

1. **Download the Executable:**
   - Visit the [Releases](https://github.com/neledov/salesforce-case-download-organizer/releases) page.
   - Download the latest `tm_sf_server-mac` from the **Assets** section.

2. **Configure the Application:**
   - **Place Files Together:** Ensure `tm_sf_server-mac` and `config.json.example` are in the same directory.
   - **Set Up Configuration:**
     - Copy [`config.json.example`](https://github.com/neledov/salesforce-case-download-organizer/blob/main/config.json.example) and rename the copy to `config.json`.
     - **Edit `config.json`:**
       - Open `config.json` with a text editor like TextEdit or Visual Studio Code.
       - Set your Downloads directory path. Example:
         ```json
         "downloads_dir": "/Users/YourUsername/Downloads"
         ```

3. **Run the Executable:**
   - Open Terminal and navigate to the executable's directory.
   - Make the file executable if necessary:
     ```bash
     chmod +x tm_sf_server-mac
     ```
   - Run the executable:
     ```bash
     ./tm_sf_server-mac
     ```
   - The console will display an ASCII art logo indicating the server is running.

4. **Install the Tampermonkey Script:**
   - Open Tampermonkey in your browser.
   - Create a new script and paste the contents of `tm_sf_listener.js`.
   - Save the script.

#### Linux

*Note: Pre-built executables for Linux are not provided. Users can run the Python script directly.*

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/neledov/salesforce-case-download-organizer.git
   ```

2. **Navigate to the Project Directory:**
   ```bash
   cd salesforce-case-download-organizer
   ```

3. **Configure the Application:**
   - **Set Up Configuration:**
     - Copy [`config.json.example`](https://github.com/neledov/salesforce-case-download-organizer/blob/main/config.json.example) and rename the copy to `config.json`.
     - **Edit `config.json`:**
       - Open `config.json` with a text editor.
       - Set your Downloads directory path. Example:
         ```json
         "downloads_dir": "/home/YourUsername/Downloads"
         ```

4. **Run the Server:**
   ```bash
   python tm_sf_server.py
   ```
   - The console will display an ASCII art logo indicating the server is running.

5. **Install the Tampermonkey Script:**
   - Open Tampermonkey in your browser.
   - Create a new script and paste the contents of `tm_sf_listener.js`.
   - Save the script.

## Usage Recommendations

- **Keep the Salesforce Case Tab Active:**  
  Ensure you're on the active Salesforce case tab while downloading files to allow accurate association.

## Troubleshooting

**Server Doesn't Start:**  
Check the `server.log` file for any error messages to identify issues. Ensure that the configured port is not being used by another application and verify that all paths and settings in `config.json` are correct.

**Files Not Organizing:**  
Make sure the Tampermonkey script is active and properly configured. Confirm that you are on an active Salesforce case tab when downloading files. Additionally, review your file organization rules to ensure they match the types and naming conventions of your downloaded files.

**Cleanup Not Working:**  
Ensure that `"cleanup_enabled": true` is set in `config.json`. Verify that the `"cleanup_age_threshold"` and `"cleanup_interval"` values are appropriately configured. Check the `server.log` for any errors related to the cleanup process.

## Contributing

We welcome your contributions! To get started:

1. **Fork the Repository:**  
   Click the "Fork" button on the repository page to create your own copy.

2. **Clone Your Fork:**
   ```bash
   git clone https://github.com/your-username/salesforce-case-download-organizer.git
   ```

3. **Create a New Branch:**
   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes:**  
   Implement your feature or fix bugs.

5. **Commit Your Changes:**
   ```bash
   git add .
   git commit -m "Add feature: YourFeatureName"
   ```

6. **Push to Your Fork:**
   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Open a Pull Request:**  
   Go to the original repository and open a pull request detailing your changes.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). You're free to use and modify it as needed.

## Contact

For questions or support, please visit the [GitHub Issues](https://github.com/neledov/salesforce-case-download-organizer/issues) page of the repository.  
Fellow colleagues can reach out via Slack!

---

*Thank you for using the Salesforce Case Download Organizer! Your feedback and contributions are highly appreciated.*