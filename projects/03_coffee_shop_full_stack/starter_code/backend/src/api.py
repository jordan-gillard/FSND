import os

import sqlalchemy
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()

"""
Permissions:
- `get:drinks-detail`
- `post:drinks`
- `patch:drinks`
- `delete:drinks`
"""


@app.route('/drinks')
def get_drinks(*args):
    '''
    @TODO implement endpoint
        GET /drinks
            it should be a public endpoint
            it should contain only the drink.short() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(*args):
    '''
    @TODO implement endpoint
        GET /drinks-detail
            it should require the 'get:drinks-detail' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
            or appropriate status code indicating reason for failure
    '''
    all_drinks = Drink.query.all()
    drinks = [drink.long() for drink in all_drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(*args):
    '''
    @TODO implement endpoint
        POST /drinks
            it should create a new row in the drinks table
            it should require the 'post:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
            or appropriate status code indicating reason for failure
    '''
    new_drink_dict = json.loads(request.data)
    drink = {}
    try:
        new_drink = Drink()
        new_drink.title = new_drink_dict['title']
        new_drink.recipe = json.dumps(new_drink_dict['recipe'])
        drink = new_drink.long()
        new_drink.insert()

    except:
        abort(422)

    return jsonify({
        "success": True,
        "drinks": [drink]
    })


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(*args, id):
    '''
    @TODO implement endpoint
        PATCH /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should update the corresponding row for <id>
            it should require the 'patch:drinks' permission
            it should contain the drink.long() data representation
        returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
            or appropriate status code indicating reason for failure
    '''
    print('all drinks are:')
    print(Drink.query.all())
    try:
        drink = Drink.query.filter(Drink.id == id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        abort(404)

    drink_details = json.loads(request.data)

    for key, value in drink_details.items():
        setattr(drink, key, value)
    drink_info = drink.long()
    drink.update()

    return jsonify(
        {
            "success": True,
            "drinks": drink_info
        })



@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(*args, id):
    '''
    @TODO implement endpoint
        DELETE /drinks/<id>
            where <id> is the existing model id
            it should respond with a 404 error if <id> is not found
            it should delete the corresponding row for <id>
            it should require the 'delete:drinks' permission
        returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
            or appropriate status code indicating reason for failure
    '''
    try:
        drink = Drink.query.filter(Drink.id == id).one()
    except sqlalchemy.orm.exc.NoResultFound:
        abort(404)
    drink.delete()
    return jsonify(
        {
            "success": True,
            "delete": id
        })


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(404)
def resource_not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "unauthorized"
    }), 401
