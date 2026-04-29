"""
Simulación - Barbería con Sistema de Turnos  [VERSIÓN DE PRUEBA]
Universidad Tecnológica Nacional - Facultad Regional Buenos Aires

F.D.P. definidas para prueba:
  - IA : Uniforme equiprobable entre 3 y 15 minutos
  - TA : Normal (Gauss) truncada entre 10 y 20 minutos
           media  = (10+20)/2 = 15 min
           desvío = (20-10)/6 ≈ 1.67 min  (regla 3-sigma)
"""

import random
import math


# =============================================================================
# SUBRUTINAS DE F.D.P.
# =============================================================================

def generar_IA() -> float:
    """
    Intervalo entre arribos.
    F.d.p.: UNIFORME equiprobable entre 3 y 15 minutos.
    """
    a = 3.0    # límite inferior (minutos)
    b = 15.0   # límite superior (minutos)
    return random.uniform(a, b)


def generar_TA() -> float:
    """
    Tiempo de atención.
    F.d.p.: NORMAL (Gauss) truncada entre 10 y 20 minutos.
      media  = 15 min
      desvío = (20-10)/6 ≈ 1.667 min  → 99.7% de valores en [10, 20]
    Se usa truncamiento: si el valor generado cae fuera del rango se vuelve
    a generar (método de rechazo), garantizando siempre un valor en [10, 20].
    """
    mu    = 15.0
    sigma = (20.0 - 10.0) / 6.0   # ≈ 1.667
    MIN_TA = 10.0
    MAX_TA = 20.0

    while True:
        valor = random.gauss(mu, sigma)
        if MIN_TA <= valor <= MAX_TA:
            return valor


# =============================================================================
# FUNCIÓN AUXILIAR: MenorTC
# =============================================================================

def menor_TC(TC: list) -> int:
    """
    Retorna el índice (base 0) del puesto con menor TC.
    Empate → menor índice (primer puesto).
    """
    idx_min = 0
    for j in range(1, len(TC)):
        if TC[j] < TC[idx_min]:
            idx_min = j
    return idx_min


# =============================================================================
# SIMULACIÓN PRINCIPAL
# =============================================================================

