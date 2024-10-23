import http.server
import socketserver
import threading
import json
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any
import re
import signal
from logging.handlers import RotatingFileHandler
import datetime
import os
import sys

# ----------------------------- ASCII Art -----------------------------

ASCII_ART = r"""
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
"""

# ----------------------------- Configuration -----------------------------

CONFIG_FILE = 'config.json'  # Path to the configuration file

# Default configuration values
DEFAULT_CONFIG: Dict[str, Any] = {
    "no_case_folder": "Other_downloads",
    "downloads_dir": "/Users/aneledov/Downloads",
    "server_port": 8000,
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
    "cleanup_enabled": False,
    "cleanup_age_threshold": "6m",
    "cleanup_interval": "1d"  # Optional: Clean up every day
}

# ----------------------------- Logging Setup -----------------------------

# Create a rotating file handler
log_handler = RotatingFileHandler('server.log', maxBytes=5*1024*1024, backupCount=2)
log_formatter = logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s')
log_handler.setFormatter(log_formatter)
log_handler.setLevel(logging.INFO)

# Configure the root logger
logging.basicConfig(level=logging.INFO, handlers=[log_handler])

# ----------------------------- Global State -------------------------------

current_company_name: Optional[str] = None
current_case_number: Optional[str] = None
config: Dict[str, Any] = {}
DOWNLOADS_DIR = Path()
NO_CASE_FOLDER = ''
DEFAULT_SUBFOLDER = ''
file_assignments: Dict[str, Optional[tuple]] = {}
assignments_lock = threading.Lock()

FILE_CHECK_INTERVAL = 0.5  # Default: 0.5 seconds
MONITOR_INTERVAL = 0.5     # Default: 0.5 seconds
ERROR_SLEEP = 5            # Default: 5 seconds
PORT = 8000                # Default port
CLEANUP_ENABLED = False
CLEANUP_AGE_THRESHOLD = "6m"
CLEANUP_INTERVAL = "1d"    # Optional

# ----------------------------- Utility Functions --------------------------

def sanitize_filename(name: str) -> str:
    """
    Sanitize the folder name to prevent filesystem issues.
    Removes or replaces characters that are invalid in folder names.
    """
    # Replace any character that is not alphanumeric, space, hyphen, or underscore
    sanitized = re.sub(r'[<>:"/\\|?*]', '_', name)
    sanitized = sanitized.strip()
    # Replace multiple spaces or underscores with a single underscore
    sanitized = re.sub(r'[_\s]+', '_', sanitized)
    # Truncate to a reasonable length (e.g., 255 characters)
    sanitized = sanitized[:255]
    # Prevent reserved names (example for Windows)
    reserved_names = {"CON", "PRN", "AUX", "NUL",
                      "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
                      "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9"}
    if sanitized.upper() in reserved_names:
        sanitized = f"{sanitized}_folder"
    return sanitized

def move_file_with_retry(source: Path, target: Path, retries: int = 3, delay: int = 2) -> bool:
    """
    Attempt to move a file with retries in case of transient errors.
    """
    for attempt in range(1, retries + 1):
        try:
            source.rename(target)
            logging.info(f"Moved {source.name} to {target}")
            return True
        except Exception as e:
            logging.error(f"Attempt {attempt}: Error moving file {source.name} to {target}: {e}")
            if attempt < retries:
                time.sleep(delay)
            else:
                logging.error(f"Failed to move {source.name} after {retries} attempts.")
                return False

def load_config():
    """
    Load configuration from the config.json file.
    Overrides default values with those provided in the file.
    """
    global config, DOWNLOADS_DIR, NO_CASE_FOLDER, DEFAULT_SUBFOLDER
    global FILE_CHECK_INTERVAL, MONITOR_INTERVAL, ERROR_SLEEP, PORT
    global CLEANUP_ENABLED, CLEANUP_AGE_THRESHOLD, CLEANUP_INTERVAL

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            logging.info(f"Configuration loaded from {CONFIG_FILE}")
    except FileNotFoundError:
        logging.warning(f"{CONFIG_FILE} not found. Using default configuration.")
        config = DEFAULT_CONFIG.copy()
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in {CONFIG_FILE}: {e}. Using default configuration.")
        config = DEFAULT_CONFIG.copy()
    except Exception as e:
        logging.error(f"Error loading {CONFIG_FILE}: {e}. Using default configuration.")
        config = DEFAULT_CONFIG.copy()

    # Override defaults with config file values
    config = {**DEFAULT_CONFIG, **config}

    # Set global variables from config
    DOWNLOADS_DIR = Path(config['downloads_dir']).resolve()
    NO_CASE_FOLDER = config['no_case_folder']
    DEFAULT_SUBFOLDER = config['default_subfolder']
    FILE_CHECK_INTERVAL = config.get('file_check_interval', 0.5)
    MONITOR_INTERVAL = config.get('monitor_interval', 0.5)
    ERROR_SLEEP = config.get('error_sleep', 5)
    PORT = config.get('server_port', 8000)
    CLEANUP_ENABLED = config.get('cleanup_enabled', False)
    CLEANUP_AGE_THRESHOLD = config.get('cleanup_age_threshold', "6m")
    CLEANUP_INTERVAL = config.get('cleanup_interval', "1d")  # Optional

