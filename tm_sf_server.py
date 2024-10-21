import http.server
import socketserver
import threading
import json
import os
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(levelname)s: %(message)s')

PORT = 8000  # Port number for the local server
CONFIG_FILE = 'config.json'  # Path to the configuration file

case_number = None
config = {}
DOWNLOADS_DIR = ''
NO_CASE_FOLDER = ''
DEFAULT_SUBFOLDER = ''

def move_files_to_no_case_folder():
    """
    Move existing files in the Downloads directory to the 'no_case_folder' at startup.
    """
    try:
        target_folder = os.path.join(DOWNLOADS_DIR, NO_CASE_FOLDER)
        os.makedirs(target_folder, exist_ok=True)

        files = os.listdir(DOWNLOADS_DIR)
        for filename in files:
            filepath = os.path.join(DOWNLOADS_DIR, filename)
            if os.path.isfile(filepath) and not filename.startswith('.') and not filename.endswith('.download'):
                new_filepath = os.path.join(target_folder, filename)
                try:
                    os.rename(filepath, new_filepath)
                    logging.info(f"Moved existing file {filename} to {target_folder}")
                except Exception as e:
                    logging.error(f"Error moving file {filename} to '{NO_CASE_FOLDER}' folder: {e}")
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

def is_file_complete(filepath):
    """
    Check if a file is fully downloaded by monitoring its size over time.
    """
    try:
        previous_size = -1
        stable_count = 0
        while True:
            try:
                current_size = os.path.getsize(filepath)
            except FileNotFoundError:
                # File might have been deleted or moved
                logging.warning(f"File not found during size check: {filepath}")
                return False
            if current_size == previous_size:
                stable_count += 1
                if stable_count >= 3:
                    # Size hasn't changed for 3 checks (approx 3 seconds)
                    return True
            else:
                stable_count = 0
                previous_size = current_size
            time.sleep(1)
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
        if not downloads_dir or not os.path.isdir(downloads_dir):
            logging.error(f"Invalid downloads_dir in configuration: {downloads_dir}")
            raise ValueError("Invalid downloads_dir in configuration.")
        DOWNLOADS_DIR = downloads_dir

        # Set the no_case_folder
        no_case_folder = config.get('no_case_folder', 'Other')
        NO_CASE_FOLDER = no_case_folder

        # Set the default subfolder
        DEFAULT_SUBFOLDER = config.get('default_subfolder', 'Other')
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        config = {
            "downloads_dir": "",
            "no_case_folder": "Other",
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
            return rule['subfolder']
        except Exception as e:
            logging.error(f"Error processing rule {rule}: {e}")
    # If no rules match, return the default subfolder
    return DEFAULT_SUBFOLDER

def monitor_downloads():
    already_seen = set()
    while True:
        try:
            files = os.listdir(DOWNLOADS_DIR)
            new_files = [f for f in files if f not in already_seen and not f.startswith('.') and not f.endswith('.download')]
            for filename in new_files:
                filepath = os.path.join(DOWNLOADS_DIR, filename)
                if os.path.isfile(filepath):
                    # Wait until the file is fully downloaded
                    if is_file_complete(filepath):
                        # Determine the subfolder based on the configuration
                        subfolder = determine_subfolder(filename)
                        if case_number:
                            # Move the file to the appropriate subfolder within the case number folder
                            case_folder = os.path.join(DOWNLOADS_DIR, case_number)
                            target_folder = os.path.join(case_folder, subfolder)
                        else:
                            # Move the file to the no_case_folder
                            target_folder = os.path.join(DOWNLOADS_DIR, NO_CASE_FOLDER, subfolder)
                        try:
                            os.makedirs(target_folder, exist_ok=True)
                        except Exception as e:
                            logging.error(f"Error creating directory {target_folder}: {e}")
                            continue  # Skip to the next file
                        new_filepath = os.path.join(target_folder, filename)
                        # Handle duplicates
                        if os.path.exists(new_filepath):
                            try:
                                os.remove(new_filepath)
                                logging.info(f"Removed existing file: {new_filepath}")
                            except Exception as e:
                                logging.error(f"Error removing existing file {new_filepath}: {e}")
                                continue  # Skip to the next file
                        try:
                            os.rename(filepath, new_filepath)
                            if case_number:
                                logging.info(f"Moved {filename} to {target_folder} under case {case_number}")
                            else:
                                logging.info(f"Moved {filename} to {target_folder} (no active case)")
                        except Exception as e:
                            logging.error(f"Error moving file {filename} to {target_folder}: {e}")
                        already_seen.add(filename)
                    else:
                        logging.info(f"File {filename} is not fully downloaded yet.")
            # Update the set of already seen files
            already_seen.update(files)
            time.sleep(1)
        except Exception as e:
            logging.error(f"Error in monitor_downloads loop: {e}")
            time.sleep(5)  # Wait before retrying to prevent rapid error logging

def run_server():
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
        move_files_to_no_case_folder()

        # Start the server in a separate thread
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()

        # Start monitoring downloads
        monitor_downloads()
    except Exception as e:
        logging.critical(f"Critical error: {e}")
        logging.critical("Exiting script due to critical error.")
