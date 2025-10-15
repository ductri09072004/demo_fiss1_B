#!/usr/bin/env python3
"""
Auto-generated script to import all collections into MongoDB
"""

import json
import os
from pymongo import MongoClient
from datetime import datetime

def import_all_collections():
    """Import all collections into MongoDB"""
    
    # MongoDB connection
    client = MongoClient("mongodb+srv://BlueDuck2:Fcsunny0907@tpexpress.zjf26.mongodb.net/?retryWrites=true&w=majority&appName=TPExpress")
    db = client["AutoToolDevOPS"]
    
    # Collection files
    collections = [
        'services.json',
        'deployments.json', 
        'k8s_services.json',
        'configmaps.json',
        'hpas.json',
        'ingresses.json',
        'namespaces.json',
        'secrets.json',
        'argocd_applications.json',
        'manifest_versions.json'
    ]
    
    imported_count = 0
    
    for collection_file in collections:
        collection_name = collection_file.replace('.json', '')
        file_path = collection_file
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
            
            # Read JSON data
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Clear existing data for this service
            db[collection_name].delete_many({"service_name": "demo-v72"})
            
            # Insert new data
            if isinstance(data, list):
                result = db[collection_name].insert_many(data)
                count = len(result.inserted_ids)
            else:
                result = db[collection_name].insert_one(data)
                count = 1
            
            print(f"Imported {count} document(s) into {collection_name}")
            imported_count += count
            
        except Exception as e:
            print(f"Error importing {collection_file}: {e}")
    
    print(f"\nTotal imported: {imported_count} documents")
    print("Collections imported:")
    for collection in collections:
        print(f"   - {collection.replace('.json', '')}")

if __name__ == "__main__":
    import_all_collections()
