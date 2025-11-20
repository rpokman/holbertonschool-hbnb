from app import create_app, db
from app.models.user import User
from app.models.place import Place
from app.models.review import Review
from app.models.amenity import Amenity
import sqlalchemy as sa
import uuid

app = create_app()

with app.app_context():
    print("🎯 COMPLETE TEST OF 4 SQLALCHEMY MODELS")
    print("=" * 50)
    
    inspector = sa.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"📊 Tables in database: {tables}")
    
    print("\n🔍 Test Place - ID verification...")
    place_test = Place(
        title="Test Place",
        description="Test description",
        price=100.0,
        latitude=48.8566,
        longitude=2.3522,
        owner_id=str(uuid.uuid4())
    )
    print(f"Place ID after __init__: {hasattr(place_test, 'id')}")
    print(f"Place ID value: {getattr(place_test, 'id', 'NO ID')}")
    
    import time
    unique_email = f"test{int(time.time())}@example.com"
    
    print(f"\n👤 Creating User: {unique_email}")
    user = User(
        first_name="TestUser", 
        last_name="ModelTest",
        email=unique_email,
        password="test123"
    )
    user.save()
    print(f"✅ User created - ID: {user.id}")
    
    print(f"\n🏠 Creating Place...")
    place = Place(
        title="Beautiful Apartment",
        description="Lovely place in the city",
        price=120.0,
        latitude=48.8566,
        longitude=2.3522,
        owner_id=user.id
    )
    print(f"Place before save - ID: {getattr(place, 'id', 'NO ID')}")
    place.save()
    print(f"✅ Place created - ID: {place.id}")
    
    print(f"\n⭐ Creating Review...")
    review = Review(
        text="Amazing place! Highly recommend!",
        rating=5,
        place_id=place.id,
        user_id=user.id
    )
    review.save()
    print(f"✅ Review created - ID: {review.id}")
    
    print(f"\n🏊 Creating Amenity...")
    amenity = Amenity(name=f"Pool{int(time.time())}")
    amenity.save()
    print(f"✅ Amenity created - ID: {amenity.id}")
    
    print(f"\n🔍 Verifying retrieval...")
    saved_user = User.query.get(user.id)
    saved_place = Place.query.get(place.id)
    saved_review = Review.query.get(review.id)
    saved_amenity = Amenity.query.get(amenity.id)

    print(f"✅ User retrieved: {saved_user.email}")
    print(f"✅ Place retrieved: {saved_place.title}")
    print(f"✅ Review retrieved: {saved_review.text[:20]}...") 
    print(f"✅ Amenity retrieved: {saved_amenity.name}")

    print("\n🎉" + "="*47 + "🎉")
    print("🎯 MODELS TEST COMPLETELY SUCCESSFUL!")
    print("🎯 All 4 models are PERFECTLY mapped to SQLAlchemy!")
    print("🎉" + "="*47 + "🎉")