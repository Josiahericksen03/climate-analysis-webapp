import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
from typing import Tuple, List, Dict
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

class ClimateML:
    """
    Implements machine learning algorithms for climate data analysis.
    """

    def __init__(self):
        """Initialize the ClimateML class."""
        self.model = None
        self.scaler = MinMaxScaler()

    def create_sequences(self, data: np.ndarray, seq_length: int) -> Tuple[np.ndarray, np.ndarray]:
        """
        Create sequences for time series prediction.

        Args:
            data (np.ndarray): Input time series data
            seq_length (int): Length of each sequence

        Returns:
            Tuple[np.ndarray, np.ndarray]: X and y sequences
        """
        X, y = [], []
        for i in range(len(data) - seq_length):
            X.append(data[i:(i + seq_length)])
            y.append(data[i + seq_length])
        return np.array(X), np.array(y)

    def predict_temperature(self, data: np.ndarray, target: np.ndarray,
                            forecast_period: int) -> np.ndarray:
        """
        Predict future temperature trends using LSTM.

        Args:
            data (np.ndarray): Historical temperature data
            target (np.ndarray): Target values
            forecast_period (int): Number of periods to forecast

        Returns:
            np.ndarray: Predicted temperature values
        """
        # Scale the data
        scaled_data = self.scaler.fit_transform(data.reshape(-1, 1))

        # Create sequences
        seq_length = 10  # Look back 10 time steps
        X, y = self.create_sequences(scaled_data, seq_length)

        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        # Build LSTM model with ultra-lightweight architecture for Render
        self.model = Sequential([
            LSTM(10, activation='relu', input_shape=(seq_length, 1), return_sequences=True),
            Dropout(0.1),
            LSTM(10, activation='relu'),
            Dropout(0.1),
            Dense(1)
        ])

        self.model.compile(optimizer='adam', loss='mse')

        # Train model with minimal epochs for Render
        self.model.fit(
            X_train, y_train,
            epochs=10,  # Ultra-reduced for Render
            batch_size=16,  # Smaller batch size
            validation_split=0.1,
            verbose=0
        )

        # Make predictions
        last_sequence = scaled_data[-seq_length:]
        predictions = []

        for _ in range(forecast_period):
            # Reshape the last sequence for prediction
            current_sequence = last_sequence.reshape(1, seq_length, 1)
            # Get the next predicted value
            next_pred = self.model.predict(current_sequence, verbose=0)[0]
            predictions.append(next_pred)
            # Update the sequence
            last_sequence = np.roll(last_sequence, -1)
            last_sequence[-1] = next_pred

        # Inverse transform predictions
        predictions = self.scaler.inverse_transform(np.array(predictions))
        return predictions.flatten()

    def cluster_regions(self, data_by_region: Dict[str, np.ndarray], n_clusters: int) -> Dict[str, int]:
        """
        Cluster stations based on their average temperature patterns.

        Args:
            data_by_region (Dict[str, np.ndarray]): Dictionary of station name to temperature arrays
            n_clusters (int): Number of clusters

        Returns:
            Dict[str, int]: Mapping from station name to cluster ID
        """
        region_names = list(data_by_region.keys())
        # Pad or truncate time series to same length
        min_len = min(len(v) for v in data_by_region.values())
        aligned_data = np.array([v[:min_len] for v in data_by_region.values()])
        scaled = self.scaler.fit_transform(aligned_data)

        kmeans = KMeans(n_clusters=n_clusters, random_state=42)
        labels = kmeans.fit_predict(scaled)

        return dict(zip(region_names, labels))

    def detect_anomalies(self, data: np.ndarray, threshold: float = 2.0) -> List[bool]:
        """
        Detect anomalies in climate data using Z-score method.

        Args:
            data (np.ndarray): Climate data time series
            threshold (float): Z-score threshold for anomaly detection

        Returns:
            List[bool]: Boolean mask indicating anomalies
        """
        mean = np.mean(data)
        std = np.std(data)
        z_scores = np.abs((data - mean) / std)
        anomalies = z_scores > threshold
        return anomalies.tolist()
