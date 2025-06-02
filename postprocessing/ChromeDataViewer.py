import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.ticker as ticker  # Add this to your imports


class DepthPlotterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Counts vs. Depth Plotter")
        self.root.geometry("300x150")

        self.label = tk.Label(root, text="Select a CSV file:")
        self.label.pack(pady=10)

        self.open_button = tk.Button(root, text="Open CSV", command=self.open_csv)
        self.open_button.pack()

    def open_csv(self):
        filepath = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not filepath:
            return

        try:
            df = pd.read_csv(filepath)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to read file:\n{e}")
            return

        # Ensure required columns exist
        if 'Depth(m)' not in df.columns or '# Counts' not in df.columns:
            messagebox.showerror("Error", "CSV must contain 'Depth(m)' and '# Counts' columns.")
            return

        self.plot_data(df)

    def plot_data(self, df):
        plt.figure(figsize=(4, 8))

        x = df['# Counts']
        y = df['Depth(m)']

        plt.plot(x, y, color='blue', label='Counts vs. Depth')

        # Fill beneath the curve conditionally
        # Create masks for below and above threshold
        below_mask = x < 30000
        above_mask = x >= 30000

        # Fill where counts < 30000 (brown)
        plt.fill_betweenx(y, 0, x, where=below_mask, color='saddlebrown', alpha=0.5)

        # Fill where counts >= 30000 (white) - white fill is basically no fill,
        # but we can fill with white to "overwrite" if needed
        plt.fill_betweenx(y, 0, x, where=above_mask, color='white', alpha=0.5)

        plt.xlabel("ADC Counts")
        plt.ylabel("Depth (m)")
        plt.title("Counts vs. Depth")
        plt.grid(True)

        plt.gca().invert_yaxis()  # Make depth increase downward

        ax = plt.gca()
        # ax.invert_yaxis()

        # Minor ticks every 0.05 m
        minor_locator = ticker.MultipleLocator(0.10)
        ax.yaxis.set_minor_locator(minor_locator)

        # Major ticks every 0.25 m with labels
        major_locator = ticker.MultipleLocator(0.20)
        ax.yaxis.set_major_locator(major_locator)

        # Optional: smaller ticks for minor ones
        ax.tick_params(axis='y', which='minor', length=4)
        ax.tick_params(axis='y', which='major', length=8)

        plt.tight_layout()
        plt.subplots_adjust(left=0.2, right=0.95)  # Adds margin so y-labels aren't cut off
        plt.show()

if __name__ == "__main__":
    root = tk.Tk()
    app = DepthPlotterApp(root)
    root.mainloop()
