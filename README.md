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
**Repository:** [https://github.com/neledov/salesforce-case-download-organizer](https://github.com/neledov/salesforce-case-download-organizer)

## Table of Contents

- [Motivation](#motivation)
- [Overview](#overview)
- [Features](#features)
- [How It Works](#how-it-works)
- [Component Descriptions](#component-descriptions)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Installation Steps by Operating System](#installation-steps-by-operating-system)
    - [Windows](#windows)
    - [macOS](#macos)
    - [Linux](#linux)
- [Configuration](#configuration)
- [Usage Recommendations](#usage-recommendations)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Motivation

This application was developed in response to the **ban of unpacked browser extensions on corporate browsers**. Due to these restrictions, traditional browser extensions could not be deployed to facilitate seamless communication between Salesforce and the local file system. As a solution:

- **Tampermonkey** was chosen as the user agent because it allows the creation and deployment of user scripts within corporate browsers without requiring unpacked extensions.
- **Python** was selected as the server base for its cross-platform compatibility, robust file handling capabilities, and ease of integration with existing systems.

## Overview

The **Salesforce Case Download Organizer** (SCDO) automatically organizes your downloaded files based on active Salesforce cases and associated companies, keeping your Downloads folder tidy and efficient.

## Features

- **Tampermonkey Integration:** A browser script that communicates active case information to the local server in real-time.
- **Automatic File Monitoring:** Watches your Downloads folder and organizes new files as they arrive.
- **Configurable Rules:** Customize how files are categorized based on their extensions and names.
- **Case-Based Organization:** Sorts files into folders corresponding to your active Salesforce cases and companies.
- **File Cleanup:** Automatically removes old files based on configurable age thresholds (e.g., 1 month, 1 year).
- **Enable/Disable Cleanup:** Control the file cleanup feature through configuration settings.
- **Cross-Platform Support:** Compatible with Windows, macOS, and Linux.

## How It Works

```
+---------------------+          HTTP POST (Port 8000)          +---------------------+
| Tampermonkey Script | --------------------------------------->| Local Python Server |
| (Browser Extension) |                                         |  (Listening on      |
+---------------------+                                         |   Port 8000)        |
                                                                +---------------------+
                                                                          |
                                                                          | Disk Operations
                                                                          v
                                                                +---------------------+
                                                                |  Downloads Folder   |
                                                                |  (File Organization)|
                                                                +---------------------+
                                                                          |
                                                                          | File Cleanup
                                                                          v
                                                                +---------------------+
                                                                |  Cleanup Scheduler  |
                                                                |  (Optional Feature) |
                                                                +---------------------+
```

### Component Descriptions

1. **Tampermonkey Script (Browser Extension):**
   - **Function:** Detects when you view or stop viewing a Salesforce case in your browser.
   - **Operation:** Captures the active case number and company name from the Salesforce Lightning interface and sends this information to the Python server via an HTTP POST request on port `8000`.

2. **Local Python Server (Listening on Port 8000):**
   - **Function:** Receives case information from the Tampermonkey script.
   - **Operation:** Monitors the Downloads directory for new files. Based on the received case data and predefined rules, it organizes incoming files into the appropriate folders.

3. **File Cleanup Scheduler (Optional Feature):**
   - **Function:** Periodically scans the Downloads directory to remove files older than a specified age threshold.
   - **Operation:** Deletes files that exceed the configured age (e.g., files older than 6 months) to maintain disk space and reduce clutter.
   - **Configurable:** Can be enabled or disabled via `config.json`.

## Installation

### Prerequisites

Ensure you have the following installed on your system:

- **Python 3.6 or higher:** Download from the [official Python website](https://www.python.org/downloads/).
- **Git:** To clone the repository, download it from [here](https://git-scm.com/downloads), or you can download the ZIP file directly from GitHub.
- **Tampermonkey Extension:** Install Tampermonkey in your preferred browser:
  - [Chrome](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
  - [Firefox](https://addons.mozilla.org/firefox/addon/tampermonkey/)
  - [Edge](https://microsoftedge.microsoft.com/addons/detail/tampermonkey/)
  - [Safari](https://www.tampermonkey.net/?browser=safari)

### Installation Steps by Operating System

#### Windows

1. **Clone the Repository with VSCode:**

   - **Open Visual Studio Code (VSCode):**
     - If you don't have VSCode installed, download it from the [official website](https://code.visualstudio.com/).

   - **Clone the Repository:**
     - Click on the **"Source Control"** icon in the sidebar or press `Ctrl+Shift+G`.
     - Click on **"Clone Repository"**.
     - Enter the repository URL: `https://github.com/neledov/salesforce-case-download-organizer.git`
     - Choose a local directory where you want to clone the repository.
     - After cloning, open the repository folder in VSCode.

2. **Configure the Application:**

   - **Rename Configuration File:**
     - In the cloned repository, locate the `config.json.example` file.
     - Rename it to `config.json`.

   - **Edit `config.json`:**
     - Open the `config.json` file in VSCode.
     - **Important:** Provide the absolute path to your Downloads directory in the `downloads_dir` field. This configuration is mandatory for the organizer to function correctly.
     - **Enable File Cleanup (Optional):** Set `cleanup_enabled` to `true` and specify `cleanup_age_threshold` as desired (e.g., `"6m"` for six months).

     ```json
     {
         "no_case_folder": "Other_downloads",
         "downloads_dir": "C:/Users/YourUsername/Downloads",
         "server_port": 8000,
         "rules": [
             {
                 "subfolder": "Screenshots",
                 "extensions": [".jpg", ".jpeg", ".png", ".gif"]
             },
             {
                 "subfolder": "Documents",
                 "extensions": [".pdf", ".docx", ".txt"],
                 "filename_contains": ["report", "summary"]
             },
             {
                 "subfolder": "Logs",
                 "extensions": [".zip", ".tar", ".gz"],
                 "filename_contains": ["log"]
             },
             {
                 "subfolder": "Scripts",
                 "extensions": [".py", ".sh"],
                 "filename_contains": ["script", "run"]
             },
             {
                 "subfolder": "Playbooks",
                 "extensions": [".yml"]
             },
             {
                 "subfolder": "HAR",
                 "extensions": [".har"]
             }
         ],
         "default_subfolder": "other",
         "file_check_interval": 0.5,
         "monitor_interval": 0.5,
         "error_sleep": 5,
         "cleanup_enabled": true,
         "cleanup_age_threshold": "6m",
         "cleanup_interval": "1d"
     }
     ```

3. **Run the Python Server:**

   - Open the integrated terminal in VSCode by clicking **"Terminal"** > **"New Terminal"** or pressing `` Ctrl+` ``.
   - Ensure you're in the project directory.
   - Run the server script:

     ```bash
     python tm_sf_server.py
     ```

4. **Install the Tampermonkey Script:**

   - **Create a New Script:**
     - Click on the Tampermonkey icon in your browser toolbar.
     - Select **"Create a new script..."** from the dropdown menu.

   - **Copy and Paste the Script:**
     - Open the `tm_sf_listener.js` file located in the project directory using VSCode.
     - Copy the entire content of `tm_sf_listener.js`.
     - Paste it into the Tampermonkey editor, replacing any existing code.

   - **Save the Script:**
     - Click **"File"** > **"Save"** or press `Ctrl+S` to save the script.

   - **Configure the Script (Optional):**
     - By default, the script sends notifications to `http://localhost:8000`, which matches the server's default port.
     - If you changed the server port in `config.json`, update the script's URL accordingly:
       - Open the Tampermonkey dashboard.
       - Find the **Salesforce Case Number Notifier** script and click **"Edit"**.
       - Modify the `url` field in the `GM_xmlhttpRequest` section to match your server's port.

   - **Note:** It may take some time for the Tampermonkey script to intercept the URL and launch on the page. If you encounter issues, try refreshing the Salesforce Lightning tab or restarting your browser.

#### macOS

1. **Clone the Repository:**

   Open Terminal and run:

   ```bash
   git clone https://github.com/neledov/salesforce-case-download-organizer.git
   ```

   *Alternatively, download the ZIP file from the [GitHub repository](https://github.com/neledov/salesforce-case-download-organizer) and extract it.*

2. **Navigate to the Project Directory:**

   ```bash
   cd salesforce-case-download-organizer
   ```

3. **Configure the Application:**

   - **Rename Configuration File:**
     - Locate the `config.json.example` file in the repository.
     - Rename it to `config.json`.

   - **Edit `config.json`:**
     - Open the `config.json` file in your preferred text editor.
     - **Important:** Provide the absolute path to your Downloads directory in the `downloads_dir` field.
     - **Enable File Cleanup (Optional):** Set `cleanup_enabled` to `true` and specify `cleanup_age_threshold` as desired (e.g., `"6m"` for six months).

     ```json
     {
         "no_case_folder": "Other_downloads",
         "downloads_dir": "/Users/YourUsername/Downloads",
         "server_port": 8000,
         "rules": [
             {
                 "subfolder": "Screenshots",
                 "extensions": [".jpg", ".jpeg", ".png", ".gif"]
             },
             {
                 "subfolder": "Documents",
                 "extensions": [".pdf", ".docx", ".txt"],
                 "filename_contains": ["report", "summary"]
             },
             {
                 "subfolder": "Logs",
                 "extensions": [".zip", ".tar", ".gz"],
                 "filename_contains": ["log"]
             },
             {
                 "subfolder": "Scripts",
                 "extensions": [".py", ".sh"],
                 "filename_contains": ["script", "run"]
             },
             {
                 "subfolder": "Playbooks",
                 "extensions": [".yml"]
             },
             {
                 "subfolder": "HAR",
                 "extensions": [".har"]
             }
         ],
         "default_subfolder": "other",
         "file_check_interval": 0.5,
         "monitor_interval": 0.5,
         "error_sleep": 5,
         "cleanup_enabled": true,
         "cleanup_age_threshold": "6m",
         "cleanup_interval": "1d"
     }
     ```

4. **Run the Python Server:**

   ```bash
   python tm_sf_server.py
   ```

5. **Install the Tampermonkey Script:**

   - **Create a New Script:**
     - Click on the Tampermonkey icon in your browser toolbar.
     - Select **"Create a new script..."** from the dropdown menu.

   - **Copy and Paste the Script:**
     - Open the `tm_sf_listener.js` file located in the project directory using your text editor.
     - Copy the entire content of `tm_sf_listener.js`.
     - Paste it into the Tampermonkey editor, replacing any existing code.

   - **Save the Script:**
     - Click **"File"** > **"Save"** or press `Cmd+S` to save the script.

   - **Configure the Script (Optional):**
     - By default, the script sends notifications to `http://localhost:8000`, which matches the server's default port.
     - If you changed the server port in `config.json`, update the script's URL accordingly:
       - Open the Tampermonkey dashboard.
       - Find the **Salesforce Case Number Notifier** script and click **"Edit"**.
       - Modify the `url` field in the `GM_xmlhttpRequest` section to match your server's port.

   - **Note:** It may take some time for the Tampermonkey script to intercept the URL and launch on the page. If you encounter issues, try refreshing the Salesforce Lightning tab or restarting your browser.

#### Linux

1. **Clone the Repository:**

   Open Terminal and run:

   ```bash
   git clone https://github.com/neledov/salesforce-case-download-organizer.git
   ```

   *Alternatively, download the ZIP file from the [GitHub repository](https://github.com/neledov/salesforce-case-download-organizer) and extract it.*

2. **Navigate to the Project Directory:**

   ```bash
   cd salesforce-case-download-organizer
   ```

3. **Configure the Application:**

   - **Rename Configuration File:**
     - Locate the `config.json.example` file in the repository.
     - Rename it to `config.json`.

   - **Edit `config.json`:**
     - Open the `config.json` file in your preferred text editor.
     - **Important:** Provide the absolute path to your Downloads directory in the `downloads_dir` field.
     - **Enable File Cleanup (Optional):** Set `cleanup_enabled` to `true` and specify `cleanup_age_threshold` as desired (e.g., `"6m"` for six months).

     ```json
     {
         "no_case_folder": "Other_downloads",
         "downloads_dir": "/home/YourUsername/Downloads",
         "server_port": 8000,
         "rules": [
             {
                 "subfolder": "Screenshots",
                 "extensions": [".jpg", ".jpeg", ".png", ".gif"]
             },
             {
                 "subfolder": "Documents",
                 "extensions": [".pdf", ".docx", ".txt"],
                 "filename_contains": ["report", "summary"]
             },
             {
                 "subfolder": "Logs",
                 "extensions": [".zip", ".tar", ".gz"],
                 "filename_contains": ["log"]
             },
             {
                 "subfolder": "Scripts",
                 "extensions": [".py", ".sh"],
                 "filename_contains": ["script", "run"]
             },
             {
                 "subfolder": "Playbooks",
                 "extensions": [".yml"]
             },
             {
                 "subfolder": "HAR",
                 "extensions": [".har"]
             }
         ],
         "default_subfolder": "other",
         "file_check_interval": 0.5,
         "monitor_interval": 0.5,
         "error_sleep": 5,
         "cleanup_enabled": true,
         "cleanup_age_threshold": "6m",
         "cleanup_interval": "1d"
     }
     ```

4. **Run the Python Server:**

   ```bash
   python tm_sf_server.py
   ```

5. **Install the Tampermonkey Script:**

   - **Create a New Script:**
     - Click on the Tampermonkey icon in your browser toolbar.
     - Select **"Create a new script..."** from the dropdown menu.

   - **Copy and Paste the Script:**
     - Open the `tm_sf_listener.js` file located in the project directory using your text editor.
     - Copy the entire content of `tm_sf_listener.js`.
     - Paste it into the Tampermonkey editor, replacing any existing code.

   - **Save the Script:**
     - Click **"File"** > **"Save"** or press `Ctrl+S` to save the script.

   - **Configure the Script (Optional):**
     - By default, the script sends notifications to `http://localhost:8000`, which matches the server's default port.
     - If you changed the server port in `config.json`, update the script's URL accordingly:
       - Open the Tampermonkey dashboard.
       - Find the **Salesforce Case Number Notifier** script and click **"Edit"**.
       - Modify the `url` field in the `GM_xmlhttpRequest` section to match your server's port.

   - **Note:** It may take some time for the Tampermonkey script to intercept the URL and launch on the page. If you encounter issues, try refreshing the Salesforce Lightning tab or restarting your browser.

## Configuration

The application uses a `config.json` file to manage settings. Since the repository includes `config.json.example`, you need to rename and configure it accordingly.

### Configuration Steps

1. **Rename Configuration File:**

   - Locate the `config.json.example` file in the cloned repository.
   - Rename it to `config.json`.

2. **Edit `config.json`:**

   - Open the `config.json` file in your preferred text editor.
   - **Important:** Provide the absolute path to your Downloads directory in the `downloads_dir` field. This configuration is mandatory for the organizer to function correctly.
   - **Enable File Cleanup (Optional):** To activate the file cleanup feature, set `cleanup_enabled` to `true` and define appropriate `cleanup_age_threshold` and `cleanup_interval`.

   ```json
   {
       "no_case_folder": "Other_downloads",
       "downloads_dir": "/path/to/your/Downloads",
       "server_port": 8000,
       "rules": [
           {
               "subfolder": "Screenshots",
               "extensions": [".jpg", ".jpeg", ".png", ".gif"]
           },
           {
               "subfolder": "Documents",
               "extensions": [".pdf", ".docx", ".txt"],
               "filename_contains": ["report", "summary"]
           },
           {
               "subfolder": "Logs",
               "extensions": [".zip", ".tar", ".gz"],
               "filename_contains": ["log"]
           },
           {
               "subfolder": "Scripts",
               "extensions": [".py", ".sh"],
               "filename_contains": ["script", "run"]
           },
           {
               "subfolder": "Playbooks",
               "extensions": [".yml"]
           },
           {
               "subfolder": "HAR",
               "extensions": [".har"]
           }
       ],
       "default_subfolder": "other",
       "file_check_interval": 0.5,
       "monitor_interval": 0.5,
       "error_sleep": 5,
       "cleanup_enabled": true,
       "cleanup_age_threshold": "6m",
       "cleanup_interval": "1d"
   }
   ```

### Configuration Parameters

- **`no_case_folder`**: Name of the folder where files without an active case are moved.
- **`downloads_dir`**: **Absolute path to your Downloads directory.**  
  **Important for Windows:** Ensure you provide the full path (e.g., `C:/Users/YourUsername/Downloads`). This is a mandatory configuration.
- **`server_port`**: Port number on which the server listens (default is `8000`).
- **`rules`**: List of rules to categorize files based on extensions and filename content.
  - **`subfolder`**: Destination subfolder name.
  - **`extensions`**: List of file extensions to match.
  - **`filename_contains`** *(optional)*: List of substrings that must be present in the filename.
- **`default_subfolder`**: Subfolder name used when no rules match.
- **`file_check_interval`**: Time (in seconds) between file size checks to determine if a download is complete.
- **`monitor_interval`**: Time (in seconds) between scans of the Downloads directory.
- **`error_sleep`**: Time (in seconds) to wait before retrying after an error occurs.
- **`cleanup_enabled`**: *(Boolean)* Enable (`true`) or disable (`false`) the file cleanup feature.
- **`cleanup_age_threshold`**: *(String)* Specifies the age threshold for deleting files. Format examples: `"1m"` (1 month), `"6m"` (6 months), `"1y"` (1 year).
- **`cleanup_interval`**: *(String)* Defines how often the cleanup process should run. Format examples: `"1d"` (1 day), `"12h"` (12 hours).  
  **Note:** If `cleanup_interval` is not set, cleanup runs only once at startup.

### Tips for Configuration

- **Customize Rules:** Modify the `rules` section to fit your file categorization needs. Add or remove rules as necessary.
- **Adjust Intervals:** If you experience performance issues, consider increasing `monitor_interval` and `file_check_interval` to reduce resource usage.
- **Change Port:** Ensure that the `server_port` you choose is not in use by another application.
- **Enable Cleanup:** To activate automatic file cleanup, set `cleanup_enabled` to `true` and define appropriate `cleanup_age_threshold` and `cleanup_interval`.

## Usage Recommendations

- **Stay on Active Case Tab During Downloads:**  
  To ensure that files are correctly associated with the active Salesforce case, it's recommended to keep the Salesforce case tab active in your browser until all relevant downloads have completed. This allows the Tampermonkey script to accurately capture and send the active case information to the Python server.

## Contributing

Contributions are welcome! If you'd like to contribute to the Salesforce Case Download Organizer, please follow these steps:

1. **Fork the Repository:**

   Click the "Fork" button at the top right of the repository page to create your own copy.

2. **Clone Your Fork:**

   ```bash
   git clone https://github.com/your-username/salesforce-case-download-organizer.git
   ```

3. **Create a New Branch:**

   ```bash
   git checkout -b feature/YourFeatureName
   ```

4. **Make Your Changes:**

   Implement your feature or fix.

5. **Commit Your Changes:**

   ```bash
   git commit -m "Add feature: YourFeatureName"
   ```

6. **Push to Your Fork:**

   ```bash
   git push origin feature/YourFeatureName
   ```

7. **Open a Pull Request:**

   Navigate to the original repository and open a pull request describing your changes.

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). Feel free to use and modify it as needed.

## Contact

For any questions or support, please reach out through the [GitHub Issues](https://github.com/neledov/salesforce-case-download-organizer/issues) page of the repository.
If you are my fellow colleagues - please reach out to me via Slack :)
---

*Thank you for using the Salesforce Case Download Organizer! Your feedback and contributions are highly appreciated.*