def determine_subfolder(filename: str) -> str:
    """
    Determine the appropriate subfolder for a file based on configured rules.
    """
    filename_lower = filename.lower()
    for rule in config.get('rules', []):
        try:
            # Check extensions
            extensions = rule.get('extensions', [])
            if extensions:
                if not any(filename_lower.endswith(ext.lower()) for ext in extensions):
                    continue  # Extension doesn't match, check next rule
            # Check filename_contains
            filename_contains = rule.get('filename_contains', [])
            if filename_contains:
                if not isinstance(filename_contains, list):
                    filename_contains = [filename_contains]
                if not any(s.lower() in filename_lower for s in filename_contains):
                    continue  # Filename doesn't contain required string, check next rule
            # If both checks pass or are not specified, return the subfolder
            return rule.get('subfolder', DEFAULT_SUBFOLDER)
        except Exception as e:
            logging.error(f"Error processing rule {rule}: {e}")
    # If no rules match, return the default subfolder
    return DEFAULT_SUBFOLDER

# ----------------------------- Cleanup Functions -------------------------

def parse_time_threshold(threshold_str: str) -> Optional[datetime.timedelta]:
    """
    Parses a time threshold string (e.g., '1m', '6m', '1y') into a timedelta object.
    Supports days (d), weeks (w), months (m), and years (y).
    Note: Months and years are approximated (30 days for a month, 365 days for a year).
    
    Args:
        threshold_str (str): The time threshold string.

    Returns:
        Optional[datetime.timedelta]: The corresponding timedelta or None if invalid format.
    """
    match = re.fullmatch(r'(\d+)([dwmy])', threshold_str.strip().lower())
    if not match:
        logging.error(f"Invalid cleanup_age_threshold format: '{threshold_str}'. Expected formats like '1m', '6m', '1y'.")
        return None

    value, unit = match.groups()
    value = int(value)

    if unit == 'd':
        return datetime.timedelta(days=value)
    elif unit == 'w':
        return datetime.timedelta(weeks=value)
    elif unit == 'm':
        return datetime.timedelta(days=30 * value)  # Approximation
    elif unit == 'y':
        return datetime.timedelta(days=365 * value)  # Approximation
    else:
        logging.error(f"Unsupported time unit in cleanup_age_threshold: '{unit}'.")
        return None

def cleanup_old_files():
    """
    Removes files in the downloads directory older than the configured threshold.
    """
    if not CLEANUP_ENABLED:
        logging.info("File cleanup is disabled. Skipping cleanup process.")
        return

    threshold = parse_time_threshold(CLEANUP_AGE_THRESHOLD)
    if not threshold:
        logging.error("Failed to parse cleanup_age_threshold. Skipping cleanup process.")
        return

    cutoff_time = datetime.datetime.now() - threshold
    logging.info(f"Starting cleanup: Removing files older than {CLEANUP_AGE_THRESHOLD} (before {cutoff_time})")

    try:
        removed_files = 0
        for root, dirs, files in os.walk(DOWNLOADS_DIR):
            for file in files:
                file_path = Path(root) / file
                try:
                    # Skip system folders like no_case_folder and default_subfolder
                    relative_path = file_path.relative_to(DOWNLOADS_DIR)
                    if relative_path.parts[0] in [NO_CASE_FOLDER, DEFAULT_SUBFOLDER]:
                        continue  # Skip system folders

                    # Get file's last modification time
                    file_mtime = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        # Attempt to remove the file
                        file_path.unlink()
                        logging.info(f"Removed old file: {file_path}")
                        removed_files += 1
                except Exception as e:
                    logging.error(f"Error removing file {file_path}: {e}")

        logging.info(f"Cleanup completed. Total files removed: {removed_files}")
    except Exception as e:
        logging.error(f"Error during cleanup process: {e}")

