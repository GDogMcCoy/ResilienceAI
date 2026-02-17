"""
Enhanced 3D Geospatial Visualizations
Advanced 3D charts using Plotly for ResilienceAI dashboard
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple, Any


class Geospatial3DVisualizer:
    """
    Advanced 3D geospatial visualization with multiple rendering modes.
    Supports: 3D scatter, surface, mesh, and network visualizations.
    """
    
    COLOR_SCALES = {
        'risk': 'RdYlGn_r',
        'temperature': 'RdBu_r',
        'elevation': 'terrain',
        'population': 'Viridis',
        'custom': [
            [0, '#4ade80'],      # Green for low
            [0.5, '#fbbf24'],    # Amber for medium
            [1, '#ef4444']       # Red for high
        ]
    }
    
    def __init__(self, df: pd.DataFrame, geo_df: Optional[pd.DataFrame] = None):
        self.df = df
        self.geo_df = geo_df
        self.default_layout = {
            'paper_bgcolor': 'rgba(15, 23, 42, 1)',
            'font': {'color': '#f8fafc'},
            'margin': dict(l=0, r=0, t=40, b=0)
        }
        
    def create_3d_risk_landscape(
        self,
        x_col: str = 'longitude',
        y_col: str = 'latitude',
        z_col: str = 'risk_score',
        color_col: str = 'vulnerability_index',
        size_col: str = 'total_population',
        hover_cols: Optional[List[str]] = None,
        sample_size: Optional[int] = None
    ) -> go.Figure:
        """
        Create an interactive 3D risk landscape visualization.
        
        Args:
            x_col: Column for x-axis (longitude)
            y_col: Column for y-axis (latitude)
            z_col: Column for z-axis (risk score)
            color_col: Column for color coding
            size_col: Column for marker sizing
            hover_cols: Additional columns for hover info
            sample_size: Limit data points for performance
        
        Returns:
            Plotly Figure object
        """
        # Sample data if needed for performance
        plot_df = self.df.copy()
        if sample_size and len(plot_df) > sample_size:
            plot_df = plot_df.sample(n=sample_size, random_state=42)
        
        hover_data = hover_cols or ['county_name', 'state', 'risk_level']
        
        # Calculate marker sizes
        sizes = np.log(plot_df[size_col] + 1) * 3
        
        # Create hover text
        hover_text = plot_df.apply(
            lambda row: '<br>'.join([
                f"<b>{row.get('county_name', 'Unknown')}</b>",
                f"State: {row.get('state', 'N/A')}",
                f"Risk Score: {row.get('risk_score', 0):.3f}",
                f"Population: {row.get('total_population', 0):,}",
                f"Risk Level: {row.get('risk_level', 'Unknown')}"
            ]),
            axis=1
        )
        
        fig = go.Figure(data=[go.Scatter3d(
            x=plot_df[x_col],
            y=plot_df[y_col],
            z=plot_df[z_col],
            mode='markers',
            marker=dict(
                size=sizes,
                color=plot_df[color_col],
                colorscale=self.COLOR_SCALES['risk'],
                opacity=0.7,
                colorbar=dict(
                    title=color_col.replace('_', ' ').title(),
                    titleside='right',
                    thickness=15,
                    len=0.7
                ),
                line=dict(width=0.5, color='rgba(255,255,255,0.3)')
            ),
            text=hover_text,
            hoverinfo='text',
            name='Risk Landscape'
        )])
        
        fig.update_layout(
            title='3D Risk Landscape Visualization',
            scene=dict(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                zaxis_title='Risk Score',
                bgcolor='rgba(15, 23, 42, 0.9)',
                xaxis=dict(
                    gridcolor='rgba(148, 163, 184, 0.2)',
                    showbackground=True,
                    backgroundcolor='rgba(30, 41, 59, 0.5)'
                ),
                yaxis=dict(
                    gridcolor='rgba(148, 163, 184, 0.2)',
                    showbackground=True,
                    backgroundcolor='rgba(30, 41, 59, 0.5)'
                ),
                zaxis=dict(
                    gridcolor='rgba(148, 163, 184, 0.2)',
                    showbackground=True,
                    backgroundcolor='rgba(30, 41, 59, 0.5)'
                ),
                camera=dict(
                    eye=dict(x=1.5, y=1.5, z=1.0),
                    up=dict(x=0, y=0, z=1),
                    center=dict(x=0, y=0, z=0.5)
                ),
                aspectmode='manual',
                aspectratio=dict(x=2, y=1, z=0.5)
            ),
            **self.default_layout,
            height=700
        )
        
        return fig
    
    def create_3d_surface(
        self,
        value_col: str = 'risk_score',
        grid_resolution: int = 50,
        interpolation_method: str = 'cubic'
    ) -> go.Figure:
        """
        Create a 3D surface visualization of risk across geography.
        
        Args:
            value_col: Column to visualize on z-axis
            grid_resolution: Grid resolution for interpolation
            interpolation_method: Interpolation method ('linear', 'cubic', 'nearest')
        
        Returns:
            Plotly Figure object
        """
        from scipy.interpolate import griddata
        
        # Create grid
        x = self.df['longitude'].values
        y = self.df['latitude'].values
        z = self.df[value_col].values
        
        xi = np.linspace(x.min(), x.max(), grid_resolution)
        yi = np.linspace(y.min(), y.max(), grid_resolution)
        xi, yi = np.meshgrid(xi, yi)
        
        # Interpolate
        zi = griddata((x, y), z, (xi, yi), method=interpolation_method)
        
        # Handle NaN values
        zi = np.nan_to_num(zi, nan=np.nanmean(z))
        
        fig = go.Figure(data=[go.Surface(
            x=xi,
            y=yi,
            z=zi,
            colorscale=self.COLOR_SCALES['risk'],
            colorbar=dict(
                title=value_col.replace('_', ' ').title(),
                titleside='right',
                thickness=15,
                len=0.7
            ),
            contours=dict(
                z=dict(
                    show=True,
                    usecolormap=True,
                    highlightcolor='#c084fc',
                    project_z=True
                ),
                y=dict(show=True),
                x=dict(show=True)
            ),
            lighting=dict(
                ambient=0.6,
                diffuse=0.8,
                roughness=0.4,
                specular=0.5
            ),
            hovertemplate=(
                'Lon: %{x:.2f}<br>' +
                'Lat: %{y:.2f}<br>' +
                f'{value_col}: %{{z:.3f}}<br>' +
                '<extra></extra>'
            )
        )])
        
        fig.update_layout(
            title=f'3D Risk Surface: {value_col.replace("_", " ").title()}',
            scene=dict(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                zaxis_title=value_col.replace('_', ' ').title(),
                bgcolor='rgba(15, 23, 42, 0.9)',
                aspectratio=dict(x=1, y=1, z=0.5),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.0))
            ),
            **self.default_layout,
            height=700
        )
        
        return fig
    
    def create_network_graph_3d(
        self,
        node_col: str = 'county_name',
        edge_connections: Optional[List[Tuple[str, str]]] = None,
        node_size_col: str = 'risk_score',
        node_color_col: str = 'vulnerability_index',
        use_coordinates: bool = True
    ) -> go.Figure:
        """
        Create a 3D network graph visualization.
        
        Args:
            node_col: Column containing node identifiers
            edge_connections: List of (source, target) tuples
            node_size_col: Column for node sizing
            node_color_col: Column for node coloring
            use_coordinates: Use lat/lon for positioning
        
        Returns:
            Plotly Figure object
        """
        # Get node positions
        if use_coordinates and 'longitude' in self.df.columns and 'latitude' in self.df.columns:
            pos = {
                row[node_col]: (
                    row['longitude'],
                    row['latitude'],
                    row[node_size_col] * 10  # Height based on risk
                )
                for _, row in self.df.iterrows()
            }
        else:
            # Generate positions using 3D layout
            from sklearn.decomposition import PCA
            coords = PCA(n_components=3).fit_transform(
                self.df[[node_size_col, node_color_col]].values
            )
            pos = {
                row[node_col]: tuple(coords[idx] * 20)
                for idx, row in self.df.iterrows()
            }
        
        # Generate edges if not provided
        if edge_connections is None:
            edge_connections = self._generate_neighbor_edges(node_col)
        
        # Create edge traces
        edge_traces = []
        for edge in edge_connections:
            if edge[0] in pos and edge[1] in pos:
                start = pos[edge[0]]
                end = pos[edge[1]]
                
                edge_trace = go.Scatter3d(
                    x=[start[0], end[0], None],
                    y=[start[1], end[1], None],
                    z=[start[2], end[2], None],
                    mode='lines',
                    line=dict(
                        color='rgba(192, 132, 252, 0.3)',
                        width=1
                    ),
                    hoverinfo='none',
                    showlegend=False
                )
                edge_traces.append(edge_trace)
        
        # Create node trace
        node_x = [pos[node][0] for node in pos]
        node_y = [pos[node][1] for node in pos]
        node_z = [pos[node][2] for node in pos]
        
        # Get node data
        node_data = self.df.set_index(node_col)
        
        node_trace = go.Scatter3d(
            x=node_x,
            y=node_y,
            z=node_z,
            mode='markers',
            marker=dict(
                size=node_data[node_size_col] * 30,
                color=node_data[node_color_col],
                colorscale=self.COLOR_SCALES['risk'],
                colorbar=dict(
                    title=node_color_col.replace('_', ' ').title(),
                    thickness=15,
                    len=0.7
                ),
                line=dict(width=1, color='rgba(255,255,255,0.5)'),
                opacity=0.8
            ),
            text=[
                f"<b>{node}</b><br>" +
                f"Risk: {node_data.loc[node, node_size_col]:.3f}<br>" +
                f"Vulnerability: {node_data.loc[node, node_color_col]:.3f}"
                for node in pos.keys()
            ],
            hovertemplate='%{text}<extra></extra>',
            name='Counties'
        )
        
        fig = go.Figure(data=edge_traces + [node_trace])
        
        fig.update_layout(
            title='3D County Network Visualization',
            scene=dict(
                bgcolor='rgba(15, 23, 42, 0.9)',
                xaxis=dict(showgrid=False, showticklabels=False, title=''),
                yaxis=dict(showgrid=False, showticklabels=False, title=''),
                zaxis=dict(showgrid=False, showticklabels=False, title='Risk'),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.0))
            ),
            **self.default_layout,
            showlegend=False,
            height=700
        )
        
        return fig
    
    def _generate_neighbor_edges(self, node_col: str) -> List[Tuple[str, str]]:
        """Generate edges based on geographic proximity."""
        edges = []
        
        if 'longitude' not in self.df.columns or 'latitude' not in self.df.columns:
            return edges
        
        # Calculate distances and connect nearby counties
        from scipy.spatial import cKDTree
        
        coords = self.df[['longitude', 'latitude']].values
        tree = cKDTree(coords)
        
        # Find 3 nearest neighbors for each county
        distances, indices = tree.query(coords, k=4)
        
        for i, neighbors in enumerate(indices):
            source = self.df.iloc[i][node_col]
            for j in neighbors[1:]:  # Skip self (first neighbor)
                if distances[i][list(neighbors).index(j)] < 2.0:  # Within ~200km
                    target = self.df.iloc[j][node_col]
                    edges.append((source, target))
        
        return edges
    
    def create_time_series_3d(
        self,
        time_col: str = 'year',
        value_cols: List[str] = ['risk_score', 'vulnerability_index'],
        group_col: str = 'state',
        top_n_groups: int = 10
    ) -> go.Figure:
        """
        Create a 3D time series ribbon visualization.
        
        Args:
            time_col: Column containing time values
            value_cols: Columns to visualize
            group_col: Column for grouping
            top_n_groups: Number of top groups to show
        
        Returns:
            Plotly Figure object
        """
        # Aggregate by time and group
        agg_df = self.df.groupby([time_col, group_col])[value_cols].mean().reset_index()
        
        # Get top groups by latest value
        latest_time = agg_df[time_col].max()
        top_groups = agg_df[agg_df[time_col] == latest_time].nlargest(
            top_n_groups, value_cols[0]
        )[group_col].tolist()
        
        fig = go.Figure()
        
        colors = px.colors.qualitative.Set3
        
        for idx, group in enumerate(top_groups):
            group_df = agg_df[agg_df[group_col] == group]
            
            color = colors[idx % len(colors)]
            
            fig.add_trace(go.Scatter3d(
                x=group_df[time_col],
                y=[idx] * len(group_df),
                z=group_df[value_cols[0]],
                mode='lines+markers',
                name=group,
                line=dict(width=4, color=color),
                marker=dict(size=4, color=color),
                surfaceaxis=1,
                surfacecolor=group_df[value_cols[1]] if len(value_cols) > 1 else None
            ))
        
        fig.update_layout(
            title=f'3D Time Series: {value_cols[0].replace("_", " ").title()}',
            scene=dict(
                xaxis_title='Time',
                yaxis_title='State',
                zaxis_title=value_cols[0].replace('_', ' ').title(),
                bgcolor='rgba(15, 23, 42, 0.9)',
                yaxis=dict(
                    tickmode='array',
                    tickvals=list(range(len(top_groups))),
                    ticktext=top_groups
                ),
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.0))
            ),
            **self.default_layout,
            height=700
        )
        
        return fig
    
    def create_risk_heatmap_3d(
        self,
        x_col: str = 'longitude',
        y_col: str = 'latitude',
        z_col: str = 'risk_score',
        bin_size: float = 0.5
    ) -> go.Figure:
        """
        Create a 3D histogram/heatmap visualization.
        
        Args:
            x_col: Column for x-axis binning
            y_col: Column for y-axis binning
            z_col: Column for aggregation
            bin_size: Size of bins in degrees
        
        Returns:
            Plotly Figure object
        """
        # Create bins
        x_bins = np.arange(
            self.df[x_col].min(),
            self.df[x_col].max() + bin_size,
            bin_size
        )
        y_bins = np.arange(
            self.df[y_col].min(),
            self.df[y_col].max() + bin_size,
            bin_size
        )
        
        # Digitize
        x_indices = np.digitize(self.df[x_col], x_bins) - 1
        y_indices = np.digitize(self.df[y_col], y_bins) - 1
        
        # Aggregate
        binned = self.df.groupby([x_indices, y_indices])[z_col].mean().reset_index()
        
        # Create meshgrid
        X, Y = np.meshgrid(x_bins[:-1], y_bins[:-1])
        Z = np.zeros_like(X)
        
        for _, row in binned.iterrows():
            xi, yi = int(row['level_0']), int(row['level_1'])
            if 0 <= xi < Z.shape[1] and 0 <= yi < Z.shape[0]:
                Z[yi, xi] = row[z_col]
        
        fig = go.Figure(data=[go.Surface(
            x=X,
            y=Y,
            z=Z,
            colorscale=self.COLOR_SCALES['risk'],
            colorbar=dict(title=z_col.replace('_', ' ').title()),
            contours=dict(
                z=dict(show=True, usecolormap=True, project_z=True)
            )
        )])
        
        fig.update_layout(
            title=f'3D Risk Heatmap',
            scene=dict(
                xaxis_title='Longitude',
                yaxis_title='Latitude',
                zaxis_title=z_col.replace('_', ' ').title(),
                bgcolor='rgba(15, 23, 42, 0.9)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.0))
            ),
            **self.default_layout,
            height=700
        )
        
        return fig
    
    def render_viz_selector(self, container: st.container):
        """Render a visualization type selector."""
        viz_types = {
            '3D Risk Landscape': self.create_3d_risk_landscape,
            '3D Risk Surface': self.create_3d_surface,
            '3D Network Graph': self.create_network_graph_3d,
            '3D Time Series': self.create_time_series_3d,
            '3D Risk Heatmap': self.create_risk_heatmap_3d
        }
        
        with container:
            st.markdown("### 🌐 3D Visualization Options")
            
            cols = st.columns(3)
            selected_viz = None
            
            for idx, (viz_name, viz_func) in enumerate(viz_types.items()):
                with cols[idx % 3]:
                    if st.button(viz_name, key=f"viz_btn_{idx}", use_container_width=True):
                        selected_viz = viz_name
            
            if selected_viz:
                with st.spinner(f"Generating {selected_viz}..."):
                    fig = viz_types[selected_viz]()
                    st.plotly_chart(fig, use_container_width=True, key=f"viz_{selected_viz}")


# Convenience functions for dashboard integration
def create_3d_visualizer(df: pd.DataFrame, geo_df: Optional[pd.DataFrame] = None) -> Geospatial3DVisualizer:
    """Create a 3D visualizer instance."""
    return Geospatial3DVisualizer(df, geo_df)


def render_3d_tab(df: pd.DataFrame, geo_df: Optional[pd.DataFrame] = None):
    """Render a complete 3D visualization tab."""
    viz = Geospatial3DVisualizer(df, geo_df)
    
    st.markdown("### 🌐 3D Geospatial Explorer")
    
    viz_type = st.selectbox(
        "Visualization Type",
        [
            "3D Risk Landscape",
            "3D Risk Surface",
            "3D Network Graph",
            "3D Time Series",
            "3D Risk Heatmap"
        ]
    )
    
    with st.spinner(f"Generating {viz_type}..."):
        if viz_type == "3D Risk Landscape":
            fig = viz.create_3d_risk_landscape()
        elif viz_type == "3D Risk Surface":
            fig = viz.create_3d_surface()
        elif viz_type == "3D Network Graph":
            fig = viz.create_network_graph_3d()
        elif viz_type == "3D Time Series":
            fig = viz.create_time_series_3d()
        else:
            fig = viz.create_risk_heatmap_3d()
        
        st.plotly_chart(fig, use_container_width=True)
