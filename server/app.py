#!/usr/bin/env python3

from flask import request, session, make_response
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import app, db, api
from models import User, Recipe

class Signup(Resource):
    def post(self):
        request_dict = request.get_json()
        if 'username' not in request_dict or 'password' not in request_dict or 'image_url' not in request_dict or 'bio' not in request_dict:
            return {'message': 'Missing necessary attributes'}, 422
        else:
            new_user = User(
                username=request_dict['username'], 
                image_url=request_dict['image_url'], 
                bio=request_dict['bio'])
            new_user.password_hash = request_dict['password']
            
            db.session.add(new_user)
            db.session.commit()
            new_user_dict = new_user.to_dict()
            session['user_id'] = new_user.id
            response = make_response(new_user_dict, 201)
            return response
        

class CheckSession(Resource):
    def get(self):
        if session['user_id']:
            user = User.query.filter_by(id=session['user_id']).first()
            response = make_response(user.to_dict(), 200)
            return response
        else:
            return {'message': 'Error, unauthorized user'}, 401

class Login(Resource):
    pass

class Logout(Resource):
    pass

class RecipeIndex(Resource):
    pass

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)