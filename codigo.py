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
    F.d.p.: UNIFORME — parámetros pendientes.

    TODO: reemplazar los valores de a y b con los parámetros reales.
    """
    a = None   # límite inferior (minutos)  ← PENDIENTE
    b = None   # límite superior (minutos)  ← PENDIENTE

    if a is None or b is None:
        raise NotImplementedError(
            "generar_IA(): los parámetros a y b de la distribución uniforme "
            "aún no han sido definidos."
        )

    return random.uniform(a, b)


def generar_TA() -> float:
    """
    Genera el tiempo de atención (minutos) según el tipo de servicio
    (Corte / Barba / Corte y Barba).
    F.d.p.: PENDIENTE — se conoce al momento de la reserva.

    TODO: implementar la lógica de selección del tipo de servicio
          y la distribución correspondiente para cada uno.
          Rango conocido: 60 a X minutos (X pendiente).
    """
    raise NotImplementedError(
        "generar_TA(): la f.d.p. del tiempo de atención aún no ha sido definida."
    )


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

        if verbose:
            print(
                f"T={T:7.2f} | Arribo → Puesto {I+1} | "
                f"TC={[round(x,1) for x in TC]} | IA={IA:.2f} | TA={ta_cliente:.2f}"
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

    # --- Parámetros de la simulación ---
    N_PUESTOS     = 2          # Variable de control: cantidad de puestos
    APERTURA      = 9 * 60     # 9:00  → minuto 540 (referencia interna)
    CIERRE        = 20 * 60    # 20:00 → minuto 1200
    TF_SIMULACION = CIERRE - APERTURA  # 660 minutos de jornada

    print("=" * 60)
    print("   SIMULACIÓN — BARBERÍA CON SISTEMA DE TURNOS")
    print("=" * 60)
    print(f"   Puestos (N)  : {N_PUESTOS}")
    print(f"   Duración (TF): {TF_SIMULACION} minutos")
    print("=" * 60)

    try:
        resultados = simular(N=N_PUESTOS, TF=TF_SIMULACION, verbose=False)

        print("\nRESULTADOS POR PUESTO:")
        for i in range(N_PUESTOS):
            print(f"\n  Puesto {i+1}:")
            print(f"    Clientes atendidos        : {resultados['CLL'][i]}")
            print(f"    PPS  – Prom. permanencia  : {resultados['PPS'][i]:.2f} min")
            print(f"    PE   – Prom. espera cola  : {resultados['PE'][i]:.2f} min")
            print(f"    PTO  – % tiempo ocioso    : {resultados['PTO'][i]:.2f} %")
            print(f"    PE20 – % espera > 20 min  : {resultados['PE20'][i]:.2f} %")

    except NotImplementedError as e:
        print(f"\n[PENDIENTE] {e}")
        print("\nEl código está estructurado correctamente.")
        print("Completar las funciones generar_IA() y generar_TA() para ejecutar.")