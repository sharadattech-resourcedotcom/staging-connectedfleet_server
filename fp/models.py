from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String

import database
from datetime import datetime
from sqlalchemy import or_
from sqlalchemy import func
from configs import config
import re

import re

class Company(database.Base):
    __tablename__ = 'companies'

class User(database.Base):
    __tablename__ = 'users'
    tokens = relationship("Token", backref="user")
    devices = relationship("Device", backref="user")
    trips = relationship("Trip", backref="user", lazy='dynamic')
    points = relationship("Point", backref="user", lazy='dynamic')
    periods = relationship("Period", backref="user", lazy='dynamic')
    driver_type = relationship("DriverType")

    def getPassword(self):
        return self.password

    def getSalt(self):
        return self.salt

    def getId(self):
        return self.id

    def getFullName(self):
        return self.first_name + ' ' + self.last_name

    def getCompanyId(self):
        return self.company_id

    def getDevices(self):
        return self.devices

    def getOn_trip(self):
        return self.on_trip

    def setOn_trip(self, on_trip):
        self.on_trip = on_trip

    def getTrips(self):
        return self.trips

    def getPeriods(self):
        return self.periods

    def getPeriodForDate(self, date):
        return self.periods.filter(Period.start_date <= date,
                                   or_(Period.end_date == None, Period.end_date >= date)).first()
    def getTripForDate(self, date):
        return self.trips.filter(Trip.start_date == date).first()

    def setLast_login(self, last_login):
        self.last_login = last_login

    def setApiVersion(self, v):
        self.api_version = v

    def setAppVersion(self, v):
        self.app_version = v

    def check_update(self, app_version):
        update = AppVersion.check_update(self, app_version)
        if not update:
            return_data = {}
        else:
            return_data = update.serialize
        return return_data   

    def getVehicle_reg_number(self):
        t = self.trips.filter(Trip.vehicle_reg_number <> "").order_by(Trip.id.desc()).first()
        if t and t.getVehicle_reg_number() != "":
            return t.getVehicle_reg_number()
        else:
            return self.vehicle_reg_number


    def getPointWithTimeStamp(self, timestamp):
        return self.points.filter(Point.timestamp == timestamp).first()


class Device(database.Base):
    __tablename__ = 'devices'
    token = relationship("Token", uselist=False, backref="device")

    def getId(self):
        return self.id


class Token(database.Base):
    __tablename__ = 'tokens'

    def __init__(self, user_id, access, refresh, timestamp, lifetime):
        self.user_id = user_id
        self.access = access
        self.refresh = refresh
        self.timestamp = timestamp
        self.lifetime = lifetime

    def getAccess(self):
        return self.access

    def getId(self):
        return self.id

    def getTimestamp(self):
        return self.timestamp

    def getLifetime(self):
        return self.lifetime

    def getUser_id(self):
        return self.user_id

    def getRefresh(self):
        return self.refresh

    def getUser(self):
        return self.user

