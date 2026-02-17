"""
ResilienceAI - Vector Space 3D Visualization Examples

This script demonstrates the interactive 3D visualization capabilities
of the hyperdimensional vector space module.

Run this to generate interactive HTML visualizations that can be opened
in a web browser for exploration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from pathlib import Path

# Import vector space modules
from src.vector_space import VectorSpaceManager, create_vector_space
from src.visualizations.vector_3d import Vector3DVisualizer, create_full_visualization_suite
from config import PROCESSED_DIR, FIGURES_DIR


def example_1_basic_3d_projection():
    """
    Example 1: Create a basic 3D projection of the county vector space.
    
    This creates an interactive 3D scatter plot where:
    - Each point represents a county
    - Color represents risk score
    - Size represents population
    - Hover shows county details
    """
    print("\n" + "=" * 70)
    print("Example 1: Basic 3D Projection")
    print("=" * 70)
    
    # Load or create vector space
    print("\nLoading vector space...")
    manager = create_vector_space()
    
    # Create visualizer
    visualizer = Vector3DVisualizer(manager)
    
    # Compute 3D projection using UMAP
    print("Computing UMAP projection to 3D...")
    coords = visualizer.compute_projection(manager.embeddings, method="umap")
    
    # Create 3D scatter plot
    print("Creating interactive 3D plot...")
    fig = visualizer.create_3d_scatter(
        coords,
        manager.df,
        color_by="risk_score",
        size_by="total_population",
        title="County Risk Landscape (UMAP 3D Projection)",
        hover_data=['county_name', 'fips', 'risk_score', 'vulnerability_index', 
                   'disaster_count', 'median_income', 'poverty_pct']
    )
    
    # Save
    output_path = FIGURES_DIR / "vector_3d" / "example_1_basic_3d.html"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(output_path))
    print(f"\nSaved to: {output_path}")
    print("Open this file in a web browser to explore interactively!")
    
    return fig


def example_2_domain_comparison():
    """
    Example 2: Compare counties across different domains.
    
    Creates a 2x2 grid of 3D plots showing how counties cluster
    differently in each domain (climate, health, infrastructure, socioeconomic).
    """
    print("\n" + "=" * 70)
    print("Example 2: Cross-Domain Comparison")
    print("=" * 70)
    
    print("\nLoading vector space with domain analysis...")
    manager = create_vector_space()
    
    visualizer = Vector3DVisualizer(manager)
    
    print("Creating domain comparison visualization...")
    fig = visualizer.visualize_domain_comparison(
        manager.df,
        manager.analyzer.domain_embeddings,
        method="umap"
    )
    
    output_path = FIGURES_DIR / "vector_3d" / "example_2_domain_comparison.html"
    fig.write_html(str(output_path))
    print(f"\nSaved to: {output_path}")
    
    return fig


def example_3_anomaly_detection():
    """
    Example 3: Visualize anomalous counties.
    
    Highlights counties that are outliers in the vector space,
    potentially indicating unusual risk profiles.
    """
    print("\n" + "=" * 70)
    print("Example 3: Anomaly Detection Visualization")
    print("=" * 70)
    
    print("\nLoading vector space...")
    manager = create_vector_space()
    
    visualizer = Vector3DVisualizer(manager)
    
    # Compute projection
    print("Computing projection...")
    coords = visualizer.compute_projection(manager.embeddings, method="umap")
    
    # Detect anomalies
    print("Detecting anomalies...")
    anomalies = manager.get_anomalies(contamination=0.03)
    n_anomalies = anomalies['is_anomaly'].sum()
    print(f"Found {n_anomalies} anomalous counties")
    
    # Create visualization
    print("Creating anomaly visualization...")
    fig = visualizer.visualize_anomalies(
        coords,
        manager.df,
        anomalies,
        title="Anomalous Counties in Vector Space"
    )
    
    output_path = FIGURES_DIR / "vector_3d" / "example_3_anomalies.html"
    fig.write_html(str(output_path))
    print(f"\nSaved to: {output_path}")
    
    # Print top anomalies
    print("\nTop 5 anomalous counties:")
    top_anomalies = anomalies[anomalies['is_anomaly']].head(5)
    for _, row in top_anomalies.iterrows():
        print(f"  - {row['county_name']}: score {row['anomaly_score']:.3f}")
    
    return fig


def example_4_similarity_network():
    """
    Example 4: Visualize similarity network for a specific county.
    
    Shows a county and its nearest neighbors in the vector space,
    connected by lines to show similarity relationships.
    """
    print("\n" + "=" * 70)
    print("Example 4: Similarity Network")
    print("=" * 70)
    
    print("\nLoading vector space...")
    manager = create_vector_space()
    
    visualizer = Vector3DVisualizer(manager)
    
    # Compute projection
    print("Computing projection...")
    coords = visualizer.compute_projection(manager.embeddings, method="umap")
    
    # Pick a sample county (first one)
    sample_fips = manager.df.iloc[0]['fips']
    sample_name = manager.df.iloc[0]['county_name']
    
    print(f"\nCreating similarity network for: {sample_name}")
    
    # Find similar counties
    similar = manager.search_similar(sample_fips, k=10)
    print(f"\nTop 5 similar counties:")
    for _, row in similar.head(5).iterrows():
        print(f"  - {row['county_name']}: similarity {row['similarity_score']:.3f}")
    
    # Create visualization
    fig = visualizer.visualize_similarity_network(
        coords,
        manager.df,
        sample_fips,
        k=15,
        title=f"Similarity Network: {sample_name}"
    )
    
    output_path = FIGURES_DIR / "vector_3d" / "example_4_similarity_network.html"
    fig.write_html(str(output_path))
    print(f"\nSaved to: {output_path}")
    
    return fig


def example_5_multi_view_dashboard():
    """
    Example 5: Create a comprehensive visualization suite.
    
    Generates all visualization types and saves them to a directory.
    """
    print("\n" + "=" * 70)
    print("Example 5: Complete Visualization Suite")
    print("=" * 70)
    
    print("\nLoading vector space...")
    manager = create_vector_space()
    
    output_dir = FIGURES_DIR / "vector_3d" / "complete_suite"
    print(f"\nGenerating complete visualization suite in: {output_dir}")
    
    figures = create_full_visualization_suite(manager, output_dir=output_dir)
    
    print("\nGenerated visualizations:")
    for name in figures.keys():
        print(f"  ✓ {name}.html")
    
    return figures


def example_6_cross_domain_insights():
    """
    Example 6: Explore cross-domain insights.
    
    Discovers and visualizes counties with interesting cross-domain patterns.
    """
    import plotly.graph_objects as go
    
    print("\n" + "=" * 70)
    print("Example 6: Cross-Domain Insights")
    print("=" * 70)
    
    print("\nLoading vector space...")
    manager = create_vector_space()
    
    print("\nDiscovering cross-domain insights...")
    insights = manager.get_insights(top_n=10)
    
    print("\nTop insights:")
    for i, insight in enumerate(insights[:10], 1):
        print(f"\n{i}. {insight.county_name}")
        print(f"   Type: {insight.insight_type}")
        print(f"   Description: {insight.description}")
        print(f"   Correlation strength: {insight.correlation_strength:.3f}")
    
    # Create a visualization highlighting these counties
    visualizer = Vector3DVisualizer(manager)
    coords = visualizer.compute_projection(manager.embeddings, method="umap")
    
    # Mark insight counties
    insight_fips = [ins.county_fips for ins in insights]
    manager.df['has_insight'] = manager.df['fips'].isin(insight_fips)
    
    # Create figure with highlighted insights
    fig = go.Figure()
    
    # Normal counties
    normal = manager.df[~manager.df['has_insight']]
    normal_idx = normal.index
    
    fig.add_trace(go.Scatter3d(
        x=coords[normal_idx, 0],
        y=coords[normal_idx, 1],
        z=coords[normal_idx, 2],
        mode='markers',
        marker=dict(size=4, color='lightgray', opacity=0.3),
        name='Other Counties',
        hoverinfo='skip'
    ))
    
    # Insight counties
    insight_df = manager.df[manager.df['has_insight']]
    insight_idx = insight_df.index
    
    fig.add_trace(go.Scatter3d(
        x=coords[insight_idx, 0],
        y=coords[insight_idx, 1],
        z=coords[insight_idx, 2],
        mode='markers',
        marker=dict(
            size=10,
            color=insight_df['risk_score'],
            colorscale='Viridis',
            opacity=0.9,
            line=dict(width=2, color='red')
        ),
        text=insight_df['county_name'],
        name='Insight Counties',
        hovertemplate='<b>%{text}</b><extra></extra>'
    ))
    
    fig.update_layout(
        title=dict(
            text="Counties with Cross-Domain Insights",
            x=0.5,
            font=dict(size=16)
        ),
        scene=dict(
            xaxis_title='Component 1',
            yaxis_title='Component 2',
            zaxis_title='Component 3'
        ),
        width=1000,
        height=800
    )
    
    output_path = FIGURES_DIR / "vector_3d" / "example_6_insights.html"
    fig.write_html(str(output_path))
    print(f"\nSaved to: {output_path}")
    
    return fig


def print_usage_instructions():
    """Print instructions for using the visualizations."""
    print("\n" + "=" * 70)
    print("Usage Instructions")
    print("=" * 70)
    print("""
