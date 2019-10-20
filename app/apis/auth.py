from flask import request
from flask_restplus import Namespace, Resource, fields

from app.service.auth_helper import Auth

api = Namespace('auth',
                path='/',
                description='Operations related to authentication')


user_auth = api.model('auth_details', {
    'username': fields.String(required=True, description='The username'),
    'password': fields.String(required=True, description='The user password'),
})


@api.route('/login')
class UserLogin(Resource):
    """
        User Login Resource
    """
    @api.doc('user login')
    @api.expect(user_auth, validate=True)
    def post(self):
        # get the post data
        post_data = request.json
        return Auth.login_user(data=post_data)
