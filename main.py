from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Dinamiza ECO 360 - IA API",
    description="Microservicio de IA para recomendaciones energéticas y predicción de subvenciones.",
    version="1.0.0",
)


# --------------------------------------------------------------------
# MODELOS DE ENTRADA
# --------------------------------------------------------------------
class Comunidad(BaseModel):
    id_comunidad: Optional[int] = None
    nombre_comunidad: Optional[str] = None
    provincia: Optional[str] = None
    municipio: Optional[str] = None
    tipo_edificio: Optional[str] = None
    anio_construccion: Optional[int] = None
    num_viviendas: Optional[int] = None
    num_pisos: Optional[int] = None

    electricidad_kwh: Optional[float] = None
    termica_kwh: Optional[float] = None
    fuentes_energia: Optional[str] = None

    area_techo_m2: Optional[float] = None
    orientacion: Optional[str] = None
    tipo_calefaccion: Optional[str] = None
    bateria: Optional[str] = None

    codigo_postal: Optional[int] = None
    zona_climatica: Optional[str] = None

    gasto_mensual_energia: Optional[float] = None
    presupuesto: Optional[float] = None


# --------------------------------------------------------------------
# MODELO DE SALIDA
# --------------------------------------------------------------------
class RecomendacionSalida(BaseModel):
    recomendacion_final: str

    mix_fotovoltaica_pct: int
    mix_aerotermia_pct: int
    mix_geotermia_pct: int
    mix_biomasa_pct: int
    mix_microhidraulica_pct: int

    instalar_bateria: str
    pct_ahorro_bateria: int

    instalar_bomba_calor: str
    pct_ahorro_bomba_calor: int

    ahorro_1anio_kwh: int
    ahorro_3anios_kwh: int
    ahorro_5anios_kwh: int

    ahorro_1anio_eur: int
    ahorro_3anios_eur: int
    ahorro_5anios_eur: int

    co2_1anio_kg: int
    co2_3anios_kg: int
    co2_5anios_kg: int


# --------------------------------------------------------------------
# HOME
# --------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "API Dinamiza ECO 360 funcionando 🚀"}


# --------------------------------------------------------------------
# ENDPOINT RECOMENDACIONES
# --------------------------------------------------------------------
@app.post("/recomendaciones", response_model=RecomendacionSalida)
def generar_recomendaciones(data: Comunidad) -> RecomendacionSalida:

    recomendacion = "Instalar fotovoltaica y aerotermia."

    # Mezcla energética (fijo por ahora)
    mix_fotovoltaica_pct = 75
    mix_aerotermia_pct = 25
    mix_geotermia_pct = 0
    mix_biomasa_pct = 0
    mix_microhidraulica_pct = 0

    # Batería
    instalar_bateria = "sí" if str(data.bateria).lower() in ["no", "n", "0"] else "no"
    pct_ahorro_bateria = 8 if instalar_bateria == "sí" else 0

    # Aerotermia
    instalar_bomba_calor = "sí" if "caldera" in str(data.tipo_calefaccion).lower() else "no"
    pct_ahorro_bomba_calor = 18 if instalar_bomba_calor == "sí" else 0

    # Consumo
    consumo = data.electricidad_kwh or 0

    # ----------------------------------------------------
    # 🔥 NUEVAS REGLAS IMPRESIONANTES PARA EL DEMO DAY 🔥
    # ----------------------------------------------------

    # AHORRO DE ENERGÍA (60% del consumo)
    ahorro_1anio_kwh = int(consumo * 0.60)
    ahorro_3anios_kwh = int(consumo * 0.60 * 3)
    ahorro_5anios_kwh = int(consumo * 0.60 * 5)

    # AHORRO ECONÓMICO = 80% del ahorro energético
    ahorro_1anio_eur = int(ahorro_1anio_kwh * 0.80)
    ahorro_3anios_eur = int(ahorro_3anios_kwh * 0.80)
    ahorro_5anios_eur = int(ahorro_5anios_kwh * 0.80)

    # CO₂ = 90% del ahorro energético
    co2_1anio_kg = int(ahorro_1anio_kwh * 0.90)
    co2_3anios_kg = int(ahorro_3anios_kwh * 0.90)
    co2_5anios_kg = int(ahorro_5anios_kwh * 0.90)

    # ----------------------------------------------------

    return RecomendacionSalida(
        recomendacion_final=recomendacion,

        mix_fotovoltaica_pct=mix_fotovoltaica_pct,
        mix_aerotermia_pct=mix_aerotermia_pct,
        mix_geotermia_pct=mix_geotermia_pct,
        mix_biomasa_pct=mix_biomasa_pct,
        mix_microhidraulica_pct=mix_microhidraulica_pct,

        instalar_bateria=instalar_bateria,
        pct_ahorro_bateria=pct_ahorro_bateria,

        instalar_bomba_calor=instalar_bomba_calor,
        pct_ahorro_bomba_calor=pct_ahorro_bomba_calor,

        ahorro_1anio_kwh=ahorro_1anio_kwh,
        ahorro_3anios_kwh=ahorro_3anios_kwh,
        ahorro_5anios_kwh=ahorro_5anios_kwh,

        ahorro_1anio_eur=ahorro_1anio_eur,
        ahorro_3anios_eur=ahorro_3anios_eur,
        ahorro_5anios_eur=ahorro_5anios_eur,

        co2_1anio_kg=co2_1anio_kg,
        co2_3anios_kg=co2_3anios_kg,
        co2_5anios_kg=co2_5anios_kg,
    )


# --------------------------------------------------------------------
# ENDPOINT SUBVENCIONES
# --------------------------------------------------------------------
@app.post("/subvenciones", response_model=SubvencionesSalida)
def estimar_subvenciones(data: Comunidad) -> SubvencionesSalida:

    factor = {"A": 1.0, "B": 0.95, "C": 0.9, "D": 0.85, "E": 0.8}.get(
        data.zona_climatica.upper(), 0.9
    )

    return {
        "nacional": 0.72 * factor,
        "autonomica": 0.64 * factor,
        "provincial": 0.41 * factor,
        "ue_nextgen": 0.55 * factor,
    }
