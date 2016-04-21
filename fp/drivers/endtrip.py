__author__ = 'rychol'
from .. import database, models, error
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
import json

def endTrip(data, driver):
    status = True
    error_msg = ''

    try:
        # driver = database.db_session.query(models.User).filter(models.User.id == data['driverId'], models.User.user_type==1).first()

        trip_start_date = datetime.utcfromtimestamp(int(data['startDateTrip']) / 1000)

        trip = driver.getTripForDate(trip_start_date)
        if not trip:
            trip = driver.getTripForDate(trip_start_date + timedelta(hours=1))
        if not trip:
            trip = driver.getTripForDate(trip_start_date - timedelta(hours=1))
        if not trip:
            if trip_start_date.month == datetime.today().month:
                raise error.Error('Invalid trip'+ json.dumps(data))
        else:
            end_date = datetime.utcfromtimestamp(int(data['timestamp']) / 1000)
            end_mileage = data['trip']['end_mileage']
            #TODO: CAN GET VALUES FROM data['lng'], data['lat'] below fields are useless
            end_lat = data['trip']['end_lat']
            end_lon = data['trip']['end_lon']
            job_is_done = data['trip']['isJobDone']

            address = "-"
            try:
                geolocator = Nominatim()
                location = geolocator.reverse(str(end_lat) + "," + str(end_lon))
                if location:
                    address = location.address

            except Exception, e:
                print "Geocoder timeout"
            if data['trip'].has_key('dongleConnectionTime'):
                trip.endTrip(end_date, end_mileage, end_lat, end_lon, address, job_is_done, data['trip']['dongleConnectionTime'])
            else:
                trip.endTrip(end_date, end_mileage, end_lat, end_lon, address, job_is_done, -1)
            driver.setOn_trip(False)
            if driver.driver_type:
                payroll = database.db_session.query(models.Payroll).filter_by(user = driver, for_date = end_date.strftime('%Y-%m-%d')).first()
                if payroll:
                    payroll.set_end_datetime(end_date)

    except Exception, e:
        error_msg += e.message
        status = False

    return_data = {'status': status, 'error': error_msg}
    return return_data