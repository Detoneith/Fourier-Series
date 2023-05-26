import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# Paramètres du dessin
slider_value = 2  # Valeur initiale du slider (nb de cercles)
# temps de départ de l'animation est défini à zéro
time = 0
# stock les valeurs de l'ordonnée (y) des points de la courbe tracée dans l'animation
wave = []

# Définition des paramètres du dessin

# Configuration de la figure
# Création de la figure avec deux sous-graphiques (ax1 et ax2) et configuration des limites
'''fig: C'est l'objet de la figure principale qui va contenir les sous-graphiques.
(ax1, ax2): C'est une déconstruction de la sortie de plt.subplots(1, 2), qui retourne deux axes dans une liste.
plt.subplots(1, 2): Cette fonction crée une grille de sous-graphiques avec 1 ligne et 2 colonnes.
figsize=(10, 4): Cela définit la taille de la figure à une largeur de 10 pouces et une hauteur de 4 pouces.
gridspec_kw={'height_ratios': [1]}: C'est un dictionnaire d'arguments optionnels pour la spécification de la grille.
Ici, on utilise height_ratios pour spécifier que la hauteur des sous-graphiques doit être répartie de manière égale, donc [1]
indique une hauteur égale pour les deux axes.'''

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), gridspec_kw={'height_ratios': [1]})
ax1.set_xlim(-100, 100)
ax1.set_ylim(-100, 100)
ax1.set_aspect('equal')  # Garantit l'aspect ratio égal pour les cercles
#ax1.autoscale(enable=False)  # Désactive le redimensionnement automatique
ax2.set_xlim(0, 250)
ax2.set_ylim(-200, 200)


# Création des objets graphiques pour les cercles, la ligne et la courbe
circles = []
# trace une ligne en utilisant les coordonnées x et y
line, = ax2.plot([], [], 'c-')
#curve, = ax2.plot([], [], 'c-')


# Fonction d'initialisation pour chaque frame de l'animation
def init():
    # réinitialiser les objets graphiques à leur état initial avant de commencer l'animation.
    # suprime les cercles de la ax1
    for circle in circles:
        circle.remove()
    # reinitialisation de la liste des circles
    circles.clear()
    # vide les données de la courbe line
    line.set_data([], [])
    #curve.set_data([], [])
    ax1.set_xlim(-100, 100)  # Fixer les limites x de la fenêtre
    ax1.set_ylim(-100, 100)  # Fixer les limites y de la fenêtre
    return circles, line, #curve


# Fonction d'animation
def animate(frame):
    # variables globalespartagées et modifiées à l'extérieur de la fonction animate
    global time, wave

    ax1.cla()  # Effacer le dessin précédent pour tracer les cercles

    ax1.set_xlim(-200, 200)  # Fixer les limites x de la fenêtre
    ax1.set_ylim(-200, 200)  # Fixer les limites y de la fenêtre

    #initialisation de x et y
    x = 0
    y = 0

    # parcourt les valeurs de i allant de 0 à slider_value-1.
    # Cela permet de tracer plusieurs cercles en fonction de la valeur du slider.
    for i in range(slider_value):
        #stocke les coordonnées du cercle précédent, afin de tracer une ligne reliant le cercle précédent et le cercle actuel.
        prevx = x
        prevy = y

        # détermine le nombre d'ondes du cercle (un cercle complet = 2π).
        n = i * 2 + 1
        # radius est calculée en fonction de n pour déterminer le rayon du cercle
        # formule utilisée: approximation de la série de Fourier pour obtenir des cercles harmoniques
        radius = 75 * (4 / (n * np.pi))
        # x et y sont mises à jour en ajoutant les déplacements calculés en fonction du temps time et des propriétés du cercle (rayon, fréquence).
        x += radius * np.cos(n * time)
        y += radius * np.sin(n * time)
        
        # Un objet circle est créé avec les coordonnées prevx et prevy, le rayon radius, et les paramètres de couleur
        # et est ajouté à la figure ax1 avec add_patch
        circle = plt.Circle((prevx, prevy), radius, color='blue', ec='black', alpha=0.5)
        ax1.add_patch(circle)
        # ajoute a la liste des cercles
        circles.append(circle)

        # trace une ligne rouge 'r-' reliant les coordonnées (prevx, prevy) et (x, y). Cela représente le mouvement du point
        # sur le cercle.
        ax1.plot([prevx, x], [prevy, y], 'r-')

    # Tracer le trait horizontal
    ax1.plot([x, 200], [y, y], 'black')

    # Fonction de mise à jour pour chaque frame de l'animation
    # insère la valeur y au début de la liste wave
    # sert a créer une trace de la courbe au fil du temps
    wave.insert(0, y)
    # vérifie si la longueur de la liste wave dépasse 250 éléments. Si c'est le cas, cela signifie que la liste contient
    # plus de 250 éléments et on doit donc enlever le dernier élément de la liste en utilisant wave.pop(). Cela maintient 
    # la taille de la liste à 250 éléments maximum, ce qui limite la longueur de la trace de la courbe.
    if len(wave) > 250:
        wave.pop()

    #met à jour les données de la ligne line avec les coordonnées x et y pour représenter la trace de la courbe. La liste
    # range(len(wave)) fournit les valeurs x correspondantes, tandis que la liste wave fournit les valeurs y correspondantes.
    line.set_data(range(len(wave)), wave)
    #curve.set_data([x - 200, 0], [y, wave[0]])

    # incrémente la variable time de 0.05 à chaque frame de l'animation. Cela permet de faire évoluer le temps et de créer
    # l'illusion de mouvement dans les cercles tracés.
    time += 0.05


# # Création de l'objet d'animation
ani = FuncAnimation(fig, animate, init_func=init, frames=100, interval=50)

# Affichage de la figure animée
plt.show()
