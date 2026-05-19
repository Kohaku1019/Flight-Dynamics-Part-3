import matplotlib
matplotlib.use('qtagg')

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec


def main():

    def grafic():

        # =========================
        # LEER CSV
        # =========================
        CSV_FILE = "RCAM.csv"

        df = pd.read_csv(CSV_FILE)

        # =========================
        # VALIDACIONES
        # =========================
        if len(df) == 0:
            print("El CSV está vacío")
            return

        if df.shape[1] < 15:
            print("El CSV no tiene suficientes columnas")
            return

        # =========================
        # DATOS
        # =========================
        t_data     = df.iloc[:, 0].values
        da_data    = df.iloc[:, 1].values
        de_data    = df.iloc[:, 2].values
        dr_data    = df.iloc[:, 3].values
        em1_data   = df.iloc[:, 4].values
        em2_data   = df.iloc[:, 5].values
        u_data     = df.iloc[:, 6].values
        v_data     = df.iloc[:, 7].values
        w_data     = df.iloc[:, 8].values
        p_data     = df.iloc[:, 9].values
        q_data     = df.iloc[:, 10].values
        r_data     = df.iloc[:, 11].values
        phi_data   = df.iloc[:, 12].values
        theta_data = df.iloc[:, 13].values
        zhi_data   = df.iloc[:, 14].values

        N = len(da_data)

        # =========================
        # LÍMITES
        # =========================
        PI_180 = np.pi / 180

        lim_da  = (-25 * PI_180,  25 * PI_180)
        lim_de  = (-25 * PI_180,  10 * PI_180)
        lim_dr  = (-30 * PI_180,  30 * PI_180)

        lim_em1 = (0, 1)
        lim_em2 = (0, 1)

        # =========================
        # MATRICES DE ROTACIÓN
        # =========================
        def get_rotation_matrix_rad(psi, theta, phi):

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
                [0, np.cos(roll), -np.sin(roll)],
                [0, np.sin(roll),  np.cos(roll)]
            ])

            return Rz @ Ry @ Rx

        # =========================
        # FIGURA
        # =========================
        fig = plt.figure(figsize=(32, 10))
        fig.patch.set_facecolor('#0d0d0d')

        gs = GridSpec(
            3,
            14,
            figure=fig,
            hspace=0.55,
            wspace=0.45
        )

        col_dark = '#0d0d0d'
        col_grid = '#1e1e1e'
        col_text = '#cccccc'

        def estilo_ax(ax, titulo, color_linea):

            ax.set_facecolor(col_dark)

            ax.tick_params(
                colors=col_text,
                labelsize=7
            )

            for sp in ax.spines.values():
                sp.set_edgecolor('#333333')

            ax.set_title(
                titulo,
                color=color_linea,
                fontsize=8,
                pad=3
            )

            ax.grid(
                True,
                color=col_grid,
                linewidth=0.5
            )

            ax.set_xlim(t_data[0], t_data[-1])

        # =========================
        # SUBPLOTS
        # =========================
        ax_da  = fig.add_subplot(gs[0, 0:2])
        ax_de  = fig.add_subplot(gs[1, 0:2])
        ax_dr  = fig.add_subplot(gs[2, 0:2])

        for ax, titulo, col, data, ylim in zip(
            [ax_da, ax_de, ax_dr],
            [
                "Deflexión Alerón (rad)",
                "Deflexión Elevador (rad)",
                "Deflexión Ruder (rad)"
            ],
            ['#00d4ff', '#ff6b35', '#7fff6b'],
            [da_data, de_data, dr_data],
            [lim_da, lim_de, lim_dr]
        ):

            estilo_ax(ax, titulo, col)

            ax.set_ylim(ylim[0], ylim[1])

            ax.plot(
                t_data,
                data,
                color=col,
                linewidth=0.8,
                alpha=0.3
            )

        # =========================
        # EMPUJE
        # =========================
        ax_em1 = fig.add_subplot(gs[0, 2:4])
        ax_em2 = fig.add_subplot(gs[1, 2:4])
        ax_uvw = fig.add_subplot(gs[2, 2:4])

        for ax, titulo, col, data, ylim in zip(
            [ax_em1, ax_em2],
            ["Empuje Motor 1", "Empuje Motor 2"],
            ['#ff3cac', '#ffe53b'],
            [em1_data, em2_data],
            [lim_em1, lim_em2]
        ):

            estilo_ax(ax, titulo, col)

            ax.set_ylim(ylim[0], ylim[1])

            ax.plot(
                t_data,
                data,
                color=col,
                linewidth=0.8,
                alpha=0.3
            )

        # =========================
        # VELOCIDADES LINEALES
        # =========================
        ax_u = ax_uvw
        ax_v = fig.add_subplot(gs[0, 4:6])
        ax_w = fig.add_subplot(gs[1, 4:6])

        for ax, titulo, col, data in zip(
            [ax_u, ax_v, ax_w],
            ["u (m/s)", "v (m/s)", "w (m/s)"],
            ['#3c78ff', '#ff9f43', '#ee5a24'],
            [u_data, v_data, w_data]
        ):

            estilo_ax(ax, titulo, col)

            if data.min() == data.max():
                ax.set_ylim(data.min()-1, data.max()+1)
            else:
                ax.set_ylim(data.min()-0.02, data.max()+0.02)

            ax.plot(
                t_data,
                data,
                color=col,
                linewidth=0.8,
                alpha=0.3
            )

        # =========================
        # VELOCIDADES ANGULARES
        # =========================
        ax_p = fig.add_subplot(gs[2, 4:6])
        ax_q = fig.add_subplot(gs[0, 6:8])
        ax_r = fig.add_subplot(gs[1, 6:8])

        for ax, titulo, col, data in zip(
            [ax_p, ax_q, ax_r],
            ["p (rad/s)", "q (rad/s)", "r (rad/s)"],
            ['#a29bfe', '#6c5ce7', '#74b9ff'],
            [p_data, q_data, r_data]
        ):

            estilo_ax(ax, titulo, col)

            if data.min() == data.max():
                ax.set_ylim(data.min()-1, data.max()+1)
            else:
                ax.set_ylim(data.min()-0.02, data.max()+0.02)

            ax.plot(
                t_data,
                data,
                color=col,
                linewidth=0.8,
                alpha=0.3
            )

        # =========================
        # ÁNGULOS DE EULER
        # =========================
        ax_phi   = fig.add_subplot(gs[2, 6:8])
        ax_theta = fig.add_subplot(gs[0, 8:10])
        ax_zhi   = fig.add_subplot(gs[1, 8:10])

        for ax, titulo, col, data in zip(
            [ax_phi, ax_theta, ax_zhi],
            ["φ phi (rad)", "θ theta (rad)", "ψ zhi (rad)"],
            ['#fd79a8', '#55efc4', '#ffeaa7'],
            [phi_data, theta_data, zhi_data]
        ):

            estilo_ax(ax, titulo, col)

            if data.min() == data.max():
                ax.set_ylim(data.min()-1, data.max()+1)
            else:
                ax.set_ylim(data.min()-0.02, data.max()+0.02)

            ax.plot(
                t_data,
                data,
                color=col,
                linewidth=0.8,
                alpha=0.3
            )

        # =========================
        # LÍNEAS ANIMADAS
        # =========================
        line_da, = ax_da.plot([], [], color='#00d4ff', linewidth=1.5)
        dot_da,  = ax_da.plot([], [], 'o', color='#00d4ff', ms=5)

        # =========================
        # VISTA 3D
        # =========================
        ax3d = fig.add_subplot(gs[:, 11:], projection='3d')

        ax3d.set_facecolor(col_dark)

        ax3d.xaxis.pane.fill = False
        ax3d.yaxis.pane.fill = False
        ax3d.zaxis.pane.fill = False

        S = 7.0
        lim_3d = S * 3 + 10

        ax3d.set_xlim(-lim_3d, lim_3d)
        ax3d.set_ylim(-lim_3d, lim_3d)
        ax3d.set_zlim(-lim_3d, lim_3d)

        ax3d.set_box_aspect([1, 1, 1])

        ax3d.set_xticks([])
        ax3d.set_yticks([])
        ax3d.set_zticks([])

        # =========================
        # TELEMETRÍA
        # =========================
        fig.canvas.draw()

        pos3d = ax3d.get_position()

        cx  = pos3d.x0 + pos3d.width * 0.5
        top = pos3d.y0 + pos3d.height
        bot = pos3d.y0

        text_vel = fig.text(
            cx,
            top + 0.075,
            "u = 0.000 m/s   v = 0.000 m/s   w = 0.000 m/s",
            ha='center',
            va='bottom',
            fontsize=9,
            color='#74b9ff',
            fontfamily='monospace'
        )

        text_euler = fig.text(
            cx,
            top + 0.040,
            "φ = 0.000 rad   θ = 0.000 rad   ψ = 0.000 rad",
            ha='center',
            va='bottom',
            fontsize=9,
            color='#ffeaa7',
            fontfamily='monospace'
        )

        titulo_3d = fig.text(
            cx,
            top + 0.010,
            "t = 0 s",
            ha='center',
            va='bottom',
            fontsize=10,
            color='#ffffff',
            fontweight='bold'
        )

        text_euler_deg = fig.text(
            cx,
            bot - 0.030,
            "φ = 0.00°   θ = 0.00°   ψ = 0.00°",
            ha='center',
            va='top',
            fontsize=9,
            color='#ffd580',
            fontfamily='monospace'
        )

        # =========================
        # CONFIGURACIÓN ANIMACIÓN
        # =========================
        INTERVAL_MS = 20

        all_lines = [line_da]
        all_dots  = [dot_da]
        all_data  = [da_data]

        def init():

            for line in all_lines:
                line.set_data([], [])

            return []

        def update(frame):

            idx = frame % N

            t_slice = t_data[:idx+1]

            for line, dot, data in zip(
                all_lines,
                all_dots,
                all_data
            ):

                line.set_data(
                    t_slice,
                    data[:idx+1]
                )

                dot.set_data(
                    [t_data[idx]],
                    [data[idx]]
                )

            phi_i   = phi_data[idx]
            theta_i = theta_data[idx]
            zhi_i   = zhi_data[idx]

            ui = u_data[idx]
            vi = v_data[idx]
            wi = w_data[idx]

            R = get_rotation_matrix_rad(
                zhi_i,
                theta_i,
                phi_i
            )

            titulo_3d.set_text(
                f"t = {t_data[idx]:.2f} s"
            )

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

            text_euler_deg.set_text(
                f"φ = {np.degrees(phi_i):+.2f}°   "
                f"θ = {np.degrees(theta_i):+.2f}°   "
                f"ψ = {np.degrees(zhi_i):+.2f}°"
            )

            return []

        ani = animation.FuncAnimation(
            fig,
            update,
            frames=N,
            init_func=init,
            interval=INTERVAL_MS,
            blit=False,
            repeat=True
        )

        plt.show()

    grafic()


main()