import http.server
import socketserver
import threading
import json
import os
import time
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

PORT = 8000  # Port number for the local server
CONFIG_FILE = 'config.json'  # Path to the configuration file

case_number = None
config = {}
DOWNLOADS_DIR = Path()
NO_CASE_FOLDER = ''
DEFAULT_SUBFOLDER = ''

def move_existing_files_to_no_case_folder():
    """
    Move existing files in the Downloads directory to the 'no_case_folder' at startup.
    """
    try:
        target_folder = DOWNLOADS_DIR / NO_CASE_FOLDER
        target_folder.mkdir(parents=True, exist_ok=True)

        for file in DOWNLOADS_DIR.iterdir():
            if file.is_file() and not file.name.startswith('.') and not file.name.endswith('.download'):
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

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        global case_number
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data)
            if 'case_number' in data:
                received_case_number = data['case_number']
                logging.info(f"Received case number: {received_case_number}")
                if received_case_number == 'NO_CASE':
                    case_number = None
                else:
                    case_number = received_case_number
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b'Case number received')
                return
            else:
                logging.error('Case number not found in POST data.')
        except Exception as e:
            logging.error(f"Error processing request: {e}")
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Invalid request')

    def log_message(self, format, *args):
        # Override to prevent logging every GET request to stdout
        return

def is_file_fully_downloaded(filepath):
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
            time.sleep(1)
        return True
    except Exception as e:
        logging.error(f"Error checking if file is complete: {e}")
        return False

def load_config():
    global config, DOWNLOADS_DIR, NO_CASE_FOLDER, DEFAULT_SUBFOLDER
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            logging.info(f"Configuration loaded from {CONFIG_FILE}")
        
        # Validate and set the downloads directory
        downloads_dir = config.get('downloads_dir')
        if not downloads_dir or not Path(downloads_dir).is_dir():
            logging.error(f"Invalid downloads_dir in configuration: {downloads_dir}")
            raise ValueError("Invalid downloads_dir in configuration.")
        DOWNLOADS_DIR = Path(downloads_dir).resolve()

        # Set the no_case_folder
        no_case_folder = config.get('no_case_folder', 'Miscellaneous')
        NO_CASE_FOLDER = no_case_folder

        # Set the default subfolder
        DEFAULT_SUBFOLDER = config.get('default_subfolder', 'Other')
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        config = {
            "downloads_dir": "",
            "no_case_folder": "Miscellaneous",
            "rules": [],
            "default_subfolder": "Other"
        }
        raise e  # Re-raise the exception to halt execution

def determine_subfolder(filename):
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
                if not any(s.lower() in filename_lower for s in filename_contains):
                    continue  # Filename doesn't contain required string, check next rule
            # If both checks pass or are not specified, return the subfolder
            return rule.get('subfolder', DEFAULT_SUBFOLDER)
        except Exception as e:
            logging.error(f"Error processing rule {rule}: {e}")
    # If no rules match, return the default subfolder
    return DEFAULT_SUBFOLDER

def monitor_downloads():
    """
    Monitor the Downloads directory for new files and move them accordingly.
    """
    while True:
        try:
            for file in DOWNLOADS_DIR.iterdir():
                if file.is_file() and not file.name.startswith('.') and not file.name.endswith('.download'):
                    # Skip files already in no_case_folder or case_number folders
                    if file.parent == (DOWNLOADS_DIR / NO_CASE_FOLDER):
                        continue
                    if case_number and file.parent == (DOWNLOADS_DIR / case_number):
                        continue

                    # Check if file is fully downloaded
                    if is_file_fully_downloaded(file):
                        filename = file.name
                        logging.info(f"Detected new file: {filename}")

                        if case_number:
                            # Determine subfolder based on rules
                            subfolder = determine_subfolder(filename)
                            target_folder = DOWNLOADS_DIR / case_number / subfolder
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
                                continue  # Skip moving this file

                        # Move the file
                        try:
                            file.rename(target_filepath)
                            if case_number:
                                logging.info(f"Moved {filename} to {target_folder} under case {case_number}")
                            else:
                                logging.info(f"Moved {filename} to {target_folder} (no active case)")
                        except Exception as e:
                            logging.error(f"Error moving file {filename} to {target_folder}: {e}")
            time.sleep(1)  # Check every second
        except Exception as e:
            logging.error(f"Error in monitor_downloads loop: {e}")
            time.sleep(5)  # Wait before retrying to prevent rapid error logging

def run_server():
    """
    Start the HTTP server to receive case number notifications.
    """
    try:
        with socketserver.TCPServer(("", PORT), Handler) as httpd:
            logging.info(f"Serving at port {PORT}")
            httpd.serve_forever()
    except Exception as e:
        logging.error(f"Error starting server: {e}")

if __name__ == '__main__':
    try:
        # Load the configuration at startup
        load_config()

        # Move existing files to 'no_case_folder'
        move_existing_files_to_no_case_folder()

        # Start the server in a separate thread
        server_thread = threading.Thread(target=run_server, daemon=True)
        server_thread.start()

        # Start monitoring downloads
        monitor_downloads()
    except Exception as e:
        logging.critical(f"Critical error: {e}")
        logging.critical("Exiting script due to critical error.")
