import numbers

import numpy as np
import pytest
from src.ml_algorithms import ClimateML


def test_predict_temperature_shape():
    ml = ClimateML()
    historical_data = np.linspace(10, 30, 365)  # 1 year of data
    forecast = ml.predict_temperature(historical_data, historical_data, forecast_period=30)
    assert isinstance(forecast, np.ndarray)
    assert len(forecast) == 30


def test_detect_anomalies_behavior():
    ml = ClimateML()
    data = np.array([20, 21, 22, 23, 150, 24, 25])  # 150 is an obvious outlier
    anomalies = ml.detect_anomalies(data)
    assert isinstance(anomalies, list)
    assert len(anomalies) == len(data)
    assert any(anomalies)  # There should be at least one True (for the outlier)


def test_cluster_regions_output():
    ml = ClimateML()
    station_data = {
        "Station A": np.array([15.0, 16.2, 15.8]),
        "Station B": np.array([25.5, 26.1, 24.9]),
        "Station C": np.array([15.1, 15.9, 16.3]),
        "Station D": np.array([24.8, 26.2, 25.3])
    }
    clusters = ml.cluster_regions(station_data, n_clusters=2)
    assert isinstance(clusters, dict)
    assert set(clusters.keys()) == set(station_data.keys())
    assert all(isinstance(label, numbers.Integral) for label in clusters.values())
    assert set(clusters.values()).issubset({0, 1})


@pytest.mark.parametrize("threshold", [1.5, 2.0, 3.0])
def test_anomaly_threshold_effect(threshold):
    ml = ClimateML()
    data = np.array([10] * 50 + [100])  # One extreme outlier
    anomalies = ml.detect_anomalies(data, threshold=threshold)
    assert anomalies[-1] is True  # Ensure last value is detected as an anomaly

