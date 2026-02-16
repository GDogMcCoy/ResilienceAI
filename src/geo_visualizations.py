"""
Advanced Geospatial Visualizations for ResilienceAI
Choropleth maps, hexbin aggregations, and 3D visualizations
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import json


class GeoVisualizer:
    """
    Advanced geospatial visualization components
    """
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.color_scales = {
            'risk': ['#2ecc71', '#f1c40f', '#e67e22', '#e74c3c', '#8e44ad'],
            'population': ['#3498db', '#2980b9', '#8e44ad', '#c0392b'],
            'vulnerability': ['#27ae60', '#f39c12', '#d35400', '#c0392b']
        }
    
    def create_choropleth_map(self, value_column: str = 'risk_score',
                             geojson_url: str = None,
                             locations_column: str = 'fips',
                             title: str = "Risk by County") -> go.Figure:
        """
        Create a choropleth map using US counties GeoJSON
        """
        # Use US counties GeoJSON from public source
        if geojson_url is None:
            geojson_url = "https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json"
        
        # Ensure FIPS is string and zero-padded
        plot_df = self.df.copy()
        plot_df[locations_column] = plot_df[locations_column].astype(str).str.zfill(5)
        
        fig = px.choropleth(
            plot_df,
            geojson=geojson_url,
            locations=locations_column,
            color=value_column,
            color_continuous_scale=self.color_scales['risk'],
            scope="usa",
            labels={value_column: value_column.replace('_', ' ').title()},
            title=title,
            hover_data=['county_name', 'total_population', 'risk_level'] if all(col in plot_df.columns for col in ['county_name', 'total_population', 'risk_level']) else None
        )
        
        fig.update_layout(
            geo=dict(
                showlakes=True,
                lakecolor='rgb(255, 255, 255)',
                showsubunits=True,
                subunitcolor='rgb(200, 200, 200)',
                subunitwidth=0.5
            ),
            margin={"r":0,"t":50,"l":0,"b":0},
            height=700
        )
        
        return fig
    
    def create_hexbin_map(self, value_column: str = 'risk_score',
                         hex_resolution: int = 3,
                         title: str = "Risk Distribution (Hexbin)") -> go.Figure:
        """
        Create a hexbin aggregation map using H3 hexagons
        Falls back to 2D histogram if H3 not available
        """
        try:
            import h3
            has_h3 = True
        except ImportError:
            has_h3 = False
        
        if has_h3 and 'latitude' in self.df.columns and 'longitude' in self.df.columns:
            # Create H3 hexagons
            self.df['h3_index'] = self.df.apply(
                lambda row: h3.latlng_to_cell(row['latitude'], row['longitude'], hex_resolution)
                if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude'))
                else None, axis=1
            )
            
            # Aggregate by hexagon
            hex_data = self.df.groupby('h3_index').agg({
                value_column: 'mean',
                'county_name': 'count',
                'latitude': 'mean',
                'longitude': 'mean'
            }).reset_index()
            
            hex_data = hex_data.rename(columns={'county_name': 'county_count'})
            
            # Create scatter map with hexagon-like markers
            fig = px.scatter_mapbox(
                hex_data,
                lat='latitude',
                lon='longitude',
                color=value_column,
                size='county_count',
                color_continuous_scale=self.color_scales['risk'],
                zoom=3,
                height=700,
                title=title,
                hover_data=['county_count', 'h3_index']
            )
            
            fig.update_layout(mapbox_style="carto-darkmatter")
            
        else:
            # Fallback to 2D histogram/contour
            if 'latitude' in self.df.columns and 'longitude' in self.df.columns:
                fig = px.density_mapbox(
                    self.df,
                    lat='latitude',
                    lon='longitude',
                    z=value_column,
                    radius=20,
                    zoom=3,
                    height=700,
                    title=title,
                    color_continuous_scale=self.color_scales['risk']
                )
                fig.update_layout(mapbox_style="carto-darkmatter")
            else:
                # Final fallback to regular scatter
                fig = px.scatter_mapbox(
                    self.df,
                    lat='latitude',
                    lon='longitude',
                    color=value_column,
                    color_continuous_scale=self.color_scales['risk'],
                    zoom=3,
                    height=700,
                    title=title
                )
                fig.update_layout(mapbox_style="carto-positron")
        
        return fig
    
    def create_3d_risk_landscape(self, value_column: str = 'risk_score') -> go.Figure:
        """
        Create a 3D scatter plot of risk dots on a 2D map base.
        Ensures a grounded horizontal axis and high-resolution representation.
        """
        if 'latitude' not in self.df.columns or 'longitude' not in self.df.columns:
            return None
        
        plot_df = self.df.copy()
        
        # Create 3D Scatter
        fig = go.Figure(data=[go.Scatter3d(
            x=plot_df['longitude'],
            y=plot_df['latitude'],
            z=plot_df[value_column],
            mode='markers',
            marker=dict(
                size=4,
                color=plot_df[value_column],
                colorscale='RdYlGn_r',
                opacity=0.8,
                showscale=True,
                colorbar=dict(title=value_column.replace('_', ' ').title())
            ),
            text=plot_df['county_name'],
            hoverinfo='text+z'
        )])

        # Add an opaque base layer (flat map)
        fig.add_trace(go.Scatter3d(
            x=plot_df['longitude'],
            y=plot_df['latitude'],
            z=np.zeros(len(plot_df)),
            mode='markers',
            marker=dict(
                size=2,
                color='rgba(100, 100, 100, 0.2)',
                opacity=0.2
            ),
            hoverinfo='skip'
        ))
        
        fig.update_layout(
            title=f'County Risk Landscape (3D Projection)',
            scene=dict(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                zaxis_title='Risk Level',
                aspectratio=dict(x=1, y=1, z=0.5),
                bgcolor='rgba(0,0,0,0)'
            ),
            margin=dict(l=0, r=0, b=0, t=50),
            height=800,
            template="plotly_dark"
        )
        
        return fig
    
    def create_state_choropleth(self, state_abbr: str, value_column: str = 'risk_score') -> go.Figure:
        """
        Create a detailed choropleth for a single state
        """
        # Filter to state
        state_df = self.df[self.df['county_name'].str.contains(f", {state_abbr}$", na=False)]
        
        if len(state_df) == 0:
            return None
        
        # Create choropleth focused on state
        fig = px.choropleth(
            state_df,
            geojson="https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json",
            locations='fips',
            color=value_column,
            color_continuous_scale=self.color_scales['risk'],
            scope="usa",
            title=f"{state_abbr} County {value_column.replace('_', ' ').title()}"
        )
        
        # Zoom to state (approximate center)
        if 'latitude' in state_df.columns and 'longitude' in state_df.columns:
            center_lat = state_df['latitude'].mean()
            center_lon = state_df['longitude'].mean()
            fig.update_geos(center=dict(lat=center_lat, lon=center_lon), projection_scale=5)
        
        fig.update_layout(height=700, margin={"r":0,"t":50,"l":0,"b":0})
        
        return fig
    
    def create_heatmap(self, x_column: str = 'longitude', y_column: str = 'latitude',
                      value_column: str = 'risk_score') -> go.Figure:
        """
        Create a 2D heatmap of risk
        """
        if x_column not in self.df.columns or y_column not in self.df.columns:
            return None
        
        # Create 2D histogram/heatmap
        fig = px.density_heatmap(
            self.df,
            x=x_column,
            y=y_column,
            z=value_column,
            nbinsx=50,
            nbinsy=50,
            color_continuous_scale=self.color_scales['risk'],
            title=f"{value_column.replace('_', ' ').title()} Heatmap"
        )
        
        fig.update_layout(height=700)
        
        return fig


# Deck.gl visualization component (for advanced users)
def create_deckgl_map(df: pd.DataFrame, value_column: str = 'risk_score'):
    """
    Create a Deck.gl visualization (requires pydeck)
    """
    try:
        import pydeck as pdk
        
        # Prepare data
        plot_df = df[['latitude', 'longitude', value_column, 'county_name']].dropna()
        
        layer = pdk.Layer(
            'HeatmapLayer',
            data=plot_df,
            get_position=['longitude', 'latitude'],
            get_weight=value_column,
            radius_pixels=50,
            intensity=1,
            threshold=0.05
        )
        
        view_state = pdk.ViewState(
            latitude=plot_df['latitude'].mean(),
            longitude=plot_df['longitude'].mean(),
            zoom=3,
            pitch=0
        )
        
        deck = pdk.Deck(
            layers=[layer],
            initial_view_state=view_state,
            tooltip={
                'html': '<b>{county_name}</b><br/>Risk: {' + value_column + '}',
                'style': {'color': 'white'}
            }
        )
        
        return deck
    except ImportError:
        return None


# Streamlit component wrappers
def render_choropleth_tab(df: pd.DataFrame):
    """Render choropleth map in Streamlit"""
    st.subheader("🗺️ County Choropleth Map")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        value_col = st.selectbox(
            "Color by",
            ['risk_score', 'vulnerability_index', 'isolation_index', 'poverty_pct', 'elderly_pct'],
            index=0
        )
        
        show_all = st.checkbox("Show all US counties", value=True)
        
        if not show_all:
            states = sorted(df['county_name'].str.extract(r', ([A-Z]{2})$')[0].dropna().unique())
            selected_state = st.selectbox("Select State", states)
        else:
            selected_state = None
    
    with col2:
        viz = GeoVisualizer(df)
        
        if selected_state:
            fig = viz.create_state_choropleth(selected_state, value_col)
        else:
            fig = viz.create_choropleth_map(value_col)
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Could not create map")


def render_hexbin_tab(df: pd.DataFrame):
    """Render hexbin map in Streamlit"""
    st.subheader("⬡ Hexbin Aggregation Map")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        value_col = st.selectbox(
            "Aggregate by",
            ['risk_score', 'vulnerability_index', 'total_population'],
            index=0,
            key='hexbin_value'
        )
        
        aggregation = st.radio(
            "Aggregation",
            ['mean', 'sum', 'count'],
            index=0
        )
    
    with col2:
        viz = GeoVisualizer(df)
        fig = viz.create_hexbin_map(value_col)
        
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("Could not create hexbin map")


def render_3d_landscape_tab(df: pd.DataFrame):
    """Render 3D landscape in Streamlit"""
    st.subheader("🏔️ 3D Risk Landscape")
    
    value_col = st.selectbox(
        "Elevation by",
        ['risk_score', 'vulnerability_index', 'isolation_index'],
        index=0,
        key='3d_value'
    )
    
    viz = GeoVisualizer(df)
    fig = viz.create_3d_risk_landscape(value_col)
    
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("3D landscape requires latitude/longitude data")
