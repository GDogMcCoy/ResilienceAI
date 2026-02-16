"""
ResilienceAI - Advanced 3D Data Visualization Module
Enhanced 3D visualizations using PyDeck (Deck.gl) and Plotly
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass

try:
    import pydeck as pdk
    HAS_PYDECK = True
except ImportError:
    HAS_PYDECK = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False


@dataclass
class VisualizationConfig:
    """Configuration for 3D visualizations."""
    # Tower settings
    tower_radius_multiplier: float = 1.0
    tower_height_multiplier: float = 50000
    tower_opacity: float = 0.85
    
    # Hexagon settings
    hexagon_radius: int = 50000  # meters
    hexagon_height_multiplier: float = 100
    
    # Color schemes
    color_low: List[int] = None
    color_med: List[int] = None
    color_high: List[int] = None
    
    def __post_init__(self):
        if self.color_low is None:
            self.color_low = [39, 174, 96, 200]    # Green
        if self.color_med is None:
            self.color_med = [255, 235, 59, 200]   # Yellow
        if self.color_high is None:
            self.color_high = [231, 76, 60, 200]   # Red


def risk_to_gradient_color(score: float, config: VisualizationConfig = None) -> List[int]:
    """Convert risk score to smooth gradient color."""
    if config is None:
        config = VisualizationConfig()
    
    if score < 0.33:
        t = score / 0.33
        return [
            int(config.color_low[0] + (config.color_med[0] - config.color_low[0]) * t),
            int(config.color_low[1] + (config.color_med[1] - config.color_low[1]) * t),
            int(config.color_low[2] + (config.color_med[2] - config.color_low[2]) * t),
            config.color_low[3]
        ]
    elif score < 0.67:
        t = (score - 0.33) / 0.34
        return [
            int(config.color_med[0] + (config.color_high[0] - config.color_med[0]) * t),
            int(config.color_med[1] + (config.color_high[1] - config.color_med[1]) * t),
            int(config.color_med[2] + (config.color_high[2] - config.color_med[2]) * t),
            config.color_med[3]
        ]
    else:
        # Deep red for extreme risk
        t = min(1.0, (score - 0.67) / 0.33)
        return [
            int(config.color_high[0] + (139 - config.color_high[0]) * t),  # Towards dark red
            int(config.color_high[1] * (1 - t)),
            int(config.color_high[2] * (1 - t)),
            config.color_high[3]
        ]


def prepare_data_for_3d(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare county data for 3D visualization."""
    map_df = df.dropna(subset=["latitude", "longitude", "risk_score"]).copy()
    
    # Filter to continental US
    map_df = map_df[
        (map_df["latitude"] > 24) & (map_df["latitude"] < 50) &
        (map_df["longitude"] > -130) & (map_df["longitude"] < -65)
    ].copy()
    
    if len(map_df) == 0:
        return map_df
    
    config = VisualizationConfig()
    
    # Risk-based color
    map_df["color"] = map_df["risk_score"].apply(
        lambda x: risk_to_gradient_color(x, config)
    )
    
    # Multi-dimensional elevation (composite score)
    # Combine risk_score with other factors for tower height
    map_df["elevation"] = map_df["risk_score"] * config.tower_height_multiplier
    
    # Population-weighted elevation for extra visual encoding
    if "total_population" in map_df.columns:
        pop_normalized = (map_df["total_population"] - map_df["total_population"].min()) / \
                        (map_df["total_population"].max() - map_df["total_population"].min() + 1e-10)
        map_df["elevation_weighted"] = map_df["elevation"] * (1 + 0.3 * pop_normalized)
    else:
        map_df["elevation_weighted"] = map_df["elevation"]
    
    # Radius based on population (visual importance)
    if "total_population" in map_df.columns:
        pop_log = np.log1p(map_df["total_population"])
        map_df["radius"] = 5000 + (pop_log / pop_log.max()) * 15000
    else:
        map_df["radius"] = 8000
    
    # Create rich tooltip data
    map_df["tooltip_text"] = map_df.apply(create_tooltip_text, axis=1)
    
    return map_df


