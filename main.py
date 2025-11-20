from typing import List, Optional

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(
    title="Dinamiza ECO 360 - IA API",
    description="Microservicio de IA para recomendaciones energéticas y predicción de subvenciones.",
    version="1.0.0",
)


# ------------------------------
# MODELOS DE ENTRADA
# ------------------------------

class Comunidad(BaseModel):
    id_comunidad: Optional[int] = None
    nombre_comunidad: Optional[str] = None
    provincia: Optional[str] = None
    municipio: Optional[str] = None
    tipo_edificio: Optional[str] = None
    anio_construccion: Optional[int] = None
    num_viviendas: Optional[int] = None
    superficie: Optional[float] = None
    tipo_calefaccion: Optional[str] = None
    tipo_aislamiento: Optional[str] = None


# ------------------------------
# MODELOS DE SALIDA
# ------------------------------

class RecomendacionSalida(BaseModel):
    recomendaciones: List[str]
    prioridad: List[str]
    ahorro_estimado: float


class SubvencionesSalida(BaseModel):
    nacional: float
    autonomica: float
    provincial: float
    ue_nextgen: float


# ------------------------------
# ENDPOINTS
# ------------------------------

@app.get("/")
def root():
    return {"message": "API Dinamiza ECO 360 funcionando 🚀"}


@app.post("/recomendaciones", response_model=RecomendacionSalida)
def generar_recomendaciones(data: Comunidad):

    recomendaciones = [
        "Instalar sistema de aislamiento SATE para reducir pérdidas térmicas.",
        "Instalar placas solares fotovoltaicas para autoconsumo.",
        "Sustituir caldera por sistema de aerotermia de alta eficiencia."
    ]

    prioridad = ["Aislamiento", "Solar FV", "Aerotermia"]
    ahorro_estimado = 34.7  # % estimado (placeholder)

    return {
        "recomendaciones": recomendaciones,
        "prioridad": prioridad,
        "ahorro_estimado": ahorro_estimado
    }


@app.post("/subvenciones", response_model=SubvencionesSalida)
def estimar_subvenciones(data: Comunidad):

    # Placeholder de probabilidades (luego lo sustituimos con ML real)
    return {
        "nacional": 0.72,
        "autonomica": 0.64,
        "provincial": 0.41,
        "ue_nextgen": 0.55
    }
