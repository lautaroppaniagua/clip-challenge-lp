"""
clip_style.py
Estilo matplotlib con la identidad visual de Clip (naranja como acento único,
grises neutros como contexto). Pensado para entregables serios/fintech,
priorizando interpretabilidad por sobre decoracion.

Uso basico:
    import clip_style as cs
    cs.apply()

    fig, ax = plt.subplots()
    ax.bar(meses, valores, color=cs.NARANJA)
    cs.style_axes(ax)

Uso con foco/contexto (recomendado para comparar 1 serie vs benchmark):
    colors = cs.emphasis_colors(n=6, highlight_idx=5)
    ax.bar(meses, valores, color=colors)
"""

import matplotlib.pyplot as plt
import matplotlib as mpl
from matplotlib.colors import LinearSegmentedColormap

# --------------------------------------------------------------------------
# Paleta base
# --------------------------------------------------------------------------
NARANJA          = "#FF5722"   # primario / foco / hallazgo
NARANJA_OSCURO   = "#D6480F"   # texto sobre fondo naranja claro, hover, enfasis fuerte
NARANJA_MEDIO    = "#FF8A5C"   # variante media, splits dentro de la misma categoria
NARANJA_CLARO    = "#FFB088"   # fills de area, variantes claras
GRIS_CARBON      = "#2B2B2B"   # texto principal, titulos
GRIS_NEUTRO      = "#8A8A85"   # contexto, benchmark, series secundarias
GRIS_CLARO       = "#D3D1C7"   # gridlines, bordes suaves
FONDO_SUAVE      = "#F4F3EF"   # fondo de secciones (no del canvas del chart)
BLANCO           = "#FCFCFB"

# Rampa secuencial de un solo hue (naranja) para heatmaps / magnitud
_NARANJA_RAMP = [BLANCO, NARANJA_CLARO, NARANJA_MEDIO, NARANJA, NARANJA_OSCURO]
CLIP_CMAP = LinearSegmentedColormap.from_list("clip_naranja", _NARANJA_RAMP)

# Paleta categorica de respaldo cuando de verdad hacen falta >1 series
# (usar con moderacion — preferir siempre foco+contexto en vez de esto)
CATEGORICA = [NARANJA, GRIS_NEUTRO, NARANJA_CLARO, GRIS_CARBON, NARANJA_OSCURO]


def apply():
    """Aplica el estilo Clip como rcParams globales de matplotlib."""
    mpl.rcParams.update({
        # Tipografia
        "font.family": "sans-serif",
        "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
        "font.size": 11,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "axes.labelsize": 11,
        "axes.labelcolor": GRIS_CARBON,

        # Colores generales
        "text.color": GRIS_CARBON,
        "axes.edgecolor": GRIS_CLARO,
        "axes.facecolor": BLANCO,
        "figure.facecolor": BLANCO,
        "savefig.facecolor": BLANCO,

        # Ejes: sobrios, sin recuadro completo
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": True,
        "axes.spines.bottom": True,
        "axes.linewidth": 0.8,

        # Grillas: tenues, nunca compiten con el dato
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.color": GRIS_CLARO,
        "grid.linewidth": 0.6,
        "grid.alpha": 0.7,
        "axes.axisbelow": True,

        # Ticks
        "xtick.color": GRIS_NEUTRO,
        "ytick.color": GRIS_NEUTRO,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,

        # Ciclo de color por defecto (por si no se especifica color explicito)
        "axes.prop_cycle": mpl.cycler(color=CATEGORICA),

        # Leyenda
        "legend.frameon": False,
        "legend.fontsize": 10,

        # Lineas
        "lines.linewidth": 2,
        "lines.solid_capstyle": "round",

        # Barras: sin borde, para look plano
        "patch.edgecolor": "none",
        "patch.linewidth": 0,

        "figure.dpi": 110,
        "savefig.dpi": 150,
    })


def style_axes(ax, grid_axis="y"):
    """Aplica retoques finos a un Axes ya creado (por si no se uso apply())."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color(GRIS_CLARO)
    ax.spines["bottom"].set_color(GRIS_CLARO)
    ax.tick_params(colors=GRIS_NEUTRO)
    ax.grid(axis=grid_axis, color=GRIS_CLARO, linewidth=0.6, alpha=0.7)
    ax.set_axisbelow(True)
    return ax


def emphasis_colors(n, highlight_idx=None, highlight_idxs=None):
    """
    Devuelve una lista de n colores donde solo el/los indices resaltados
    van en naranja y el resto en gris neutro. Patron recomendado para
    'esta barra/categoria es la que importa, el resto es contexto'.

    highlight_idx: un solo indice a resaltar
    highlight_idxs: lista de indices a resaltar (alternativa a highlight_idx)
    """
    idxs = set(highlight_idxs) if highlight_idxs is not None else {highlight_idx}
    return [NARANJA if i in idxs else GRIS_NEUTRO for i in range(n)]


def add_value_labels(ax, fmt="{:.0f}", color=None, fontsize=9):
    """Agrega etiquetas de valor arriba de cada barra (bar charts)."""
    color = color or GRIS_CARBON
    for container in ax.containers:
        ax.bar_label(container, fmt=fmt, color=color, fontsize=fontsize, padding=2)