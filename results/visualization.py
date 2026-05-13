"""Visualization helpers for research outputs."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd


def plot_cumulative_returns(cumret: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    plt.figure(figsize=(12, 6))
    for col in cumret.columns:
        plt.plot(cumret.index, cumret[col], label=col, alpha=0.8)
    plt.title("Factor Long-Short Cumulative Returns")
    plt.xlabel("Date")
    plt.ylabel("Cumulative Return")
    plt.legend(ncol=2, fontsize=8)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()


def plot_corr_heatmap(corr: pd.DataFrame, output_path: str | Path) -> None:
    output_path = Path(output_path)
    plt.figure(figsize=(10, 8))
    sns.heatmap(corr, cmap="coolwarm", center=0, annot=False)
    plt.title("Factor Correlation Matrix")
    plt.tight_layout()
    plt.savefig(output_path, dpi=180)
    plt.close()
