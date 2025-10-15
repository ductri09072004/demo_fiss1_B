#!/usr/bin/env python3
"""
Check all collections in the database
"""

from pymongo import MongoClient

def check_all_collections():
    """Check all collections in the database"""
    
    # MongoDB connection
    client = MongoClient("mongodb+srv://BlueDuck2:Fcsunny0907@tpexpress.zjf26.mongodb.net/?retryWrites=true&w=majority&appName=TPExpress")
    db = client["AutoToolDevOPS"]
    
    print("=== Database Collections Status ===")
    print(f"Database: AutoToolDevOPS")
    print(f"Total collections: {len(db.list_collection_names())}")
    print()
    
    # Expected collections
    expected_collections = [
        'services',
        'deployments', 
        'k8s_services',
        'configmaps',
        'hpas',
        'ingresses',
        'namespaces',
        'secrets',
        'argocd_applications',
        'manifest_versions'
    ]
    
    total_docs = 0
    
    for collection_name in expected_collections:
        try:
            collection = db[collection_name]
            count = collection.count_documents({"service_name": "demo-v72"})
            total_count = collection.count_documents({})
            
            print(f"OK {collection_name}:")
            print(f"   - demo-v72 documents: {count}")
            print(f"   - total documents: {total_count}")
            
            if count > 0:
                # Show sample document
                sample = collection.find_one({"service_name": "demo-v72"})
                print(f"   - sample _id: {sample.get('_id', 'N/A')}")
            
            total_docs += count
            print()
            
        except Exception as e:
            print(f"ERROR {collection_name}: ERROR - {e}")
            print()
    
    print(f"Total demo-v72 documents across all collections: {total_docs}")
    
    # List all collections in database
    all_collections = db.list_collection_names()
    print(f"\nAll collections in database: {all_collections}")

if __name__ == "__main__":
    check_all_collections()