def create_tooltip_text(row: pd.Series) -> str:
    """Create rich HTML tooltip text for a county."""
    lines = [f"<b>{row.get('county_name', 'Unknown')}</b>"]
    
    if "risk_score" in row:
        lines.append(f"Risk Score: <b>{row['risk_score']:.3f}</b>")
    if "risk_level" in row:
        lines.append(f"Risk Level: <b>{row['risk_level']}</b>")
    if "total_population" in row:
        lines.append(f"Population: {row['total_population']:,.0f}")
    if "vulnerability_index" in row:
        lines.append(f"Vulnerability: {row['vulnerability_index']:.3f}")
    if "isolation_index" in row:
        lines.append(f"Isolation: {row['isolation_index']:.3f}")
    if "disaster_count" in row:
        lines.append(f"Disasters: {row['disaster_count']:.0f}")
    if "compound_risk_count" in row:
        lines.append(f"Risk Dimensions: {row['compound_risk_count']:.0f}")
    if "dist_nearest_hospitals_km" in row:
        lines.append(f"Nearest Hospital: {row['dist_nearest_hospitals_km']:.1f} km")
    
    return "<br/>".join(lines)


def create_enhanced_column_layer(df: pd.DataFrame, config: VisualizationConfig = None) -> Optional[Any]:
    """Create enhanced PyDeck ColumnLayer with multi-dimensional encoding."""
    if not HAS_PYDECK or len(df) == 0:
        return None
    
    if config is None:
        config = VisualizationConfig()
    
    return pdk.Layer(
        "ColumnLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_elevation="elevation_weighted",
        elevation_scale=1,
        get_radius="radius",
        radius_scale=1,
        get_fill_color="color",
        get_line_color=[255, 255, 255, 50],
        line_width_min_pixels=1,
        pickable=True,
        auto_highlight=True,
        extruded=True,
        coverage=1,
        material={
            "ambient": 0.64,
            "diffuse": 0.8,
            "shininess": 32,
            "specularColor": [255, 255, 255]
        }
    )


def create_heatmap_layer(df: pd.DataFrame, weight_column: str = "risk_score") -> Optional[Any]:
    """Create HeatmapLayer showing risk density."""
    if not HAS_PYDECK or len(df) == 0 or weight_column not in df.columns:
        return None
    
    return pdk.Layer(
        "HeatmapLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_weight=weight_column,
        radius_pixels=50,
        intensity=1,
        threshold=0.05,
        color_range=[
            [39, 174, 96, 50],    # Low - green
            [255, 235, 59, 100],  # Medium - yellow
            [231, 76, 60, 150],   # High - red
            [139, 0, 0, 200],     # Extreme - dark red
        ]
    )


def create_hexagon_layer(df: pd.DataFrame, config: VisualizationConfig = None) -> Optional[Any]:
    """Create HexagonLayer for aggregate risk visualization."""
    if not HAS_PYDECK or len(df) == 0:
        return None
    
    if config is None:
        config = VisualizationConfig()
    
    return pdk.Layer(
        "HexagonLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_elevation_value="risk_score",
        get_color_value="risk_score",
        radius=config.hexagon_radius,
        elevation_scale=config.hexagon_height_multiplier,
        elevation_range=[0, 1000],
        extruded=True,
        coverage=0.8,
        upper_percentile=100,
        color_range=[
            [39, 174, 96, 200],
            [255, 235, 59, 200],
            [231, 76, 60, 200],
            [139, 0, 0, 200],
        ],
        pickable=True,
        auto_highlight=True,
    )


def create_text_layer(df: pd.DataFrame, min_risk_threshold: float = 0.5) -> Optional[Any]:
    """Create TextLayer for labeling high-risk counties."""
    if not HAS_PYDECK or len(df) == 0:
        return None
    
    # Only label high-risk counties
    high_risk = df[df["risk_score"] >= min_risk_threshold].copy()
    if len(high_risk) == 0:
        return None
    
    # Extract short name
    high_risk["short_name"] = high_risk["county_name"].str.replace(", .*", "", regex=True)
    
    return pdk.Layer(
        "TextLayer",
        data=high_risk,
        get_position=["longitude", "latitude"],
        get_text="short_name",
        get_size=14,
        get_color=[255, 255, 255, 200],
        get_angle=0,
        get_text_anchor="middle",
        get_alignment_baseline="bottom",
        get_pixel_offset=[0, -10],
        billboard=True,
        font_family="Monaco, monospace",
        font_weight="bold",
    )


