import subprocess
import threading
import json
import os

def run_flask_app(flask_app_path):
    script_path = os.path.join(flask_app_path, 'start_flask.sh')  # Use 'start_flask.bat' on Windows
    subprocess.Popen(script_path, shell=True)

def run_react_app(react_app_path):
    with open('react_output.log', 'w') as f:
        subprocess.Popen(["npm", "start"], cwd=react_app_path, stdout=f, stderr=subprocess.STDOUT)

def start_servers(config_file):
    with open(config_file, 'r') as f:
        config = json.load(f)

    flask_app_path = config.get('Flask', 'default_flask_path')
    react_app_path = config.get('ReactJS', 'default_react_path')

    print(f"Starting Flask app on http://localhost:5000")
    flask_thread = threading.Thread(target=run_flask_app, args=(flask_app_path,))
    flask_thread.start()

    print(f"Starting React app on http://localhost:3000")
    react_thread = threading.Thread(target=run_react_app, args=(react_app_path,))
    react_thread.start()

    flask_thread.join()
    react_thread.join()

# Replace 'path/to/config.json' with your actual config file path
config_file = 'config.json'
start_servers(config_file)