class Point(database.Base):
    __tablename__ = 'points'

    def clearDongleParam(self, param):
        if param == '--' or param == 'NODATA':
            return -1

        param = param.replace("km/h", "")
        param = param.replace("F", "")
        param = param.replace("mpg", "")
        param = param.replace("mph", "")
        param = param.replace(" ", "")
        param = param.replace("RPM", "")
        param = param.replace("kml", "")
        param = param.replace("Infinity", "")
        param = param.replace(",", ".")

        if param == '':
            return 0
            
        print param
        
        return (param)

    def __init__(self, trip_id, user_id, timestamp, latitude, longitude, on_pause, dongle):
        self.trip_id = trip_id
        self.user_id = user_id
        self.timestamp = timestamp
        self.latitude = latitude
        self.longitude = longitude
        self.on_pause = on_pause
        
        if dongle:
            if 'Vehicle Speed' in dongle:
                if "mph" in dongle['Vehicle Speed']:
                    self.vehicle_speed = int(int(self.clearDongleParam(dongle['Vehicle Speed'])) * 1.609) # MPH to KM/H
                else:
                    self.vehicle_speed = int(self.clearDongleParam(dongle['Vehicle Speed']))
            if 'vehicle_speed' in dongle:
                if "mph" in dongle['vehicle_speed']:
                    self.vehicle_speed = int(int(self.clearDongleParam(dongle['vehicle_speed'])) * 1.609) # MPH to KM/H
                else:
                    self.vehicle_speed = int(self.clearDongleParam(dongle['vehicle_speed']))
            if 'engine_rpm' in dongle:
                self.rpm = int(self.clearDongleParam(dongle['engine_rpm']))
            if 'fuel_economy' in dongle:
                if 'mpg' in dongle['fuel_economy']:
                    self.fuel_economy = float(self.clearDongleParam(dongle['fuel_economy'])) * 0.425143707 #MPG to KML
                else:
                    self.fuel_economy = float(self.clearDongleParam(dongle['fuel_economy']))
            if 'acceleration' in dongle:
                self.acceleration = float(self.clearDongleParam(dongle['acceleration']))
            if 'maf_air_flow' in dongle:
                self.maf = int(self.clearDongleParam(dongle['maf_air_flow']))
            if 'coolant_temp' in dongle:
                self.engine_coolant = int((float(self.clearDongleParam(dongle['coolant_temp']))-32)/1.8) #F to C



class Trip(database.Base):
    __tablename__ = 'trips'


    points = relationship("Point", backref="trip")
    job = relationship("Job")


    def __init__(self, start_location, estimated_time, start_date, start_lat, start_lon, start_mileage, reason, status,
                 user_id, period_start_date, vehicle_reg_number, period_id, vehicle_id, job_id):
        self.estimated_time = estimated_time
        self.start_date = start_date
        self.start_lat = start_lat
        self.start_lon = start_lon
        self.start_mileage = start_mileage
        self.reason = reason
        self.status = status
        self.user_id = user_id
        self.start_location = start_location
        self.period_start_date = period_start_date
        self.vehicle_reg_number = vehicle_reg_number
        self.period_id = period_id
        self.vehicle_id = vehicle_id
        self.job_id = job_id


    def getId(self):
        return self.id


    def getStatus(self):
        return self.status


    def setStatus(self, status):
        self.status = status


    def getEstimated_time(self):
        return self.estimated_time


    def getStart_date(self):
        return self.start_date


    def getStart_lat(self):
        return self.start_lat


    def getStart_lon(self):
        return self.start_lon


    def getStart_mileage(self):
        return self.start_mileage


    def getEnd_mileage(self):
        return self.end_mileage


    def getReason(self):
        return self.reason


    def getVehicle_reg_number(self):
        return self.vehicle_reg_number


    def getUser_id(self):
        return self.user_id


    def endTrip(self, end_date, end_mileage, end_lat, end_lon, end_location, job_is_done, dongle_time):
        self.end_date = end_date
        self.end_mileage = end_mileage
        self.end_location = end_location
        self.end_lat = end_lat
        self.end_lon = end_lon
        self.mileage = end_mileage - self.start_mileage
        self.dongle_time = dongle_time
        self.setStatus('finished')
        if self.job != None:
            self.job.is_done = job_is_done

    def serialize(self):
        if self.end_date:
            end_date = self.end_date.strftime('%Y-%m-%d %H:%M')
        else:
            end_date = None
        dict = {
            'id': self.id,
            'start_mileage': self.start_mileage,
            'end_mileage': self.end_mileage,
            'start_date': self.start_date.strftime('%Y-%m-%d %H:%M'),
            'end_date': end_date,
            'vehicle_reg_number': self.vehicle_reg_number,
            'private_mileage': self.private_mileage,
            'business_mileage': self.mileage
        }
        return dict


