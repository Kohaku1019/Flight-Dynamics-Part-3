import math as mt
import numpy as np
import csv

def xdot(X, U):

    # =========================
    # STATE VARIABLES
    # =========================

    x1 = X[0]   # u
    x2 = X[1]   # v
    x3 = X[2]   # w
    x4 = X[3]   # p
    x5 = X[4]   # q
    x6 = X[5]   # r
    x7 = X[6]   # phi
    x8 = X[7]   # theta
    x9 = X[8]   # psi

    # =========================
    # CONTROL VARIABLES
    # =========================

    u1 = float(U[0])   # aileron
    u2 = float(U[1])   # stabilizer
    u3 = float(U[2])   # rudder
    u4 = float(U[3])   # throttle 1
    u5 = float(U[4])   # throttle 2

    # =========================
    # STEP 1 - CONTROL LIMITS
    # =========================

    if not (-25 * mt.pi/180 <= u1 <= 25 * mt.pi/180):
        print("u1 fuera de limites")
        return

    if not (-25 * mt.pi/180 <= u2 <= 10 * mt.pi/180):
        print("u2 fuera de limites")
        return

    if not (-30 * mt.pi/180 <= u3 <= 30 * mt.pi/180):
        print("u3 fuera de limites")
        return

    # throttle normalizado
    if not (0 <= u4 <= 1):
        print("u4 fuera de limites")
        return

    if not (0 <= u5 <= 1):
        print("u5 fuera de limites")
        return

    # =========================
    # STEP 2 - INTERMEDIATE VARIABLES
    # =========================

    V = mt.sqrt(x1**2 + x2**2 + x3**2)

    # protección numérica
    if V < 0.01:
        V = 0.01

    alpha = mt.atan2(x3, x1)

    beta_argument = np.clip(x2 / V, -1.0, 1.0)
    beta = mt.asin(beta_argument)

    rho = 1.225
    Q = 0.5 * rho * V**2

    # =========================
    # GEOMETRY
    # =========================

    lt = 24.8
    b = 44.8
    s = 260
    st = 64
    c_mac = 6.6

    # =========================
    # STEP 3 - AERODYNAMIC COEFFICIENTS
    # =========================

    n = 5.5
    alpha_zero = -11.5 * mt.pi / 180

    a0 = 15.212
    a1 = -155.2
    a2 = 609.2
    a3 = -768.5

    # Wing lift
    if alpha <= 14.5 * mt.pi / 180:
        Clw = n * (alpha - alpha_zero)
    else:
        Clw = a3*alpha**3 + a2*alpha**2 + a1*alpha + a0

    # Tail lift
    epsilon = 0.25 * (alpha - alpha_zero)

    alpha_tail = alpha - epsilon + u2 + (1.3 * x5 * lt / V)

    Clt = 3.1 * (st / s) * alpha_tail

    # Total lift
    CL = Clw + Clt

    # Drag
    CD = 0.13 + 0.07 * ((5.5 * alpha + 0.654)**2)

    # Side force
    CY = -1.6 * beta + 0.24 * u3

    # =========================
    # ROTATION Fs -> Fw
    # =========================

    Cw_from_s = np.array([
        [np.cos(beta),  np.sin(beta), 0],
        [-np.sin(beta), np.cos(beta), 0],
        [0,             0,            1]
    ])

    CFs = np.array([
        [-CD],
        [CY],
        [-CL]
    ])

    CFw = Cw_from_s @ CFs

    # =========================
    # STEP 4 - AERODYNAMIC FORCE IN Fb
    # =========================

    Cb_from_s = np.array([
        [np.cos(alpha), 0, -np.sin(alpha)],
        [0,             1, 0],
        [np.sin(alpha), 0, np.cos(alpha)]
    ])

    FAs = np.array([
        [-CD * Q * s],
        [CY * Q * s],
        [-CL * Q * s]
    ])

    FAb = Cb_from_s @ FAs

    # =========================
    # STEP 5 - MOMENT COEFFICIENTS
    # =========================

    n_vec = np.array([
        [-1.4 * beta],
        [-0.59 - (3.1 * ((st * lt) / (s * c_mac)) * (alpha - epsilon))],
        [(1 - alpha * (180 / (15 * mt.pi))) * beta]
    ])

    Cm_vs_x = np.array([
        [-11, 0, 5],
        [0, -4.03 * ((st * lt**2)/(s * c_mac**2)), 0],
        [1.7, 0, -11.5 * beta]
    ]) * (c_mac / V)

    wb_eb = np.array([
        [x4],
        [x5],
        [x6]
    ])

    Cm_vs_u = np.array([
        [-0.6, 0, 0.22],
        [0, -3.1 * ((st * lt)/(s * c_mac)), 0],
        [0, 0, -0.63]
    ])

    Sc = np.array([
        [u1],
        [u2],
        [u3]
    ])

    Cm_ac = n_vec + (Cm_vs_x @ wb_eb) + (Cm_vs_u @ Sc)

    # =========================
    # STEP 6 - MOMENT ABOUT AC
    # =========================

    Mac_b = Cm_ac * (Q * s * c_mac)

    # =========================
    # STEP 7 - MOMENT ABOUT CG
    # =========================

    rcg = np.array([
        [0.23 * c_mac],
        [0],
        [0.1 * c_mac]
    ])

    rac = np.array([
        [0.12 * c_mac],
        [0],
        [0]
    ])

    r = rcg - rac

    cross_product = np.cross(
        r.flatten(),
        FAb.flatten()
    ).reshape(3,1)

    Macg_b = Mac_b + cross_product

    # =========================
    # STEP 8 - PROPULSION
    # =========================

    m = 120000 * 0.453592
    g = 9.81

    Fe1 = np.array([
        [u4 * m * g],
        [0],
        [0]
    ])

    Fe2 = np.array([
        [u5 * m * g],
        [0],
        [0]
    ])

    Fe_tot = Fe1 + Fe2

    # Engine 1 position
    u1b = np.array([
        [(0.23 * c_mac)],
        [7.94],
        [(0.1 * c_mac) - 1.9]
    ])

    Me1cg = np.cross(
        u1b.flatten(),
        Fe1.flatten()
    ).reshape(3,1)

    # Engine 2 position
    u2b = np.array([
        [(0.23 * c_mac)],
        [-7.94],
        [(0.1 * c_mac) - 1.9]
    ])

    Me2cg = np.cross(
        u2b.flatten(),
        Fe2.flatten()
    ).reshape(3,1)

    Mecg_tot = Me1cg + Me2cg

    # =========================
    # STEP 9 - GRAVITY
    # =========================

    Fgb = np.array([
        [-g * np.sin(x8)],
        [g * np.cos(x8) * np.sin(x7)],
        [g * np.cos(x8) * np.cos(x7)]
    ]) * m

    # =========================
    # STEP 10 - EXPLICIT FIRST ORDER
    # =========================

    # RCAM inertia matrix
    Ib = np.array([
        [40.07, 0, -2.0923],
        [0, 64, 0],
        [-2.0923, 0, 99.92]
    ]) * 120000

    Fb = Fgb + FAb + Fe_tot

    v = np.array([
        [x1],
        [x2],
        [x3]
    ])

    gyro_force = np.cross(
        wb_eb.flatten(),
        v.flatten()
    ).reshape(3,1)

    V_dot = (1/m) * Fb - gyro_force

    Mcg = Mecg_tot + Macg_b

    angular_momentum = Ib @ wb_eb

    gyro_moment = np.cross(
        wb_eb.flatten(),
        angular_momentum.flatten()
    ).reshape(3,1)

    turn_rate_dot = np.linalg.inv(Ib) @ (Mcg - gyro_moment)

    # =========================
    # EULER KINEMATICS
    # =========================

    # protección singularidad theta = 90°
    if abs(np.cos(x8)) < 1e-6:
        x8 += 1e-6

    C_euler_Angles = np.array([
        [1, np.sin(x7)*np.tan(x8),  np.cos(x7)*np.tan(x8)],
        [0, np.cos(x7),            -np.sin(x7)],
        [0, np.sin(x7)/np.cos(x8), np.cos(x7)/np.cos(x8)]
    ])

    euler_dot = C_euler_Angles @ wb_eb

    # =========================
    # OUTPUT
    # =========================

    X_dot = np.array([
        V_dot[0,0],
        V_dot[1,0],
        V_dot[2,0],
        turn_rate_dot[0,0],
        turn_rate_dot[1,0],
        turn_rate_dot[2,0],
        euler_dot[0,0],
        euler_dot[1,0],
        euler_dot[2,0]
    ])

    return X_dot


# ==========================================
# SAVE CSV
# ==========================================

def guardar_csv(X0_csv, nombre_archivo="RCAM.csv"):

    with open(nombre_archivo, mode='w', newline='') as archivo:

        writer = csv.writer(archivo)

        writer.writerow([
            "time",
            "u",
            "v",
            "w",
            "p",
            "q",
            "r",
            "phi",
            "theta",
            "psi"
        ])

        for fila in X0_csv:
            writer.writerow(fila)

    print(f"Archivo guardado como: {nombre_archivo}")