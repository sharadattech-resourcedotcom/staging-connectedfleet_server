from .. import app, database, models
import json
import sqlalchemy
import base64
import os
from sqlalchemy.exc import IntegrityError
from ..configs import config

from datetime import datetime, timedelta
from flask	import request

@app.route("/driver/period_trips", methods=['GET'])
def period_trips():
	print request.headers['ACCESS-TOKEN']
	token  = database.db_session.query(models.Token).filter(models.Token.access == request.headers['ACCESS-TOKEN']).first()
	if not token:
		return_data = { "status" : False, "error" : "Authorization fail."}
		return json.dumps(return_data)
	driver = database.db_session.query(models.User).filter(models.User.id == token.getUser_id(), models.User.user_type==1).first()
	if not driver:
		return_data = { "status" : False, "error" : "Authorization fail."}
		return json.dumps(return_data)
	period = database.db_session.query(models.Period).filter(models.Period.user_id == driver.id, models.Period.status == 'opened').order_by('start_date desc').first()
	trips = period.getSerializedPeriodTrips()
	confirm = "I confirm that I have completed all checks (Visual, Internal and External), as described in Photo-Me's online Driver Awareness training and Driver Handbook. I have also reported any defects to CLM and/or Photo-Me's Health & Safety Manager."
	return_data = { "status" : True, "error" : None, "data" : {"period" : period.serialize(), "trips": trips, "url": config.DOWNLOAD_URL, "confirm_text": confirm}}
	return json.dumps(return_data)