def create_scatterplot_layer(df: pd.DataFrame) -> Optional[Any]:
    """Create ScatterplotLayer for additional context."""
    if not HAS_PYDECK or len(df) == 0:
        return None
    
    return pdk.Layer(
        "ScatterplotLayer",
        data=df,
        get_position=["longitude", "latitude"],
        get_radius="radius",
        get_fill_color="color",
        get_line_color=[255, 255, 255, 100],
        line_width_min_pixels=1,
        stroked=True,
        filled=True,
        opacity=0.3,
        pickable=True,
    )


def create_deck_with_layers(
    layers: List[Any],
    initial_view: Dict = None,
    tooltip: Dict = None,
    map_style: str = "dark"
) -> Optional[Any]:
    """Create a PyDeck deck with the given layers."""
    if not HAS_PYDECK:
        return None
    
    if initial_view is None:
        initial_view = {
            "latitude": 39.5,
            "longitude": -98.35,
            "zoom": 3.5,
            "pitch": 45,
            "bearing": 0,
        }
    
    view_state = pdk.ViewState(**initial_view)
    
    # Map styles
    map_styles = {
        "dark": "mapbox://styles/mapbox/dark-v10",
        "light": "mapbox://styles/mapbox/light-v10",
        "satellite": "mapbox://styles/mapbox/satellite-v9",
        "streets": "mapbox://styles/mapbox/streets-v11",
    }
    
    if tooltip is None:
        tooltip = {
            "html": "{tooltip_text}",
            "style": {
                "backgroundColor": "#1A1F2E",
                "color": "#E0E0E0",
                "padding": "10px",
                "borderRadius": "5px",
                "border": "1px solid #4FC3F7",
            }
        }
    
    return pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        tooltip=tooltip,
        map_style=map_styles.get(map_style, map_styles["dark"]),
    )


def create_plotly_3d_scatter(
    df: pd.DataFrame,
    color_by: str = "risk_level",
    size_by: str = "total_population"
) -> Optional[Any]:
    """Create an interactive 3D scatter plot using Plotly."""
    if not HAS_PLOTLY or len(df) == 0:
        return None
    
    # Filter for better performance
    plot_df = df.sample(min(2000, len(df))) if len(df) > 2000 else df.copy()
    
    # Normalize size
    if size_by in plot_df.columns:
        plot_df["size_normalized"] = np.sqrt(plot_df[size_by]) / 10
    else:
        plot_df["size_normalized"] = 5
    
    # Color mapping
    color_discrete_map = {
        "Low": "#27ae60",
        "Medium": "#f39c12",
        "High": "#e74c3c"
    }
    
    # Create 3D scatter
    fig = go.Figure(data=[go.Scatter3d(
        x=plot_df["longitude"],
        y=plot_df["latitude"],
        z=plot_df["risk_score"] if "risk_score" in plot_df.columns else [0.5] * len(plot_df),
        mode="markers",
        marker=dict(
            size=plot_df["size_normalized"],
            color=plot_df["risk_score"] if "risk_score" in plot_df.columns else "blue",
            colorscale="RdYlGn_r",
            cmin=0,
            cmax=1,
            opacity=0.7,
            line=dict(color="white", width=1)
        ),
        text=plot_df.apply(lambda row: f"{row.get('county_name', 'Unknown')}<br>" +
                                       f"Risk: {row.get('risk_score', 0):.3f}<br>" +
                                       f"Pop: {row.get('total_population', 0):,.0f}", axis=1),
        hoverinfo="text",
        name="Counties"
    )])
    
    fig.update_layout(
        title=dict(
            text="3D Risk Landscape (Longitude × Latitude × Risk Score)",
            font=dict(color="#E0E0E0", size=16)
        ),
        scene=dict(
            xaxis=dict(title="Longitude", backgroundcolor="#0E1117", gridcolor="#1E293B", color="#E0E0E0"),
            yaxis=dict(title="Latitude", backgroundcolor="#0E1117", gridcolor="#1E293B", color="#E0E0E0"),
            zaxis=dict(title="Risk Score", backgroundcolor="##0E1117", gridcolor="#1E293B", color="#E0E0E0", range=[0, 1]),
            bgcolor="#0E1117",
            camera=dict(eye=dict(x=1.5, y=1.5, z=0.8))
        ),
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E0E0E0"),
        margin=dict(l=0, r=0, b=0, t=40),
        height=600
    )
    
    return fig


