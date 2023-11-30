import json
import os
import subprocess
import sys

technologies = set(['Flask', 'ReactJS', 'SQLite'])

def create_react_template(react_app_path):
    try:
        # Use npx to create a new React app
        subprocess.run(["npx", "create-react-app", react_app_path], check=True)

        # Configure the React app to proxy API requests to the Flask server
        package_json_path = os.path.join(react_app_path, "package.json")
        with open(package_json_path, "r+") as package_json:
            data = json.load(package_json)
            data["proxy"] = "http://localhost:5000"
            package_json.seek(0)
            json.dump(data, package_json, indent=2)
            package_json.truncate()

        print(f"React app created at {react_app_path} and configured to connect to Flask API.")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while creating the React app: {e}")


def setup_virtual_environment(flask_app_path, reset=False):
    venv_path = os.path.join(flask_app_path, 'venv')

    # Delete the existing virtual environment if reset is True
    if reset and os.path.exists(venv_path):
        shutil.rmtree(venv_path)
        print(f"Existing virtual environment at {venv_path} has been removed.")

    # Create a virtual environment
    subprocess.run([sys.executable, '-m', 'venv', venv_path], check=True)
    print(f"Virtual environment created at {venv_path}")

    return venv_path


def generate_flask_template(component_path, reset_venv=False):
    try:
        # Define the Flask API template directory structure with content for SQLAlchemy with SQLite
        flask_structure = {
            'app': {
                '__init__.py': '''
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)

from app import routes, models
''',
                'routes.py': '''
from app import app, db
from app.models import User

@app.route('/')
@app.route('/index')
def index():
    user_count = User.query.count()
    return f"Hello, World! There are {user_count} users."
''',
                'models.py': '''
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    # Other fields...
'''
            },
            'tests': {
                '__init__.py': '',
                'test_basic.py': '''
import unittest
from app import app, db
from app.models import User

class BasicTestCase(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        response = self.app.get('/index', content_type='html/text')
        self.assertTrue(b'Hello, World!' in response.data)

if __name__ == '__main__':
    unittest.main()
'''
            },
            'requirements.txt': '''
Flask>=3.0.0
Flask-SQLAlchemy>=3.0.0
Werkzeug>=3.0.0
''',
            'config.py': '''
class Config(object):
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///your_database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
''',
            'run.py': '''
from app import app, db

@app.before_first_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
'''
        }


        for dir_name, content in flask_structure.items():
            if isinstance(content, dict):
                dir_path = os.path.join(component_path, dir_name)
                os.makedirs(dir_path, exist_ok=True)
                for file_name, file_content in content.items():
                    file_path = os.path.join(dir_path, file_name)
                    with open(file_path, 'w') as file:
                        file.write(file_content.strip())
            else:
                file_path = os.path.join(component_path, dir_name)
                if os.path.isdir(file_path):
                    os.rmdir(file_path)
                with open(file_path, 'w') as file:
                    file.write(content.strip())

        try:
            # Install dependencies from requirements.txt
            requirements_path = os.path.join(component_path, 'requirements.txt')

            # Set up virtual environment
            venv_path = setup_virtual_environment(component_path, reset=reset_venv)


            # Install dependencies within the virtual environment
            pip_path = os.path.join(venv_path, 'bin', 'pip3')  # Use 'Scripts\\pip.exe' on Windows
            subprocess.run([pip_path, 'install', '-r', requirements_path], check=True)
            print(f"Dependencies installed for the Flask app in {component_path}")

            # # Additional code for start_flask.sh
            # flask_start_script = os.path.join(component_path, "start_flask.sh")

            # with open(flask_start_script, 'w') as file:
            #     file.write("#!/bin/bash\n")
            #     file.write(f"source {venv_path}/bin/activate\n")
            #     file.write("export FLASK_APP=app.py\n")
            #     file.write("export FLASK_ENV=development\n")
            #     file.write("python3 -m flask run\n")

            # # Make the script executable
            # os.chmod(flask_start_script, 0o755)

        except subprocess.CalledProcessError as e:
            print(f"An error occurred while installing dependencies: {e}")

    except Exception as e:
        print(f"An error occurred while generating Flask template: {e}")

def generate_template(component_technology, component_path):
    reset_venv = True
    if component_technology == "Flask":
        os.environ['FLASK_APP_PATH'] = component_path
        generate_flask_template(component_path, reset_venv)
    elif component_technology == "ReactJS":
        os.environ['REACT_APP_PATH'] = component_path
        create_react_template(component_path)


def create_directories_from_json(json_file, config_file):
    config = {}
    try:
        with open(json_file, 'r') as file:
            components = json.load(file)

        for component in components:
            base_path = component['locator']
            component_name = component['name']
            component_technology = component['technology']

            directory_path = os.path.join(base_path, component_name)

            if not os.path.exists(directory_path):
                os.makedirs(directory_path)
                print(f"Directory created for component '{component_name}': {directory_path}")
            else:
                print(f"Directory already exists for component '{component_name}': {directory_path}")

            if component_technology in technologies:
                config[component_technology] = directory_path

                if(component_technology == 'Flask'):
                    generate_flask_template(directory_path)
                if(component_technology == 'ReactJS'):
                    create_react_template(directory_path)

            else:
                print(f"Component technology '{component_technology}' not in set of valid technologies")

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=4)

    except Exception as e:
        print(f"An error occurred: {e}")

# Replace 'path/to/your/jsonfile.json' with your actual JSON file path
create_directories_from_json('sample_json.json', 'config.json')
