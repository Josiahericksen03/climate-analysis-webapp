import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend

from typing import List
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

class ClimateVisualizer:
    def __init__(self):
        plt.style.use('default')
        sns.set_theme()

    def plot_temperature_with_predictions_and_anomalies(self, dates, temperatures, predictions, anomalies, title, output_path=None):
        plt.figure(figsize=(14, 6))

        # Actual data
        plt.plot(dates, temperatures, label="Actual", color="blue")

        # Predicted data
        if len(predictions) > 0:
            future_dates = pd.date_range(start=dates[-1], periods=len(predictions) + 1, freq='D')[1:]
            plt.plot(future_dates, predictions, label="Predicted", color="red", linestyle="--", linewidth=2)

        # Anomalies
        if len(anomalies) > 0:
            anomaly_dates = [d for d, a in zip(dates, anomalies) if a]
            anomaly_temps = [t for t, a in zip(temperatures, anomalies) if a]
            if len(anomaly_dates) > 0:
                plt.scatter(anomaly_dates, anomaly_temps, color="orange", label="Anomalies", zorder=5)

        plt.title(title)
        plt.xlabel("Date")
        plt.ylabel("Temperature (°F)")
        plt.xticks(rotation=45)
        plt.legend()
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')  # Reduced DPI for memory
        else:
            safe_title = title.lower().replace(" ", "_").replace(",", "").replace("/", "_")
            plt.savefig(f"temperature_analysis_{safe_title}.png", dpi=150, bbox_inches='tight')  # Reduced DPI for memory
        plt.close('all')  # Close all figures to free memory

    def plot_cluster_summary(self, station_names: List[str], cluster_ids: List[int], output_path=None) -> None:
        import matplotlib.pyplot as plt
        import seaborn as sns

        plt.figure(figsize=(12, 8))
        
        # Create a DataFrame for better plotting
        df = pd.DataFrame({
            'Station': station_names,
            'Cluster': cluster_ids
        })
        
        # Create a scatter plot instead of bar plot for better visualization
        colors = ['#ff7f0e' if c == 0 else '#1f77b4' for c in cluster_ids]  # Orange for cluster 0, Blue for cluster 1
        
        plt.scatter(range(len(station_names)), cluster_ids, c=colors, s=200, alpha=0.7)
        
        # Add station names as labels
        for i, station in enumerate(station_names):
            plt.annotate(station, (i, cluster_ids[i]), xytext=(0, 10), 
                        textcoords='offset points', ha='center', fontsize=10)
        
        plt.title("Climate Clusters by Station", fontsize=16, fontweight='bold')
        plt.ylabel("Cluster ID", fontsize=12)
        plt.xlabel("Weather Stations", fontsize=12)
        plt.ylim(-0.5, 1.5)
        plt.xticks([])  # Remove x-axis ticks since we have annotations
        
        # Add cluster legend
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#ff7f0e', alpha=0.7, label='Cluster 0'),
            Patch(facecolor='#1f77b4', alpha=0.7, label='Cluster 1')
        ]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')  # Reduced DPI for memory
        else:
            plt.savefig("climate_clusters.png", dpi=150, bbox_inches='tight')  # Reduced DPI for memory
        plt.close('all')  # Close all figures to free memory

    def plot_temperature_heatmap(self, data: pd.DataFrame, regions: List[str] = None, times: List[str] = None, title: str = "Average Yearly Temperature by Station", output_path=None):
        """
        Create a heatmap of temperature data.

        Args:
            data (pd.DataFrame): Pivoted DataFrame with stations as rows and years as columns
            regions (List[str]): List of station names (row labels)
            times (List[str]): List of years (column labels)
            title (str): Title of the plot
            output_path (str): Path to save the plot
        """
        plt.figure(figsize=(15, 6))
        sns.heatmap(data, annot=True, cmap='coolwarm', fmt=".1f", cbar_kws={'label': 'Temperature (°F)'})
        plt.title(title)
        plt.xlabel("Year")
        plt.ylabel("Station")
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=150, bbox_inches='tight')  # Reduced DPI for memory
        else:
            plt.savefig("temperature_heatmap.png", dpi=150, bbox_inches='tight')  # Reduced DPI for memory
        plt.close('all')  # Close all figures to free memory
