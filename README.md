# Salesforce Case Download Organizer

**Author:** Anton Neledov  

## Overview

The **Salesforce Case Download Organizer** automatically organizes your downloaded files based on active Salesforce cases and associated companies, keeping your Downloads folder tidy and efficient.

## Features

- **Automatic File Monitoring:** Watches your Downloads folder and organizes new files as they arrive.
- **Configurable Rules:** Customize how files are categorized based on their extensions and names.
- **Case-Based Organization:** Sorts files into folders corresponding to your active Salesforce cases and companies.
- **Tampermonkey Integration:** A browser script that communicates active case information to the local server in real-time.
- **Graceful Shutdown:** Ensures the server stops smoothly without disrupting ongoing operations.
- **Robust Logging:** Detailed logs with automatic rotation to help you monitor activities.
- **Cross-Platform Support:** Compatible with Windows, macOS, and Linux.

## How It Works

1. **Tampermonkey Script:** When you view or stop viewing a Salesforce case in your browser, the Tampermonkey script sends the active case number and company name to the local Python server.
2. **Python Server:** Continuously monitors your Downloads directory for new files. Based on the received case information, it organizes downloaded files into appropriate folders following the defined rules.
3. **File Organization:** Files are categorized into subfolders like `Screenshots`, `Documents`, etc., within folders named after the company and case number.

## Installation

### Prerequisites

Ensure you have the following installed on your system:

- **Python 3.6 or higher:** Download from the [official Python website](https://www.python.org/downloads/).
- **Git:** To clone the repository, download it from [here](https://git-scm.com/downloads), or you can download the ZIP file directly from GitHub.
- **Tampermonkey Extension:** Install Tampermonkey in your preferred browser:
  - [Chrome](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
  - [Firefox](https://addons.mozilla.org/firefox/addon/tampermonkey/)
  - [Edge](https://microsoftedge.microsoft.com/addons/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
  - [Safari](https://www.tampermonkey.net/?browser=safari)

### Installation Steps by Operating System

#### Windows

1. **Clone the Repository:**

   Open Command Prompt and run:

   ```bash
   git clone https://github.com/neledov/salesforce-case-download-organizer.git
   ```

   *Alternatively, download the ZIP file from the [GitHub repository](https://github.com/neledov/salesforce-case-download-organizer) and extract it.*

2. **Navigate to the Project Directory:**

   ```bash
   cd salesforce-case-download-organizer
   ```

3. **Set Up the Python Environment:**

   It's a good practice to use a virtual environment to manage dependencies.

   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

4. **Configure the Application:**

   Open the `config.json` file in a text editor and adjust the settings as needed. Refer to the [Configuration](#configuration) section for details.

5. **Run the Server:**

   ```bash
   python server.py
   ```

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

3. **Set Up the Python Environment:**

   It's a good practice to use a virtual environment to manage dependencies.

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Configure the Application:**

   Open the `config.json` file in a text editor and adjust the settings as needed. Refer to the [Configuration](#configuration) section for details.

5. **Run the Server:**

   ```bash
   python server.py
   ```

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

3. **Set Up the Python Environment:**

   It's a good practice to use a virtual environment to manage dependencies.

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. **Configure the Application:**

   Open the `config.json` file in a text editor and adjust the settings as needed. Refer to the [Configuration](#configuration) section for details.

5. **Run the Server:**

   ```bash
   python server.py
   ```

## Configuration

The application uses a `config.json` file to manage settings. Below is an example configuration:

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
    "error_sleep": 5
}
```

### Configuration Parameters

- **`no_case_folder`**: Name of the folder where files without an active case are moved.
- **`downloads_dir`**: Absolute path to your Downloads directory.
- **`server_port`**: Port number on which the server listens (default is `8000`).
- **`rules`**: List of rules to categorize files based on extensions and filename content.
  - **`subfolder`**: Destination subfolder name.
  - **`extensions`**: List of file extensions to match.
  - **`filename_contains`** *(optional)*: List of substrings that must be present in the filename.
- **`default_subfolder`**: Subfolder name used when no rules match.
- **`file_check_interval`**: Time (in seconds) between file size checks to determine if a download is complete.
- **`monitor_interval`**: Time (in seconds) between scans of the Downloads directory.
- **`error_sleep`**: Time (in seconds) to wait before retrying after an error occurs.

### Tips for Configuration

- **Customize Rules:** Modify the `rules` section to fit your file categorization needs. Add or remove rules as necessary.
- **Adjust Intervals:** If you experience performance issues, consider increasing `monitor_interval` and `file_check_interval` to reduce resource usage.
- **Change Port:** Ensure that the `server_port` you choose is not in use by another application.

## Usage

### Setting Up the Python Server

1. **Start the Server:**

   Ensure you've activated your virtual environment and are in the project directory, then run:

   ```bash
   python server.py
   ```

   **Behavior:**
   - **Initial File Move:** On startup, existing files in the `downloads_dir` are moved to the `no_case_folder`.
   - **Server Operation:** The server listens on the specified `server_port` on `localhost` (`127.0.0.1`).
   - **File Monitoring:** Continuously monitors the `downloads_dir` for new files and organizes them based on the current `company_name` and `case_number` received via POST requests.

2. **Monitor Logs:**

   Check the `server.log` file for detailed logs about file movements and server operations.

### Installing the Tampermonkey Script

The **Salesforce Case Number Notifier** is a Tampermonkey script that automatically sends active case information to the local server when you view or stop viewing a Salesforce case.

1. **Install Tampermonkey Extension:**

   If you haven't already, install the Tampermonkey extension in your preferred browser:
   - [Chrome](https://chrome.google.com/webstore/detail/tampermonkey/)
   - [Firefox](https://addons.mozilla.org/firefox/addon/tampermonkey/)
   - [Edge](https://microsoftedge.microsoft.com/addons/detail/tampermonkey/)
   - [Safari](https://www.tampermonkey.net/?browser=safari)

2. **Add the Tampermonkey Script:**

   - **Create a New Script:**
     - Click on the Tampermonkey icon in your browser toolbar.
     - Select **"Create a new script..."** from the dropdown menu.

   - **Copy and Paste the Script:**
     - Open the `tm_sf_listener.js` file located in the project directory.
     - Copy the entire content of `tm_sf_listener.js`.
     - Paste it into the Tampermonkey editor, replacing any existing code.

   - **Save the Script:**
     - Click **"File"** > **"Save"** or press `Ctrl+S` (Windows/Linux) or `Cmd+S` (macOS) to save the script.

3. **Configure the Script (Optional):**

   - By default, the script sends notifications to `http://localhost:8000`, which matches the server's default port.
   - If you changed the server port in `config.json`, update the script's URL accordingly:
     - Open the Tampermonkey dashboard.
     - Find the **Salesforce Case Number Notifier** script and click **"Edit"**.
     - Modify the `url` field in the `GM_xmlhttpRequest` section to match your server's port.

4. **Usage:**

   - **Active Case:**
     - When you view a Salesforce case, the script automatically sends the `case_number` and `company_name` to the local server.
   - **No Active Case:**
     - If you stop viewing a case or navigate away, it sends `'NO_CASE'` and `'NO_COMPANY'` to indicate no active case is being viewed.
   - **File Organization:**
     - The server will organize downloaded files based on the received information, placing them in the appropriate folders.

## Tweaking Recommendations

- **Performance Optimization:**
  - **Monitor Intervals:** Adjust `monitor_interval` and `file_check_interval` in `config.json` to balance responsiveness and resource usage.

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

---

*Thank you for using the Salesforce Case Download Organizer! Your feedback and contributions are highly appreciated.*