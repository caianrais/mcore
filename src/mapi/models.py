# -*- coding: utf-8 -*-

"""
--- TODO: DOCUMENTATION ---
"""

# Primitive types
from mapi.db import (Bol, Flo, Dat, Int, Str)

# Database objects
from mapi.db import (Col, Mod)

# Relations
from mapi.db import (BR, FK, Rel)


class Entity(Mod):
    """
    --- TODO: DOCUMENTATION ---
    """
    __abstract__ = True

    uid = Col(Int, primary_key=True, autoincrement=True)

    def R(self, attrs):
        """
        --- TODO: DOCUMENTATION ---
        """
        class_name = type(self).__name__
        attributes = ', '.join("'{0}'".format(attr) for attr in attrs)

        return '<{0} {1}>'.format(class_name, attributes)

    def __attr__(self):
        """
        --- TODO: DOCUMENTATION ---
        """
        pass


class Relation(Mod):
    """
    --- TODO: DOCUMENTATION ---
    """
    __abstract__ = True


class Person(Entity):
    """
    --- TODO: DOCUMENTATION ---
    """
    __abstract__ = True

    name      = Col(Str(64), nullable=False)
    telephone = Col(Str(11), nullable=False)
    email     = Col(Str(64), nullable=False, index=True, unique=True)
    passhash  = Col(Str(128))

    def __attr__(self):
        return self.R([self.name, self.email])


class Company(Person):
    """
    --- TODO: DOCUMENTATION ---
    """
    __tablename__ = 'company'

    cnpj    = Col(Str(14), nullable=False, index=True, unique=True)
    opening = Col(Dat, nullable=False)

    def __repr__(self):
        return self.R([self.name, self.cnpj])


class Worker(Person):
    """
    --- TODO: DOCUMENTATION ---
    """
    __tablename__ = 'worker'

    # Fields
    rg           = Col(Str(9), nullable=False, index=True, unique=True)
    cpf          = Col(Str(11), nullable=False, index=True, unique=True)
    birthday     = Col(Dat, nullable=False)
    license_id   = Col(Str, nullable=False, index=True, unique=True)
    license_type = Col(Str, nullable=False)

    # Relations
    vehicles = Rel('Vehicle', back_populates='owner')

    def __repr__(self):
        return self.R([self.name, self.cpf])


class Address(Entity):
    """
    --- TODO: DOCUMENTATION ---
    """
    __tablename__ = 'address'

    number     = Col(Str(8))
    complement = Col(Str(16), nullable=True)
    postcode   = Col(Str(8), index=True)

    # Relations
    workers = Rel(Worker, secondary='worker_addr_assoc')
    companies = Rel(Company, secondary='company_addr_assoc')

    def __repr__(self):
        return self.R([self.postcode, self.number])


class Vehicle(Entity):
    """
    --- TODO: DOCUMENTATION ---
    """
    __tablename__ = 'vehicle'

    # Fields
    license = Col(Str(11), nullable=False, index=True, unique=True)
    model   = Col(Str(32), nullable=False)
    brand   = Col(Str(24), nullable=False)
    plate   = Col(Str(8), nullable=False)
    year    = Col(Int, nullable=False)

    # Foreign keys
    owner_uid = Col(Int, FK('worker.uid'))

    # Relations
    owner = Rel(Worker, back_populates='vehicles')

    def __repr__(self):
        return self.R([self.brand, self.year])


class Proposal(Entity):
    """
    --- TODO: DOCUMENTATION ---
    """
    __tablename__ = 'proposal'

    # Fields
    deadline = Col(Dat, nullable=False)

    # Foreign keys
    origin_addr_uid = Col(Int, FK('address.uid'))
    destin_addr_uid = Col(Int, FK('address.uid'))
    company_uid = Col(Int, FK('company.uid'))

    # Relations
    orig_address = Rel(Address, foreign_keys='Proposal.origin_addr_uid',
                       backref=BR('orig_assoc', uselist=False))

    dest_address = Rel(Address, foreign_keys='Proposal.destin_addr_uid',
                       backref=BR('dest_assoc', uselist=False))

    company = Rel(Company, backref=BR('company_assoc', uselist=False))


class Item(Entity):
    """
    --- TODO: DOCUMENTATION ---
    """
    __tablename__ = 'item'

    fragile = Col(Bol, nullable=False)
    weight  = Col(Flo, nullable=False)
    width   = Col(Flo, nullable=False)
    height  = Col(Flo, nullable=False)

    # Relations
    Proposals = Rel(Proposal, secondary='proposal_item_assoc')


class Offer(Entity):
    """
    --- TODO: DOCUMENTATION ---
    """
    __tablename__ = 'offer'

    price = Col(Flo, nullable=False)

    # Foreign keys
    worker_uid = Col(Int, FK('worker.uid'), primary_key=True)


class ProposalItemAssoc(Relation):
    """
    --- TODO: DOCUMENTATION ---
    """
    __tablename__ = 'proposal_item_assoc'

    # Foreign keys
    proposal_uid = Col(Int, FK('proposal.uid'), primary_key=True)
    item_uid     = Col(Int, FK('item.uid'), primary_key=True)

    # Relations
    proposal = Rel(Proposal, backref=BR('item_assoc'))
    item     = Rel(Item, backref=BR('proposal_assoc'))


class WorkerAddressAssoc(Relation):
    """
    --- TODO: DOCUMENTATION ---
    """
    __tablename__ = 'worker_addr_assoc'

    # Foreign keys
    worker_uid = Col(Int, FK('worker.uid'), primary_key=True)
    address_uid = Col(Int, FK('address.uid'), primary_key=True)

    # Relations
    worker  = Rel(Worker, backref=BR('address_assoc'))
    address = Rel(Address, backref=BR('worker_assoc'))


class CompanyAddressAssoc(Relation):
    """
    --- TODO: DOCUMENTATION ---
    """
    __tablename__ = 'company_addr_assoc'

    # Foreign keys
    company_uid = Col(Int, FK('company.uid'), primary_key=True)
    address_uid = Col(Int, FK('address.uid'), primary_key=True)

    # Relations
    company = Rel(Company, backref=BR('address_assoc'))
    address = Rel(Address, backref=BR('company_assoc'))
