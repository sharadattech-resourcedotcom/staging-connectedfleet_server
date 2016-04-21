from .. import database, models, error
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim

import traceback

def startTrip(data, driver):
    status = True
    error_msg = ''

    try:
    # raise error.Error(data)
        start_date = datetime.utcfromtimestamp(int(data['startDateTrip']) / 1000)
        job_id = None
        period = driver.getPeriodForDate(start_date)
        if period is None:
            period = models.Period(driver.getId(), start_date, data['trip']['start_mileage'])
            database.db_session.add(period)

        trip = database.db_session.query(models.Trip).filter(models.Trip.user_id == data['driverId'], models.Trip.start_date==start_date).first()
        if not trip:
            trip = database.db_session.query(models.Trip).filter(models.Trip.user_id == data['driverId'], models.Trip.start_date==(start_date + timedelta(hours=1))).first()
        if not trip:
            trip = database.db_session.query(models.Trip).filter(models.Trip.user_id == data['driverId'], models.Trip.start_date==(start_date - timedelta(hours=1))).first()
        if not trip:
            #TODO: CONFLICT! DISCUSS CASE WHEN ADDING TRIP TO CLOSED PERIOD? MIGHT HAPPEND DO WE ADD THIS TRIP TO DB OR PRINT EXCEPTION TO MOBILE
            # if period.getStatus() != 'opened':
            # 	raise error.Error('Period for this trip is closed')
            estimated_time = data['trip']['estimated_time']

            estimated_time = timedelta(seconds=estimated_time)

            #TODO: DISCUSS IF CHCECKIN START MILEAGE WITH PERIOD AND SURROUNDING TRIPS


            #TODO: CAN GET VALUES FROM data['lng'], data['lat'] below fields are useless
            start_lat = data['trip']['start_lat']
            start_lon = data['trip']['start_lon']
            start_mileage = data['trip']['start_mileage']

            if data['trip'].has_key('reason'):
                reason = data['trip']['reason']
            else:
                reason = 'Business'

            vehicle_reg_number = ''
            if data['trip'].has_key('vehicleRegistrationNumber') or int(data['trip']['jobId']) == -1:
                print data['trip']
                if int(data['trip']['jobId']) == -1:
                    vehicle_reg_number = 'NOJOB'
                else:                    
                    vehicle_reg_number = models.Vehicle.fixed_registration(data['trip']['vehicleRegistrationNumber'])

                v = database.db_session.query(models.Vehicle).filter_by(registration=vehicle_reg_number).first()
                if not v:
                    v = models.Vehicle(vehicle_reg_number, driver.getCompanyId())
                    database.db_session.add(v)
                    v = database.db_session.query(models.Vehicle).filter_by(registration=vehicle_reg_number).first()

            elif data['trip'].has_key('jobId'):
                job_id = data['trip']['jobId']
                vehicle_reg_number = database.db_session.query(models.Job).filter(models.Job.id == job_id).first().serialize['vehicle']['registration']
                v = database.db_session.query(models.Vehicle).filter_by(registration=vehicle_reg_number).first()
                
            address = "-"
            
            try:
                geolocator = Nominatim()
                location = geolocator.reverse(str(start_lat) + "," + str(start_lon))
                if location:
                    address = location.address

            except Exception, e:
                print "Geocoder timeout"

            trip = models.Trip(address, estimated_time, start_date, start_lat, start_lon, start_mileage, reason, 'active', driver.getId(), period.getStart_date(), vehicle_reg_number, period.getId(), v.id, job_id)
            payroll = models.Payroll.create_if_not_exist(driver, start_date.strftime('%Y-%m-%d'), start_date)

            database.db_session.add(trip)
            driver.setOn_trip(True)
    except Exception, e:
        error_msg += traceback.format_exc()
        status = False
        print 'Star trip error'+ e.message

    if status == False:
        raise error.Error('Trip could not be started' + error_msg)

    return_data = {'status': status, 'error': error_msg}
    return return_data