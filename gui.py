import os
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
from numpy import interp
from math import tau
from scipy.integrate import quad

import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename


class GIFGeneratorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("GIF Generator")
        self.canvas = tk.Canvas(self.root, width=800, height=400)
        self.canvas.pack(side=tk.LEFT)

        self.image_label = tk.Label(self.root, text="No image selected")
        self.image_label.pack(pady=10)

        self.open_button = tk.Button(self.root, text="Open Image", command=self.open_image)
        self.open_button.pack(pady=10)

        self.generate_button = tk.Button(self.root, text="Generate GIF", command=self.generate_gif)
        self.generate_button.pack(pady=10)

        self.gif_label = tk.Label(self.root, text="No GIF generated")
        self.gif_label.pack(pady=10)


        self.root.mainloop()

    def open_image(self):
        image_path = askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")])
        if image_path:
            self.image_label.config(text="Image: " + image_path)
            self.image = Image.open(image_path)
            self.image.thumbnail((400, 400))
            self.image_tk = ImageTk.PhotoImage(self.image)
            self.canvas.create_image(0, 0, anchor="nw", image=self.image_tk)

    def generate_gif(self):
        if not hasattr(self, 'image'):
            self.gif_label.config(text="No image selected")
            return

        gif_generator = GIFGenerator()
        gif_path = asksaveasfilename(filetypes=[("GIF files", "*.gif")])
        if gif_path:
            gif_generator.generate_gif_ask_user(self.image_label.cget("text")[7:])
            self.gif_label.config(text="GIF: " + gif_path)

            # Open the generated GIF
            self.open_generated_gif(gif_generator.gif_file)
            '''gif = Image.open(gif_generator.gif_file)
            gif.thumbnail((400, 400))
            gif_tk = ImageTk.PhotoImage(gif)
            self.canvas.create_image(400, 0, anchor="nw", image=gif_tk)'''
    
    '''def open_generated_gif(self, gif_file):
        gif = Image.open(gif_file)
        gif.thumbnail((400, 400))
        gif_tk = ImageTk.PhotoImage(gif)
        self.canvas.create_image(400, 0, anchor="nw", image=gif_tk)'''
    
    def open_generated_gif(self, gif_file):
        gif = Image.open(gif_file)
        gif.thumbnail((400, 400))
        gif_tk = ImageTk.PhotoImage(gif)

        # Créer une nouvelle fenêtre pour afficher le GIF
        gif_window = tk.Toplevel(self.root)
        gif_window.title("Generated GIF")
        gif_canvas = tk.Canvas(gif_window, width=gif.width, height=gif.height)
        gif_canvas.pack()
        gif_canvas.create_image(0, 0, anchor="nw", image=gif_tk)

        # Mettre à jour la fenêtre principale pour montrer le chemin du GIF généré
        self.gif_label.config(text="GIF: " + gif_file)


    


