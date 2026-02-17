"""
ResilienceAI - 3D Vector Space Visualizations

Interactive 3D visualizations for exploring hyperdimensional county vectors.
Uses t-SNE and UMAP for dimensionality reduction, Plotly for interactive 3D plots.

Features:
- t-SNE/UMAP projection to 3D
- Interactive Plotly 3D scatter plots
- Color-coded by domain/risk level
- Hover details for county information
- Rotation, zoom, pan controls
- Cross-domain comparison views
- Anomaly highlighting
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path
import warnings

# Visualization libraries
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.offline as pyo

# Dimensionality reduction
try:
    from sklearn.manifold import TSNE
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False
    warnings.warn("UMAP not installed. Using t-SNE only for dimensionality reduction.")

from sklearn.decomposition import PCA

# Vector space module
from vector_space import (
    VectorSpaceManager, CountyVectorEncoder, CrossDomainAnalyzer,
    DOMAIN_FEATURES, ALL_FEATURES
)

from config import PROCESSED_DIR, FIGURES_DIR


class Vector3DVisualizer:
    """
    3D visualization toolkit for county vector spaces.
    
    Provides interactive Plotly-based 3D scatter plots with:
    - t-SNE and UMAP projections
    - Color coding by domain, risk, or custom attributes
    - Hover tooltips with county details
    - Camera controls and animations
    """
    
    def __init__(self, manager: Optional[VectorSpaceManager] = None):
        """
        Initialize the visualizer.
        
        Args:
            manager: VectorSpaceManager instance (optional)
        """
        self.manager = manager
        self.projections = {}  # Store computed projections
        self.colorscale = px.colors.sequential.Viridis
    
    def compute_projection(self, vectors: np.ndarray, method: str = "umap",
                          n_components: int = 3, **kwargs) -> np.ndarray:
        """
        Compute dimensionality reduction projection.
        
        Args:
            vectors: High-dimensional vectors (n_samples x n_features)
            method: Reduction method ('umap', 'tsne', 'pca')
            n_components: Number of output dimensions (default: 3)
            **kwargs: Additional parameters for the reducer
            
        Returns:
            Projected coordinates (n_samples x n_components)
        """
        method = method.lower()
        
        if method == "umap":
            if not UMAP_AVAILABLE:
                print("UMAP not available, falling back to t-SNE")
                method = "tsne"
            else:
                reducer = umap.UMAP(
                    n_components=n_components,
                    n_neighbors=kwargs.get('n_neighbors', 15),
                    min_dist=kwargs.get('min_dist', 0.1),
                    metric=kwargs.get('metric', 'cosine'),
                    random_state=kwargs.get('random_state', 42)
                )
                return reducer.fit_transform(vectors)
        
        if method == "tsne":
            if not SKLEARN_AVAILABLE:
                raise ImportError("scikit-learn not available")
            reducer = TSNE(
                n_components=n_components,
                perplexity=kwargs.get('perplexity', 30),
                learning_rate=kwargs.get('learning_rate', 'auto'),
                n_iter=kwargs.get('n_iter', 1000),
                random_state=kwargs.get('random_state', 42),
                metric=kwargs.get('metric', 'cosine')
            )
            return reducer.fit_transform(vectors)
        
        if method == "pca":
            reducer = PCA(n_components=n_components, random_state=42)
            return reducer.fit_transform(vectors)
        
        raise ValueError(f"Unknown method: {method}")
    
    def create_3d_scatter(self, coords: np.ndarray, df: pd.DataFrame,
                         color_by: str = "risk_score",
                         size_by: Optional[str] = None,
                         title: str = "County Vector Space (3D)",
                         hover_data: Optional[List[str]] = None,
                         opacity: float = 0.7) -> go.Figure:
        """
        Create an interactive 3D scatter plot.
        
        Args:
            coords: 3D coordinates (n_samples x 3)
            df: DataFrame with county metadata
            color_by: Column to use for color coding
            size_by: Column to use for marker sizing
            title: Plot title
            hover_data: Additional columns for hover tooltip
            opacity: Marker opacity
            
        Returns:
            Plotly Figure object
        """
        # Prepare data
        plot_df = df.copy()
        plot_df['x'] = coords[:, 0]
        plot_df['y'] = coords[:, 1]
        plot_df['z'] = coords[:, 2]
        
        # Determine color
        if color_by in plot_df.columns:
            color_values = plot_df[color_by]
        else:
            color_values = None
        
        # Determine size
        if size_by and size_by in plot_df.columns:
            size_values = plot_df[size_by]
            size_values = (size_values - size_values.min()) / (size_values.max() - size_values.min())
            size_values = 5 + size_values * 20  # Scale to 5-25 range
        else:
            size_values = 8
        
        # Default hover data
        if hover_data is None:
            hover_data = ['county_name', 'fips', 'risk_score', 'vulnerability_index']
        
        # Create hover text
        hover_text = []
        for _, row in plot_df.iterrows():
            text_parts = [f"<b>{row.get('county_name', 'Unknown')}</b>"]
            for col in hover_data:
                if col in row and col != 'county_name':
                    val = row[col]
                    if isinstance(val, float):
                        text_parts.append(f"{col}: {val:.3f}")
                    else:
                        text_parts.append(f"{col}: {val}")
            hover_text.append("<br>".join(text_parts))
        
        # Create figure
        fig = go.Figure(data=[go.Scatter3d(
            x=plot_df['x'],
            y=plot_df['y'],
            z=plot_df['z'],
            mode='markers',
            marker=dict(
                size=size_values,
                color=color_values,
                colorscale=self.colorscale,
                opacity=opacity,
                colorbar=dict(title=color_by.replace('_', ' ').title()),
                line=dict(width=0.5, color='darkgray')
            ),
            text=hover_text,
            hovertemplate='%{text}<extra></extra>',
            name='Counties'
        )])
        
        # Layout
        fig.update_layout(
            title=dict(
                text=title,
                x=0.5,
                font=dict(size=16)
            ),
            scene=dict(
                xaxis=dict(title='Component 1', showgrid=True, gridwidth=1),
                yaxis=dict(title='Component 2', showgrid=True, gridwidth=1),
                zaxis=dict(title='Component 3', showgrid=True, gridwidth=1),
                aspectmode='cube'
            ),
            width=1000,
            height=800,
            margin=dict(l=0, r=0, b=0, t=40),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def visualize_domain_comparison(self, df: pd.DataFrame,
                                    domain_embeddings: Dict[str, np.ndarray],
                                    method: str = "umap") -> go.Figure:
        """
        Create side-by-side 3D visualizations for each domain.
        
        Args:
            df: DataFrame with county metadata
            domain_embeddings: Dictionary of domain-specific embeddings
            method: Projection method
            
        Returns:
            Plotly Figure with subplots
        """
        domains = list(domain_embeddings.keys())
        n_domains = len(domains)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'scatter3d'}] * 2] * 2,
            subplot_titles=[d.title() + " Domain" for d in domains],
            vertical_spacing=0.05,
            horizontal_spacing=0.05
        )
        
        positions = [(1, 1), (1, 2), (2, 1), (2, 2)]
        
        for i, (domain, embeddings) in enumerate(domain_embeddings.items()):
            if i >= 4:
                break
            
            # Compute projection
            coords = self.compute_projection(embeddings, method=method)
            
            row, col = positions[i]
            
            # Add trace
            fig.add_trace(
                go.Scatter3d(
                    x=coords[:, 0],
                    y=coords[:, 1],
                    z=coords[:, 2],
                    mode='markers',
                    marker=dict(
                        size=5,
                        color=df['risk_score'] if 'risk_score' in df.columns else None,
                        colorscale=self.colorscale,
                        opacity=0.7
                    ),
                    text=df['county_name'],
                    hovertemplate='<b>%{text}</b><extra></extra>',
                    name=domain.title()
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title=dict(
                text="Cross-Domain Vector Space Comparison",
                x=0.5,
                font=dict(size=18)
            ),
            height=1000,
            width=1200,
            showlegend=False
        )
        
        return fig
    
    def visualize_anomalies(self, coords: np.ndarray, df: pd.DataFrame,
                           anomaly_df: pd.DataFrame,
                           title: str = "Anomaly Detection in Vector Space") -> go.Figure:
        """
        Highlight anomalous counties in 3D space.
        
        Args:
            coords: 3D coordinates
            df: DataFrame with all counties
            anomaly_df: DataFrame with anomaly scores
            title: Plot title
            
        Returns:
            Plotly Figure
        """
        # Merge anomaly info
        plot_df = df.merge(anomaly_df[['fips', 'anomaly_score', 'is_anomaly']], on='fips')
        
        # Create figure with two traces
        fig = go.Figure()
        
        # Normal counties
        normal = plot_df[~plot_df['is_anomaly']]
        fig.add_trace(go.Scatter3d(
            x=coords[normal.index, 0],
            y=coords[normal.index, 1],
            z=coords[normal.index, 2],
            mode='markers',
            marker=dict(
                size=4,
                color='lightgray',
                opacity=0.4
            ),
            name='Normal',
            text=normal['county_name'],
            hovertemplate='<b>%{text}</b><extra></extra>'
        ))
        
        # Anomalous counties
        anomalies = plot_df[plot_df['is_anomaly']]
        fig.add_trace(go.Scatter3d(
            x=coords[anomalies.index, 0],
            y=coords[anomalies.index, 1],
            z=coords[anomalies.index, 2],
            mode='markers',
            marker=dict(
                size=10,
                color=anomalies['anomaly_score'],
                colorscale='Reds',
                opacity=0.9,
                line=dict(width=2, color='darkred')
            ),
            name='Anomaly',
            text=anomalies['county_name'],
            hovertemplate='<b>%{text}</b><br>Anomaly Score: %{marker.color:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            scene=dict(
                xaxis_title='Component 1',
                yaxis_title='Component 2',
                zaxis_title='Component 3'
            ),
            width=1000,
            height=800,
            legend=dict(x=0.02, y=0.98)
        )
        
        return fig
    
    def visualize_similarity_network(self, coords: np.ndarray, df: pd.DataFrame,
                                     fips: str, k: int = 20,
                                     title: Optional[str] = None) -> go.Figure:
        """
        Visualize a county and its nearest neighbors in 3D.
        
        Args:
            coords: 3D coordinates
            df: DataFrame with county metadata
            fips: Center county FIPS code
            k: Number of neighbors to show
            title: Plot title
            
        Returns:
            Plotly Figure
        """
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Find center county
        center_idx = df[df['fips'] == fips].index[0]
        center_name = df.loc[center_idx, 'county_name']
        
        if title is None:
            title = f"Similarity Network: {center_name}"
        
        # Compute similarities
        similarities = cosine_similarity([coords[center_idx]], coords)[0]
        
        # Get top k neighbors
        top_indices = np.argsort(similarities)[::-1][:k+1]
        
        # Create figure
        fig = go.Figure()
        
        # Plot all counties faintly
        fig.add_trace(go.Scatter3d(
            x=coords[:, 0],
            y=coords[:, 1],
            z=coords[:, 2],
            mode='markers',
            marker=dict(size=3, color='lightgray', opacity=0.2),
            name='All Counties',
            hoverinfo='skip'
        ))
        
        # Plot neighbors
        neighbor_coords = coords[top_indices]
        neighbor_sims = similarities[top_indices]
        neighbor_names = df.iloc[top_indices]['county_name'].values
        
        fig.add_trace(go.Scatter3d(
            x=neighbor_coords[:, 0],
            y=neighbor_coords[:, 1],
            z=neighbor_coords[:, 2],
            mode='markers+text',
            marker=dict(
                size=8,
                color=neighbor_sims,
                colorscale='Viridis',
                opacity=0.9
            ),
            text=neighbor_names,
            textposition='top center',
            textfont=dict(size=8),
            name='Similar Counties',
            hovertemplate='<b>%{text}</b><br>Similarity: %{marker.color:.3f}<extra></extra>'
        ))
        
        # Draw lines from center to neighbors
        center_coord = coords[center_idx]
        for i, neighbor_idx in enumerate(top_indices[1:], 1):  # Skip self
            neighbor_coord = coords[neighbor_idx]
            
            fig.add_trace(go.Scatter3d(
                x=[center_coord[0], neighbor_coord[0]],
                y=[center_coord[1], neighbor_coord[1]],
                z=[center_coord[2], neighbor_coord[2]],
                mode='lines',
                line=dict(color='rgba(100,100,100,0.3)', width=1),
                hoverinfo='skip',
                showlegend=False
            ))
        
        # Highlight center
        fig.add_trace(go.Scatter3d(
            x=[center_coord[0]],
            y=[center_coord[1]],
            z=[center_coord[2]],
            mode='markers+text',
            marker=dict(size=15, color='red', symbol='diamond'),
            text=[center_name],
            textposition='top center',
            textfont=dict(size=10, color='red'),
            name='Center County'
        ))
        
        fig.update_layout(
            title=dict(text=title, x=0.5, font=dict(size=16)),
            scene=dict(
                xaxis_title='Component 1',
                yaxis_title='Component 2',
                zaxis_title='Component 3'
            ),
            width=1000,
            height=800,
            showlegend=True
        )
        
        return fig
    
    def create_animated_rotation(self, fig: go.Figure, output_path: str,
                                 n_frames: int = 36, duration: int = 50) -> None:
        """
        Create an animated rotating view of a 3D plot.
        
        Args:
            fig: Plotly Figure to animate
            output_path: Path to save HTML file
            n_frames: Number of rotation frames
            duration: Duration per frame in milliseconds
        """
        frames = []
        
        for i in range(n_frames):
            angle = i * (360 / n_frames)
            frames.append(go.Frame(
                layout=dict(
                    scene=dict(
                        camera=dict(
                            eye=dict(
                                x=1.5 * np.cos(np.radians(angle)),
                                y=1.5 * np.sin(np.radians(angle)),
                                z=1.0
                            )
                        )
                    )
                )
            ))
        
        fig.frames = frames
        
        # Add play button
        fig.update_layout(
            updatemenus=[dict(
                type='buttons',
                showactive=False,
                buttons=[dict(
                    label='▶ Rotate',
                    method='animate',
                    args=[None, dict(
                        frame=dict(duration=duration, redraw=True),
                        fromcurrent=True,
                        transition=dict(duration=0)
                    )]
                )]
            )]
        )
        
        # Save
        fig.write_html(output_path)
        print(f"Saved animated visualization to {output_path}")
    
    def export_static(self, fig: go.Figure, output_path: str,
                     width: int = 1200, height: int = 900) -> None:
        """
        Export a static image of the 3D plot.
        
        Args:
            fig: Plotly Figure
            output_path: Output file path (.png, .pdf, .svg)
            width: Image width
            height: Image height
        """
        fig.write_image(output_path, width=width, height=height, scale=2)
        print(f"Saved static image to {output_path}")


def create_full_visualization_suite(manager: VectorSpaceManager,
                                   output_dir: Optional[str] = None) -> Dict[str, go.Figure]:
    """
    Create a complete suite of 3D visualizations.
    
    Args:
        manager: VectorSpaceManager with built index
        output_dir: Directory to save visualizations (optional)
        
    Returns:
        Dictionary of visualization names to figures
    """
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    visualizer = Vector3DVisualizer(manager)
    df = manager.df
    figures = {}
    
    print("Creating visualization suite...")
    
    # 1. Main 3D projection colored by risk score
    print("  1. Main risk-colored projection...")
    coords = visualizer.compute_projection(manager.embeddings, method="umap")
    fig1 = visualizer.create_3d_scatter(
        coords, df,
        color_by="risk_score",
        size_by="total_population",
        title="County Risk Landscape (UMAP 3D)"
    )
    figures['risk_landscape'] = fig1
    
    # 2. Vulnerability view
    print("  2. Vulnerability view...")
    fig2 = visualizer.create_3d_scatter(
        coords, df,
        color_by="vulnerability_index",
        title="Vulnerability Distribution (UMAP 3D)"
    )
    figures['vulnerability_landscape'] = fig2
    
    # 3. Domain comparison
    print("  3. Domain comparison...")
    if manager.analyzer:
        fig3 = visualizer.visualize_domain_comparison(
            df, manager.analyzer.domain_embeddings, method="umap"
        )
        figures['domain_comparison'] = fig3
    
    # 4. Anomaly detection
    print("  4. Anomaly detection...")
    anomalies = manager.get_anomalies(contamination=0.03)
    fig4 = visualizer.visualize_anomalies(coords, df, anomalies)
    figures['anomalies'] = fig4
    
    # 5. Example similarity network
    print("  5. Similarity network example...")
    sample_fips = df.iloc[0]['fips']
    fig5 = visualizer.visualize_similarity_network(coords, df, sample_fips, k=15)
    figures['similarity_network'] = fig5
    
    # Save if output directory provided
    if output_dir:
        print(f"\nSaving visualizations to {output_dir}...")
        for name, fig in figures.items():
            # Save as HTML
            html_path = output_dir / f"{name}.html"
            fig.write_html(str(html_path))
            print(f"  Saved {name}.html")
            
            # Save as PNG
            try:
                png_path = output_dir / f"{name}.png"
                visualizer.export_static(fig, str(png_path))
                print(f"  Saved {name}.png")
            except Exception as e:
                print(f"  Could not save PNG for {name}: {e}")
    
    return figures


def demo_visualization():
    """
    Demonstrate the 3D visualization capabilities.
    Creates sample visualizations using the vector space.
    """
    print("=" * 70)
    print("ResilienceAI 3D Vector Space Visualization Demo")
    print("=" * 70)
    
    # Load or create vector space
    from vector_space import create_vector_space
    
    print("\nInitializing vector space...")
    manager = create_vector_space()
    
    # Create visualizations
    output_dir = FIGURES_DIR / "vector_3d"
    figures = create_full_visualization_suite(manager, output_dir=output_dir)
    
    print("\n" + "=" * 70)
    print("Visualization Demo Complete!")
    print(f"Open the HTML files in {output_dir} to explore interactively.")
    print("=" * 70)
    
    # Print summary
    print("\nCreated visualizations:")
    for name in figures.keys():
        print(f"  - {name}")
    
    return figures


if __name__ == "__main__":
    # Run demo
    figures = demo_visualization()
