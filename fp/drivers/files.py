from .. import app, database, models
import os
import json
from datetime import datetime
from flask import request
from sqlalchemy import exc
import bcrypt
import time

#test: ab -n2000 -c10 -p post.txt -T "multipart/form-data; boundary=1234567890" -H "Access-Token:fa861425-38d9-4809-a40c-249cb31384cb" -H "Token-Id:33706" -H "App-Version: 2.2" -H "Device-Model: ab-test" -H "App-Version-Code: 0" -H "App-Type: ab-test"  http://0.0.0.0:8001/driver/files 

@app.route("/driver/files", methods=['POST'])
# Method to send Damage files (its being send outside synchronization because 
# of issues with sending multiple files in one request)
def sendFiles():
	return_data = { "status" : True, "error" : None, "data" : 0}
	print request.args
	try:
		if request.method == 'POST':
			token  = database.db_session.query(models.Token).filter_by(access=request.headers['Access-Token'], id=int(request.headers['Token-Id'])).first()		

			if not token:
				raise Exception("We couldn't authenticate you")
			else:
				driver = database.db_session.query(models.User).filter_by(id=token.getUser().getId()).first()

				if not driver:
					raise Exception("We couldn't authenticate you")
				else:
					for f in request.files:
						if "damage_item" in f:
							filename = f + '_' + str(int(round(time.time() * 1000))) + '.jpg'
							request.files[f].save(os.path.join(app.config['UPLOAD_PATH'] + 'damages', filename))
							
							d = models.DamageItem.attach_file(filename, f, driver.getId())
							if d:
								database.db_session.add(d)
								return_data["data"] = return_data["data"] + 1

						if "disposal_photo" in f:
							filename = f + '_' + str(int(round(time.time() * 1000))) + '.jpg'
							path = os.path.join(app.config['UPLOAD_PATH'] + 'disposal_photos', filename)
							request.files[f].save(path)
							d = models.DisposalPhoto.attach_file("/public/disposal_photos/"+filename, f, driver.getId())
							if d:
								database.db_session.add(d)
								return_data["data"] = return_data["data"] + 1

		else:
			raise Exception("Wrong request METHOD used")

		print return_data
		log = models.UploadLog(driver, request.headers, True, "sendFiles", None, request.remote_addr)
		database.db_session.add(log)
		database.db_session.commit()
		return json.dumps(return_data)
	except Exception, e:
		print e
		return_data["status"] = False
	 	return_data["error"] = e.message
	 	log = models.UploadLog(driver, request.headers, False, "sendFiles", e.message, request.remote_addr)
		database.db_session.add(log)
		database.db_session.commit()
		return json.dumps(return_data)