def simular(N: int, TF: float, verbose: bool = False) -> dict:
    """
    Ejecuta la simulación de la barbería.

    Parámetros
    ----------
    N       : cantidad de puestos de atención
    TF      : duración de la jornada en minutos
    verbose : imprime cada evento si True

    Retorna
    -------
    dict con PPS, PE, PTO, PE20 (listas por puesto) y CLL (clientes por puesto)
    """

    # --- Inicialización ---
    T    = 0.0
    TPLL = 0.0
    TC   = [0.0] * N

    CLL  = [0]   * N   # clientes llegados a cada puesto
    STO  = [0.0] * N   # suma de tiempos ociosos del servidor
    SPS  = [0.0] * N   # suma de permanencias en el sistema
    SE20 = [0]   * N   # clientes que esperaron > 20 min
    SE   = [0.0] * N   # suma de tiempos de espera en cola

    if verbose:
        header = f"{'T':>8} | {'Puesto':>6} | {'IA':>6} | {'TA':>6} | {'Espera':>7} | TC"
        print(header)
        print("-" * 70)

    # --- Bucle principal ---
    while True:

        T    = TPLL
        IA   = generar_IA()
        TPLL = T + IA

        ta_cliente = generar_TA()

        I = menor_TC(TC)

        # ¿El cliente esperará más de 20 minutos?
        espera = max(0.0, TC[I] - T)
        if espera > 20:
            SE20[I] += 1

        if TC[I] <= T:
            # Puesto libre → acumular ocio del servidor
            STO[I] += (T - TC[I])
            TC[I]   = T + ta_cliente
        else:
            # Puesto ocupado → cliente espera
            SE[I]  += espera
            TC[I]  += ta_cliente

        CLL[I] += 1
        SPS[I] += (TC[I] - T)   # permanencia = TC[I] - momento de llegada

        if verbose:
            print(
                f"{T:8.2f} | {I+1:>6} | {IA:6.2f} | {ta_cliente:6.2f} | "
                f"{espera:7.2f} | {[round(x,1) for x in TC]}"
            )

        if T >= TF:
            break

    # --- Cálculo de resultados ---
    PPS  = []
    PE   = []
    PTO  = []
    PE20 = []

    for i in range(N):
        if CLL[i] > 0:
            pps_i  = SPS[i]  / CLL[i]
            pto_i  = (STO[i] * 100.0) / TF
            pe20_i = (SE20[i] * 100.0) / CLL[i]
            pe_i   = SE[i]   / CLL[i]
        else:
            pps_i = pto_i = pe20_i = pe_i = 0.0

        PPS.append(round(pps_i,  2))
        PE.append( round(pe_i,   2))
        PTO.append(round(pto_i,  2))
        PE20.append(round(pe20_i,2))

    return {"PPS": PPS, "PE": PE, "PTO": PTO, "PE20": PE20, "CLL": CLL}


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":

    N_PUESTOS     = 1
    TF_SIMULACION = 20 * 60 - 9 * 60   # 660 minutos (9:00 a 20:00)
    VERBOSE       = False               # cambiar a True para ver evento a evento

    print("=" * 65)
    print("   SIMULACIÓN — BARBERÍA  [versión de prueba con FDPs definidas]")
    print("=" * 65)
    print(f"   Puestos (N)      : {N_PUESTOS}")
    print(f"   Duración (TF)    : {TF_SIMULACION} min  (9:00 a 20:00)")
    print(f"   IA               : Uniforme [3, 15] min")
    print(f"   TA               : Normal truncada  μ=15, σ≈1.67  en [10, 20] min")
    print("=" * 65)

    resultados = simular(N=N_PUESTOS, TF=TF_SIMULACION, verbose=VERBOSE)

    total_clientes = sum(resultados["CLL"])

    print("\nRESULTADOS POR PUESTO:")
    print(f"  {'Métrica':<35} ", end="")
    for i in range(N_PUESTOS):
        print(f"{'Puesto '+str(i+1):>12}", end="")
    print()
    print("  " + "-" * (35 + 12 * N_PUESTOS))

    filas = [
        ("Clientes atendidos",          "CLL",  ""),
        ("PPS – Prom. permanencia (min)","PPS",  " min"),
        ("PE  – Prom. espera cola (min)","PE",   " min"),
        ("PTO – % tiempo ocioso",        "PTO",  " %"),
        ("PE20 – % espera > 20 min",     "PE20", " %"),
    ]

    for label, key, unit in filas:
        print(f"  {label:<35} ", end="")
        for i in range(N_PUESTOS):
            val = resultados[key][i]
            print(f"{str(val)+unit:>12}", end="")
        print()

    print("\nRESULTADOS GLOBALES:")
    print(f"  Total clientes simulados   : {total_clientes}")

    # Promedios ponderados globales
    pps_global  = sum(resultados["PPS"][i]  * resultados["CLL"][i] for i in range(N_PUESTOS)) / max(total_clientes, 1)
    pe_global   = sum(resultados["PE"][i]   * resultados["CLL"][i] for i in range(N_PUESTOS)) / max(total_clientes, 1)
    pto_global  = sum(resultados["PTO"][i]                          for i in range(N_PUESTOS)) / N_PUESTOS
    pe20_global = sum(resultados["PE20"][i] * resultados["CLL"][i] for i in range(N_PUESTOS)) / max(total_clientes, 1)

    print(f"  PPS  global (ponderado)    : {pps_global:.2f} min")
    print(f"  PE   global (ponderado)    : {pe_global:.2f} min")
    print(f"  PTO  global (promedio)     : {pto_global:.2f} %")
    print(f"  PE20 global (ponderado)    : {pe20_global:.2f} %")
    print()