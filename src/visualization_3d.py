"""
ResilienceAI - Advanced 3D Data Visualization Module
Enhanced 3D visualizations using PyDeck (Deck.gl) and Plotly
Includes topological manifold surfaces for smooth risk landscapes
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

try:
    from scipy.interpolate import griddata, Rbf, CloughTocher2DInterpolator
    from scipy.ndimage import gaussian_filter
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


@dataclass
class VisualizationConfig:
    """Configuration for 3D visualizations."""
    # Tower settings
    tower_radius_multiplier: float = 1.0
    tower_height_multiplier: float = 50000
    tower_opacity: float = 0.85
    
    # Surface/Manifold settings
    surface_resolution: int = 100  # Grid resolution for interpolation
    surface_smoothness: float = 2.0  # Gaussian smoothing sigma
    height_scale: float = 0.3  # Z-axis exaggeration (0-1)
    
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


def create_interpolated_surface(
    df: pd.DataFrame,
    value_column: str = "risk_score",
    resolution: int = 100,
    smoothing: float = 2.0,
    method: str = "rbf"
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create a smooth interpolated surface from scattered data points.
    Returns x_grid, y_grid, z_surface for 3D plotting.
    """
    if not HAS_SCIPY or len(df) == 0:
        return None, None, None
    
    # Extract coordinates and values
    x = df["longitude"].values
    y = df["latitude"].values
    z = df[value_column].values
    
    # Create regular grid
    xi = np.linspace(x.min(), x.max(), resolution)
    yi = np.linspace(y.min(), y.max(), resolution)
    xi, yi = np.meshgrid(xi, yi)
    
    # Interpolation method
    if method == "rbf":
        # Radial Basis Function interpolation - very smooth
        try:
            rbf = Rbf(x, y, z, function="multiquadric", smooth=0.1)
            zi = rbf(xi, yi)
        except:
            # Fallback to griddata
            zi = griddata((x, y), z, (xi, yi), method="cubic", fill_value=0)
    elif method == "linear":
        zi = griddata((x, y), z, (xi, yi), method="linear", fill_value=0)
    else:
        zi = griddata((x, y), z, (xi, yi), method="cubic", fill_value=0)
    
    # Apply Gaussian smoothing for even smoother surface
    if smoothing > 0:
        zi = gaussian_filter(zi, sigma=smoothing)
    
    # Clip to valid range
    zi = np.clip(zi, 0, 1)
    
    return xi, yi, zi


