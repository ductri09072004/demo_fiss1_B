#!/usr/bin/env python3
"""
ArgoCD CMP generator: renders Kubernetes manifests by calling Dev-Tool APIs.

Inputs (env):
  - API_BASE: Base URL of Dev-Tool backend (default: http://localhost:3050)
  - SERVICE_NAME: Optional specific service to render; if empty, render all services

Usage: ArgoCD configManagementPlugins will invoke:
  python cmp/generator.py

Output: YAML manifests to stdout (--- separated)
"""

import os
import sys
import json
import requests
import yaml


API_BASE = os.environ.get('API_BASE', 'http://localhost:3050').rstrip('/')
SERVICE_NAME = os.environ.get('SERVICE_NAME', '').strip()


def fetch_json(url: str, params: dict | None = None):
    r = requests.get(url, params=params or {}, timeout=10)
    r.raise_for_status()
    return r.json()


def get_services():
    if SERVICE_NAME:
        return [{'name': SERVICE_NAME}]
    data = fetch_json(f"{API_BASE}/api/db/services", params={'limit': 1000})
    items = data.get('items') if isinstance(data, dict) else data
    if not isinstance(items, list):
        return []
    # Normalize
    services = []
    for s in items:
        name = s.get('name') or s.get('service_name')
        if name:
            services.append({'name': name})
    return services


def get_collection(service_name: str, collection: str):
    data = fetch_json(f"{API_BASE}/api/db/{collection}", params={'service_name': service_name, 'limit': 100})
    return data.get('items', []) if isinstance(data, dict) else []


def emit(doc: dict):
    sys.stdout.write(yaml.safe_dump(doc, sort_keys=False))
    sys.stdout.write("---\n")


def main():
    services = get_services()
    if not services:
        # Emit empty List to satisfy ArgoCD
        sys.stdout.write(yaml.safe_dump({'apiVersion': 'v1', 'kind': 'List', 'items': []}))
        return

    for svc in services:
        name = svc['name']

        # Namespaces
        for ns in get_collection(name, 'namespaces'):
            meta = ns.get('metadata', {})
            emit({
                'apiVersion': 'v1',
                'kind': 'Namespace',
                'metadata': meta,
            })

        # ConfigMaps
        for cm in get_collection(name, 'configmaps'):
            emit({
                'apiVersion': 'v1',
                'kind': 'ConfigMap',
                'metadata': cm.get('metadata', {}),
                'data': cm.get('data', {}),
            })

        # Secrets
        for sec in get_collection(name, 'secrets'):
            doc = {
                'apiVersion': 'v1',
                'kind': 'Secret',
                'metadata': sec.get('metadata', {}),
                'type': sec.get('type', 'Opaque'),
            }
            if 'data' in sec:
                doc['data'] = sec['data']
            emit(doc)

        # Deployments
        deps = get_collection(name, 'deployments')
        if deps:
            for d in deps:
                emit({
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'metadata': d.get('metadata', {}),
                    'spec': d.get('spec', {}),
                })
        else:
            # Fallback minimal deployment from services API if needed
            pass

        # Services
        for ks in get_collection(name, 'k8s_services'):
            emit({
                'apiVersion': 'v1',
                'kind': 'Service',
                'metadata': ks.get('metadata', {}),
                'spec': ks.get('spec', {}),
            })

        # HPA
        for h in get_collection(name, 'hpas'):
            emit({
                'apiVersion': 'autoscaling/v2',
                'kind': 'HorizontalPodAutoscaler',
                'metadata': h.get('metadata', {}),
                'spec': h.get('spec', {}),
            })

        # Ingresses
        for ig in get_collection(name, 'ingresses'):
            emit({
                'apiVersion': 'networking.k8s.io/v1',
                'kind': 'Ingress',
                'metadata': ig.get('metadata', {}),
                'spec': ig.get('spec', {}),
            })

        # Optional: ArgoCD Application (usually managed separately)
        # for app in get_collection(name, 'argocd_applications'):
        #     emit({ 'apiVersion': 'argoproj.io/v1alpha1', 'kind': 'Application', ... })

if __name__ == '__main__':
    main()