The generated HTML files are interactive Plotly visualizations.
Open them in any modern web browser to explore:

Navigation Controls:
  - Left click + drag: Rotate the 3D view
  - Right click + drag: Pan the view
  - Scroll: Zoom in/out
  - Double click: Reset to default view

Interactivity:
  - Hover over points to see county details
  - Click legend items to toggle visibility
  - Use the mode bar (top right) for additional options:
    - Download plot as PNG
    - Box select/Lasso select
    - Reset axes
    - Toggle spike lines

The visualizations work entirely in the browser - no server required!
    """)


def main():
    """Run all examples."""
    print("=" * 70)
    print("ResilienceAI - Vector Space 3D Visualization Examples")
    print("=" * 70)
    print("""
This script demonstrates the 3D visualization capabilities of the
ResilienceAI vector space module. It will generate interactive HTML
files that can be opened in a web browser.

Requirements:
  - sentence-transformers (for embeddings)
  - faiss-cpu (for fast similarity search)
  - umap-learn (for dimensionality reduction)
  - plotly (for interactive 3D visualizations)

The script will create visualizations in:
  outputs/figures/vector_3d/
""")
    
    # Check if data exists
    if not (PROCESSED_DIR / "county_features.csv").exists():
        print("\nERROR: County features data not found!")
        print(f"Expected at: {PROCESSED_DIR / 'county_features.csv'}")
        print("\nPlease run the data pipeline first to generate county features.")
        return
    
    try:
        # Run examples
        example_1_basic_3d_projection()
        example_2_domain_comparison()
        example_3_anomaly_detection()
        example_4_similarity_network()
        example_5_multi_view_dashboard()
        example_6_cross_domain_insights()
        
        print_usage_instructions()
        
        print("\n" + "=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)
        print(f"\nVisualizations saved to: {FIGURES_DIR / 'vector_3d'}")
        print("Open the HTML files in a web browser to explore.")
        
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return


if __name__ == "__main__":
    main()
