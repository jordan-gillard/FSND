import sqlalchemy
from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

db_drop_and_create_all()


@app.route('/drinks')
def get_drinks(*args):
    """
    Returns a JSON response containing a short description
    of all drinks in the database.
    Returns:
        {
        "success": True,
        "drinks": drinks
    }
    where drinks is an array of all drink's short description.
    """
    all_drinks = Drink.query.all()
    drinks = [drink.short() for drink in all_drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_detail(*args):
    """
    Returns the long description for all drinks in the
    database.
    Returns:
        {
        "success": True,
        "drinks": drinks
    }
    where drinks is an array of all drink's long description.
    """
    all_drinks = Drink.query.all()
    drinks = [drink.long() for drink in all_drinks]
    return jsonify({
        "success": True,
        "drinks": drinks
    })


@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def post_drinks(*args):
    """
    Adds a new drink to the database and returns
    {
        "success": True,
        "drinks": [drink]
    }
    if successful, else aborts 422.
    """
    new_drink_dict = json.loads(request.data)
    try:
        new_drink = Drink()
        new_drink.title = new_drink_dict['title']
        new_drink.recipe = json.dumps(new_drink_dict['recipe'])
        new_drink.insert()

    except:
        abort(422)

    drink = Drink.query.filter(Drink.title == new_drink_dict['title']).one()
    drink = drink.long()
    return jsonify({
        "success": True,
        "drinks": [drink]
    })


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def patch_drink(*args, id):
    """
    Edits the drink with the given id.
    Returns:
        {
            "success": True,
            "drinks": [drink_info]
        }
    where drink_info is the drinks with the given id's
    long description.
    """
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
            "drinks": [drink_info]
        })


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(*args, id):
    """
    Deletes the drink with the given id from the database.
    Returns:
        {
            "success": True,
            "delete": id
        }
    where id is the id of the deleted drink.
    """
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


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        "success": False,
        "error": 400,
        "message": "bad request"
    }), 400


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
