import pandas as pd
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from geo_visualizations import GeoVisualizer

def test_visualizations():
    print("🧪 Testing Geospatial Visualizations...")
    
    # Create mock data
    df = pd.DataFrame({
        'fips': ['29019', '29189', '29510'],
        'county_name': ['Boone County, Missouri', 'St. Louis County, Missouri', 'St. Louis City, Missouri'],
        'risk_score': [0.5, 0.8, 0.9],
        'latitude': [38.95, 38.62, 38.63],
        'longitude': [-92.33, -90.19, -90.20],
        'total_population': [180000, 1000000, 300000],
        'vulnerability_index': [0.4, 0.7, 0.8]
    })
    
    viz = GeoVisualizer(df)
    
    try:
        print("  - Testing 3D Landscape...", end=" ")
        fig = viz.create_3d_risk_landscape('risk_score')
        if fig:
            print("✅ Success")
        else:
            print("❌ Failed (returned None)")
            
        print("  - Testing Choropleth...", end=" ")
        fig2 = viz.create_choropleth_map('risk_score')
        if fig2:
            print("✅ Success")
        else:
            print("❌ Failed")
            
        print("  - Testing Hexbin...", end=" ")
        fig3 = viz.create_hexbin_map('risk_score')
        if fig3:
            print("✅ Success")
        else:
            print("❌ Failed")
            
    except Exception as e:
        print(f"❌ Exception during visualization: {e}")

if __name__ == "__main__":
    test_visualizations()
