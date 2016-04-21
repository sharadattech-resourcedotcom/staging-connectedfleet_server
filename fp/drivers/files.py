from .. import app, database, models
import os
import json
from datetime import datetime
from flask import request
from sqlalchemy import exc
import bcrypt
import time

@app.route("/driver/files", methods=['POST'])

# Method to send Damage files (its being send outside synchronization because 
# of issues with sending multiple files in one request)
def sendFiles():
	return_data = { "status" : True, "error" : None, "data" : 0}

	print request.args
	print request.files
	if request.method == 'POST':
		token  = database.db_session.query(models.Token).filter_by(access=request.headers['Access-Token'], id=int(request.headers['Token-Id'])).first()		

		if not token:
			return_data['error'] = "We couldn't authenticate you"
		else:
			driver = database.db_session.query(models.User).filter_by(id=token.getUser().getId()).first()

			if not driver:
				return_data['error'] = "We couldn't authenticate you"
			else:
				for f in request.files:
					filename = f + '_' + str(int(round(time.time() * 1000))) + '.jpg'
					request.files[f].save(os.path.join(app.config['UPLOAD_PATH'] + 'damages', filename))
					
					d = models.DamageItem.attach_file(filename, f, driver.getId())
					if d:
						database.db_session.add(d)
						return_data["data"] = return_data["data"] + 1

				database.db_session.commit()
	else:
		return_data['error'] = "Wrong request METHOD used"

	print return_data

	return json.dumps(return_data)