# -*- coding: utf-8 -*-

# ...
from datetime import datetime

# ...
from . import db

# ...
from . import Offer
from . import Worker
from . import Vehicle
from . import Address
from . import WorkerHasAddresses

# ...
from . import WorkerSchema
from . import WorkerOfferSchema

# ...
from . import Resource
from . import request
from . import response

# ...
from .person import PersonNew
from .person import PersonAuth
from .person import PersonRecord

# ...
from .auth import Validator
from .auth import Authorizer


class WorkerAuth(PersonAuth):
    entity = Worker


class WorkerNew(PersonNew):
    entity = Worker
    schema = WorkerSchema

    def post(self):
        payload = request.get_json()

        if not Validator.check_struct(payload, ['data']):
            return response.bad_request

        data = payload['data']
        required = ['address', 'vehicle']
        if not Validator.check_struct(data, required):
            return response.bad_request

        address = data['address']
        vehicle = data['vehicle']

        params = [
            data.get('name'),
            data.get('telephone'),
            data.get('email'),
            data.get('password'),
            data.get('rg'),
            data.get('cpf'),
            data.get('gender'),
            data.get('birthday'),
            data.get('licenseId'),
            data.get('licenseType'),
            vehicle.get('model'),
            vehicle.get('brand'),
            vehicle.get('plate'),
            vehicle.get('year'),
            address.get('number'),
            address.get('postcode')
        ]

        if not Validator.check_payload(params):
            return response.bad_request

        data['birthday'] = datetime.strptime(data['birthday'], '%d-%m-%Y')

        worker = self.new(name=data['name'],
                          telephone=data['telephone'],
                          email=data['email'],
                          rg=data['rg'],
                          cpf=data['cpf'],
                          gender=data['gender'],
                          birthday=data['birthday'],
                          license_id=data['licenseId'],
                          license_type=data['licenseType'])

        worker.set_password(data['password'])

        address = Address(postcode=address['postcode'],
                          number=address['number'],
                          complement=address['complement'])

        db.session.add(worker)
        db.session.add(address)
        db.session.commit()

        vehicle = Vehicle(model=vehicle['model'],
                          brand=vehicle['brand'],
                          plate=vehicle['plate'],
                          year=vehicle['year'],
                          owner=worker)

        worker_address = WorkerHasAddresses(worker=worker, address=address)

        db.session.add(vehicle)
        db.session.add(worker_address)
        db.session.commit()

        return response.created('workers', worker.uid)


class WorkerOffers(Resource):
    def get(self, uid):
        payload = request.get_json()
        err, res = Authorizer.validate('worker', payload, ['auth'])
        if err:
            return res

        worker = Worker.query.get(uid)
        if not worker:
            return response.not_found

        offers = Offer.query.filter_by(bidder=worker).all()
        offer_schema = WorkerOfferSchema(many=True)

        data = offer_schema.dump(offers)
        return response.ok(data[0])


class WorkerRecord(PersonRecord):
    entity = Worker
    schema = WorkerSchema
    addresses = WorkerHasAddresses
