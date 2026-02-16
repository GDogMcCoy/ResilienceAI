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
    from scipy.interpolate import griddata, Rbf
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
    surface_resolution: int = 150  # Higher resolution for sharper peaks
    surface_smoothness: float = 0.8  # LESS smoothing = sharper peaks
    height_scale: float = 0.5  # Z-axis exaggeration
    
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


def get_state_borders() -> List[Dict]:
    """
    Get simplified US state border coordinates.
    Returns list of line segments for major state boundaries.
    """
    # Simplified state borders as line segments
    # Format: [(lon1, lat1), (lon2, lat2)] for each segment
    borders = []
    
    # Pacific Coast (CA, OR, WA)
    borders.extend([
        # California coast approximation
        (-124.2, 42.0, -124.2, 32.5),
        (-120.0, 42.0, -120.0, 39.0),  # CA-OR
        (-120.0, 39.0, -119.0, 39.0),  # CA-NV
        (-119.0, 39.0, -119.0, 35.0),  # CA-NV
        (-119.0, 35.0, -114.0, 35.0),  # CA-AZ
        # Washington
        (-124.7, 49.0, -124.7, 46.2),
        (-124.7, 46.2, -117.0, 46.2),  # WA-ID
        (-117.0, 46.2, -117.0, 49.0),  # WA-Canada
        # Oregon
        (-124.5, 46.2, -124.5, 42.0),
        (-117.0, 46.2, -117.0, 42.0),  # OR-ID
    ])
    
    # Mountain States
    borders.extend([
        # Montana
        (-116.0, 49.0, -104.0, 49.0),  # Canada border
        (-104.0, 49.0, -104.0, 45.0),  # MT-ND/SD
        (-116.0, 49.0, -116.0, 45.0),  # MT-ID
        # Idaho
        (-117.0, 49.0, -117.0, 42.0),
        (-117.0, 42.0, -111.0, 42.0),  # ID-UT
        (-111.0, 42.0, -111.0, 49.0),  # ID-WY
        # Nevada
        (-120.0, 42.0, -114.0, 42.0),  # NV-OR/ID
        (-114.0, 42.0, -114.0, 35.0),  # NV-AZ
        (-120.0, 35.0, -114.0, 35.0),  # NV-AZ
        # Utah
        (-114.0, 42.0, -109.0, 42.0),  # UT-ID/WY
        (-109.0, 42.0, -109.0, 37.0),  # UT-CO
        (-109.0, 37.0, -114.0, 37.0),  # UT-AZ
        # Arizona
        (-114.0, 37.0, -109.0, 37.0),  # AZ-NM
        (-109.0, 37.0, -109.0, 31.3),  # AZ-NM
        (-114.0, 35.0, -114.0, 32.5),  # AZ-CA
    ])
    
    # Great Plains
    borders.extend([
        # North Dakota
        (-104.0, 49.0, -97.0, 49.0),   # ND-Canada
        (-97.0, 49.0, -97.0, 46.0),    # ND-MN
        (-104.0, 46.0, -97.0, 46.0),   # ND-SD
        # South Dakota
        (-104.0, 46.0, -104.0, 43.0),  # SD-WY
        (-104.0, 43.0, -96.5, 43.0),   # SD-NE
        (-96.5, 43.0, -96.5, 46.0),    # SD-MN
        # Nebraska
        (-104.0, 43.0, -104.0, 40.0),  # NE-WY/CO
        (-104.0, 40.0, -95.0, 40.0),   # NE-IA
        (-95.0, 40.0, -95.0, 43.0),    # NE-IA/SD
        # Kansas
        (-102.0, 40.0, -94.6, 40.0),   # KS-MO
        (-94.6, 40.0, -94.6, 37.0),    # KS-MO/OK
        (-102.0, 37.0, -94.6, 37.0),   # KS-OK
        # Oklahoma
        (-103.0, 37.0, -103.0, 33.5),  # OK-TX
        (-103.0, 33.5, -94.5, 33.5),   # OK-TX/AR
        # Texas
        (-106.6, 32.0, -94.0, 32.0),   # TX-NM/LA
        (-106.6, 32.0, -106.6, 25.8),  # TX-Mexico
    ])
    
    # Midwest
    borders.extend([
        # Minnesota
        (-97.0, 49.0, -89.5, 49.0),    # MN-Canada
        (-89.5, 49.0, -89.5, 43.5),    # MN-WI
        (-89.5, 43.5, -91.0, 43.5),    # MN-IA
        # Iowa
        (-96.5, 43.5, -90.0, 43.5),    # IA-WI/IL
        (-90.0, 43.5, -90.0, 40.4),    # IA-IL/MO
        # Missouri
        (-95.8, 40.4, -89.0, 40.4),    # MO-IL/KY
        (-89.0, 40.4, -89.0, 36.5),    # MO-KY/TN
        # Wisconsin
        (-92.9, 47.0, -87.0, 47.0),    # WI-MI
        (-87.0, 47.0, -87.0, 42.5),    # WI-IL
        # Illinois
        (-90.5, 42.5, -87.5, 42.5),    # IL-IN
        (-87.5, 42.5, -87.5, 37.0),    # IL-KY
        # Indiana
        (-88.0, 41.8, -84.8, 41.8),    # IN-OH
        (-84.8, 41.8, -84.8, 39.0),    # IN-KY/OH
        # Ohio
        (-84.3, 41.0, -80.5, 41.0),    # OH-PA
        (-80.5, 41.0, -80.5, 38.5),    # OH-PA/WV/VA
    ])
    
    # Southeast
    borders.extend([
        # Louisiana
        (-94.0, 33.0, -88.8, 33.0),    # LA-MS
        (-88.8, 33.0, -88.8, 30.0),    # LA-MS
        # Mississippi
        (-91.0, 35.0, -88.2, 35.0),    # MS-AL
        (-88.2, 35.0, -88.2, 30.2),    # MS-AL
        # Alabama
        (-88.5, 35.0, -85.0, 35.0),    # AL-GA
        (-85.0, 35.0, -85.0, 31.0),    # AL-GA/FL
        # Georgia
        (-85.6, 35.0, -80.8, 35.0),    # GA-SC/NC
        (-80.8, 35.0, -80.8, 32.0),    # GA-SC
        # Florida
        (-87.6, 30.7, -80.0, 30.7),    # FL-GA/AL
        (-80.0, 30.7, -80.0, 25.0),    # FL-East coast
        # Tennessee
        (-90.3, 36.5, -81.7, 36.5),    # TN-MO/KY/VA/NC
        (-81.7, 36.5, -81.7, 35.2),    # TN-NC
        (-84.0, 35.2, -83.0, 35.2),    # TN-GA
    ])
    
    # Northeast
    borders.extend([
        # New York
        (-79.8, 43.0, -73.0, 43.0),    # NY-VT/MA/CT
        (-74.0, 45.0, -73.5, 45.0),    # NY-Canada
        # Pennsylvania
        (-80.5, 42.0, -75.0, 42.0),    # PA-NY/NJ
        (-75.0, 42.0, -75.0, 39.7),    # PA-NJ/DE/MD
        # New England
        (-73.5, 45.0, -70.5, 45.0),    # VT-NH-ME Canada
        (-71.5, 45.0, -71.0, 41.2),    # NH-ME-MA
        (-73.5, 42.0, -69.9, 42.0),    # NY-MA-RI
    ])
    
    # Mississippi River (major geographic feature)
    mississippi_river = [
        (-95.0, 29.7, -92.0, 33.0),    # Delta to Memphis
        (-92.0, 33.0, -91.0, 35.5),    # Memphis to MO
        (-91.0, 35.5, -90.3, 40.6),    # MO to IL
        (-90.3, 40.6, -91.2, 43.0),    # IL to IA/WI
        (-91.2, 43.0, -93.5, 47.0),    # To MN
    ]
    borders.extend(mississippi_river)
    
    # Great Lakes approximations
    great_lakes = [
        # Lake Superior
        (-92.0, 46.5, -84.5, 46.5),
        (-84.5, 46.5, -84.5, 48.0),
        # Lake Michigan
        (-88.0, 42.5, -86.0, 42.5),
        (-86.0, 42.5, -86.0, 46.0),
        (-86.0, 46.0, -88.0, 46.0),
        # Lake Huron/Erie/Ontario
        (-83.0, 41.5, -79.0, 43.5),
    ]
    borders.extend(great_lakes)
    
    return borders