def create_topological_manifold(
    df: pd.DataFrame,
    height_scale: float = 0.3,
    resolution: int = 100,
    show_surface: bool = True,
    show_wireframe: bool = False,
    show_counties: bool = True,
    colorscale: str = "RdYlGn_r"
) -> Optional[Any]:
    """
    Create a 3D topological manifold surface representing risk as energy landscape.
    Like SGD loss landscape with hills (high risk) and valleys (low risk).
    """
    if not HAS_PLOTLY or len(df) == 0:
        return None
    
    # Create interpolated surface
    xi, yi, zi = create_interpolated_surface(
        df, 
        value_column="risk_score",
        resolution=resolution,
        smoothing=2.0,
        method="rbf"
    )
    
    if xi is None:
        return None
    
    fig = go.Figure()
    
    # Main surface - the topological manifold
    if show_surface:
        fig.add_trace(go.Surface(
            x=xi,
            y=yi,
            z=zi * height_scale,  # Scale height for visual appeal
            colorscale=colorscale,
            cmin=0,
            cmax=1,
            showscale=True,
            colorbar=dict(
                title=dict(text="Risk Score", font=dict(color="#E0E0E0")),
                tickfont=dict(color="#E0E0E0"),
                x=0.95,
                thickness=20,
                len=0.8
            ),
            lighting=dict(
                ambient=0.6,
                diffuse=0.8,
                roughness=0.4,
                specular=0.5,
                fresnel=0.2
            ),
            lightposition=dict(x=100, y=100, z=1000),
            contours=dict(
                z=dict(
                    show=True,
                    usecolormap=True,
                    highlightcolor="#FFFFFF",
                    project_z=True,
                    size=0.05,
                    start=0,
                    end=height_scale
                )
            ),
            hovertemplate="Lon: %{x:.2f}<br>Lat: %{y:.2f}<br>Risk: %{z:.3f}<extra></extra>",
            name="Risk Landscape"
        ))
    
    # Wireframe overlay for structure visibility
    if show_wireframe:
        fig.add_trace(go.Surface(
            x=xi,
            y=yi,
            z=zi * height_scale,
            colorscale=[[0, "rgba(255,255,255,0.1)"], [1, "rgba(255,255,255,0.1)"]],
            showscale=False,
            contours=dict(
                x=dict(show=True, color="rgba(255,255,255,0.1)", width=1),
                y=dict(show=True, color="rgba(255,255,255,0.1)", width=1),
            ),
            hoverinfo="skip",
            name="Wireframe"
        ))
    
    # County markers on top of surface
    if show_counties:
        # Sample for performance
        sample_df = df.sample(min(500, len(df))) if len(df) > 500 else df.copy()
        
        # Calculate z-position for each county (on the surface)
        county_z = []
        for _, row in sample_df.iterrows():
            # Find nearest grid point
            lon_idx = np.argmin(np.abs(xi[0, :] - row["longitude"]))
            lat_idx = np.argmin(np.abs(yi[:, 0] - row["latitude"]))
            county_z.append(zi[lat_idx, lon_idx] * height_scale + 0.02)  # Slightly above surface
        
        fig.add_trace(go.Scatter3d(
            x=sample_df["longitude"],
            y=sample_df["latitude"],
            z=county_z,
            mode="markers",
            marker=dict(
                size=3,
                color=sample_df["risk_score"],
                colorscale=colorscale,
                cmin=0,
                cmax=1,
                opacity=0.8,
                line=dict(color="white", width=0.5)
            ),
            text=sample_df.apply(
                lambda row: f"{row.get('county_name', 'Unknown')}<br>Risk: {row.get('risk_score', 0):.3f}",
                axis=1
            ),
            hovertemplate="%{text}<extra></extra>",
            name="Counties"
        ))
    
    # Layout for dark theme
    fig.update_layout(
        title=dict(
            text="<b>Risk Landscape Topology</b><br><sup>3D Energy Surface - Hills = High Risk, Valleys = Low Risk</sup>",
            font=dict(color="#E0E0E0", size=18),
            x=0.5
        ),
        scene=dict(
            xaxis=dict(
                title="Longitude",
                backgroundcolor="#0E1117",
                gridcolor="#1E293B",
                color="#E0E0E0",
                showbackground=True,
                zerolinecolor="#4FC3F7"
            ),
            yaxis=dict(
                title="Latitude",
                backgroundcolor="#0E1117",
                gridcolor="#1E293B",
                color="#E0E0E0",
                showbackground=True,
                zerolinecolor="#4FC3F7"
            ),
            zaxis=dict(
                title="Risk Score",
                backgroundcolor="#0E1117",
                gridcolor="#1E293B",
                color="#E0E0E0",
                showbackground=True,
                zerolinecolor="#4FC3F7",
                range=[0, height_scale * 1.2]
            ),
            bgcolor="#0E1117",
            camera=dict(
                eye=dict(x=1.5, y=1.5, z=0.8),
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            ),
            aspectratio=dict(x=2, y=1.5, z=0.5),  # Flattened for better view
        ),
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E0E0E0", family="Inter, sans-serif"),
        margin=dict(l=0, r=0, b=0, t=60),
        height=700,
        showlegend=False,
        # Add rotation instructions
        annotations=[
            dict(
                text="Click & Drag to Rotate | Scroll to Zoom | Right-click to Pan",
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=-0.02,
                font=dict(color="#90A4AE", size=11)
            )
        ]
    )
    
    return fig


