from flask import Flask

app = Flask(__name__)
app.config['UPLOAD_PATH'] = '/home/marcin/connectedfleet-backend/public/'

import database
import drivers
import sessions