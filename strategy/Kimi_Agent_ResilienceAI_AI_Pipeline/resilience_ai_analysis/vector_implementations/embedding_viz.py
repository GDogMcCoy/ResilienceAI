"""
Embedding Visualization Tools

This module provides interactive visualization tools for embedding analysis:
- t-SNE projections
- UMAP projections
- PCA scatter plots
- Similarity heatmaps
- Domain comparison radar charts

Author: Vector Embedding Specialist
"""

from typing import Dict, List, Optional, Any, Tuple, Union
import numpy as np
import pandas as pd
import warnings

# Optional imports
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    warnings.warn("Plotly not installed. Visualizations will be limited.")

try:
    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import umap
    UMAP_AVAILABLE = True
except ImportError:
    UMAP_AVAILABLE = False
    warnings.warn("UMAP not installed. UMAP projections unavailable.")


class EmbeddingVisualizer:
    """
    Visualization tools for embedding analysis.
    
    This class provides interactive visualizations using Plotly for:
    - Dimensionality reduction projections (t-SNE, UMAP, PCA)
    - Similarity heatmaps
    - Domain comparison radar charts
    - Interactive scatter plots
    
    Example:
        >>> viz = EmbeddingVisualizer(embeddings, metadata)
        >>> 
        >>> # Compute and plot UMAP projection
        >>> fig = viz.plot_2d_scatter(
        ...     projection_type="umap",
        ...     color_by="risk_score",
        ...     hover_data=["vulnerability_index"]
        ... )
        >>> fig.show()
    """
    
    def __init__(
        self,
        embeddings: np.ndarray,
        metadata: pd.DataFrame
    ):
        """
        Initialize the visualizer.
        
        Args:
            embeddings: Array of embedding vectors
            metadata: DataFrame with county metadata
        """
        self.embeddings = embeddings
        self.metadata = metadata
        self.projections = {}
        
        # Validate inputs
        if len(embeddings) != len(metadata):
            raise ValueError(
                f"Embeddings ({len(embeddings)}) and metadata ({len(metadata)}) "
                "must have same length"
            )
    
    def compute_tsne(
        self,
        n_components: int = 2,
        perplexity: float = 30.0,
        learning_rate: float = 200.0,
        n_iter: int = 1000,
        random_state: int = 42,
        n_jobs: int = -1
    ) -> np.ndarray:
        """
        Compute t-SNE projection.
        
        t-SNE is a non-linear dimensionality reduction technique that
        preserves local structure. Good for visualizing clusters.
        
        Args:
            n_components: 2 or 3 for visualization
            perplexity: Perplexity parameter (typically 5-50)
            learning_rate: Learning rate for optimization
            n_iter: Number of iterations
            random_state: Random seed
            n_jobs: Number of parallel jobs (-1 for all cores)
            
        Returns:
            Projected coordinates (n_samples x n_components)
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for t-SNE")
        
        print(f"Computing t-SNE (perplexity={perplexity}, n_components={n_components})...")
        
        tsne = TSNE(
            n_components=n_components,
            perplexity=perplexity,
            learning_rate=learning_rate,
            n_iter=n_iter,
            random_state=random_state,
            n_jobs=n_jobs,
            verbose=1
        )
        
        projection = tsne.fit_transform(self.embeddings)
        self.projections['tsne'] = projection
        
        print(f"t-SNE complete. KL divergence: {tsne.kl_divergence_:.4f}")
        
        return projection
    
    def compute_umap(
        self,
        n_components: int = 2,
        n_neighbors: int = 15,
        min_dist: float = 0.1,
        metric: str = "cosine",
        random_state: int = 42
    ) -> np.ndarray:
        """
        Compute UMAP projection.
        
        UMAP is a dimensionality reduction technique that often produces
        better visualizations than t-SNE and is faster.
        
        Args:
            n_components: 2 or 3 for visualization
            n_neighbors: Number of neighbors for local structure
            min_dist: Minimum distance between points
            metric: Distance metric
            random_state: Random seed
            
        Returns:
            Projected coordinates (n_samples x n_components)
        """
        if not UMAP_AVAILABLE:
            raise ImportError("UMAP required for UMAP projection")
        
        print(f"Computing UMAP (n_neighbors={n_neighbors}, min_dist={min_dist})...")
        
        reducer = umap.UMAP(
            n_components=n_components,
            n_neighbors=n_neighbors,
            min_dist=min_dist,
            metric=metric,
            random_state=random_state
        )
        
        projection = reducer.fit_transform(self.embeddings)
        self.projections['umap'] = projection
        
        print("UMAP complete.")
        
        return projection
    
    def compute_pca(
        self,
        n_components: int = 2
    ) -> np.ndarray:
        """
        Compute PCA projection.
        
        PCA is a linear dimensionality reduction technique that
        preserves global structure.
        
        Args:
            n_components: Number of components
            
        Returns:
            Projected coordinates
        """
        if not SKLEARN_AVAILABLE:
            raise ImportError("scikit-learn required for PCA")
        
        print(f"Computing PCA (n_components={n_components})...")
        
        pca = PCA(n_components=n_components)
        projection = pca.fit_transform(self.embeddings)
        self.projections['pca'] = projection
        
        explained_var = sum(pca.explained_variance_ratio_)
        print(f"PCA complete. Explained variance: {explained_var:.2%}")
        
        return projection
    
    def plot_2d_scatter(
        self,
        projection_type: str = "umap",
        color_by: Optional[str] = None,
        size_by: Optional[str] = None,
        hover_data: Optional[List[str]] = None,
        title: Optional[str] = None,
        opacity: float = 0.7,
        marker_size: int = 8
    ) -> go.Figure:
        """
        Create interactive 2D scatter plot.
        
        Args:
            projection_type: "tsne", "umap", or "pca"
            color_by: Column to use for color
            size_by: Column to use for point size
            hover_data: Additional columns for hover tooltip
            title: Plot title
            opacity: Point opacity
            marker_size: Base marker size
            
        Returns:
            Plotly figure
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required for visualization")
        
        # Compute projection if needed
        if projection_type not in self.projections:
            if projection_type == "tsne":
                self.compute_tsne()
            elif projection_type == "umap":
                self.compute_umap()
            elif projection_type == "pca":
                self.compute_pca()
            else:
                raise ValueError(f"Unknown projection: {projection_type}")
        
        projection = self.projections[projection_type]
        
        # Prepare data
        plot_df = pd.DataFrame({
            'x': projection[:, 0],
            'y': projection[:, 1],
            'county_name': self.metadata['county_name'],
            'fips': self.metadata['fips']
        })
        
        # Add color column
        if color_by and color_by in self.metadata.columns:
            plot_df['color'] = self.metadata[color_by]
        
        # Add size column
        if size_by and size_by in self.metadata.columns:
            plot_df['size'] = self.metadata[size_by]
        
        # Add hover data
        hover_cols = ['county_name', 'fips']
        if hover_data:
            for col in hover_data:
                if col in self.metadata.columns:
                    plot_df[col] = self.metadata[col]
                    hover_cols.append(col)
        
        # Create figure
        fig = px.scatter(
            plot_df,
            x='x',
            y='y',
            color='color' if 'color' in plot_df.columns else None,
            size='size' if 'size' in plot_df.columns else None,
            hover_data=hover_cols,
            title=title or f"County Embeddings ({projection_type.upper()})",
            labels={'color': color_by},
            opacity=opacity
        )
        
        fig.update_traces(marker=dict(size=marker_size))
        
        fig.update_layout(
            width=900,
            height=700,
            template='plotly_white',
            xaxis_title=f"{projection_type.upper()} 1",
            yaxis_title=f"{projection_type.upper()} 2"
        )
        
        return fig
    
    def plot_3d_scatter(
        self,
        projection_type: str = "umap",
        color_by: Optional[str] = None,
        hover_data: Optional[List[str]] = None,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Create interactive 3D scatter plot.
        
        Args:
            projection_type: "tsne", "umap", or "pca"
            color_by: Column to use for color
            hover_data: Additional columns for hover tooltip
            title: Plot title
            
        Returns:
            Plotly figure
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required for visualization")
        
        # Compute 3D projection if needed
        proj_key = f"{projection_type}_3d"
        if proj_key not in self.projections:
            if projection_type == "tsne":
                self.compute_tsne(n_components=3)
            elif projection_type == "umap":
                self.compute_umap(n_components=3)
            elif projection_type == "pca":
                self.compute_pca(n_components=3)
            else:
                raise ValueError(f"Unknown projection: {projection_type}")
            self.projections[proj_key] = self.projections[projection_type]
        
        projection = self.projections[proj_key]
        
        # Prepare data
        plot_df = pd.DataFrame({
            'x': projection[:, 0],
            'y': projection[:, 1],
            'z': projection[:, 2],
            'county_name': self.metadata['county_name'],
            'fips': self.metadata['fips']
        })
        
        # Add color column
        if color_by and color_by in self.metadata.columns:
            plot_df['color'] = self.metadata[color_by]
        
        # Add hover data
        hover_cols = ['county_name', 'fips']
        if hover_data:
            for col in hover_data:
                if col in self.metadata.columns:
                    plot_df[col] = self.metadata[col]
                    hover_cols.append(col)
        
        # Create 3D figure
        fig = px.scatter_3d(
            plot_df,
            x='x',
            y='y',
            z='z',
            color='color' if 'color' in plot_df.columns else None,
            hover_data=hover_cols,
            title=title or f"County Embeddings 3D ({projection_type.upper()})",
            labels={'color': color_by},
            opacity=0.7
        )
        
        fig.update_layout(
            width=900,
            height=800,
            template='plotly_white'
        )
        
        return fig
    
    def plot_similarity_heatmap(
        self,
        county_fips: List[str],
        metric: str = "cosine",
        title: Optional[str] = None,
        colorscale: str = "RdYlBu"
    ) -> go.Figure:
        """
        Create similarity heatmap for selected counties.
        
        Args:
            county_fips: List of FIPS codes to include
            metric: Similarity metric
            title: Plot title
            colorscale: Plotly colorscale
            
        Returns:
            Plotly figure
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required for visualization")
        
        # Get embeddings for selected counties
        indices = []
        for fips in county_fips:
            idx = self.metadata[self.metadata['fips'] == fips].index
            if len(idx) == 0:
                raise ValueError(f"FIPS {fips} not found")
            indices.append(idx[0])
        
        selected_embeddings = self.embeddings[indices]
        
        # Compute similarity matrix
        if metric == "cosine":
            from sklearn.metrics.pairwise import cosine_similarity
            sim_matrix = cosine_similarity(selected_embeddings)
        elif metric == "euclidean":
            from sklearn.metrics.pairwise import euclidean_distances
            dist_matrix = euclidean_distances(selected_embeddings)
            sim_matrix = 1 / (1 + dist_matrix)
        else:
            raise ValueError(f"Unknown metric: {metric}")
        
        # Get county names
        county_names = [
            self.metadata[self.metadata['fips'] == fips]['county_name'].iloc[0]
            for fips in county_fips
        ]
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=sim_matrix,
            x=county_names,
            y=county_names,
            colorscale=colorscale,
            zmid=0.5,
            text=np.round(sim_matrix, 2),
            texttemplate='%{text}',
            textfont={"size": 10},
            hoverongaps=False
        ))
        
        fig.update_layout(
            title=title or "County Similarity Matrix",
            width=800,
            height=800,
            xaxis_tickangle=-45,
            xaxis_title="",
            yaxis_title=""
        )
        
        return fig
    
    def plot_domain_comparison(
        self,
        fips: str,
        domain_embeddings: Dict[str, np.ndarray],
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Visualize county profile across different domains using radar chart.
        
        Args:
            fips: County FIPS code
            domain_embeddings: Dictionary of domain-specific embeddings
            title: Plot title
            
        Returns:
            Plotly figure
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required for visualization")
        
        # Get county index
        county_data = self.metadata[self.metadata['fips'] == fips]
        if len(county_data) == 0:
            raise ValueError(f"FIPS {fips} not found")
        
        idx = county_data.index[0]
        county_name = county_data['county_name'].iloc[0]
        
        # Compute similarity to average for each domain
        domains = list(domain_embeddings.keys())
        values = []
        
        for domain, embeddings in domain_embeddings.items():
            county_emb = embeddings[idx]
            avg_emb = np.mean(embeddings, axis=0)
            
            # Cosine similarity
            sim = np.dot(county_emb, avg_emb) / (
                np.linalg.norm(county_emb) * np.linalg.norm(avg_emb) + 1e-8
            )
            values.append(float(sim))
        
        # Create radar chart
        fig = go.Figure(data=go.Scatterpolar(
            r=values + [values[0]],  # Close the polygon
            theta=domains + [domains[0]],
            fill='toself',
            name=county_name,
            line_color='blue',
            fillcolor='rgba(0, 0, 255, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    tickformat='.2f'
                )
            ),
            title=title or f"Domain Profile: {county_name}",
            showlegend=True,
            width=600,
            height=600
        )
        
        return fig
    
    def plot_comparison_dashboard(
        self,
        fips_list: List[str],
        projection_type: str = "umap"
    ) -> go.Figure:
        """
        Create a comparison dashboard for multiple counties.
        
        Args:
            fips_list: List of FIPS codes to compare
            projection_type: Projection type for scatter plot
            
        Returns:
            Plotly figure with subplots
        """
        if not PLOTLY_AVAILABLE:
            raise ImportError("Plotly required for visualization")
        
        # Create subplots
        fig = make_subplots(
            rows=2,
            cols=2,
            subplot_titles=(
                "Embedding Space",
                "Similarity Matrix",
                "Risk Comparison",
                "Vulnerability Comparison"
            ),
            specs=[
                [{"type": "scatter"}, {"type": "heatmap"}],
                [{"type": "bar"}, {"type": "bar"}]
            ]
        )
        
        # 1. Embedding space scatter plot
        if projection_type not in self.projections:
            if projection_type == "umap":
                self.compute_umap()
            elif projection_type == "tsne":
                self.compute_tsne()
            elif projection_type == "pca":
                self.compute_pca()
        
        projection = self.projections[projection_type]
        
        # Highlight selected counties
        colors = ['red' if fips in fips_list else 'lightgray' for fips in self.metadata['fips']]
        sizes = [15 if fips in fips_list else 5 for fips in self.metadata['fips']]
        
        fig.add_trace(
            go.Scatter(
                x=projection[:, 0],
                y=projection[:, 1],
                mode='markers',
                marker=dict(color=colors, size=sizes, opacity=0.7),
                text=self.metadata['county_name'],
                hovertemplate='%{text}<extra></extra>',
                showlegend=False
            ),
            row=1,
            col=1
        )
        
        # 2. Similarity heatmap
        indices = [self.metadata[self.metadata['fips'] == f].index[0] for f in fips_list]
        selected_embeddings = self.embeddings[indices]
        
        from sklearn.metrics.pairwise import cosine_similarity
        sim_matrix = cosine_similarity(selected_embeddings)
        
        county_names = [
            self.metadata[self.metadata['fips'] == f]['county_name'].iloc[0]
            for f in fips_list
        ]
        
        fig.add_trace(
            go.Heatmap(
                z=sim_matrix,
                x=county_names,
                y=county_names,
                colorscale='RdYlBu',
                zmid=0.5,
                showscale=True,
                colorbar=dict(x=0.97, len=0.4, y=0.78)
            ),
            row=1,
            col=2
        )
        
        # 3. Risk comparison
        risk_scores = [
            self.metadata[self.metadata['fips'] == f]['risk_score'].iloc[0]
            for f in fips_list
        ]
        
        fig.add_trace(
            go.Bar(
                x=county_names,
                y=risk_scores,
                name='Risk Score',
                marker_color='coral'
            ),
            row=2,
            col=1
        )
        
        # 4. Vulnerability comparison
        vuln_scores = [
            self.metadata[self.metadata['fips'] == f]['vulnerability_index'].iloc[0]
            for f in fips_list
        ]
        
        fig.add_trace(
            go.Bar(
                x=county_names,
                y=vuln_scores,
                name='Vulnerability',
                marker_color='lightblue'
            ),
            row=2,
            col=2
        )
        
        fig.update_layout(
            title_text="County Comparison Dashboard",
            height=900,
            width=1200,
            showlegend=False
        )
        
        return fig


# Convenience functions
def create_visualizer(
    embeddings: np.ndarray,
    metadata: pd.DataFrame
) -> EmbeddingVisualizer:
    """
    Create an embedding visualizer.
    
    Args:
        embeddings: County embeddings
        metadata: County metadata DataFrame
        
    Returns:
        Configured EmbeddingVisualizer
    """
    return EmbeddingVisualizer(embeddings, metadata)


if __name__ == "__main__":
    # Example usage
    print("EmbeddingVisualizer - Example Usage")
    print("=" * 50)
    
    # Generate sample data
    np.random.seed(42)
    n_counties = 200
    dimension = 128
    
    embeddings = np.random.randn(n_counties, dimension).astype(np.float32)
    
    metadata = pd.DataFrame({
        'fips': [f"{i:05d}" for i in range(n_counties)],
        'county_name': [f"County {i}" for i in range(n_counties)],
        'state': np.random.choice(['AL', 'CA', 'NY', 'TX', 'FL'], n_counties),
        'risk_score': np.random.rand(n_counties),
        'vulnerability_index': np.random.rand(n_counties)
    })
    
    print(f"\nSample data: {n_counties} counties")
    
    # Create visualizer
    viz = EmbeddingVisualizer(embeddings, metadata)
    
    # Compute projections
    print("\n--- Computing Projections ---")
    viz.compute_umap()
    viz.compute_tsne()
    
    # Create plots
    print("\n--- Creating Visualizations ---")
    
    # 2D scatter
    fig_2d = viz.plot_2d_scatter(
        projection_type="umap",
        color_by="risk_score",
        hover_data=["vulnerability_index"]
    )
    print(f"2D scatter plot created: {len(fig_2d.data)} traces")
    
    # Similarity heatmap
    sample_fips = metadata['fips'].head(10).tolist()
    fig_heatmap = viz.plot_similarity_heatmap(sample_fips)
    print(f"Heatmap created: {fig_heatmap.data[0].z.shape}")
    
    print("\nEmbeddingVisualizer ready for use!")
    print("Call fig.show() to display plots.")
