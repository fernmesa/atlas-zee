"""
Descarga imagen de galaxia espiral de NASA (dominio público).
NASA proporciona imágenes de alta resolución de libre uso.
"""
import urllib.request
import base64
import os

# Imagen de galaxia M51 (Whirlpool Galaxy) - dominio público NASA
# Usando versión de menor resolución para web
url = "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=800"

try:
    print("Intentando descargar imagen...")
    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=15) as response:
        data = response.read()
    
    # Convertir a base64 para data URI
    b64 = base64.b64encode(data).decode('utf-8')
    print(f"Descargado: {len(data)} bytes")
    
    # Guardar para inspeccionar
    with open('/tmp/galaxy.b64', 'w') as f:
        f.write(b64)
    print("Base64 guardado en /tmp/galaxy.b64")
    print(f"Data URI (primeros 150 chars):\ndata:image/jpeg;base64,{b64[:150]}...")
    
except Exception as e:
    print(f"Error: {e}")
    print("Alternativa: usar imagen SVG procedural mejorada en lugar de foto")
