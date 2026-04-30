"""
Simulación - Barbería con Sistema de Turnos
Universidad Tecnológica Nacional - Facultad Regional Buenos Aires

Consigna:
- Barbería con N puestos de atención
- Horario: Lunes a Sábado, 9:00 a 20:00 (660 minutos)
- Turnos de 1 hora de duración
- Los clientes se ubican en la cola del puesto con menor TC; empates → puesto 1 (menor índice)
- IA: intervalo entre arribos con f.d.p. uniforme (PENDIENTE parámetros)
- TA[i]: tiempo de atención según tipo de corte (PENDIENTE f.d.p. y rangos)
- Todos los clientes esperan el tiempo necesario
- Costo del corte: ARS $13.000

Resultados:
  1. PPS  - Promedio de permanencia en el sistema
  2. PE   - Promedio de espera en cola por puesto
  3. PTO  - Porcentaje de tiempo ocioso por puesto
  4. PE20 - Porcentaje de personas que esperaron más de 20 minutos
"""

import random


# =============================================================================
# SUBRUTINAS DE F.D.P.  (INCOMPLETAS — completar cuando se definan los datos)
# =============================================================================

def generar_IA() -> float:
    """
    Genera el intervalo entre arribos (minutos).
    F.d.p.: LOGNORMAL — ajustada con los datos reales.
    Parámetros: s=0.4696, loc=21.6551, scale=39.6709
    """
    import math
    s     = 0.4695894952283533
    loc   = 21.655105619120544
    scale = 39.67092802604982

    # Lognormal: loc + scale * e^(s * Z),  donde Z ~ N(0,1)
    Z = random.gauss(0, 1)
    return loc + scale * math.exp(s * Z)


def generar_TA() -> float:
    """
    Genera el tiempo de atención (minutos).
    F.d.p.: UNIFORME — ajustada con los datos reales.
    Parámetros: loc=30.0, scale=30.0  →  U(30, 60)
    """
    loc   = 30.0
    scale = 30.0
    return random.uniform(loc, loc + scale)

# =============================================================================
# FUNCIÓN AUXILIAR: MenorTC
# Devuelve el índice del puesto con menor TC.
# En caso de empate se elige el de menor índice (el primero encontrado).
# =============================================================================

def menor_TC(TC: list) -> int:
    """
    Recorre el vector TC y retorna el índice (base 0) del puesto con menor
    tiempo comprometido. En caso de empate se queda con el primer puesto
    (menor índice), replicando el comportamiento del diagrama de flujo.
    """
    idx_min = 0
    for j in range(1, len(TC)):
        if TC[j] < TC[idx_min]:
            idx_min = j
    return idx_min


# =============================================================================
# SIMULACIÓN PRINCIPAL  (sigue exactamente el diagrama de flujo)
# =============================================================================

