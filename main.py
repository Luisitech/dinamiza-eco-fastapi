from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# --------------------------------------------------------------------
# 🟦 INICIALIZAR FASTAPI
# --------------------------------------------------------------------
app = FastAPI(
    title="Dinamiza ECO 360 - IA API",
    description="Microservicio de IA para recomendaciones energéticas y predicción de subvenciones.",
    version="1.3.0",
)

# --------------------------------------------------------------------
# 🟦 MODELO DE ENTRADA
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
# 🏠 ENDPOINT HOME
# --------------------------------------------------------------------
@app.get("/")
def root():
    return {"message": "API Dinamiza ECO 360 funcionando 🚀"}



# --------------------------------------------------------------------
# 🟧 ENDPOINT DE SUBVENCIONES (REALISTA + COMPATIBLE XANO)
# --------------------------------------------------------------------
@app.post("/subvenciones")
def estimar_subvenciones(data: Comunidad):

    # ----------------------------
    # 1. Variables base
    # ----------------------------
    anio = data.anio_construccion or 0
    superficie = float(data.area_techo_m2 or 0)
    zona = (data.zona_climatica or "").upper()
    tipo = (data.tipo_edificio or "").lower()
    viviendas = data.num_viviendas or 1
    presupuesto = float(data.presupuesto or 0)

    # ----------------------------
    # 2. Reducción energética estimada (criterio real IDAE)
    # ----------------------------
    if superficie > 400:
        reduccion_estim = 0.55
    elif superficie > 200:
        reduccion_estim = 0.45
    elif superficie > 100:
        reduccion_estim = 0.35
    else:
        reduccion_estim = 0.30

    # ----------------------------
    # 3. Criterios
    # ----------------------------

    # NextGEN / PREE / Rehabilitación
    requisitos_nextgen = {
        "antiguedad": anio < 2007,
        "reduccion": reduccion_estim >= 0.30,
        "edificio_residencial": "residencial" in tipo or "vivienda" in tipo,
        "zona_valida": zona in ["A", "B", "C", "D", "E"]
    }
    nextgen_elegible = all(requisitos_nextgen.values())

    # Nacional (IDAE)
    requisitos_nacional = {
        "renovables": True,
        "reduccion_minima_20": reduccion_estim >= 0.20,
        "presupuesto_min": presupuesto >= 8000
    }
    nacional_elegible = all(requisitos_nacional.values())

    # Autonómica
    requisitos_autonomica = {
        "reduccion": reduccion_estim >= 0.20,
        "antiguedad": anio < 2013,
        "residencial": "residencial" in tipo or viviendas >= 3
    }
    autonomica_elegible = all(requisitos_autonomica.values())

    # Municipal
    requisitos_municipal = {
        "fv_instalable": superficie >= 30,
        "presupuesto_max": presupuesto <= 500000
    }
    municipal_elegible = all(requisitos_municipal.values())

    # ----------------------------
    # 4. Score global (modelo consultoría)
    # ----------------------------
    score = (
        (40 if nextgen_elegible else 0) +
        (30 if nacional_elegible else 0) +
        (20 if autonomica_elegible else 0) +
        (10 if municipal_elegible else 0)
    )

    # ----------------------------
    # 5. Estructura FINAL para XANO
    # ----------------------------
    return {
        "subvenciones": {
            "nextgen_elegible": nextgen_elegible,
            "nacional_elegible": nacional_elegible,
            "autonomica_elegible": autonomica_elegible,
            "municipal_elegible": municipal_elegible,
            "reduccion_energetica_estimado_pct": int(reduccion_estim * 100),
            "probabilidad_total_subvencion_pct": score
        },
        "criterios": {
            "nextgen": requisitos_nextgen,
            "nacional": requisitos_nacional,
            "autonomica": requisitos_autonomica,
            "municipal": requisitos_municipal
        }
    }



