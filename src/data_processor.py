import os

import pandas as pd
import numpy as np
from typing import Dict, Any

class DataProcessor:
    """
    Handles loading, cleaning, and preprocessing of climate data.
    """
    
    def __init__(self, data_path: str):
        """
        Initialize the DataProcessor with the path to the data file.
        
        Args:
            data_path (str): Path to the climate data file (CSV/JSON)
        """
        self.data_path = data_path
        self.data = None

    def load_data(self) -> pd.DataFrame:
        """
        Load data from the specified file path.
        Returns:
            pd.DataFrame: Loaded climate data
        """
        try:
            # Ensure path is relative to project root
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # /src/ -> root
            full_path = os.path.join(base_dir, self.data_path)
            if not os.path.exists(full_path):
                raise FileNotFoundError(f"Resolved path does not exist: {full_path}")
            self.data = pd.read_csv(
                full_path,
                header=0
            )
            return self.data
        except Exception as e:
            raise Exception(f"Error loading data: {str(e)}")
            
    def clean_data(self) -> pd.DataFrame:
        """
        Clean the loaded data by removing nulls and duplicates.
        
        Returns:
            pd.DataFrame: Cleaned climate data
        """
        if self.data is None:
            raise Exception("Data not loaded. Call load_data() first.")
            
        # Remove duplicate entries
        self.data = self.data.drop_duplicates()
        self.data['date'] = pd.to_datetime(self.data['date'], format="%Y-%m-%d", errors='coerce')
        self.data['temperature'] = pd.to_numeric(self.data['temperature'], errors='coerce')
        self.data = self.data.dropna(subset=["date", "temperature"])

        # Set datetime index for interpolation
        self.data.set_index('date', inplace=True)

        # Remove outliers using Z-score
        z = (self.data['temperature'] - self.data['temperature'].mean()) / self.data['temperature'].std()
        self.data = self.data[(np.abs(z) < 3)]

        # Interpolate missing temperatures
        self.data['temperature'] = self.data['temperature'].interpolate(method='time')

        self.data = self.data.reset_index()  # put 'date' back as column
        
        return self.data
        
    def normalize_data(self) -> pd.DataFrame:
        """
        Normalize numerical columns in the dataset.
        
        Returns:
            pd.DataFrame: Normalized climate data
        """
        if self.data is None:
            raise Exception("Data not loaded. Call load_data() first.")
            
        numeric_columns = self.data.select_dtypes(include=[np.number]).columns
        
        for column in numeric_columns:
            self.data[column] = (self.data[column] - self.data[column].mean()) / self.data[column].std()
            
        return self.data 