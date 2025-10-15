#!/usr/bin/env python3
"""
Import JSON collections for a service into MongoDB.

Usage examples:
  python import_json_to_mongodb.py demo-v73
  python import_json_to_mongodb.py demo-v70 --uri "mongodb+srv://USER:PASS@HOST/?retryWrites=true&w=majority" --db AutoToolDevOPS

It expects JSON files in: E:\\Study\\Json_demo\\<service_name>\\*.json
Collections imported:
  services, deployments, k8s_services, configmaps, hpas, ingresses,
  namespaces, secrets, argocd_applications, manifest_versions
"""

import os
import sys
import json
import argparse
from pymongo import MongoClient


DEFAULT_OUT_ROOT = r"E:\\Study\\Json_demo"
DEFAULT_URI = os.environ.get('MONGO_URI', 'mongodb+srv://BlueDuck2:Fcsunny0907@tpexpress.zjf26.mongodb.net/?retryWrites=true&w=majority&appName=TPExpress')
DEFAULT_DB = os.environ.get('MONGO_DB', 'AutoToolDevOPS')


def load_json(path: str):
    if not os.path.exists(path):
        return None
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def ensure_list(data):
    if data is None:
        return []
    return data if isinstance(data, list) else [data]


def import_collection(db, collection: str, docs: list, service_name: str):
    if not docs:
        return 0
    # Clear existing service documents (by service_name) except for "services" collection
    if collection == 'services':
        # services collection is one doc per service without service_name field → upsert by _id/name
        # Strategy: remove any existing with _id == service_name OR name == service_name, then insert
        db[collection].delete_many({'$or': [{'_id': service_name}, {'name': service_name}]})
    else:
        db[collection].delete_many({'service_name': service_name})

    if isinstance(docs, list):
        if not docs:
            return 0
        res = db[collection].insert_many(docs)
        return len(res.inserted_ids)
    else:
        db[collection].insert_one(docs)
        return 1


def main():
    parser = argparse.ArgumentParser(description='Import JSON collections for a service into MongoDB')
    parser.add_argument('service_name', help='Service name (e.g., demo-v73)')
    parser.add_argument('--root', default=DEFAULT_OUT_ROOT, help='Root folder containing JSON outputs (default: %(default)s)')
    parser.add_argument('--uri', default=DEFAULT_URI, help='MongoDB connection URI (default: env MONGO_URI or %(default)s)')
    parser.add_argument('--db', dest='db_name', default=DEFAULT_DB, help='MongoDB database name (default: env MONGO_DB or %(default)s)')
    args = parser.parse_args()

    service_name = args.service_name.strip()
    service_dir = os.path.join(args.root, service_name)
    if not os.path.isdir(service_dir):
        print(f"JSON folder not found: {service_dir}")
        sys.exit(1)

    # Connect MongoDB
    client = MongoClient(args.uri)
    db = client[args.db_name]

    # Mapping of file → collection
    files_to_collections = [
        ('services.json', 'services'),
        ('deployments.json', 'deployments'),
        ('k8s_services.json', 'k8s_services'),
        ('configmaps.json', 'configmaps'),
        ('hpas.json', 'hpas'),
        ('ingresses.json', 'ingresses'),
        ('namespaces.json', 'namespaces'),
        ('secrets.json', 'secrets'),
        ('argocd_applications.json', 'argocd_applications'),
        ('manifest_versions.json', 'manifest_versions')
    ]

    total = 0
    for filename, collection in files_to_collections:
        path = os.path.join(service_dir, filename)
        data = load_json(path)
        docs = ensure_list(data)
        count = import_collection(db, collection, docs, service_name)
        print(f"Imported {count} docs into {collection} from {filename}")
        total += count

    print(f"Done. Total inserted: {total}")


if __name__ == '__main__':
    main()


