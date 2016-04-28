from .. import app, database, models
from . import starttrip, endtrip
import json
import sqlalchemy
import base64
import os
from sqlalchemy.exc import IntegrityError

from datetime import datetime, timedelta
from flask	import request

@app.route("/driver/synchronize", methods=['POST'])
def synchronize():

    # if float(request.headers['App-Version']) < 2.0:
    #         return_data = {'status': False, 'error': 'Please install newest version of application.', 'data': None}
    #         return json.dumps(return_data)
            
    if request.method == 'POST':
        postdata = request.get_json()
        print postdata
        token  = database.db_session.query(models.Token).filter(models.Token.id == postdata['token_id']).first()
        driver = database.db_session.query(models.User).filter(models.User.id == token.getUser_id(), models.User.user_type==1).first()
        print request.headers
        # Save method input
        log = models.ApiLogger(driver.getId(), 'S', request.headers['App-Version'], None)
        log.setInput(str(request.data))
        
        database.db_session.commit()
        
        try:
            driver.app_version = request.headers['App-Version']   
            driver.app_version_code = request.headers['App-Version-Code']
            log.app_version_code = request.headers['App-Version-Code']    
            database.db_session.add(driver)
        except Exception, e:
            print e.message 
        database.db_session.add(log)
        status = True
        error = ''
        #TODO: CHECK TOKENS
        #TODO: GROUP PACKAGES BY DRIVER AND TRIP THEN:
        #TODO: GET DRIVER HERE NOT TO MAKE MANY QUERIES
        #TODO: GET PERIOD THERE
        #TODO: GET GET TRIP THERE
        
        last_point = None    
        for event in postdata['events']:
            d = None
            print 'Parsing event type'+ event['type']
            if event['type'] == 'START':
                if event['driverId'] > 0:
                    d = database.db_session.query(models.User).filter(models.User.id == event['driverId'], models.User.user_type==1).first()
                if not d:
                    d = driver
                return_data = starttrip.startTrip(event, d)
                if not return_data['status']:
                    print 'Start trip error'
                    error += (return_data['error'] + ';')
                    status = False
            if event['type'] == 'STOP':
                if event['driverId'] > 0:
                    d = database.db_session.query(models.User).filter(models.User.id == event['driverId'], models.User.user_type==1).first()
                if not d:
                    d = driver
                return_data = endtrip.endTrip(event, d)
                if not return_data['status']:
                    error += (return_data['error'] + ';')
                    status = False
            # if event['type'] == 'PAUSE':
            #     return_data = pausetrip.pauseTrip(event)
            #     if not return_data['status']:
            #         error += (return_data['error'] + ';')
            #         status = False
            if event['type'] == 'CHANGE_MILEAGE':
                if event['driverId'] > 0:
                    d = database.db_session.query(models.User).filter(models.User.id == event['driverId'], models.User.user_type==1).first()
                if not d:
                    d = driver

                trip_start_date = datetime.utcfromtimestamp(int(event['startDateTrip']) / 1000)

                trip = driver.getTripForDate(trip_start_date)
                if not trip:
                    trip = driver.getTripForDate(trip_start_date + timedelta(hours=1))
                if not trip:
                    trip = driver.getTripForDate(trip_start_date - timedelta(hours=1))
                if not trip:
                    error += ('Invalid trip'+ json.dumps(event))
                    status = False
                else:
                    trip.end_mileage = int(event['customEventObject'])
                    database.db_session.add(trip)

            if event['type'] == 'STATUS':
                if event['driverId'] > 0:
                    d = database.db_session.query(models.User).filter(models.User.id == event['driverId'], models.User.user_type==1).first()
                if not d:
                    d = driver
                d.status = event['customEventObject']
                database.db_session.add(d)

            if event['type'] == 'LOCATION':
                if event['driverId'] > 0:
                    d = database.db_session.query(models.User).filter(models.User.id == event['driverId'], models.User.user_type==1).first()
                if not d:
                    d = driver
                d.lat = event['lat']
                d.lng = event['lng']
                d.last_sync = event['timestamp']
                database.db_session.add(d)

            if event['type'] == 'LOGOUT':
                end_date = datetime.strptime(event['timestamp'], '%Y-%m-%d %H:%M:%S')
                payroll = None
                if driver.driver_type:
                    payroll = database.db_session.query(models.Payroll).filter_by(user = driver, for_date = end_date.strftime('%Y-%m-%d')).first()
                if payroll:
                    payroll.set_end_datetime(end_date)  

            if event['type'] == 'RESUME':
                #RESUME TRIP
                None
            if event['type'] == 'ACKNOWLEDGE_JOB':
                obj = json.loads(event['customEventObject'])
                job  = database.db_session.query(models.Job).filter_by(id=obj['jobId']).first()
                if job:
                    job.is_acknowledged = True
                    database.db_session.add(job)

            if event['type'] == 'INSPECTION':                  
                inspection = json.loads(event['customEventObject'])
                city = None
                address_line_1 = None
                address_line_2 = None
                postcode = None
                email = None
                home_number = None
                customer_name = None
                if 'addressLine1' in inspection:
                    address_line_1 = inspection['addressLine1']
                if 'addressLine2' in inspection:
                    address_line_2 = inspection['addressLine2']
                if 'city' in inspection:
                    city = inspection['city']
                if 'homeNumber' in inspection:
                    home_number = inspection['homeNumber']
                if 'postcode' in inspection:    
                    postcode = inspection['postcode']
                if 'email' in inspection:
                    email = inspection['email']
                if 'customerName' in inspection:
                    customer_name = inspection['customerName']

                answers = ''
                if 'answers' in inspection:
                    answers = ''
                    for a in inspection['answers']:
                        answers = answers + ',' + a['question'] + ': ' + a['answer']                                

                file_name = ''


                if 'termsImage' in inspection:
                    image = base64.decodestring(inspection['termsImage'].replace('\\n', '\r\n'))
                    file_name = (str(driver.getId()) + '_' + str(event['timestamp']) + '.png').replace(" ", "")

                    path = app.config['UPLOAD_PATH'] + "/inspections"

                    if not os.path.exists(path):
                        os.makedirs(path)

                    fh = open(path + "/" + file_name, "wb")
                    fh.write(image)
                    fh.close()       
                job = database.db_session.query(models.Job).filter_by(id = inspection['jobId']).first()
                if job:
                    mi = models.MobileInspection(inspection, token.getUser().getId(), inspection['jobId'], job.appointment.vehicle_id, inspection['looseItemsChecked'], answers, inspection['driverNotes'], inspection['mileage'], file_name, email, city, postcode, address_line_1, address_line_2, home_number, customer_name)
                else:
                    vehicle = database.db_session.query(models.Vehicle).filter_by(registration = inspection['registration'], company_id = driver.getCompanyId() ).first()
                    if not vehicle:
                        vehicle = models.Vehicle(inspection['registration'], driver.getCompanyId())
                        database.db_session.add(vehicle)
                        vehicle = database.db_session.query(models.Vehicle).filter_by(registration=inspection['registration'], company_id = driver.getCompanyId()).first()
                    vehicle.assignManfacAndModel(inspection['manufacturer'], inspection['model'], driver.getCompanyId())
                    
                    mi = models.MobileInspection(inspection, token.getUser().getId(), None, vehicle.id, inspection['looseItemsChecked'], answers, inspection['driverNotes'], inspection['mileage'], file_name, email, city, postcode, address_line_1, address_line_2, home_number, customer_name)

                database.db_session.add(mi)
                if inspection.has_key('collections'):
                    for c in inspection['collections']:
                        dc = models.DamageCollection(c, mi)
                        print dc
                        database.db_session.add(dc)

                if 'damagedItems' in inspection:
                    for d in inspection['damagedItems']:
                        dm = models.DamageItem(d.get('dmgDescription', None), d['id'], event['timestamp'], d.get('collectionId', None), driver.getId(), mi)
                        database.db_session.add(dm)

            if event['type'] == 'POINT':
                try:                    
                    d = None
                    print event
                    if event['driverId'] > 0:
                        d = database.db_session.query(models.User).filter(models.User.id == event['driverId'], models.User.user_type==1).first()

                    if not d:
                        d = driver

                    trip_start_date = datetime.utcfromtimestamp(int(event['startDateTrip']) / 1000)
            
                    trip = d.getTripForDate(trip_start_date)
                    if not trip:
                        trip = d.getTripForDate(trip_start_date + timedelta(hours=1))
                    if not trip:
                        trip = d.getTripForDate(trip_start_date - timedelta(hours=1))
                    if not trip:
                        if trip_start_date.month == datetime.today().month:
                            error += 'Trip not found: '+ event['startDateTrip'] + ' for user ' + str(d.getId())
                            status = False
                    else:
                        timestamp = datetime.utcfromtimestamp(int(event['timestamp']) / 1000)
                        p = d.getPointWithTimeStamp(timestamp)
                        if not p:
                            lat = event['lat']
                            lon = event['lng']
                            on_pause = event['onPause']
                            
                            dongle = dict()

                            try:
                                if 'customEventObject' in event and event['customEventObject'] != '':
                                    dongle = json.loads(event['customEventObject'])
                            except Exception, e:
                                error += 'Point error:' + e.message

                            point = models.Point(trip.getId(), d.getId(), timestamp, lat, lon, on_pause, dongle)

                            if event['dongle']:
                                point.dongle = int(event['dongle'])
                            if event['bt']:
                                point.bt = int(event['bt'])

                            database.db_session.add(point)                            
                            last_point = point
                except sqlalchemy.exc.IntegrityError:
                    print 'IntegrityError'
                except Exception, e:
                    print type(e).__name__
                    #status = False
                    error += 'Point error:' + e.message

        if last_point and float(request.headers['Api-Version']) < 2.1:
            driver.lat = last_point.latitude
            driver.lng = last_point.longitude
            driver.last_sync = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S') 
            driver.app_version = request.headers['App-Version']        
            database.db_session.add(driver)

        try:
            database.db_session.commit()
        except Exception, e:
            database.db_session.rollback()
            status = False
            error += 'Sync main loop error:' + e.message

        if error == '':
            error = None

        return_data = { "status" : status, "error" : error, "data" : str(len(postdata['events']))}
        print return_data
        # Save output of method
        log.setOutput(str(return_data))

        if status:
            log.setSucceeded()

        database.db_session.add(log)
        database.db_session.commit()

        print return_data
        return json.dumps(return_data)