# --------------------------------------------------------------------
# 🟧 ENDPOINT RECOMENDACIONES (SIN SUBVENCIONES — COMO ANTES)
# --------------------------------------------------------------------
@app.post("/recomendaciones")
def generar_recomendaciones(data: Comunidad):

    consumo_elec = float(data.electricidad_kwh or 0)
    consumo_term = float(data.termica_kwh or 0)
    total_demanda = consumo_elec + consumo_term

    superficie = float(data.area_techo_m2 or 0)
    orient = (data.orientacion or "").lower()
    zona = (data.zona_climatica or "").upper()
    presupuesto = float(data.presupuesto or 0)

    # Factores
    factor_clima = {"A":1.0,"B":0.95,"C":0.9,"D":0.85,"E":0.8}.get(zona,0.9)

    factor_orient = 1.0
    if "norte" in orient: factor_orient = 0.55
    elif "este" in orient or "oeste" in orient: factor_orient = 0.80

    capacidad_fv_kwp = superficie * 0.18
    capacidad_fv_max = capacidad_fv_kwp * factor_orient
    fv_pct_max = min(75, int((capacidad_fv_max / max(total_demanda/1000,0.0001)) * 100))

    # Mix Base
    if total_demanda == 0:
        pct_fv, pct_aero = 60, 40
    else:
        ratio_elec = consumo_elec / total_demanda
        ratio_term = consumo_term / total_demanda
        pct_fv = int(70 * ratio_elec)
        pct_aero = int(50 * ratio_term * factor_clima)

    pct_fv = min(pct_fv, fv_pct_max)

    pct_geotermia = 10 if presupuesto > 250000 and factor_clima <= 0.9 else 0
    pct_biomasa = 10 if factor_clima <= 0.85 else 0
    pct_micro = 0

    if data.tipo_edificio and data.tipo_edificio.lower() in ["industrial","fábrica","planta"]:
        pct_micro = 10
    if "rio" in (data.fuentes_energia or "").lower(): pct_micro = 10
    if "canal" in (data.fuentes_energia or "").lower(): pct_micro = 10

    # Normalizar a 100%
    suma = pct_fv + pct_aero + pct_geotermia + pct_biomasa + pct_micro
    if suma == 0:
        pct_fv, pct_aero = 50, 50
    else:
        f = 100 / suma
        pct_fv = int(pct_fv*f)
        pct_aero = int(pct_aero*f)
        pct_geotermia = int(pct_geotermia*f)
        pct_biomasa = int(pct_biomasa*f)
        pct_micro = int(pct_micro*f)

    ajuste = 100 - (pct_fv + pct_aero + pct_geotermia + pct_biomasa + pct_micro)
    pct_fv += ajuste

    # Batería
    instalar_bateria = data.bateria or pct_fv >= 40
    pct_ahorro_bateria = 8 if instalar_bateria else 0

    # Bomba de calor
    tipo_calef = (data.tipo_calefaccion or "").lower()
    instalar_bomba_calor = "caldera" in tipo_calef or consumo_term > 30000
    pct_ahorro_bomba_calor = 18 if instalar_bomba_calor else 0

    # Ahorros
    ahorro_pct_total = (pct_fv*0.5 + pct_aero*0.3 + pct_ahorro_bomba_calor*0.1)/100
    ahorro_1 = int(total_demanda * ahorro_pct_total)
    ahorro_3 = ahorro_1 * 3
    ahorro_5 = ahorro_1 * 5

    ahorro_1_eur = int(ahorro_1 * 0.75)
    ahorro_3_eur = ahorro_1_eur * 3
    ahorro_5_eur = ahorro_1_eur * 5

    co2_1 = int(ahorro_1 * 0.9)
    co2_3 = co2_1 * 3
    co2_5 = co2_1 * 5

    # Texto final
    nombre = data.nombre_comunidad or "la comunidad"
    muni = data.municipio or ""
    prov = data.provincia or ""
    ubic = f" de {muni} ({prov})" if muni or prov else ""

    recomendacion = (
        f"Para {nombre}{ubic}, el mix óptimo recomendado es {pct_fv}% fotovoltaica, "
        f"{pct_aero}% aerotermia, {pct_geotermia}% geotermia, "
        f"{pct_biomasa}% biomasa y {pct_micro}% microhidráulica."
    )

    # Solo recomendaciones (sin subvenciones)
    return {
        "id_comunidad": data.id_comunidad,
        "recomendacion_final": recomendacion,
        "mix_fotovoltaica_pct": pct_fv,
        "mix_aerotermia_pct": pct_aero,
        "mix_geotermia_pct": pct_geotermia,
        "mix_biomasa_pct": pct_biomasa,
        "mix_microhidraulica_pct": pct_micro,
        "instalar_bateria": instalar_bateria,
        "pct_ahorro_bateria": pct_ahorro_bateria,
        "instalar_bomba_calor": instalar_bomba_calor,
        "pct_ahorro_bomba_calor": pct_ahorro_bomba_calor,
        "ahorro_1anio_kwh": ahorro_1,
        "ahorro_3anios_kwh": ahorro_3,
        "ahorro_5anios_kwh": ahorro_5,
        "ahorro_1anio_eur": ahorro_1_eur,
        "ahorro_3anios_eur": ahorro_3_eur,
        "ahorro_5anios_eur": ahorro_5_eur,
        "co2_1anio_kg": co2_1,
        "co2_3anios_kg": co2_3,
        "co2_5anios_kg": co2_5,
    }
