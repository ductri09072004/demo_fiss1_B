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


API_BASE = os.environ.get('API_BASE', 'https://auto-tool-production.up.railway.app').rstrip('/')
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


def get_service_data(service_name: str):
    """Get service data from MongoDB services collection"""
    data = fetch_json(f"{API_BASE}/api/db/services", params={'name': service_name, 'limit': 1})
    items = data.get('items', []) if isinstance(data, dict) else data
    if items and len(items) > 0:
        return items[0]
    return None


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
        service_data = get_service_data(name)
        
        if not service_data:
            continue
            
        # 1. Namespace
        emit({
            'apiVersion': 'v1',
            'kind': 'Namespace',
            'metadata': {
                'name': service_data.get('namespace', name),
                'labels': service_data.get('namespace_info', {}).get('labels', {})
            }
        })

        # 2. ConfigMap
        configmap_data = service_data.get('configmap', {})
        emit({
            'apiVersion': 'v1',
            'kind': 'ConfigMap',
            'metadata': {
                'name': configmap_data.get('name', f"{name}-config"),
                'namespace': service_data.get('namespace', name)
            },
            'data': configmap_data.get('data', {})
        })

        # 3. Secret
        secret_data = service_data.get('secret', {})
        emit({
            'apiVersion': 'v1',
            'kind': 'Secret',
            'metadata': {
                'name': secret_data.get('name', f"{name}-secret"),
                'namespace': service_data.get('namespace', name)
            },
            'type': secret_data.get('type', 'Opaque'),
            'data': secret_data.get('data', {})
        })

        # 4. Deployment
        deployment_data = service_data.get('deployment', {})
        emit({
            'apiVersion': 'apps/v1',
            'kind': 'Deployment',
            'metadata': {
                'name': deployment_data.get('name', name),
                'namespace': service_data.get('namespace', name),
                'labels': {'app': name}
            },
            'spec': {
                'replicas': service_data.get('replicas', 3),
                'selector': {'matchLabels': {'app': name}},
                'template': {
                    'metadata': {'labels': {'app': name}},
                    'spec': {
                        'containers': [{
                            'name': name,
                            'image': deployment_data.get('image', f"ghcr.io/ductri09072004/{name}:latest"),
                            'ports': [{'containerPort': deployment_data.get('target_port', service_data.get('port', 5001))}],
                            'resources': {
                                'requests': {
                                    'cpu': service_data.get('cpu_request', '100m'),
                                    'memory': service_data.get('memory_request', '128Mi')
                                },
                                'limits': {
                                    'cpu': service_data.get('cpu_limit', '200m'),
                                    'memory': service_data.get('memory_limit', '256Mi')
                                }
                            },
                            'envFrom': [{'configMapRef': {'name': configmap_data.get('name', f"{name}-config")}}]
                        }]
                    }
                }
            }
        })

        # 5. Service
        k8s_service_data = service_data.get('k8s_service', {})
        emit({
            'apiVersion': 'v1',
            'kind': 'Service',
            'metadata': {
                'name': k8s_service_data.get('name', f"{name}-service"),
                'namespace': service_data.get('namespace', name),
                'labels': {'app': name}
            },
            'spec': {
                'type': k8s_service_data.get('type', 'ClusterIP'),
                'selector': {'app': name},
                'ports': [{
                    'port': service_data.get('port', 5001),
                    'targetPort': k8s_service_data.get('target_port', service_data.get('port', 5001)),
                    'protocol': 'TCP'
                }]
            }
        })

        # 6. HPA
        hpa_data = service_data.get('hpa', {})
        emit({
            'apiVersion': 'autoscaling/v2',
            'kind': 'HorizontalPodAutoscaler',
            'metadata': {
                'name': hpa_data.get('name', f"{name}-hpa"),
                'namespace': service_data.get('namespace', name)
            },
            'spec': {
                'scaleTargetRef': {
                    'apiVersion': 'apps/v1',
                    'kind': 'Deployment',
                    'name': deployment_data.get('name', name)
                },
                'minReplicas': service_data.get('min_replicas', 2),
                'maxReplicas': service_data.get('max_replicas', 10),
                'metrics': [{
                    'type': 'Resource',
                    'resource': {
                        'name': 'cpu',
                        'target': {
                            'type': 'Utilization',
                            'averageUtilization': hpa_data.get('target_cpu_utilization', 70)
                        }
                    }
                }]
            }
        })

        # 7. Ingress
        ingress_data = service_data.get('ingress', {})
        emit({
            'apiVersion': 'networking.k8s.io/v1',
            'kind': 'Ingress',
            'metadata': {
                'name': ingress_data.get('name', f"{name}-ingress"),
                'namespace': service_data.get('namespace', name)
            },
            'spec': {
                'rules': [{
                    'host': ingress_data.get('host', f"{name}.local"),
                    'http': {
                        'paths': [{
                            'path': ingress_data.get('path', '/'),
                            'pathType': 'Prefix',
                            'backend': {
                                'service': {
                                    'name': k8s_service_data.get('name', f"{name}-service"),
                                    'port': {'number': service_data.get('port', 5001)}
                                }
                            }
                        }]
                    }
                }]
            }
        })

if __name__ == '__main__':
    main()


