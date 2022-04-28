"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from sqlalchemy import true
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User
from flask_jwt_extended import get_jwt_identity, jwt_required
from flask_jwt_extended  import JWTManager,create_access_token, get_jwt_identity, jwt_required


app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY']= os.environ.get('FLASK_API_KEY')
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

jwt=JWTManager(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/user', methods=['GET'])
def handle_hello():

    response_body = {
        "msg": "Hello, this is your GET /user response "
    }

    return jsonify(response_body), 200

#endpoint para registrarse (Hacer sign up)
@app.route('/signup', methods=['POST'])
def create_user():
    body=request.json
    user=User.create(
        name=body["name"],
        email=body["email"],
        password=body["password"]
    )
    if user is not None:
        db.session.add(user)
        try:
            db.session.commit()
            return jsonify(user.serialize()),201
        except Exception as error:  
            db.session.rollback()
            return jsonify({
                "msg":"One error happened during record data"
            }),500
    else:
        return jsonify({"msg":"Check your data, there are some mistake"}),400


#endpoint para crear token (Hacer login)
@app.route('/token', methods=['POST'])
def handle_token():
    #extraer cuerpo de la solicitud
    body = request.json
    #Verificar user (existencia en BD)
    email = body['email']
    password = body['password']
    
    user = User.query.filter_by( email = email).one_or_none()
    if user is None:
        return jsonify({
            'msj': 'Invalid user'
        }),400
    #Comparar contrase;a recibida con contrase'a BD
    if password != user.password:
        #En caso de rechazo status: 400 Bad Request
        return jsonify({
            'msj': 'Bad Request'
        }),400
    #En caso OK: Generar token
    access_token = create_access_token(identity = user.id)
    #Responder Status 200 y retornar token
    return jsonify(
        {'token': access_token,
        'user': user.serialize()
        }
    ),201


@app.route('/protegido', methods=["GET"])
@jwt_required()
def handle_protegido():
    user_id = get_jwt_identity()
    return jsonify(
        {
            'user_id':user_id
        }
    ),200


# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
