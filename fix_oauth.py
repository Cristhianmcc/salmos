"""
Script para regenerar oauth.json con las credenciales correctas
"""
import json
import os

# Leer el archivo oauth_config.env
client_id = None
client_secret = None

if os.path.exists('oauth_config.env'):
    with open('oauth_config.env', 'r') as f:
        for line in f:
            if line.startswith('CLIENT_ID='):
                client_id = line.split('=')[1].strip()
            elif line.startswith('CLIENT_SECRET='):
                client_secret = line.split('=')[1].strip()

if not client_id or not client_secret:
    print("❌ No se encontraron las credenciales en oauth_config.env")
    print("   Ejecuta: python setup_oauth.py primero")
    exit(1)

# Leer el oauth.json actual
if os.path.exists('oauth.json'):
    with open('oauth.json', 'r') as f:
        oauth_data = json.load(f)
    
    # Agregar las credenciales
    oauth_data['client_id'] = client_id
    oauth_data['client_secret'] = client_secret
    
    # Guardar el archivo actualizado
    with open('oauth.json', 'w') as f:
        json.dump(oauth_data, f, indent=1)
    
    print("✅ oauth.json actualizado con las credenciales")
    print(f"   Client ID: {client_id[:50]}...")
    print(f"   Client Secret: {client_secret[:20]}...")
else:
    print("❌ No se encontró oauth.json")
    print("   Ejecuta: ytmusicapi oauth primero")
