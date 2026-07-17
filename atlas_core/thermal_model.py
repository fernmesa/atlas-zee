# -*- coding: utf-8 -*-
"""
Modelo termal completo para ATLAS v0.3.
Considera: radiación estelar + calor interno + mareas + temperatura de equilibrio.
"""
import math

class ThermalBudget:
    """Calcula presupuesto energético total."""
    
    EARTH_MASS = 1.0
    EARTH_RADIUS = 1.0
    EARTH_AGE = 4.54e9
    EARTH_STELLAR = 1360.0  # W/m^2
    EARTH_GEOTHERMAL = 0.063  # W/m^2
    EARTH_TEQM = 288.0  # K
    
    def __init__(self, nombre, tipo_cuerpo):
        self.nombre = nombre
        self.tipo = tipo_cuerpo
        self.masa = None
        self.radio = None
        self.edad = None
        self.insol = None
        self.temp_eq = None  # K (fallback)
        self.tiene_compañero_masivo = False
        self.distancia_compañero = None
        self.masa_compañero = None
        
    def E_stellar(self):
        """Energia de radiacion estelar."""
        if self.insol and self.insol > 0:
            return min(10.0, (self.insol / 1360.0) * 9.0)
        elif self.temp_eq and self.temp_eq > 0:
            return min(10.0, (self.temp_eq / 288.0) * 9.0)
        return 0
    
    def E_internal_radioactive(self):
        """Energia de desintegracion radiactiva."""
        if not self.masa or not self.edad or self.masa <= 0:
            return 0
        
        edad_ga = self.edad / 1e9
        f_radioactive = math.exp(-edad_ga / 8.0)
        
        if self.radio and self.radio > 0:
            heat_density = (self.masa ** (2.0/3.0)) / (self.radio ** 2)
            earth_heat_density = (1.0 ** (2.0/3.0)) / (1.0 ** 2)
            flux = (heat_density / earth_heat_density) * self.EARTH_GEOTHERMAL * f_radioactive
            E_internal = min(10.0, (flux / self.EARTH_GEOTHERMAL) * 5.0)
            return E_internal
        
        return 0
    
    def E_tidal(self):
        """Energia de disipacion de mareas."""
        if not self.tiene_compañero_masivo or not self.distancia_compañero:
            return 0
        
        if not self.masa or not self.radio or self.radio <= 0:
            return 0
        
        if self.distancia_compañero <= 0:
            return 0
        
        mass_ratio = (self.masa_compañero or 1.0) / 318.0
        distance_factor = (1.0 / self.distancia_compañero) ** 2
        
        if self.tipo in ("luna", "satelite"):
            base_tidal = 2.0 * mass_ratio * distance_factor
            E_tidal = min(10.0, base_tidal * 5.0)
            return E_tidal
        
        return 0
    
    def E_total(self, mode="realistic"):
        """Energia total."""
        E_s = self.E_stellar()
        E_i = self.E_internal_radioactive()
        E_t = self.E_tidal()
        
        if mode == "dominant":
            return max(E_s, E_i, E_t)
        else:
            if E_t > E_s * 1.5:
                return (E_s + E_i + E_t * 2.0) / 4.0
            else:
                return (E_s * 0.6 + E_i * 0.2 + E_t * 0.2)
    
    def breakdown(self):
        """Desglose por fuentes."""
        return {
            "E_stellar": round(self.E_stellar(), 2),
            "E_internal": round(self.E_internal_radioactive(), 2),
            "E_tidal": round(self.E_tidal(), 2),
            "E_total": round(self.E_total(), 2),
            "dominant": self._dominant_source()
        }
    
    def _dominant_source(self):
        E_s = self.E_stellar()
        E_i = self.E_internal_radioactive()
        E_t = self.E_tidal()
        
        vals = [("stellar", E_s), ("internal", E_i), ("tidal", E_t)]
        max_val = max(vals, key=lambda x: x[1])
        return max_val[0] if max_val[1] > 0 else "none"

