# MongoDB Connection
client = MongoClient("mongodb://localhost:27017/")
db = client["user_database"]  # Change this to your database name
users_collection = db["users"]  # Change this to your collection name