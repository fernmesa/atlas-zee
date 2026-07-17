# -*- coding: utf-8 -*-
"""
Importer robusto para NASA Exoplanet Archive con reintentos.
Usa CSV directo + fallback a JSON.
"""
import sys, os, csv, json, time
try:
    import urllib.request, urllib.error
except ImportError:
    import urllib2 as urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTPUT = os.path.join(ROOT, "data", "atlas_bodies_nasa_import.csv")

def download_with_retry(url, max_retries=3):
    """Descarga con reintentos."""
    for attempt in range(max_retries):
        try:
            print(f"[intento {attempt+1}] GET {url[:80]}...")
            with urllib.request.urlopen(url, timeout=30) as response:
                data = response.read()
                print(f"✅ Descargado {len(data)} bytes")
                return data.decode('utf-8')
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP {e.code}: {e.reason}")
            time.sleep(2 ** attempt)  # exponential backoff
        except Exception as e:
            print(f"⚠️  Error: {e}")
            time.sleep(2 ** attempt)
    return None

def main():
    # Intento 1: NASA CSV directo
    print("\n=== ATLAS NASA IMPORTER (Robusto) ===\n")
    
    # URL de descarga directa de CSV desde NASA Exoplanet Archive
    csv_url = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?query=select+pl_name,pl_rade,pl_masse,pl_orbper,pl_eqt,disc_year,discoverymethod+from+exoplanets+where+pl_rade>0+and+pl_masse>0+limit+1000&format=csv"
    
    print("Intentando descarga CSV...")
    csv_data = download_with_retry(csv_url)
    
    if not csv_data:
        print("⚠️  CSV falló. Aquí te muestro cómo descargar manualmente:\n")
        print("1. Ve a: https://exoplanetarchive.ipac.caltech.edu/cgi-bin/TblView/nph-tblView")
        print("2. Selecciona: Exoplanet table")
        print("3. Descarga CSV")
        print("4. Coloca el archivo en: data/exoplanet_archive.csv")
        print("5. Ejecuta: python tools/import_from_csv.py")
        return
    
    print("✅ Parseando CSV...")
    lines = csv_data.strip().split('\n')
    if len(lines) < 2:
        print("❌ CSV vacío")
        return
    
    # Escribir resultado
    with open(OUTPUT, 'w', newline='', encoding='utf-8') as f:
        f.write(csv_data)
    
    # Contar
    reader = csv.DictReader(csv_data.split('\n'))
    count = sum(1 for _ in reader)
    print(f"✅ Importados {count} cuerpos")
    print(f"   → {OUTPUT}")

if __name__ == "__main__":
    main()
