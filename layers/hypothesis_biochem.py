# -*- coding: utf-8 -*-
"""
CAPA ANOTADORA — Hipótesis de bioquímica por familia ZEE.

Dada la familia de un cuerpo, AVENTURA qué tipo de vida (si la hubiera) sería
químicamente compatible con ese ecosistema físico. NO afecta a la clasificación:
solo añade una hipótesis a la salida.

>>> ADVERTENCIA CIENTÍFICA <<<
Todo lo de aquí es ESPECULATIVO salvo donde se indica un análogo terrestre REAL
(familias O y V tienen ecosistemas quimiosintéticos reales en la Tierra). No es una
predicción de que exista vida; es "qué química sería consistente con esta ZEE".

Nota sobre alternativas a la vida terrestre:
  - El disolvente es lo que más cambia: metano/etano líquido o amoníaco en vez de agua.
  - El esqueleto casi siempre sigue siendo CARBONO (versátil, encadena). El SILICIO es
    la alternativa clásica, plausible solo en ambientes muy calientes, y aun así frágil.
  - El litio, el boro, etc. NO sirven como esqueleto (no forman cadenas estables).

Campos de la hipótesis:
  disolvente · esqueleto · energia · metabolismo · membrana · analogo · plausibilidad
"""
from atlas_core.registry import annotator

# plausibilidad: REAL (existe en la Tierra) · PLAUSIBLE · ESPECULATIVO · MUY_ESPECULATIVO
HIPOTESIS = {
    "A": {  # Acuática — la vida tal como la conocemos
        "disolvente": "agua líquida",
        "esqueleto": "carbono",
        "energia": "luz estelar (fotosíntesis) + redox",
        "metabolismo": "fotosíntesis oxigénica y respiración aeróbica/anaeróbica",
        "membrana": "bicapa de fosfolípidos",
        "analogo": "toda la biosfera terrestre",
        "plausibilidad": "REAL",
        "resumen": "Vida tipo terrestre: carbono en agua, con la luz de la estrella "
                   "como motor. Es el único caso confirmado que existe.",
    },
    "M": {  # Metánica — el caso "litio/metano" que preguntabas, bien planteado
        "disolvente": "metano / etano líquido (~-180 °C)",
        "esqueleto": "carbono (química orgánica en frío)",
        "energia": "escasa luz UV + gradientes químicos",
        "metabolismo": "hipótesis Titán: consumir H2 + acetileno/etano y exhalar metano",
        "membrana": "azotosoma (acrilonitrilo) en vez de fosfolípidos, que se congelarían",
        "analogo": "ninguno terrestre; modelos teóricos de Titán",
        "plausibilidad": "ESPECULATIVO",
        "resumen": "Vida de carbono pero en un MAR DE METANO, no de agua. Membranas "
                   "distintas (azotosomas) y metabolismo lentísimo por el frío. Aquí es "
                   "donde tendría sentido una bioquímica alternativa, aunque basada en "
                   "cambiar el disolvente, no en sustituir el carbono por litio.",
    },
    "O": {  # Océano interno — quimiosíntesis, ¡con análogo REAL!
        "disolvente": "agua líquida (bajo hielo)",
        "esqueleto": "carbono",
        "energia": "hidrotermal: H2, H2S, Fe/S del fondo rocoso (SIN luz)",
        "metabolismo": "quimiosíntesis: metanogénesis, oxidación de azufre/hierro",
        "membrana": "bicapa lipídica (como los microbios de fuentes hidrotermales)",
        "analogo": "ecosistemas de fumarolas negras del fondo oceánico terrestre",
        "plausibilidad": "PLAUSIBLE",
        "resumen": "Vida sin luz, alimentada por la química roca-agua del fondo. En la "
                   "Tierra ESTO YA EXISTE en las fuentes hidrotermales abisales, por eso "
                   "Europa/Encélado son los objetivos astrobiológicos más serios.",
    },
    "V": {  # Volcánica — termófilos, y aquí sí cabe el silicio
        "disolvente": "agua/salmuera en bordes, o films finos",
        "esqueleto": "carbono (termófilo); silicio concebible en zonas muy calientes",
        "energia": "calor interno, gradientes redox volcánicos (S, Fe)",
        "metabolismo": "quimiolitotrofía: oxidación de azufre e hidrógeno a alta T",
        "membrana": "lípidos de arqueas hipertermófilas (muy estables al calor)",
        "analogo": "hipertermófilos terrestres junto a volcanes y géiseres",
        "plausibilidad": "PLAUSIBLE",
        "resumen": "Vida amante del calor extremo. En la Tierra hay microbios así en "
                   "volcanes. Es el único entorno donde una química de SILICIO se discute "
                   "en serio, aunque el carbono seguiría siendo favorito.",
    },
    "C": {  # Criogénica — vida latente/marginal
        "disolvente": "bolsas de salmuera; hielo casi total",
        "esqueleto": "carbono",
        "energia": "casi nula",
        "metabolismo": "latencia/criopreservación; metabolismo mínimo en salmueras",
        "membrana": "lípidos con anticongelantes",
        "analogo": "criófilos del permafrost y salmueras subglaciales terrestres",
        "plausibilidad": "MUY_ESPECULATIVO",
        "resumen": "A lo sumo vida dormida en bolsas saladas que no se congelan. Energía "
                   "insuficiente para un ecosistema activo; más 'conservación' que 'vida'.",
    },
    "G": {  # Gaseosa — "flotadores" en las nubes
        "disolvente": "gotas de agua/amoníaco en capas de nube templadas",
        "esqueleto": "carbono",
        "energia": "luz en las capas altas + convección térmica",
        "metabolismo": "plancton aéreo fotosintético (hipótesis Sagan-Salpeter)",
        "membrana": "vesículas flotantes que regulan su flotabilidad",
        "analogo": "ninguno; microbios en nubes terrestres como pista débil",
        "plausibilidad": "MUY_ESPECULATIVO",
        "resumen": "Sin superficie: vida 'flotadora' suspendida en la banda de nubes con "
                   "temperatura templada. Propuesto para Júpiter y para las nubes de Venus.",
    },
    "X": {
        "disolvente": "—", "esqueleto": "—", "energia": "—", "metabolismo": "—",
        "membrana": "—", "analogo": "—", "plausibilidad": "SIN_DATOS",
        "resumen": "Datos insuficientes para aventurar una bioquímica.",
    },
}


@annotator("biochem")
def annotate(body, clase, indices, ctx):
    h = HIPOTESIS.get(clase)
    if h is None:
        return {"plausibilidad": "n/a",
                "resumen": f"La clase '{clase}' no es una familia ZEE; "
                           "esta capa solo interpreta esquemas ZEE."}
    return dict(h)
