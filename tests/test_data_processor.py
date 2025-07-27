import pandas as pd
import numpy as np
import pytest
from src.data_processor import DataProcessor

@pytest.fixture
def sample_df():
    return pd.DataFrame({
        'station_id': ['STA001', 'STA002', 'STA003', 'STA004'],
        'station_name': ['North Station', 'South Station', 'East Station', 'West Station'],
        'date': ['2000-01-01', '2000-01-02', '2000-01-03', '2000-01-04'],
        'temperature': [15.0, 20.0, 25.0, np.nan]
    })

def test_load_data(tmp_path):
    sample_csv = tmp_path / 'sample.csv'
    df = pd.DataFrame({
        'station_id': ['STA001', 'STA002'],
        'station_name': ['Station A', 'Station B'],
        'date': ['2000-01-01', '2000-01-02'],
        'temperature': [20.0, 25.0]
    })
    df.to_csv(sample_csv, index=False, header=False)  # match real format (no headers)

    processor = DataProcessor(str(sample_csv))
    loaded = processor.load_data()
    assert isinstance(loaded, pd.DataFrame)
    assert not loaded.empty

def test_clean_data(sample_df):
    processor = DataProcessor("fake.csv")
    processor.data = sample_df
    cleaned = processor.clean_data()
    assert cleaned.isnull().sum().sum() == 0
    assert cleaned.duplicated().sum() == 0

def test_normalize_data(sample_df):
    processor = DataProcessor("fake.csv")
    processor.data = sample_df.dropna()
    normalized = processor.normalize_data()
    assert 'temperature' in normalized.columns
    assert np.isclose(normalized['temperature'].mean(), 0, atol=1e-1)