class Period(database.Base):
    __tablename__ = 'periods'

    trips = relationship("Trip", backref="period", lazy='dynamic')

    def __init__(self, user_id, start_date, start_mileage):
        self.user_id = user_id
        self.start_date = start_date
        self.start_mileage = start_mileage
        self.status = 'opened'

    def getId(self):
        return self.id

    def getStart_date(self):
        return self.start_date

    def getPeriodTrips(self):
        return database.db_session.query(Trip).filter_by(period_id=self.id)

    def getSerializedPeriodTrips(self):
        return_data = []
        trips = database.db_session.query(Trip).filter_by(period_id=self.id)
        for trip in trips:
            print trip.serialize
            return_data.append(trip.serialize())
        return return_data

    def getStart_mileage(self):
        return self.start_mileage

    def getStatus(self):
        return self.status

    def serialize(self):
        dict = {
            'id': self.id,
            'start_mileage': self.start_mileage,
            'start_date': self.start_date.strftime('%Y-%m-%d %H:%M'),
            'closing_token': self.closing_token
        }
        return dict


class Mobile_log(database.Base):
    __tablename__ = 'mobile_logs'

    def __init__(self, user_id, date, filename, reason, description):
        self.user_id = user_id
        self.date = date
        self.filename = filename
        self.reason = reason
        self.description = description


class Server_api_version(database.Base):
    __tablename__ = 'server_api_versions'

    def getVersion(self):
        return self.version

class ApiLogger(database.Base):
    __tablename__ = 'api_loggers'

    def __init__(self, user_id, type, app_v, app_v_code):
        self.user_id = user_id
        self.type = type
        self.app_version = app_v
        self.app_version_code = app_v_code
        self.created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        #self.checked = False

    def setInput(self, inputVal):
        self.input_val = inputVal

    def setSucceeded(self):
        self.succeeded = 1
    def setOutput(self, outVal):
        self.output_val = outVal

class Model(database.Base):
    __tablename__ = 'models'
    __table_args__ = {'extend_existing': True}
    #manufacturer = relationship('Manufacturer')

    def __init__(self, description, manufacturer_id):
       self.description = description
       self.manufacturer_id = manufacturer_id
       
    @staticmethod
    def find(description, manufacturer_id):
        mod = database.db_session.query(Model).filter_by(description=description, manufacturer_id = manufacturer_id).first()
        if not mod:
            return None
        return mod 

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.description
        }

class Manufacturer(database.Base):
    __tablename__ = 'manufacturers'
    __table_args__ = {'extend_existing': True}
    company = relationship('Company')

    def __init__(self, description, company_id):
       self.company_id = company_id
       self.description = description

    @staticmethod
    def find(description, company_id):
        man = database.db_session.query(Manufacturer).filter_by(description = description, company_id = company_id).first()
        if not man:
            return None
        return man 

    @property
    def serialize(self):
        return {
            'id': self.id,
            'name': self.description
        }

class Vehicle(database.Base):
    __tablename__ = 'vehicles'
    __table_args__ = {'extend_existing': True}
    manufacturer = relationship('Manufacturer')
    model = relationship('Model')

    def __init__(self, registration, company_id):
        self.registration = registration
        self.company_id = company_id
        self.manufacturer = database.db_session.query(Manufacturer).filter_by(description="Unknown").first()
        self.model = database.db_session.query(Model).filter_by(description="Unknown").first()

    def assignManfacAndModel(self, manufacturer, model, company_id):
        man = Manufacturer.find(manufacturer, company_id)
        if not man:
            man = Manufacturer(manufacturer, company_id)
            database.db_session.add(man)
        mod = Model.find(model, man.id)
        if not mod:
            mod = Model(model, man.id)
            database.db_session.add(mod)
            mod = Model.find(model, man.id)
        self.manufacturer = man
        self.model = mod

    @staticmethod    
    def fixed_registration(registration):
        return re.sub(r'\W',r'',registration).upper()

    @property
    def serialize(self):
        dict = {
            'id': self.id,
            'registration': self.registration,
            'manufacturer_id': self.manufacturer_id,
            'model_id': self.model_id,
            'manufacturer': database.db_session.query(Manufacturer).filter_by(id=self.manufacturer_id).first().serialize,
            'model': database.db_session.query(Model).filter_by(id=self.model_id).first().serialize
        }
        return dict

    @staticmethod    
    def fixed_registration(registration):
        return re.sub(r'\W',r'',registration).upper()

class Branch(database.Base):
    __tablename__ = 'branches'
    __table_args__ = {'extend_existing': True}