def create_multi_layer_topology(
    df: pd.DataFrame,
    metrics: List[str] = None,
    height_scale: float = 0.25
) -> Optional[Any]:
    """
    Create multiple topological surfaces stacked or side-by-side
    showing different risk dimensions.
    """
    if not HAS_PLOTLY or not HAS_SCIPY or len(df) == 0:
        return None
    
    if metrics is None:
        metrics = ["risk_score", "vulnerability_index", "isolation_index"]
    
    available_metrics = [m for m in metrics if m in df.columns]
    if len(available_metrics) == 0:
        return None
    
    # Create subplots for each metric
    n_metrics = len(available_metrics)
    fig = make_subplots(
        rows=1,
        cols=n_metrics,
        specs=[[{"type": "surface"}] * n_metrics],
        subplot_titles=[m.replace("_", " ").title() for m in available_metrics]
    )
    
    colorscales = ["RdYlGn_r", "Plasma", "Viridis"]
    
    for i, metric in enumerate(available_metrics):
        xi, yi, zi = create_interpolated_surface(
            df,
            value_column=metric,
            resolution=80,
            smoothing=2.0,
            method="rbf"
        )
        
        if xi is not None:
            fig.add_trace(
                go.Surface(
                    x=xi,
                    y=yi,
                    z=zi * height_scale,
                    colorscale=colorscales[i % len(colorscales)],
                    cmin=0,
                    cmax=1,
                    showscale=(i == 0),  # Only show colorbar for first
                    colorbar=dict(
                        title=dict(text="Score", font=dict(color="#E0E0E0")),
                        tickfont=dict(color="#E0E0E0"),
                        x=1.02,
                        thickness=15
                    ) if i == 0 else None,
                    lighting=dict(
                        ambient=0.6,
                        diffuse=0.8,
                        roughness=0.4,
                        specular=0.5
                    ),
                    contours=dict(
                        z=dict(
                            show=True,
                            usecolormap=True,
                            project_z=True,
                            size=0.05
                        )
                    ),
                    name=metric.replace("_", " ").title()
                ),
                row=1,
                col=i + 1
            )
    
    # Update all scenes
    for i in range(1, n_metrics + 1):
        fig.update_scenes(
            dict(
                xaxis=dict(
                    backgroundcolor="#0E1117",
                    gridcolor="#1E293B",
                    color="#E0E0E0",
                    showbackground=True
                ),
                yaxis=dict(
                    backgroundcolor="#0E1117",
                    gridcolor="#1E293B",
                    color="#E0E0E0",
                    showbackground=True
                ),
                zaxis=dict(
                    backgroundcolor="#0E1117",
                    gridcolor="#1E293B",
                    color="#E0E0E0",
                    showbackground=True,
                    range=[0, height_scale * 1.2]
                ),
                bgcolor="#0E1117",
                camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
                aspectratio=dict(x=2, y=1.5, z=0.5)
            ),
            row=1,
            col=i
        )
    
    fig.update_layout(
        title=dict(
            text="<b>Multi-Dimensional Risk Topology</b>",
            font=dict(color="#E0E0E0", size=18),
            x=0.5
        ),
        paper_bgcolor="#0E1117",
        font=dict(color="#E0E0E0"),
        height=600,
        margin=dict(l=0, r=50, b=0, t=50)
    )
    
    return fig


