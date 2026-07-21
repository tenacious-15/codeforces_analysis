import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server/script usage
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import logging
from pathlib import Path
from typing import Dict
from config import CHARTS_DIR, ACCENT_COLOR, HIGHLIGHT_COLOR, FAILURE_COLOR, SUCCESS_COLOR

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class CodeforcesVisualizer:
    def __init__(self, output_dir: Path = CHARTS_DIR):
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)
        # Modern styling
        plt.style.use('dark_background')
        plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
        plt.rcParams['axes.edgecolor'] = '#444444'
        plt.rcParams['axes.linewidth'] = 0.8
        plt.rcParams['grid.color'] = '#333333'
        plt.rcParams['grid.linestyle'] = '--'

    def plot_rating_progression(self, handle: str, df: pd.DataFrame) -> Path:
        """Plot contest rating progression curve with milestone bands."""
        fig, ax = plt.subplots(figsize=(12, 6))

        if df.empty:
            ax.text(0.5, 0.5, "No Contest Data Available", ha='center', va='center', fontsize=14, color='#888888')
            out_path = self.output_dir / "rating_progression.png"
            plt.savefig(out_path, dpi=200, bbox_inches='tight')
            plt.close()
            return out_path

        # Codeforces Rating Tiers
        tiers = [
            (0, 1199, 'Gray (Newbie)', '#CCCCCC'),
            (1200, 1399, 'Green (Pupil)', '#77FF77'),
            (1400, 1599, 'Cyan (Specialist)', '#77DDDD'),
            (1600, 1899, 'Blue (Expert)', '#AA88FF'),
            (1900, 2099, 'Purple (CM)', '#FF88FF'),
            (2100, 2299, 'Orange (Master)', '#FFBB55'),
            (2300, 2399, 'IMaster', '#FFCC00'),
            (2400, 4000, 'Red (GM+)', '#FF5555')
        ]

        # Draw tier bands in background
        max_val = max(df['new_rating'].max() + 100, 1600)
        for min_r, max_r, label, col in tiers:
            if min_r <= max_val:
                ax.axhspan(min_r, min(max_r, max_val + 200), color=col, alpha=0.08)

        # Plot rating line
        ax.plot(df['contest_num'], df['new_rating'], color=ACCENT_COLOR, marker='o', linewidth=2.5, markersize=5, label='Rating')
        
        # Highlight Max Rating
        max_row = df.loc[df['new_rating'].idxmax()]
        ax.scatter([max_row['contest_num']], [max_row['new_rating']], color=HIGHLIGHT_COLOR, s=120, zorder=5, label=f"Max: {max_row['new_rating']}")
        ax.annotate(f"Peak: {max_row['new_rating']}\n({max_row['contest_name'][:20]})", 
                    (max_row['contest_num'], max_row['new_rating']),
                    textcoords="offset points", xytext=(0, 12), ha='center',
                    fontsize=9, color=HIGHLIGHT_COLOR, weight='bold',
                    arrowprops=dict(arrowstyle="->", color=HIGHLIGHT_COLOR, lw=1))

        ax.set_title(f"Codeforces Rating History — {handle}", fontsize=14, pad=15, weight='bold', color='#FFFFFF')
        ax.set_xlabel("Contest Index", fontsize=11, labelpad=10)
        ax.set_ylabel("Rating", fontsize=11, labelpad=10)
        ax.grid(True, alpha=0.4)
        ax.legend(loc='upper left', frameon=True, facecolor='#222222', edgecolor='#444444')

        out_path = self.output_dir / "rating_progression.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=200, bbox_inches='tight')
        plt.close()
        return out_path

    def plot_topic_strength(self, handle: str, df: pd.DataFrame) -> Path:
        """Plot top solved topics and accuracy percentage."""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

        if df.empty:
            ax1.text(0.5, 0.5, "No Topic Data Available", ha='center', va='center', fontsize=14, color='#888888')
            out_path = self.output_dir / "topic_accuracy_heatmap.png"
            plt.savefig(out_path, dpi=200, bbox_inches='tight')
            plt.close()
            return out_path

        top_df = df.head(12).sort_values('unique_solved', ascending=True)

        # Bar plot 1: Solved Problems Count
        ax1.barh(top_df['tag'], top_df['unique_solved'], color=ACCENT_COLOR, alpha=0.85)
        ax1.set_title("Unique Problems Solved by Tag", fontsize=12, pad=10, weight='bold')
        ax1.set_xlabel("Unique Solved Count", fontsize=10)
        ax1.grid(True, axis='x', alpha=0.3)

        for i, val in enumerate(top_df['unique_solved']):
            ax1.text(val + 0.5, i, str(val), va='center', fontsize=9, color='#DDDDDD')

        # Bar plot 2: Accuracy Percentage
        colors = [SUCCESS_COLOR if x >= 60 else HIGHLIGHT_COLOR if x >= 40 else FAILURE_COLOR for x in top_df['accuracy_pct']]
        ax2.barh(top_df['tag'], top_df['accuracy_pct'], color=colors, alpha=0.85)
        ax2.set_title("Submission Accuracy (%) by Tag", fontsize=12, pad=10, weight='bold')
        ax2.set_xlabel("Accuracy %", fontsize=10)
        ax2.set_xlim(0, 100)
        ax2.grid(True, axis='x', alpha=0.3)

        for i, val in enumerate(top_df['accuracy_pct']):
            ax2.text(val + 1, i, f"{val}%", va='center', fontsize=9, color='#DDDDDD')

        fig.suptitle(f"Topic Performance Analysis — {handle}", fontsize=14, y=1.02, weight='bold')
        
        out_path = self.output_dir / "topic_accuracy_heatmap.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=200, bbox_inches='tight')
        plt.close()
        return out_path

    def plot_difficulty_vs_success(self, handle: str, df: pd.DataFrame) -> Path:
        """Plot problem difficulty distribution and success rate."""
        fig, ax1 = plt.subplots(figsize=(11, 5.5))

        if df.empty or df['unique_problems'].sum() == 0:
            ax1.text(0.5, 0.5, "No Rating Data Available", ha='center', va='center', fontsize=14, color='#888888')
            out_path = self.output_dir / "difficulty_vs_success.png"
            plt.savefig(out_path, dpi=200, bbox_inches='tight')
            plt.close()
            return out_path

        # Bar chart for Unique Problems Solved
        x = range(len(df))
        bars = ax1.bar(x, df['unique_solved'], color=ACCENT_COLOR, alpha=0.75, width=0.5, label='Unique Solved')
        ax1.set_xticks(x)
        ax1.set_xticklabels(df['rating_bin'], rotation=25, ha='right', fontsize=9)
        ax1.set_xlabel("Problem Difficulty Rating Range", fontsize=11, labelpad=8)
        ax1.set_ylabel("Unique Problems Solved", fontsize=11, color=ACCENT_COLOR, labelpad=8)
        ax1.tick_params(axis='y', labelcolor=ACCENT_COLOR)
        ax1.grid(True, axis='y', alpha=0.3)

        # Line chart for Accuracy Rate %
        ax2 = ax1.twinx()
        ax2.plot(x, df['ac_rate_pct'], color=HIGHLIGHT_COLOR, marker='s', linewidth=2, markersize=6, label='AC Rate %')
        ax2.set_ylabel("Accuracy Rate (%)", fontsize=11, color=HIGHLIGHT_COLOR, labelpad=8)
        ax2.tick_params(axis='y', labelcolor=HIGHLIGHT_COLOR)
        ax2.set_ylim(0, 105)

        # Add values on top of bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5, f'{int(height)}',
                         ha='center', va='bottom', fontsize=8, color='#EEEEEE')

        plt.title(f"Difficulty Range vs. Success Rate — {handle}", fontsize=13, pad=15, weight='bold')
        
        out_path = self.output_dir / "difficulty_vs_success.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=200, bbox_inches='tight')
        plt.close()
        return out_path

    def plot_activity_time_pattern(self, handle: str, time_data: Dict[str, pd.DataFrame]) -> Path:
        """Plot submission activity by Hour of Day and Day of Week."""
        dow_df = time_data.get("day_of_week", pd.DataFrame())
        hour_df = time_data.get("hour_of_day", pd.DataFrame())

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5))

        # Day of Week Plot
        if not dow_df.empty:
            ax1.bar(dow_df['day_of_week'].astype(str), dow_df['total_submissions'], color=ACCENT_COLOR, alpha=0.8)
            ax1.set_title("Submissions by Day of Week", fontsize=12, pad=10, weight='bold')
            ax1.set_xlabel("Day of Week", fontsize=10)
            ax1.set_ylabel("Submissions Count", fontsize=10)
            ax1.tick_params(axis='x', rotation=30)
            ax1.grid(True, axis='y', alpha=0.3)
        else:
            ax1.text(0.5, 0.5, "No Day Data", ha='center', va='center')

        # Hour of Day Plot
        if not hour_df.empty:
            ax2.plot(hour_df['hour_of_day'], hour_df['total_submissions'], color=HIGHLIGHT_COLOR, marker='o', linewidth=2)
            ax2.fill_between(hour_df['hour_of_day'], hour_df['total_submissions'], color=HIGHLIGHT_COLOR, alpha=0.2)
            ax2.set_title("Submissions by Hour of Day (UTC)", fontsize=12, pad=10, weight='bold')
            ax2.set_xlabel("Hour of Day (0-23)", fontsize=10)
            ax2.set_ylabel("Submissions Count", fontsize=10)
            ax2.set_xticks(range(0, 24, 2))
            ax2.grid(True, alpha=0.3)
        else:
            ax2.text(0.5, 0.5, "No Hour Data", ha='center', va='center')

        fig.suptitle(f"Submission Activity Patterns — {handle}", fontsize=14, y=1.03, weight='bold')
        
        out_path = self.output_dir / "activity_time_pattern.png"
        plt.tight_layout()
        plt.savefig(out_path, dpi=200, bbox_inches='tight')
        plt.close()
        return out_path
