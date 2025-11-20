from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services import facade

review_namespace = Namespace('reviews', description='Review operations')

review_model = review_namespace.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'place_id': fields.String(required=True, description='ID of the place')
})

# Model for partial review updates
review_update_model = review_namespace.model('ReviewUpdate', {
    'text': fields.String(required=False, description='Text of the review'),
    'rating': fields.Integer(required=False, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=False, description='ID of the user'),
    'place_id': fields.String(required=False, description='ID of the place')
})

review_response_model = review_namespace.model('ReviewResponse', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)'),
    'user_id': fields.String(required=False, description='ID of the user'),
    'place_id': fields.String(description='ID of the place')
})

review_list_model = review_namespace.model('ReviewList', {
    'id': fields.String(description='Review ID'),
    'text': fields.String(description='Text of the review'),
    'rating': fields.Integer(description='Rating of the place (1-5)')
})

@review_namespace.route('/')
class ReviewList(Resource):
    @review_namespace.expect(review_model, validate=True)
    @jwt_required()
    @review_namespace.response(201, 'Review successfully created')
    @review_namespace.response(400, 'Invalid input data')
    @review_namespace.response(404, 'User or place not found')
    def post(self):
        """Register a new review"""
        current_user_id = get_jwt_identity()
        
        review_data = review_namespace.payload
        review_data['user_id'] = current_user_id
        
        place = facade.get_place(review_data['place_id'])
        if place.owner_id == current_user_id:
            return {'error': 'You cannot review your own place'}, 400
        
        try:
            new_review = facade.create_review(review_data)
            return new_review.to_dict(), 201
        except ValueError as e:
            if "not found" in str(e).lower():
                return {'error': str(e)}, 404
            else:
                return {'error': str(e)}, 400
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500

    @review_namespace.response(200, 'List of reviews retrieved successfully')
    @review_namespace.marshal_list_with(review_list_model)
    def get(self):
        """Retrieve a list of all reviews"""
        try:
            reviews = facade.get_all_reviews()
            return [{
                'id': review.id,
                'text': review.text,
                'rating': review.rating
            } for review in reviews], 200
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500

@review_namespace.route('/<review_id>')
class ReviewResource(Resource):
    @review_namespace.expect(review_update_model, validate=True)
    @jwt_required()
    @review_namespace.response(200, 'Review details retrieved successfully')
    @review_namespace.response(404, 'Review not found')
    @review_namespace.marshal_with(review_response_model)
    def get(self, review_id):
        """Get review details by ID"""
        try:
            review = facade.get_review(review_id)
            if not review:
                return {'error': 'Review not found'}, 404
            return review.to_dict(), 200
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500

    @review_namespace.expect(review_update_model, validate=True)
    @review_namespace.response(200, 'Review updated successfully')
    @review_namespace.response(404, 'Review not found')
    @review_namespace.response(400, 'Invalid input data')
    def put(self, review_id):
        """Update a review's information"""
        current_user_id = get_jwt_identity()
        
        review = facade.get_review(review_id)
        if not review:
            return {'error': 'Review not found'}, 404
            
        if review.user_id != current_user_id:
            return {'error': 'You can only update your own reviews'}, 403
        
        review_data = review_namespace.payload
        
        try:
            updated_review = facade.update_review(review_id, review_data)
            if updated_review:
                return {'message': 'Review updated successfully'}, 200
            else:
                return {'error': 'Review not found'}, 404
        except ValueError as e:
            if "not found" in str(e).lower():
                return {'error': str(e)}, 404
            else:
                return {'error': str(e)}, 400
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500

    @review_namespace.response(200, 'Review deleted successfully')
    @review_namespace.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review"""
        try:
            success = facade.delete_review(review_id)
            if success:
                return {'message': 'Review deleted successfully'}, 200
            else:
                return {'error': 'Review not found'}, 404
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500

@review_namespace.route('/places/<place_id>/reviews')
class PlaceReviewList(Resource):
    @review_namespace.response(200, 'List of reviews for the place retrieved successfully')
    @review_namespace.response(404, 'Place not found')
    @review_namespace.marshal_list_with(review_list_model)

    def get(self, place_id):
        """Get all reviews for a specific place"""
        try:
            reviews = facade.get_reviews_by_place(place_id)
            return [{
                'id': review.id,
                'text': review.text,
                'rating': review.rating
            } for review in reviews], 200
        except ValueError as e:
            return {'error': str(e)}, 404
        except Exception as e:
            return {'error': f'Internal server error: {str(e)}'}, 500
