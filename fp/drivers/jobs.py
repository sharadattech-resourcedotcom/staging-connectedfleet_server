from .. import app, database, models
import json
from datetime import datetime
from datetime import timedelta
from flask import request
from flask import jsonify

from sqlalchemy.ext.declarative import DeclarativeMeta

class AlchemyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj.__class__, DeclarativeMeta):
            # an SQLAlchemy class
            fields = {}
            for field in [x for x in dir(obj) if not x.startswith('_') and x != 'metadata']:
                data = obj.__getattribute__(field)
                try:
                    json.dumps(data) # this will fail on non-encodable values, like other classes
                    fields[field] = data
                except TypeError:
                    fields[field] = None
            # a json-encodable dict
            return fields

        return json.JSONEncoder.default(self, obj)

@app.route("/driver/jobs", methods=['POST'])
def getJobs():
    if request.method == 'POST':

        json_data = request.get_json()
        
        token_id = json_data['token_id']
        token_access = json_data['access']

        token = database.db_session.query(models.Token).filter_by(id=token_id).first()

        if token is None:
            return_data = {'status': False, 'error': 'Invalid token', 'data': None}
            return json.dumps(return_data)

        if token_access != token.getAccess():
            return_data = {'status': False, 'error': 'Invalid token', 'data': None}
            return json.dumps(return_data)

        timestamp = datetime.utcnow()

        # if timestamp - token.getLifetime() >= token.getTimestamp():
        #     return_data = {'status': False, 'error': 'Token out of date', 'data': None}
        #     return json.dumps(return_data)

        driver = token.getUser()

        curr_date = datetime.strftime(datetime.today(), "%Y-%m-%d") 
        tomorrow = datetime.today() + timedelta(days=1)


        jobs = database.db_session.query(models.Job).filter(models.Job.start_date >= curr_date).filter(models.Job.start_date <= tomorrow).filter_by(user_id = token.getUser().id) 
        jobs_data = [j.serialize for j in jobs]
        jobs_data.insert(0, models.Job.nojob(driver.company_id))

        return_data = {'status': True, 'error': None, 'data': jobs_data}

        return json.dumps(return_data)
