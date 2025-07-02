from flask import request, session
from flask_restful import Resource
from models import User, Recipe, db

class Signup(Resource):
    def post(self):
        data = request.get_json()

        try:
            new_user = User(
                username=data['username'],
                image_url=data.get('image_url'),
                bio=data.get('bio')
            )
            new_user.password_hash = data['password']

            db.session.add(new_user)
            db.session.commit()

            session['user_id'] = new_user.id

            return {
                "id": new_user.id,
                "username": new_user.username,
                "image_url": new_user.image_url,
                "bio": new_user.bio
            }, 201

        except Exception as e:
            return { "error": str(e) }, 422

class CheckSession(Resource):
    def get(self):
        user_id = session.get('user_id')

        if user_id:
            user = User.query.get(user_id)
            if user:
                return {
                    "id": user.id,
                    "username": user.username,
                    "image_url": user.image_url,
                    "bio": user.bio
                }, 200

        return { "error": "Unauthorized" }, 401

class Login(Resource):
    def post(self):
        data = request.get_json()

        user = User.query.filter_by(username=data['username']).first()

        if user and user.authenticate(data['password']):
            session['user_id'] = user.id

            return {
                "id": user.id,
                "username": user.username,
                "image_url": user.image_url,
                "bio": user.bio
            }, 200

        return { "error": "Unauthorized" }, 401

class Logout(Resource):
    def delete(self):
        if session.get('user_id'):
            session.pop('user_id')
            return {}, 204
        return { "error": "Unauthorized" }, 401

class RecipeIndex(Resource):
    def get(self):
        user_id = session.get('user_id')
        if not user_id:
            return { "error": "Unauthorized" }, 401

        recipes = Recipe.query.all()
        return [{
            "id": r.id,
            "title": r.title,
            "instructions": r.instructions,
            "minutes_to_complete": r.minutes_to_complete,
            "user": {
                "id": r.user.id,
                "username": r.user.username,
                "image_url": r.user.image_url,
                "bio": r.user.bio
            }
        } for r in recipes], 200

    def post(self):
        user_id = session.get('user_id')
        if not user_id:
            return { "error": "Unauthorized" }, 401

        data = request.get_json()
        try:
            recipe = Recipe(
                title=data['title'],
                instructions=data['instructions'],
                minutes_to_complete=data['minutes_to_complete'],
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()

            return {
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": {
                    "id": recipe.user.id,
                    "username": recipe.user.username,
                    "image_url": recipe.user.image_url,
                    "bio": recipe.user.bio
                }
            }, 201
        except Exception as e:
            return { "error": str(e) }, 422