class GIFGenerator:
    def __init__(self):
        fig_size = (6, 6)  # Specify the desired figure size (width, height) in inches
        self.fig, self.ax = plt.subplots(figsize=fig_size)
        self.ax.set_aspect('equal', 'datalim')

    def create_close_loop(self, image_name, level=[200]):
        im = Image.open(image_name).convert('L')
        im_array = np.array(im)
        contour_plot = plt.contour(im_array, levels=level, colors='orange', origin='image')
        contour_path = contour_plot.collections[0].get_paths()[0]
        x_table, y_table = contour_path.vertices[:, 0], contour_path.vertices[:, 1]
        time_table = np.linspace(0, tau, len(x_table))

        x_table = x_table - min(x_table)
        y_table = y_table - min(y_table)
        x_table = x_table - np.max(x_table) / 2
        y_table = y_table - np.max(y_table) / 2

        return time_table, x_table, y_table

    def f(self, t, time_table, x_table, y_table):
        return interp(t, time_table, x_table) + 1j * interp(t, time_table, y_table)

    def DFT(self, t, coef_list, order=5):
        kernel = np.array([np.exp(-n * 1j * t) for n in range(-order, order + 1)])
        series = np.sum((coef_list[:, 0] + 1j * coef_list[:, 1]) * kernel[:])
        return np.real(series), np.imag(series)

    def coef_list(self, time_table, x_table, y_table, order=5):
        coef_list = []
        for n in range(-order, order + 1):
            real_coef = quad(lambda t: np.real(self.f(t, time_table, x_table, y_table) * np.exp(-n * 1j * t)), 0, tau,
                             limit=100, full_output=1)[0] / tau
            imag_coef = quad(lambda t: np.imag(self.f(t, time_table, x_table, y_table) * np.exp(-n * 1j * t)), 0, tau,
                             limit=100, full_output=1)[0] / tau
            coef_list.append([real_coef, imag_coef])
        return np.array(coef_list)

    def visualize(self, x_DFT, y_DFT, coef, order, space, fig_lim):
        self.ax.clear()
        lim = max(fig_lim)
        self.ax.set_xlim([-lim, lim])
        self.ax.set_ylim([-lim, lim])
        self.ax.set_aspect('equal')

        line = self.ax.plot([], [], 'k-', linewidth=2)[0]
        radius = [self.ax.plot([], [], 'r-', linewidth=0.5, marker='o', markersize=1)[0] for _ in range(2 * order + 1)]
        circles = [self.ax.plot([], [], 'r-', linewidth=0.5)[0] for _ in range(2 * order + 1)]

        def update_c(c, t):
            new_c = []
            for i, j in enumerate(range(-order, order + 1)):
                dtheta = -j * t
                ct, st = np.cos(dtheta), np.sin(dtheta)
                v = [ct * c[i][0] - st * c[i][1], st * c[i][0] + ct * c[i][1]]
                new_c.append(v)
            return np.array(new_c)

        def sort_velocity(order):
            idx = []
            for i in range(1, order + 1):
                idx.extend([order + i, order - i])
            return idx

        def animate(i):
            line.set_data(x_DFT[:i], y_DFT[:i])
            r = [np.linalg.norm(coef[j]) for j in range(len(coef))]
            pos = coef[order]
            c = update_c(coef, i / len(space) * tau)
            idx = sort_velocity(order)
            for j, rad, circle in zip(idx, radius, circles):
                new_pos = pos + c[j]
                rad.set_data([pos[0], new_pos[0]], [pos[1], new_pos[1]])
                theta = np.linspace(0, tau, 50)
                x, y = r[j] * np.cos(theta) + pos[0], r[j] * np.sin(theta) + pos[1]
                circle.set_data(x, y)
                pos = new_pos

        ani = animation.FuncAnimation(self.fig, animate, frames=len(space), interval=5)

        return ani

    def generate_gif_ask_user(self, image_name):
        asset_folder = os.path.join(os.path.dirname('Interface'), 'assets')
        os.makedirs(asset_folder, exist_ok=True)

        base_name = os.path.splitext(os.path.basename(image_name))[0]
        default_save_path = os.path.join(asset_folder, base_name + '.gif')

        save_path = asksaveasfilename(
            initialdir=asset_folder,
            initialfile=base_name + '.gif',
            defaultextension='.gif',
            filetypes=[('GIF files', '*.gif'), ('All files', '*.*')]
        )

        if not save_path:
            return  # L'utilisateur a annulé la sélection du fichier

        self.gif_file = save_path

        time_table, x_table, y_table = self.create_close_loop(image_name)
        order = 30
        coef = self.coef_list(time_table, x_table, y_table, order)
        space = np.linspace(0, tau, 300)
        x_DFT = [self.DFT(t, coef, order)[0] for t in space]
        y_DFT = [self.DFT(t, coef, order)[1] for t in space]

        xmin, xmax = min(x_DFT), max(x_DFT)
        ymin, ymax = min(y_DFT), max(y_DFT)

        anim = self.visualize(x_DFT, y_DFT, coef, order, space, [xmin, xmax, ymin, ymax])
        anim.save(self.gif_file, writer='pillow', fps=60)


if __name__ == '__main__':
    gif_generator_gui = GIFGeneratorGUI()
