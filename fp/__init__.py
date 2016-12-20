from flask import Flask

app = Flask(__name__)
app.config['UPLOAD_PATH'] = '/home/newbury/cf-staging/codebase/connectedfleet_backend/public/'

import database
import drivers
import sessions
