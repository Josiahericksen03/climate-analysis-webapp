import os
import sys
import json
import numpy as np
import pandas as pd
from pathlib import Path
from flask import render_template, request, jsonify, send_file
import hashlib
import gc
import psutil

# Add parent directory to path to import src modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Get the correct data path
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'climate_data.csv')
from src.data_processor import DataProcessor
from src.ml_algorithms import ClimateML
from src.visualizer import ClimateVisualizer


def get_cache_key(station, analysis_type):
    """Generate a cache key for the analysis"""
    return hashlib.md5(f"{station}_{analysis_type}".encode()).hexdigest()


def is_plot_cached(plot_filename):
    """Check if a plot already exists"""
    static_dir = Path("static")
    return (static_dir / plot_filename).exists()


def configure_routes(app):
    @app.route('/')
    def index():
        """Main climate analysis homepage"""
        return render_template('index.html')

    @app.route('/analyze', methods=['POST'])
    def analyze():
        """Handle climate analysis requests"""
        try:
            # Get form data
            station = request.form.get('station', 'all')
            analysis_type = request.form.get('type', 'trends')
            
            # Process data
            processor = DataProcessor(DATA_PATH)
            df = processor.load_data()
            df = processor.clean_data()
            
            # Initialize ML and visualizer
            ml = ClimateML()
            visualizer = ClimateVisualizer()
            
            results = {
                'success': True,
                'message': 'Analysis completed successfully',
                'station': station,
                'analysis_type': analysis_type,
                'data_summary': {
                    'total_records': len(df),
                    'stations': df['station_name'].nunique(),
                    'date_range': f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
                }
            }
            
            # Filter data by station if specific station selected
            if station != 'all':
                df = df[df['station_name'].str.contains(station, case=False)]
                if len(df) == 0:
                    return jsonify({
                        'success': False,
                        'message': f'No data found for station: {station}'
                    }), 400
            
            # Serve pre-generated visualizations (cached approach)
            if analysis_type == 'temperature':
                if station == 'all':
                    # Serve all individual station plots
                    results['plots'] = [
                        "trend_analysis_TALLAHASSEE_REGIONAL_AIRPORT_FL_US.png",
                        "trend_analysis_DALLAS_7_NE_GA_US.png", 
                        "trend_analysis_LOS_ANGELES_INTERNATIONAL_AIRPORT_CA_US.png"
                    ]
                    results['cached'] = True
                    results['message'] = 'Serving pre-generated temperature analyses for all stations'
                else:
                    # Serve specific station plot
                    safe_name = station.replace(' ', '_').replace(',', '').replace('/', '_')[:50]
                    plot_name = f"trend_analysis_{safe_name}.png"
                    results['plots'] = [plot_name]
                    results['cached'] = True
                    results['message'] = f'Serving pre-generated temperature analysis for {station}'
                    
            elif analysis_type == 'clustering':
                results['plots'] = ["climate_clusters.png"]
                results['cached'] = True
                results['message'] = 'Serving pre-generated regional clustering analysis'
            
            return jsonify(results)
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'Analysis failed: {str(e)}'
            }), 500

    @app.route('/api/stats')
    def get_stats():
        """Get project statistics"""
        try:
            processor = DataProcessor(DATA_PATH)
            df = processor.load_data()
            
            stats = {
                'total_records': len(df),
                'stations': df['station_name'].nunique(),
                'years': (df['date'].max() - df['date'].min()).days / 365.25,
                'avg_temperature': df['temperature'].mean(),
                'date_range': {
                    'start': df['date'].min().strftime('%Y-%m-%d'),
                    'end': df['date'].max().strftime('%Y-%m-%d')
                }
            }
            
            return jsonify(stats)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/api/station-data/<station_name>')
    def get_station_data(station_name):
        """Get data for a specific weather station"""
        try:
            processor = DataProcessor(DATA_PATH)
            df = processor.load_data()
            df = processor.clean_data()
            
            if station_name != 'all':
                station_data = df[df['station_name'].str.contains(station_name, case=False)]
            else:
                station_data = df
            
            # Convert to JSON-serializable format
            data = {
                'dates': station_data['date'].dt.strftime('%Y-%m-%d').tolist(),
                'temperatures': station_data['temperature'].tolist(),
                'station_name': station_data['station_name'].iloc[0] if len(station_data) > 0 else 'Unknown'
            }
            
            return jsonify(data)
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/download/<filename>')
    def download_file(filename):
        """Download analysis results"""
        try:
            file_path = os.path.join('static', filename)
            if os.path.exists(file_path):
                return send_file(file_path, as_attachment=True)
            else:
                return jsonify({'error': 'File not found'}), 404
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/export-analysis')
    def export_analysis():
        """Export analysis results as JSON"""
        try:
            processor = DataProcessor(DATA_PATH)
            df = processor.load_data()
            df = processor.clean_data()
            
            # Generate summary statistics
            summary = {
                'data_summary': {
                    'total_records': len(df),
                    'stations': df['station_name'].nunique(),
                    'date_range': {
                        'start': df['date'].min().strftime('%Y-%m-%d'),
                        'end': df['date'].max().strftime('%Y-%m-%d')
                    }
                },
                'station_summary': df.groupby('station_name').agg({
                    'temperature': ['mean', 'std', 'min', 'max'],
                    'date': ['min', 'max']
                }).round(2).to_dict(),
                'analysis_timestamp': pd.Timestamp.now().isoformat()
            }
            
            return jsonify(summary)
        except Exception as e:
            return jsonify({'error': str(e)}), 500


