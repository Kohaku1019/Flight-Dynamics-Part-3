import op_corregido as op
import numpy as np
import trim_pso as tri
import animador as gr

# =========================================================
# MÉTODO RK4
# =========================================================
def rk4_step(X, U, dt):
    k1 = np.array(op.xdot(X, U))

    k2 = np.array(op.xdot(
        X + 0.5 * dt * k1,
        U
    ))

    k3 = np.array(op.xdot(
        X + 0.5 * dt * k2,
        U
    ))

    k4 = np.array(op.xdot(
        X + dt * k3,
        U
    ))

    return X + (dt / 6.0) * (k1 + 2*k2 + 2*k3 + k4)


print ("Bienvenido ingeniero al programa de simulacion de vuelo")
print("Cual caso desea experimentar")
print("1. Vuelo recto y nivelado")
print("2. Perturbacion de aleron")
print("3. Falla de motor")
print("4. Uso del modelo de optimizacion PSO")

opcion = int(input("Digite el numero del caso que desea probar >> "))

if opcion == 1:

    print("\nCASO 1")

    X0 = np.array([85, 0, 0, 0, 0, 0, 0, 0.1, 0], dtype=float)
    U0 = [0, -0.1, 0, 0.08, 0.08]

    t = 0
    dt = 0.3

    x0 = []
    X0_csv = []

    X0_csv.append([
        t, U0[0], U0[1], U0[2], U0[3], U0[4],
        X0[0], X0[1], X0[2], X0[3], X0[4],
        X0[5], X0[6], X0[7], X0[8]
    ])

    x0.append([
        t, X0[0], X0[1], X0[2], X0[3],
        X0[4], X0[5], X0[6], X0[7], X0[8]
    ])

    while t <= 180:

        X0 = rk4_step(X0, U0, dt)

        t += dt

        x0.append([
            t, X0[0], X0[1], X0[2], X0[3],
            X0[4], X0[5], X0[6], X0[7], X0[8]
        ])

        X0_csv.append([
            t, U0[0], U0[1], U0[2], U0[3], U0[4],
            X0[0], X0[1], X0[2], X0[3], X0[4],
            X0[5], X0[6], X0[7], X0[8]
        ])

    op.guardar_csv(X0_csv, "RCAM.csv")
    gr.grafica()

    print("Simulacion terminada")

elif opcion == 2:

    print("\nCASO 2")

    X0 = np.array([85, 0, 0, 0, 0, 0, 0, 0.1, 0], dtype=float)
    U0 = [0, -0.1, 0, 0.08, 0.08]

    t = 0
    dt = 0.3

    x0 = []
    X0_csv = []

    x0.append([
        t, X0[0], X0[1], X0[2], X0[3],
        X0[4], X0[5], X0[6], X0[7], X0[8]
    ])

    X0_csv.append([
        t, U0[0], U0[1], U0[2], U0[3], U0[4],
        X0[0], X0[1], X0[2], X0[3], X0[4],
        X0[5], X0[6], X0[7], X0[8]
    ])

    while t <= 180:

        if t >= 30 and t <= 32:
            U0 = [(5*np.pi/180), -0.1, 0, 0.08, 0.08]
        else:
            U0 = [0, -0.1, 0, 0.08, 0.08]

        X0 = rk4_step(X0, U0, dt)

        t += dt

        x0.append([
            t, X0[0], X0[1], X0[2], X0[3],
            X0[4], X0[5], X0[6], X0[7], X0[8]
        ])

        X0_csv.append([
            t, U0[0], U0[1], U0[2], U0[3], U0[4],
            X0[0], X0[1], X0[2], X0[3], X0[4],
            X0[5], X0[6], X0[7], X0[8]
        ])

    op.guardar_csv(X0_csv, "RCAM.csv")
    gr.grafica()

    print("Simulacion terminada")

elif opcion == 3:

    print ("\nCASO 3")

    X0 = np.array([85, 0, 0, 0, 0, 0, 0, 0.1, 0], dtype=float)

    t = 0
    dt = 0.3

    x0 = []
    X0_csv = []

    x0.append([
        t, X0[0], X0[1], X0[2], X0[3],
        X0[4], X0[5], X0[6], X0[7], X0[8]
    ])

    eleccion = int(input(
        "\nQue motor desea fallar\n1. motor izquierdo\n2. motor derecho\n >>>    "
    ))

    if eleccion == 1:

        U0 = [0, -0.1, 0, 0, 0.08]

        X0_csv.append([
            t, U0[0], U0[1], U0[2], U0[3], U0[4],
            X0[0], X0[1], X0[2], X0[3], X0[4],
            X0[5], X0[6], X0[7], X0[8]
        ])

        while t <= 180:

            X0 = rk4_step(X0, U0, dt)

            t += dt

            x0.append([
                t, X0[0], X0[1], X0[2], X0[3],
                X0[4], X0[5], X0[6], X0[7], X0[8]
            ])

            X0_csv.append([
                t, U0[0], U0[1], U0[2], U0[3], U0[4],
                X0[0], X0[1], X0[2], X0[3], X0[4],
                X0[5], X0[6], X0[7], X0[8]
            ])

        op.guardar_csv(X0_csv, "RCAM.csv")
        gr.grafica()

    elif eleccion == 2:

        U0 = [0, -0.1, 0, 0.08, 0]

        while t <= 180:

            X0 = rk4_step(X0, U0, dt)

            t += dt

            x0.append([
                t, X0[0], X0[1], X0[2], X0[3],
                X0[4], X0[5], X0[6], X0[7], X0[8]
            ])

            X0_csv.append([
                t, U0[0], U0[1], U0[2], U0[3], U0[4],
                X0[0], X0[1], X0[2], X0[3], X0[4],
                X0[5], X0[6], X0[7], X0[8]
            ])

        op.guardar_csv(X0_csv, "RCAM.csv")
        gr.grafica()

        print("Simulacion terminada")

    else:
        print("opcion incorrecta, vuelva a intentarlo")

elif opcion == 4:

    tri.result_optimization()

else:

    print("Elija una de las opciones indicadas")