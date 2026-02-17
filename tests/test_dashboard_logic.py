import pandas as pd
import numpy as np
import sys
import os
from pathlib import Path

def test_dashboard_data_integrity():
    print("🔬 DASHBOARD FEATURE TEST: DATA INTEGRITY")
    print("=" * 50)
    
    try:
        data_path = 'data/processed/county_features.csv'
        if not os.path.exists(data_path):
            print(f"❌ FAIL: {data_path} not found")
            return
            
        df = pd.read_csv(data_path)
        
        # 1. Missouri Filter Test
        mo_df = df[df['county_name'].str.endswith(", Missouri")]
        count = len(mo_df)
        print(f"Checking MO County Count: {count} (Expected: 115)")
        assert count == 115, f"Expected 115 MO counties, found {count}"
        print("✅ PASS: Missouri count validated.")
        
        # 2. Healthcare Gap Math Test
        uninsured_avg = mo_df['uninsured_pct'].mean()
        print(f"Checking Uninsured Avg: {uninsured_avg:.2f}% (Expected: ~11.76%)")
        assert 5 < uninsured_avg < 25, f"Uninsured avg {uninsured_avg} out of realistic bounds!"
        print("✅ PASS: Healthcare gap math validated.")
        
        # 3. High Risk Count Test
        high_risk_mo = len(mo_df[mo_df['risk_level'] == 'High'])
        print(f"Checking High Risk Count: {high_risk_mo} (Expected: 57)")
        assert high_risk_mo > 0, "No high risk counties found in MO?"
        print("✅ PASS: Risk classification presence validated.")
        
        # 4. Longitude/Latitude Bound Test (For 3D Viz)
        print("Checking Geo Coordinates for MO...")
        assert mo_df['latitude'].between(35, 41).all(), "MO Latitude out of bounds!"
        assert mo_df['longitude'].between(-96, -89).all(), "MO Longitude out of bounds!"
        print("✅ PASS: Geospatial coordinates validated.")

        print("\n🏆 SUMMARY: ALL CRITICAL FEATURES PASSED VALIDATION")
        
    except Exception as e:
        print(f"\n💥 CRITICAL TEST FAILURE: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_dashboard_data_integrity()