def generate_trend_plots(df, ml, visualizer, selected_station='all'):
    """Generate temperature trend plots for selected station(s)"""
    plots = []
    
    # Ensure static directory exists
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # If specific station selected, only process that one
    if selected_station != 'all':
        station_names = [selected_station]
    else:
        station_names = df['station_name'].unique()
    
    for station_name in station_names:
        # Find the actual station name from the data
        matching_stations = df[df['station_name'].str.contains(station_name, case=False)]
        if len(matching_stations) == 0:
            continue
            
        actual_station_name = matching_stations['station_name'].iloc[0]
        station_data = df[df['station_name'] == actual_station_name].copy()
        station_data = station_data.sort_values('date')
        
        dates = station_data['date'].tolist()
        temps = station_data['temperature'].tolist()
        
        # Detect anomalies
        anomalies = ml.detect_anomalies(np.array(temps))
        
        # Generate predictions (use shorter sequence to avoid issues)
        if len(temps) > 30:
            predictions = ml.predict_temperature(np.array(temps[:-30]), np.array(temps[:-30]), forecast_period=30)
        else:
            predictions = []
        
        # Create plot filename
        safe_name = actual_station_name.replace(' ', '_').replace(',', '').replace('/', '_')[:20]
        plot_filename = f"trend_analysis_{safe_name}.png"
        plot_path = static_dir / plot_filename
        
        try:
            # Generate plot
            visualizer.plot_temperature_with_predictions_and_anomalies(
                dates, temps, predictions, anomalies,
                title=f"Temperature Trends for {actual_station_name}",
                output_path=str(plot_path)
            )
            plots.append(plot_filename)
            
            # Clear matplotlib memory after each plot
            import matplotlib.pyplot as plt
            plt.close('all')
            
        except Exception as e:
            print(f"Error generating trend plot for {actual_station_name}: {e}")
            continue
    
    return plots


