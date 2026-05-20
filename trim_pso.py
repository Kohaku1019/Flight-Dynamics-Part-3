import numpy as np
import math as mt
import op_corregido as op

# ==============================================================
# CÁLCULO DEL ESTADO DE TRIM MEDIANTE PSO
# ==============================================================

# ==============================================================
# DEFINICIÓN DE CONSTANTES DEL PROBLEMA
# ==============================================================

TARGET_SPEED = 78.0                         # Velocidad deseada para el trim [m/s]
TARGET_PSI = 45 * mt.pi / 180               # Rumbo deseado (45 grados en radianes)
TOLERANCE = 5e-6                            # Tolerancia numérica para convergencia

# ==============================================================
# DEFINICIÓN DE LOS LÍMITES DE BÚSQUEDA (RESTRICCIONES DURAS)
# ==============================================================

bounds = {
    "u": (60.0, 100.0),                      # Velocidad longitudinal en eje cuerpo [m/s]
    "w": (-20.0, 20.0),                      # Velocidad vertical en eje cuerpo [m/s]
    "theta": (-10*mt.pi/180, 15*mt.pi/180),  # Ángulo de pitch [rad]
    "delta_s": (-25*mt.pi/180, 10*mt.pi/180),# Deflexión del estabilizador [rad]
    "T": (0.01, 0.15)                        # Nivel de potencia (modelo adimensional)
}

# ==============================================================
# FUNCIÓN DE COSTO
# ==============================================================

def cost_function(z):
    """
    Vector de decisión:
    z = [u, w, theta, delta_s, T]

    Esta función:
    1. Construye el vector completo de estados X.
    2. Construye el vector completo de controles U.
    3. Evalúa la dinámica mediante xdot(X,U).
    4. Calcula el error cuadrático respecto al equilibrio dinámico.
    """

    u, w, theta, delta_s, T = z

    # Condiciones estrictas de vuelo recto y nivelado
    v = 0.0
    p = 0.0
    q = 0.0
    r = 0.0
    phi = 0.0
    psi = TARGET_PSI

    # Construcción del vector completo de estado
    X = [u, v, w, p, q, r, phi, theta, psi]

    # Controles (motores simétricos)
    delta_a = 0.0
    delta_r = 0.0
    U = [delta_a, delta_s, delta_r, T, T]

    # Evaluación del modelo dinámico
    X_dot = op.xdot(X, U)

    # Si el modelo retorna None (valores fuera de rango), penalización alta
    if X_dot is None:
        return 1e6

    du, dv, dw, dp, dq, dr, dphi, dtheta, dzhi = X_dot

    # Cálculo de la magnitud total de la velocidad
    V = mt.sqrt(u**2 + v**2 + w**2)

    # Función de costo:
    # Se minimizan simultáneamente las aceleraciones lineales,
    # aceleraciones angulares y el error en velocidad total.
    J = (
        du**2 +
        dv**2 +
        dw**2 +
        dp**2 +
        dq**2 +
        dr**2 +
        (V - TARGET_SPEED)**2+
        dphi**2+
        (dzhi - TARGET_PSI)**2
    )

    return J

# ==============================================================
# IMPLEMENTACIÓN DEL ALGORITMO PSO
# ==============================================================

def particle_swarm_optimization():

    # Parámetros del PSO
    num_particles = 40        # Número de partículas en el enjambre
    max_iterations = 200      # Número máximo de iteraciones
    w_inertia = 0.7           # Peso de inercia
    c1 = 1.7                  # Coeficiente cognitivo
    c2 = 1.7                  # Coeficiente social

    dim = 5                   # Dimensión del espacio de búsqueda

    # Inicialización de partículas y velocidades
    particles = np.zeros((num_particles, dim))
    velocities = np.zeros((num_particles, dim))

    keys = list(bounds.keys())

    # Inicialización aleatoria dentro de los límites físicos
    for i in range(num_particles):
        for j in range(dim):
            low, high = bounds[keys[j]]
            particles[i, j] = np.random.uniform(low, high)
            velocities[i, j] = np.random.uniform(-(high-low), (high-low)) * 0.1

    # Inicialización de mejores posiciones individuales
    pbest = particles.copy()
    pbest_cost = np.array([cost_function(p) for p in particles])

    # Inicialización del mejor global
    gbest_index = np.argmin(pbest_cost)
    gbest = pbest[gbest_index].copy()
    gbest_cost = pbest_cost[gbest_index]

    # Bucle principal del PSO
    for iteration in range(max_iterations):

        for i in range(num_particles):

            r1 = np.random.rand(dim)
            r2 = np.random.rand(dim)

            # Actualización de velocidad según ecuación clásica del PSO
            velocities[i] = (
                w_inertia * velocities[i]
                + c1 * r1 * (pbest[i] - particles[i])
                + c2 * r2 * (gbest - particles[i])
            )

            # Actualización de posición
            particles[i] += velocities[i]

            # Aplicación de límites físicos (restricciones duras)
            for j in range(dim):
                low, high = bounds[keys[j]]
                if particles[i, j] < low:
                    particles[i, j] = low
                elif particles[i, j] > high:
                    particles[i, j] = high

            # Evaluación del costo
            cost = cost_function(particles[i])

            # Actualización del mejor individual
            if cost < pbest_cost[i]:
                pbest[i] = particles[i].copy()
                pbest_cost[i] = cost

                # Actualización del mejor global
                if cost < gbest_cost:
                    gbest = particles[i].copy()
                    gbest_cost = cost

        #print(f"Iteración {iteration+1} | Mejor costo actual: {gbest_cost}")

        # Criterio de parada por tolerancia
        if gbest_cost < TOLERANCE:
            print("Convergencia alcanzada.")
            break

    return gbest, gbest_cost

# ==============================================================
# EJECUCIÓN PRINCIPAL
# ==============================================================

def result_optimization():
    
    trim_state, final_cost = particle_swarm_optimization()
    J = cost_function([trim_state[0],trim_state[1],trim_state[2],trim_state[3],trim_state[4]])
    print("\n========== RESULTADO DE TRIM ==========")
    print(f"la funcion de costo obtenida es j = du**2 + dv**2 + dw**2 + dp**2 + dq**2 + dr**2 + (V - TARGET_SPEED)**2+ dphi**2+ (dzhi - TARGET_PSI)**2")
    print(f"u       = {trim_state[0]} m/s")
    print(f"w       = {trim_state[1]} m/s")
    print(f"theta   = {trim_state[2]} rad")
    print(f"delta_s = {trim_state[3]} rad")
    print(f"Throttle= {trim_state[4]}")
    print(f"Costo final = {final_cost}")