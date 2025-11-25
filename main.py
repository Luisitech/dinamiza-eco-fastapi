from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

# --------------------------------------------------------------------
# 🟦 INICIALIZAR FASTAPI
# --------------------------------------------------------------------
app = FastAPI(
    title="Dinamiza ECO 360 - IA API",
    description="Microservicio de IA para recomendaciones energéticas y predicción de subvenciones.",
    version="1.1.1",
)

# --------------------------------------------------------------------
# 🟠 ENDPOINT SUBVENCIONES
# --------------------------------------------------------------------
@app.post("/recomendaciones", response_model=RecomendacionSalida)
def generar_recomendaciones(data: Comunidad) -> RecomendacionSalida:

    # -----------------------------
    # 1. Extraer variables base
    # -----------------------------
    consumo_elec = float(data.electricidad_kwh or 0.0)
    consumo_term = float(data.termica_kwh or 0.0)
    total_demanda = consumo_elec + consumo_term

    superficie = float(data.area_techo_m2 or 0)
    viviendas = data.num_viviendas or 1
    orient = (data.orientacion or "").lower()
    zona = (data.zona_climatica or "").upper()
    presupuesto = float(data.presupuesto or 0)

    # -----------------------------
    # 2. FACTOR CLIMÁTICO
    # -----------------------------
    factor_clima = {
        "A": 1.0,  # muy cálido
        "B": 0.95,
        "C": 0.9,
        "D": 0.85,
        "E": 0.8,  # muy frío
    }.get(zona, 0.9)

    # -----------------------------
    # 3. FACTOR ORIENTACIÓN FV
    # -----------------------------
    factor_orient = 1.0
    if "norte" in orient:
        factor_orient = 0.55
    elif "este" in orient or "oeste" in orient:
        factor_orient = 0.80
    elif "sur" in orient:
        factor_orient = 1.0

    # -----------------------------
    # 4. Capacidad FV disponible
    #    1 m2 ≈ 180 Wp → 0.18 kWp
    # -----------------------------
    capacidad_fv_kwp = superficie * 0.18
    capacidad_fv_max = capacidad_fv_kwp * factor_orient

    # En comunidades grandes, FV no suele cubrir todo → limitamos el % máximo
    fv_pct_max = min(75, int((capacidad_fv_max / (total_demanda / 1000 + 1e-6)) * 100))

    # -----------------------------
    # 5. Mix base según demanda térmica vs eléctrica
    # -----------------------------
    if total_demanda == 0:
        pct_fv = 60
        pct_aero = 40
    else:
        ratio_elec = consumo_elec / total_demanda
        ratio_term = consumo_term / total_demanda

        pct_fv = int(70 * ratio_elec)
        pct_aero = int(50 * ratio_term * factor_clima)

    # Ajustar FV al máximo real permitido por cubierta
    pct_fv = min(pct_fv, fv_pct_max)

    # -----------------------------
    # 6. Geotermia, biomasa y microhidráulica
    # -----------------------------
    pct_geotermia = 0
    pct_biomasa = 0
    pct_micro = 0

    # Geotermia solo en presupuestos altos
    if presupuesto > 250000 and factor_clima <= 0.9:
        pct_geotermia = 10

    # Biomasa útil solo en zonas frías
    if factor_clima <= 0.85:
        pct_biomasa = 10

    # Ajustes finales para que sumen 100
    suma_parcial = pct_fv + pct_aero + pct_geotermia + pct_biomasa
    if suma_parcial < 100:
        pct_micro = 100 - suma_parcial
    else:
        # Normalizar si excede
        factor_norm = 100 / suma_parcial
        pct_fv = int(pct_fv * factor_norm)
        pct_aero = int(pct_aero * factor_norm)
        pct_geotermia = int(pct_geotermia * factor_norm)
        pct_biomasa = int(pct_biomasa * factor_norm)
        pct_micro = 0

    # -----------------------------
    # 7. Reglas para batería
    # -----------------------------
    instalar_bateria = False
    if data.bateria:
        instalar_bateria = True
    elif pct_fv >= 40:
        instalar_bateria = True

    pct_ahorro_bateria = 8 if instalar_bateria else 0

    # -----------------------------
    # 8. Bomba de calor
    # -----------------------------
    tipo_calef = (data.tipo_calefaccion or "").lower()
    instalar_bomba_calor = "caldera" in tipo_calef or consumo_term > 30000
    pct_ahorro_bomba_calor = 18 if instalar_bomba_calor else 0

    # -----------------------------
    # 9. Estimaciones de ahorros (realistas)
    # -----------------------------
    ahorro_pct_total = (pct_fv * 0.5 + pct_aero * 0.3 + pct_ahorro_bomba_calor * 0.1) / 100
    ahorro_1anio_kwh = int(total_demanda * ahorro_pct_total)
    ahorro_3anios_kwh = ahorro_1anio_kwh * 3
    ahorro_5anios_kwh = ahorro_1anio_kwh * 5

    ahorro_1anio_eur = int(ahorro_1anio_kwh * 0.75)
    ahorro_3anios_eur = ahorro_1anio_eur * 3
    ahorro_5anios_eur = ahorro_1anio_eur * 5

    co2_1anio_kg = int(ahorro_1anio_kwh * 0.9)
    co2_3anios_kg = co2_1anio_kg * 3
    co2_5anios_kg = co2_1anio_kg * 5

    # -----------------------------
    # 10. TEXTO FINAL PERSONALIZADO
    # -----------------------------
    nombre = data.nombre_comunidad or "la comunidad"
    municipio = data.municipio or ""
    provincia = data.provincia or ""
    ubicacion = f" de {municipio} ({provincia})" if municipio or provincia else ""

    recomendacion = (
        f"Para {nombre}{ubicacion}, la solución óptima recomendada se basa en un "
        f"mix energético formado por {pct_fv}% de fotovoltaica, {pct_aero}% de aerotermia, "
        f"{pct_geotermia}% de geotermia, {pct_biomasa}% de biomasa y {pct_micro}% de microhidráulica. "
        f"Este mix se adapta a la demanda real del edificio, su superficie disponible, la orientación del tejado "
        f"y las condiciones climáticas de la zona, maximizando el ahorro energético global y la reducción de emisiones."
    )

    # -----------------------------
    # 11. DEVOLVER RESULTADO
    # -----------------------------
    return RecomendacionSalida(
        recomendacion_final=recomendacion,
        mix_fotovoltaica_pct=pct_fv,
        mix_aerotermia_pct=pct_aero,
        mix_geotermia_pct=pct_geotermia,
        mix_biomasa_pct=pct_biomasa,
        mix_microhidraulica_pct=pct_micro,
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
@app.post("/subvenciones")
def estimar_subvenciones(data: Comunidad):

    # Factor climático como antes
    factor = {"A": 1.0, "B": 0.95, "C": 0.9, "D": 0.85, "E": 0.8}.get(
        (data.zona_climatica or "").upper(), 0.9
    )

    # Regla simple tipo demo
    eligible_nextgen = factor >= 0.9
    eligible_nacional = True
    eligible_regional = factor >= 0.85
    eligible_municipal = True if data.presupuesto and data.presupuesto < 500000 else False

    return {
        "subvenciones": {
            "eligible_nextgen": eligible_nextgen,
            "eligible_nacional": eligible_nacional,
            "eligible_regional": eligible_regional,
            "eligible_municipal": eligible_municipal,
        }
    }

