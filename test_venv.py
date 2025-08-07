#!/usr/bin/env python3
import sys
import subprocess

print("=" * 50)
print("VIRTUAL ENVIRONMENT STATUS")
print("=" * 50)

print(f"Python executable: {sys.executable}")
print(f"Python version: {sys.version}")
print(f"Python path: {sys.path[0:3]}")

print("\n" + "=" * 50)
print("INSTALLED PACKAGES (first 10)")
print("=" * 50)

try:
    result = subprocess.run([sys.executable, "-m", "pip", "list"], 
                          capture_output=True, text=True)
    lines = result.stdout.strip().split('\n')
    for i, line in enumerate(lines[:12]):  # Show header + first 10 packages
        print(line)
        if i >= 11:
            break
    if len(lines) > 12:
        print(f"... and {len(lines) - 12} more packages")
except Exception as e:
    print(f"Error getting package list: {e}")

print("\n" + "=" * 50)
print("KEY DEPENDENCIES CHECK")
print("=" * 50)

key_packages = ['fastapi', 'uvicorn', 'firebase-admin', 'google-generativeai', 'pinecone-client']
# Map package names to their correct import names
package_import_map = {
    'fastapi': 'fastapi',
    'uvicorn': 'uvicorn',
    'firebase-admin': 'firebase_admin',
    'google-generativeai': 'google.generativeai',
    'pinecone-client': 'pinecone',
}
for package in key_packages:
    import_name = package_import_map.get(package, package.replace('-', '_'))
    try:
        __import__(import_name)
        print(f"✅ {package}")
    except ImportError:
        print(f"❌ {package}")
