#!/usr/bin/env python3
"""
Cache Generator for Climate Analysis Webapp
Pre-generates all possible analysis plots for instant serving
"""

import os
import sys
import time
import numpy as np
from pathlib import Path

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from data_processor import DataProcessor
from ml_algorithms import ClimateML
from visualizer import ClimateVisualizer

def generate_all_cache():
    """Generate all possible analysis plots and cache them"""
    
    print("🚀 Starting cache generation for Climate Analysis Webapp...")
    print("This will pre-generate all possible analyses for instant serving.")
    print("=" * 60)
    
    # Initialize components
    data_path = os.path.join('data', 'climate_data.csv')
    processor = DataProcessor(data_path)
    ml = ClimateML()
    visualizer = ClimateVisualizer()
    
    # Load and clean data
    print("📊 Loading and cleaning data...")
    df = processor.load_data()
    df = processor.clean_data()
    
    # Create static directory if it doesn't exist
    static_dir = Path('webapp/static')
    static_dir.mkdir(exist_ok=True)
    
    # Get unique stations
    stations = df['station_name'].unique()
    print(f"📍 Found {len(stations)} stations: {list(stations)}")
    
    # Generate all possible analyses
    analyses_generated = 0
    
    # 1. Temperature Analysis for each individual station
    print("\n🌡️  Generating temperature analysis for each station...")
    for station in stations:
        print(f"   Processing: {station}")
        try:
            # Filter data for this station
            station_data = df[df['station_name'] == station]
            
            if len(station_data) > 0:
                # Generate trend plot with predictions and anomalies
                generate_trend_plot_for_station(station_data, ml, visualizer, station)
                analyses_generated += 1
                print(f"   ✅ Generated trend analysis for {station}")
            else:
                print(f"   ⚠️  No data for {station}")
                
        except Exception as e:
            print(f"   ❌ Error processing {station}: {str(e)}")
    
    # 2. Regional Clustering Analysis
    print("\n🗺️  Generating regional clustering analysis...")
    try:
        generate_clustering_analysis(df, ml, visualizer)
        analyses_generated += 1
        print("   ✅ Generated clustering analysis")
    except Exception as e:
        print(f"   ❌ Error generating clustering: {str(e)}")
    
    # 3. Temperature Heatmap
    print("\n🔥 Generating temperature heatmap...")
    try:
        generate_heatmap(df, visualizer)
        analyses_generated += 1
        print("   ✅ Generated temperature heatmap")
    except Exception as e:
        print(f"   ❌ Error generating heatmap: {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"🎉 Cache generation complete!")
    print(f"📈 Generated {analyses_generated} analysis types")
    print(f"📁 All plots saved to: webapp/static/")
    print("\n💡 Your website will now serve these pre-generated analyses instantly!")
    print("   No more waiting for LSTM training or memory issues on Render!")

def generate_trend_plot_for_station(station_data, ml, visualizer, station_name):
    """Generate trend analysis plot for a specific station"""
    
    # Prepare data
    dates = station_data['date'].tolist()
    temperatures = station_data['temperature'].tolist()
    
    # Generate predictions (30 days into future)
    predictions = ml.predict_temperature(
        np.array(temperatures), 
        np.array(temperatures), 
        forecast_period=30
    )
    
    # Detect anomalies
    anomalies = ml.detect_anomalies(np.array(temperatures), threshold=2.0)
    
    # Create safe filename
    safe_name = station_name.replace(' ', '_').replace(',', '').replace('/', '_')[:50]
    output_path = f"webapp/static/trend_analysis_{safe_name}.png"
    
    # Generate plot
    visualizer.plot_temperature_with_predictions_and_anomalies(
        dates, temperatures, predictions, anomalies,
        f"Temperature Analysis: {station_name}",
        output_path
    )

def generate_clustering_analysis(df, ml, visualizer):
    """Generate regional clustering analysis"""
    
    # Group data by station
    stations_data = {}
    for station in df['station_name'].unique():
        station_data = df[df['station_name'] == station]
        if len(station_data) > 0:
            stations_data[station] = station_data['temperature'].values
    
    # Perform clustering
    cluster_results = ml.cluster_regions(stations_data, n_clusters=2)
    
    # Generate plot
    station_names = list(cluster_results.keys())
    cluster_ids = list(cluster_results.values())
    
    output_path = "webapp/static/climate_clusters.png"
    visualizer.plot_cluster_summary(station_names, cluster_ids, output_path)

def generate_heatmap(df, visualizer):
    """Generate temperature heatmap"""
    
    # Create pivot table for heatmap
    df['year'] = df['date'].dt.year
    heatmap_data = df.pivot_table(
        values='temperature', 
        index='station_name', 
        columns='year', 
        aggfunc='mean'
    )
    
    # Generate plot
    output_path = "webapp/static/temperature_heatmap.png"
    visualizer.plot_temperature_heatmap(
        heatmap_data, 
        title="Average Yearly Temperature by Station",
        output_path=output_path
    )

if __name__ == "__main__":
    start_time = time.time()
    generate_all_cache()
    end_time = time.time()
    
    print(f"\n⏱️  Total time: {end_time - start_time:.2f} seconds")
    print("\n🚀 Ready to deploy! All analyses are now cached for instant serving.") 