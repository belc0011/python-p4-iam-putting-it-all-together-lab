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
    def post(self):
        request_dict = request.get_json()
        user = User.query.filter_by(username=request_dict['username']).first()
        if user:
            if user.authenticate:
                user_dict = user.to_dict()
                session['user_id'] = user.id
                response = make_response(user_dict, 200)
                return response
            else:
                return {'message': 'Error: unauthorized'}, 401
        else:
            return {'message': 'Incorrect username or password'}, 401
class Logout(Resource):
    def delete(self):
        if session['user_id']:
            session['user_id'] = None
            return {}, 204
        else:
            return {'message': 'Error, not currently logged in'}, 401

class RecipeIndex(Resource):
    def get(self):
        if session['user_id']:
            recipes = Recipe.query.filter_by(user_id=session['user_id']).all()
            recipe_list = [recipe.to_dict() for recipe in recipes]
            response = make_response(recipe_list, 200)
            return response
        else:
            return {'message': "Error: Unauthorized user"}, 401
    def post(self):
        if session['user_id']:
            userid = session['user_id']
            request_dict = request.get_json()
            print("//////PRINT STATEMENT//////", request_dict)
            try:
                new_recipe = Recipe(
                    title=request_dict['title'],
                    instructions=request_dict['instructions'],
                    minutes_to_complete=request_dict.get('minutes_to_complete'),
                    user_id=userid
                )
                db.session.add(new_recipe)
                db.session.commit()

                new_recipe_dict = new_recipe.to_dict()
                response = make_response(new_recipe_dict, 201)
                return response
            except ValueError as e:
                return {'message': str(e)}, 422
                
        else:
            return {'message': 'User not authorized'}, 401

api.add_resource(Signup, '/signup', endpoint='signup')
api.add_resource(CheckSession, '/check_session', endpoint='check_session')
api.add_resource(Login, '/login', endpoint='login')
api.add_resource(Logout, '/logout', endpoint='logout')
api.add_resource(RecipeIndex, '/recipes', endpoint='recipes')

if __name__ == '__main__':
    app.run(port=5555, debug=True)