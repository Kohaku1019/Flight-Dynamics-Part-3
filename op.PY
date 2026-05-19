import math as mt
import numpy as np
import csv
def xdot(X,U):
    # State and Control vector
    x1 = X[0] # u
    x2 = X[1] # v
    x3 = X[2] # w
    x4 = X[3] # p
    x5 = X[4] # q
    x6 = X[5] # r
    x7 = X[6] # phi
    x8 = X[7] # theta
    x9 = X[8] # psi
    
    u1 = float(U[0]) # aileron
    u2 = float(U[1]) # stabilizer
    u3 = float(U[2]) # rudder
    u4 = float(U[3]) # throttle 1
    u5 = float(U[4]) # throttle 2


    # paso 1: limites de control / saturacion
    if not ((-25)*mt.pi / 180) <= u1 <= (25 * mt.pi / 180):
        print ("u1 fuera de limites")
        return
    if not((-25)*mt.pi / 180) <= u2 <= (10 * mt.pi / 180):
        print ("u2 fuera de limites")
        return
    if not((-30)*mt.pi / 180) <= u3 <= (30 * mt.pi / 180):
        print ("u3 fuera de limites")
        return
    if not(0.5 * mt.pi / 180) <= u4 <= (10 * mt.pi / 180):
        print ("u4 fuera de limites")
        return
    if not (0.5  * mt.pi / 180) <= u5 <= (10 * mt.pi / 180):
        print ("u5 fuera de limites")
        return
        
    
    # paso 2: variables intermedias
    V = mt.sqrt((x1**2)+(x2**2)+(x3**2))
    alpha = mt.atan2(x3,x1)
    betha = mt.asin (x2/V)
    Q = 1.225*0.5*(V**2)
    
    # paso 3: coeficientes aerodinamicos adimensionales en la superficie
    # primer coeficiente CL
    # datos para el calculo del coeficiente de lift del ala
    n = 5.5
    alpha_zero = float(-11.5 * mt.pi /180)
    a0 = 15.212
    a1 = -155.2
    a2 = 609.2
    a3 = -768.5
    if alpha <= (14.5* mt.pi / 180):
        Clw = n * (alpha - alpha_zero)
    else:
        Clw = (a3 * (alpha**3)) + (a2 * (alpha**2)) + (a1 * alpha) + a0
    # datos geometricos del ala
    lt = float(24.8)
    b = 44.8
    s = int(260)
    st = int(64)
    c_mac = 6.6
    # datos para calculos de coeficiente de lift de la cola
    etha = 0.25 * (alpha - alpha_zero)
    alpha_tail = alpha - etha + u2 + (1.3 * x5 * lt / V)   
    Clt = 3.1 * (st / s) * alpha_tail
    CL = Clw + Clt 
    # segundo coeficiente CD
    CD = 0.13 + 0.07 * (((5.5 * alpha) + 0.654)**2)
    # tercer coeficiente Cy
    CY = (-16 * betha) + (0.24 * u3)
    # matriz de transformacion de datos de superficie a datos del viento
    Cw_from_s = np.array([
            [np.cos(betha),  np.sin(betha), 0],
            [-np.sin(betha), np.cos(betha), 0],
            [0,              0,             1]
        ])
    # matriz de coeficientes aerodinamicos en la superficie?
    CFs = np.array([
            [-CD],   
            [CY],    
            [CL]
    ])
    # matriz de coeficientes aerodinamicos en terminos del viento 
    CFw = Cw_from_s @ CFs
    
    # paso 4: calculo de fuerzas aerodinamicas en el body
    # matriz de transformacion de datos de superficie a datos del body
    Cb_from_s = np.array([
            [np.cos(alpha),  0, -np.sin(alpha)],
            [0,              1,              0],
            [np.sin(alpha),  0,  np.cos(alpha)]
        ])
    # matriz de fuerzas aerodinamicas de la superficie?
    FAs = np.array([
            [-CD*Q*s],   
            [CY*Q*s],    
            [-CL*Q*s]
    ])
    # matriz de fuerzas aerodinamicas del body
    FAb = Cb_from_s @ FAs
    
    # paso 5: coeficientes de momento adimensionales alrededor del AC en Fb
    # matrices que se deben crear antes de calcula la matriz de coeficientes de momento del AC
    n = np.array([
            [-1.4 * betha],   
            [-0.59 - (3.1 * ((st * lt) / (s * c_mac)) * (alpha - etha))],    
            [(1 - (alpha * (180 / (15 * mt.pi)))) * betha]
    ]) 
    Cm_vs_x = np.array([
            [-11,  0,                                                       5],
            [0,    (-4.03 * ((st * lt**2) / (s * c_mac**2))),               0],
            [1.7,  0,                                         (-11.5 * betha)]
        ]) * (c_mac / V)
    wb_eb = np.array([
            [x4],   
            [x5],    
            [x6]
    ])
    Cm_vs_u = np.array([
            [-0.6, 0,                                    0.22],
            [0,    (-3.1 * ((st * lt) / (s * c_mac))),      0],
            [0,    0,                                   -0.63]
        ]) 
    Sc = np.array([
            [u1],   
            [u2],    
            [u3]
    ])
    # armamos la matriz de coeficientes en el AC
    Cm_ac = n + (Cm_vs_x @ wb_eb) + (Cm_vs_u @ Sc)
    
    # paso 6: momento aerodinamico alrededor del AC en las Fb
    Mac_b = Cm_ac * (Q * s * c_mac)
    
    # paso 7: momento aerodinamico alrededor del Cg en las Fb
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
    r_trans = r.flatten()
    FAb_trans = FAb.flatten()
    # calculo del momento en Cg
    cross_product = np.cross(r_trans, FAb_trans).reshape(3,1)
    Macg_b = Mac_b + cross_product
    
    # paso 8: efectos de la propulsion
    # datos fisicos de la aeronave
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
    # fuerza total de empuje
    Fe_tot = Fe1 + Fe2
    u1b = np.array([
            [(0.23 * c_mac) - 0],   
            [7.94 - 0],    
            [(0.1 * c_mac) - 1.9]
    ])
    # momento en el centro aerodinamico producido por el empuje del motor 1
    u1b_trans = u1b.flatten()
    Fe1_trans = Fe1.flatten()
    cross_product = np.cross(u1b_trans, Fe1_trans).reshape(3,1)
    Me1cg = cross_product
    u2b = np.array([
            [(0.23 * c_mac) - 0],   
            [-7.94 - 0],    
            [(0.1 * c_mac) - 1.9]
    ])
    # momento en el centro aerodinamico producido por el empuje del motor 2
    u2b_trans = u2b.flatten()
    Fe2_trans = Fe2.flatten()
    cross_product = np.cross(u2b_trans, Fe2_trans).reshape(3,1)
    Me2cg =cross_product
    # momento aerodinamico total producido por el empuje de ambos motores
    Mecg_tot = Me1cg + Me2cg
    
    # paso 9: efectos producidos por la gravedad
    # matriz de fuerza de gravedad del NED
    Fg = np.array([
            [0],   
            [0],    
            [g]
    ]) * m
    # matriz de fuerza de gravedad del body
    Fgb =  np.array([
            [-g * np.sin(x8)],   
            [g * np.cos(x8) * np.sin(x9)],    
            [g * np.cos(x8) * np.cos(x9)]
    ]) * m
    
    # paso 10: forma explicita de primer orden
    # matriz de inercia de la aeronave
    Ib = np.array([
            [40.07,  0,  2.098],
            [0,      64,     0],
            [2.098,  0,  99.92]
        ]) * 120000
    Fb = Fgb + FAb + Fe_tot
    v = np.array([
            [x1],   
            [x2],    
            [x3]
    ]) 
    wb_eb_trans = wb_eb.flatten()
    v_trans = v.flatten()
    cross_product = np.cross(wb_eb_trans,v_trans).reshape(3,1)
    V_dot = (1 / m) * Fb - cross_product
    Mcg = Mecg_tot + Macg_b
    inverted = np.linalg.inv(Ib)
    product_matrix = Ib @ wb_eb
    PM_trans = product_matrix.flatten()
    cross_product = np.cross(wb_eb_trans, PM_trans).reshape(3,1)
    turn_rate_dot = inverted @ (Mcg - cross_product)
    C_euler_Angles = np.array([
            [1, np.sin(x7) * np.tan(x8), np.cos(x7) * np.tan(x8)],
            [0, np.cos(x7),                          -np.sin(x8)],
            [0, np.sin(x7) * np.cos(x8), np.cos(x7) * np.cos(x8)]
        ])
    euler_dot = C_euler_Angles @ wb_eb
    V_dot_trans = V_dot.T
    turn_rate_dot_trans = turn_rate_dot.T
    euler_dot_trans = euler_dot.T
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
    return (X_dot)

def guardar_csv(pos, nombre_archivo="RCAM.csv"):
    with open(nombre_archivo, mode='w', newline='') as archivo:
        writer = csv.writer(archivo)
        writer.writerow(["time","u","v","w","p","q","r","phi","theta","zhi"])
        for fila in pos:
            writer.writerow(fila)
    print(f"Archivo guardado como: {nombre_archivo}")