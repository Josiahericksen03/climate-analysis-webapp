import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_sample_climate_data(num_regions: int = 5, 
                               start_date: str = '2000-01-01',
                               end_date: str = '2023-12-31') -> pd.DataFrame:
    """
    Generate sample climate data for testing.
    
    Args:
        num_regions (int): Number of regions to generate data for
        start_date (str): Start date for the time series
        end_date (str): End date for the time series
        
    Returns:
        pd.DataFrame: Generated climate data
    """
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate dates
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Generate random coordinates for regions
    regions = [f'Region_{i}' for i in range(num_regions)]
    latitudes = np.random.uniform(-90, 90, num_regions)
    longitudes = np.random.uniform(-180, 180, num_regions)
    
    # Create empty list to store data
    data = []
    
    # Generate temperature data with seasonal patterns and long-term trend
    for region, lat, lon in zip(regions, latitudes, longitudes):
        base_temp = 15 - abs(lat)/5  # Base temperature depends on latitude
        
        for date in dates:
            # Add seasonal variation
            day_of_year = date.dayofyear
            seasonal_effect = 10 * np.sin(2 * np.pi * day_of_year / 365)
            
            # Add long-term warming trend
            years_since_start = (date - dates[0]).days / 365
            warming_trend = 0.02 * years_since_start
            
            # Add random variation
            noise = np.random.normal(0, 1)
            
            temperature = base_temp + seasonal_effect + warming_trend + noise
            precipitation = max(0, np.random.normal(100, 30) + seasonal_effect)
            humidity = max(0, min(100, np.random.normal(70, 10) + seasonal_effect/2))
            
            data.append({
                'date': date,
                'region': region,
                'latitude': lat,
                'longitude': lon,
                'temperature': temperature,
                'precipitation': precipitation,
                'humidity': humidity
            })
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Generate sample data
    df = generate_sample_climate_data()
    
    # Save to CSV
    df.to_csv('data/climate_data.csv', index=False)
    print("Sample data generated and saved to 'data/climate_data.csv'") 