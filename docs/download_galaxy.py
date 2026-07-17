"""
Descarga imagen de galaxia espiral de dominio público.
Usa NASA Hubble o Unsplash (dominio público CC0).
"""
import urllib.request, base64, os

# Intentamos varias fuentes de dominio público
URLs = [
    # Unsplash - Galaxia espiral (CC0)
    "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=1200&q=80",
    # Pexels - Espacio/galaxia
    "https://images.pexels.com/photos/87651/earth-blue-planet-globe-planet-87651.jpeg?w=1200",
]

HERE = os.path.dirname(os.path.abspath(__file__))

for url in URLs:
    try:
        print(f"Intentando: {url[:60]}...")
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = response.read()
        
        b64 = base64.b64encode(data).decode('utf-8')
        print(f"✓ Descargado: {len(data)} bytes")
        print(f"Data URI (primeros 100 chars): data:image/jpeg;base64,{b64[:100]}...")
        break
    except Exception as e:
        print(f"✗ Error: {e}\n")
