from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Dinamiza ECO 360 - IA API",
    description="Microservicio de IA para recomendaciones energéticas y predicción de subvenciones.",
    version="1.0.0",
)

# -------------------------------------------------------------------
# MODELOS DE ENTRADA
# -------------------------------------------------------------------


class Comunidad(BaseModel):
    """
    Modelo de entrada que debe coincidir con la tabla `comunidades` de Xano.
    Todos los campos vienen del registro de comunidad ya guardado en Xano.
    """
    id_comunidad: int
    comunidad: str
    provincia: str
    municipio: str
    tipo_edificio: str
    anio_construccion: int
    num_viviendas: int
    num_pisos: int
    electricidad_kwh: int
    termica_kwh: int
    fuentes_energia: str
    area_techo_m2: int
    orientacion: str
    tipo_calefaccion: str
    bateria: str               # "yes" / "no"
    codigo_postal: int
    zona_climatica: str        # A, B, C, D, E...
    gasto_mensual_energia: int
    presupuesto: int


# -------------------------------------------------------------------
# MODELOS DE SALIDA
# -------------------------------------------------------------------


class RecomendacionSalida(BaseModel):
    """
    Modelo de salida que FastAPI devuelve a Xano y que luego Xano
    guarda en la tabla `recomendaciones`.
    Los nombres de los campos deben coincidir 100% con los que
    estás usando en Xano (ia_reco.campo).
    """
    recomendacion_final: str

    mix_fotovoltaica_pct: int
    mix_aerotermia_pct: int
    mix_geotermia_pct: int
    mix_biomasa_pct: int
    mix_microhidraulica_pct: int

    instalar_bateria: str          # "sí"/"no"
    pct_ahorro_bateria: int

    instalar_bomba_calor: str      # "sí"/"no"
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


class SubvencionesSalida(BaseModel):
    """
    Placeholder de salida para el endpoint de subvenciones.
    Más adelante lo podemos alinear con la tabla de subvenciones de Xano.
    """
    nacional: float
    autonomica: float
    provincial: float
    ue_nextgen: float


# -------------------------------------------------------------------
# ENDPOINTS
# -------------------------------------------------------------------


@app.get("/")
def root():
    return {"message": "API Dinamiza ECO 360 funcionando 🚀"}


@app.post("/recomendaciones", response_model=RecomendacionSalida)
def generar_recomendaciones(data: Comunidad) -> RecomendacionSalida:
    """
    Endpoint que recibe los datos completos de una comunidad desde Xano
    y devuelve una recomendación energética + ahorros estimados.

    Ahora mismo la lógica es de ejemplo (reglas simples).
    Más adelante aquí enchufamos el modelo de ML real.
    """

    # --- Ejemplo de lógica muy sencilla sólo para tener algo funcional ---

    # Recomendación base
    recomendacion = "Instalar fotovoltaica y mejora de sistema de calefacción."

    # Mezcla de tecnologías (porcentaje aproximado)
    mix_fotovoltaica_pct = 50
    mix_aerotermia_pct = 25
    mix_geotermia_pct = 0
    mix_biomasa_pct = 10
    mix_microhidraulica_pct = 15

    # Decisiones sobre batería
    instalar_bateria = "sí" if data.bateria.lower() in ["no", "n", "0"] else "no"
    pct_ahorro_bateria = 8 if instalar_bateria == "sí" else 0

    # Decisiones sobre bomba de calor
    instalar_bomba_calor = "sí" if "caldera" in data.tipo_calefaccion.lower() else "no"
    pct_ahorro_bomba_calor = 18 if instalar_bomba_calor == "sí" else 0

    # Ahorros energéticos (kWh) – ejemplo: % del consumo actual
    ahorro_1anio_kwh = int(data.electricidad_kwh * 0.15)
    ahorro_3anios_kwh = int(data.electricidad_kwh * 0.15 * 3)
    ahorro_5anios_kwh = int(data.electricidad_kwh * 0.15 * 5)

    # Conversión a € (ejemplo: 0.20 €/kWh)
    precio_kwh = 0.20
    ahorro_1anio_eur = int(ahorro_1anio_kwh * precio_kwh)
    ahorro_3anios_eur = int(ahorro_3anios_kwh * precio_kwh)
    ahorro_5anios_eur = int(ahorro_5anios_kwh * precio_kwh)

    # Reducción de CO2 (ejemplo: 0.25 kg CO2 por kWh evitado)
    factor_co2 = 0.25
    co2_1anio_kg = int(ahorro_1anio_kwh * factor_co2)
    co2_3anios_kg = int(ahorro_3anios_kwh * factor_co2)
    co2_5anios_kg = int(ahorro_5anios_kwh * factor_co2)

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


@app.post("/subvenciones", response_model=SubvencionesSalida)
def estimar_subvenciones(data: Comunidad) -> SubvencionesSalida:
    """
    Endpoint placeholder para subvenciones.
    De momento devuelve probabilidades fijas; luego lo podemos
    conectar a otro modelo de IA o a reglas de negocio.
    """

    # Ejemplo tonto: variar un poco según zona climática
    factor = {"A": 1.0, "B": 0.95, "C": 0.9, "D": 0.85, "E": 0.8}.get(
        data.zona_climatica.upper(), 0.9
    )

    return SubvencionesSalida(
        nacional=0.72 * factor,
        autonomica=0.64 * factor,
        provincial=0.41 * factor,
        ue_nextgen=0.55 * factor,
    )