def create_gradient_flow_field(
    df: pd.DataFrame,
    height_scale: float = 0.2
) -> Optional[Any]:
    """
    Create a 3D visualization showing the gradient/flow of risk
    like a vector field showing how risk flows across geography.
    """
    if not HAS_PLOTLY or not HAS_SCIPY or len(df) == 0:
        return None
    
    # Create surface
    xi, yi, zi = create_interpolated_surface(df, resolution=50, smoothing=1.5)
    if xi is None:
        return None
    
    # Calculate gradients
    dy, dx = np.gradient(zi)
    
    # Subsample for vector field
    step = 5
    x_sample = xi[::step, ::step]
    y_sample = yi[::step, ::step]
    z_sample = zi[::step, ::step] * height_scale
    dx_sample = dx[::step, ::step] * 0.5  # Scale arrows
    dy_sample = dy[::step, ::step] * 0.5
    dz_sample = np.zeros_like(dx_sample)
    
    fig = go.Figure()
    
    # Surface
    fig.add_trace(go.Surface(
        x=xi,
        y=yi,
        z=zi * height_scale,
        colorscale="RdYlGn_r",
        cmin=0,
        cmax=1,
        showscale=True,
        opacity=0.7,
        name="Risk Surface"
    ))
    
    # Gradient vectors (arrows showing direction of steepest increase)
    fig.add_trace(go.Cone(
        x=x_sample.flatten(),
        y=y_sample.flatten(),
        z=z_sample.flatten(),
        u=dx_sample.flatten(),
        v=dy_sample.flatten(),
        w=dz_sample.flatten(),
        colorscale="Blues",
        showscale=False,
        sizemode="absolute",
        sizeref=0.5,
        opacity=0.6,
        name="Risk Gradient"
    ))
    
    fig.update_layout(
        title=dict(
            text="<b>Risk Gradient Flow Field</b><br><sup>Arrows show direction of steepest risk increase</sup>",
            font=dict(color="#E0E0E0", size=16),
            x=0.5
        ),
        scene=dict(
            xaxis=dict(title="Longitude", backgroundcolor="#0E1117", gridcolor="#1E293B", color="#E0E0E0"),
            yaxis=dict(title="Latitude", backgroundcolor="#0E1117", gridcolor="#1E293B", color="#E0E0E0"),
            zaxis=dict(title="Risk Score", backgroundcolor="#0E1117", gridcolor="#1E293B", color="#E0E0E0"),
            bgcolor="#0E1117",
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.0))
        ),
        paper_bgcolor="#0E1117",
        font=dict(color="#E0E0E0"),
        height=650,
        margin=dict(l=0, r=0, b=0, t=60)
    )
    
    return fig


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
            text="3D Risk Landscape (Longitude x Latitude x Risk Score)",
            font=dict(color="#E0E0E0", size=16)
        ),
        scene=dict(
            xaxis=dict(title="Longitude", backgroundcolor="#0E1117", gridcolor="#1E293B", color="#E0E0E0"),
            yaxis=dict(title="Latitude", backgroundcolor="#0E1117", gridcolor="#1E293B", color="#E0E0E0"),
            zaxis=dict(title="Risk Score", backgroundcolor="#0E1117", gridcolor="#1E293B", color="#E0E0E0", range=[0, 1]),
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
        subplot_titles=("Risk x Vulnerability x Isolation", "Risk x Population x Disasters")
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
    
    def create_topological_manifold_map(
        self,
        height_scale: float = 0.3,
        show_surface: bool = True,
        show_wireframe: bool = False,
        show_counties: bool = True
    ) -> Optional[Any]:
        """Create the topological manifold surface visualization."""
        if len(self.df) == 0:
            return None
        return create_topological_manifold(
            self.df,
            height_scale=height_scale,
            show_surface=show_surface,
            show_wireframe=show_wireframe,
            show_counties=show_counties
        )
    
    def create_multi_layer_topology(self, height_scale: float = 0.25) -> Optional[Any]:
        """Create multi-layer topology comparing different metrics."""
        if len(self.df) == 0:
            return None
        return create_multi_layer_topology(self.df, height_scale=height_scale)
    
    def create_gradient_flow_field(self, height_scale: float = 0.2) -> Optional[Any]:
        """Create gradient flow field visualization."""
        if len(self.df) == 0:
            return None
        return create_gradient_flow_field(self.df, height_scale=height_scale)
    
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
            views["comparison"] = create_risk_comparison_3d(self.df)
            views["manifold"] = self.create_topological_manifold_map()
            views["multi_layer"] = self.create_multi_layer_topology()
            views["gradient_flow"] = self.create_gradient_flow_field()
        
        return views


def get_visualization_help() -> str:
    """Return help text about the visualization options."""
    return """
    ## 3D Visualization Guide
    
    ### Topological Manifold (NEW!):
    - **Risk Landscape Surface**: Smooth interpolated surface like SGD loss landscape
    - **Energy Hills/Troughs**: High risk = hills (peaks), Low risk = valleys
    - **Contour Lines**: Visual elevation guides
    - **County Markers**: Actual county locations on the surface
    - **Fully Interactive**: Click & drag to rotate, scroll to zoom
    
    ### Multi-Layer Topology:
    - Compare Risk, Vulnerability, and Isolation as separate surfaces
    - Side-by-side comparison with synchronized views
    
    ### Gradient Flow Field:
    - Shows direction of steepest risk increase across geography
    - Cone arrows pointing "uphill" in risk landscape
    
    ### Traditional Views:
    - **Enhanced Towers**: Population-scaled columns with risk coloring
    - **Hexagon Aggregation**: Regional risk density
    - **Heatmap**: Concentration overlay
    - **3D Scatter**: Interactive point cloud
    
    ### Visual Encodings:
    - **Height**: Risk score (scaled for visual appeal)
    - **Color**: Smooth gradient Green -> Yellow -> Red -> Dark Red
    - **Surface**: Continuous interpolation between counties
    - **Contours**: Risk level boundaries
    
    ### Interactions:
    - Click & drag to rotate view
    - Scroll to zoom in/out
    - Right-click and drag to pan
    - Hover for county details
    """