def create_sharp_topological_surface(
    df: pd.DataFrame,
    value_column: str = "risk_score",
    resolution: int = 150,
    smoothing: float = 0.3,  # REDUCED for sharper peaks
    neighborhood_size: float = 2.5  # Degrees - how far to look for neighbors
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Create a sharp interpolated surface that preserves local peaks.
    Uses nearest-neighbor interpolation for sharp peaks + light smoothing.
    """
    if not HAS_SCIPY or len(df) == 0:
        return None, None, None
    
    # Extract coordinates and values
    x = df["longitude"].values
    y = df["latitude"].values
    z = df[value_column].values
    
    # Create regular grid - HIGHER RESOLUTION
    xi = np.linspace(x.min(), x.max(), resolution)
    yi = np.linspace(y.min(), y.max(), resolution)
    xi, yi = np.meshgrid(xi, yi)
    
    # Use cubic interpolation for sharper peaks than linear
    # but with a mask to only interpolate near actual data points
    zi = griddata((x, y), z, (xi, yi), method="cubic", fill_value=0)
    
    # Create a distance mask - only show surface near actual counties
    # This prevents the "bed sheet" effect extending to empty areas
    from scipy.spatial import cKDTree
    points = np.column_stack([x, y])
    tree = cKDTree(points)
    grid_points = np.column_stack([xi.ravel(), yi.ravel()])
    distances, _ = tree.query(grid_points, k=1)
    distance_mask = distances.reshape(xi.shape) > neighborhood_size  # degrees
    
    # Apply distance mask
    zi[distance_mask] = np.nan
    
    # Light smoothing to remove artifacts but keep peaks sharp
    if smoothing > 0:
        # Only smooth non-NaN values
        zi_smooth = zi.copy()
        valid_mask = ~np.isnan(zi)
        if valid_mask.any():
            zi_valid = np.where(valid_mask, zi, 0)
            zi_smoothed = gaussian_filter(zi_valid, sigma=smoothing)
            # Restore NaN values
            zi_smooth[valid_mask] = zi_smoothed[valid_mask]
            zi = zi_smooth
    
    # Clip to valid range
    zi = np.clip(zi, 0, 1)
    
    return xi, yi, zi


def create_topographic_manifold(
    df: pd.DataFrame,
    height_scale: float = 0.6,  # INCREASED default for more dramatic peaks
    show_surface: bool = True,
    show_wireframe: bool = False,
    show_counties: bool = True,
    show_borders: bool = True,
    colorscale: str = "RdYlGn_r"
) -> Optional[Any]:
    """
    Create a 3D topographic manifold with SHARP PEAKS resembling the US map.
    Like population density maps with dramatic spikes over cities.
    """
    if not HAS_PLOTLY or len(df) == 0:
        return None
    
    # Create SHARP interpolated surface with less smoothing
    xi, yi, zi = create_sharp_topological_surface(
        df, 
        value_column="risk_score",
        resolution=120,  # Higher resolution
        smoothing=0.5,   # LESS smoothing = sharper peaks
        neighborhood_size=2.0  # Only interpolate near counties
    )
    
    if xi is None:
        return None
    
    fig = go.Figure()
    
    # Main surface - SHARP PEAKS with geographic mask
    if show_surface:
        fig.add_trace(go.Surface(
            x=xi,
            y=yi,
            z=zi * height_scale,
            colorscale=colorscale,
            cmin=0,
            cmax=1,
            showscale=True,
            colorbar=dict(
                title=dict(text="Risk Score", font=dict(color="#E0E0E0")),
                tickfont=dict(color="#E0E0E0"),
                x=0.95,
                thickness=20,
                len=0.8,
                tickvals=[0, 0.33, 0.67, 1.0],
                ticktext=["Low", "Medium", "High", "Extreme"]
            ),
            lighting=dict(
                ambient=0.5,
                diffuse=0.9,  # More diffuse for better peak visibility
                roughness=0.3,
                specular=0.6,
                fresnel=0.1
            ),
            lightposition=dict(x=100, y=200, z=1000),  # Angled light for peak shadows
            contours=dict(
                z=dict(
                    show=True,
                    usecolormap=True,
                    highlightcolor="#FFFFFF",
                    project_z=True,
                    size=0.1,  # Larger contour intervals
                    start=0,
                    end=height_scale
                ),
                x=dict(show=False),
                y=dict(show=False)
            ),
            hovertemplate="Lon: %{x:.2f}<br>Lat: %{y:.2f}<br>Risk: %{z:.3f}<extra></extra>",
            name="Risk Surface",
            opacity=0.95
        ))
    
    # Add state borders as 3D lines on the surface
    if show_borders:
        borders = get_state_borders()
        border_lines = []
        
        for lon1, lat1, lon2, lat2 in borders:
            # Sample points along the border line
            n_points = 20
            lons = np.linspace(lon1, lon2, n_points)
            lats = np.linspace(lat1, lat2, n_points)
            
            # Find Z values at these positions from our surface
            zs = []
            for lo, la in zip(lons, lats):
                # Find nearest point in grid
                lon_idx = np.argmin(np.abs(xi[0, :] - lo))
                lat_idx = np.argmin(np.abs(yi[:, 0] - la))
                z_val = zi[lat_idx, lon_idx]
                if not np.isnan(z_val):
                    zs.append(z_val * height_scale + 0.015)  # Slightly above surface
                else:
                    zs.append(0.015)  # Base level if outside mask
            
            # Add border line
            if len(zs) == n_points:
                fig.add_trace(go.Scatter3d(
                    x=lons,
                    y=lats,
                    z=zs,
                    mode='lines',
                    line=dict(
                        color='rgba(255, 255, 255, 0.4)',
                        width=2
                    ),
                    hoverinfo='skip',
                    showlegend=False
                ))
    
    # Add county markers as SPIKES for dramatic effect
    if show_counties:
        # Sample high-risk counties for spike markers
        high_risk = df[df["risk_score"] > 0.5].copy()
        if len(high_risk) > 200:
            high_risk = high_risk.nlargest(200, "risk_score")
        
        for _, row in high_risk.iterrows():
            # Create vertical spike
            lon = row["longitude"]
            lat = row["latitude"]
            risk = row["risk_score"]
            
            # Find base Z
            lon_idx = np.argmin(np.abs(xi[0, :] - lon))
            lat_idx = np.argmin(np.abs(yi[:, 0] - lat))
            base_z = zi[lat_idx, lon_idx] * height_scale
            
            # Spike goes from surface to peak
            spike_height = risk * height_scale * 0.3  # Extra height for spike
            
            fig.add_trace(go.Scatter3d(
                x=[lon, lon],
                y=[lat, lat],
                z=[base_z, base_z + spike_height],
                mode='lines',
                line=dict(
                    color='rgba(255, 255, 255, 0.6)',
                    width=1
                ),
                hoverinfo='skip',
                showlegend=False
            ))
        
        # Add county dots at peaks
        fig.add_trace(go.Scatter3d(
            x=high_risk["longitude"],
            y=high_risk["latitude"],
            z=[risk * height_scale for risk in high_risk["risk_score"]],
            mode="markers",
            marker=dict(
                size=3,
                color=high_risk["risk_score"],
                colorscale=colorscale,
                cmin=0,
                cmax=1,
                opacity=0.9,
                line=dict(color="rgba(255,255,255,0.5)", width=0.5)
            ),
            text=high_risk.apply(
                lambda row: f"<b>{row.get('county_name', 'Unknown')}</b><br>Risk: {row.get('risk_score', 0):.3f}",
                axis=1
            ),
            hovertemplate="%{text}<extra></extra>",
            name="High-Risk Counties"
        ))
    
    # Layout with better camera angle for viewing peaks
    fig.update_layout(
        title=dict(
            text="<b>Risk Topography</b><br><sup>Sharp Peaks = High Risk Counties | Valleys = Low Risk</sup>",
            font=dict(color="#E0E0E0", size=18),
            x=0.5
        ),
        scene=dict(
            xaxis=dict(
                title="Longitude",
                backgroundcolor="rgba(14, 17, 23, 0.8)",
                gridcolor="rgba(30, 41, 59, 0.5)",
                color="#E0E0E0",
                showbackground=True,
                zeroline=False,
                range=[-130, -65]
            ),
            yaxis=dict(
                title="Latitude",
                backgroundcolor="rgba(14, 17, 23, 0.8)",
                gridcolor="rgba(30, 41, 59, 0.5)",
                color="#E0E0E0",
                showbackground=True,
                zeroline=False,
                range=[24, 50]
            ),
            zaxis=dict(
                title="Risk Score",
                backgroundcolor="rgba(14, 17, 23, 0.8)",
                gridcolor="rgba(30, 41, 59, 0.5)",
                color="#E0E0E0",
                showbackground=True,
                zeroline=False,
                range=[0, height_scale * 1.1]
            ),
            bgcolor="rgba(14, 17, 23, 0.9)",
            camera=dict(
                eye=dict(x=1.2, y=1.8, z=1.0),  # Angle to see peaks better
                center=dict(x=0, y=0, z=0),
                up=dict(x=0, y=0, z=1)
            ),
            aspectratio=dict(x=2.0, y=1.3, z=0.8),  # Taller Z for dramatic peaks
            aspectmode='manual'
        ),
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E0E0E0", family="Inter, sans-serif"),
        margin=dict(l=0, r=0, b=0, t=60),
        height=750,
        showlegend=False,
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
        radius=50000,
        elevation_scale=100,
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


class Visualization3D:
    """Main class for creating 3D visualizations."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = prepare_data_for_3d(df)
        self.config = VisualizationConfig()
    
    def create_topological_manifold_map(
        self,
        height_scale: float = 0.6,
        show_surface: bool = True,
        show_wireframe: bool = False,
        show_counties: bool = True
    ) -> Optional[Any]:
        """Create the new SHARP topographic manifold with geographic features."""
        if len(self.df) == 0:
            return None
        return create_topographic_manifold(
            self.df,
            height_scale=height_scale,
            show_surface=show_surface,
            show_wireframe=show_wireframe,
            show_counties=show_counties,
            show_borders=True
        )
    
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
        
        if show_heatmap:
            heatmap = create_heatmap_layer(self.df)
            if heatmap:
                layers.append(heatmap)
        
        column_layer = create_enhanced_column_layer(self.df, self.config)
        if column_layer:
            layers.append(column_layer)
        
        scatter = create_scatterplot_layer(self.df)
        if scatter:
            layers.append(scatter)
        
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
        
        return views


def get_visualization_help() -> str:
    """Return help text about the visualization options."""
    return """
    ## 3D Visualization Guide
    
    ### Risk Topography (NEW!):
    - **Sharp Peaks**: High risk counties form dramatic spikes (like population density maps)
    - **Geographic Mask**: Surface only appears where counties exist (no "bed sheet" effect)
    - **State Borders**: White lines show US state boundaries on the surface
    - **Spike Markers**: Vertical lines showing exact county locations
    - **Contour Lines**: Risk level boundaries
    - **Fully Interactive**: Click & drag to rotate, scroll to zoom
    
    ### Visual Encodings:
    - **Height**: Risk score (scaled for dramatic peaks)
    - **Color**: Smooth gradient Green → Yellow → Red → Dark Red
    - **Surface**: Interpolated only near actual counties (distance mask)
    - **Borders**: State boundary lines on surface
    
    ### Interactions:
    - Click & drag to rotate view
    - Scroll to zoom in/out
    - Right-click and drag to pan
    - Hover for county details
    """