def create_plotly_3d_surface(df: pd.DataFrame) -> Optional[Any]:
    """Create a 3D surface plot showing risk landscape."""
    if not HAS_PLOTLY or len(df) == 0:
        return None
    
    # Create grid for surface interpolation
    from scipy.interpolate import griddata
    
    # Sample for performance
    plot_df = df.sample(min(1000, len(df))) if len(df) > 1000 else df.copy()
    
    # Create grid
    xi = np.linspace(plot_df["longitude"].min(), plot_df["longitude"].max(), 50)
    yi = np.linspace(plot_df["latitude"].min(), plot_df["latitude"].max(), 50)
    xi, yi = np.meshgrid(xi, yi)
    
    # Interpolate
    zi = griddata(
        (plot_df["longitude"], plot_df["latitude"]),
        plot_df["risk_score"],
        (xi, yi),
        method="cubic",
        fill_value=0
    )
    
    fig = go.Figure(data=[go.Surface(
        x=xi, y=yi, z=zi,
        colorscale="RdYlGn_r",
        cmin=0, cmax=1,
        showscale=True,
        colorbar=dict(title="Risk Score", x=0.95),
        lighting=dict(
            ambient=0.6,
            diffuse=0.8,
            roughness=0.4,
            specular=0.5
        )
    )])
    
    fig.update_layout(
        title=dict(
            text="Risk Landscape Surface (Interpolated)",
            font=dict(color="#E0E0E0", size=16)
        ),
        scene=dict(
            xaxis=dict(title="Longitude", backgroundcolor="#0E1117", gridcolor="#1E293B", color="#E0E0E0"),
            yaxis=dict(title="Latitude", backgroundcolor="#0E1117", gridcolor="#1E293B", color="#E0E0E0"),
            zaxis=dict(title="Risk Score", backgroundcolor="#0E1117", gridcolor="#1E293B", color="#E0E0E0"),
            bgcolor="#0E1117",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0))
        ),
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E0E0E0"),
        margin=dict(l=0, r=0, b=0, t=40),
        height=600
    )
    
    return fig


def create_risk_comparison_3d(df: pd.DataFrame) -> Optional[Any]:
    """Create 3D comparison of multiple risk dimensions."""
    if not HAS_PLOTLY or len(df) == 0:
        return None
    
    # Select metrics for 3D axes
    metrics = ["risk_score", "vulnerability_index", "isolation_index"]
    available_metrics = [m for m in metrics if m in df.columns]
    
    if len(available_metrics) < 3:
        return None
    
    # Sample for performance
    plot_df = df.sample(min(1500, len(df))) if len(df) > 1500 else df.copy()
    
    # Create figure with subplots
    fig = make_subplots(
        rows=1, cols=2,
        specs=[[{"type": "scatter3d"}, {"type": "scatter3d"}]],
        subplot_titles=("Risk × Vulnerability × Isolation", "Risk × Population × Disasters")
    )
    
    # First 3D scatter
    fig.add_trace(go.Scatter3d(
        x=plot_df["risk_score"],
        y=plot_df["vulnerability_index"] if "vulnerability_index" in plot_df.columns else plot_df["risk_score"],
        z=plot_df["isolation_index"] if "isolation_index" in plot_df.columns else plot_df["risk_score"],
        mode="markers",
        marker=dict(
            size=4,
            color=plot_df["risk_score"],
            colorscale="RdYlGn_r",
            cmin=0, cmax=1,
            opacity=0.6
        ),
        text=plot_df["county_name"],
        hovertemplate="<b>%{text}</b><br>Risk: %{x:.3f}<br>Vuln: %{y:.3f}<br>Iso: %{z:.3f}",
        name="Counties"
    ), row=1, col=1)
    
    # Second 3D scatter - different dimensions
    fig.add_trace(go.Scatter3d(
        x=plot_df["risk_score"],
        y=np.log1p(plot_df["total_population"]) if "total_population" in plot_df.columns else plot_df["risk_score"],
        z=plot_df["disaster_count"] if "disaster_count" in plot_df.columns else [0] * len(plot_df),
        mode="markers",
        marker=dict(
            size=4,
            color=plot_df["risk_score"],
            colorscale="RdYlGn_r",
            cmin=0, cmax=1,
            opacity=0.6
        ),
        text=plot_df["county_name"],
        hovertemplate="<b>%{text}</b><br>Risk: %{x:.3f}<br>LogPop: %{y:.1f}<br>Disasters: %{z}",
        name="Counties"
    ), row=1, col=2)
    
    fig.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E0E0E0"),
        height=500,
        showlegend=False,
        title=dict(
            text="Multi-Dimensional Risk Analysis",
            font=dict(color="#E0E0E0", size=16)
        )
    )
    
    # Update scenes
    fig.update_scenes(
        bgcolor="#0E1117",
        xaxis=dict(gridcolor="#1E293B", color="#E0E0E0"),
        yaxis=dict(gridcolor="#1E293B", color="#E0E0E0"),
        zaxis=dict(gridcolor="#1E293B", color="#E0E0E0")
    )
    
    return fig


