# Climate Change Impact Analyzer

A web-based climate data analysis tool with machine learning capabilities and data visualization.

## Project Structure
```
.
├── data/
│   ├── climate_data.csv
│   └── sample_data_generator.py
├── src/
│   ├── data_processor.py
│   ├── main.py
│   ├── ml_algorithms.py
│   └── visualizer.py
├── tests/
│   ├── test_algorithms.py
│   ├── test_data_processor.py
│   └── test_visualizer.py
├── webapp/
│   ├── app.py
│   ├── routes.py
│   ├── static/
│   │   └── style.css
│   └── templates/
│       ├── index.html
│       ├── layout.html
│       └── result.html
└── requirements.txt
```

## Setup

1. Clone the repository:
```bash
git clone [your-repository-url]
cd [repository-name]
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Web Application
The climate analysis website provides an interactive interface for exploring climate data, running machine learning analyses, and viewing visualizations.

#### **Step 1: Activate Virtual Environment**
```bash
source venv/bin/activate
```

#### **Step 2: Navigate to Webapp Directory**
```bash
cd webapp
```

#### **Step 3: Run the Website**
```bash
python3 run_website.py
```

The website will start at **http://localhost:5001** and you should see:
- 🌍 Climate Change Impact Analyzer
- 📍 Website will be available at: http://localhost:5001
- 🛑 Press Ctrl+C to stop the server

**Note:** Make sure your virtual environment is activated before running the website to ensure all dependencies are available.


### Command Line Interface
To run the main script:
```bash
python src/main.py
```

## Running Tests
Run individual test files:
```bash
python -m unittest tests/test_algorithms.py
python -m unittest tests/test_data_processor.py
python -m unittest tests/test_visualizer.py
```

Or run all tests:
```bash
python -m unittest discover tests
```

## Components

- **Data Processing** (`src/data_processor.py`): Handles climate data loading and preprocessing
  __init__(self, data_path: str): Initializes the class with the path to the climate data file (CSV/JSON).

load_data(self) -> pd.DataFrame: Loads the data from the specified file path. It ensures the path is correct and returns a DataFrame.

clean_data(self) -> pd.DataFrame: Cleans the loaded data by removing duplicates, handling missing values, converting the date and temperature columns, removing outliers using Z-scores, and interpolating missing temperature values.

normalize_data(self) -> pd.DataFrame: Normalizes the numerical columns of the dataset to ensure that they have zero mean and unit variance.
- **Machine Learning** (`src/ml_algorithms.py`): Implements predictive algorithms
__init__(self): Initializes the class, preparing the model and scaler for use.

create_sequences(self, data: np.ndarray, seq_length: int) -> Tuple[np.ndarray, np.ndarray]: Converts the time-series data into sequences for machine learning purposes (e.g., for LSTM model training).

predict_temperature(self, data: np.ndarray, target: np.ndarray, forecast_period: int) -> np.ndarray: Uses an LSTM model to predict future temperature trends based on historical data. It scales the data, creates sequences, splits the data into training and testing sets, and trains an LSTM model.

cluster_regions(self, data_by_region: Dict[str, np.ndarray], n_clusters: int) -> Dict[str, int]: Clusters climate stations by their temperature patterns using the K-Means algorithm.

detect_anomalies(self, data: np.ndarray, threshold: float = 2.0) -> List[bool]: Detects anomalies in the climate data using Z-scores to identify values that significantly deviate from the mean.
- **Visualization** (`src/visualizer.py`): Creates data visualizations
  __init__(self): Initializes the plotting style using matplotlib and seaborn.

plot_temperature_with_predictions_and_anomalies(self, dates, temperatures, predictions, anomalies, title): Plots a temperature chart with actual data, predicted data, and anomalies highlighted. The chart is saved as a PNG file.

plot_cluster_summary(self, station_names: List[str], cluster_ids: List[int]): Creates a bar plot summarizing the climate clusters by station and saves it as a PNG file.

plot_temperature_heatmap(self, data: pd.DataFrame, regions: List[str], times: List[str], title: str): Creates a heatmap to visualize temperature data across different stations and years. The heatmap is saved as a PNG file.
- **Web Interface** (`webapp/`): Flask-based web application for interactive analysis
- **Sample Data** (`data/`): Contains climate datasets and data generation utilities

## Course Information
Repository shared with:
- Instructor: @Shifat11420
- TAs: @Schoksi20, @hirveshradhaa
