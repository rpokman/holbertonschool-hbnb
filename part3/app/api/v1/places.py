from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade

place_namespace = Namespace('places', description='Place operations')

amenity_model = place_namespace.model('PlaceAmenity', {
    'id': fields.String(description='Amenity ID'),
    'name': fields.String(description='Name of the amenity')
})

user_model = place_namespace.model('PlaceUser', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the owner'),
    'last_name': fields.String(description='Last name of the owner'),
    'email': fields.String(description='Email of the owner')
})

place_model = place_namespace.model('Place', {
    'title': fields.String(required=True, description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(required=True, description='Price per night'),
    'latitude': fields.Float(required=True, description='Latitude of the place'),
    'longitude': fields.Float(required=True, description='Longitude of the place'),
    'amenities': fields.List(fields.String, required=False, description="List of amenities ID's")
})

# Model for partial place updates
place_update_model = place_namespace.model('PlaceUpdate', {
    'title': fields.String(required=False, description='Title of the place'),
    'description': fields.String(required=False, description='Description of the place'),
    'price': fields.Float(required=False, description='Price per night'),
    'latitude': fields.Float(required=False, description='Latitude of the place'),
    'longitude': fields.Float(required=False, description='Longitude of the place'),
    'owner_id': fields.String(required=False, description='ID of the owner'),
    'amenities': fields.List(fields.String, required=False, description="List of amenities ID's")
})

review_model = place_namespace.model('PlaceReview', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(description='ID of the user')
})

place_response_model = place_namespace.model('PlaceResponse', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'description': fields.String(description='Description of the place'),
    'price': fields.Float(description='Price per night'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place'),
    'owner_id': fields.String(description='ID of the owner'),
    'owner': fields.Nested(user_model, description='Owner details'),
    'amenities': fields.List(fields.Nested(amenity_model), description='List of amenities'),
    'reviews': fields.List(fields.Nested(review_model), description='List of reviews')
})

place_list_model = place_namespace.model('PlaceList', {
    'id': fields.String(description='Place ID'),
    'title': fields.String(description='Title of the place'),
    'latitude': fields.Float(description='Latitude of the place'),
    'longitude': fields.Float(description='Longitude of the place'),
    'price': fields.Float(description='Price per night')
})

@place_namespace.route('/')
class PlaceList(Resource):
    @place_namespace.expect(place_model, validate=True)
    @jwt_required()
    @place_namespace.response(201, 'Place successfully created')
    @place_namespace.response(400, 'Invalid input data')
    @place_namespace.response(404, 'Owner or amenity not found')
    def post(self):
        """Register a new place"""
        current_user_id = get_jwt_identity()

        place_data = place_namespace.payload
        place_data['owner_id'] = current_user_id
        place_data['amenities'] = place_data.get('amenities', [])
        
        try:
            new_place = facade.create_place(place_data)
            return new_place.to_dict(), 201
        except ValueError as e:
            if "not found" in str(e).lower():
                return {'error': str(e)}, 404
            else:
                return {'error': str(e)}, 400
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500

    @place_namespace.response(200, 'List of places retrieved successfully')
    @place_namespace.marshal_list_with(place_list_model)
    def get(self):
        """Retrieve a list of all places"""
        try:
            places = facade.get_all_places()
            return [{
                'id': place.id,
                'title': place.title,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'price': float(place.price) if place.price else 0
            } for place in places], 200
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500

@place_namespace.route('/<place_id>')
class PlaceResource(Resource):
    @jwt_required()
    @place_namespace.response(200, 'Place details retrieved successfully')
    @place_namespace.response(404, 'Place not found')
    @place_namespace.response(400, 'Invalid input data')
    def get(self, place_id):
        """Get place details by ID"""
        try:
            place = facade.get_place(place_id)
            if not place:
                return {'error': 'Place not found'}, 404

            owner = facade.get_user(place.owner_id)
            if not owner:
                return {'error': 'Owner not found'}, 404

            amenities_data = []
            for amenity in place.amenities:
                amenities_data.append({
                    'id': amenity.id,
                    'name': amenity.name
                })

            reviews_data = []
            for review in place.reviews:
                review_user = facade.get_user(review.user_id)
                reviews_data.append({
                    'id': review.id,
                    'text': review.text,
                    'rating': review.rating,
                    'user_id': review.user_id,
                    'user': {
                        'id': review_user.id,
                        'first_name': review_user.first_name,
                        'last_name': review_user.last_name
                    } if review_user else None
                })
            
            response = {
                'id': place.id,
                'title': place.title,
                'description': place.description,
                'price': float(place.price) if place.price else None,
                'latitude': place.latitude,
                'longitude': place.longitude,
                'owner_id': place.owner_id,
                'owner': {
                    'id': owner.id,
                    'first_name': owner.first_name,
                    'last_name': owner.last_name,
                    'email': owner.email
                } if owner else None,
                'amenities': amenities_data,
                'reviews': reviews_data
            }
            return response, 200
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500

    @place_namespace.expect(place_update_model, validate=True)
    @jwt_required()
    def put(self, place_id):
        """Update a place's information"""
        current_user_id = get_jwt_identity()
        
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404
            
        if place.owner_id != current_user_id:
            return {'error': 'You can only update your own places'}, 403
        
        place_data = place_namespace.payload
        
        try:
            updated_place = facade.update_place(place_id, place_data)
            if updated_place:
                return {'message': 'Place updated successfully'}, 200
            else:
                return {'error': 'Place not found'}, 404
        except ValueError as e:
            if "not found" in str(e).lower():
                return {'error': str(e)}, 404
            else:
                return {'error': str(e)}, 400
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500


@place_namespace.route('/<place_id>/reviews')
class PlaceReviews(Resource):
    @place_namespace.response(200, 'List of reviews for the place retrieved successfully')
    @place_namespace.response(404, 'Place not found')
    def get(self, place_id):
        """Get all reviews for a specific place"""
        try:
            reviews = facade.get_reviews_by_place(place_id)
            return [{
                'id': review.id,
                'text': review.text,
                'rating': review.rating,
                'user_id': review.user.id
            } for review in reviews], 200
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500

    @jwt_required()
    @place_namespace.response(200, 'Place deleted successfully')
    @place_namespace.response(404, 'Place not found')
    @place_namespace.response(403, 'Not authorized to delete this place')
    def delete(self, place_id):
        """Delete a place (Owner or Admin only)"""
        current_user_id = get_jwt_identity()
        current_user = facade.get_user(current_user_id)
        
        place = facade.get_place(place_id)
        if not place:
            return {'error': 'Place not found'}, 404

        if place.owner_id != current_user_id and (not current_user or not current_user.is_admin):
            return {'error': 'You can only delete your own places'}, 403
        
        try:
            success = facade.delete_place(place_id)
            if success:
                return {'message': 'Place deleted successfully'}, 200
            else:
                return {'error': 'Place not found'}, 404
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500