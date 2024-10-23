# Salesforce Case Download Organizer (Windows build)

**Example Configuration**

Create a `config.json` file in the same directory as the `tm_sf_server.exe` executable with the following content:

```json
{
    "no_case_folder": "Other_downloads",
    "downloads_dir": "C:\\Users\\YourUsername\\Downloads",
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
    "default_subfolder": "Other",
    "file_check_interval": 0.5,
    "monitor_interval": 0.5,
    "error_sleep": 5,
    "cleanup_enabled": false,
    "cleanup_age_threshold": "6m",
    "cleanup_interval": "1d"
}
```

**How to Use**

1. **Configure:**
   - Edit the `config.json` file to set your preferences.
     - **`downloads_dir`**: Set this to the path of your Downloads folder.
     - **`server_port`**: Choose a port number for the server (default is 8000).
     - **`rules`**: Define how different file types should be organized.
     - **Cleanup Settings**: Enable and configure file cleanup if desired.

2. **Run the Server Executable:**
   - Ensure both `tm_sf_server.exe` and `config.json` are in the same directory.
   - Double-click `tm_sf_server.exe` to start the server.
   - The console will display an ASCII art logo indicating the server is running.

3. **Shut Down the Server:**
   - In the console window where the server is running, type `q` and press `Enter` to gracefully shut down the server.

Ensure that you have the necessary permissions to read/write in the specified directories and that no other application is using the configured server port.
