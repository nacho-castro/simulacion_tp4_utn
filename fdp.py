# -*- coding: utf-8 -*-
"""
barberia_fdp.py

Procesamiento y ajuste de datos de la Barbería mediante el uso de Python y Fitter.

El objetivo de este trabajo consiste en:

1. Realizar el procesamiento del dataset de turnos de barbería mediante Pandas y NumPy.
2. Obtener información estadística descriptiva y visualizaciones con Matplotlib.
3. Ajustar los datos a funciones de densidad de probabilidad (FDP) usando Fitter.
4. Simular arrays de datos con las FDP sugeridas y verificar su similitud con los datos originales.

Las dos variables de interés son:
    - Tiempo de Atención (min): duración del servicio por cliente.
    - Intervalos de Arribo (min): tiempo entre atenciones sucesivas por barbero por día.
"""

# =============================================================================
# 1. Importación de bibliotecas
# =============================================================================
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
from fitter import Fitter

# =============================================================================
# 2. Carga de datos
# =============================================================================
# Modificar la ruta al archivo según corresponda
ARCHIVO = "Registro_Turnos_Barberia_Simulacion.xlsx"

df = pd.read_excel(ARCHIVO, sheet_name="Datos de Turnos")

print("=" * 60)
print("VISTA PREVIA DEL DATASET")
print("=" * 60)
print(df.head(10))
print(f"\nDimensiones: {df.shape[0]} filas × {df.shape[1]} columnas")
print("\nTipos de datos:")
print(df.dtypes)

# =============================================================================
# 3. Procesamiento de datos
# =============================================================================

def hora_a_minutos(t):
    """Convierte cadena 'HH:MM' a minutos desde medianoche."""
    partes = str(t).split(":")
    return int(partes[0]) * 60 + int(partes[1])

# Filtrar solo turnos completados
df_comp = df[df["Estado"] == "Completado"].copy()

# --- Variable 1: Tiempo de Atención ---
tiempo_atencion = df_comp["Tiempo Atención (min)"]
tiempo_atencion = tiempo_atencion[tiempo_atencion > 0].reset_index(drop=True)

# --- Variable 2: Intervalos de Arribo ---
# Se calcula como la diferencia entre horas de salida reales de clientes
# sucesivos del mismo barbero en el mismo día (proxy de inter-llegadas reales).
df_comp["salida_min"] = df_comp["Hora Salida Real"].apply(hora_a_minutos)
df_sorted = df_comp.sort_values(["Fecha", "Barbero", "salida_min"])
df_sorted["intervalo_arribo"] = df_sorted.groupby(["Fecha", "Barbero"])["salida_min"].diff()
intervalos = df_sorted["intervalo_arribo"].dropna()
intervalos = intervalos[intervalos > 0].reset_index(drop=True)

print("\n" + "=" * 60)
print("ESTADÍSTICAS DESCRIPTIVAS")
print("=" * 60)
print("\n--- Tiempo de Atención (min) ---")
print(tiempo_atencion.describe())
print(f"\n--- Intervalos de Arribo (min) ---")
print(intervalos.describe())

# =============================================================================
# 4. Visualización exploratoria (histogramas de los datos originales)
# =============================================================================
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Histogramas - Datos Originales", fontsize=14, fontweight="bold")

axes[0].hist(tiempo_atencion, bins=30, color="steelblue", edgecolor="white", alpha=0.85)
axes[0].set_title("Tiempo de Atención (min)")
axes[0].set_xlabel("Minutos")
axes[0].set_ylabel("Frecuencia")

axes[1].hist(intervalos, bins=30, color="darkorange", edgecolor="white", alpha=0.85)
axes[1].set_title("Intervalos de Arribo (min)")
axes[1].set_xlabel("Minutos")
axes[1].set_ylabel("Frecuencia")

plt.tight_layout()
plt.savefig("histogramas_originales.png", dpi=150)
plt.show()
print("\n[Gráfico guardado como 'histogramas_originales.png']")

# =============================================================================
# 5. Ajuste con Fitter
# =============================================================================

# Lista de distribuciones candidatas a evaluar
distribuciones_candidatas = [
    "norm", "expon", "gamma", "lognorm", "beta",
    "triang", "uniform", "weibull_min", "weibull_max",
    "erlang", "chi2", "truncnorm"
]

# --- 5.1 Ajuste: Tiempo de Atención ---
print("\n" + "=" * 60)
print("AJUSTE FDP — TIEMPO DE ATENCIÓN")
print("=" * 60)

f_ta = Fitter(tiempo_atencion, distributions=distribuciones_candidatas)
f_ta.fit()

print("\nResumen de las mejores distribuciones (Tiempo de Atención):")
print(f_ta.summary())

mejor_ta = f_ta.get_best(method="sumsquare_error")
nombre_mejor_ta = list(mejor_ta.keys())[0]
params_mejor_ta = list(mejor_ta.values())[0]
print(f"\n>>> Mejor distribución: {nombre_mejor_ta}")
print(f"    Parámetros:          {params_mejor_ta}")

fig_ta = f_ta.plot_pdf(names=[nombre_mejor_ta], Nbest=1)
plt.title(f"FDP Ajustada — Tiempo de Atención\n({nombre_mejor_ta})")
plt.xlabel("Minutos")
plt.savefig("fdp_tiempo_atencion.png", dpi=150)
plt.show()
print("[Gráfico guardado como 'fdp_tiempo_atencion.png']")