class Product(database.Base):
    __tablename__ = 'products'
    __table_args__ = {'extend_existing': True}

class Appointment(database.Base):
    __tablename__ = 'appointments'
    __table_args__ = {'extend_existing': True}
    branch = relationship("Branch")
    product = relationship("Product")

class Job(database.Base):
    __tablename__ = 'jobs'
    __table_args__ = {'extend_existing': True}

    appointment = relationship("Appointment")
    at = datetime.utcnow()

    def getJobTypeName(self):
        if self.job_type == "D":
            return 'Delivery'
        elif self.job_type == "C":
            return 'Collection'
        elif self.job_type == "T":
            return 'Travel'
        return ''

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        dict = {
           'id'   : self.id,
           'name' : str(self.job_type) + self.number ,
           'postcode' : self.appointment.postcode,
           'city' : self.appointment.city,
           'street' : self.appointment.street,
           'street2' : self.appointment.street2,
           'home_number' : self.appointment.home_number,
           'number': self.number,
           'description' : self.appointment.branch.description +' - '+self.appointment.product.description,
           'abort_code' : self.abort_code,
           'notes' : self.appointment.notes,
           'type': self.job_type,
           'address': self.appointment.street,
           "insurer": self.appointment.insurer,
           "vatstatus": self.appointment.vatstatus,
           "contact_name": self.appointment.contact_name,
           "customer_name": self.appointment.contact_name,
           "home_phone": self.appointment.home_phone,
           "work_phone": self.appointment.work_phone,
           "courtesy_car": self.appointment.courtesy_car,
           "excess": self.appointment.excess
        }

        if self.job_type == "C":
            dict["city"] = self.appointment.col_city
            dict["street"] = self.appointment.col_street
            dict["postcode"] = self.appointment.col_postcode
            dict["address"] = self.appointment.col_street

        # if self.postcode:
        #     dict['name'] += " - " + self.postcode
        b = None
        
        #dict['loan'] = '01/09/2015-03/09/2015'

        # if self.jobable_id > 0:
        #     b = database.db_session.query(Booking).filter_by(id=self.jobable_id).first()

        #     if self.job_type == 'C':
        #         dict['address'] = b.getCollectionAddress()
        #     if self.job_type == 'D':
        #         dict['address'] = b.getDeliveryAddress()

        # if self.job_type == 'L':
        #     parent_job = database.db_session.query(Job).filter_by(id=self.parent_id).first()
        #     if parent_job:
        #         lifting = database.db_session.query(User).filter_by(id=parent_job.user_id).first()
        #         if lifting:
        #             dict['description'] = 'You will be lifted by ' + lifting.firstname + ' ' + lifting.surname + ' ('+ lifting.work_phone + ')'
        #             dict['description'] += ' from ' + self.start_postcode + ' to ' + self.postcode
        # elif self.job_type == 'T':
        #     dict['description'] = 'Travel by ' + self.travel_type


        # if b:
        #     dict['booking'] = b.serialize
        #     dict['loan'] = b.del_datetime.strftime("%d/%m/%Y") + " - " + b.col_datetime.strftime("%d/%m/%Y")

        if self.end_date:
            dict['date_time_to'] = self.end_date.strftime('%Y-%m-%d %H:%M')

        if self.start_date:
            dict['date'] = self.start_date.strftime('%Y-%m-%d')
            dict['date_time'] = self.start_date.strftime('%Y-%m-%d %H:%M')
            dict['date_time_at'] = self.start_date.strftime('%Y-%m-%d %H:%M')

        # if not (self.job_type == 'C' or self.job_type == 'D'):
        #     dict['name'] = self.job_number
        #     if self.postcode:
        #         dict['name'] += ' - ' + self.postcode        
        
        v = None

        if self.appointment.vehicle_id > 0:
            v = database.db_session.query(Vehicle).filter_by(id=self.appointment.vehicle_id).first()
            if v:
                dict['vehicle'] = v.serialize

        dict['legal_words'] = []
        dict['loose_items'] = []
        dict['yes_no_questions'] = []
        
        # if b and (self.job_type == 'C' or self.job_type == 'D'):           
        #     if self.job_type == 'C':
        #         lwdid = b.col_legal_doc_id
        #     elif self.job_type == 'D':
        #         lwdid = b.del_legal_doc_id

        #     lwd = database.db_session.query(LegalWordDoc).filter_by(id=lwdid).first()

        #     if lwd:
        #         words = database.db_session.query(LegalWord).filter_by(words_doc_id=lwdid)
        #         for l in words:
        #             dict['legal_words'].append(l.serialize)
        dict['loose_items'] = [{'id': 1, 'name': 'Handbook'}, {'id': 2, 'name': 'Floor Mats'}, {'id': 3, 'name': 'Inflation Kit'},
        {'id': 4, 'name': 'Jack & Tool Kit'}, {'id': 5, 'name': 'Locking Wheel Nut Kit'}, {'id': 6, 'name': 'Load Cover'}, 
        {'id': 7, 'name': 'Sat. Nav. SD Card/Becker'}, {'id': 8, 'name': 'Media Cables'}, {'id': 9, 'name': '1st Aid Kit'}, 
        {'id': 10, 'name': '2x Hi Viz'}, {'id': 11, 'name': 'Fold Down Basket'}, {'id': 12, 'name': 'ADR Card'},
        {'id': 13, 'name': 'Charge Cable (S)'}, {'id': 14, 'name': 'EV Charging Cable (S)'}, {'id': 15, 'name': 'Spare Wheel / Tyre Inflation Kit'}]
        #         # items = database.db_session.query(LooseItemConstans).filter_by(words_doc_id=lwdid)
        #         # for l in items:
        #         #     dict['loose_items'].append(l.serialize)
        dict['legal_words'] = [{'content': 'Delivery Representative', 'field_type': 'signature', 'placeholder': 'Signature', 'id': 1},
          # {'content': '', 'field_type': 'name', 'placeholder': 'Name', 'id': 2},
          # {'content': 'I receive the vehicle as recorded and noted by the driver and agree to the terms and conditions as sent via email.', 'field_type': 'signature', 'placeholder': 'Customer Signature', 'id': 3},
          {'content': '','field_type': 'name','placeholder': 'Name', 'id': 4},
          {'content': '','field_type': 'date_time', 'placeholder': 'Date and Time', 'id': 5}]

        if self.appointment.company_id == 3:
            dict['legal_words'].append({'content': "",'field_type': 'email', 'placeholder': 'Email', 'id': 7})
            dict['legal_words'].append({'content': "Statement of Liability:: I agree that while the rental agreement is in force I will be liable for any fixed penalty offence or parking charge for that vehicle under S66 Road Traffic Offenders Act 1988 and schedule 6 Road Traffic Act 1991 or as subsequently amended.",'field_type': 'text', 'placeholder': '', 'id': 6})

        dict['extra_notes'] = ''
        dict['notes'] = ''        

        return dict

    @staticmethod
    def nojob(company_id):
        dict = {
           'id'   : -1,
           'name' : 'NO JOB',
           'postcode' : '',
           'city' : '',
           'street' : '',
           'home_number' : '',
           'number': '',
           'description' : '',
           'abort_code' : '',
           'notes' : '',
           'type': 'D',
           'address': ''
        }

        dict['yes_no_questions'] = []
        dict['loose_items'] = [{'id': 1, 'name': 'Handbook'}, {'id': 2, 'name': 'Floor Mats'}, {'id': 3, 'name': 'Inflation Kit'},
        {'id': 4, 'name': 'Jack & Tool Kit'}, {'id': 5, 'name': 'Locking Wheel Nut Kit'}, {'id': 6, 'name': 'Load Cover'}, 
        {'id': 7, 'name': 'Sat. Nav. SD Card/Becker'}, {'id': 8, 'name': 'Media Cables'}, {'id': 9, 'name': '1st Aid Kit'}, 
        {'id': 10, 'name': '2x Hi Viz'}, {'id': 11, 'name': 'Fold Down Basket'}, {'id': 12, 'name': 'ADR Card'},
        {'id': 13, 'name': 'Charge Cable (S)'}, {'id': 14, 'name': 'EV Charging Cable (S)'}, {'id': 15, 'name': 'Spare Wheel / Tyre Inflation Kit'}]

        dict['legal_words'] = [{'content': 'Delivery Representative', 'field_type': 'signature', 'placeholder': 'Signature', 'id': 1},
          {'content': '','field_type': 'name','placeholder': 'Name', 'id': 4},
          {'content': '','field_type': 'date_time', 'placeholder': 'Date and Time', 'id': 5}]

        if company_id == 3:
            dict['legal_words'].append({'content': "",'field_type': 'email', 'placeholder': 'Email', 'id': 7})
            dict['legal_words'].append({'content': "Statement of Liability:: I agree that while the rental agreement is in force I will be liable for any fixed penalty offence or parking charge for that vehicle under S66 Road Traffic Offenders Act 1988 and schedule 6 Road Traffic Act 1991 or as subsequently amended.",'field_type': 'text', 'placeholder': '', 'id': 6})


        dict['extra_notes'] = ''
        dict['notes'] = ''

        return dict

