# Salesforce Case Download Organizer

A Python script that organizes downloaded files from Salesforce cases into case-specific folders and subfolders based on configurable rules.

## Author

**Anton Neledov**

GitHub: [https://github.com/neledov/salesforce-case-download-organizer](https://github.com/neledov/salesforce-case-download-organizer)

## Description

This script automates the organization of files downloaded from Salesforce cases by:

- Receiving the active case number from a Tampermonkey script.
- Monitoring the Downloads directory for new files.
- Moving files into folders named after the case number.
- Organizing files into subfolders based on file extensions and filename patterns defined in a configuration file.

## Features

- **Configurable Rules**: Define how files are organized using a `config.json` file.
- **Automatic Case Detection**: Uses a Tampermonkey script to detect the active Salesforce case number.
- **No Elevated Privileges Required**: Runs without the need for sudo or administrator privileges.
- **Error Handling**: Robust exception handling to ensure smooth operation.

## Requirements

- Python 3.x
- Tampermonkey extension installed in your browser (Chrome, Firefox, etc.)

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/neledov/salesforce-case-download-organizer.git
   cd salesforce-case-download-organizer
   ```

2. **Set Up a Virtual Environment (Optional but Recommended)**

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   - The script uses only standard Python libraries, so no additional packages are required.

4. **Create Your Configuration File**

   - Copy the example configuration file:

     ```bash
     cp config.json.example config.json
     ```

   - Edit `config.json` to set your `downloads_dir` and customize the rules.

     ```json
     {
       "downloads_dir": "/path/to/your/Downloads",
       "rules": [
         {
           "subfolder": "Screenshots",
           "extensions": [".jpg", ".jpeg", ".png", ".gif"]
         },
         {
           "subfolder": "documents",
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
         }
       ],
       "default_subfolder": "other"
     }
     ```

## Usage

### Running the Python Script

1. **Start the Script**

   ```bash
   python3 tm_sf_server.py
   ```

   Ensure that you replace `tm_sf_server.py` with the actual name of the Python script if different.

2. **Keep the Script Running**

   - The script needs to run in the background to monitor downloads and organize files.

### Setting Up the Tampermonkey Script

1. **Install Tampermonkey Extension**

   - [Chrome Web Store](https://chrome.google.com/webstore/detail/tampermonkey/dhdgffkkebhmkfjojejmpbldmpobfkfo)
   - [Firefox Add-ons](https://addons.mozilla.org/en-US/firefox/addon/tampermonkey/)

2. **Create a New Tampermonkey Script**

   - Open Tampermonkey dashboard.
   - Click on **Create a new script**.

3. **Paste the Tampermonkey Script**

   - Copy the contents of `tm_sf_listener.js` and paste it into the Tampermonkey editor.

4. **Save the Script**

   - Click on **File** > **Save** or press `Ctrl+S`.

### Using the Scripts Together

1. **Start the Python Script**

   - Ensure the Python script `tm_sf_server.py` is running.

2. **Open Salesforce in Your Browser**

   - Navigate to a Salesforce case.

3. **Download Files from Salesforce**

   - Download attachments or files from a case.
   - The Tampermonkey script will send the active case number to the Python script.
   - The Python script will organize the downloaded files into folders based on your configuration.

## Troubleshooting

- **Python Script Errors**

  - Check the console output where the Python script is running for any error messages.
  - Ensure that the `downloads_dir` in your `config.json` is correct and accessible.

- **Tampermonkey Script Issues**

  - Open the browser console (press `F12` or `Ctrl+Shift+I`) to see if any errors are logged.
  - Ensure that the Tampermonkey script is enabled and matches your Salesforce domain in the `@match` directive.

- **Local Server Connection Problems**

  - Ensure that no other application is using port `8000`.
  - If needed, change the port number in both the Python script (`tm_sf_server.py`) and the Tampermonkey script (`tm_sf_listener.js`).

## Contributing

Contributions are welcome! Please open an issue or submit a pull request on GitHub.

## License

This project is licensed under the MIT License.