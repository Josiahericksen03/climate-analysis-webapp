#!/usr/bin/env python3
"""
Climate Change Impact Analyzer - Website Runner

Simple script to run the climate analysis website.
"""

import os
import sys
from pathlib import Path

def main():
    """Run the climate analysis website"""
    print("🌍 Climate Change Impact Analyzer")
    print("=" * 40)
    
    # Check if we're in the webapp directory
    if not Path("app.py").exists():
        print("❌ Error: Please run this script from the webapp directory")
        print("   Expected: cd webapp && python3 run_website.py")
        sys.exit(1)
    
    # Check if static files exist
    static_dir = Path("static")
    if not static_dir.exists():
        static_dir.mkdir(exist_ok=True)
        print("📁 Created static directory")
    
    # Copy visualization files from parent directory if they don't exist
    viz_files = [
        "climate_clusters.png",
        "temperature_heatmap.png",
        "temperature_analysis_tallahassee_regional_airport_fl_us_temperature_trends.png",
        "temperature_analysis_dallas_7_ne_ga_us_temperature_trends.png",
        "temperature_analysis_los_angeles_international_airport_ca_us_temperature_trends.png"
    ]
    
    for file in viz_files:
        src = Path(f"../{file}")
        dst = static_dir / file
        if src.exists() and not dst.exists():
            print(f"📁 Copying {file} to static directory")
            import shutil
            shutil.copy2(src, dst)
    
    print("🚀 Starting Climate Analysis Website...")
    print("📍 Website will be available at: http://localhost:5001")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 40)
    
    try:
        # Set Flask environment variables
        os.environ['FLASK_ENV'] = 'development'
        os.environ['FLASK_DEBUG'] = '1'
        
        # Import and run the app
        from app import app
        app.run(host='0.0.0.0', port=5001, debug=True)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Error running website: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 