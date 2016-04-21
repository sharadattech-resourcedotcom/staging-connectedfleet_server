from .. import app, database, models
import json
import sqlalchemy
import base64
import os
from sqlalchemy.exc import IntegrityError

from datetime import datetime, timedelta
from flask	import request

@app.route("/driver/check_update", methods=['GET'])
def check_update():
	token  = database.db_session.query(models.Token).filter(models.Token.access == request.headers['ACCESS-TOKEN']).first()
	driver = database.db_session.query(models.User).filter(models.User.id == token.getUser_id(), models.User.user_type==1).first()
	update = models.AppVersion.check_update(driver, request.headers['App-Version-Code'])
	if not update:
		return_data = {'status': True, 'data': {}}
	else:
		return_data = {'status': True, 'data': update.serialize}
	print return_data
	return json.dumps(return_data)