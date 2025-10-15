#!/usr/bin/env python3
"""
Generate 10 JSON collection files for demo-v73 by reading original k8s YAMLs.
Output: E:\\Study\\Json_demo\\demo-v73\\*.json
"""

import os
import json
from datetime import datetime
import sys

def resolve_paths(service_name: str):
    k8s_dir = os.path.join("E:\\Study\\demo_fiss1_B", "services", service_name, "k8s")
    out_dir = os.path.join("E:\\Study\\Json_demo", service_name)
    return k8s_dir, out_dir

def read_yaml(path):
    if not os.path.exists(path):
        return None
    text = open(path, 'r', encoding='utf-8').read()
    try:
        import yaml  # type: ignore
        return yaml.safe_load(text)
    except Exception:
        # Fallback: naive loader for simple key/value we care about
        # Return raw text as a hint
        return {"_raw": text}

def write_json(filename, data, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, filename)
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def now_iso():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

def main():
    # Accept service name via CLI arg, env, or default
    service_name = (sys.argv[1] if len(sys.argv) > 1 else os.getenv('SERVICE_NAME', 'demo-v73')).strip()
    k8s_dir, out_dir = resolve_paths(service_name)
    # Ensure output folder exists upfront
    os.makedirs(out_dir, exist_ok=True)
    created = now_iso()

    if not os.path.isdir(k8s_dir):
        print(f"K8s folder not found: {k8s_dir}")
        sys.exit(1)

    # 1) services.json (metadata-level record)
    # Best-effort infer namespace from namespace.yaml | deployment metadata
    namespace_yaml = read_yaml(os.path.join(k8s_dir, 'namespace.yaml'))
    deployment_yaml = read_yaml(os.path.join(k8s_dir, 'deployment.yaml'))
    namespace = service_name
    if isinstance(namespace_yaml, dict):
        try:
            namespace = namespace_yaml.get('metadata', {}).get('name', service_name)
        except Exception:
            pass
    elif isinstance(deployment_yaml, dict):
        try:
            namespace = deployment_yaml.get('metadata', {}).get('namespace', service_name)
        except Exception:
            pass

    services = [
        {
            "_id": service_name,
            "name": service_name,
            "namespace": namespace,
            "status": "Unknown",
            "description": f"Demo service {service_name}",
            "created_at": created,
            "updated_at": created,
            "created_by": "portal",
            "tags": ["demo", "api", "flask"]
        }
    ]
    write_json('services.json', services, out_dir)

    # 2) deployments.json
    deployments = []
    if isinstance(deployment_yaml, dict):
        deployments.append({
            "_id": f"{service_name}-deployment",
            "service_name": service_name,
            "metadata": deployment_yaml.get('metadata', {}),
            "spec": deployment_yaml.get('spec', {}),
            "template": deployment_yaml.get('spec', {}).get('template', {}),
            "version": 1,
            "created_at": created,
            "updated_at": created
        })
    write_json('deployments.json', deployments, out_dir)

    # 3) k8s_services.json
    svc_yaml = read_yaml(os.path.join(k8s_dir, 'service.yaml'))
    k8s_services = []
    if isinstance(svc_yaml, dict):
        k8s_services.append({
            "_id": f"{service_name}-service",
            "service_name": service_name,
            "metadata": svc_yaml.get('metadata', {}),
            "spec": svc_yaml.get('spec', {}),
            "version": 1,
            "created_at": created,
            "updated_at": created
        })
    write_json('k8s_services.json', k8s_services, out_dir)

    # 4) configmaps.json
    cfg_yaml = read_yaml(os.path.join(k8s_dir, 'configmap.yaml'))
    configmaps = []
    if isinstance(cfg_yaml, dict):
        configmaps.append({
            "_id": f"{service_name}-config",
            "service_name": service_name,
            "metadata": cfg_yaml.get('metadata', {}),
            "data": cfg_yaml.get('data', {}),
            "version": 1,
            "created_at": created,
            "updated_at": created
        })
    write_json('configmaps.json', configmaps, out_dir)

    # 5) hpas.json
    hpa_yaml = read_yaml(os.path.join(k8s_dir, 'hpa.yaml'))
    hpas = []
    if isinstance(hpa_yaml, dict):
        hpas.append({
            "_id": f"{service_name}-hpa",
            "service_name": service_name,
            "metadata": hpa_yaml.get('metadata', {}),
            "spec": hpa_yaml.get('spec', {}),
            "version": 1,
            "created_at": created,
            "updated_at": created
        })
    write_json('hpas.json', hpas, out_dir)

    # 6) ingresses.json (ingress.yaml + ingress-gateway.yaml if exist)
    ingresses = []
    ingress_yaml = read_yaml(os.path.join(k8s_dir, 'ingress.yaml'))
    if isinstance(ingress_yaml, dict):
        ingresses.append({
            "_id": f"{service_name}-ingress",
            "service_name": service_name,
            "ingress_name": ingress_yaml.get('metadata', {}).get('name', f"{service_name}-ingress"),
            "metadata": ingress_yaml.get('metadata', {}),
            "spec": ingress_yaml.get('spec', {}),
            "version": 1,
            "created_at": created,
            "updated_at": created
        })
    ingress_gw_yaml = read_yaml(os.path.join(k8s_dir, 'ingress-gateway.yaml'))
    if isinstance(ingress_gw_yaml, dict):
        ingresses.append({
            "_id": f"{service_name}-gateway",
            "service_name": service_name,
            "ingress_name": ingress_gw_yaml.get('metadata', {}).get('name', f"{service_name}-gateway"),
            "metadata": ingress_gw_yaml.get('metadata', {}),
            "spec": ingress_gw_yaml.get('spec', {}),
            "version": 1,
            "created_at": created,
            "updated_at": created
        })
    write_json('ingresses.json', ingresses, out_dir)

    # 7) namespaces.json
    namespaces = []
    if isinstance(namespace_yaml, dict):
        namespaces.append({
            "_id": f"{service_name}-namespace",
            "service_name": service_name,
            "metadata": namespace_yaml.get('metadata', {}),
            "version": 1,
            "created_at": created,
            "updated_at": created
        })
    write_json('namespaces.json', namespaces, out_dir)

    # 8) secrets.json
    secret_yaml = read_yaml(os.path.join(k8s_dir, 'secret.yaml'))
    secrets = []
    if isinstance(secret_yaml, dict):
        secrets.append({
            "_id": f"{service_name}-secret",
            "service_name": service_name,
            "metadata": secret_yaml.get('metadata', {}),
            "type": secret_yaml.get('type', ''),
            "data": secret_yaml.get('data', {}),
            # optional docker_config if present in annotations (not standard)
            "version": 1,
            "created_at": created,
            "updated_at": created
        })
    write_json('secrets.json', secrets, out_dir)

    # 9) argocd_applications.json
    app_yaml = read_yaml(os.path.join(k8s_dir, 'argocd-application.yaml'))
    argocd_apps = []
    if isinstance(app_yaml, dict):
        # Normalize to match schema used previously
        argocd_apps.append({
            "_id": f"{service_name}-argocd",
            "service_name": service_name,
            "metadata": {
                "name": app_yaml.get('metadata', {}).get('name', service_name),
                "namespace": app_yaml.get('metadata', {}).get('namespace', 'argocd'),
                "finalizers": app_yaml.get('metadata', {}).get('finalizers', [])
            },
            "spec": app_yaml.get('spec', {}),
            "version": 1,
            "created_at": created,
            "updated_at": created
        })
    write_json('argocd_applications.json', argocd_apps, out_dir)

    # 10) manifest_versions.json (store full deployment content as a versioned artifact)
    manifest_versions = []
    if isinstance(deployment_yaml, dict):
        manifest_versions.append({
            "_id": f"{service_name}-deployment-v1",
            "service_name": service_name,
            "manifest_type": "deployment",
            "version": 1,
            "content": deployment_yaml,
            "changes": {
                "description": f"Initial deployment for {service_name}",
                "changed_by": "portal",
                "changed_fields": ["spec.replicas", "spec.template.spec.containers[0].image", "spec.template.spec.containers[0].resources"]
            },
            "created_at": created,
            "created_by": "portal"
        })
    write_json('manifest_versions.json', manifest_versions, out_dir)

    print(f"Generated JSON collections for {service_name} at {out_dir}")

if __name__ == '__main__':
    main()