def cleanup_scheduler():
    """
    Schedules periodic cleanup based on the configured interval.
    """
    if not CLEANUP_ENABLED:
        logging.info("File cleanup is disabled. Cleanup scheduler not started.")
        return

    interval = parse_time_threshold(CLEANUP_INTERVAL)
    if not interval:
        logging.error("Failed to parse cleanup_interval. Cleanup scheduler not started.")
        return

    logging.info(f"Cleanup scheduler started. Next cleanup in {CLEANUP_INTERVAL}.")
    while True:
        time.sleep(interval.total_seconds())
        cleanup_old_files()
        logging.info(f"Next cleanup scheduled in {CLEANUP_INTERVAL}.")

# ----------------------------- Server Handler -----------------------------

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        global current_case_number, current_company_name
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            
            received_case_number = data.get('case_number')
            received_company_name = data.get('company_name')

            if received_case_number is None or received_company_name is None:
                logging.error('Both "case_number" and "company_name" must be provided in POST data.')
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Both "case_number" and "company_name" must be provided.')
                return

            logging.info(f"Received Case Number: {received_case_number}, Company Name: {received_company_name}")

            with assignments_lock:
                if received_case_number == 'NO_CASE' and received_company_name == 'NO_COMPANY':
                    current_case_number = None
                    current_company_name = None
                    logging.info("Set current_case_number and current_company_name to None (NO_CASE and NO_COMPANY).")
                else:
                    current_case_number = received_case_number
                    current_company_name = received_company_name
                    logging.info(f"Updated current_case_number to {current_case_number} and current_company_name to {current_company_name}.")

            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'Case information received successfully.')
            return
        except json.JSONDecodeError:
            logging.error('Invalid JSON in POST data.')
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid JSON.')
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Internal server error.')

    def log_message(self, format, *args):
        # Override to prevent logging every GET request to stdout
        return

# ----------------------------- File Monitoring ----------------------------

def is_file_fully_downloaded(filepath: Path) -> bool:
    """
    Check if a file is fully downloaded by monitoring its size over time.
    """
    try:
        previous_size = -1
        stable_count = 0
        while stable_count < 3:
            if not filepath.exists():
                return False
            current_size = filepath.stat().st_size
            if current_size == previous_size:
                stable_count += 1
            else:
                stable_count = 0
                previous_size = current_size
            time.sleep(FILE_CHECK_INTERVAL)
        return True
    except Exception as e:
        logging.error(f"Error checking if file is complete: {e}")
        return False

def move_existing_files_to_no_case_folder():
    """
    Move existing files in the Downloads directory to the 'no_case_folder' at startup.
    """
    try:
        target_folder = DOWNLOADS_DIR / NO_CASE_FOLDER
        target_folder.mkdir(parents=True, exist_ok=True)

        for file in DOWNLOADS_DIR.iterdir():
            if file.is_file() and not file.name.startswith('.') and not file.name.endswith('.crdownload'):
                try:
                    destination = target_folder / file.name
                    if destination.exists():
                        destination.unlink()  # Remove existing file
                        logging.info(f"Removed existing file: {destination.name}")
                    file.rename(destination)
                    logging.info(f"Moved existing file {file.name} to {target_folder}")
                except Exception as e:
                    logging.error(f"Error moving file {file.name} to '{NO_CASE_FOLDER}' folder: {e}")
    except Exception as e:
        logging.error(f"Error during initial file move to '{NO_CASE_FOLDER}' folder: {e}")

