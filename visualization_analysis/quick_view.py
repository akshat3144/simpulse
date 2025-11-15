"""
Quick viewer to display key validation plots
Opens the most important plots to verify simulation correctness
"""

from PIL import Image
import matplotlib.pyplot as plt
from pathlib import Path

plots_dir = Path(__file__).parent / "plots"

# Key plots to verify simulation
key_plots = [
    ("1_track_position.png", "Track Position - Should show 2D movement"),
    ("2_speed_profiles.png", "Speed Profiles - Should vary in corners"),
    ("3_steering_analysis.png", "Steering - Should have non-zero angles"),
    ("10_dashboard.png", "Dashboard - Overall view")
]

print("\n" + "="*60)
print("OPENING KEY VALIDATION PLOTS")
print("="*60)

for filename, description in key_plots:
    filepath = plots_dir / filename
    if filepath.exists():
        print(f"\n✓ {description}")
        img = Image.open(filepath)
        plt.figure(figsize=(16, 10))
        plt.imshow(img)
        plt.axis('off')
        plt.title(description, fontsize=14, fontweight='bold', pad=20)
        plt.tight_layout()
        
plt.show()

print("\n" + "="*60)
print("Review complete!")
print("="*60)
print("\nFor detailed statistics, see: plots/race_statistics.txt")
print("For all plots, check: plots/ directory")
