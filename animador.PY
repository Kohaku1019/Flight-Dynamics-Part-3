import matplotlib
matplotlib.use('qtagg')
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec

def grafica():
    # =========================
    # LEER CSV
    # =========================
    CSV_FILE = "RCAM.csv"   # ← Coloca aquí el nombre de tu CSV (en la misma carpeta)

    df = pd.read_csv(CSV_FILE)

    # Columnas esperadas (por orden):
    # deflexion_aleron, deflexion_elevador, deflexion_ruder,
    # empuje_motor1, empuje_motor2, u, v, w, p, q, r, phi, theta, zhi
    t_data     = df.iloc[:, 0].values   # Tiempo
    da_data    = df.iloc[:, 1].values   # Deflexion aleron
    de_data    = df.iloc[:, 2].values   # Deflexion elevador
    dr_data    = df.iloc[:, 3].values   # Deflexion ruder
    em1_data   = df.iloc[:, 4].values   # Empuje Motor 1
    em2_data   = df.iloc[:, 5].values   # Empuje Motor 2
    u_data     = df.iloc[:, 6].values   # u
    v_data     = df.iloc[:, 7].values   # v
    w_data     = df.iloc[:, 8].values   # w
    p_data     = df.iloc[:, 9].values   # p
    q_data     = df.iloc[:, 10].values  # q
    r_data     = df.iloc[:, 11].values  # r
    phi_data   = df.iloc[:, 12].values  # phi
    theta_data = df.iloc[:, 13].values  # theta
    zhi_data   = df.iloc[:, 14].values  # zhi

    N = len(da_data)

    # Límites para las superficies de control y empuje
    PI_180 = np.pi / 180
    lim_da  = (-25 * PI_180,  25 * PI_180)
    lim_de  = (-25 * PI_180,  10 * PI_180)
    lim_dr  = (-30 * PI_180,  30 * PI_180)
    lim_em1 = (0.5 * PI_180,  10 * PI_180)
    lim_em2 = (0.5 * PI_180,  10 * PI_180)

    # =========================
    # MATRICES DE ROTACIÓN
    # =========================
    def get_rotation_matrix(yaw_deg, pitch_deg, roll_deg):
        yaw   = -np.radians(yaw_deg)
        pitch = -np.radians(pitch_deg)
        roll  =  np.radians(roll_deg)

        Rz = np.array([
            [np.cos(yaw), -np.sin(yaw), 0],
            [np.sin(yaw),  np.cos(yaw), 0],
            [0,            0,           1]
        ])
        Ry = np.array([
            [ np.cos(pitch), 0, np.sin(pitch)],
            [0,              1, 0            ],
            [-np.sin(pitch), 0, np.cos(pitch)]
        ])
        Rx = np.array([
            [1, 0,             0            ],
            [0, np.cos(roll), -np.sin(roll) ],
            [0, np.sin(roll),  np.cos(roll) ]
        ])
        return Rz @ Ry @ Rx

    def get_rotation_matrix_rad(psi, theta, phi):
        """Misma convención que get_rotation_matrix pero recibe radianes
        directamente — para animar el avión con phi_data/theta_data/zhi_data."""
        yaw   = -psi
        pitch = -theta
        roll  =  phi

        Rz = np.array([
            [np.cos(yaw), -np.sin(yaw), 0],
            [np.sin(yaw),  np.cos(yaw), 0],
            [0,            0,           1]
        ])
        Ry = np.array([
            [ np.cos(pitch), 0, np.sin(pitch)],
            [0,              1, 0            ],
            [-np.sin(pitch), 0, np.cos(pitch)]
        ])
        Rx = np.array([
            [1, 0,             0            ],
            [0, np.cos(roll), -np.sin(roll) ],
            [0, np.sin(roll),  np.cos(roll) ]
        ])
        return Rz @ Ry @ Rx

    # =========================
    # FIGURA
    # =========================
    fig = plt.figure(figsize=(32, 10))
    fig.patch.set_facecolor('#0d0d0d')
    gs = GridSpec(3, 14, figure=fig, hspace=0.55, wspace=0.45)

    col_dark = '#0d0d0d'
    col_grid = '#1e1e1e'
    col_text = '#cccccc'

    def estilo_ax(ax, titulo, color_linea):
        ax.set_facecolor(col_dark)
        ax.tick_params(colors=col_text, labelsize=7)
        for sp in ax.spines.values():
            sp.set_edgecolor('#333333')
        ax.set_title(titulo, color=color_linea, fontsize=8, pad=3)
        ax.grid(True, color=col_grid, linewidth=0.5)
        ax.set_xlim(t_data[0], t_data[-1])

    # ── Gráficas de superficies de control ───────────────────────────────
    ax_da  = fig.add_subplot(gs[0, 0:2])
    ax_de  = fig.add_subplot(gs[1, 0:2])
    ax_dr  = fig.add_subplot(gs[2, 0:2])

    for ax, titulo, col, data, ylim in zip(
            [ax_da, ax_de, ax_dr],
            ["Deflexión Alerón (rad)", "Deflexión Elevador (rad)", "Deflexión Ruder (rad)"],
            ['#00d4ff', '#ff6b35', '#7fff6b'],
            [da_data, de_data, dr_data],
            [lim_da, lim_de, lim_dr]):
        estilo_ax(ax, titulo, col)
        ax.set_ylim(ylim[0], ylim[1])
        ax.plot(t_data, data, color=col, linewidth=0.8, alpha=0.3)

    # ── Gráficas de empuje ───────────────────────────────────────────────
    ax_em1 = fig.add_subplot(gs[0, 2:4])
    ax_em2 = fig.add_subplot(gs[1, 2:4])
    ax_uvw = fig.add_subplot(gs[2, 2:4])  # placeholder para u,v,w combinado o w solo

    for ax, titulo, col, data, ylim in zip(
            [ax_em1, ax_em2],
            ["Empuje Motor 1", "Empuje Motor 2"],
            ['#ff3cac', '#ffe53b'],
            [em1_data, em2_data],
            [lim_em1, lim_em2]):
        estilo_ax(ax, titulo, col)
        ax.set_ylim(ylim[0], ylim[1])
        ax.plot(t_data, data, color=col, linewidth=0.8, alpha=0.3)

    # ── Gráficas de velocidades lineales u, v, w ─────────────────────────
    ax_u = ax_uvw
    ax_v = fig.add_subplot(gs[0, 4:6])
    ax_w = fig.add_subplot(gs[1, 4:6])

    for ax, titulo, col, data in zip(
            [ax_u, ax_v, ax_w],
            ["u (m/s)", "v (m/s)", "w (m/s)"],
            ['#3c78ff', '#ff9f43', '#ee5a24'],
            [u_data, v_data, w_data]):
        estilo_ax(ax, titulo, col)
        ax.set_ylim(data.min() - 0.02, data.max() + 0.02)
        ax.plot(t_data, data, color=col, linewidth=0.8, alpha=0.3)

    # ── Gráficas de velocidad angular p, q, r ────────────────────────────
    ax_p = fig.add_subplot(gs[2, 4:6])
    ax_q = fig.add_subplot(gs[0, 6:8])
    ax_r = fig.add_subplot(gs[1, 6:8])

    for ax, titulo, col, data in zip(
            [ax_p, ax_q, ax_r],
            ["p (rad/s)", "q (rad/s)", "r (rad/s)"],
            ['#a29bfe', '#6c5ce7', '#74b9ff'],
            [p_data, q_data, r_data]):
        estilo_ax(ax, titulo, col)
        ax.set_ylim(data.min() - 0.02, data.max() + 0.02)
        ax.plot(t_data, data, color=col, linewidth=0.8, alpha=0.3)

    # ── Gráficas de ángulos de Euler phi, theta, zhi ─────────────────────
    ax_phi   = fig.add_subplot(gs[2, 6:8])
    ax_theta = fig.add_subplot(gs[0, 8:10])
    ax_zhi   = fig.add_subplot(gs[1, 8:10])

    for ax, titulo, col, data in zip(
            [ax_phi, ax_theta, ax_zhi],
            ["φ phi (rad)", "θ theta (rad)", "ψ zhi (rad)"],
            ['#fd79a8', '#55efc4', '#ffeaa7'],
            [phi_data, theta_data, zhi_data]):
        estilo_ax(ax, titulo, col)
        ax.set_ylim(data.min() - 0.02, data.max() + 0.02)
        ax.plot(t_data, data, color=col, linewidth=0.8, alpha=0.3)

    # ── Líneas animadas (trazado en tiempo real) ──────────────────────────
    line_da,    = ax_da.plot([],    [], color='#00d4ff', linewidth=1.5)
    line_de,    = ax_de.plot([],    [], color='#ff6b35', linewidth=1.5)
    line_dr,    = ax_dr.plot([],    [], color='#7fff6b', linewidth=1.5)
    line_em1,   = ax_em1.plot([],   [], color='#ff3cac', linewidth=1.5)
    line_em2,   = ax_em2.plot([],   [], color='#ffe53b', linewidth=1.5)
    line_u,     = ax_u.plot([],     [], color='#3c78ff', linewidth=1.5)
    line_v,     = ax_v.plot([],     [], color='#ff9f43', linewidth=1.5)
    line_w,     = ax_w.plot([],     [], color='#ee5a24', linewidth=1.5)
    line_p,     = ax_p.plot([],     [], color='#a29bfe', linewidth=1.5)
    line_q,     = ax_q.plot([],     [], color='#6c5ce7', linewidth=1.5)
    line_r,     = ax_r.plot([],     [], color='#74b9ff', linewidth=1.5)
    line_phi,   = ax_phi.plot([],   [], color='#fd79a8', linewidth=1.5)
    line_theta, = ax_theta.plot([], [], color='#55efc4', linewidth=1.5)
    line_zhi,   = ax_zhi.plot([],   [], color='#ffeaa7', linewidth=1.5)

    # Marcadores de posición actual
    dot_da,    = ax_da.plot([],    [], 'o', color='#00d4ff', ms=5)
    dot_de,    = ax_de.plot([],    [], 'o', color='#ff6b35', ms=5)
    dot_dr,    = ax_dr.plot([],    [], 'o', color='#7fff6b', ms=5)
    dot_em1,   = ax_em1.plot([],   [], 'o', color='#ff3cac', ms=5)
    dot_em2,   = ax_em2.plot([],   [], 'o', color='#ffe53b', ms=5)
    dot_u,     = ax_u.plot([],     [], 'o', color='#3c78ff', ms=5)
    dot_v,     = ax_v.plot([],     [], 'o', color='#ff9f43', ms=5)
    dot_w,     = ax_w.plot([],     [], 'o', color='#ee5a24', ms=5)
    dot_p,     = ax_p.plot([],     [], 'o', color='#a29bfe', ms=5)
    dot_q,     = ax_q.plot([],     [], 'o', color='#6c5ce7', ms=5)
    dot_r,     = ax_r.plot([],     [], 'o', color='#74b9ff', ms=5)
    dot_phi,   = ax_phi.plot([],   [], 'o', color='#fd79a8', ms=5)
    dot_theta, = ax_theta.plot([], [], 'o', color='#55efc4', ms=5)
    dot_zhi,   = ax_zhi.plot([],   [], 'o', color='#ffeaa7', ms=5)

    # =========================
    # VISTA 3D
    # =========================
    ax3d = fig.add_subplot(gs[:, 11:], projection='3d')
    ax3d.set_facecolor(col_dark)
    ax3d.xaxis.pane.fill = False
    ax3d.yaxis.pane.fill = False
    ax3d.zaxis.pane.fill = False
    ax3d.xaxis.pane.set_edgecolor('#222222')
    ax3d.yaxis.pane.set_edgecolor('#222222')
    ax3d.zaxis.pane.set_edgecolor('#222222')

    grosor = 2.5
    L = 12
    gris_ejes = '#2a2a2a'
    S = 7.0   # factor de escala del avión — también usado para lim_3d y posición de motores

    # ── Ejes NED fijos ───────────────────────────────────────────────────
    ax3d.quiver(0, 0, 0, L, 0, 0, color='#555555', linewidth=1.5)
    ax3d.text(L+1, 0, 0, 'N+', color='#888888', fontsize=8)
    ax3d.quiver(0, 0, 0, 0, -L, 0, color='#555555', linewidth=1.5)
    ax3d.text(0, -L-1, 0, 'E+', color='#888888', fontsize=8)
    ax3d.quiver(0, 0, 0, 0, 0, -L, color='#555555', linewidth=1.5)
    ax3d.text(0, 0, -L-2, 'D+', color='#888888', fontsize=8)

    # ── Límites fijos centrados en el origen (avión siempre en centro) ────
    lim_3d = S * 3 + 10   # margen proporcional al tamaño del avión
    ax3d.set_xlim(-lim_3d, lim_3d)
    ax3d.set_ylim(-lim_3d, lim_3d)
    ax3d.set_zlim(-lim_3d, lim_3d)
    ax3d.set_box_aspect([1, 1, 1])
    ax3d.set_xticks([]); ax3d.set_yticks([]); ax3d.set_zticks([])

    # ── Texto de telemetría — se ancla a la FIGURA (no al eje 3D) ──────────
    # Así nunca se solapa con el título ni con las decoraciones del eje 3D.
    # Necesitamos la posición del eje 3D en coordenadas de figura.
    fig.canvas.draw()   # forzar layout para que get_position() devuelva valores reales
    pos3d = ax3d.get_position()   # Bbox en coordenadas de figura [0,1]

    cx   = pos3d.x0 + pos3d.width  * 0.5   # centro horizontal del eje 3D
    top  = pos3d.y0 + pos3d.height          # borde superior del eje 3D

    # Línea 1 (la más alta): velocidades  u / v / w
    text_vel = fig.text(
        cx, top + 0.075,
        "u = 0.000 m/s   v = 0.000 m/s   w = 0.000 m/s",
        ha='center', va='bottom',
        fontsize=9, color='#74b9ff',
        fontfamily='monospace'
    )

    # Línea 2: ángulos de Euler
    text_euler = fig.text(
        cx, top + 0.040,
        "φ = 0.000 rad   θ = 0.000 rad   ψ = 0.000 rad",
        ha='center', va='bottom',
        fontsize=9, color='#ffeaa7',
        fontfamily='monospace'
    )

    # Línea 3 (justo encima del eje): tiempo
    titulo_3d = fig.text(
        cx, top + 0.010,
        "t = 0 s",
        ha='center', va='bottom',
        fontsize=10, color='#ffffff', fontweight='bold'
    )

    # ── Texto debajo del eje 3D: ángulos en GRADOS ────────────────────────
    bot = pos3d.y0   # borde inferior del eje 3D

    text_euler_deg = fig.text(
        cx, bot - 0.030,
        "φ = 0.00°   θ = 0.00°   ψ = 0.00°",
        ha='center', va='top',
        fontsize=9, color='#ffd580',
        fontfamily='monospace'
    )

    # ── Trayectoria eliminada (avión fijo en origen) ──────────────────────

    # ==========================================================================
    # AVIÓN DETALLADO — fuselaje cónico, alas trapezoidales, superficies móviles
    # ==========================================================================
    # Convención de cuerpo: X=nariz→cola, Y=ala derecha, Z=arriba
    # Todas las coordenadas en unidades S.

    # ── Helper: rotar+trazar una polilínea de puntos (N,3) ────────────────
    def _linea(ax, pts_body, R, col, lw=2.0, ls='-', alpha=1.0):
        rot = (R @ pts_body.T)          # (3,N)
        l, = ax.plot(rot[0], rot[1], rot[2],
                     color=col, linewidth=lw, linestyle=ls, alpha=alpha)
        return l

    def _actualizar(line, pts_body, R):
        rot = R @ pts_body.T
        line.set_data(rot[0], rot[1])
        line.set_3d_properties(rot[2])

    # ── Geometría base del fuselaje (secciones elípticas simplificadas) ──
    # Nariz puntiaguda → cabina → cuerpo → cono de cola
    # Perfil superior e inferior del fuselaje en el plano XZ (Y=0)
    fx = np.array([ 2.0, 1.5, 1.0, 0.5, 0.0,-0.5,-1.0,-1.5,-2.0,-2.3,-2.6]) * S
    fz_top = np.array([0.0, 0.18,0.28,0.32,0.30,0.28,0.25,0.20,0.15,0.08,0.0]) * S
    fz_bot = -fz_top * 0.7

    fus_top_pts    = np.column_stack([fx, np.zeros_like(fx), fz_top])
    fus_bot_pts    = np.column_stack([fx, np.zeros_like(fx), fz_bot])
    # Costados (perfil lateral Y=±radio)
    fy_side = np.array([0.0,0.20,0.30,0.33,0.32,0.30,0.27,0.22,0.16,0.09,0.0]) * S
    fus_rside_pts  = np.column_stack([fx,  fy_side, np.zeros_like(fx)])
    fus_lside_pts  = np.column_stack([fx, -fy_side, np.zeros_like(fx)])
    # Cuadernas (anillos) en 4 posiciones
    def _cuaderna(x_pos, ry, rz, n=12):
        t = np.linspace(0, 2*np.pi, n+1)
        return np.column_stack([np.full(n+1, x_pos), ry*np.cos(t), rz*np.sin(t)])

    cuad_pts = [
        _cuaderna( 1.0*S, 0.28*S, 0.26*S),
        _cuaderna( 0.0*S, 0.32*S, 0.28*S),
        _cuaderna(-1.0*S, 0.30*S, 0.26*S),
        _cuaderna(-2.0*S, 0.16*S, 0.14*S),
    ]

    # ── Alas trapezoidales con flecha ──────────────────────────────────────
    # Borde de ataque derecho: raíz → punta
    # Raíz: (x=0.3S, y=0.32S)   Punta: (x=-0.8S, y=3.0S)
    # Borde de fuga derecho: raíz (x=-0.5S, y=0.32S) → punta (x=-1.4S, y=3.0S)
    ala_d_ba = np.array([[ 0.3*S, 0.32*S, 0.0],
                          [-0.8*S, 3.0*S,  0.0]])   # borde ataque derecho
    ala_d_bf = np.array([[-0.5*S, 0.32*S, 0.0],
                          [-1.4*S, 3.0*S,  0.0]])   # borde fuga derecho
    ala_d_raiz = np.array([[ 0.3*S, 0.32*S, 0.0],
                            [-0.5*S, 0.32*S, 0.0]])  # raíz ala derecha
    ala_d_punta= np.array([[-0.8*S, 3.0*S,  0.0],
                            [-1.4*S, 3.0*S,  0.0]])  # punta ala derecha
    # Ala izquierda (Y negativo)
    ala_i_ba   = ala_d_ba.copy();   ala_i_ba[:,1]   *= -1
    ala_i_bf   = ala_d_bf.copy();   ala_i_bf[:,1]   *= -1
    ala_i_raiz = ala_d_raiz.copy(); ala_i_raiz[:,1] *= -1
    ala_i_punta= ala_d_punta.copy();ala_i_punta[:,1]*= -1

    # ── Alerones (30% exterior del ala, borde de fuga) ────────────────────
    # Posición en reposo; se rotarán respecto al borde de fuga en cada frame
    # Alerón derecho: de y=2.0S a y=3.0S sobre el borde de fuga
    AIL_Y_IN, AIL_Y_OUT = 2.0*S, 3.0*S
    AIL_CHORD = 0.35*S   # profundidad del alerón

    def _pts_aileron(sign_y, deflexion):
        """Devuelve los 5 puntos del alerón (cuadrilátero) dado el signo Y y deflexión."""
        # Bisagra en el borde de fuga del ala principal
        # x de bisagra interpolado linealmente entre raíz y punta
        def x_bf(y_abs):
            t = (y_abs - 0.32*S) / (3.0*S - 0.32*S)
            return -0.5*S + t*(-1.4*S - (-0.5*S))
        def x_ba(y_abs):
            t = (y_abs - 0.32*S) / (3.0*S - 0.32*S)
            return 0.3*S + t*(-0.8*S - 0.3*S)

        y_in  = sign_y * AIL_Y_IN
        y_out = sign_y * AIL_Y_OUT
        # Cuatro esquinas del alerón en reposo (en el plano del ala)
        p0 = np.array([x_bf(AIL_Y_IN),  y_in,  0.0])
        p1 = np.array([x_bf(AIL_Y_OUT), y_out, 0.0])
        # Borde libre rotado por deflexión respecto a la bisagra (eje Y del ala ≈ eje Y cuerpo)
        d = AIL_CHORD
        # Signo positivo → ala derecha baja (-Z), ala izquierda sube (+Z)
        p2 = p1 + np.array([-d*np.cos(deflexion), 0.0, -d*np.sin(deflexion)])
        p3 = p0 + np.array([-d*np.cos(deflexion), 0.0, -d*np.sin(deflexion)])
        return np.array([p0, p1, p2, p3, p0])   # cerrado

    # ── Estabilizador horizontal (cola) ───────────────────────────────────
    # Raíz: x=-2.3S, y=±0.28S   Punta: x=-2.6S, y=±1.2S
    stab_d_ba  = np.array([[-2.0*S, 0.28*S, 0.0],[-2.3*S, 1.2*S, 0.0]])
    stab_d_bf  = np.array([[-2.3*S, 0.28*S, 0.0],[-2.6*S, 1.2*S, 0.0]])
    stab_d_r   = np.array([[-2.0*S, 0.28*S, 0.0],[-2.3*S, 0.28*S, 0.0]])
    stab_d_p   = np.array([[-2.3*S, 1.2*S, 0.0], [-2.6*S, 1.2*S, 0.0]])
    stab_i_ba  = stab_d_ba.copy(); stab_i_ba[:,1]  *= -1
    stab_i_bf  = stab_d_bf.copy(); stab_i_bf[:,1]  *= -1
    stab_i_r   = stab_d_r.copy();  stab_i_r[:,1]   *= -1
    stab_i_p   = stab_d_p.copy();  stab_i_p[:,1]   *= -1

    # ── Elevadores (toda la envergadura del estabilizador, borde de fuga) ─
    ELEV_CHORD = 0.22*S
    def _pts_elevador(sign_y, deflexion):
        y_in  = sign_y * 0.28*S
        y_out = sign_y * 1.2*S
        def x_bf_e(y_abs):
            t = (y_abs - 0.28*S) / (1.2*S - 0.28*S)
            return -2.3*S + t*(-2.6*S - (-2.3*S))
        p0 = np.array([x_bf_e(0.28*S), y_in,  0.0])
        p1 = np.array([x_bf_e(1.2*S),  y_out, 0.0])
        d  = ELEV_CHORD
        # Signo positivo → borde libre baja (-Z = deflexión hacia abajo)
        p2 = p1 + np.array([-d*np.cos(deflexion), 0.0, -d*np.sin(deflexion)])
        p3 = p0 + np.array([-d*np.cos(deflexion), 0.0, -d*np.sin(deflexion)])
        return np.array([p0, p1, p2, p3, p0])

    # ── Timón vertical (ruder) ────────────────────────────────────────────
    # Estabilizador vertical raíz→punta
    vert_ba  = np.array([[-2.0*S, 0.0,  0.1*S],[-2.3*S, 0.0, 1.4*S]])
    vert_bf  = np.array([[-2.3*S, 0.0,  0.1*S],[-2.6*S, 0.0, 1.4*S]])
    vert_raiz= np.array([[-2.0*S, 0.0,  0.1*S],[-2.3*S, 0.0, 0.1*S]])
    vert_punta=np.array([[-2.3*S, 0.0,  1.4*S],[-2.6*S, 0.0, 1.4*S]])

    RUD_CHORD = 0.22*S
    def _pts_ruder(deflexion):
        z_in  = 0.1*S
        z_out = 1.4*S
        def x_bf_r(z):
            t = (z - z_in) / (z_out - z_in)
            return -2.3*S + t*(-2.6*S - (-2.3*S))
        p0 = np.array([x_bf_r(z_in),  0.0, z_in ])
        p1 = np.array([x_bf_r(z_out), 0.0, z_out])
        d  = RUD_CHORD
        # Signo positivo → borde libre va a la derecha (+Y)
        p2 = p1 + np.array([-d*np.cos(deflexion), +d*np.sin(deflexion), 0.0])
        p3 = p0 + np.array([-d*np.cos(deflexion), +d*np.sin(deflexion), 0.0])
        return np.array([p0, p1, p2, p3, p0])

    # ── Nacelas de motor (elipses en las alas) ────────────────────────────
    def _nacela(y_pos, n=10):
        t = np.linspace(0, 2*np.pi, n+1)
        rx, rz = 0.18*S, 0.12*S
        x_cen, z_cen = -0.15*S, -0.08*S
        return np.column_stack([x_cen + rx*np.cos(t),
                                 np.full(n+1, y_pos),
                                 z_cen + rz*np.sin(t)])

    nacela_d_pts = _nacela( 2.0*S)
    nacela_i_pts = _nacela(-2.0*S)

    # ════════════════════════════════════════════════════════════════════════
    # Crear TODAS las líneas de la escena (estado inicial con R0, da=de=dr=0)
    # ════════════════════════════════════════════════════════════════════════
    R0   = get_rotation_matrix_rad(zhi_data[0], theta_data[0], phi_data[0])
    da0  = da_data[0];  de0 = de_data[0];  dr0 = dr_data[0]

    C_FUS   = '#00d4ff'   # fuselaje — azul cielo
    C_ALA   = '#1a9fff'   # alas / estab — azul más suave
    C_AIL   = '#00ffcc'   # alerones
    C_ELEV  = '#55efc4'   # elevadores
    C_RUD   = '#ff6b35'   # timón
    C_NACELA= '#888888'   # nacelas
    LW_MAIN = 2.5
    LW_SURF = 2.0
    LW_NACe = 1.5

    # Fuselaje
    l_fus_top   = _linea(ax3d, fus_top_pts,    R0, C_FUS,  LW_MAIN)
    l_fus_bot   = _linea(ax3d, fus_bot_pts,    R0, C_FUS,  LW_MAIN)
    l_fus_r     = _linea(ax3d, fus_rside_pts,  R0, C_FUS,  LW_MAIN)
    l_fus_l     = _linea(ax3d, fus_lside_pts,  R0, C_FUS,  LW_MAIN)
    l_cuads     = [_linea(ax3d, cp, R0, '#1a3a4a', 1.0, alpha=0.5) for cp in cuad_pts]

    # Alas
    l_ala_dba   = _linea(ax3d, ala_d_ba,   R0, C_ALA, LW_MAIN)
    l_ala_dbf   = _linea(ax3d, ala_d_bf,   R0, C_ALA, LW_MAIN)
    l_ala_dr    = _linea(ax3d, ala_d_raiz, R0, C_ALA, LW_MAIN)
    l_ala_dp    = _linea(ax3d, ala_d_punta,R0, C_ALA, LW_MAIN)
    l_ala_iba   = _linea(ax3d, ala_i_ba,   R0, C_ALA, LW_MAIN)
    l_ala_ibf   = _linea(ax3d, ala_i_bf,   R0, C_ALA, LW_MAIN)
    l_ala_ir    = _linea(ax3d, ala_i_raiz, R0, C_ALA, LW_MAIN)
    l_ala_ip    = _linea(ax3d, ala_i_punta,R0, C_ALA, LW_MAIN)

    # Alerones (deflexión inicial)
    l_ail_d = _linea(ax3d, _pts_aileron(+1,  da0), R0, C_AIL, LW_SURF)
    l_ail_i = _linea(ax3d, _pts_aileron(-1, -da0), R0, C_AIL, LW_SURF)

    # Estabilizador horizontal
    l_stab_dba  = _linea(ax3d, stab_d_ba,  R0, C_ALA, LW_MAIN)
    l_stab_dbf  = _linea(ax3d, stab_d_bf,  R0, C_ALA, LW_MAIN)
    l_stab_dr   = _linea(ax3d, stab_d_r,   R0, C_ALA, LW_MAIN)
    l_stab_dp   = _linea(ax3d, stab_d_p,   R0, C_ALA, LW_MAIN)
    l_stab_iba  = _linea(ax3d, stab_i_ba,  R0, C_ALA, LW_MAIN)
    l_stab_ibf  = _linea(ax3d, stab_i_bf,  R0, C_ALA, LW_MAIN)
    l_stab_ir   = _linea(ax3d, stab_i_r,   R0, C_ALA, LW_MAIN)
    l_stab_ip   = _linea(ax3d, stab_i_p,   R0, C_ALA, LW_MAIN)

    # Elevadores
    l_elev_d = _linea(ax3d, _pts_elevador(+1, de0), R0, C_ELEV, LW_SURF)
    l_elev_i = _linea(ax3d, _pts_elevador(-1, de0), R0, C_ELEV, LW_SURF)

    # Estabilizador vertical
    l_vert_ba   = _linea(ax3d, vert_ba,    R0, C_RUD, LW_MAIN)
    l_vert_bf   = _linea(ax3d, vert_bf,    R0, C_RUD, LW_MAIN)
    l_vert_r    = _linea(ax3d, vert_raiz,  R0, C_RUD, LW_MAIN)
    l_vert_p    = _linea(ax3d, vert_punta, R0, C_RUD, LW_MAIN)

    # Timón
    l_ruder = _linea(ax3d, _pts_ruder(dr0), R0, C_RUD, LW_SURF)

    # Nacelas
    l_nac_d = _linea(ax3d, nacela_d_pts, R0, C_NACELA, LW_NACe)
    l_nac_i = _linea(ax3d, nacela_i_pts, R0, C_NACELA, LW_NACe)

    # Lista plana de (line, pts_fn) para actualizar en update()
    # Las superficies móviles se actualizan aparte con su deflexión
    _lineas_fijas = [
        (l_fus_top,  fus_top_pts),   (l_fus_bot,  fus_bot_pts),
        (l_fus_r,    fus_rside_pts), (l_fus_l,    fus_lside_pts),
        (l_ala_dba,  ala_d_ba),  (l_ala_dbf,  ala_d_bf),
        (l_ala_dr,   ala_d_raiz),(l_ala_dp,   ala_d_punta),
        (l_ala_iba,  ala_i_ba),  (l_ala_ibf,  ala_i_bf),
        (l_ala_ir,   ala_i_raiz),(l_ala_ip,   ala_i_punta),
        (l_stab_dba, stab_d_ba), (l_stab_dbf, stab_d_bf),
        (l_stab_dr,  stab_d_r),  (l_stab_dp,  stab_d_p),
        (l_stab_iba, stab_i_ba), (l_stab_ibf, stab_i_bf),
        (l_stab_ir,  stab_i_r),  (l_stab_ip,  stab_i_p),
        (l_vert_ba,  vert_ba),   (l_vert_bf,  vert_bf),
        (l_vert_r,   vert_raiz), (l_vert_p,   vert_punta),
        (l_nac_d,    nacela_d_pts),(l_nac_i,  nacela_i_pts),
    ]
    _lineas_cuad = list(zip(l_cuads, cuad_pts))

    # =========================
    # CHORROS DE MOTOR (jet exhaust)
    # =========================
    EMPUJE_MIN = 0.5 * PI_180   # mismo lower-limit que lim_em1/em2

    # ── Posición exacta de cada motor sobre el ala ────────────────────────
    # El ala va de Y=0 hasta Y=±3*S desde X=0.
    # Colocamos el motor a 2/3 del ala hacia la punta, al nivel del fuselaje (X=0).
    MOTOR1_LOCAL = np.array([ 0.0,  2.0*S, 0.0])   # motor derecho  (+Y)
    MOTOR2_LOCAL = np.array([ 0.0, -2.0*S, 0.0])   # motor izquierdo(-Y)

    # ── Parámetros de estela ──────────────────────────────────────────────
    N_JET   = 30     # puntos del chorro (más → línea más suave y larga)
    JET_LEN = 22.0   # longitud máxima del chorro en unidades de escena

    # Tres "tubos" paralelos que forman el chorro (offset en Z local)
    JET_OFFSETS = [0.0, 0.3, -0.3]   # centro, arriba, abajo

    # Crear 3 líneas por motor (centro + 2 laterales) — color gris humo
    chorro_m1_lines = [
        ax3d.plot([], [], [], color='#aaaaaa', linewidth=2.5,
                  linestyle='--', alpha=0.90)[0],
        ax3d.plot([], [], [], color='#888888', linewidth=1.5,
                  linestyle=':', alpha=0.65)[0],
        ax3d.plot([], [], [], color='#888888', linewidth=1.5,
                  linestyle=':', alpha=0.65)[0],
    ]
    chorro_m2_lines = [
        ax3d.plot([], [], [], color='#aaaaaa', linewidth=2.5,
                  linestyle='--', alpha=0.90)[0],
        ax3d.plot([], [], [], color='#888888', linewidth=1.5,
                  linestyle=':', alpha=0.65)[0],
        ax3d.plot([], [], [], color='#888888', linewidth=1.5,
                  linestyle=':', alpha=0.65)[0],
    ]
    # Glow en la boca de cada motor — blanco-grisáceo
    glow_m1, = ax3d.plot([], [], [], 'o', color='#dddddd', ms=10, alpha=0.95)
    glow_m2, = ax3d.plot([], [], [], 'o', color='#dddddd', ms=10, alpha=0.95)

    def calcular_chorro(R, motor_local, empuje, frame_offset, z_off=0.0):
        """Devuelve puntos XYZ del chorro (con offset lateral z_off en cuerpo)."""
        if empuje <= EMPUJE_MIN:
            return None

        ratio  = (empuje - EMPUJE_MIN) / (lim_em1[1] - EMPUJE_MIN)
        length = JET_LEN * (0.5 + 0.5 * ratio)

        # Fase animada: los guiones "fluyen" hacia atrás
        phase = (frame_offset * 0.55) % 1.0
        t_pts = np.linspace(phase * length / N_JET, length, N_JET)

        # El chorro sale en dirección -X del cuerpo (hacia la cola)
        body_pts = np.array([
            motor_local[0] - t_pts,
            np.full(N_JET, motor_local[1]),
            np.full(N_JET, motor_local[2] + z_off)
        ])

        return R @ body_pts   # shape (3, N_JET)


    quivers_local = []
    def crear_quivers(ox, oy, oz):
        ql = []
        dirs = [(L,0,0),(-L,0,0),(0,L,0),(0,-L,0),(0,0,L),(0,0,-L)]
        for d in dirs:
            ql.append(ax3d.quiver(ox, oy, oz, d[0], d[1], d[2],
                                color=gris_ejes, linewidth=1))
        return ql

    quivers_local = crear_quivers(0, 0, 0)

    # =========================
    # ROTACIÓN LIBRE CON MOUSE
    # =========================
    # Vista inicial: perspectiva isométrica frontal-lateral
    ax3d.view_init(elev=20, azim=-60)

    # Estado compartido de la vista: el usuario puede arrastrar libremente
    _view = {'elev': 20.0, 'azim': -60.0,
             'drag': False, 'x0': 0, 'y0': 0}

    def _on_press(event):
        if event.inaxes is ax3d and event.button == 1:
            _view['drag'] = True
            _view['x0']   = event.x
            _view['y0']   = event.y

    def _on_release(event):
        _view['drag'] = False

    def _on_motion(event):
        if not _view['drag']:
            return
        if event.inaxes is not ax3d:
            return
        dx = event.x - _view['x0']
        dy = event.y - _view['y0']
        _view['x0'] = event.x
        _view['y0'] = event.y
        # azim cambia con movimiento horizontal, elev con vertical
        _view['azim'] += dx * 0.4
        _view['elev']  = np.clip(_view['elev'] - dy * 0.4, -90, 90)
        ax3d.view_init(elev=_view['elev'], azim=_view['azim'])
        fig.canvas.draw_idle()

    fig.canvas.mpl_connect('button_press_event',   _on_press)
    fig.canvas.mpl_connect('button_release_event', _on_release)
    fig.canvas.mpl_connect('motion_notify_event',  _on_motion)

    # =========================
    # ANIMACIÓN
    # =========================
    INTERVAL_MS = 1000   # ms entre frames (ajusta para velocidad)

    all_lines = [line_da, line_de, line_dr, line_em1, line_em2,
                 line_u, line_v, line_w, line_p, line_q, line_r,
                 line_phi, line_theta, line_zhi]
    all_dots  = [dot_da, dot_de, dot_dr, dot_em1, dot_em2,
                 dot_u, dot_v, dot_w, dot_p, dot_q, dot_r,
                 dot_phi, dot_theta, dot_zhi]
    all_data  = [da_data, de_data, dr_data, em1_data, em2_data,
                 u_data, v_data, w_data, p_data, q_data, r_data,
                 phi_data, theta_data, zhi_data]

    def init():
        for line in all_lines:
            line.set_data([], [])
        return []

    def update(frame):
        idx = frame % N

        # — Gráficas 2D —
        t_slice = t_data[:idx+1]
        for line, dot, data in zip(all_lines, all_dots, all_data):
            line.set_data(t_slice, data[:idx+1])
            dot.set_data([t_data[idx]], [data[idx]])

        # — Avión 3D —
        phi_i   = phi_data[idx]
        theta_i = theta_data[idx]
        zhi_i   = zhi_data[idx]
        ui = u_data[idx]
        vi = v_data[idx]
        wi = w_data[idx]

        R = get_rotation_matrix_rad(zhi_i, theta_i, phi_i)

        # Preservar la vista que el usuario haya seteado con el mouse
        ax3d.view_init(elev=_view['elev'], azim=_view['azim'])

        # ── Estructuras fijas del avión ───────────────────────────────────
        for line, pts in _lineas_fijas:
            _actualizar(line, pts, R)
        for line, pts in _lineas_cuad:
            _actualizar(line, pts, R)

        # ── Superficies de control móviles ────────────────────────────────
        da_i = da_data[idx];  de_i = de_data[idx];  dr_i = dr_data[idx]
        # Alerones: derecho +da, izquierdo -da (diferencial)
        _actualizar(l_ail_d, _pts_aileron(+1,  da_i), R)
        _actualizar(l_ail_i, _pts_aileron(-1, -da_i), R)
        # Elevadores: ambos la misma deflexión
        _actualizar(l_elev_d, _pts_elevador(+1, de_i), R)
        _actualizar(l_elev_i, _pts_elevador(-1, de_i), R)
        # Timón
        _actualizar(l_ruder, _pts_ruder(dr_i), R)

        # Ejes locales también fijos en el origen
        for q in quivers_local:
            q.remove()
        quivers_local.clear()
        for q in crear_quivers(0, 0, 0):
            quivers_local.append(q)

        # ── Chorros de motor ──────────────────────────────────────────────
        em1_i = em1_data[idx]
        em2_i = em2_data[idx]

        for chorros, glow, motor_local, empuje in [
            (chorro_m1_lines, glow_m1, MOTOR1_LOCAL, em1_i),
            (chorro_m2_lines, glow_m2, MOTOR2_LOCAL, em2_i),
        ]:
            apagado = empuje <= EMPUJE_MIN
            for k, (linea, z_off) in enumerate(zip(chorros, JET_OFFSETS)):
                pts = calcular_chorro(R, motor_local, empuje, idx, z_off)
                if apagado or pts is None:
                    linea.set_data([], [])
                    linea.set_3d_properties([])
                else:
                    linea.set_data(pts[0], pts[1])
                    linea.set_3d_properties(pts[2])
            if apagado:
                glow.set_data([], [])
                glow.set_3d_properties([])
            else:
                boca = R @ motor_local
                glow.set_data([boca[0]], [boca[1]])
                glow.set_3d_properties([boca[2]])

        # ── Actualizar telemetría encima de la vista 3D ───────────────────
        titulo_3d.set_text(f"t = {idx} s")
        text_euler.set_text(
            f"φ = {phi_i:+.4f} rad   "
            f"θ = {theta_i:+.4f} rad   "
            f"ψ = {zhi_i:+.4f} rad"
        )
        text_vel.set_text(
            f"u = {ui:+.4f} m/s   "
            f"v = {vi:+.4f} m/s   "
            f"w = {wi:+.4f} m/s"
        )
        # ── Ángulos en grados (debajo del avión) ──────────────────────────
        text_euler_deg.set_text(
            f"φ = {np.degrees(phi_i):+.2f}°   "
            f"θ = {np.degrees(theta_i):+.2f}°   "
            f"ψ = {np.degrees(zhi_i):+.2f}°"
        )

        fig.canvas.draw_idle()
        return []

    ani = animation.FuncAnimation(
        fig, update,
        frames=N,
        init_func=init,
        interval=INTERVAL_MS,
        blit=False,
        repeat=True
    )

    plt.tight_layout()
    plt.show()

grafica()
input()