import os
import numpy as np
import pandas as pd
import pytest
from src.visualizer import ClimateVisualizer


@pytest.fixture
def visualizer():
    return ClimateVisualizer()


def test_plot_temperature_with_predictions_and_anomalies(tmp_path):
    visualizer = ClimateVisualizer()
    dates = pd.date_range(start="2023-01-01", periods=100).to_list()
    temperatures = np.random.normal(20, 5, 100).tolist()
    predictions = np.random.normal(22, 4, 30).tolist()
    anomalies = [False] * 95 + [True, True, False, True, False]

    # Temporarily change working directory
    cwd = os.getcwd()
    os.chdir(tmp_path)

    visualizer.plot_temperature_with_predictions_and_anomalies(
        dates=dates,
        temperatures=temperatures,
        predictions=predictions,
        anomalies=anomalies,
        title="Test Temperature Plot"
    )

    expected_file = tmp_path / "temperature_analysis_test_temperature_plot.png"
    assert expected_file.exists()

    os.chdir(cwd)


def test_plot_cluster_summary(tmp_path):
    visualizer = ClimateVisualizer()
    station_names = ["Station A", "Station B", "Station C"]
    cluster_ids = [0, 1, 0]

    cwd = os.getcwd()
    os.chdir(tmp_path)

    visualizer.plot_cluster_summary(station_names, cluster_ids)

    expected_file = tmp_path / "climate_clusters.png"
    assert expected_file.exists()

    os.chdir(cwd)


def test_plot_temperature_heatmap(tmp_path):
    visualizer = ClimateVisualizer()
    data = pd.DataFrame({
        2020: [15.0, 16.0, 14.5],
        2021: [15.5, 16.1, 14.8],
        2022: [15.8, 16.2, 15.0],
    }, index=["Station A", "Station B", "Station C"])
    regions = data.index.tolist()
    times = [str(col) for col in data.columns]

    cwd = os.getcwd()
    os.chdir(tmp_path)

    visualizer.plot_temperature_heatmap(data=data, regions=regions, times=times)

    expected_file = tmp_path / "temperature_heatmap.png"
    assert expected_file.exists()

    os.chdir(cwd)
