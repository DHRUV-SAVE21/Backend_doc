import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def test_mongodb_connection():
    """Test MongoDB Atlas connection"""
    try:
        print("🔗 Testing MongoDB Atlas connection...")
        print(f"   URL: {settings.MONGODB_URL}")
        print(f"   Database: {settings.MONGODB_DATABASE}")
        
        # Connect to MongoDB
        client = AsyncIOMotorClient(settings.MONGODB_URL)
        
        # Test connection
        print("\n⏳ Pinging MongoDB...")
        await client.admin.command('ping')
        print("✅ MongoDB Atlas connection successful!")
        
        # Test database access
        db = client[settings.MONGODB_DATABASE]
        print(f"\n📊 Accessing database: {settings.MONGODB_DATABASE}")
        
        # Test write operation
        test_collection = db.test_collection
        test_doc = {"test": "connection", "timestamp": "2024-01-04"}
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Write test successful. Inserted ID: {result.inserted_id}")
        
        # Test read operation
        found_doc = await test_collection.find_one({"_id": result.inserted_id})
        print(f"✅ Read test successful. Found: {found_doc}")
        
        # Clean up test document
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ Cleanup successful")
        
        # List collections
        collections = await db.list_collection_names()
        print(f"📁 Existing collections: {collections}")
        
        # Close connection
        client.close()
        print("\n🎉 MongoDB Atlas is ready for production!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ MongoDB connection failed: {str(e)}")
        print("\n🔧 Possible solutions:")
        print("   1. Check your internet connection")
        print("   2. Verify MongoDB Atlas credentials")
        print("   3. Ensure IP is whitelisted in MongoDB Atlas")
        print("   4. Check if cluster is running")
        return False

if __name__ == "__main__":
    asyncio.run(test_mongodb_connection())
