from pymongo import MongoClient
import os

# Connect to MongoDB
mongo_uri = "mongodb+srv://BlueDuck2:Fcsunny0907@tpexpress.zjf26.mongodb.net/?retryWrites=true&w=majority&appName=TPExpress"
client = MongoClient(mongo_uri)
db = client.AutoToolDevOPS

# Update demo-v90 path
result = db.services.update_one(
    {'name': 'demo-v90'},
    {'$set': {'argocd_application.path': '.'}}
)

print(f"Updated {result.modified_count} document(s)")
print("demo-v90 path updated to '.' in MongoDB")
