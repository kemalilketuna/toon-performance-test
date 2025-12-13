"""
Shared styling configuration for all graphics.
Ensures consistent look across the article.
"""

import matplotlib.pyplot as plt
import matplotlib as mpl

# Color palette
COLORS = {
    "JSON": "#3498db",      # Blue
    "YAML": "#f39c12",      # Amber
    "TOON": "#2ecc71",      # Green
    "accent": "#e74c3c",    # Red (for highlights)
    "neutral": "#95a5a6",   # Gray
    "dark": "#2c3e50",      # Dark blue-gray
    "light": "#ecf0f1",     # Light gray
}

# Font settings
FONT_FAMILY = "sans-serif"
TITLE_SIZE = 14
LABEL_SIZE = 11
TICK_SIZE = 10

def apply_style():
    """Apply consistent style to matplotlib plots."""
    plt.style.use('seaborn-v0_8-whitegrid')
    
    mpl.rcParams['font.family'] = FONT_FAMILY
    mpl.rcParams['font.size'] = TICK_SIZE
    mpl.rcParams['axes.titlesize'] = TITLE_SIZE
    mpl.rcParams['axes.labelsize'] = LABEL_SIZE
    mpl.rcParams['xtick.labelsize'] = TICK_SIZE
    mpl.rcParams['ytick.labelsize'] = TICK_SIZE
    mpl.rcParams['legend.fontsize'] = TICK_SIZE
    mpl.rcParams['figure.titlesize'] = TITLE_SIZE
    mpl.rcParams['axes.spines.top'] = False
    mpl.rcParams['axes.spines.right'] = False
    mpl.rcParams['figure.facecolor'] = 'white'
    mpl.rcParams['axes.facecolor'] = 'white'
    mpl.rcParams['savefig.facecolor'] = 'white'
    mpl.rcParams['savefig.edgecolor'] = 'white'
    mpl.rcParams['savefig.bbox'] = 'tight'
    mpl.rcParams['savefig.dpi'] = 500

def save_figure(fig, name, formats=['png', 'svg']):
    """Save figure in multiple formats."""
    from pathlib import Path
    output_dir = Path(__file__).parent
    
    for fmt in formats:
        path = output_dir / f"{name}.{fmt}"
        fig.savefig(path, format=fmt, bbox_inches='tight', dpi=500)
        print(f"Saved: {path}")

