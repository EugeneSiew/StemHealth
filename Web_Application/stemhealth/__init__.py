from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Define the project's root directory
project_root = os.path.dirname(os.path.abspath(__file__))

# Define the upload folder relative to the project root
UPLOAD_FOLDER = os.path.join(app.static_folder, 'seedling_data')

# Configure the database URI relative to the project root
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(project_root, "site.db")}'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

db = SQLAlchemy(app)

from stemhealth.models import Batch, Entry
from stemhealth import routes
