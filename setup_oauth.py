"""
Script para configurar OAuth con YouTube Music

Pasos:
1. Ve a https://console.cloud.google.com/
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita "YouTube Data API v3"
4. Ve a "Credenciales" > "Crear credenciales" > "ID de cliente de OAuth"
5. Selecciona "TVs y dispositivos con entrada limitada"
6. Descarga las credenciales o copia el client_id y client_secret

Luego ejecuta este script con:
    python setup_oauth.py
"""

import sys
import os

def setup_oauth():
    print("=" * 60)
    print("🔐 CONFIGURACIÓN DE OAUTH PARA YOUTUBE MUSIC")
    print("=" * 60)
    print()
    print("📋 PASOS PREVIOS:")
    print("1. Ve a: https://console.cloud.google.com/")
    print("2. Crea/selecciona un proyecto")
    print("3. Habilita 'YouTube Data API v3'")
    print("4. Crea credenciales OAuth 2.0")
    print("5. Tipo: 'TVs y dispositivos con entrada limitada'")
    print()
    print("=" * 60)
    print()
    
    # Pedir credenciales
    print("Ingresa tus credenciales de OAuth:")
    client_id = input("Client ID: ").strip()
    client_secret = input("Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("❌ Error: Debes proporcionar ambas credenciales")
        return
    
    # Guardar en un archivo de configuración
    config_content = f"""# Credenciales OAuth para YouTube Music
CLIENT_ID={client_id}
CLIENT_SECRET={client_secret}
"""
    
    with open('oauth_config.env', 'w') as f:
        f.write(config_content)
    
    print()
    print("✅ Credenciales guardadas en oauth_config.env")
    print()
    print("🔄 Ahora ejecuta el comando de autenticación:")
    print("   ytmusicapi oauth")
    print()
    print("Esto abrirá un navegador para que autorices la aplicación")
    print("Se creará un archivo oauth.json con tu token de acceso")
    print()

if __name__ == "__main__":
    try:
        setup_oauth()
    except KeyboardInterrupt:
        print("\n❌ Cancelado por el usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
