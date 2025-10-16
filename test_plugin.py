#!/usr/bin/env python3
"""
Test script for ArgoCD CMP generator
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set environment variables
os.environ['API_BASE'] = 'https://auto-tool-production.up.railway.app'
os.environ['SERVICE_NAME'] = 'demo-v83'  # Test with existing service

# Import and run generator
from cmp.generator import main

if __name__ == '__main__':
    print("Testing ArgoCD CMP Generator...")
    print(f"API_BASE: {os.environ.get('API_BASE')}")
    print(f"SERVICE_NAME: {os.environ.get('SERVICE_NAME')}")
    print("=" * 50)
    
    main()
