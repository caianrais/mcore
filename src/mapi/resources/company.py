# -*- coding: utf-8 -*-

# ...
from datetime import datetime

# ...
from . import db

# ...
from . import Company
from . import Address
from . import Proposal
from . import CompanyHasAddresses

# ...
from . import CompanySchema
from . import CompanyProposalsSchema

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


class CompanyAuth(PersonAuth):
    entity = Company


class CompanyNew(PersonNew):
    entity = Company
    schema = CompanySchema

    def post(self):
        payload = request.get_json()

        if not Validator.check_struct(payload, ['data']):
            return response.bad_request

        data = payload['data']
        required = ['address']
        if not Validator.check_struct(data, required):
            return response.bad_request

        address = data['address']

        params = [
            data.get('name'),
            data.get('email'),
            data.get('cnpj'),
            data.get('opening'),
            data.get('telephone'),
            data.get('password'),
            address.get('number'),
            address.get('postcode')
        ]

        if not Validator.check_payload(params):
            return response.bad_request

        data['opening'] = datetime.strptime(data['opening'], '%d-%m-%Y')

        company = self.new(name=data['name'],
                           email=data['email'],
                           cnpj=data['cnpj'],
                           opening=data['opening'],
                           telephone=data['telephone'])

        company.set_password(data['password'])

        address = Address(postcode=address['postcode'],
                          number=address['number'],
                          complement=address['complement'])

        db.session.add(company)
        db.session.add(address)
        db.session.commit()

        company_address = CompanyHasAddresses(company=company, address=address)

        db.session.add(company_address)
        db.session.commit()

        return response.created('companies', company.uid)


class CompanyProposals(Resource):
    def get(self, uid):
        payload = request.get_json()
        err, res = Authorizer.validate('company', payload, ['auth'])
        if err:
            return res

        company = Company.query.get(uid)
        if not company:
            return response.not_found

        proposals = Proposal.query.filter_by(company=company).all()
        proposal_schema = CompanyProposalsSchema(many=True)

        data = proposal_schema.dump(proposals)
        return response.ok(data[0])


class CompanyRecord(PersonRecord):
    entity = Company
    schema = CompanySchema
    addresses = CompanyHasAddresses