class MobileInspection(database.Base):

    __tablename__ = 'mobile_inspections'

    def __init__(self, inspection_dict, user_id, job_id, vehicle_id, loose_items, questions, notes, mileage, terms_file, email, city, postcode, address_line_1, address_line_2, home_number, customer_name):
        j = database.db_session.query(Job).filter_by(id=job_id).first()
            
        if j:
            #self.bookings_id = j.jobable_id
            self.job_id = j.id 

        if inspection_dict.has_key('jobType'):
            self.job_type = inspection_dict['jobType'] 
        if inspection_dict.has_key('refNumber'):
            self.ref_number = inspection_dict['refNumber'] 
        # print inspection_dict
        # raise 'x'
        self.customer_email = email 
        self.city = city 
        self.postcode = postcode 
        self.address_line_1 = address_line_1 
        self.address_line_2 = address_line_2 
        self.home_number = home_number 
        self.created_at = datetime.utcnow()  
        self.loose_items = loose_items 
        self.questions = questions 
        self.user_id = user_id 
        self.vehicle_id = vehicle_id 
        self.notes = notes 
        self.mileage = mileage 
        self.terms_file_name = terms_file 
        self.customer_name = customer_name 


class DamageItem(database.Base):
    mobile_inspection = relationship("MobileInspection")

    __tablename__ = 'damage_items'

    def __init__(self, description, local_id, timestamp, collection_id, driver_id, insp):
        self.local_id = local_id
        self.mobile_inspection = insp
        self.user_id = driver_id
        self.description = description
        self.inspection_datetime = timestamp
        self.collection_id = collection_id

    @staticmethod
    def attach_file(file_name, local_id, driver_id):
        lid = local_id.replace('damage_item_id[', '').replace(']', '')
        lid = lid.split("|") 

        d = database.db_session.query(DamageItem).filter_by(local_id=lid[1], user_id=driver_id, inspection_datetime=lid[0]).first()
        
        if d:
            d.file_path = file_name
            database.db_session.add(d)
            return d
        else:
            print 'Damage not found'

        return None

