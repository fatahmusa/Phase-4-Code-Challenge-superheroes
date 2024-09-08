from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)

class Hero(db.Model, SerializerMixin):
    __tablename__ = 'heroes'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    super_name = db.Column(db.String)

    # add relationship

    # Relationship mapping the hero to related hero_powers
    hero_powers = db.relationship('HeroPower', back_populates='hero', cascade='all, delete-orphan')

    # Association proxy to get power for this hero through hero_powers
    powers = association_proxy('hero_powers', 'power',
                                 creator=lambda power_obj: HeroPower(power=power_obj))


    # add serialization rules

    serialize_rules = ('-hero_powers',)

    def to_dict(self, include_powers=False):
        data = {
            'id': self.id,
            'name': self.name,
            'super_name': self.super_name,
            "powers": [power.id for power in self.powers],
            
        }

        if include_powers:
            data["hero_powers"] = [hp.to_dict() for hp in self.hero_powers]
        return data


    def __repr__(self):
        return f'<Hero {self.id}>'


class Power(db.Model, SerializerMixin):
    __tablename__ = 'powers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    description = db.Column(db.String)

    # add relationship

    hero_powers = db.relationship('HeroPower', back_populates='power', cascade='all, delete-orphan')

    heroes = association_proxy('hero_powers', 'hero', creator=lambda hero_obj: HeroPower(hero=hero_obj))


    # add serialization rules

    serialize_rules = ('-hero_powers',)


    # add validation

    @validates('description')
    def validate_description(self, name, description):
        if len(description)<20:
            raise ValueError("Description must be atleast 20 characters long.")
        return description

    def __repr__(self):
        return f'<Power {self.id}>'


class HeroPower(db.Model, SerializerMixin):
    __tablename__ = 'hero_powers'

    id = db.Column(db.Integer, primary_key=True)
    strength = db.Column(db.String, nullable=False)

    # Foreign key to store the hero id
    hero_id = db.Column(db.Integer, db.ForeignKey('heroes.id'))
    # Foreign key to store the power id
    power_id = db.Column(db.Integer, db.ForeignKey('powers.id'))

    # add relationships
    # Relationship mapping the HeroPower to related hero
    hero = db.relationship('Hero', back_populates='hero_powers')

    # Relationship mapping the HeroPower to related power
    power = db.relationship('Power',back_populates='hero_powers')


    # add serialization rules
    serialize_rules = ('-hero', '-power')

    # add validation

    @validates('strength')
    def validate_strength(self, key, strength):
        if strength not in ['Strong', 'Weak', 'Average']:
            raise ValueError("Strength must be of one of Strong, Weak or Average")
        return strength

    def __repr__(self):
        return f'<HeroPower {self.id}>'
