from .. import app, database, models
import json
import uuid
from datetime import datetime, timedelta
from flask import request


@app.route("/session/refresh", methods=['POST'])
def refresh():
	if request.method == 'POST':

		# try:
		# 	version = request.headers['API_VERSION']
		# except Exception, e:
		# 	return_data = {'status': False, 'error': 'Version out of date', 'data': None}
		# 	return json.dumps(return_data)
        #
		# api_version = database.db_session.query(models.Server_api_version).order_by(models.Server_api_version.timestamp.desc()).first()
        #
		# if float(version) < api_version.getVersion():
		# 	return_data = {'status': False, 'error': 'Version out of date', 'data': None}
		# 	return json.dumps(return_data)

		json_data = request.get_json()
		token_id = json_data['token_id']
		token_refresh = json_data['refresh']

		token = database.db_session.query(models.Token).filter_by(id=token_id).first()

		if token is None:
			return_data = {'status': False, 'error': 'Invalid token', 'data': None}
			return json.dumps(return_data)

		if token_refresh != token.getRefresh():
			return_data = {'status': False, 'error': 'Invalid token', 'data': None}
			return json.dumps(return_data)

		try:
			#database.db_session.delete(token)
			database.db_session.commit()
		except:
			database.db_session.rollback()
			return_data = {'status': False, 'error': 'Failed to delete token', 'data': None}
			return json.dumps(return_data)

		access = str(uuid.uuid4())
		refresh = str(uuid.uuid4())
		timestamp = datetime.utcnow()
		lifetime = timedelta(days=2, hours=0, minutes=0, seconds=0)

		token = models.Token(token.getUser_id(), access, refresh, timestamp, lifetime)

		data = None
		status = True
		error = None
		try:
			database.db_session.add(token)
			database.db_session.commit()
			data = {
					'token_id': token.getId(),
					'access': token.getAccess(),
					'refresh': token.getRefresh(),
					'timestamp': str(token.getTimestamp()),
					'lifetime': str(token.getLifetime().total_seconds())
					}
		except:
			database.db_session.rollback()
			status = False
			error = 'Could not register token'

		return_data = {'status': status, 'error': error, 'data': data}
		return json.dumps(return_data)