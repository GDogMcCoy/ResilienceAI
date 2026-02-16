"""
ResilienceAI - Lightweight County-Level Heatmap Visualizations
Simple, reliable 2D heatmaps for county-level risk visualization
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any

try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    HAS_PLOTLY = True
except ImportError:
    HAS_PLOTLY = False

try:
    import pydeck as pdk
    HAS_PYDECK = True
except ImportError:
    HAS_PYDECK = False


def prepare_data_for_viz(df: pd.DataFrame) -> pd.DataFrame:
    """Prepare county data for visualization."""
    map_df = df.dropna(subset=["latitude", "longitude", "risk_score"]).copy()
    
    # Filter to continental US
    map_df = map_df[
        (map_df["latitude"] > 24) & (map_df["latitude"] < 50) &
        (map_df["longitude"] > -130) & (map_df["longitude"] < -65)
    ].copy()
    
    # Create color based on risk
    map_df["risk_color"] = map_df["risk_score"].apply(
        lambda x: "#27ae60" if x < 0.33 else "#f39c12" if x < 0.67 else "#e74c3c"
    )
    
    # Size based on population
    if "total_population" in map_df.columns:
        map_df["marker_size"] = np.log1p(map_df["total_population"]) * 2
    else:
        map_df["marker_size"] = 5
    
    return map_df


def create_county_heatmap(df: pd.DataFrame, color_by: str = "risk_score") -> Optional[Any]:
    """
    Create a reliable county-level density heatmap.
    Simple, fast, and clear.
    """
    if not HAS_PLOTLY or len(df) == 0:
        return None
    
    # Sample for performance if needed
    plot_df = df.copy()
    if len(plot_df) > 3000:
        # Keep all high-risk, sample others
        high_risk = plot_df[plot_df["risk_score"] > 0.5]
        low_risk = plot_df[plot_df["risk_score"] <= 0.5].sample(min(1500, len(plot_df[plot_df["risk_score"] <= 0.5])))
        plot_df = pd.concat([high_risk, low_risk])
    
    fig = px.density_mapbox(
        plot_df,
        lat="latitude",
        lon="longitude",
        z=color_by,
        radius=15,  # Size of each county's heat influence
        center=dict(lat=39.5, lon=-98.35),
        zoom=3,
        mapbox_style="carto-darkmatter",
        color_continuous_scale="RdYlGn_r",
        range_color=[0, 1],
        opacity=0.7,
        height=650,
        labels={color_by: "Risk Score"},
        hover_data={
            "county_name": True,
            color_by: ":.3f",
            "total_population": ":,.0f" if "total_population" in plot_df.columns else False
        }
    )
    
    fig.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E0E0E0"),
        margin=dict(l=0, r=0, b=0, t=40),
        coloraxis_colorbar=dict(
            title=dict(text="Risk Score", font=dict(color="#E0E0E0")),
            tickfont=dict(color="#E0E0E0"),
            tickvals=[0, 0.33, 0.67, 1.0],
            ticktext=["Low", "Medium", "High", "Extreme"]
        ),
        title=dict(
            text="<b>County-Level Risk Heatmap</b><br><sup>Higher intensity = Higher risk concentration</sup>",
            font=dict(color="#E0E0E0", size=16),
            x=0.5
        )
    )
    
    return fig


def create_county_scatter_map(df: pd.DataFrame, size_by: str = "marker_size") -> Optional[Any]:
    """
    Create a simple scatter map with sized/colored counties.
    Most reliable view - each county is a visible dot.
    """
    if not HAS_PLOTLY or len(df) == 0:
        return None
    
    plot_df = df.copy()
    
    # Cap marker size for visibility
    if size_by in plot_df.columns:
        plot_df[size_by] = plot_df[size_by].clip(upper=20)
    
    fig = px.scatter_geo(
        plot_df,
        lat="latitude",
        lon="longitude",
        color="risk_score",
        size=size_by if size_by in plot_df.columns else None,
        color_continuous_scale="RdYlGn_r",
        range_color=[0, 1],
        scope="usa",
        projection="albers usa",
        height=600,
        opacity=0.7,
        labels={"risk_score": "Risk Score"},
        hover_data={
            "county_name": True,
            "risk_score": ":.3f",
            "risk_level": True,
            "total_population": ":,.0f" if "total_population" in plot_df.columns else False,
            "latitude": False,
            "longitude": False
        }
    )
    
    fig.update_layout(
        paper_bgcolor="#0E1117",
        font=dict(color="#E0E0E0"),
        margin=dict(l=0, r=0, b=0, t=40),
        geo=dict(
            bgcolor="#0E1117",
            showland=True,
            landcolor="#1A1F2E",
            showsubunits=True,
            subunitcolor="#4FC3F7",
            subunitwidth=0.5,
            showframe=False,
            showcoastlines=True,
            coastlinecolor="#4FC3F7",
            coastlinewidth=0.5,
            lakecolor="#0E1117",
            showlakes=True
        ),
        coloraxis_colorbar=dict(
            title=dict(text="Risk", font=dict(color="#E0E0E0")),
            tickfont=dict(color="#E0E0E0")
        ),
        title=dict(
            text="<b>County Risk Distribution</b><br><sup>Each dot = one county | Size = Population | Color = Risk</sup>",
            font=dict(color="#E0E0E0", size=16),
            x=0.5
        )
    )
    
    return fig


def create_state_choropleth(df: pd.DataFrame) -> Optional[Any]:
    """
    Aggregate by state and show as choropleth.
    Simple high-level view.
    """
    if not HAS_PLOTLY or len(df) == 0:
        return None
    
    # Extract state from county_name
    df["state"] = df["county_name"].str.extract(r", (\w+)$")
    
    # Aggregate by state
    state_risk = df.groupby("state").agg({
        "risk_score": "mean",
        "total_population": "sum" if "total_population" in df.columns else "count",
        "county_name": "count"
    }).reset_index()
    state_risk.columns = ["state", "avg_risk", "total_pop", "county_count"]
    
    # Map state abbreviations to names for plotly
    state_names = {
        "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
        "CA": "California", "CO": "Colorado", "CT": "Connecticut", "DE": "Delaware",
        "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
        "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas",
        "KY": "Kentucky", "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
        "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota", "MS": "Mississippi",
        "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
        "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
        "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma",
        "OR": "Oregon", "PA": "Pennsylvania", "RI": "Rhode Island", "SC": "South Carolina",
        "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas", "UT": "Utah",
        "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
        "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"
    }
    state_risk["state_name"] = state_risk["state"].map(state_names)
    
    fig = px.choropleth(
        state_risk,
        locations="state_name",
        locationmode="USA-states",
        color="avg_risk",
        color_continuous_scale="RdYlGn_r",
        range_color=[0, 1],
        scope="usa",
        height=600,
        labels={"avg_risk": "Avg Risk Score"},
        hover_data={
            "state": True,
            "avg_risk": ":.3f",
            "county_count": True,
            "total_pop": ":,.0f"
        }
    )
    
    fig.update_layout(
        paper_bgcolor="#0E1117",
        font=dict(color="#E0E0E0"),
        margin=dict(l=0, r=0, b=0, t=40),
        geo=dict(
            bgcolor="#0E1117",
            showlakes=True,
            lakecolor="#0E1117"
        ),
        coloraxis_colorbar=dict(
            title=dict(text="Avg Risk", font=dict(color="#E0E0E0")),
            tickfont=dict(color="#E0E0E0")
        ),
        title=dict(
            text="<b>State-Level Average Risk</b><br><sup>Color = Average risk score across all counties</sup>",
            font=dict(color="#E0E0E0", size=16),
            x=0.5
        )
    )
    
    return fig


def create_hexbin_map(df: pd.DataFrame) -> Optional[Any]:
    """
    Create a hexbin-style aggregation map.
    Good for showing regional patterns.
    """
    if not HAS_PLOTLY or len(df) == 0:
        return None
    
    fig = go.Figure()
    
    # Create hexbin-like scatter with aggregation
    fig.add_trace(go.Hexbin(
        x=df["longitude"],
        y=df["latitude"],
        z=df["risk_score"],
        reduce_func="mean",
        colorscale="RdYlGn_r",
        zmin=0,
        zmax=1,
        gridsize=30,  # Number of hexagons
        showscale=True,
        colorbar=dict(
            title=dict(text="Avg Risk", font=dict(color="#E0E0E0")),
            tickfont=dict(color="#E0E0E0")
        ),
        hovertemplate="Avg Risk: %{z:.3f}<br>Counties: %{count}<extra></extra>"
    ))
    
    fig.update_layout(
        paper_bgcolor="#0E1117",
        plot_bgcolor="#0E1117",
        font=dict(color="#E0E0E0"),
        margin=dict(l=0, r=0, b=0, t=40),
        xaxis=dict(
            title="Longitude",
            color="#E0E0E0",
            gridcolor="#1E293B",
            showgrid=True,
            range=[-130, -65]
        ),
        yaxis=dict(
            title="Latitude",
            color="#E0E0E0",
            gridcolor="#1E293B",
            showgrid=True,
            scaleanchor="x",
            scaleratio=1.3,
            range=[24, 50]
        ),
        title=dict(
            text="<b>Regional Risk Hexbins</b><br><sup>Hexagons show average risk in geographic regions</sup>",
            font=dict(color="#E0E0E0", size=16),
            x=0.5
        ),
        height=650
    )
    
    return fig


class Visualization3D:
    """Simplified visualization class focused on reliable 2D heatmaps."""
    
    def __init__(self, df: pd.DataFrame):
        self.df = prepare_data_for_viz(df)
    
    def create_county_heatmap(self) -> Optional[Any]:
        """Create county-level density heatmap."""
        if len(self.df) == 0:
            return None
        return create_county_heatmap(self.df)
    
    def create_county_scatter_map(self) -> Optional[Any]:
        """Create scatter map with sized/colored counties."""
        if len(self.df) == 0:
            return None
        return create_county_scatter_map(self.df)
    
    def create_state_choropleth(self) -> Optional[Any]:
        """Create state-level choropleth."""
        if len(self.df) == 0:
            return None
        return create_state_choropleth(self.df)
    
    def create_hexbin_map(self) -> Optional[Any]:
        """Create hexbin aggregation map."""
        if len(self.df) == 0:
            return None
        return create_hexbin_map(self.df)
    
    # Backwards compatibility - return simple heatmap instead of 3D
    def create_topological_manifold_map(self, **kwargs) -> Optional[Any]:
        """Fallback to simple heatmap."""
        return self.create_county_heatmap()
    
    def create_enhanced_tower_map(self, **kwargs) -> Optional[Any]:
        """Fallback to scatter map."""
        return self.create_county_scatter_map()
    
    def create_hexagon_map(self, **kwargs) -> Optional[Any]:
        """Fallback to hexbin."""
        return self.create_hexbin_map()
    
    def create_plotly_3d_views(self) -> Dict[str, Any]:
        """Return available views."""
        return {
            "county_heatmap": self.create_county_heatmap(),
            "county_scatter": self.create_county_scatter_map(),
            "state_choropleth": self.create_state_choropleth(),
            "hexbin": self.create_hexbin_map()
        }


def get_visualization_help() -> str:
    """Return help text about the visualization options."""
    return """
    ## County-Level Heatmap Guide
    
    ### Available Views:
    - **County Heatmap**: Density-based heatmap showing risk concentration
    - **County Scatter**: Each county as a sized/colored dot on US map
    - **State Choropleth**: Average risk by state
    - **Regional Hexbins**: Hexagonal aggregation showing regional patterns
    
    ### Visual Encodings:
    - **Color**: Green (low) → Yellow (medium) → Red (high) risk
    - **Size** (scatter): Population size
    - **Intensity** (heatmap): Risk concentration
    
    ### All views are:
    - Fast and reliable
    - Interactive (zoom, pan, hover)
    - Mobile-friendly
    - No complex 3D physics
    """
