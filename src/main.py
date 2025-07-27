from data_processor import DataProcessor
from ml_algorithms import ClimateML
from visualizer import ClimateVisualizer

def main():
    print("Climate Change Impact Analyzer (CLI Mode)")
    print("-------------------------------------------")

    # 1. Load data
    print("\n1. Loading real climate data...")
    processor = DataProcessor('data/climate_data.csv')
    df = processor.load_data()
    df = processor.clean_data()
    print(f"Loaded data shape: {df.shape}")

    # 2. Anomaly detection and predictions
    print("\n2. Running anomaly detection and predictions...")
    ml = ClimateML()
    visualizer = ClimateVisualizer()

    grouped = df.groupby("station_name")
    data_by_station = {}

    for station_name, station_df in grouped:
        print(f"\nProcessing station: {station_name}")

        temps = station_df['temperature'].values
        dates = station_df['date'].values

        # Detect anomalies
        anomalies = ml.detect_anomalies(temps)

        # Predict future temps
        prediction = ml.predict_temperature(temps[:-30], temps[:-30], forecast_period=90)

        # Store for clustering
        data_by_station[station_name] = temps

        # Plot
        visualizer.plot_temperature_with_predictions_and_anomalies(
            dates=dates,
            temperatures=temps,
            predictions=prediction,
            anomalies=anomalies,
            title=f"{station_name} Temperature Trends"
        )

    # 3. Cluster regions based on mean temp patterns
    print("\n3. Performing station clustering...")
    clusters = ml.cluster_regions(data_by_region=data_by_station, n_clusters=2)
    visualizer.plot_cluster_summary(station_names=list(clusters.keys()), cluster_ids=list(clusters.values()))

    # 4. Heatmap
    print("\n4. Generating heatmap...")

    # Extract year from date column
    df['year'] = df['date'].dt.year

    # Pivot to get average temperature per year per station
    pivot = df.pivot_table(index='station_name', columns='year', values='temperature', aggfunc='mean')

    # Generate the heatmap
    visualizer.plot_temperature_heatmap(
        data=pivot,
        regions=pivot.index.tolist(),
        times=[str(year) for year in pivot.columns]
    )

if __name__ == "__main__":
    main()