class DamageCollection(database.Base):
    __tablename__ = 'damage_collections'
    mobile_inspection = relationship("MobileInspection")

    def __init__(self, collection, insp):
        self.collection_id = collection['collectionId']
        self.description = collection.get('description', None)
        self.mobile_inspection = insp
        self.collection_type = collection['collectionType']
        self.dual_tyres = collection.get('dualTyres', None)
        self.x_percent = collection['xPercent']
        self.y_percent = collection['yPercent']
        self.spare = None
        if collection.get("spare") and collection.get("spare") != "":
            self.spare = collection.get('spare', None)
        if collection.get("driverBack") and collection.get("driverBack") != "":
            self.driver_back = collection.get('driverBack', None)
        if collection.get("passengerBack") and collection.get("passengerBack") != "":
            self.passenger_back = collection.get('passengerBack', None)
        if collection.get("driverFront") and collection.get("driverFront") != "":
            self.driver_front = collection.get('driverFront', None)
        if collection.get("passengerFront") and collection.get("passengerFront") != "":
            self.passenger_front = collection.get('passengerFront', None)


class DriverType(database.Base):
    __tablename__ = 'driver_types'

    def __init__(self, company_id, name, hourly_rate, additional_hour_rate):
        self.company_id = company_id
        self.name = name
        self.hourly_rate = hourly_rate
        self.additional_hour_rate = additional_hour_rate

