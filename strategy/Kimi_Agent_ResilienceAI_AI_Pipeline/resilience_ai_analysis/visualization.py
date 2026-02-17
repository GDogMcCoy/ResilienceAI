"""
Digital Twin Visualization Components
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime


class TwinDashboard:
    """Interactive digital twin dashboard"""
    
    def __init__(self, county_twin: Any):
        self.county_twin = county_twin
        self.color_schemes = {
            "resilience": ["#d73027", "#fc8d59", "#fee08b", "#d9ef8b", "#91cf60", "#1a9850"],
            "risk": ["#1a9850", "#91cf60", "#fee08b", "#fc8d59", "#d73027"],
            "condition": ["#d73027", "#f46d43", "#fdae61", "#fee08b", "#e6f598", "#abdda4", "#66c2a5", "#3288bd"]
        }
    
    def create_county_overview_map(self) -> go.Figure:
        """Create interactive county overview map"""
        lats, lons, texts, colors, sizes = [], [], [], [], []
        
        for asset_id, asset in self.county_twin.assets.items():
            lats.append(asset.get("latitude", 0))
            lons.append(asset.get("longitude", 0))
            
            text = f"<b>{asset.get('name', asset_id)}</b><br>"
            text += f"Type: {asset.get('asset_type', 'unknown')}<br>"
            text += f"Condition: {asset.get('condition_index', 0.5):.2f}<br>"
            text += f"Criticality: {asset.get('criticality_score', 0.5):.2f}"
            texts.append(text)
            
            condition = asset.get("condition_index", 0.5)
            colors.append(self._condition_to_color(condition))
            
            criticality = asset.get("criticality_score", 0.5)
            sizes.append(10 + criticality * 30)
        
        fig = go.Figure(data=go.Scattermapbox(
            lat=lats, lon=lons, mode='markers',
            marker=dict(size=sizes, color=colors, opacity=0.8),
            text=texts, hoverinfo='text'
        ))
        
        fig.update_layout(
            title=f"{self.county_twin.county_name} Digital Twin Overview",
            mapbox=dict(
                style="carto-positron",
                zoom=10,
                center=dict(lat=np.mean(lats) if lats else 0, lon=np.mean(lons) if lons else 0)
            ),
            height=600
        )
        return fig
    
    def create_resilience_scorecard(self) -> go.Figure:
        """Create resilience scorecard visualization"""
        resilience = self.county_twin.calculate_resilience_index()
        
        categories = ['Overall', 'Infrastructure', 'Connectivity', 'Emergency Prep', 'Env. Risk']
        values = [
            resilience['overall'],
            resilience['infrastructure_health'],
            resilience['network_connectivity'],
            resilience['emergency_preparedness'],
            1 - resilience['environmental_risk']
        ]
        
        fig = go.Figure()
        
        for i, (cat, val) in enumerate(zip(categories, values)):
            fig.add_trace(go.Indicator(
                mode="gauge+number",
                value=val * 100,
                title={'text': cat},
                domain={'row': i // 3, 'column': i % 3},
                gauge={
                    'axis': {'range': [0, 100]},
                    'bar': {'color': self._score_to_color(val)},
                    'steps': [
                        {'range': [0, 40], 'color': '#ffcccc'},
                        {'range': [40, 70], 'color': '#ffffcc'},
                        {'range': [70, 100], 'color': '#ccffcc'}
                    ],
                    'threshold': {
                        'line': {'color': 'red', 'width': 4},
                        'thickness': 0.75,
                        'value': 70
                    }
                }
            ))
        
        fig.update_layout(
            title=f"{self.county_twin.county_name} Resilience Scorecard",
            grid={'rows': 2, 'columns': 3, 'pattern': "independent"},
            height=500
        )
        return fig
    
    def create_asset_condition_heatmap(self) -> go.Figure:
        """Create asset condition heatmap"""
        asset_conditions = {}
        for asset in self.county_twin.assets.values():
            asset_type = asset.get("asset_type", "unknown")
            if asset_type not in asset_conditions:
                asset_conditions[asset_type] = []
            asset_conditions[asset_type].append(asset.get("condition_index", 0.5))
        
        types = list(asset_conditions.keys())
        avg_conditions = [np.mean(conds) for conds in asset_conditions.values()]
        min_conditions = [np.min(conds) for conds in asset_conditions.values()]
        max_conditions = [np.max(conds) for conds in asset_conditions.values()]
        
        fig = go.Figure(data=[
            go.Bar(name='Average', x=types, y=avg_conditions, marker_color='#2ecc71'),
            go.Bar(name='Minimum', x=types, y=min_conditions, marker_color='#e74c3c'),
            go.Bar(name='Maximum', x=types, y=max_conditions, marker_color='#3498db')
        ])
        
        fig.update_layout(
            title="Asset Condition by Type",
            xaxis_title="Asset Type",
            yaxis_title="Condition Index",
            barmode='group',
            height=400
        )
        return fig
    
    def create_predictive_maintenance_chart(self, predictions: List[Dict]) -> go.Figure:
        """Create predictive maintenance visualization"""
        if not predictions:
            return go.Figure()
        
        sorted_preds = sorted(predictions, key=lambda x: x['failure_probability'], reverse=True)[:20]
        asset_ids = [p.get('asset_id', 'unknown')[:15] for p in sorted_preds]
        probabilities = [p['failure_probability'] for p in sorted_preds]
        priorities = [p.get('priority', 'medium') for p in sorted_preds]
        
        colors = ['#e74c3c' if p == 'critical' else '#f39c12' if p == 'high' else '#3498db' for p in priorities]
        
        fig = go.Figure(data=[
            go.Bar(
                x=asset_ids, y=probabilities,
                marker_color=colors,
                text=[f"{p:.1%}" for p in probabilities],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Top 20 Assets by Failure Probability",
            xaxis_title="Asset ID",
            yaxis_title="Failure Probability",
            yaxis=dict(tickformat='.0%'),
            height=500
        )
        return fig
    
    def _condition_to_color(self, condition: float) -> str:
        """Convert condition index to color"""
        if condition >= 0.8:
            return '#1a9850'
        elif condition >= 0.6:
            return '#91cf60'
        elif condition >= 0.4:
            return '#fee08b'
        elif condition >= 0.2:
            return '#fc8d59'
        else:
            return '#d73027'
    
    def _score_to_color(self, score: float) -> str:
        """Convert score to color"""
        if score >= 0.7:
            return '#27ae60'
        elif score >= 0.4:
            return '#f39c12'
        else:
            return '#e74c3c'