def generate_anomaly_plots(df, ml, visualizer, selected_station='all'):
    """Generate anomaly detection plots for selected station(s)"""
    plots = []
    
    # Ensure static directory exists
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # If specific station selected, only process that one
    if selected_station != 'all':
        station_names = [selected_station]
    else:
        station_names = df['station_name'].unique()
    
    for station_name in station_names:
        # Find the actual station name from the data
        matching_stations = df[df['station_name'].str.contains(station_name, case=False)]
        if len(matching_stations) == 0:
            continue
            
        actual_station_name = matching_stations['station_name'].iloc[0]
        station_data = df[df['station_name'] == actual_station_name].copy()
        temps = station_data['temperature'].values
        
        # Detect anomalies
        anomalies = ml.detect_anomalies(temps)
        
        # Create anomaly plot
        safe_name = actual_station_name.replace(' ', '_').replace(',', '').replace('/', '_')[:20]
        plot_filename = f"anomaly_analysis_{safe_name}.png"
        plot_path = static_dir / plot_filename
        
        try:
            # Generate anomaly visualization
            visualizer.plot_temperature_with_predictions_and_anomalies(
                station_data['date'].tolist(), temps.tolist(), [], anomalies,
                title=f"Anomaly Detection for {actual_station_name}",
                output_path=str(plot_path)
            )
            plots.append(plot_filename)
        except Exception as e:
            print(f"Error generating anomaly plot for {actual_station_name}: {e}")
            continue
    
    return plots


def generate_clustering_plots(df, ml, visualizer):
    """Generate clustering analysis plots"""
    # Ensure static directory exists
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # Calculate multiple features for each station for better clustering
    station_features = df.groupby('station_name').agg({
        'temperature': ['mean', 'std', 'min', 'max']
    }).reset_index()
    
    # Flatten column names
    station_features.columns = ['station_name', 'temp_mean', 'temp_std', 'temp_min', 'temp_max']
    
    # Prepare data for clustering using multiple features
    data_by_region = {}
    for _, row in station_features.iterrows():
        data_by_region[row['station_name']] = [
            row['temp_mean'], 
            row['temp_std'], 
            row['temp_min'], 
            row['temp_max']
        ]
    
    # Perform clustering
    cluster_labels = ml.cluster_regions(data_by_region, n_clusters=2)
    
    # Generate cluster plot
    plot_filename = "climate_clusters.png"
    plot_path = static_dir / plot_filename
    
    try:
        visualizer.plot_cluster_summary(
            station_names=station_features['station_name'].tolist(),
            cluster_ids=list(cluster_labels.values()),
            output_path=str(plot_path)
        )
        return [plot_filename]
    except Exception as e:
        print(f"Error generating clustering plot: {e}")
        return []


def generate_prediction_plots(df, ml, visualizer, selected_station='all'):
    """Generate future prediction plots for selected station(s)"""
    plots = []
    
    # Ensure static directory exists
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # If specific station selected, only process that one
    if selected_station != 'all':
        station_names = [selected_station]
    else:
        station_names = df['station_name'].unique()
    
    for station_name in station_names:
        # Find the actual station name from the data
        matching_stations = df[df['station_name'].str.contains(station_name, case=False)]
        if len(matching_stations) == 0:
            continue
            
        actual_station_name = matching_stations['station_name'].iloc[0]
        station_data = df[df['station_name'] == actual_station_name].copy()
        station_data = station_data.sort_values('date')
        
        temps = station_data['temperature'].values
        
        # Generate longer-term predictions (use shorter sequence to avoid issues)
        if len(temps) > 30:
            predictions = ml.predict_temperature(temps[:-30], temps[:-30], forecast_period=90)
        else:
            predictions = []
        
        # Create prediction plot
        safe_name = actual_station_name.replace(' ', '_').replace(',', '').replace('/', '_')[:20]
        plot_filename = f"prediction_{safe_name}.png"
        plot_path = static_dir / plot_filename
        
        try:
            visualizer.plot_temperature_with_predictions_and_anomalies(
                station_data['date'].tolist(), temps.tolist(), predictions, [],
                title=f"Future Predictions for {actual_station_name}",
                output_path=str(plot_path)
            )
            plots.append(plot_filename)
        except Exception as e:
            print(f"Error generating prediction plot for {actual_station_name}: {e}")
            continue
    
    return plots
