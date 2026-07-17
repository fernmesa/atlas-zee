"""
Descarga imagen de la Vía Láctea de Wikimedia Commons (dominio público).
Usamos una imagen de alta resolución en formato web-friendly.
"""
import urllib.request, base64, os

HERE = os.path.dirname(os.path.abspath(__file__))

# Imagen de la Vía Láctea: "Milky Way Arms" (Dominio público)
# Fuente: Wikimedia Commons
URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e5/Milky_Way_2005.jpg/1280px-Milky_Way_2005.jpg"

try:
    print("Descargando imagen de la Vía Láctea...")
    with urllib.request.urlopen(URL, timeout=30) as response:
        data = response.read()
    
    # Convertir a base64 para incrustar en HTML
    b64 = base64.b64encode(data).decode('utf-8')
    print(f"Imagen descargada: {len(data)} bytes")
    print(f"Base64: {len(b64)} caracteres (primeros 100: {b64[:100]}...)")
    
    # Guardar como archivo para referencia
    out = os.path.join(HERE, "milky_way.jpg")
    with open(out, 'wb') as f:
        f.write(data)
    print(f"Guardado en: {out}")
    print("\nPara incrustar en HTML:")
    print(f"<img src='data:image/jpeg;base64,{b64[:50]}...' />")
    
except Exception as e:
    print(f"Error: {e}")