class Payroll(database.Base):
    user = relationship("User")
    __tablename__ = 'payrolls'

    def __init__(self, user, for_date, start_datetime):
        self.user = user
        self.for_date = for_date
        self.start_datetime = start_datetime

    def set_end_datetime(self, datetime):
        self.end_datetime = datetime

    @staticmethod
    def create_if_not_exist(user, for_date, start_datetime):
        payroll = database.db_session.query(Payroll).filter_by(user = user, for_date = for_date).first()
        if not payroll:
            if user.driver_type:
                payroll = Payroll(user, for_date, start_datetime)
                database.db_session.add(payroll)
                return True
        else:
            return True
        return False

class AppVersion(database.Base):
    __tablename__ = 'app_versions'

    def __init__(self, company_id, version_name, version_code, comment, file_path, private):
        self.company_id = company_id
        self.version_name = version_name
        self.version_code = version_code
        self.comment = comment
        self.file_path = file_path
        self.internal_group = private

    @property
    def serialize(self):
        dict = {
           'url'   : config.DOWNLOAD_URL+self.file_path,
           'version' : self.version_name,
           'whatsnew' : self.comment,
           'title' : "Version "+str(self.version_name)+" is now available."
        }
        return dict

    @staticmethod
    def check_update(user, version_code):
        builds = database.db_session.query(AppVersion).filter_by(company_id = user.company_id, internal_group = user.internal_staff)
        update = None
        for b in builds:
            if float(b.version_code) > float(version_code):
                if update == None:
                    update = b
                elif float(b.version_code) > float(update.version_code):
                    update = b
        if update != None:
            return update
        return False

class DisposalInspection(database.Base):

    __tablename__ = 'disposal_inspections'

    def __init__(self, user_id, local_id, timestamp, vehicle_registration):
        self.user_id = user_id
        self.local_id = local_id
        self.inspection_timestamp = datetime.utcfromtimestamp(int(timestamp)/1000)
        self.vehicle_registration = vehicle_registration

class DisposalPhoto(database.Base):
    disposal_inspection = relationship("DisposalInspection")

    __tablename__ = 'disposal_photos'

    def __init__(self, path, ftp_filename, insp):
        self.disposal_inspection = insp
        self.path = path
        self.ftp_filename = ftp_filename

    @staticmethod
    def attach_file(file_path, local_id, driver_id):
        lid = local_id.replace('disposal_photo[', '').replace(']', '')
        lid = lid.split("|") 
        print "********************"
        print lid[1], driver_id, datetime.utcfromtimestamp(int(lid[0])/1000)
        insp = database.db_session.query(DisposalInspection).filter_by(local_id=lid[1], user_id=driver_id, inspection_timestamp=datetime.utcfromtimestamp(int(lid[0])/1000)).first()
        ftp_filename = insp.vehicle_registration + lid[2] + ".jpg"

        photo = DisposalPhoto(file_path, ftp_filename, insp)
        database.db_session.add(photo)
        # d = database.db_session.query(DisposalInspection).filter_by(local_id=lid[1], user_id=driver_id, inspection_datetime=datetime.utcfromtimestamp(int(lid[0])/1000)).first()
        

        return None

class UploadLog(database.Base):
    __tablename__ = 'upload_logs'

    def __init__(self, user, headers, succeeded, method, error, ip):
        self.user_id = user.id
        self.company_id = user.company_id
        self.created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.app_version = headers['App-Version']
        self.device_model = headers['Device-Model']
        self.app_version_code = headers['App-Version-Code']
        self.app_type = headers['App-Type']
        self.method = method
        self.succeeded = succeeded
        self.ip = ip
        self.error_message = error