class Visualization3D:
    """Main class for creating 3D visualizations."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = prepare_data_for_3d(df)
        self.config = VisualizationConfig()
    
    def create_enhanced_tower_map(
        self,
        view_pitch: int = 45,
        view_bearing: int = 0,
        view_zoom: float = 3.5,
        show_labels: bool = True,
        show_heatmap: bool = False
    ) -> Optional[Any]:
        """Create the main enhanced 3D tower map."""
        if not HAS_PYDECK or len(self.df) == 0:
            return None
        
        layers = []
        
        # Add heatmap layer if requested
        if show_heatmap:
            heatmap = create_heatmap_layer(self.df)
            if heatmap:
                layers.append(heatmap)
        
        # Main column layer
        column_layer = create_enhanced_column_layer(self.df, self.config)
        if column_layer:
            layers.append(column_layer)
        
        # Add scatterplot for context
        scatter = create_scatterplot_layer(self.df)
        if scatter:
            layers.append(scatter)
        
        # Add text labels for high-risk counties
        if show_labels:
            text_layer = create_text_layer(self.df, min_risk_threshold=0.6)
            if text_layer:
                layers.append(text_layer)
        
        initial_view = {
            "latitude": 39.5,
            "longitude": -98.35,
            "zoom": view_zoom,
            "pitch": view_pitch,
            "bearing": view_bearing,
        }
        
        return create_deck_with_layers(layers, initial_view)
    
    def create_hexagon_map(
        self,
        view_pitch: int = 55,
        view_zoom: float = 3.5
    ) -> Optional[Any]:
        """Create hexagon aggregation map."""
        if not HAS_PYDECK or len(self.df) == 0:
            return None
        
        hex_layer = create_hexagon_layer(self.df, self.config)
        
        initial_view = {
            "latitude": 39.5,
            "longitude": -98.35,
            "zoom": view_zoom,
            "pitch": view_pitch,
            "bearing": 0,
        }
        
        return create_deck_with_layers([hex_layer], initial_view)
    
    def create_plotly_3d_views(self) -> Dict[str, Any]:
        """Create multiple Plotly 3D views."""
        views = {}
        
        if HAS_PLOTLY and len(self.df) > 0:
            views["scatter_3d"] = create_plotly_3d_scatter(self.df)
            views["surface"] = create_plotly_3d_surface(self.df)
            views["comparison"] = create_risk_comparison_3d(self.df)
        
        return views


def get_visualization_help() -> str:
    """Return help text about the visualization options."""
    return """
    ## 3D Visualization Guide
    
    ### PyDeck (Deck.gl) Views:
    - **Enhanced Tower Map**: 3D columns with height = risk score, radius = population, color = risk gradient
    - **Hexagon Map**: Aggregate view showing risk density across regions
    - **Heatmap Layer**: Overlay showing concentration of high-risk areas
    
    ### Plotly 3D Views:
    - **3D Scatter**: Interactive scatter plot (Longitude × Latitude × Risk)
    - **Surface Plot**: Interpolated risk landscape surface
    - **Multi-Dimensional**: Compare different risk metrics in 3D space
    
    ### Visual Encodings:
    - **Height**: Risk score (elevated for population weighting)
    - **Color**: Smooth gradient from green (low) to red (high)
    - **Radius**: Population size (larger = more populous)
    - **Opacity**: Semi-transparent to show overlap
    
    ### Interactions:
    - Click and drag to rotate
    - Scroll to zoom
    - Hover for detailed county information
    - Pitch and bearing sliders for custom views
    """
