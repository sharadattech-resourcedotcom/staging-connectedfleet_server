import hashlib
import json
import uuid
from datetime import datetime, timedelta
from sqlalchemy import func
from flask import request

from .. import app, database, models


@app.route("/session/login", methods=['POST'])
def login():
    if request.method == 'POST':
        # try:
        # version = request.headers['API_VERSION']
        # except Exception, e:
        #     return_data = {'status': False, 'error': 'Version out of date', 'data': None}
        #     return json.dumps(return_data)



        # api_version = database.db_session.query(models.Server_api_version).order_by(models.Server_api_version.timestamp.desc()).first()
        #
        #         if float(version) < api_version.getVersion():
        #             return_data = {'status': False, 'error': 'Version out of date', 'data': None}
        #             return json.dumps(return_data)

        if float(request.headers['App-Version']) < 2.0:
            return_data = {'status': False, 'error': 'Please install newest version of application.', 'data': None}
            return json.dumps(return_data)

        json_data = request.get_json()

        driver_login = json_data['username']
        driver_password = json_data['password']
        driver = database.db_session.query(models.User).filter(
            func.lower(models.User.email) == func.lower(driver_login), models.User.user_type == 1).first()

        if driver is None:
            return_data = {'status': False, 'error': 'Incorrect login or password', 'data': None}
            return json.dumps(return_data)

        hashed = hashlib.sha512()
        hashed.update(driver_password + ' ' + driver.getSalt())

        if driver.active == False:
            return_data = {'status': False, 'error': 'This account is deactivated.', 'data': None}
            return json.dumps(return_data)

        if str(hashed.hexdigest()) != driver.getPassword():
            return_data = {'status': False, 'error': 'Incorrect login or password', 'data': None}
            return json.dumps(return_data)

        access = str(uuid.uuid4())
        refresh = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        lifetime = timedelta(days=2, hours=0, minutes=0, seconds=0)
        token = models.Token(driver.getId(), access, refresh, timestamp, lifetime)


        data = None
        status = True
        error = None
        try:
            database.db_session.add(token)
            driver.setLast_login(timestamp)
            driver.setApiVersion(request.headers['API_VERSION'])

            database.db_session.commit()

            if request.headers.has_key('App-Version-Code'):
                version_code = request.headers['App-Version-Code']
            else:
                version_code = 0
            data = {'driver_id': driver.getId(), 'token_id': token.getId(), 'access': token.getAccess(),
                    'name': driver.getFullName(),
                    'refresh': token.getRefresh(), 'timestamp': str(token.getTimestamp()),
                    'lifetime': str(token.getLifetime().total_seconds()),
                    'vehicle_reg_number': driver.getVehicle_reg_number(),
                    'synchronization_per': 60 * 3,
                    'gps_point_per': 10,
                    'update': driver.check_update(version_code)

                    # 'vehicle_reg_number': driver.getVehicle_reg_number()
            }
        except Exception, e:
            print e
            database.db_session.rollback()
            status = False
            error = 'Could not register token'

        return_data = {'status': status, 'error': error, 'data': data}
        return json.dumps(return_data)