def monitor_downloads(server: socketserver.TCPServer):
    """
    Monitor the Downloads directory for new files and move them accordingly.
    Each file is assigned to the current company_name and case_number at the time of detection.
    """
    while True:
        try:
            for file in DOWNLOADS_DIR.iterdir():
                if file.is_file() and not file.name.startswith('.') and not file.name.endswith('.download'):
                    # Skip files already in no_case_folder or company/case folders
                    if file.parent == (DOWNLOADS_DIR / NO_CASE_FOLDER):
                        continue
                    if current_company_name and current_case_number:
                        target_folder = DOWNLOADS_DIR / sanitize_filename(current_company_name) / sanitize_filename(current_case_number)
                        if file.parent == target_folder:
                            continue  # Already in the correct folder
                    else:
                        # If not assigned to a case, skip if already in no_case_folder
                        if file.parent == (DOWNLOADS_DIR / NO_CASE_FOLDER):
                            continue

                    # Acquire lock to assign case and company
                    with assignments_lock:
                        if file.name in file_assignments:
                            continue  # Already assigned
                        assigned_company = current_company_name  # Capture current company
                        assigned_case = current_case_number    # Capture current case
                        file_assignments[file.name] = (assigned_company, assigned_case)

                    # Check if file is fully downloaded
                    if is_file_fully_downloaded(file):
                        filename = file.name
                        logging.info(f"Detected new file: {filename}")

                        if assigned_company and assigned_case:
                            # Determine subfolder based on rules
                            subfolder = determine_subfolder(filename)
                            target_folder = DOWNLOADS_DIR / sanitize_filename(assigned_company) / sanitize_filename(assigned_case) / subfolder
                        else:
                            # Move directly to no_case_folder without subfolders
                            target_folder = DOWNLOADS_DIR / NO_CASE_FOLDER

                        # Create target folder if it doesn't exist
                        target_folder.mkdir(parents=True, exist_ok=True)

                        target_filepath = target_folder / filename

                        # If the file already exists in the target, remove it
                        if target_filepath.exists():
                            try:
                                target_filepath.unlink()
                                logging.info(f"Removed existing file in target: {target_filepath.name}")
                            except Exception as e:
                                logging.error(f"Error removing existing file {target_filepath.name}: {e}")
                                # Remove assignment since move failed
                                with assignments_lock:
                                    del file_assignments[file.name]
                                continue  # Skip moving this file

                        # Move the file with retry
                        success = move_file_with_retry(file, target_filepath)
                        if not success:
                            with assignments_lock:
                                del file_assignments[file.name]
                            continue  # Skip to the next file

                        # Remove assignment after moving
                        with assignments_lock:
                            del file_assignments[file.name]
        except Exception as e:
            logging.error(f"Error in monitor_downloads loop: {e}")
            time.sleep(ERROR_SLEEP)  # Configurable error sleep intervals

# ----------------------------- Server Initialization ----------------------

def run_server(server: socketserver.TCPServer):
    """
    Start the HTTP server to receive case number and company name notifications.
    """
    try:
        logging.info(f"Serving at port {PORT} on localhost only.")
        server.serve_forever()
    except Exception as e:
        logging.error(f"Error running server: {e}")
    finally:
        server.server_close()
        logging.info("Server has been shut down.")

# ----------------------------- Main Execution -----------------------------

def main():
    try:
        # Load the configuration at startup
        load_config()

        # Ensure the downloads directory exists
        if not DOWNLOADS_DIR.exists():
            logging.error(f"Downloads directory does not exist: {DOWNLOADS_DIR}")
            raise FileNotFoundError(f"Downloads directory does not exist: {DOWNLOADS_DIR}")

        # Move existing files to 'no_case_folder'
        move_existing_files_to_no_case_folder()

        # Perform cleanup if enabled
        cleanup_old_files()

        # Start cleanup scheduler in a separate thread if periodic cleanup is desired
        if CLEANUP_ENABLED and CLEANUP_INTERVAL:
            cleanup_scheduler_thread = threading.Thread(target=cleanup_scheduler, daemon=True)
            cleanup_scheduler_thread.start()

        # Create the server object
        with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
            # Start monitoring downloads in a separate thread
            monitor_thread = threading.Thread(target=monitor_downloads, args=(httpd,), daemon=True)
            monitor_thread.start()

            # Start the server in a separate thread
            server_thread = threading.Thread(target=run_server, args=(httpd,), daemon=True)
            server_thread.start()

            # Notify the user that the server is running
            print("SCDO server is up and running.")
            print(ASCII_ART)
            print("Press 'q' then Enter to exit.")

            # Listen for 'q' input to shut down the server
            while True:
                user_input = input().strip().lower()
                if user_input == 'q':
                    logging.info("Shutdown initiated by user input.")
                    print("Shutting down the SCDO server...")
                    httpd.shutdown()
                    break
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully if possible
        logging.info("KeyboardInterrupt received. Shutting down the server.")
        print("\nShutting down the SCDO server...")
    except Exception as e:
        logging.critical(f"Critical error: {e}")
        logging.critical("Exiting script due to critical error.")
        sys.exit(1)

if __name__ == '__main__':
    main()
