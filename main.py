from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(
    title="Dinamiza ECO 360 - IA API",
    description="Microservicio de IA para recomendaciones energéticas y predicción de subvenciones.",
    version="1.1.1",
)


# --------------------------------------------------------------------
# 🟦 MODELOS DE ENTRADA (COINCIDEN CON LA TABLA COMUNIDADES DE XANO)
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

    bateria: Optional[bool] = None

    codigo_postal: Optional[int] = None
    zona_climatica: Optional[str] = None

    gasto_mensual_energia: Optional[float] = None
    presupuesto: Optional[float] = None


# --------------------------------------------------------------------
# 🟩 MODELO DE SALIDA PARA RECOMENDACIONES (COINCIDE CON XANO)
# --------------------------------------------------------------------
class RecomendacionSalida(BaseModel):
    recomendacion_final: str

    mix_fotovoltaica_pct: int
    mix_aerotermia_pct: int
    mix_geotermia_pct: int
    mix_biomasa_pct: int
    mix_microhidraulica_pct: int

    instalar_bateria: bool
    pct_ahorro_bateria: int

    instalar_bomba_calor: bool
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
# 🔵 MODELO SALIDA SUBVENCIONES (placeholder)
# --------------------------------------------------------------------
class SubvencionesSalida(BaseModel):
    nacional: float
    autonomica: float
    provincial: float
    ue_nextgen: float


# --------------------------------------------------------------------
# 🟢 ENDPOINT HOME
# --------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "API Dinamiza ECO 360 funcionando 🚀"}


# --------------------------------------------------------------------
# 🟧 ENDPOINT DE RECOMENDACIONES (lógica demo para el pitch)
# --------------------------------------------------------------------
@app.post("/recomendaciones", response_model=RecomendacionSalida)
def generar_recomendaciones(data: Comunidad) -> RecomendacionSalida:
    nombre = data.nombre_comunidad or "la comunidad"
    municipio = data.municipio or ""
    provincia = data.provincia or ""

    ubicacion = f" de {municipio} ({provincia})" if municipio or provincia else ""
    recomendacion = (
        f"Para {nombre}{ubicacion}, se recomienda una solución combinada con "
        "fotovoltaica en cubierta como recurso principal (≈70 % de la demanda) "
        "y un sistema de aerotermia de apoyo (≈30 %) que permita reducir de forma "
        "muy significativa el consumo energético y las emisiones de CO₂."
    )

    mix_fotovoltaica_pct = 70
    mix_aerotermia_pct = 30
    mix_geotermia_pct = 0
    mix_biomasa_pct = 0
    mix_microhidraulica_pct = 0

    instalar_bateria = False if data.bateria is False else True
    pct_ahorro_bateria = 8 if instalar_bateria else 0

    instalar_bomba_calor = "caldera" in str(data.tipo_calefaccion or "").lower()
    pct_ahorro_bomba_calor = 18 if instalar_bomba_calor else 0

    consumo = float(data.electricidad_kwh or 0.0)

    ahorro_1anio_kwh = int(consumo * 0.60)
    ahorro_3anios_kwh = int(consumo * 0.60 * 3)
    ahorro_5anios_kwh = int(consumo * 0.60 * 5)

    ahorro_1anio_eur = int(ahorro_1anio_kwh * 0.80)
    ahorro_3anios_eur = int(ahorro_3anios_kwh * 0.80)
    ahorro_5anios_eur = int(ahorro_5anios_kwh * 0.80)

    co2_1anio_kg = int(ahorro_1anio_kwh * 0.90)
    co2_3anios_kg = int(ahorro_3anios_kwh * 0.90)
    co2_5anios_kg = int(ahorro_5anios_kwh * 0.90)

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
# 🟠 ENDPOINT SUBVENCIONES
# --------------------------------------------------------------------
@app.post("/subvenciones", response_model=SubvencionesSalida)
def estimar_subvenciones(data: Comunidad) -> SubvencionesSalida:
    factor = {"A": 1.0, "B": 0.95, "C": 0.9, "D": 0.85, "E": 0.8}.get(
        (data.zona_climatica or "").upper(), 0.9
    )

    return SubvencionesSalida(
        nacional=0.72 * factor,
        autonomica=0.64 * factor,
        provincial=0.41 * factor,
        ue_nextgen=0.55 * factor,
    )
