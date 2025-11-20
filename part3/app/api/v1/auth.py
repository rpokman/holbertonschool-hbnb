from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.services.facade import facade

api = Namespace('auth', description='Authentication operations')

login_model = api.model('Login', {
    'email': fields.String(required=True, description='User email'),
    'password': fields.String(required=True, description='User password')
})

@api.route('/login')
class Login(Resource):
    @api.expect(login_model)
    def post(self):
        """Authenticate user and return a JWT token"""
        credentials = api.payload
        user = facade.get_user_by_email(credentials['email'])

        if user and user.verify_password(credentials['password']):
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={"is_admin": user.is_admin}
            )
            return {'access_token': access_token}, 200
        
        return {'error': 'Invalid credentials'}, 401

@api.route('/protected')
class ProtectedResource(Resource):
    @jwt_required()
    def get(self):
        current_user = get_jwt_identity()
        return {'message': f'Hello, user {current_user}'}, 200

@api.route('/init-admin')
class InitAdmin(Resource):
    def post(self):
        """Create initial admin user (use once only)"""
        try:
            # Check if admin exists
            existing_admin = facade.get_user_by_email("admin@hbnb.com")
            if existing_admin:
                return {'error': 'Admin user already exists'}, 400
            
            # Create admin
            admin_data = {
                "first_name": "Super",
                "last_name": "Admin", 
                "email": "admin@hbnb.com",
                "password": "admin123",
                "is_admin": True
            }
            
            admin = facade.create_user(admin_data)
            return {
                'message': 'Admin user created successfully',
                'user': {
                    'id': admin.id,
                    'email': admin.email
                }
            }, 201
            
        except Exception as e:
            return {'error': f'Failed to create admin: {str(e)}'}, 500
