#!/usr/bin/env python3

from flask import Flask, request, make_response, jsonify
from flask_migrate import Migrate
from flask_restful import Api, Resource
from models import db, Hero, Power, HeroPower
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def index():
    return '<h1>Code challenge</h1>'

@app.route('/heroes', methods=['GET'])
def get_heroes():
    heroes = Hero.query.all()
    return jsonify([hero.to_dict(include_powers=False) for hero in heroes]), 200

@app.route('/heroes/<int:id>', methods=['GET'])
def get_hero(id):
    hero = db.session.get(Hero, id)
    if hero is None:
        return jsonify({
        'error': 'Hero not found'
    }), 404 

    return jsonify(hero.to_dict(include_powers= True)), 200

@app.route('/powers', methods=['GET'])
def get_powers():
    powers = Power.query.all()
    return jsonify([power.to_dict() for power in powers]), 200

@app.route('/powers/<int:id>', methods=['GET'])
def get_power(id):
    power = db.session.get(Power, id)
    if power is None:
        return jsonify({
        'error': 'Power not found'
    }), 404 

    return jsonify(power.to_dict()), 200

@app.route('/powers/<int:id>', methods=['PATCH'])
def update_power(id):
    data = request.get_json()
    power = db.session.get(Power, id)

    if power is None:
        return jsonify({
            'error': 'Power not found'
        }), 404
    
    if 'description' in data:
        description= data['description']
        if not isinstance (description, str) or len(description)<20:
            return jsonify({
                'errors': ['validation errors']
            }), 400
        power.description = description
    db.session.commit()
    return jsonify({
        'id': power.id,
        'name': power.name,
        'description': power.description
    })

@app.route('/hero_powers', methods=['POST'])
def creates_hero_powers():
    data = request.get_json()

    hero_id = data.get('hero_id')
    power_id = data.get('power_id')
    strength = data.get('strength')

    if not hero_id or not power_id or strength is None:
        return jsonify({'error': 'Missing data'}), 400

    if strength not in ['Strong', 'Weak', 'Average']:
        return jsonify({'errors': ['validation errors']}), 400

    hero = db.session.get(Hero, hero_id)
    power = db.session.get(Power, power_id)

    if not hero or not power:
        return jsonify({'error': 'Hero or Power not found'}), 404



    hero_power = HeroPower( hero_id=hero_id, power_id=power_id, strength=strength)
    db.session.add(hero_power)
    db.session.commit()

    return jsonify({
        "id": hero_power.id,
        "hero_id": hero_power.hero_id,
        "power_id": hero_power.power_id,
        "strength": hero_power.strength,
        "hero": {
            "id": hero.id,
            "name": hero.name,
            "super_name": hero.super_name,
        },
        "power": {
            "id": power.id,
            "name": power.name,
            "description": power.description    
        }
        
    }), 201

    


if __name__ == '__main__':
    app.run(port=5555, debug=True)