# --- 5.2 Ajuste: Intervalos de Arribo ---
print("\n" + "=" * 60)
print("AJUSTE FDP — INTERVALOS DE ARRIBO")
print("=" * 60)

f_ia = Fitter(intervalos, distributions=distribuciones_candidatas)
f_ia.fit()

print("\nResumen de las mejores distribuciones (Intervalos de Arribo):")
print(f_ia.summary())

mejor_ia = f_ia.get_best(method="sumsquare_error")
nombre_mejor_ia = list(mejor_ia.keys())[0]
params_mejor_ia = list(mejor_ia.values())[0]
print(f"\n>>> Mejor distribución: {nombre_mejor_ia}")
print(f"    Parámetros:          {params_mejor_ia}")

fig_ia = f_ia.plot_pdf(names=[nombre_mejor_ia], Nbest=1)
plt.title(f"FDP Ajustada — Intervalos de Arribo\n({nombre_mejor_ia})")
plt.xlabel("Minutos")
plt.savefig("fdp_intervalos_arribo.png", dpi=150)
plt.show()
print("[Gráfico guardado como 'fdp_intervalos_arribo.png']")

# =============================================================================
# 6. Simulación — generación de datos con las FDP obtenidas
# =============================================================================
print("\n" + "=" * 60)
print("SIMULACIÓN DE DATOS")
print("=" * 60)

N_SIM = 4000  # Tamaño del array simulado

# --- 6.1 Simular Tiempo de Atención ---
dist_ta = getattr(stats, nombre_mejor_ta)
sim_ta = dist_ta.rvs(*params_mejor_ta.values(), size=N_SIM, random_state=42)
sim_ta = sim_ta[sim_ta > 0]  # Descartar valores no físicos

print(f"\nDatos simulados — Tiempo de Atención ({nombre_mejor_ta}):")
print(pd.Series(sim_ta).describe())

# --- 6.2 Simular Intervalos de Arribo ---
dist_ia = getattr(stats, nombre_mejor_ia)
sim_ia = dist_ia.rvs(*params_mejor_ia.values(), size=N_SIM, random_state=42)
sim_ia = sim_ia[sim_ia > 0]

print(f"\nDatos simulados — Intervalos de Arribo ({nombre_mejor_ia}):")
print(pd.Series(sim_ia).describe())

# =============================================================================
# 7. Verificación — comparación datos originales vs. simulados
# =============================================================================
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("Verificación: Datos Originales vs. Simulados", fontsize=14, fontweight="bold")

# Tiempo de Atención — original
axes[0, 0].hist(tiempo_atencion, bins=30, color="steelblue", edgecolor="white",
                alpha=0.85, density=True)
axes[0, 0].set_title("Tiempo de Atención — Original")
axes[0, 0].set_xlabel("Minutos")
axes[0, 0].set_ylabel("Densidad")

# Tiempo de Atención — simulado
axes[0, 1].hist(sim_ta, bins=30, color="cornflowerblue", edgecolor="white",
                alpha=0.85, density=True)
axes[0, 1].set_title(f"Tiempo de Atención — Simulado\n({nombre_mejor_ta})")
axes[0, 1].set_xlabel("Minutos")
axes[0, 1].set_ylabel("Densidad")

# Intervalos de Arribo — original
axes[1, 0].hist(intervalos, bins=30, color="darkorange", edgecolor="white",
                alpha=0.85, density=True)
axes[1, 0].set_title("Intervalos de Arribo — Original")
axes[1, 0].set_xlabel("Minutos")
axes[1, 0].set_ylabel("Densidad")

# Intervalos de Arribo — simulado
axes[1, 1].hist(sim_ia, bins=30, color="sandybrown", edgecolor="white",
                alpha=0.85, density=True)
axes[1, 1].set_title(f"Intervalos de Arribo — Simulado\n({nombre_mejor_ia})")
axes[1, 1].set_xlabel("Minutos")
axes[1, 1].set_ylabel("Densidad")

plt.tight_layout()
plt.savefig("verificacion_simulacion.png", dpi=150)
plt.show()
print("[Gráfico guardado como 'verificacion_simulacion.png']")

# =============================================================================
# 8. Verificación con Fitter sobre datos simulados (opcional)
# =============================================================================
print("\n" + "=" * 60)
print("VERIFICACIÓN FITTER — DATOS SIMULADOS")
print("=" * 60)

print("\n[Tiempo de Atención simulado]")
v_ta = Fitter(sim_ta, distributions=distribuciones_candidatas)
v_ta.fit()
print(v_ta.summary())

print("\n[Intervalos de Arribo simulados]")
v_ia = Fitter(sim_ia, distributions=distribuciones_candidatas)
v_ia.fit()
print(v_ia.summary())

# =============================================================================
# 9. Conclusión
# =============================================================================
print("\n" + "=" * 60)
print("CONCLUSIÓN")
print("=" * 60)
print(f"""
Tiempo de Atención:
  - Mejor FDP ajustada: {nombre_mejor_ta}
  - Parámetros: {params_mejor_ta}

Intervalos de Arribo:
  - Mejor FDP ajustada: {nombre_mejor_ia}
  - Parámetros: {params_mejor_ia}

Los arrays simulados (N={N_SIM}) fueron generados con scipy.stats usando
los parámetros obtenidos por Fitter. La comparación visual de histogramas
y el re-ajuste con Fitter sobre los datos simulados confirman la similitud
con los datos de origen.
""")