def simular(N: int, TF: float, verbose: bool = False):
    """
    Ejecuta la simulación de la barbería.

    Parámetros
    ----------
    N       : cantidad de puestos de atención (variable de control)
    TF      : tiempo final de la simulación en minutos
              (ej. 660 para una jornada de 9:00 a 20:00)
    verbose : si True imprime el estado en cada arribo

    Retorna
    -------
    dict con los resultados:
        PPS   – promedio de permanencia en el sistema (minutos)
        PE    – lista con el promedio de espera en cola por puesto (minutos)
        PTO   – lista con el % de tiempo ocioso por puesto
        PE20  – % de clientes que esperaron más de 20 minutos
    """

    # ------------------------------------------------------------------
    # INICIALIZACIÓN  (bloque superior del diagrama)
    # T=0 ; TPLL=0 ; TC=0 ; TF=dato
    # ------------------------------------------------------------------
    T    = 0.0                  # Tiempo actual de simulación
    TPLL = 0.0                  # Tiempo de la próxima llegada
    TC   = [0.0] * N            # Tiempo comprometido de cada puesto (vector)

    # Acumuladores de resultados
    CLL   = [0]   * N            # Número total de clientes atendidos por puesto
    STO  = [0.0] * N            # Suma de tiempos de espera > 0 (tiempo ocioso opuesto)
    SPS  = [0.0] * N            # Suma de permanencias en el sistema por puesto
    SE20 = [0]   * N            # Cantidad de clientes que esperaron > 20 min por puesto
    SE   = [0.0] * N            # Suma de tiempos de espera en cola por puesto (para PE)

    # ------------------------------------------------------------------
    # BUCLE PRINCIPAL  (flecha que vuelve al inicio: T = TPLL)
    # ------------------------------------------------------------------
    while True:

        # --- Avanzar al próximo arribo ---
        T = TPLL

        # --- Generar intervalo entre arribos y actualizar TPLL ---
        IA   = generar_IA()
        TPLL = T + IA

        # --- Generar tiempo de atención del cliente que acaba de llegar ---
        ta_cliente = generar_TA()   # TA(I) para el cliente actual

        # --- Determinar a qué puesto va el cliente (I = MenorTC) ---
        I = menor_TC(TC)

        # --- Evaluación del puesto elegido ---
        if TC[I] - T > 20:
            # El cliente tendrá que esperar más de 20 minutos
            SE20[I] += 1

        if TC[I] <= T:
            # El puesto estaba libre: acumular tiempo ocioso del servidor
            STO[I] += (T - TC[I])
            # Actualizar TC: el cliente entra de inmediato
            TC[I] = T + ta_cliente
        else:
            # El puesto estaba ocupado: el cliente espera
            # TC se extiende con el tiempo de atención del nuevo cliente
            TC[I] = TC[I] + ta_cliente
            # Acumular tiempo de espera en cola
            SE[I] += TC[I] - T  

        # --- Acumuladores por puesto ---
        CLL[I]  += 1
        SPS[I] += (TC[I] - T)        # Permanencia = tiempo que TC queda adelante de T

        # --- Impresión del estado (si verbose=True) ---
        if verbose:
            estado_puesto = "LIBRE " if TC[I] - ta_cliente <= T else "OCUPADO"
            espera_mostrar = max(0.0, (TC[I] - ta_cliente) - T) if TC[I] - ta_cliente > T else 0.0
            print(
                f"T={T:7.2f} | Arribo → Puesto {I+1} ({estado_puesto}) | "
                f"Espera={espera_mostrar:5.1f} min | TA={ta_cliente:.2f} min | "
                f"TC={[round(x,1) for x in TC]}"
            )

        # --- Condición de fin: ¿T >= TF? ---
        if T >= TF:
            break

    # ------------------------------------------------------------------
    # CÁLCULO DE RESULTADOS FINALES
    # ------------------------------------------------------------------
    PPS  = []
    PE   = []
    PTO  = []
    PE20 = []

    for i in range(N):
        if CLL[i] > 0:
            pps_i  = SPS[i] / CLL[i]
            pto_i  = (STO[i] * 100) / TF
            pe20_i = (SE20[i] * 100) / CLL[i]
            pe_i   = SE[i] / CLL[i]
        else:
            pps_i = pto_i = pe20_i = pe_i = 0.0

        PPS.append(round(pps_i,  2))
        PE.append( round(pe_i,   2))
        PTO.append(round(pto_i,  2))
        PE20.append(round(pe20_i,2))

    return {
        "PPS":  PPS,
        "PE":   PE,
        "PTO":  PTO,
        "PE20": PE20,
        "CLL":   CLL,
    }


# =============================================================================
# PUNTO DE ENTRADA
# =============================================================================

if __name__ == "__main__":

    N_PUESTOS     = 2
    TF_SIMULACION = 20 * 60 - 9 * 60   # 660 minutos (9:00 a 20:00)
    VERBOSE       = False

    # Parámetros reales de las FDP (para mostrar en el header)
    IA_DIST  = "Lognormal"
    IA_PARAM = "s=0.4696, loc=21.66, scale=39.67"
    TA_DIST  = "Uniforme"
    TA_PARAM = "U(30, 60) min"

    print("=" * 65)
    print("   SIMULACIÓN — BARBERÍA - TP N4")
    print("=" * 65)
    print(f"   Puestos (N)      : {N_PUESTOS}")
    print(f"   Duración (TF)    : {TF_SIMULACION} min  (9:00 a 20:00)")
    print(f"   IA               : {IA_DIST}  ({IA_PARAM})")
    print(f"   TA               : {TA_DIST}  ({TA_PARAM})")
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
        ("Clientes atendidos",           "CLL",  ""),
        ("PPS – Prom. permanencia (min)", "PPS",  " min"),
        ("PE  – Prom. espera cola (min)", "PE",   " min"),
        ("PTO – % tiempo ocioso",         "PTO",  " %"),
        ("PE20 – % espera > 20 min",      "PE20", " %"),
    ]

    for label, key, unit in filas:
        print(f"  {label:<35} ", end="")
        for i in range(N_PUESTOS):
            val = resultados[key][i]
            print(f"{str(val)+unit:>12}", end="")
        print()

    print("\nRESULTADOS GLOBALES:")
    print(f"  Total clientes simulados   : {total_clientes}")

    pps_global  = sum(resultados["PPS"][i]  * resultados["CLL"][i] for i in range(N_PUESTOS)) / max(total_clientes, 1)
    pe_global   = sum(resultados["PE"][i]   * resultados["CLL"][i] for i in range(N_PUESTOS)) / max(total_clientes, 1)
    pto_global  = sum(resultados["PTO"][i]                          for i in range(N_PUESTOS)) / N_PUESTOS
    pe20_global = sum(resultados["PE20"][i] * resultados["CLL"][i] for i in range(N_PUESTOS)) / max(total_clientes, 1)

    print(f"  PPS  global (ponderado)    : {pps_global:.2f} min")
    print(f"  PE   global (ponderado)    : {pe_global:.2f} min")
    print(f"  PTO  global (promedio)     : {pto_global:.2f} %")
    print(f"  PE20 global (ponderado)    : {pe20_global:.2f} %")
    print()