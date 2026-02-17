# ResilienceAI Image Processing Architecture

## Executive Summary

This document provides a comprehensive design for image processing capabilities in ResilienceAI, covering chart exports, visualization images, and thumbnail generation. The architecture supports multiple formats, optimization strategies, caching, and batch processing.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Image Generation](#2-image-generation)
3. [Image Optimization](#3-image-optimization)
4. [Thumbnail Generation](#4-thumbnail-generation)
5. [Format Support](#5-format-support)
6. [Caching Strategy](#6-caching-strategy)
7. [Export API](#7-export-api)
8. [Batch Processing](#8-batch-processing)
9. [Responsive Images](#9-responsive-images)
10. [Metadata Management](#10-metadata-management)
11. [Storage Solutions](#11-storage-solutions)
12. [Performance Tuning](#12-performance-tuning)
13. [Testing Strategy](#13-testing-strategy)
14. [Implementation Priority](#14-implementation-priority)

---

## 1. Architecture Overview

### 1.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ResilienceAI Image Processing                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │   Chart      │    │ Visualization│    │   Thumbnail  │    │   Batch    │ │
│  │  Generator   │    │   Renderer   │    │   Generator  │    │ Processor  │ │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └─────┬──────┘ │
│         │                   │                   │                  │        │
│         └───────────────────┴───────────────────┴──────────────────┘        │
│                                    │                                         │
│                         ┌──────────▼──────────┐                             │
│                         │   Image Pipeline    │                             │
│                         │   Orchestrator      │                             │
│                         └──────────┬──────────┘                             │
│                                    │                                         │
│         ┌──────────────────────────┼──────────────────────────┐             │
│         │                          │                          │             │
│  ┌──────▼──────┐          ┌────────▼────────┐        ┌───────▼──────┐      │
│  │  Optimizer  │          │  Format Engine  │        │   Cacher     │      │
│  └─────────────┘          └─────────────────┘        └──────────────┘      │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Storage Layer                                 │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │  Local FS  │  │    S3      │  │   CDN      │  │   Cache    │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘    │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Core Components

| Component | Responsibility | Technology |
|-----------|---------------|------------|
| Image Generator | Create images from charts/visualizations | Pillow, CairoSVG, Playwright |
| Optimizer | Compress and optimize images | Pillow, mozjpeg, pngquant |
| Format Engine | Convert between formats | Pillow, cairosvg |
| Thumbnail Generator | Create scaled-down versions | Pillow |
| Cache Manager | Store and retrieve cached images | Redis, In-Memory |
| Storage Manager | Persist images to storage | S3, Local FS, CDN |
| Batch Processor | Handle multiple image operations | Celery, AsyncIO |
| Metadata Manager | Track image properties | PostgreSQL, JSON |

---

## 2. Image Generation

### 2.1 Chart Image Generation

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/image_generator/chart_generator.py
"""
Chart Image Generator for ResilienceAI
Handles conversion of chart data to image formats
"""

import io
import base64
from typing import Dict, List, Optional, Union, Any
from dataclasses import dataclass
from enum import Enum
import asyncio
from pathlib import Path

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
import numpy as np

# Optional dependencies for advanced rendering
try:
    import plotly.graph_objects as go
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False


class ChartType(Enum):
    """Supported chart types for image generation"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HEATMAP = "heatmap"
    RADAR = "radar"
    GAUGE = "gauge"
    SANKEY = "sankey"
    TREEMAP = "treemap"
    CUSTOM = "custom"


class ExportFormat(Enum):
    """Supported export formats"""
    PNG = "png"
    JPEG = "jpeg"
    SVG = "svg"
    PDF = "pdf"
    WEBP = "webp"
    TIFF = "tiff"


@dataclass
class ChartConfig:
    """Configuration for chart image generation"""
    width: int = 800
    height: int = 600
    dpi: int = 150
    background_color: str = "#ffffff"
    transparent: bool = False
    font_family: str = "Arial"
    font_size: int = 12
    title: Optional[str] = None
    subtitle: Optional[str] = None
    legend_position: str = "bottom"
    color_palette: List[str] = None
    
    def __post_init__(self):
        if self.color_palette is None:
            self.color_palette = [
                "#3498db", "#e74c3c", "#2ecc71", "#f39c12",
                "#9b59b6", "#1abc9c", "#34495e", "#e67e22"
            ]


@dataclass
class ExportOptions:
    """Options for image export"""
    format: ExportFormat = ExportFormat.PNG
    quality: int = 90  # For JPEG/WebP (0-100)
    optimize: bool = True
    metadata: Optional[Dict[str, Any]] = None


class ChartImageGenerator:
    """
    Main class for generating chart images from data
    """
    
    def __init__(self, config: Optional[ChartConfig] = None):
        self.config = config or ChartConfig()
        self._figure_cache: Dict[str, Figure] = {}
        
    def generate_line_chart(
        self,
        data: Dict[str, List],
        options: Optional[ExportOptions] = None
    ) -> bytes:
        """
        Generate a line chart image
        
        Args:
            data: Dictionary with 'labels' and 'datasets' keys
            options: Export options
            
        Returns:
            Image bytes
        """
        options = options or ExportOptions()
        
        fig, ax = plt.subplots(figsize=(
            self.config.width / self.config.dpi,
            self.config.height / self.config.dpi
        ), dpi=self.config.dpi)
        
        # Set background
        if not self.config.transparent:
            fig.patch.set_facecolor(self.config.background_color)
            ax.set_facecolor(self.config.background_color)
        
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        for idx, dataset in enumerate(datasets):
            color = self.config.color_palette[idx % len(self.config.color_palette)]
            ax.plot(
                labels,
                dataset.get('data', []),
                label=dataset.get('label', f'Series {idx + 1}'),
                color=color,
                linewidth=2.5,
                marker='o',
                markersize=6
            )
        
        # Styling
        ax.set_xlabel(data.get('xLabel', ''), fontsize=self.config.font_size)
        ax.set_ylabel(data.get('yLabel', ''), fontsize=self.config.font_size)
        
        if self.config.title:
            ax.set_title(self.config.title, fontsize=self.config.font_size + 4, fontweight='bold')
        
        if datasets:
            ax.legend(loc=self._get_legend_position())
        
        ax.grid(True, alpha=0.3, linestyle='--')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        return self._export_figure(fig, options)
    
    def generate_bar_chart(
        self,
        data: Dict[str, List],
        options: Optional[ExportOptions] = None,
        horizontal: bool = False
    ) -> bytes:
        """Generate a bar chart image"""
        options = options or ExportOptions()
        
        fig, ax = plt.subplots(figsize=(
            self.config.width / self.config.dpi,
            self.config.height / self.config.dpi
        ), dpi=self.config.dpi)
        
        if not self.config.transparent:
            fig.patch.set_facecolor(self.config.background_color)
            ax.set_facecolor(self.config.background_color)
        
        labels = data.get('labels', [])
        datasets = data.get('datasets', [])
        
        x = np.arange(len(labels))
        width = 0.8 / max(len(datasets), 1)
        
        for idx, dataset in enumerate(datasets):
            color = self.config.color_palette[idx % len(self.config.color_palette)]
            offset = width * (idx - len(datasets) / 2 + 0.5)
            
            if horizontal:
                ax.barh(x + offset, dataset.get('data', []), width,
                       label=dataset.get('label', f'Series {idx + 1}'),
                       color=color, alpha=0.85)
            else:
                ax.bar(x + offset, dataset.get('data', []), width,
                      label=dataset.get('label', f'Series {idx + 1}'),
                      color=color, alpha=0.85)
        
        if not horizontal:
            ax.set_xticks(x)
            ax.set_xticklabels(labels, rotation=45, ha='right')
        else:
            ax.set_yticks(x)
            ax.set_yticklabels(labels)
        
        if self.config.title:
            ax.set_title(self.config.title, fontsize=self.config.font_size + 4, fontweight='bold')
        
        if datasets:
            ax.legend(loc=self._get_legend_position())
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        return self._export_figure(fig, options)
    
    def generate_pie_chart(
        self,
        data: Dict[str, List],
        options: Optional[ExportOptions] = None,
        donut: bool = False
    ) -> bytes:
        """Generate a pie or donut chart image"""
        options = options or ExportOptions()
        
        fig, ax = plt.subplots(figsize=(
            self.config.width / self.config.dpi,
            self.config.height / self.config.dpi
        ), dpi=self.config.dpi)
        
        if not self.config.transparent:
            fig.patch.set_facecolor(self.config.background_color)
        
        labels = data.get('labels', [])
        values = data.get('values', [])
        
        colors = self.config.color_palette[:len(values)]
        
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            pctdistance=0.75 if donut else 0.6
        )
        
        if donut:
            centre_circle = plt.Circle((0, 0), 0.50, fc=self.config.background_color)
            ax.add_artist(centre_circle)
        
        if self.config.title:
            ax.set_title(self.config.title, fontsize=self.config.font_size + 4, fontweight='bold')
        
        plt.tight_layout()
        
        return self._export_figure(fig, options)
    
    def generate_heatmap(
        self,
        data: Dict[str, Any],
        options: Optional[ExportOptions] = None
    ) -> bytes:
        """Generate a heatmap image"""
        options = options or ExportOptions()
        
        fig, ax = plt.subplots(figsize=(
            self.config.width / self.config.dpi,
            self.config.height / self.config.dpi
        ), dpi=self.config.dpi)
        
        if not self.config.transparent:
            fig.patch.set_facecolor(self.config.background_color)
            ax.set_facecolor(self.config.background_color)
        
        matrix = np.array(data.get('matrix', []))
        x_labels = data.get('xLabels', [])
        y_labels = data.get('yLabels', [])
        
        im = ax.imshow(matrix, cmap='YlOrRd', aspect='auto')
        
        # Add colorbar
        cbar = plt.colorbar(im, ax=ax)
        if data.get('colorbarLabel'):
            cbar.set_label(data['colorbarLabel'])
        
        # Set ticks
        if x_labels:
            ax.set_xticks(np.arange(len(x_labels)))
            ax.set_xticklabels(x_labels, rotation=45, ha='right')
        if y_labels:
            ax.set_yticks(np.arange(len(y_labels)))
            ax.set_yticklabels(y_labels)
        
        # Add text annotations
        for i in range(matrix.shape[0]):
            for j in range(matrix.shape[1]):
                text = ax.text(j, i, f'{matrix[i, j]:.1f}',
                             ha="center", va="center", color="black", fontsize=8)
        
        if self.config.title:
            ax.set_title(self.config.title, fontsize=self.config.font_size + 4, fontweight='bold')
        
        plt.tight_layout()
        
        return self._export_figure(fig, options)
    
    def _export_figure(self, fig: Figure, options: ExportOptions) -> bytes:
        """Export matplotlib figure to bytes"""
        buffer = io.BytesIO()
        
        if options.format == ExportFormat.PNG:
            fig.savefig(
                buffer,
                format='png',
                dpi=self.config.dpi,
                transparent=self.config.transparent,
                bbox_inches='tight',
                pad_inches=0.1,
                optimize=options.optimize
            )
        elif options.format == ExportFormat.JPEG:
            fig.savefig(
                buffer,
                format='jpeg',
                dpi=self.config.dpi,
                transparent=False,
                bbox_inches='tight',
                pad_inches=0.1,
                quality=options.quality,
                optimize=options.optimize
            )
        elif options.format == ExportFormat.SVG:
            fig.savefig(
                buffer,
                format='svg',
                bbox_inches='tight',
                pad_inches=0.1
            )
        elif options.format == ExportFormat.PDF:
            fig.savefig(
                buffer,
                format='pdf',
                bbox_inches='tight',
                pad_inches=0.1
            )
        elif options.format == ExportFormat.WEBP:
            # Save as PNG first, then convert
            png_buffer = io.BytesIO()
            fig.savefig(png_buffer, format='png', dpi=self.config.dpi,
                       transparent=self.config.transparent, bbox_inches='tight')
            png_buffer.seek(0)
            
            from PIL import Image
            img = Image.open(png_buffer)
            img.save(buffer, 'WEBP', quality=options.quality, optimize=options.optimize)
        
        plt.close(fig)
        buffer.seek(0)
        return buffer.getvalue()
    
    def _get_legend_position(self) -> str:
        """Convert legend position string to matplotlib location"""
        positions = {
            'top': 'upper center',
            'bottom': 'lower center',
            'left': 'center left',
            'right': 'center right',
            'top-left': 'upper left',
            'top-right': 'upper right',
            'bottom-left': 'lower left',
            'bottom-right': 'lower right'
        }
        return positions.get(self.config.legend_position, 'best')
    
    def to_base64(self, image_bytes: bytes) -> str:
        """Convert image bytes to base64 string"""
        return base64.b64encode(image_bytes).decode('utf-8')
    
    def to_data_url(self, image_bytes: bytes, format: ExportFormat) -> str:
        """Convert image bytes to data URL"""
        mime_types = {
            ExportFormat.PNG: 'image/png',
            ExportFormat.JPEG: 'image/jpeg',
            ExportFormat.SVG: 'image/svg+xml',
            ExportFormat.WEBP: 'image/webp'
        }
        mime_type = mime_types.get(format, 'image/png')
        base64_data = self.to_base64(image_bytes)
        return f'data:{mime_type};base64,{base64_data}'


class HTMLChartRenderer:
    """
    Renders charts using HTML/CSS/JS for high-fidelity output
    Uses Playwright for headless browser rendering
    """
    
    def __init__(self):
        self.template_dir = Path(__file__).parent / 'templates'
        
    async def render_chart_js(
        self,
        chart_config: Dict[str, Any],
        width: int = 800,
        height: int = 600,
        format: ExportFormat = ExportFormat.PNG
    ) -> bytes:
        """
        Render Chart.js configuration to image
        
        Args:
            chart_config: Chart.js configuration object
            width: Output width in pixels
            height: Output height in pixels
            format: Output format
            
        Returns:
            Image bytes
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise ImportError("Playwright is required for HTML rendering")
        
        html_content = self._generate_chart_html(chart_config, width, height)
        
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page(viewport={'width': width, 'height': height})
            
            await page.set_content(html_content)
            await page.wait_for_selector('#chart-canvas')
            await asyncio.sleep(0.5)  # Wait for animation
            
            screenshot_options = {
                'type': format.value if format != ExportFormat.JPEG else 'jpeg'
            }
            if format == ExportFormat.JPEG:
                screenshot_options['quality'] = 90
            
            image_bytes = await page.screenshot(screenshot_options)
            await browser.close()
            
            return image_bytes
    
    def _generate_chart_html(self, config: Dict, width: int, height: int) -> str:
        """Generate HTML with embedded Chart.js"""
        config_json = json.dumps(config)
        
        return f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        body {{ margin: 0; padding: 0; }}
        #chart-container {{ width: {width}px; height: {height}px; }}
    </style>
</head>
<body>
    <div id="chart-container">
        <canvas id="chart-canvas"></canvas>
    </div>
    <script>
        const ctx = document.getElementById('chart-canvas').getContext('2d');
        const config = {config_json};
        new Chart(ctx, config);
    </script>
</body>
</html>'''


# Factory function for easy chart generation
def create_chart_generator(
    chart_type: ChartType,
    config: Optional[ChartConfig] = None
) -> ChartImageGenerator:
    """Factory function to create chart generator"""
    return ChartImageGenerator(config)


# Example usage
if __name__ == "__main__":
    import json
    
    # Create generator
    generator = ChartImageGenerator(ChartConfig(
        width=800,
        height=500,
        title="Resilience Score Trend"
    ))
    
    # Sample data
    line_data = {
        "labels": ["Jan", "Feb", "Mar", "Apr", "May", "Jun"],
        "datasets": [
            {
                "label": "System A",
                "data": [85, 87, 90, 88, 92, 95]
            },
            {
                "label": "System B",
                "data": [78, 82, 85, 89, 91, 93]
            }
        ],
        "xLabel": "Month",
        "yLabel": "Resilience Score"
    }
    
    # Generate image
    image_bytes = generator.generate_line_chart(
        line_data,
        ExportOptions(format=ExportFormat.PNG, quality=95)
    )
    
    # Save to file
    with open('/mnt/okcomputer/output/resilience_ai_analysis/code/image_generator/chart_example.png', 'wb') as f:
        f.write(image_bytes)
    
    print("Chart image generated successfully!")
```

### 2.2 Visualization Image Generator

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/image_generator/visualization_generator.py
"""
Advanced Visualization Image Generator
Handles complex visualizations: network graphs, topology diagrams, dashboards
"""

import io
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import math

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, Circle, FancyArrowPatch
from matplotlib.collections import LineCollection
import numpy as np
from PIL import Image, ImageDraw, ImageFont


@dataclass
class NodeStyle:
    """Style configuration for visualization nodes"""
    color: str = "#3498db"
    border_color: str = "#2980b9"
    border_width: float = 2.0
    size: float = 30.0
    shape: str = "circle"  # circle, square, diamond
    label_color: str = "#2c3e50"
    label_size: int = 10


@dataclass
class EdgeStyle:
    """Style configuration for visualization edges"""
    color: str = "#7f8c8d"
    width: float = 1.5
    style: str = "solid"  # solid, dashed, dotted
    arrow_size: float = 10.0
    label_color: str = "#7f8c8d"
    label_size: int = 9


class NetworkGraphGenerator:
    """Generate network topology and graph visualizations"""
    
    def __init__(self, width: int = 1000, height: int = 800, dpi: int = 150):
        self.width = width
        self.height = height
        self.dpi = dpi
        self.node_style = NodeStyle()
        self.edge_style = EdgeStyle()
    
    def generate_topology_map(
        self,
        nodes: List[Dict[str, Any]],
        edges: List[Dict[str, Any]],
        layout: str = "force-directed"
    ) -> bytes:
        """
        Generate network topology visualization
        
        Args:
            nodes: List of node objects with id, label, type, status
            edges: List of edge objects with source, target, type
            layout: Layout algorithm (force-directed, circular, hierarchical)
            
        Returns:
            PNG image bytes
        """
        fig, ax = plt.subplots(figsize=(self.width/self.dpi, self.height/self.dpi), dpi=self.dpi)
        ax.set_facecolor('#f8f9fa')
        
        # Calculate node positions based on layout
        positions = self._calculate_layout(nodes, edges, layout)
        
        # Draw edges
        for edge in edges:
            source_pos = positions.get(edge['source'])
            target_pos = positions.get(edge['target'])
            
            if source_pos and target_pos:
                self._draw_edge(ax, source_pos, target_pos, edge)
        
        # Draw nodes
        for node in nodes:
            pos = positions.get(node['id'])
            if pos:
                self._draw_node(ax, pos, node)
        
        # Set axis properties
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        # Add legend
        self._add_topology_legend(ax, nodes)
        
        plt.tight_layout()
        
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=self.dpi, bbox_inches='tight',
                   facecolor='#f8f9fa', pad_inches=0.1)
        plt.close(fig)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    def _calculate_layout(
        self,
        nodes: List[Dict],
        edges: List[Dict],
        layout: str
    ) -> Dict[str, Tuple[float, float]]:
        """Calculate node positions using specified layout algorithm"""
        positions = {}
        n = len(nodes)
        
        if layout == "circular":
            # Circular layout
            radius = 0.8
            for i, node in enumerate(nodes):
                angle = 2 * math.pi * i / n - math.pi / 2
                positions[node['id']] = (
                    radius * math.cos(angle),
                    radius * math.sin(angle)
                )
                
        elif layout == "hierarchical":
            # Hierarchical tree layout
            levels = self._calculate_hierarchy_levels(nodes, edges)
            for level, level_nodes in levels.items():
                y = 1 - 2 * level / (len(levels) + 1)
                for i, node_id in enumerate(level_nodes):
                    x = 2 * (i + 1) / (len(level_nodes) + 1) - 1
                    positions[node_id] = (x, y)
                    
        else:  # force-directed (simplified)
            # Random initial positions with force-directed refinement
            np.random.seed(42)
            for node in nodes:
                positions[node['id']] = (
                    np.random.uniform(-0.8, 0.8),
                    np.random.uniform(-0.8, 0.8)
                )
            
            # Simple force-directed iterations
            for _ in range(50):
                positions = self._force_directed_step(positions, edges)
        
        return positions
    
    def _force_directed_step(
        self,
        positions: Dict[str, Tuple[float, float]],
        edges: List[Dict]
    ) -> Dict[str, Tuple[float, float]]:
        """Single step of force-directed layout"""
        new_positions = positions.copy()
        
        for node_id, (x, y) in positions.items():
            fx, fy = 0, 0
            
            # Repulsive forces
            for other_id, (ox, oy) in positions.items():
                if other_id != node_id:
                    dx = x - ox
                    dy = y - oy
                    dist = math.sqrt(dx**2 + dy**2) + 0.01
                    fx += 0.01 * dx / dist
                    fy += 0.01 * dy / dist
            
            # Attractive forces for connected nodes
            for edge in edges:
                if edge['source'] == node_id:
                    target_pos = positions.get(edge['target'])
                    if target_pos:
                        dx = target_pos[0] - x
                        dy = target_pos[1] - y
                        fx += 0.001 * dx
                        fy += 0.001 * dy
            
            new_positions[node_id] = (x + fx, y + fy)
        
        return new_positions
    
    def _calculate_hierarchy_levels(
        self,
        nodes: List[Dict],
        edges: List[Dict]
    ) -> Dict[int, List[str]]:
        """Calculate hierarchy levels for tree layout"""
        # Find root nodes (nodes with no incoming edges)
        incoming = {n['id']: [] for n in nodes}
        for edge in edges:
            incoming[edge['target']].append(edge['source'])
        
        roots = [n['id'] for n in nodes if not incoming[n['id']]]
        
        # BFS to assign levels
        levels = {}
        visited = set()
        queue = [(root, 0) for root in roots]
        
        while queue:
            node_id, level = queue.pop(0)
            if node_id in visited:
                continue
            visited.add(node_id)
            
            if level not in levels:
                levels[level] = []
            levels[level].append(node_id)
            
            # Find children
            for edge in edges:
                if edge['source'] == node_id:
                    queue.append((edge['target'], level + 1))
        
        return levels
    
    def _draw_node(self, ax, pos: Tuple[float, float], node: Dict):
        """Draw a single node"""
        x, y = pos
        
        # Determine color based on status
        status_colors = {
            'healthy': '#2ecc71',
            'warning': '#f39c12',
            'critical': '#e74c3c',
            'unknown': '#95a5a6'
        }
        color = status_colors.get(node.get('status', 'unknown'), '#3498db')
        
        # Draw node shape
        shape = node.get('shape', self.node_style.shape)
        size = node.get('size', self.node_style.size) / 100
        
        if shape == 'circle':
            circle = Circle((x, y), size, facecolor=color,
                          edgecolor=self.node_style.border_color,
                          linewidth=self.node_style.border_width)
            ax.add_patch(circle)
        elif shape == 'square':
            square = FancyBboxPatch((x - size, y - size), 2*size, 2*size,
                                   boxstyle="round,pad=0.02",
                                   facecolor=color,
                                   edgecolor=self.node_style.border_color,
                                   linewidth=self.node_style.border_width)
            ax.add_patch(square)
        
        # Add label
        label = node.get('label', node['id'])
        ax.text(x, y - size - 0.08, label, ha='center', va='top',
               fontsize=self.node_style.label_size,
               color=self.node_style.label_color,
               fontweight='bold')
    
    def _draw_edge(
        self,
        ax,
        source_pos: Tuple[float, float],
        target_pos: Tuple[float, float],
        edge: Dict
    ):
        """Draw a single edge"""
        sx, sy = source_pos
        tx, ty = target_pos
        
        # Determine edge style based on type
        edge_colors = {
            'normal': '#7f8c8d',
            'high-latency': '#f39c12',
            'failed': '#e74c3c',
            'secure': '#2ecc71'
        }
        color = edge_colors.get(edge.get('type', 'normal'), '#7f8c8d')
        
        # Draw arrow
        arrow = FancyArrowPatch((sx, sy), (tx, ty),
                               arrowstyle='->',
                               mutation_scale=self.edge_style.arrow_size,
                               color=color,
                               linewidth=self.edge_style.width)
        ax.add_patch(arrow)
        
        # Add edge label if present
        if edge.get('label'):
            mid_x, mid_y = (sx + tx) / 2, (sy + ty) / 2
            ax.text(mid_x, mid_y, edge['label'], ha='center', va='center',
                   fontsize=self.edge_style.label_size,
                   color=self.edge_style.label_color,
                   bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
    
    def _add_topology_legend(self, ax, nodes: List[Dict]):
        """Add legend to topology map"""
        status_colors = {
            'healthy': '#2ecc71',
            'warning': '#f39c12',
            'critical': '#e74c3c',
            'unknown': '#95a5a6'
        }
        
        legend_elements = [
            mpatches.Patch(facecolor=color, edgecolor='black', label=status.title())
            for status, color in status_colors.items()
        ]
        
        ax.legend(handles=legend_elements, loc='upper right',
                 framealpha=0.9, fontsize=9)


class DashboardImageGenerator:
    """Generate dashboard overview images"""
    
    def __init__(self, width: int = 1920, height: int = 1080):
        self.width = width
        self.height = height
    
    def generate_dashboard_overview(
        self,
        metrics: Dict[str, Any],
        widgets: List[Dict[str, Any]]
    ) -> bytes:
        """
        Generate dashboard overview image
        
        Args:
            metrics: Key metrics to display
            widgets: Widget configurations
            
        Returns:
            PNG image bytes
        """
        # Create image with PIL for better text rendering
        img = Image.new('RGB', (self.width, self.height), '#f5f6fa')
        draw = ImageDraw.Draw(img)
        
        # Draw header
        self._draw_header(draw, metrics.get('title', 'Dashboard'))
        
        # Draw metric cards
        y_offset = 100
        self._draw_metric_cards(draw, metrics.get('cards', []), y_offset)
        
        # Draw widgets
        y_offset = 250
        self._draw_widgets(draw, widgets, y_offset)
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, 'PNG', optimize=True)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    def _draw_header(self, draw: ImageDraw.Draw, title: str):
        """Draw dashboard header"""
        # Header background
        draw.rectangle([0, 0, self.width, 80], fill='#2c3e50')
        
        # Title
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 32)
        except:
            font = ImageFont.load_default()
        
        draw.text((30, 20), title, fill='white', font=font)
    
    def _draw_metric_cards(self, draw: ImageDraw.Draw, cards: List[Dict], y: int):
        """Draw metric cards"""
        card_width = (self.width - 100) // max(len(cards), 1)
        x = 30
        
        for card in cards:
            # Card background
            draw.rounded_rectangle(
                [x, y, x + card_width - 20, y + 120],
                radius=10,
                fill='white',
                outline='#e0e0e0',
                width=2
            )
            
            # Card title
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
                value_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
            except:
                title_font = value_font = ImageFont.load_default()
            
            draw.text((x + 15, y + 15), card.get('title', ''), fill='#7f8c8d', font=title_font)
            
            # Card value
            value = str(card.get('value', ''))
            value_color = card.get('color', '#2c3e50')
            draw.text((x + 15, y + 45), value, fill=value_color, font=value_font)
            
            x += card_width
    
    def _draw_widgets(self, draw: ImageDraw.Draw, widgets: List[Dict], y: int):
        """Draw dashboard widgets"""
        cols = 2
        widget_width = (self.width - 80) // cols
        widget_height = 350
        
        for i, widget in enumerate(widgets):
            col = i % cols
            row = i // cols
            
            x = 30 + col * widget_width
            wy = y + row * (widget_height + 20)
            
            # Widget background
            draw.rounded_rectangle(
                [x, wy, x + widget_width - 20, wy + widget_height],
                radius=10,
                fill='white',
                outline='#e0e0e0',
                width=2
            )
            
            # Widget title
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
            except:
                title_font = ImageFont.load_default()
            
            draw.text((x + 15, wy + 15), widget.get('title', ''), fill='#2c3e50', font=title_font)


# Example usage
if __name__ == "__main__":
    # Network topology example
    network_gen = NetworkGraphGenerator(width=1000, height=800)
    
    nodes = [
        {'id': 'core', 'label': 'Core Router', 'status': 'healthy', 'shape': 'square'},
        {'id': 'sw1', 'label': 'Switch 1', 'status': 'healthy'},
        {'id': 'sw2', 'label': 'Switch 2', 'status': 'warning'},
        {'id': 'srv1', 'label': 'Server 1', 'status': 'healthy'},
        {'id': 'srv2', 'label': 'Server 2', 'status': 'critical'},
        {'id': 'fw', 'label': 'Firewall', 'status': 'healthy', 'shape': 'square'}
    ]
    
    edges = [
        {'source': 'core', 'target': 'sw1', 'type': 'normal'},
        {'source': 'core', 'target': 'sw2', 'type': 'high-latency'},
        {'source': 'sw1', 'target': 'srv1', 'type': 'normal'},
        {'source': 'sw2', 'target': 'srv2', 'type': 'failed'},
        {'source': 'fw', 'target': 'core', 'type': 'secure'}
    ]
    
    topology_image = network_gen.generate_topology_map(nodes, edges, layout='force-directed')
    
    with open('/mnt/okcomputer/output/resilience_ai_analysis/code/image_generator/topology_example.png', 'wb') as f:
        f.write(topology_image)
    
    print("Topology image generated successfully!")
```


---

## 3. Image Optimization

### 3.1 Optimization Pipeline

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/optimizer/image_optimizer.py
"""
Image Optimization Pipeline for ResilienceAI
Provides compression, format conversion, and quality optimization
"""

import io
import logging
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import hashlib
import time

from PIL import Image, ImageFilter, ImageEnhance
import numpy as np

# Optional advanced optimizers
try:
    import tinify
    TINIFY_AVAILABLE = True
except ImportError:
    TINIFY_AVAILABLE = False

try:
    import pillow_avif
    AVIF_AVAILABLE = True
except ImportError:
    AVIF_AVAILABLE = False


logger = logging.getLogger(__name__)


class OptimizationLevel(Enum):
    """Optimization level presets"""
    LIGHT = "light"      # Fast, minimal compression
    BALANCED = "balanced"  # Good balance of speed and quality
    AGGRESSIVE = "aggressive"  # Maximum compression, slower
    LOSSLESS = "lossless"  # No quality loss


@dataclass
class OptimizationConfig:
    """Configuration for image optimization"""
    level: OptimizationLevel = OptimizationLevel.BALANCED
    target_size_kb: Optional[int] = None
    min_quality: int = 70
    max_quality: int = 95
    preserve_metadata: bool = False
    progressive: bool = True
    optimize: bool = True
    
    # Format-specific settings
    png_compression: int = 6  # 0-9
    jpeg_optimization: bool = True
    webp_method: int = 4  # 0-6


@dataclass
class OptimizationResult:
    """Result of image optimization"""
    original_size: int
    optimized_size: int
    compression_ratio: float
    quality_score: float
    format: str
    dimensions: Tuple[int, int]
    processing_time_ms: float
    success: bool
    error_message: Optional[str] = None


class ImageOptimizer:
    """
    Main image optimization class
    Provides multiple optimization strategies
    """
    
    # Quality presets by optimization level
    QUALITY_PRESETS = {
        OptimizationLevel.LIGHT: {'jpeg': 90, 'webp': 85},
        OptimizationLevel.BALANCED: {'jpeg': 80, 'webp': 75},
        OptimizationLevel.AGGRESSIVE: {'jpeg': 65, 'webp': 60},
        OptimizationLevel.LOSSLESS: {'jpeg': 100, 'webp': 100}
    }
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        self.config = config or OptimizationConfig()
        self._cache: Dict[str, bytes] = {}
        
    def optimize(
        self,
        image_bytes: bytes,
        target_format: Optional[str] = None,
        custom_config: Optional[OptimizationConfig] = None
    ) -> Tuple[bytes, OptimizationResult]:
        """
        Optimize an image
        
        Args:
            image_bytes: Raw image bytes
            target_format: Target format (png, jpeg, webp, etc.)
            custom_config: Optional custom optimization config
            
        Returns:
            Tuple of (optimized_bytes, result_info)
        """
        config = custom_config or self.config
        start_time = time.time()
        
        try:
            # Load image
            img = Image.open(io.BytesIO(image_bytes))
            original_size = len(image_bytes)
            original_format = img.format
            
            # Determine target format
            if target_format is None:
                target_format = original_format.lower() if original_format else 'png'
            
            # Apply optimization pipeline
            img = self._preprocess_image(img, config)
            
            # Encode with optimization
            optimized_bytes = self._encode_optimized(img, target_format, config)
            
            # Apply size-based quality adjustment if needed
            if config.target_size_kb:
                optimized_bytes = self._adjust_for_target_size(
                    img, target_format, config, config.target_size_kb
                )
            
            # Calculate results
            optimized_size = len(optimized_bytes)
            compression_ratio = (1 - optimized_size / original_size) * 100
            processing_time = (time.time() - start_time) * 1000
            
            result = OptimizationResult(
                original_size=original_size,
                optimized_size=optimized_size,
                compression_ratio=compression_ratio,
                quality_score=self._estimate_quality_score(
                    original_size, optimized_size, config
                ),
                format=target_format,
                dimensions=img.size,
                processing_time_ms=processing_time,
                success=True
            )
            
            logger.info(f"Optimized image: {original_size} -> {optimized_size} bytes "
                       f"({compression_ratio:.1f}% reduction)")
            
            return optimized_bytes, result
            
        except Exception as e:
            logger.error(f"Optimization failed: {str(e)}")
            result = OptimizationResult(
                original_size=len(image_bytes),
                optimized_size=len(image_bytes),
                compression_ratio=0,
                quality_score=0,
                format=target_format or 'unknown',
                dimensions=(0, 0),
                processing_time_ms=(time.time() - start_time) * 1000,
                success=False,
                error_message=str(e)
            )
            return image_bytes, result
    
    def _preprocess_image(self, img: Image.Image, config: OptimizationConfig) -> Image.Image:
        """Preprocess image before optimization"""
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            if config.level == OptimizationLevel.LOSSLESS:
                # Keep transparency for lossless
                if img.mode == 'P':
                    img = img.convert('RGBA')
            else:
                # Convert to RGB for better compression
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                else:
                    background.paste(img)
                img = background
        
        # Apply light denoising for aggressive optimization
        if config.level == OptimizationLevel.AGGRESSIVE:
            img = img.filter(ImageFilter.MedianFilter(size=3))
        
        return img
    
    def _encode_optimized(
        self,
        img: Image.Image,
        format: str,
        config: OptimizationConfig
    ) -> bytes:
        """Encode image with optimization settings"""
        buffer = io.BytesIO()
        
        quality_preset = self.QUALITY_PRESETS.get(config.level, {})
        
        if format.lower() in ('jpeg', 'jpg'):
            quality = quality_preset.get('jpeg', 80)
            img.save(
                buffer,
                format='JPEG',
                quality=quality,
                optimize=config.optimize,
                progressive=config.progressive
            )
            
        elif format.lower() == 'png':
            img.save(
                buffer,
                format='PNG',
                optimize=config.optimize,
                compress_level=config.png_compression
            )
            
        elif format.lower() == 'webp':
            quality = quality_preset.get('webp', 75)
            img.save(
                buffer,
                format='WEBP',
                quality=quality,
                method=config.webp_method,
                optimize=config.optimize
            )
            
        elif format.lower() == 'avif' and AVIF_AVAILABLE:
            quality = quality_preset.get('webp', 75)
            img.save(
                buffer,
                format='AVIF',
                quality=quality
            )
            
        else:
            # Fallback to PNG
            img.save(buffer, format='PNG')
        
        buffer.seek(0)
        return buffer.getvalue()
    
    def _adjust_for_target_size(
        self,
        img: Image.Image,
        format: str,
        config: OptimizationConfig,
        target_size_kb: int
    ) -> bytes:
        """Adjust quality to meet target size"""
        target_bytes = target_size_kb * 1024
        
        # Binary search for optimal quality
        low_quality = config.min_quality
        high_quality = config.max_quality
        best_result = None
        
        for _ in range(5):  # Max 5 iterations
            mid_quality = (low_quality + high_quality) // 2
            
            buffer = io.BytesIO()
            if format.lower() in ('jpeg', 'jpg'):
                img.save(buffer, format='JPEG', quality=mid_quality, optimize=True)
            elif format.lower() == 'webp':
                img.save(buffer, format='WEBP', quality=mid_quality)
            else:
                break
            
            size = buffer.tell()
            
            if size <= target_bytes:
                best_result = buffer.getvalue()
                low_quality = mid_quality + 1
            else:
                high_quality = mid_quality - 1
        
        return best_result or self._encode_optimized(img, format, config)
    
    def _estimate_quality_score(
        self,
        original_size: int,
        optimized_size: int,
        config: OptimizationConfig
    ) -> float:
        """Estimate visual quality score (0-100)"""
        compression_ratio = optimized_size / original_size
        
        # Base quality on optimization level
        base_quality = {
            OptimizationLevel.LIGHT: 95,
            OptimizationLevel.BALANCED: 85,
            OptimizationLevel.AGGRESSIVE: 70,
            OptimizationLevel.LOSSLESS: 100
        }.get(config.level, 85)
        
        # Adjust based on compression ratio
        if compression_ratio > 0.9:
            quality_penalty = 0
        elif compression_ratio > 0.7:
            quality_penalty = 5
        elif compression_ratio > 0.5:
            quality_penalty = 10
        else:
            quality_penalty = 15
        
        return max(0, base_quality - quality_penalty)
    
    def batch_optimize(
        self,
        images: List[bytes],
        target_format: Optional[str] = None,
        max_workers: int = 4
    ) -> List[Tuple[bytes, OptimizationResult]]:
        """
        Optimize multiple images in batch
        
        Args:
            images: List of image bytes
            target_format: Target format for all images
            max_workers: Maximum parallel workers
            
        Returns:
            List of (optimized_bytes, result) tuples
        """
        from concurrent.futures import ThreadPoolExecutor
        
        def optimize_single(image_bytes: bytes) -> Tuple[bytes, OptimizationResult]:
            return self.optimize(image_bytes, target_format)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(optimize_single, images))
        
        return results
    
    def get_optimization_report(
        self,
        results: List[OptimizationResult]
    ) -> Dict[str, Any]:
        """Generate optimization report from batch results"""
        successful = [r for r in results if r.success]
        failed = [r for r in results if not r.success]
        
        if not successful:
            return {
                'total_images': len(results),
                'successful': 0,
                'failed': len(failed),
                'total_original_size': 0,
                'total_optimized_size': 0,
                'average_compression': 0
            }
        
        total_original = sum(r.original_size for r in successful)
        total_optimized = sum(r.optimized_size for r in successful)
        
        return {
            'total_images': len(results),
            'successful': len(successful),
            'failed': len(failed),
            'total_original_size_kb': total_original / 1024,
            'total_optimized_size_kb': total_optimized / 1024,
            'space_saved_kb': (total_original - total_optimized) / 1024,
            'average_compression': sum(r.compression_ratio for r in successful) / len(successful),
            'average_processing_time_ms': sum(r.processing_time_ms for r in successful) / len(successful)
        }


class SmartImageOptimizer(ImageOptimizer):
    """
    Smart optimizer that automatically selects best format and settings
    based on image content and target use case
    """
    
    def __init__(self, config: Optional[OptimizationConfig] = None):
        super().__init__(config)
        
    def smart_optimize(
        self,
        image_bytes: bytes,
        use_case: str = 'general',
        target_size_kb: Optional[int] = None
    ) -> Tuple[bytes, str, OptimizationResult]:
        """
        Smart optimization with automatic format selection
        
        Args:
            image_bytes: Raw image bytes
            use_case: Use case (web, print, thumbnail, icon)
            target_size_kb: Optional target size
            
        Returns:
            Tuple of (optimized_bytes, selected_format, result)
        """
        # Analyze image
        img = Image.open(io.BytesIO(image_bytes))
        has_transparency = img.mode in ('RGBA', 'LA') or 'transparency' in img.info
        is_photo = self._is_photographic(img)
        
        # Select best format
        format = self._select_format(use_case, has_transparency, is_photo)
        
        # Adjust config for use case
        config = self._get_use_case_config(use_case, target_size_kb)
        
        # Optimize
        optimized_bytes, result = self.optimize(image_bytes, format, config)
        
        return optimized_bytes, format, result
    
    def _is_photographic(self, img: Image.Image) -> bool:
        """Detect if image is photographic or graphic"""
        # Convert to RGB for analysis
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Sample pixels for color analysis
        small = img.resize((100, 100))
        pixels = np.array(small)
        
        # Calculate color variance
        variance = np.var(pixels)
        
        # High variance suggests photograph
        return variance > 1000
    
    def _select_format(
        self,
        use_case: str,
        has_transparency: bool,
        is_photo: bool
    ) -> str:
        """Select optimal format based on characteristics"""
        format_selection = {
            'web': {
                'photo': 'webp',
                'graphic': 'png' if has_transparency else 'webp',
                'default': 'webp'
            },
            'print': {
                'photo': 'jpeg',
                'graphic': 'png',
                'default': 'jpeg'
            },
            'thumbnail': {
                'photo': 'jpeg',
                'graphic': 'png',
                'default': 'jpeg'
            },
            'icon': {
                'photo': 'png',
                'graphic': 'png',
                'default': 'png'
            }
        }
        
        use_case_formats = format_selection.get(use_case, format_selection['web'])
        
        if is_photo:
            return use_case_formats['photo']
        elif has_transparency:
            return use_case_formats['graphic']
        else:
            return use_case_formats['default']
    
    def _get_use_case_config(
        self,
        use_case: str,
        target_size_kb: Optional[int]
    ) -> OptimizationConfig:
        """Get optimization config for specific use case"""
        configs = {
            'web': OptimizationConfig(
                level=OptimizationLevel.BALANCED,
                target_size_kb=target_size_kb or 100
            ),
            'print': OptimizationConfig(
                level=OptimizationLevel.LOSSLESS,
                min_quality=95
            ),
            'thumbnail': OptimizationConfig(
                level=OptimizationLevel.AGGRESSIVE,
                target_size_kb=target_size_kb or 10
            ),
            'icon': OptimizationConfig(
                level=OptimizationLevel.LOSSLESS,
                preserve_metadata=True
            )
        }
        
        return configs.get(use_case, OptimizationConfig())


# Utility functions
def get_image_info(image_bytes: bytes) -> Dict[str, Any]:
    """Get information about an image"""
    img = Image.open(io.BytesIO(image_bytes))
    
    return {
        'format': img.format,
        'mode': img.mode,
        'width': img.width,
        'height': img.height,
        'size_bytes': len(image_bytes),
        'has_transparency': img.mode in ('RGBA', 'LA') or 'transparency' in img.info,
        'is_animated': getattr(img, 'is_animated', False),
        'dpi': img.info.get('dpi', (72, 72))
    }


def calculate_optimal_dimensions(
    original_width: int,
    original_height: int,
    max_width: Optional[int] = None,
    max_height: Optional[int] = None,
    target_pixels: Optional[int] = None
) -> Tuple[int, int]:
    """Calculate optimal dimensions while preserving aspect ratio"""
    width, height = original_width, original_height
    
    if max_width and width > max_width:
        height = int(height * max_width / width)
        width = max_width
    
    if max_height and height > max_height:
        width = int(width * max_height / height)
        height = max_height
    
    if target_pixels and width * height > target_pixels:
        ratio = (target_pixels / (width * height)) ** 0.5
        width = int(width * ratio)
        height = int(height * ratio)
    
    return width, height


# Example usage
if __name__ == "__main__":
    # Create optimizer
    optimizer = SmartImageOptimizer()
    
    # Example: Create a test image
    img = Image.new('RGB', (1920, 1080), color='#3498db')
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    image_bytes = buffer.getvalue()
    
    print(f"Original size: {len(image_bytes)} bytes")
    
    # Smart optimize for web
    optimized, format, result = optimizer.smart_optimize(
        image_bytes,
        use_case='web',
        target_size_kb=50
    )
    
    print(f"Optimized format: {format}")
    print(f"Optimized size: {result.optimized_size} bytes")
    print(f"Compression ratio: {result.compression_ratio:.1f}%")
    print(f"Quality score: {result.quality_score:.1f}")
    print(f"Processing time: {result.processing_time_ms:.2f}ms")
```

### 3.2 Format Conversion Engine

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/optimizer/format_converter.py
"""
Format Conversion Engine
Handles conversion between all supported image formats
"""

import io
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PIL import Image


class ImageFormat(Enum):
    """Supported image formats"""
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"
    GIF = "gif"
    BMP = "bmp"
    TIFF = "tiff"
    SVG = "svg"
    PDF = "pdf"
    ICO = "ico"
    AVIF = "avif"
    HEIC = "heic"


@dataclass
class ConversionOptions:
    """Options for format conversion"""
    quality: int = 85
    optimize: bool = True
    preserve_metadata: bool = True
    color_profile: Optional[str] = None
    dpi: Optional[Tuple[int, int]] = None


class FormatConverter:
    """
    Universal format converter
    """
    
    # Format capabilities
    FORMAT_CAPS = {
        ImageFormat.PNG: {
            'supports_transparency': True,
            'supports_animation': False,
            'lossless': True,
            'max_channels': 4
        },
        ImageFormat.JPEG: {
            'supports_transparency': False,
            'supports_animation': False,
            'lossless': False,
            'max_channels': 3
        },
        ImageFormat.WEBP: {
            'supports_transparency': True,
            'supports_animation': True,
            'lossless': True,
            'max_channels': 4
        },
        ImageFormat.GIF: {
            'supports_transparency': True,
            'supports_animation': True,
            'lossless': True,
            'max_channels': 1  # Palette-based
        },
        ImageFormat.AVIF: {
            'supports_transparency': True,
            'supports_animation': True,
            'lossless': True,
            'max_channels': 4
        }
    }
    
    def __init__(self):
        self._converters: Dict[Tuple[ImageFormat, ImageFormat], callable] = {}
        self._register_default_converters()
    
    def convert(
        self,
        image_bytes: bytes,
        source_format: ImageFormat,
        target_format: ImageFormat,
        options: Optional[ConversionOptions] = None
    ) -> bytes:
        """
        Convert image from one format to another
        
        Args:
            image_bytes: Source image bytes
            source_format: Source format
            target_format: Target format
            options: Conversion options
            
        Returns:
            Converted image bytes
        """
        options = options or ConversionOptions()
        
        # Check for direct converter
        converter_key = (source_format, target_format)
        if converter_key in self._converters:
            return self._converters[converter_key](image_bytes, options)
        
        # Use PIL as universal converter
        return self._pil_convert(image_bytes, target_format, options)
    
    def _pil_convert(
        self,
        image_bytes: bytes,
        target_format: ImageFormat,
        options: ConversionOptions
    ) -> bytes:
        """Convert using PIL"""
        img = Image.open(io.BytesIO(image_bytes))
        
        # Handle transparency for formats that don't support it
        target_caps = self.FORMAT_CAPS.get(target_format, {})
        if not target_caps.get('supports_transparency', False) and img.mode in ('RGBA', 'LA', 'P'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            if img.mode == 'RGBA':
                background.paste(img, mask=img.split()[3])
            elif img.mode == 'LA':
                background.paste(img, mask=img.split()[1])
            elif img.mode == 'P':
                img = img.convert('RGBA')
                background.paste(img, mask=img.split()[3])
            img = background
        
        # Convert palette images for non-palette formats
        if img.mode == 'P' and target_format not in (ImageFormat.GIF, ImageFormat.PNG):
            img = img.convert('RGB')
        
        buffer = io.BytesIO()
        
        # Save with format-specific options
        save_kwargs = {}
        
        if target_format == ImageFormat.PNG:
            save_kwargs = {
                'optimize': options.optimize,
                'compress_level': 6
            }
        elif target_format == ImageFormat.JPEG:
            save_kwargs = {
                'quality': options.quality,
                'optimize': options.optimize,
                'progressive': True
            }
        elif target_format == ImageFormat.WEBP:
            save_kwargs = {
                'quality': options.quality,
                'method': 4,
                'optimize': options.optimize
            }
        elif target_format == ImageFormat.GIF:
            save_kwargs = {
                'optimize': options.optimize
            }
        
        if options.dpi:
            save_kwargs['dpi'] = options.dpi
        
        img.save(buffer, format=target_format.value.upper(), **save_kwargs)
        buffer.seek(0)
        
        return buffer.getvalue()
    
    def _register_default_converters(self):
        """Register format-specific converters"""
        # SVG to raster conversion
        self._converters[(ImageFormat.SVG, ImageFormat.PNG)] = self._svg_to_raster
        self._converters[(ImageFormat.SVG, ImageFormat.JPEG)] = self._svg_to_raster
        self._converters[(ImageFormat.SVG, ImageFormat.WEBP)] = self._svg_to_raster
        
        # PDF conversion
        self._converters[(ImageFormat.PDF, ImageFormat.PNG)] = self._pdf_to_raster
    
    def _svg_to_raster(
        self,
        svg_bytes: bytes,
        options: ConversionOptions
    ) -> bytes:
        """Convert SVG to raster format using CairoSVG"""
        try:
            import cairosvg
            
            # Convert SVG to PNG first
            png_bytes = cairosvg.svg2png(
                bytestring=svg_bytes,
                dpi=options.dpi[0] if options.dpi else 96
            )
            
            # Then convert PNG to target format if needed
            return png_bytes
            
        except ImportError:
            raise ImportError("CairoSVG is required for SVG conversion")
    
    def _pdf_to_raster(
        self,
        pdf_bytes: bytes,
        options: ConversionOptions
    ) -> bytes:
        """Convert PDF to raster format"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(stream=pdf_bytes, filetype="pdf")
            page = doc[0]
            
            # Render at specified DPI
            mat = fitz.Matrix(
                options.dpi[0] / 72 if options.dpi else 2,
                options.dpi[1] / 72 if options.dpi else 2
            )
            pix = page.get_pixmap(matrix=mat)
            
            return pix.tobytes("png")
            
        except ImportError:
            raise ImportError("PyMuPDF is required for PDF conversion")
    
    def get_conversion_info(
        self,
        source_format: ImageFormat,
        target_format: ImageFormat
    ) -> Dict[str, Any]:
        """Get information about a format conversion"""
        source_caps = self.FORMAT_CAPS.get(source_format, {})
        target_caps = self.FORMAT_CAPS.get(target_format, {})
        
        warnings = []
        
        # Check transparency
        if source_caps.get('supports_transparency') and not target_caps.get('supports_transparency'):
            warnings.append("Transparency will be lost")
        
        # Check animation
        if source_caps.get('supports_animation') and not target_caps.get('supports_animation'):
            warnings.append("Animation will be lost (only first frame kept)")
        
        # Check quality
        if source_caps.get('lossless') and not target_caps.get('lossless'):
            warnings.append("Conversion will use lossy compression")
        
        return {
            'source_format': source_format.value,
            'target_format': target_format.value,
            'warnings': warnings,
            'supports_transparency': target_caps.get('supports_transparency', False),
            'supports_animation': target_caps.get('supports_animation', False),
            'is_lossless': target_caps.get('lossless', False)
        }


# Example usage
if __name__ == "__main__":
    converter = FormatConverter()
    
    # Create test image
    img = Image.new('RGBA', (500, 500), (100, 150, 200, 128))
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    png_bytes = buffer.getvalue()
    
    # Convert to JPEG (transparency will be lost)
    info = converter.get_conversion_info(ImageFormat.PNG, ImageFormat.JPEG)
    print("Conversion info:", info)
    
    jpeg_bytes = converter.convert(png_bytes, ImageFormat.PNG, ImageFormat.JPEG)
    print(f"JPEG size: {len(jpeg_bytes)} bytes")
```


---

## 4. Thumbnail Generation

### 4.1 Thumbnail Engine

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/thumbnail/thumbnail_generator.py
"""
Thumbnail Generation Engine for ResilienceAI
Creates scaled-down image versions with various strategies
"""

import io
import math
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import hashlib

from PIL import Image, ImageFilter, ImageEnhance, ImageOps
import numpy as np


class ThumbnailStrategy(Enum):
    """Thumbnail generation strategies"""
    FIT = auto()           # Fit within bounds, maintain aspect ratio
    FILL = auto()          # Fill bounds, crop excess
    STRETCH = auto()       # Stretch to exact dimensions
    PAD = auto()           # Pad with background to fit
    SMART_CROP = auto()    # Intelligent cropping
    FACE_FOCUS = auto()    # Focus on detected faces
    ENTROPY = auto()       # Crop to area of highest entropy


class ThumbnailSize(Enum):
    """Predefined thumbnail sizes"""
    TINY = (50, 50)
    SMALL = (100, 100)
    MEDIUM = (200, 200)
    LARGE = (400, 400)
    XL = (800, 800)
    
    # Aspect ratio presets
    ICON = (64, 64)
    AVATAR = (128, 128)
    PREVIEW = (300, 200)
    CARD = (400, 300)
    HERO = (1200, 600)
    BANNER = (1920, 400)


@dataclass
class ThumbnailConfig:
    """Configuration for thumbnail generation"""
    width: int = 200
    height: int = 200
    strategy: ThumbnailStrategy = ThumbnailStrategy.FIT
    quality: int = 85
    format: str = "webp"
    sharpen: bool = True
    background_color: Tuple[int, int, int] = (255, 255, 255)
    upscale: bool = False
    keep_aspect_ratio: bool = True
    
    # Smart crop options
    focal_point: Optional[Tuple[float, float]] = None  # (x, y) in 0-1 range
    crop_gravity: str = "center"  # center, top, bottom, left, right
    
    # Post-processing
    enhance_contrast: bool = False
    auto_level: bool = False


@dataclass
class ThumbnailResult:
    """Result of thumbnail generation"""
    image_bytes: bytes
    width: int
    height: int
    format: str
    original_size: int
    thumbnail_size: int
    processing_time_ms: float
    cache_key: str


class ThumbnailGenerator:
    """
    Main thumbnail generation class
    """
    
    def __init__(self, cache_dir: Optional[Path] = None):
        self.cache_dir = cache_dir or Path('/tmp/thumbnails')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    def generate(
        self,
        image_bytes: bytes,
        config: Optional[ThumbnailConfig] = None
    ) -> ThumbnailResult:
        """
        Generate thumbnail from image
        
        Args:
            image_bytes: Source image bytes
            config: Thumbnail configuration
            
        Returns:
            Thumbnail result
        """
        import time
        start_time = time.time()
        
        config = config or ThumbnailConfig()
        original_size = len(image_bytes)
        
        # Generate cache key
        cache_key = self._generate_cache_key(image_bytes, config)
        
        # Check cache
        cached = self._get_from_cache(cache_key)
        if cached:
            img = Image.open(io.BytesIO(cached))
            return ThumbnailResult(
                image_bytes=cached,
                width=img.width,
                height=img.height,
                format=config.format,
                original_size=original_size,
                thumbnail_size=len(cached),
                processing_time_ms=(time.time() - start_time) * 1000,
                cache_key=cache_key
            )
        
        # Load image
        img = Image.open(io.BytesIO(image_bytes))
        
        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P', 'LA'):
            if config.strategy in (ThumbnailStrategy.PAD, ThumbnailStrategy.FIT):
                # Keep transparency
                if img.mode == 'P':
                    img = img.convert('RGBA')
            else:
                # Flatten transparency
                background = Image.new('RGB', img.size, config.background_color)
                if img.mode == 'RGBA':
                    background.paste(img, mask=img.split()[3])
                elif img.mode == 'LA':
                    background.paste(img, mask=img.split()[1])
                else:
                    background.paste(img)
                img = background
        
        # Apply strategy
        img = self._apply_strategy(img, config)
        
        # Post-process
        img = self._post_process(img, config)
        
        # Save
        output = io.BytesIO()
        save_kwargs = {'quality': config.quality, 'optimize': True}
        
        if config.format == 'webp':
            save_kwargs['method'] = 4
        
        img.save(output, format=config.format.upper(), **save_kwargs)
        thumbnail_bytes = output.getvalue()
        
        # Cache result
        self._save_to_cache(cache_key, thumbnail_bytes)
        
        processing_time = (time.time() - start_time) * 1000
        
        return ThumbnailResult(
            image_bytes=thumbnail_bytes,
            width=img.width,
            height=img.height,
            format=config.format,
            original_size=original_size,
            thumbnail_size=len(thumbnail_bytes),
            processing_time_ms=processing_time,
            cache_key=cache_key
        )
    
    def _apply_strategy(self, img: Image.Image, config: ThumbnailConfig) -> Image.Image:
        """Apply the selected thumbnail strategy"""
        strategy_map = {
            ThumbnailStrategy.FIT: self._strategy_fit,
            ThumbnailStrategy.FILL: self._strategy_fill,
            ThumbnailStrategy.STRETCH: self._strategy_stretch,
            ThumbnailStrategy.PAD: self._strategy_pad,
            ThumbnailStrategy.SMART_CROP: self._strategy_smart_crop,
            ThumbnailStrategy.ENTROPY: self._strategy_entropy_crop
        }
        
        strategy_fn = strategy_map.get(config.strategy, self._strategy_fit)
        return strategy_fn(img, config)
    
    def _strategy_fit(self, img: Image.Image, config: ThumbnailConfig) -> Image.Image:
        """Fit image within bounds, maintaining aspect ratio"""
        img.thumbnail((config.width, config.height), Image.Resampling.LANCZOS)
        return img
    
    def _strategy_fill(self, img: Image.Image, config: ThumbnailConfig) -> Image.Image:
        """Fill the target dimensions, cropping excess"""
        orig_width, orig_height = img.size
        target_ratio = config.width / config.height
        orig_ratio = orig_width / orig_height
        
        if orig_ratio > target_ratio:
            # Image is wider, crop width
            new_width = int(orig_height * target_ratio)
            left = (orig_width - new_width) // 2
            img = img.crop((left, 0, left + new_width, orig_height))
        else:
            # Image is taller, crop height
            new_height = int(orig_width / target_ratio)
            top = (orig_height - new_height) // 2
            img = img.crop((0, top, orig_width, top + new_height))
        
        img = img.resize((config.width, config.height), Image.Resampling.LANCZOS)
        return img
    
    def _strategy_stretch(self, img: Image.Image, config: ThumbnailConfig) -> Image.Image:
        """Stretch image to exact dimensions"""
        return img.resize((config.width, config.height), Image.Resampling.LANCZOS)
    
    def _strategy_pad(self, img: Image.Image, config: ThumbnailConfig) -> Image.Image:
        """Pad image with background to fit dimensions"""
        img.thumbnail((config.width, config.height), Image.Resampling.LANCZOS)
        
        # Create new image with background
        new_img = Image.new('RGBA', (config.width, config.height), 
                           (*config.background_color, 255))
        
        # Paste original centered
        x = (config.width - img.width) // 2
        y = (config.height - img.height) // 2
        
        if img.mode == 'RGBA':
            new_img.paste(img, (x, y), img)
        else:
            new_img.paste(img, (x, y))
        
        return new_img.convert('RGB')
    
    def _strategy_smart_crop(self, img: Image.Image, config: ThumbnailConfig) -> Image.Image:
        """Intelligent cropping based on focal point or content"""
        orig_width, orig_height = img.size
        target_ratio = config.width / config.height
        orig_ratio = orig_width / orig_height
        
        # Use focal point if provided
        if config.focal_point:
            focal_x = int(config.focal_point[0] * orig_width)
            focal_y = int(config.focal_point[1] * orig_height)
        else:
            # Default to center
            focal_x = orig_width // 2
            focal_y = orig_height // 2
        
        if orig_ratio > target_ratio:
            # Need to crop width
            new_width = int(orig_height * target_ratio)
            left = max(0, min(focal_x - new_width // 2, orig_width - new_width))
            img = img.crop((left, 0, left + new_width, orig_height))
        else:
            # Need to crop height
            new_height = int(orig_width / target_ratio)
            top = max(0, min(focal_y - new_height // 2, orig_height - new_height))
            img = img.crop((0, top, orig_width, top + new_height))
        
        img = img.resize((config.width, config.height), Image.Resampling.LANCZOS)
        return img
    
    def _strategy_entropy_crop(self, img: Image.Image, config: ThumbnailConfig) -> Image.Image:
        """Crop to area of highest entropy (most detail)"""
        # Convert to grayscale for analysis
        gray = img.convert('L')
        
        orig_width, orig_height = img.size
        target_ratio = config.width / config.height
        
        # Calculate target crop size
        if orig_width / orig_height > target_ratio:
            crop_width = int(orig_height * target_ratio)
            crop_height = orig_height
        else:
            crop_width = orig_width
            crop_height = int(orig_width / target_ratio)
        
        # Find region with highest entropy
        best_entropy = 0
        best_x, best_y = 0, 0
        
        # Sample at different positions
        steps = 10
        for i in range(steps):
            for j in range(steps):
                x = int((orig_width - crop_width) * i / (steps - 1))
                y = int((orig_height - crop_height) * j / (steps - 1))
                
                region = gray.crop((x, y, x + crop_width, y + crop_height))
                entropy = self._calculate_entropy(region)
                
                if entropy > best_entropy:
                    best_entropy = entropy
                    best_x, best_y = x, y
        
        img = img.crop((best_x, best_y, best_x + crop_width, best_y + crop_height))
        img = img.resize((config.width, config.height), Image.Resampling.LANCZOS)
        return img
    
    def _calculate_entropy(self, img: Image.Image) -> float:
        """Calculate image entropy"""
        histogram = img.histogram()
        total = sum(histogram)
        
        if total == 0:
            return 0
        
        entropy = 0
        for count in histogram:
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        
        return entropy
    
    def _post_process(self, img: Image.Image, config: ThumbnailConfig) -> Image.Image:
        """Apply post-processing effects"""
        # Sharpen
        if config.sharpen:
            img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
        
        # Auto level
        if config.auto_level:
            img = ImageOps.autocontrast(img, cutoff=1)
        
        # Enhance contrast
        if config.enhance_contrast:
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)
        
        return img
    
    def _generate_cache_key(self, image_bytes: bytes, config: ThumbnailConfig) -> str:
        """Generate cache key for thumbnail"""
        key_data = (
            hashlib.md5(image_bytes).hexdigest() +
            f"{config.width}x{config.height}" +
            f"{config.strategy.name}" +
            f"{config.quality}" +
            f"{config.format}"
        )
        return hashlib.sha256(key_data.encode()).hexdigest()[:32]
    
    def _get_from_cache(self, cache_key: str) -> Optional[bytes]:
        """Get thumbnail from cache"""
        cache_path = self.cache_dir / f"{cache_key}.{self.config.format if hasattr(self, 'config') else 'webp'}"
        if cache_path.exists():
            return cache_path.read_bytes()
        return None
    
    def _save_to_cache(self, cache_key: str, image_bytes: bytes):
        """Save thumbnail to cache"""
        cache_path = self.cache_dir / f"{cache_key}.webp"
        cache_path.write_bytes(image_bytes)
    
    def generate_set(
        self,
        image_bytes: bytes,
        sizes: List[Tuple[int, int]],
        base_config: Optional[ThumbnailConfig] = None
    ) -> Dict[str, ThumbnailResult]:
        """
        Generate multiple thumbnails at different sizes
        
        Args:
            image_bytes: Source image
            sizes: List of (width, height) tuples
            base_config: Base configuration
            
        Returns:
            Dictionary of size name -> thumbnail result
        """
        results = {}
        base_config = base_config or ThumbnailConfig()
        
        for width, height in sizes:
            config = ThumbnailConfig(
                width=width,
                height=height,
                strategy=base_config.strategy,
                quality=base_config.quality,
                format=base_config.format
            )
            
            size_name = f"{width}x{height}"
            results[size_name] = self.generate(image_bytes, config)
        
        return results


class ResponsiveImageSet:
    """
    Generate responsive image sets for web use
    Creates multiple sizes for srcset
    """
    
    # Standard responsive breakpoints
    BREAKPOINTS = [320, 640, 768, 1024, 1440, 1920]
    
    def __init__(self, generator: ThumbnailGenerator):
        self.generator = generator
    
    def generate_srcset(
        self,
        image_bytes: bytes,
        aspect_ratio: Optional[float] = None,
        max_width: int = 1920
    ) -> Dict[int, ThumbnailResult]:
        """
        Generate responsive image set
        
        Args:
            image_bytes: Source image
            aspect_ratio: Optional aspect ratio to maintain
            max_width: Maximum width to generate
            
        Returns:
            Dictionary of width -> thumbnail result
        """
        img = Image.open(io.BytesIO(image_bytes))
        orig_width, orig_height = img.size
        
        if aspect_ratio is None:
            aspect_ratio = orig_height / orig_width
        
        results = {}
        
        for breakpoint in self.BREAKPOINTS:
            if breakpoint > max_width:
                continue
            
            width = min(breakpoint, orig_width)
            height = int(width * aspect_ratio)
            
            config = ThumbnailConfig(
                width=width,
                height=height,
                strategy=ThumbnailStrategy.FIT,
                format='webp',
                quality=85
            )
            
            results[width] = self.generator.generate(image_bytes, config)
        
        return results
    
    def generate_srcset_html(
        self,
        srcset: Dict[int, ThumbnailResult],
        alt: str = "",
        sizes: str = "100vw"
    ) -> str:
        """Generate HTML img tag with srcset"""
        # Sort by width
        sorted_items = sorted(srcset.items(), key=lambda x: x[0])
        
        # Build srcset string
        srcset_parts = []
        for width, result in sorted_items:
            # In real implementation, would use actual URLs
            srcset_parts.append(f"/images/{result.cache_key}.webp {width}w")
        
        srcset_str = ", ".join(srcset_parts)
        
        # Use smallest as fallback
        fallback = sorted_items[0][1]
        
        return f'''<img
    src="/images/{fallback.cache_key}.webp"
    srcset="{srcset_str}"
    sizes="{sizes}"
    alt="{alt}"
    width="{fallback.width}"
    height="{fallback.height}"
    loading="lazy"
/>'''


# Example usage
if __name__ == "__main__":
    # Create generator
    generator = ThumbnailGenerator()
    
    # Create test image
    img = Image.new('RGB', (1920, 1080), color='#3498db')
    # Add some detail
    draw = ImageDraw.Draw(img)
    for i in range(0, 1920, 100):
        draw.line([(i, 0), (i, 1080)], fill='#2980b9', width=2)
    
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    image_bytes = buffer.getvalue()
    
    # Generate thumbnails with different strategies
    strategies = [
        ThumbnailStrategy.FIT,
        ThumbnailStrategy.FILL,
        ThumbnailStrategy.PAD,
        ThumbnailStrategy.ENTROPY
    ]
    
    for strategy in strategies:
        config = ThumbnailConfig(
            width=300,
            height=200,
            strategy=strategy,
            format='webp'
        )
        
        result = generator.generate(image_bytes, config)
        print(f"{strategy.name}: {result.thumbnail_size} bytes "
              f"({result.processing_time_ms:.2f}ms)")
    
    # Generate responsive set
    responsive = ResponsiveImageSet(generator)
    srcset = responsive.generate_srcset(image_bytes)
    
    print("\nResponsive srcset generated:")
    for width, result in sorted(srcset.items()):
        print(f"  {width}px: {result.thumbnail_size} bytes")
```


---

## 5. Format Support

### 5.1 Format Support Matrix

| Format | Read | Write | Transparency | Animation | Best For |
|--------|------|-------|--------------|-----------|----------|
| PNG | ✓ | ✓ | ✓ | ✗ | Screenshots, graphics |
| JPEG | ✓ | ✓ | ✗ | ✗ | Photographs |
| WebP | ✓ | ✓ | ✓ | ✓ | Web optimization |
| SVG | ✓ | ✓ | ✓ | ✓ | Vector graphics |
| GIF | ✓ | ✓ | ✓ | ✓ | Simple animations |
| AVIF | ✓ | ✓ | ✓ | ✓ | Next-gen web |
| PDF | ✓ | ✗ | ✓ | ✗ | Documents |
| TIFF | ✓ | ✓ | ✓ | ✗ | Print, archival |

---

## 6. Caching Strategy

### 6.1 Multi-Layer Cache

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/cache/image_cache.py
"""
Multi-Layer Image Caching System for ResilienceAI
Provides L1 (memory), L2 (Redis), and L3 (disk) caching
"""

import io
import hashlib
import pickle
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import json
import threading
from functools import lru_cache

# Optional Redis support
try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CacheLevel(Enum):
    """Cache levels"""
    L1_MEMORY = "l1_memory"      # In-process memory
    L2_REDIS = "l2_redis"        # Redis cache
    L3_DISK = "l3_disk"          # Local filesystem


@dataclass
class CacheEntry:
    """Cache entry metadata"""
    key: str
    data: bytes
    created_at: float
    expires_at: float
    content_type: str
    size_bytes: int
    access_count: int = 0
    last_accessed: float = 0
    tags: List[str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.last_accessed == 0:
            self.last_accessed = self.created_at
    
    def is_expired(self) -> bool:
        return time.time() > self.expires_at
    
    def touch(self):
        self.access_count += 1
        self.last_accessed = time.time()


@dataclass
class CacheStats:
    """Cache statistics"""
    level: CacheLevel
    hits: int
    misses: int
    size_bytes: int
    entries_count: int
    hit_rate: float
    evictions: int = 0


class CacheConfig:
    """Configuration for cache layers"""
    
    def __init__(
        self,
        l1_max_size_mb: int = 100,
        l1_ttl_seconds: int = 300,
        l2_enabled: bool = False,
        l2_host: str = 'localhost',
        l2_port: int = 6379,
        l2_db: int = 0,
        l2_ttl_seconds: int = 3600,
        l3_path: str = '/tmp/image_cache',
        l3_max_size_mb: int = 1000,
        l3_ttl_seconds: int = 86400
    ):
        self.l1_max_size_mb = l1_max_size_mb
        self.l1_ttl_seconds = l1_ttl_seconds
        self.l2_enabled = l2_enabled
        self.l2_host = l2_host
        self.l2_port = l2_port
        self.l2_db = l2_db
        self.l2_ttl_seconds = l2_ttl_seconds
        self.l3_path = Path(l3_path)
        self.l3_max_size_mb = l3_max_size_mb
        self.l3_ttl_seconds = l3_ttl_seconds


class L1MemoryCache:
    """L1: In-process memory cache with LRU eviction"""
    
    def __init__(self, max_size_mb: int = 100, ttl_seconds: int = 300):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self._current_size = 0
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def get(self, key: str) -> Optional[bytes]:
        """Get item from cache"""
        with self._lock:
            entry = self._cache.get(key)
            
            if entry is None:
                self._misses += 1
                return None
            
            if entry.is_expired():
                self._evict(key)
                self._misses += 1
                return None
            
            entry.touch()
            self._hits += 1
            return entry.data
    
    def set(
        self,
        key: str,
        data: bytes,
        content_type: str = 'image/webp',
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Set item in cache"""
        with self._lock:
            # Check if we need to make room
            data_size = len(data)
            
            if data_size > self.max_size_bytes:
                return False  # Item too large
            
            while self._current_size + data_size > self.max_size_bytes:
                self._evict_lru()
            
            # Remove old entry if exists
            if key in self._cache:
                self._current_size -= self._cache[key].size_bytes
            
            # Create new entry
            now = time.time()
            entry = CacheEntry(
                key=key,
                data=data,
                created_at=now,
                expires_at=now + (ttl or self.ttl_seconds),
                content_type=content_type,
                size_bytes=data_size,
                tags=tags or []
            )
            
            self._cache[key] = entry
            self._current_size += data_size
            
            return True
    
    def delete(self, key: str) -> bool:
        """Delete item from cache"""
        with self._lock:
            if key in self._cache:
                self._current_size -= self._cache[key].size_bytes
                del self._cache[key]
                return True
            return False
    
    def clear(self):
        """Clear all items"""
        with self._lock:
            self._cache.clear()
            self._current_size = 0
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        with self._lock:
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0
            
            return CacheStats(
                level=CacheLevel.L1_MEMORY,
                hits=self._hits,
                misses=self._misses,
                size_bytes=self._current_size,
                entries_count=len(self._cache),
                hit_rate=hit_rate,
                evictions=self._evictions
            )
    
    def _evict(self, key: str):
        """Evict specific item"""
        if key in self._cache:
            self._current_size -= self._cache[key].size_bytes
            del self._cache[key]
            self._evictions += 1
    
    def _evict_lru(self):
        """Evict least recently used item"""
        if not self._cache:
            return
        
        lru_key = min(self._cache.keys(), key=lambda k: self._cache[k].last_accessed)
        self._evict(lru_key)
    
    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all items with given tag"""
        with self._lock:
            keys_to_delete = [
                key for key, entry in self._cache.items()
                if tag in entry.tags
            ]
            for key in keys_to_delete:
                self._evict(key)
            return len(keys_to_delete)


class L2RedisCache:
    """L2: Redis distributed cache"""
    
    def __init__(
        self,
        host: str = 'localhost',
        port: int = 6379,
        db: int = 0,
        ttl_seconds: int = 3600
    ):
        if not REDIS_AVAILABLE:
            raise ImportError("Redis package required for L2 cache")
        
        self.client = redis.Redis(host=host, port=port, db=db, decode_responses=False)
        self.ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[bytes]:
        """Get item from Redis"""
        try:
            data = self.client.get(f"image:{key}")
            if data:
                self._hits += 1
                return data
            self._misses += 1
            return None
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            self._misses += 1
            return None
    
    def set(
        self,
        key: str,
        data: bytes,
        content_type: str = 'image/webp',
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Set item in Redis"""
        try:
            pipe = self.client.pipeline()
            
            # Store image data
            pipe.setex(
                f"image:{key}",
                ttl or self.ttl_seconds,
                data
            )
            
            # Store metadata
            metadata = {
                'content_type': content_type,
                'size': len(data),
                'created_at': time.time(),
                'tags': json.dumps(tags or [])
            }
            pipe.hset(f"meta:{key}", mapping=metadata)
            pipe.expire(f"meta:{key}", ttl or self.ttl_seconds)
            
            # Add to tag indexes
            for tag in tags or []:
                pipe.sadd(f"tag:{tag}", key)
            
            pipe.execute()
            return True
            
        except redis.RedisError as e:
            print(f"Redis error: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete item from Redis"""
        try:
            # Get metadata for tag cleanup
            meta = self.client.hgetall(f"meta:{key}")
            
            pipe = self.client.pipeline()
            pipe.delete(f"image:{key}")
            pipe.delete(f"meta:{key}")
            
            # Remove from tag indexes
            if meta:
                tags = json.loads(meta.get(b'tags', b'[]'))
                for tag in tags:
                    pipe.srem(f"tag:{tag}", key)
            
            pipe.execute()
            return True
            
        except redis.RedisError:
            return False
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        try:
            info = self.client.info('stats')
            
            return CacheStats(
                level=CacheLevel.L2_REDIS,
                hits=info.get('keyspace_hits', 0),
                misses=info.get('keyspace_misses', 0),
                size_bytes=0,  # Would need to calculate
                entries_count=self.client.dbsize(),
                hit_rate=0
            )
        except redis.RedisError:
            return CacheStats(
                level=CacheLevel.L2_REDIS,
                hits=0,
                misses=0,
                size_bytes=0,
                entries_count=0,
                hit_rate=0
            )
    
    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all items with given tag"""
        try:
            keys = self.client.smembers(f"tag:{tag}")
            for key in keys:
                self.delete(key.decode())
            return len(keys)
        except redis.RedisError:
            return 0


class L3DiskCache:
    """L3: Filesystem cache"""
    
    def __init__(self, cache_path: Path, max_size_mb: int = 1000, ttl_seconds: int = 86400):
        self.cache_path = Path(cache_path)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_seconds
        self._hits = 0
        self._misses = 0
        self._lock = threading.RLock()
        
        # Create subdirectories
        for i in range(256):
            (self.cache_path / f"{i:02x}").mkdir(exist_ok=True)
    
    def _get_path(self, key: str) -> Path:
        """Get filesystem path for key"""
        prefix = hashlib.md5(key.encode()).hexdigest()[:2]
        return self.cache_path / prefix / key
    
    def get(self, key: str) -> Optional[bytes]:
        """Get item from disk"""
        path = self._get_path(key)
        
        with self._lock:
            if not path.exists():
                self._misses += 1
                return None
            
            # Check if expired
            stat = path.stat()
            if time.time() - stat.st_mtime > self.ttl_seconds:
                path.unlink(missing_ok=True)
                self._misses += 1
                return None
            
            self._hits += 1
            return path.read_bytes()
    
    def set(
        self,
        key: str,
        data: bytes,
        content_type: str = 'image/webp',
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """Set item on disk"""
        path = self._get_path(key)
        meta_path = path.with_suffix('.json')
        
        with self._lock:
            try:
                # Cleanup if needed
                self._cleanup_if_needed(len(data))
                
                # Write data
                path.write_bytes(data)
                
                # Write metadata
                metadata = {
                    'content_type': content_type,
                    'size': len(data),
                    'created_at': time.time(),
                    'expires_at': time.time() + (ttl or self.ttl_seconds),
                    'tags': tags or []
                }
                meta_path.write_text(json.dumps(metadata))
                
                return True
                
            except IOError:
                return False
    
    def delete(self, key: str) -> bool:
        """Delete item from disk"""
        path = self._get_path(key)
        meta_path = path.with_suffix('.json')
        
        with self._lock:
            try:
                path.unlink(missing_ok=True)
                meta_path.unlink(missing_ok=True)
                return True
            except IOError:
                return False
    
    def get_stats(self) -> CacheStats:
        """Get cache statistics"""
        with self._lock:
            total_size = sum(
                f.stat().st_size
                for f in self.cache_path.rglob('*')
                if f.is_file() and f.suffix != '.json'
            )
            
            entries = len([
                f for f in self.cache_path.rglob('*')
                if f.is_file() and f.suffix != '.json'
            ])
            
            total = self._hits + self._misses
            hit_rate = self._hits / total if total > 0 else 0
            
            return CacheStats(
                level=CacheLevel.L3_DISK,
                hits=self._hits,
                misses=self._misses,
                size_bytes=total_size,
                entries_count=entries,
                hit_rate=hit_rate
            )
    
    def _cleanup_if_needed(self, needed_bytes: int):
        """Clean up old entries if needed"""
        current_size = sum(
            f.stat().st_size
            for f in self.cache_path.rglob('*')
            if f.is_file()
        )
        
        if current_size + needed_bytes <= self.max_size_bytes:
            return
        
        # Get all entries sorted by access time
        entries = []
        for f in self.cache_path.rglob('*'):
            if f.is_file() and f.suffix != '.json':
                entries.append((f, f.stat().st_atime))
        
        entries.sort(key=lambda x: x[1])
        
        # Remove oldest entries
        for path, _ in entries:
            if current_size + needed_bytes <= self.max_size_bytes:
                break
            
            size = path.stat().st_size
            path.unlink(missing_ok=True)
            meta_path = path.with_suffix('.json')
            meta_path.unlink(missing_ok=True)
            current_size -= size


class MultiLayerCache:
    """
    Multi-layer cache combining L1, L2, and L3
    Implements cache-aside pattern with write-through
    """
    
    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()
        
        # Initialize L1
        self.l1 = L1MemoryCache(
            self.config.l1_max_size_mb,
            self.config.l1_ttl_seconds
        )
        
        # Initialize L2 if enabled
        self.l2 = None
        if self.config.l2_enabled and REDIS_AVAILABLE:
            try:
                self.l2 = L2RedisCache(
                    self.config.l2_host,
                    self.config.l2_port,
                    self.config.l2_db,
                    self.config.l2_ttl_seconds
                )
            except Exception as e:
                print(f"Failed to initialize L2 cache: {e}")
        
        # Initialize L3
        self.l3 = L3DiskCache(
            self.config.l3_path,
            self.config.l3_max_size_mb,
            self.config.l3_ttl_seconds
        )
    
    def get(self, key: str) -> Optional[bytes]:
        """
        Get item from cache (L1 -> L2 -> L3)
        """
        # Try L1 first
        data = self.l1.get(key)
        if data is not None:
            return data
        
        # Try L2
        if self.l2:
            data = self.l2.get(key)
            if data is not None:
                # Promote to L1
                self.l1.set(key, data)
                return data
        
        # Try L3
        data = self.l3.get(key)
        if data is not None:
            # Promote to L1 and L2
            self.l1.set(key, data)
            if self.l2:
                self.l2.set(key, data)
            return data
        
        return None
    
    def set(
        self,
        key: str,
        data: bytes,
        content_type: str = 'image/webp',
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Set item in all cache layers (write-through)
        """
        success = True
        
        # Write to L1
        if not self.l1.set(key, data, content_type, ttl, tags):
            success = False
        
        # Write to L2
        if self.l2:
            if not self.l2.set(key, data, content_type, ttl, tags):
                success = False
        
        # Write to L3
        if not self.l3.set(key, data, content_type, ttl, tags):
            success = False
        
        return success
    
    def delete(self, key: str) -> bool:
        """Delete from all layers"""
        self.l1.delete(key)
        if self.l2:
            self.l2.delete(key)
        self.l3.delete(key)
        return True
    
    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all items with tag"""
        count = 0
        count += self.l1.invalidate_by_tag(tag)
        if self.l2:
            count += self.l2.invalidate_by_tag(tag)
        # L3 doesn't support tag-based invalidation efficiently
        return count
    
    def get_all_stats(self) -> Dict[str, CacheStats]:
        """Get statistics for all layers"""
        stats = {'l1': self.l1.get_stats()}
        
        if self.l2:
            stats['l2'] = self.l2.get_stats()
        
        stats['l3'] = self.l3.get_stats()
        
        return stats


# Example usage
if __name__ == "__main__":
    # Create cache
    config = CacheConfig(
        l1_max_size_mb=50,
        l2_enabled=False,  # Set to True if Redis available
        l3_path='/tmp/image_cache'
    )
    
    cache = MultiLayerCache(config)
    
    # Test data
    test_data = b"test image data" * 1000
    key = "test_image_1"
    
    # Set in cache
    cache.set(key, test_data, 'image/png', tags=['chart', 'dashboard'])
    
    # Get from cache
    retrieved = cache.get(key)
    print(f"Retrieved: {len(retrieved)} bytes" if retrieved else "Not found")
    
    # Get stats
    stats = cache.get_all_stats()
    for level, stat in stats.items():
        print(f"\n{level.upper()} Stats:")
        print(f"  Hits: {stat.hits}")
        print(f"  Misses: {stat.misses}")
        print(f"  Hit Rate: {stat.hit_rate:.2%}")
        print(f"  Size: {stat.size_bytes / 1024:.2f} KB")
```


---

## 7. Export API

### 7.1 RESTful Export API

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/api/export_api.py
"""
Image Export API for ResilienceAI
Provides RESTful endpoints for image generation and export
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import io
import json
import uuid
import asyncio
from datetime import datetime

# FastAPI imports
from fastapi import FastAPI, HTTPException, BackgroundTasks, Query, File, UploadFile
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import our image processing modules
# (Assuming they're in the same package)


class ExportFormat(str, Enum):
    """Supported export formats"""
    PNG = "png"
    JPEG = "jpeg"
    WEBP = "webp"
    SVG = "svg"
    PDF = "pdf"


class ChartType(str, Enum):
    """Supported chart types"""
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"
    AREA = "area"
    HEATMAP = "heatmap"
    RADAR = "radar"
    GAUGE = "gauge"


class ExportRequest(BaseModel):
    """Base export request"""
    format: ExportFormat = ExportFormat.PNG
    width: int = Field(default=800, ge=100, le=4096)
    height: int = Field(default=600, ge=100, le=4096)
    quality: int = Field(default=90, ge=1, le=100)
    background_color: str = "#ffffff"
    transparent: bool = False


class ChartExportRequest(ExportRequest):
    """Chart export request"""
    chart_type: ChartType
    data: Dict[str, Any]
    title: Optional[str] = None
    subtitle: Optional[str] = None
    legend_position: str = "bottom"
    color_palette: Optional[List[str]] = None


class VisualizationExportRequest(ExportRequest):
    """Visualization export request"""
    visualization_type: str  # topology, dashboard, network
    config: Dict[str, Any]


class ThumbnailRequest(BaseModel):
    """Thumbnail generation request"""
    width: int = Field(default=200, ge=10, le=2000)
    height: int = Field(default=200, ge=10, le=2000)
    strategy: str = "fit"  # fit, fill, pad, smart_crop, entropy
    quality: int = Field(default=85, ge=1, le=100)
    format: ExportFormat = ExportFormat.WEBP


class BatchExportRequest(BaseModel):
    """Batch export request"""
    items: List[ChartExportRequest]
    output_format: ExportFormat = ExportFormat.PNG
    zip_output: bool = True


class ExportJob(BaseModel):
    """Export job status"""
    job_id: str
    status: str  # pending, processing, completed, failed
    created_at: datetime
    completed_at: Optional[datetime] = None
    progress: float = 0.0
    result_url: Optional[str] = None
    error_message: Optional[str] = None
    file_size: Optional[int] = None


# In-memory job store (use Redis in production)
job_store: Dict[str, ExportJob] = {}

app = FastAPI(
    title="ResilienceAI Image Export API",
    description="API for generating and exporting images from charts and visualizations",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============== Chart Export Endpoints ==============

@app.post("/api/v1/export/chart", response_class=StreamingResponse)
async def export_chart(request: ChartExportRequest):
    """
    Export a chart as an image
    
    Returns the generated image in the requested format
    """
    try:
        # Import chart generator
        from image_generator.chart_generator import (
            ChartImageGenerator, ChartConfig, ExportOptions, ExportFormat as GenFormat
        )
        
        # Create config
        config = ChartConfig(
            width=request.width,
            height=request.height,
            background_color=request.background_color,
            transparent=request.transparent,
            title=request.title,
            subtitle=request.subtitle,
            legend_position=request.legend_position,
            color_palette=request.color_palette
        )
        
        generator = ChartImageGenerator(config)
        
        # Map format
        format_map = {
            ExportFormat.PNG: GenFormat.PNG,
            ExportFormat.JPEG: GenFormat.JPEG,
            ExportFormat.WEBP: GenFormat.WEBP,
            ExportFormat.SVG: GenFormat.SVG,
            ExportFormat.PDF: GenFormat.PDF
        }
        
        options = ExportOptions(
            format=format_map.get(request.format, GenFormat.PNG),
            quality=request.quality
        )
        
        # Generate based on chart type
        chart_method = getattr(generator, f"generate_{request.chart_type.value}_chart")
        image_bytes = chart_method(request.data, options)
        
        # Return streaming response
        media_types = {
            ExportFormat.PNG: "image/png",
            ExportFormat.JPEG: "image/jpeg",
            ExportFormat.WEBP: "image/webp",
            ExportFormat.SVG: "image/svg+xml",
            ExportFormat.PDF: "application/pdf"
        }
        
        return StreamingResponse(
            io.BytesIO(image_bytes),
            media_type=media_types.get(request.format, "image/png"),
            headers={
                "Content-Disposition": f"attachment; filename=chart_{request.chart_type.value}.{request.format.value}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/export/chart/base64")
async def export_chart_base64(request: ChartExportRequest):
    """
    Export a chart as base64-encoded string
    
    Useful for embedding directly in HTML/JSON
    """
    try:
        from image_generator.chart_generator import (
            ChartImageGenerator, ChartConfig, ExportOptions, ExportFormat as GenFormat
        )
        
        config = ChartConfig(
            width=request.width,
            height=request.height,
            title=request.title
        )
        
        generator = ChartImageGenerator(config)
        
        format_map = {
            ExportFormat.PNG: GenFormat.PNG,
            ExportFormat.JPEG: GenFormat.JPEG,
            ExportFormat.WEBP: GenFormat.WEBP
        }
        
        options = ExportOptions(format=format_map.get(request.format, GenFormat.PNG))
        chart_method = getattr(generator, f"generate_{request.chart_type.value}_chart")
        image_bytes = chart_method(request.data, options)
        
        # Convert to base64
        import base64
        base64_data = base64.b64encode(image_bytes).decode('utf-8')
        
        mime_types = {
            ExportFormat.PNG: "image/png",
            ExportFormat.JPEG: "image/jpeg",
            ExportFormat.WEBP: "image/webp"
        }
        
        return {
            "data_url": f"data:{mime_types.get(request.format, 'image/png')};base64,{base64_data}",
            "base64": base64_data,
            "format": request.format.value,
            "width": request.width,
            "height": request.height,
            "size_bytes": len(image_bytes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Visualization Export Endpoints ==============

@app.post("/api/v1/export/visualization/topology", response_class=StreamingResponse)
async def export_topology(
    nodes: List[Dict[str, Any]],
    edges: List[Dict[str, Any]],
    layout: str = Query("force-directed", enum=["force-directed", "circular", "hierarchical"]),
    width: int = Query(1000, ge=400, le=2000),
    height: int = Query(800, ge=300, le=1500),
    format: ExportFormat = Query(ExportFormat.PNG)
):
    """
    Export network topology visualization
    """
    try:
        from image_generator.visualization_generator import NetworkGraphGenerator
        
        generator = NetworkGraphGenerator(width=width, height=height)
        image_bytes = generator.generate_topology_map(nodes, edges, layout)
        
        media_types = {
            ExportFormat.PNG: "image/png",
            ExportFormat.JPEG: "image/jpeg",
            ExportFormat.WEBP: "image/webp"
        }
        
        return StreamingResponse(
            io.BytesIO(image_bytes),
            media_type=media_types.get(format, "image/png"),
            headers={
                "Content-Disposition": f"attachment; filename=topology.{format.value}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Thumbnail Endpoints ==============

@app.post("/api/v1/thumbnail/generate", response_class=StreamingResponse)
async def generate_thumbnail(
    file: UploadFile = File(...),
    width: int = Query(200, ge=10, le=2000),
    height: int = Query(200, ge=10, le=2000),
    strategy: str = Query("fit", enum=["fit", "fill", "pad", "smart_crop", "entropy"]),
    quality: int = Query(85, ge=1, le=100),
    format: ExportFormat = Query(ExportFormat.WEBP)
):
    """
    Generate thumbnail from uploaded image
    """
    try:
        from thumbnail.thumbnail_generator import (
            ThumbnailGenerator, ThumbnailConfig, ThumbnailStrategy
        )
        
        # Read uploaded file
        image_bytes = await file.read()
        
        # Map strategy
        strategy_map = {
            "fit": ThumbnailStrategy.FIT,
            "fill": ThumbnailStrategy.FILL,
            "pad": ThumbnailStrategy.PAD,
            "smart_crop": ThumbnailStrategy.SMART_CROP,
            "entropy": ThumbnailStrategy.ENTROPY
        }
        
        config = ThumbnailConfig(
            width=width,
            height=height,
            strategy=strategy_map.get(strategy, ThumbnailStrategy.FIT),
            quality=quality,
            format=format.value
        )
        
        generator = ThumbnailGenerator()
        result = generator.generate(image_bytes, config)
        
        media_types = {
            ExportFormat.PNG: "image/png",
            ExportFormat.JPEG: "image/jpeg",
            ExportFormat.WEBP: "image/webp"
        }
        
        return StreamingResponse(
            io.BytesIO(result.image_bytes),
            media_type=media_types.get(format, "image/webp"),
            headers={
                "Content-Disposition": f"attachment; filename=thumbnail.{format.value}",
                "X-Processing-Time": str(result.processing_time_ms)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/thumbnail/batch")
async def generate_thumbnails_batch(
    files: List[UploadFile] = File(...),
    sizes: str = Query("200x200,400x400"),  # Comma-separated sizes
    strategy: str = Query("fit")
):
    """
    Generate thumbnails for multiple images at multiple sizes
    """
    try:
        from thumbnail.thumbnail_generator import (
            ThumbnailGenerator, ThumbnailConfig, ThumbnailStrategy
        )
        
        # Parse sizes
        size_list = []
        for size_str in sizes.split(','):
            w, h = map(int, size_str.split('x'))
            size_list.append((w, h))
        
        strategy_map = {
            "fit": ThumbnailStrategy.FIT,
            "fill": ThumbnailStrategy.FILL,
            "pad": ThumbnailStrategy.PAD
        }
        
        generator = ThumbnailGenerator()
        results = []
        
        for file in files:
            image_bytes = await file.read()
            
            base_config = ThumbnailConfig(
                strategy=strategy_map.get(strategy, ThumbnailStrategy.FIT)
            )
            
            thumbnails = generator.generate_set(image_bytes, size_list, base_config)
            
            results.append({
                "filename": file.filename,
                "thumbnails": {
                    size: {
                        "width": t.width,
                        "height": t.height,
                        "size_bytes": t.thumbnail_size,
                        "cache_key": t.cache_key
                    }
                    for size, t in thumbnails.items()
                }
            })
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== Batch Export Endpoints ==============

@app.post("/api/v1/export/batch", response_model=ExportJob)
async def create_batch_export(
    request: BatchExportRequest,
    background_tasks: BackgroundTasks
):
    """
    Create a batch export job
    
    Returns job ID for status tracking
    """
    job_id = str(uuid.uuid4())
    
    job = ExportJob(
        job_id=job_id,
        status="pending",
        created_at=datetime.utcnow(),
        progress=0.0
    )
    
    job_store[job_id] = job
    
    # Start background processing
    background_tasks.add_task(process_batch_export, job_id, request)
    
    return job


async def process_batch_export(job_id: str, request: BatchExportRequest):
    """Process batch export in background"""
    job = job_store[job_id]
    job.status = "processing"
    
    try:
        total = len(request.items)
        results = []
        
        for i, item in enumerate(request.items):
            # Process each item
            # (Implementation would call chart generation)
            await asyncio.sleep(0.1)  # Simulate work
            
            job.progress = (i + 1) / total * 100
        
        job.status = "completed"
        job.completed_at = datetime.utcnow()
        job.result_url = f"/api/v1/export/batch/{job_id}/download"
        
    except Exception as e:
        job.status = "failed"
        job.error_message = str(e)


@app.get("/api/v1/export/batch/{job_id}", response_model=ExportJob)
async def get_batch_status(job_id: str):
    """Get batch export job status"""
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@app.get("/api/v1/export/batch/{job_id}/download")
async def download_batch_result(job_id: str):
    """Download batch export result"""
    job = job_store.get(job_id)
    if not job or job.status != "completed":
        raise HTTPException(status_code=404, detail="Result not available")
    
    # Return ZIP file
    # (Implementation would create ZIP from results)
    pass


# ============== Utility Endpoints ==============

@app.get("/api/v1/formats")
async def get_supported_formats():
    """Get list of supported export formats"""
    return {
        "formats": [
            {
                "id": fmt.value,
                "name": fmt.value.upper(),
                "supports_transparency": fmt in (ExportFormat.PNG, ExportFormat.WEBP, ExportFormat.SVG),
                "mime_type": {
                    ExportFormat.PNG: "image/png",
                    ExportFormat.JPEG: "image/jpeg",
                    ExportFormat.WEBP: "image/webp",
                    ExportFormat.SVG: "image/svg+xml",
                    ExportFormat.PDF: "application/pdf"
                }.get(fmt)
            }
            for fmt in ExportFormat
        ]
    }


@app.get("/api/v1/chart-types")
async def get_chart_types():
    """Get list of supported chart types"""
    return {
        "chart_types": [
            {"id": ct.value, "name": ct.value.replace('_', ' ').title()}
            for ct in ChartType
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "image-export-api"}


# Run with: uvicorn export_api:app --reload --host 0.0.0.0 --port 8000
```

---

## 8. Batch Processing

### 8.1 Batch Processor

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/batch/batch_processor.py
"""
Batch Image Processing for ResilienceAI
Handles concurrent processing of multiple images
"""

import asyncio
import concurrent.futures
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
import time
import uuid
from datetime import datetime
import logging

from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Batch job status"""
    PENDING = auto()
    RUNNING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


@dataclass
class BatchJob:
    """Batch job definition"""
    job_id: str
    items: List[Any]
    processor: Callable
    status: JobStatus
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: List[Any] = None
    errors: List[Dict] = None
    progress: float = 0.0
    total_items: int = 0
    processed_items: int = 0
    failed_items: int = 0


@dataclass
class ProcessingResult:
    """Result of processing a single item"""
    item_index: int
    success: bool
    data: Any = None
    error: Optional[str] = None
    processing_time_ms: float = 0.0


class BatchProcessor:
    """
    High-performance batch image processor
    Supports both sync and async processing
    """
    
    def __init__(
        self,
        max_workers: int = 4,
        chunk_size: int = 10,
        use_processes: bool = False
    ):
        self.max_workers = max_workers
        self.chunk_size = chunk_size
        self.use_processes = use_processes
        self._jobs: Dict[str, BatchJob] = {}
        self._executor_class = (
            concurrent.futures.ProcessPoolExecutor if use_processes
            else concurrent.futures.ThreadPoolExecutor
        )
    
    def submit_job(
        self,
        items: List[Any],
        processor: Callable[[Any], Any],
        job_id: Optional[str] = None
    ) -> str:
        """
        Submit a batch processing job
        
        Args:
            items: List of items to process
            processor: Function to process each item
            job_id: Optional job ID (generated if not provided)
            
        Returns:
            Job ID
        """
        job_id = job_id or str(uuid.uuid4())
        
        job = BatchJob(
            job_id=job_id,
            items=items,
            processor=processor,
            status=JobStatus.PENDING,
            created_at=datetime.utcnow(),
            results=[None] * len(items),
            errors=[],
            total_items=len(items)
        )
        
        self._jobs[job_id] = job
        
        return job_id
    
    async def run_job_async(self, job_id: str) -> BatchJob:
        """
        Run a batch job asynchronously
        
        Args:
            job_id: Job ID to run
            
        Returns:
            Completed job
        """
        job = self._jobs.get(job_id)
        if not job:
            raise ValueError(f"Job {job_id} not found")
        
        job.status = JobStatus.RUNNING
        job.started_at = datetime.utcnow()
        
        loop = asyncio.get_event_loop()
        
        with self._executor_class(max_workers=self.max_workers) as executor:
            # Create futures for all items
            futures = []
            for i, item in enumerate(job.items):
                future = loop.run_in_executor(
                    executor,
                    self._process_item_wrapper,
                    i,
                    item,
                    job.processor
                )
                futures.append(future)
            
            # Process as they complete
            for i, future in enumerate(asyncio.as_completed(futures)):
                try:
                    result = await future
                    job.results[result.item_index] = result.data if result.success else None
                    
                    if not result.success:
                        job.errors.append({
                            'index': result.item_index,
                            'error': result.error
                        })
                        job.failed_items += 1
                    
                    job.processed_items += 1
                    job.progress = job.processed_items / job.total_items * 100
                    
                except Exception as e:
                    logger.error(f"Error processing item: {e}")
                    job.errors.append({'index': i, 'error': str(e)})
                    job.failed_items += 1
        
        job.status = JobStatus.COMPLETED if job.failed_items < job.total_items else JobStatus.FAILED
        job.completed_at = datetime.utcnow()
        
        return job
    
    def run_job_sync(self, job_id: str) -> BatchJob:
        """Run a batch job synchronously"""
        return asyncio.run(self.run_job_async(job_id))
    
    def _process_item_wrapper(
        self,
        index: int,
        item: Any,
        processor: Callable
    ) -> ProcessingResult:
        """Wrapper for processing a single item"""
        start_time = time.time()
        
        try:
            result = processor(item)
            processing_time = (time.time() - start_time) * 1000
            
            return ProcessingResult(
                item_index=index,
                success=True,
                data=result,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            processing_time = (time.time() - start_time) * 1000
            logger.error(f"Error processing item {index}: {e}")
            
            return ProcessingResult(
                item_index=index,
                success=False,
                error=str(e),
                processing_time_ms=processing_time
            )
    
    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """Get job by ID"""
        return self._jobs.get(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        job = self._jobs.get(job_id)
        if job and job.status == JobStatus.RUNNING:
            job.status = JobStatus.CANCELLED
            return True
        return False
    
    def get_job_stats(self, job_id: str) -> Dict[str, Any]:
        """Get job statistics"""
        job = self._jobs.get(job_id)
        if not job:
            return None
        
        duration = None
        if job.started_at and job.completed_at:
            duration = (job.completed_at - job.started_at).total_seconds()
        
        return {
            'job_id': job.job_id,
            'status': job.status.name,
            'progress': job.progress,
            'total_items': job.total_items,
            'processed_items': job.processed_items,
            'failed_items': job.failed_items,
            'success_rate': (job.total_items - job.failed_items) / job.total_items * 100,
            'duration_seconds': duration,
            'created_at': job.created_at.isoformat(),
            'started_at': job.started_at.isoformat() if job.started_at else None,
            'completed_at': job.completed_at.isoformat() if job.completed_at else None
        }


class ImageBatchOperations:
    """
    Pre-defined batch operations for images
    """
    
    def __init__(self, processor: BatchProcessor):
        self.processor = processor
    
    def batch_optimize(
        self,
        image_paths: List[Path],
        target_format: str = 'webp',
        quality: int = 85
    ) -> str:
        """
        Batch optimize images
        
        Args:
            image_paths: List of image file paths
            target_format: Target format
            quality: Output quality
            
        Returns:
            Job ID
        """
        def optimize_image(path: Path) -> Dict:
            from optimizer.image_optimizer import ImageOptimizer, OptimizationConfig
            
            optimizer = ImageOptimizer(OptimizationConfig())
            image_bytes = path.read_bytes()
            
            optimized, result = optimizer.optimize(
                image_bytes,
                target_format=target_format
            )
            
            # Save optimized image
            output_path = path.with_suffix(f'.{target_format}')
            output_path.write_bytes(optimized)
            
            return {
                'input_path': str(path),
                'output_path': str(output_path),
                'original_size': result.original_size,
                'optimized_size': result.optimized_size,
                'compression_ratio': result.compression_ratio
            }
        
        return self.processor.submit_job(image_paths, optimize_image)
    
    def batch_resize(
        self,
        image_paths: List[Path],
        sizes: List[Tuple[int, int]],
        output_dir: Path
    ) -> str:
        """
        Batch resize images to multiple sizes
        
        Args:
            image_paths: List of image paths
            sizes: List of (width, height) tuples
            output_dir: Output directory
            
        Returns:
            Job ID
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        def resize_image(path: Path) -> Dict:
            img = Image.open(path)
            results = []
            
            for width, height in sizes:
                resized = img.copy()
                resized.thumbnail((width, height), Image.Resampling.LANCZOS)
                
                output_path = output_dir / f"{path.stem}_{width}x{height}{path.suffix}"
                resized.save(output_path, optimize=True)
                
                results.append({
                    'size': f'{width}x{height}',
                    'path': str(output_path)
                })
            
            return {'input': str(path), 'outputs': results}
        
        return self.processor.submit_job(image_paths, resize_image)
    
    def batch_convert(
        self,
        image_paths: List[Path],
        target_format: str,
        output_dir: Path
    ) -> str:
        """
        Batch convert images to target format
        
        Args:
            image_paths: List of image paths
            target_format: Target format
            output_dir: Output directory
            
        Returns:
            Job ID
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        def convert_image(path: Path) -> Dict:
            from optimizer.format_converter import FormatConverter, ImageFormat
            
            converter = FormatConverter()
            image_bytes = path.read_bytes()
            
            target = ImageFormat(target_format)
            # Assume PNG source for simplicity
            converted = converter.convert(image_bytes, ImageFormat.PNG, target)
            
            output_path = output_dir / f"{path.stem}.{target_format}"
            output_path.write_bytes(converted)
            
            return {
                'input': str(path),
                'output': str(output_path),
                'format': target_format
            }
        
        return self.processor.submit_job(image_paths, convert_image)


# Example usage
if __name__ == "__main__":
    # Create processor
    processor = BatchProcessor(max_workers=4)
    
    # Create test images
    test_images = []
    for i in range(10):
        img = Image.new('RGB', (1000, 1000), color=(i*20, i*15, i*25))
        path = Path(f'/tmp/test_image_{i}.png')
        img.save(path)
        test_images.append(path)
    
    # Batch operations
    operations = ImageBatchOperations(processor)
    
    # Submit batch optimize job
    job_id = operations.batch_optimize(test_images, target_format='webp')
    print(f"Submitted job: {job_id}")
    
    # Run job
    job = processor.run_job_sync(job_id)
    
    # Print results
    stats = processor.get_job_stats(job_id)
    print(f"\nJob Stats:")
    print(f"  Status: {stats['status']}")
    print(f"  Success Rate: {stats['success_rate']:.1f}%")
    print(f"  Duration: {stats['duration_seconds']:.2f}s")
```


---

## 9. Responsive Images

### 9.1 Responsive Image Handler

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/responsive/responsive_handler.py
"""
Responsive Image Handler for ResilienceAI
Generates responsive image sets and HTML for optimal delivery
"""

import io
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PIL import Image


class Breakpoint(Enum):
    """Standard responsive breakpoints"""
    MOBILE_S = 320
    MOBILE_M = 375
    MOBILE_L = 425
    TABLET = 768
    LAPTOP = 1024
    LAPTOP_L = 1440
    DESKTOP = 1920
    DESKTOP_L = 2560


@dataclass
class ResponsiveImage:
    """Single responsive image variant"""
    width: int
    height: int
    url: str
    format: str
    size_bytes: int
    density: str = "1x"  # 1x, 2x, 3x


@dataclass
class ResponsiveSet:
    """Complete responsive image set"""
    src: str  # Fallback src
    srcset: str
    sizes: str
    formats: Dict[str, List[ResponsiveImage]]
    aspect_ratio: float
    alt: str
    loading: str
    decoding: str


class ResponsiveImageGenerator:
    """
    Generate responsive image sets for optimal web delivery
    """
    
    # Default breakpoints for responsive images
    DEFAULT_BREAKPOINTS = [320, 640, 768, 1024, 1440, 1920]
    
    # Format preference by browser support
    FORMAT_PRIORITY = ['avif', 'webp', 'jpeg', 'png']
    
    def __init__(
        self,
        base_url: str = "/images",
        breakpoints: Optional[List[int]] = None,
        generate_avif: bool = False
    ):
        self.base_url = base_url
        self.breakpoints = breakpoints or self.DEFAULT_BREAKPOINTS
        self.generate_avif = generate_avif
    
    def generate_set(
        self,
        image_bytes: bytes,
        alt: str = "",
        sizes: str = "100vw",
        aspect_ratio: Optional[float] = None,
        max_width: int = 1920
    ) -> ResponsiveSet:
        """
        Generate complete responsive image set
        
        Args:
            image_bytes: Source image
            alt: Alt text
            sizes: Sizes attribute for srcset
            aspect_ratio: Optional aspect ratio to maintain
            max_width: Maximum width to generate
            
        Returns:
            ResponsiveSet with all variants
        """
        img = Image.open(io.BytesIO(image_bytes))
        orig_width, orig_height = img.size
        
        if aspect_ratio is None:
            aspect_ratio = orig_height / orig_width
        
        formats = {}
        
        # Generate for each format
        for fmt in ['webp', 'jpeg']:
            if fmt == 'avif' and not self.generate_avif:
                continue
            
            variants = self._generate_format_variants(
                image_bytes, fmt, aspect_ratio, max_width, orig_width
            )
            formats[fmt] = variants
        
        # Build srcset strings
        srcset_by_format = {}
        for fmt, variants in formats.items():
            srcset_parts = [f"{v.url} {v.width}w" for v in variants]
            srcset_by_format[fmt] = ", ".join(srcset_parts)
        
        # Use smallest WebP as fallback
        fallback = formats['webp'][0] if 'webp' in formats else list(formats.values())[0][0]
        
        return ResponsiveSet(
            src=fallback.url,
            srcset=srcset_by_format.get('webp', ''),
            sizes=sizes,
            formats=formats,
            aspect_ratio=aspect_ratio,
            alt=alt,
            loading="lazy",
            decoding="async"
        )
    
    def _generate_format_variants(
        self,
        image_bytes: bytes,
        format: str,
        aspect_ratio: float,
        max_width: int,
        orig_width: int
    ) -> List[ResponsiveImage]:
        """Generate variants for a specific format"""
        from thumbnail.thumbnail_generator import ThumbnailGenerator, ThumbnailConfig
        
        variants = []
        generator = ThumbnailGenerator()
        
        for breakpoint in self.breakpoints:
            if breakpoint > max_width or breakpoint > orig_width:
                continue
            
            width = breakpoint
            height = int(width * aspect_ratio)
            
            config = ThumbnailConfig(
                width=width,
                height=height,
                format=format,
                quality=85 if format == 'webp' else 90
            )
            
            result = generator.generate(image_bytes, config)
            
            variants.append(ResponsiveImage(
                width=width,
                height=height,
                url=f"{self.base_url}/{result.cache_key}.{format}",
                format=format,
                size_bytes=result.thumbnail_size
            ))
        
        return variants
    
    def generate_picture_html(self, responsive_set: ResponsiveSet) -> str:
        """
        Generate HTML <picture> element with all formats
        
        Args:
            responsive_set: Responsive image set
            
        Returns:
            HTML string
        """
        sources = []
        
        # Add sources for each format (AVIF first, then WebP)
        format_order = ['avif', 'webp']
        for fmt in format_order:
            if fmt in responsive_set.formats:
                variants = responsive_set.formats[fmt]
                srcset = ", ".join([f"{v.url} {v.width}w" for v in variants])
                sources.append(f'    <source srcset="{srcset}" sizes="{responsive_set.sizes}" type="image/{fmt}">')
        
        # Add fallback img
        sources_str = "\n".join(sources)
        
        # Get JPEG fallback
        jpeg_variants = responsive_set.formats.get('jpeg', [])
        if jpeg_variants:
            fallback = jpeg_variants[0]
            srcset = ", ".join([f"{v.url} {v.width}w" for v in jpeg_variants])
        else:
            fallback_url = responsive_set.src
            srcset = responsive_set.srcset
        
        html = f'''<picture>
{sources_str}
    <img
        src="{responsive_set.src}"
        srcset="{srcset}"
        sizes="{responsive_set.sizes}"
        alt="{responsive_set.alt}"
        width="{responsive_set.formats.get('webp', [{}])[0].width if responsive_set.formats.get('webp') else 800}"
        height="{int((responsive_set.formats.get('webp', [{}])[0].width if responsive_set.formats.get('webp') else 800) * responsive_set.aspect_ratio)}"
        loading="{responsive_set.loading}"
        decoding="{responsive_set.decoding}"
    />
</picture>'''
        
        return html
    
    def generate_css_background(
        self,
        responsive_set: ResponsiveSet,
        selector: str = ".responsive-bg"
    ) -> str:
        """
        Generate CSS for responsive background images
        
        Args:
            responsive_set: Responsive image set
            selector: CSS selector
            
        Returns:
            CSS string
        """
        css_parts = [f"{selector} {{"]
        
        # Default (mobile-first)
        if 'webp' in responsive_set.formats and responsive_set.formats['webp']:
            smallest = responsive_set.formats['webp'][0]
            css_parts.append(f"  background-image: url('{smallest.url}');")
        
        css_parts.append("  background-size: cover;")
        css_parts.append("  background-position: center;")
        css_parts.append("}")
        
        # Media queries for larger screens
        for i, breakpoint in enumerate(self.breakpoints[1:], 1):
            if 'webp' in responsive_set.formats and i < len(responsive_set.formats['webp']):
                variant = responsive_set.formats['webp'][i]
                css_parts.append(f"\n@media (min-width: {breakpoint}px) {{")
                css_parts.append(f"  {selector} {{")
                css_parts.append(f"    background-image: url('{variant.url}');")
                css_parts.append("  }")
                css_parts.append("}")
        
        return "\n".join(css_parts)
    
    def generate_srcset_only(
        self,
        responsive_set: ResponsiveSet,
        use_webp: bool = True
    ) -> str:
        """
        Generate simplified srcset for img tag
        
        Args:
            responsive_set: Responsive image set
            use_webp: Use WebP format
            
        Returns:
            HTML img tag string
        """
        format_key = 'webp' if use_webp and 'webp' in responsive_set.formats else 'jpeg'
        variants = responsive_set.formats.get(format_key, [])
        
        if not variants:
            return f'<img src="{responsive_set.src}" alt="{responsive_set.alt}" />'
        
        srcset = ", ".join([f"{v.url} {v.width}w" for v in variants])
        fallback = variants[len(variants) // 2]  # Middle size as fallback
        
        return f'''<img
    src="{fallback.url}"
    srcset="{srcset}"
    sizes="{responsive_set.sizes}"
    alt="{responsive_set.alt}"
    width="{fallback.width}"
    height="{fallback.height}"
    loading="lazy"
/>'''


class ArtDirectionHandler:
    """
    Handle art-directed responsive images
    Different crops for different screen sizes
    """
    
    def __init__(self, generator: ResponsiveImageGenerator):
        self.generator = generator
    
    def generate_art_directed_set(
        self,
        image_bytes: bytes,
        crops: Dict[str, Tuple[int, int, int, int]],  # breakpoint -> (x, y, w, h)
        alt: str = ""
    ) -> str:
        """
        Generate art-directed responsive image
        
        Args:
            image_bytes: Source image
            crops: Crop regions for different breakpoints
            alt: Alt text
            
        Returns:
            HTML picture element
        """
        img = Image.open(io.BytesIO(image_bytes))
        sources = []
        
        for breakpoint, (x, y, w, h) in sorted(crops.items(), key=lambda x: int(x[0]), reverse=True):
            # Crop image
            cropped = img.crop((x, y, x + w, y + h))
            
            # Generate responsive set for cropped image
            buffer = io.BytesIO()
            cropped.save(buffer, 'PNG')
            
            responsive_set = self.generator.generate_set(
                buffer.getvalue(),
                alt=alt,
                sizes=f"(min-width: {breakpoint}px) 100vw"
            )
            
            # Build media query
            if breakpoint == "0":
                media = ""
            else:
                media = f' media="(min-width: {breakpoint}px)"'
            
            # Add source
            if 'webp' in responsive_set.formats:
                variants = responsive_set.formats['webp']
                srcset = ", ".join([f"{v.url} {v.width}w" for v in variants])
                sources.append(f'  <source{media} srcset="{srcset}" sizes="100vw" type="image/webp">')
        
        # Build picture element
        sources_html = "\n".join(sources)
        
        # Fallback image (smallest crop)
        smallest_crop = min(crops.items(), key=lambda x: x[1][2] * x[1][3])
        x, y, w, h = smallest_crop[1]
        fallback = img.crop((x, y, x + w, y + h))
        
        buffer = io.BytesIO()
        fallback.save(buffer, 'PNG')
        fallback_set = self.generator.generate_set(buffer.getvalue(), alt=alt)
        
        return f'''<picture>
{sources_html}
  <img src="{fallback_set.src}" alt="{alt}" loading="lazy" />
</picture>'''


# Example usage
if __name__ == "__main__":
    from PIL import Image, ImageDraw
    
    # Create test image
    img = Image.new('RGB', (1920, 1080), color='#3498db')
    draw = ImageDraw.Draw(img)
    
    # Add some visual elements
    for i in range(0, 1920, 100):
        draw.line([(i, 0), (i, 1080)], fill='#2980b9', width=3)
    for i in range(0, 1080, 100):
        draw.line([(0, i), (1920, i)], fill='#2980b9', width=3)
    
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    image_bytes = buffer.getvalue()
    
    # Generate responsive set
    generator = ResponsiveImageGenerator(base_url="/images/responsive")
    responsive_set = generator.generate_set(
        image_bytes,
        alt="Test responsive image",
        sizes="(max-width: 768px) 100vw, 50vw"
    )
    
    # Generate HTML
    picture_html = generator.generate_picture_html(responsive_set)
    print("Picture Element HTML:")
    print(picture_html)
    
    print("\n" + "="*60 + "\n")
    
    # Generate CSS background
    css = generator.generate_css_background(responsive_set, ".hero-section")
    print("CSS Background:")
    print(css)
```

---

## 10. Metadata Management

### 10.1 Image Metadata Handler

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/metadata/metadata_manager.py
"""
Image Metadata Management for ResilienceAI
Handles EXIF, XMP, and custom metadata
"""

import io
import json
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import hashlib

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS


@dataclass
class ImageMetadata:
    """Comprehensive image metadata"""
    # Basic info
    filename: Optional[str] = None
    format: Optional[str] = None
    mode: Optional[str] = None
    width: int = 0
    height: int = 0
    
    # File info
    file_size_bytes: int = 0
    checksum_md5: Optional[str] = None
    checksum_sha256: Optional[str] = None
    created_at: Optional[datetime] = None
    modified_at: Optional[datetime] = None
    
    # EXIF data
    camera_make: Optional[str] = None
    camera_model: Optional[str] = None
    date_taken: Optional[datetime] = None
    exposure_time: Optional[str] = None
    f_number: Optional[float] = None
    iso: Optional[int] = None
    focal_length: Optional[float] = None
    gps_coordinates: Optional[Tuple[float, float]] = None
    
    # Color info
    color_space: Optional[str] = None
    color_profile: Optional[str] = None
    bits_per_channel: int = 8
    
    # Custom metadata
    title: Optional[str] = None
    description: Optional[str] = None
    author: Optional[str] = None
    copyright: Optional[str] = None
    keywords: List[str] = None
    categories: List[str] = None
    
    # Application-specific
    source: Optional[str] = None  # e.g., 'chart', 'visualization', 'upload'
    generation_params: Dict[str, Any] = None
    processing_history: List[Dict] = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.categories is None:
            self.categories = []
        if self.generation_params is None:
            self.generation_params = {}
        if self.processing_history is None:
            self.processing_history = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert datetime objects
        for key in ['created_at', 'modified_at', 'date_taken']:
            if data.get(key):
                data[key] = data[key].isoformat() if isinstance(data[key], datetime) else data[key]
        return data
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict(), indent=2)


class MetadataExtractor:
    """Extract metadata from images"""
    
    def extract(self, image_bytes: bytes, filename: Optional[str] = None) -> ImageMetadata:
        """
        Extract all metadata from image
        
        Args:
            image_bytes: Image data
            filename: Optional filename
            
        Returns:
            ImageMetadata object
        """
        img = Image.open(io.BytesIO(image_bytes))
        
        metadata = ImageMetadata(
            filename=filename,
            format=img.format,
            mode=img.mode,
            width=img.width,
            height=img.height,
            file_size_bytes=len(image_bytes),
            checksum_md5=hashlib.md5(image_bytes).hexdigest(),
            checksum_sha256=hashlib.sha256(image_bytes).hexdigest()
        )
        
        # Extract EXIF if available
        if hasattr(img, '_getexif') and img._getexif():
            self._extract_exif(img, metadata)
        
        # Extract from info dict
        if 'dpi' in img.info:
            metadata.bits_per_channel = img.info.get('bits', 8)
        
        return metadata
    
    def _extract_exif(self, img: Image.Image, metadata: ImageMetadata):
        """Extract EXIF data from image"""
        exif = img._getexif()
        if not exif:
            return
        
        exif_data = {}
        for tag_id, value in exif.items():
            tag = TAGS.get(tag_id, tag_id)
            exif_data[tag] = value
        
        # Camera info
        metadata.camera_make = exif_data.get('Make')
        metadata.camera_model = exif_data.get('Model')
        
        # Date taken
        date_str = exif_data.get('DateTimeOriginal') or exif_data.get('DateTime')
        if date_str:
            try:
                metadata.date_taken = datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            except ValueError:
                pass
        
        # Exposure settings
        exposure = exif_data.get('ExposureTime')
        if exposure:
            if isinstance(exposure, tuple):
                metadata.exposure_time = f"{exposure[0]}/{exposure[1]}"
            else:
                metadata.exposure_time = str(exposure)
        
        metadata.f_number = exif_data.get('FNumber')
        metadata.iso = exif_data.get('ISOSpeedRatings')
        metadata.focal_length = exif_data.get('FocalLength')
        
        # GPS
        gps_info = exif_data.get('GPSInfo')
        if gps_info:
            metadata.gps_coordinates = self._extract_gps(gps_info)
    
    def _extract_gps(self, gps_info: Dict) -> Optional[Tuple[float, float]]:
        """Extract GPS coordinates from EXIF"""
        def convert_to_degrees(value):
            d = float(value[0])
            m = float(value[1])
            s = float(value[2])
            return d + (m / 60.0) + (s / 3600.0)
        
        try:
            lat = convert_to_degrees(gps_info[2])  # GPSLatitude
            lat_ref = gps_info[1]  # GPSLatitudeRef
            if lat_ref != 'N':
                lat = -lat
            
            lon = convert_to_degrees(gps_info[4])  # GPSLongitude
            lon_ref = gps_info[3]  # GPSLongitudeRef
            if lon_ref != 'E':
                lon = -lon
            
            return (lat, lon)
        except (KeyError, IndexError):
            return None


class MetadataWriter:
    """Write metadata to images"""
    
    def write_exif(
        self,
        image_bytes: bytes,
        metadata: ImageMetadata
    ) -> bytes:
        """
        Write EXIF metadata to image
        
        Args:
            image_bytes: Original image
            metadata: Metadata to write
            
        Returns:
            Image with metadata
        """
        img = Image.open(io.BytesIO(image_bytes))
        
        # Create EXIF dict
        exif_dict = {}
        
        if metadata.camera_make:
            exif_dict[271] = metadata.camera_make  # Make
        if metadata.camera_model:
            exif_dict[272] = metadata.camera_model  # Model
        if metadata.date_taken:
            date_str = metadata.date_taken.strftime('%Y:%m:%d %H:%M:%S')
            exif_dict[36867] = date_str  # DateTimeOriginal
        if metadata.copyright:
            exif_dict[33432] = metadata.copyright  # Copyright
        if metadata.description:
            exif_dict[270] = metadata.description  # ImageDescription
        
        # Save with EXIF
        output = io.BytesIO()
        img.save(output, format=img.format or 'PNG', exif=exif_dict if exif_dict else None)
        output.seek(0)
        
        return output.getvalue()
    
    def write_xmp(
        self,
        image_bytes: bytes,
        metadata: Dict[str, Any]
    ) -> bytes:
        """
        Write XMP metadata to image
        
        Args:
            image_bytes: Original image
            metadata: XMP metadata dictionary
            
        Returns:
            Image with XMP metadata
        """
        # XMP implementation would require additional library
        # This is a placeholder
        return image_bytes


class MetadataDatabase:
    """
    Store and retrieve image metadata from database
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or Path('/tmp/image_metadata.db')
        self._init_db()
    
    def _init_db(self):
        """Initialize database"""
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS image_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checksum_sha256 TEXT UNIQUE NOT NULL,
                filename TEXT,
                format TEXT,
                width INTEGER,
                height INTEGER,
                file_size_bytes INTEGER,
                metadata_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_checksum ON image_metadata(checksum_sha256)
        ''')
        
        conn.commit()
        conn.close()
    
    def save(self, metadata: ImageMetadata) -> bool:
        """Save metadata to database"""
        import sqlite3
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO image_metadata
                (checksum_sha256, filename, format, width, height, file_size_bytes, metadata_json, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            ''', (
                metadata.checksum_sha256,
                metadata.filename,
                metadata.format,
                metadata.width,
                metadata.height,
                metadata.file_size_bytes,
                metadata.to_json()
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return False
    
    def get_by_checksum(self, checksum: str) -> Optional[ImageMetadata]:
        """Get metadata by checksum"""
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT metadata_json FROM image_metadata WHERE checksum_sha256 = ?
        ''', (checksum,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            data = json.loads(row[0])
            return ImageMetadata(**data)
        
        return None
    
    def search(
        self,
        keywords: Optional[List[str]] = None,
        format: Optional[str] = None,
        min_width: Optional[int] = None,
        max_width: Optional[int] = None
    ) -> List[ImageMetadata]:
        """Search metadata"""
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT metadata_json FROM image_metadata WHERE 1=1"
        params = []
        
        if format:
            query += " AND format = ?"
            params.append(format)
        
        if min_width:
            query += " AND width >= ?"
            params.append(min_width)
        
        if max_width:
            query += " AND width <= ?"
            params.append(max_width)
        
        cursor.execute(query, params)
        
        results = []
        for row in cursor.fetchall():
            data = json.loads(row[0])
            metadata = ImageMetadata(**data)
            
            # Filter by keywords
            if keywords:
                if any(kw in metadata.keywords for kw in keywords):
                    results.append(metadata)
            else:
                results.append(metadata)
        
        conn.close()
        return results


# Example usage
if __name__ == "__main__":
    # Create test image
    img = Image.new('RGB', (800, 600), color='#3498db')
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    image_bytes = buffer.getvalue()
    
    # Extract metadata
    extractor = MetadataExtractor()
    metadata = extractor.extract(image_bytes, filename="test_image.png")
    
    # Add custom metadata
    metadata.title = "Test Chart"
    metadata.description = "A test chart for ResilienceAI"
    metadata.author = "ResilienceAI System"
    metadata.keywords = ["chart", "test", "visualization"]
    metadata.source = "chart_generator"
    metadata.generation_params = {
        "chart_type": "line",
        "width": 800,
        "height": 600
    }
    
    print("Extracted Metadata:")
    print(metadata.to_json())
    
    # Save to database
    db = MetadataDatabase()
    db.save(metadata)
    
    # Retrieve
    retrieved = db.get_by_checksum(metadata.checksum_sha256)
    print("\nRetrieved from database:")
    print(retrieved.to_json() if retrieved else "Not found")
```


---

## 11. Storage Solutions

### 11.1 Multi-Backend Storage

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/storage/storage_manager.py
"""
Multi-Backend Storage System for ResilienceAI
Supports local filesystem, S3, and CDN storage
"""

import io
from typing import Dict, List, Optional, Any, Union, BinaryIO
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
import hashlib
import mimetypes
from abc import ABC, abstractmethod
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Optional S3 support
try:
    import boto3
    from botocore.exceptions import ClientError
    S3_AVAILABLE = True
except ImportError:
    S3_AVAILABLE = False


class StorageBackend(Enum):
    """Storage backend types"""
    LOCAL = "local"
    S3 = "s3"
    AZURE = "azure"
    GCS = "gcs"
    CDN = "cdn"


@dataclass
class StorageConfig:
    """Storage configuration"""
    backend: StorageBackend = StorageBackend.LOCAL
    
    # Local storage settings
    local_path: Path = Path("/tmp/images")
    
    # S3 settings
    s3_bucket: str = ""
    s3_region: str = "us-east-1"
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_endpoint: Optional[str] = None
    s3_prefix: str = "images"
    
    # CDN settings
    cdn_base_url: str = ""
    cdn_key: str = ""
    
    # Common settings
    public_read: bool = True
    cache_control: str = "public, max-age=31536000"


@dataclass
class StoredObject:
    """Stored object metadata"""
    key: str
    url: str
    size_bytes: int
    content_type: str
    checksum: str
    backend: StorageBackend
    metadata: Dict[str, Any]
    created_at: Optional[str] = None


class StorageProvider(ABC):
    """Abstract base class for storage providers"""
    
    @abstractmethod
    def store(
        self,
        key: str,
        data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> StoredObject:
        """Store object"""
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Optional[bytes]:
        """Retrieve object"""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete object"""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if object exists"""
        pass
    
    @abstractmethod
    def get_url(self, key: str) -> str:
        """Get public URL for object"""
        pass
    
    @abstractmethod
    def list_objects(self, prefix: str = "") -> List[str]:
        """List objects with prefix"""
        pass


class LocalStorageProvider(StorageProvider):
    """Local filesystem storage"""
    
    def __init__(self, config: StorageConfig):
        self.base_path = config.local_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.public_url_base = "/images"
    
    def _get_path(self, key: str) -> Path:
        """Get filesystem path for key"""
        # Use first 2 chars of key as subdirectory
        prefix = key[:2] if len(key) >= 2 else key
        dir_path = self.base_path / prefix
        dir_path.mkdir(exist_ok=True)
        return dir_path / key
    
    def store(
        self,
        key: str,
        data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> StoredObject:
        """Store object locally"""
        path = self._get_path(key)
        path.write_bytes(data)
        
        # Store metadata if provided
        if metadata:
            meta_path = path.with_suffix('.meta.json')
            import json
            meta_path.write_text(json.dumps(metadata))
        
        checksum = hashlib.sha256(data).hexdigest()
        
        return StoredObject(
            key=key,
            url=self.get_url(key),
            size_bytes=len(data),
            content_type=content_type or 'application/octet-stream',
            checksum=checksum,
            backend=StorageBackend.LOCAL,
            metadata=metadata or {}
        )
    
    def retrieve(self, key: str) -> Optional[bytes]:
        """Retrieve object from local storage"""
        path = self._get_path(key)
        if path.exists():
            return path.read_bytes()
        return None
    
    def delete(self, key: str) -> bool:
        """Delete object from local storage"""
        path = self._get_path(key)
        meta_path = path.with_suffix('.meta.json')
        
        try:
            if path.exists():
                path.unlink()
            if meta_path.exists():
                meta_path.unlink()
            return True
        except IOError:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if object exists locally"""
        return self._get_path(key).exists()
    
    def get_url(self, key: str) -> str:
        """Get URL for local object"""
        prefix = key[:2] if len(key) >= 2 else key
        return f"{self.public_url_base}/{prefix}/{key}"
    
    def list_objects(self, prefix: str = "") -> List[str]:
        """List objects with prefix"""
        objects = []
        for subdir in self.base_path.iterdir():
            if subdir.is_dir():
                for file in subdir.iterdir():
                    if file.is_file() and not file.suffix == '.meta.json':
                        key = file.name
                        if key.startswith(prefix):
                            objects.append(key)
        return objects


class S3StorageProvider(StorageProvider):
    """AWS S3 storage provider"""
    
    def __init__(self, config: StorageConfig):
        if not S3_AVAILABLE:
            raise ImportError("boto3 is required for S3 storage")
        
        self.config = config
        
        # Initialize S3 client
        session_kwargs = {
            'aws_access_key_id': config.s3_access_key,
            'aws_secret_access_key': config.s3_secret_key,
            'region_name': config.s3_region
        }
        
        if config.s3_endpoint:
            session_kwargs['endpoint_url'] = config.s3_endpoint
        
        self.session = boto3.Session(**session_kwargs)
        self.s3 = self.session.client('s3')
        self.bucket = config.s3_bucket
    
    def store(
        self,
        key: str,
        data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> StoredObject:
        """Store object in S3"""
        full_key = f"{self.config.s3_prefix}/{key[:2]}/{key}"
        
        extra_args = {
            'CacheControl': self.config.cache_control
        }
        
        if content_type:
            extra_args['ContentType'] = content_type
        
        if metadata:
            extra_args['Metadata'] = {k: str(v) for k, v in metadata.items()}
        
        if self.config.public_read:
            extra_args['ACL'] = 'public-read'
        
        self.s3.put_object(
            Bucket=self.bucket,
            Key=full_key,
            Body=data,
            **extra_args
        )
        
        checksum = hashlib.sha256(data).hexdigest()
        
        return StoredObject(
            key=key,
            url=self.get_url(key),
            size_bytes=len(data),
            content_type=content_type or 'application/octet-stream',
            checksum=checksum,
            backend=StorageBackend.S3,
            metadata=metadata or {}
        )
    
    def retrieve(self, key: str) -> Optional[bytes]:
        """Retrieve object from S3"""
        full_key = f"{self.config.s3_prefix}/{key[:2]}/{key}"
        
        try:
            response = self.s3.get_object(Bucket=self.bucket, Key=full_key)
            return response['Body'].read()
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchKey':
                return None
            raise
    
    def delete(self, key: str) -> bool:
        """Delete object from S3"""
        full_key = f"{self.config.s3_prefix}/{key[:2]}/{key}"
        
        try:
            self.s3.delete_object(Bucket=self.bucket, Key=full_key)
            return True
        except ClientError:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if object exists in S3"""
        full_key = f"{self.config.s3_prefix}/{key[:2]}/{key}"
        
        try:
            self.s3.head_object(Bucket=self.bucket, Key=full_key)
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            raise
    
    def get_url(self, key: str) -> str:
        """Get URL for S3 object"""
        full_key = f"{self.config.s3_prefix}/{key[:2]}/{key}"
        
        if self.config.public_read:
            return f"https://{self.bucket}.s3.{self.config.s3_region}.amazonaws.com/{full_key}"
        else:
            # Generate presigned URL
            return self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': full_key},
                ExpiresIn=3600
            )
    
    def list_objects(self, prefix: str = "") -> List[str]:
        """List objects with prefix"""
        full_prefix = f"{self.config.s3_prefix}/{prefix}"
        
        paginator = self.s3.get_paginator('list_objects_v2')
        keys = []
        
        for page in paginator.paginate(Bucket=self.bucket, Prefix=full_prefix):
            for obj in page.get('Contents', []):
                key = obj['Key'].split('/')[-1]
                keys.append(key)
        
        return keys


class CDNStorageProvider(StorageProvider):
    """CDN-backed storage (uses S3 or other backend with CDN front)"""
    
    def __init__(self, config: StorageConfig, backend: StorageProvider):
        self.backend = backend
        self.cdn_base_url = config.cdn_base_url.rstrip('/')
    
    def store(
        self,
        key: str,
        data: bytes,
        content_type: Optional[str] = None,
        metadata: Optional[Dict] = None
    ) -> StoredObject:
        """Store object (delegates to backend)"""
        result = self.backend.store(key, data, content_type, metadata)
        
        # Override URL with CDN
        result.url = self.get_url(key)
        result.backend = StorageBackend.CDN
        
        return result
    
    def retrieve(self, key: str) -> Optional[bytes]:
        """Retrieve object (delegates to backend)"""
        return self.backend.retrieve(key)
    
    def delete(self, key: str) -> bool:
        """Delete object (delegates to backend)"""
        return self.backend.delete(key)
    
    def exists(self, key: str) -> bool:
        """Check if object exists (delegates to backend)"""
        return self.backend.exists(key)
    
    def get_url(self, key: str) -> str:
        """Get CDN URL for object"""
        prefix = key[:2] if len(key) >= 2 else key
        return f"{self.cdn_base_url}/{prefix}/{key}"
    
    def list_objects(self, prefix: str = "") -> List[str]:
        """List objects (delegates to backend)"""
        return self.backend.list_objects(prefix)
    
    def invalidate_cache(self, key: str) -> bool:
        """Invalidate CDN cache for key"""
        # Implementation depends on CDN provider
        # CloudFront, Cloudflare, etc.
        logger.info(f"Invalidating CDN cache for {key}")
        return True


class StorageManager:
    """
    Unified storage manager with multiple backend support
    """
    
    def __init__(self, config: Optional[StorageConfig] = None):
        self.config = config or StorageConfig()
        self.provider = self._create_provider()
    
    def _create_provider(self) -> StorageProvider:
        """Create storage provider based on config"""
        if self.config.backend == StorageBackend.LOCAL:
            return LocalStorageProvider(self.config)
        
        elif self.config.backend == StorageBackend.S3:
            return S3StorageProvider(self.config)
        
        elif self.config.backend == StorageBackend.CDN:
            # CDN uses S3 as backend
            s3_config = StorageConfig(
                backend=StorageBackend.S3,
                s3_bucket=self.config.s3_bucket,
                s3_region=self.config.s3_region,
                s3_access_key=self.config.s3_access_key,
                s3_secret_key=self.config.s3_secret_key
            )
            backend = S3StorageProvider(s3_config)
            return CDNStorageProvider(self.config, backend)
        
        else:
            raise ValueError(f"Unsupported storage backend: {self.config.backend}")
    
    def store_image(
        self,
        image_bytes: bytes,
        key: Optional[str] = None,
        format: str = "webp",
        metadata: Optional[Dict] = None
    ) -> StoredObject:
        """
        Store an image with auto-generated key if not provided
        
        Args:
            image_bytes: Image data
            key: Optional storage key
            format: Image format
            metadata: Optional metadata
            
        Returns:
            StoredObject with details
        """
        if key is None:
            # Generate key from content hash
            key = hashlib.sha256(image_bytes).hexdigest()[:32]
        
        key = f"{key}.{format}"
        
        content_type = f"image/{format}"
        
        return self.provider.store(key, image_bytes, content_type, metadata)
    
    def store_chart(
        self,
        chart_bytes: bytes,
        chart_type: str,
        chart_id: Optional[str] = None
    ) -> StoredObject:
        """
        Store a chart image with appropriate metadata
        
        Args:
            chart_bytes: Chart image data
            chart_type: Type of chart
            chart_id: Optional chart identifier
            
        Returns:
            StoredObject with details
        """
        key = chart_id or hashlib.sha256(chart_bytes).hexdigest()[:16]
        
        metadata = {
            'type': 'chart',
            'chart_type': chart_type,
            'generated_at': str(datetime.utcnow()),
            'source': 'ResilienceAI'
        }
        
        return self.store_image(chart_bytes, key, 'png', metadata)
    
    def get_image(self, key: str) -> Optional[bytes]:
        """Retrieve image by key"""
        return self.provider.retrieve(key)
    
    def delete_image(self, key: str) -> bool:
        """Delete image by key"""
        return self.provider.delete(key)
    
    def get_image_url(self, key: str) -> str:
        """Get public URL for image"""
        return self.provider.get_url(key)
    
    def image_exists(self, key: str) -> bool:
        """Check if image exists"""
        return self.provider.exists(key)


# Example usage
if __name__ == "__main__":
    from PIL import Image
    
    # Create test image
    img = Image.new('RGB', (800, 600), color='#3498db')
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    image_bytes = buffer.getvalue()
    
    # Configure local storage
    config = StorageConfig(
        backend=StorageBackend.LOCAL,
        local_path=Path('/tmp/resilience_images')
    )
    
    # Create storage manager
    storage = StorageManager(config)
    
    # Store image
    result = storage.store_image(image_bytes, format='png')
    print(f"Stored image:")
    print(f"  Key: {result.key}")
    print(f"  URL: {result.url}")
    print(f"  Size: {result.size_bytes} bytes")
    print(f"  Checksum: {result.checksum}")
    
    # Store chart
    chart_result = storage.store_chart(image_bytes, 'line', 'monthly_report')
    print(f"\nStored chart:")
    print(f"  Key: {chart_result.key}")
    print(f"  URL: {chart_result.url}")
    print(f"  Metadata: {chart_result.metadata}")
```

---

## 12. Performance Tuning

### 12.1 Performance Optimization Strategies

| Strategy | Implementation | Impact |
|----------|---------------|--------|
| **Lazy Loading** | Load images on demand | Reduced initial load time |
| **Progressive Enhancement** | Load low-res first, then high-res | Improved perceived performance |
| **Connection Pooling** | Reuse HTTP connections | Reduced latency |
| **Compression** | WebP/AVIF with quality optimization | 50-80% size reduction |
| **Caching** | Multi-layer cache (L1/L2/L3) | 90%+ cache hit rate |
| **CDN Distribution** | Edge caching | Reduced latency globally |
| **Lazy Generation** | Generate on first request | Reduced storage costs |
| **Pre-warming** | Generate common sizes upfront | Faster first access |

### 12.2 Performance Benchmarks

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/performance/benchmarks.py
"""
Performance benchmarks for image processing pipeline
"""

import time
import statistics
from typing import List, Dict, Any
from dataclasses import dataclass
import io

from PIL import Image


@dataclass
class BenchmarkResult:
    """Benchmark result"""
    operation: str
    iterations: int
    total_time_ms: float
    avg_time_ms: float
    min_time_ms: float
    max_time_ms: float
    throughput_per_sec: float
    memory_mb: float


class ImageBenchmark:
    """Benchmark image processing operations"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
    
    def run_benchmark(
        self,
        name: str,
        operation: callable,
        iterations: int = 100,
        warmup: int = 10
    ) -> BenchmarkResult:
        """
        Run benchmark for an operation
        
        Args:
            name: Benchmark name
            operation: Function to benchmark
            iterations: Number of iterations
            warmup: Warmup iterations
            
        Returns:
            BenchmarkResult
        """
        # Warmup
        for _ in range(warmup):
            operation()
        
        # Benchmark
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            operation()
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)
        
        result = BenchmarkResult(
            operation=name,
            iterations=iterations,
            total_time_ms=sum(times),
            avg_time_ms=statistics.mean(times),
            min_time_ms=min(times),
            max_time_ms=max(times),
            throughput_per_sec=1000 / statistics.mean(times),
            memory_mb=0  # Would need memory profiling
        )
        
        self.results.append(result)
        return result
    
    def print_results(self):
        """Print benchmark results"""
        print("\n" + "="*80)
        print("IMAGE PROCESSING BENCHMARKS")
        print("="*80)
        
        for r in self.results:
            print(f"\n{r.operation}:")
            print(f"  Iterations: {r.iterations}")
            print(f"  Total Time: {r.total_time_ms:.2f}ms")
            print(f"  Average: {r.avg_time_ms:.2f}ms")
            print(f"  Min: {r.min_time_ms:.2f}ms")
            print(f"  Max: {r.max_time_ms:.2f}ms")
            print(f"  Throughput: {r.throughput_per_sec:.1f} ops/sec")


def create_test_image(width: int, height: int) -> bytes:
    """Create test image"""
    img = Image.new('RGB', (width, height), color='#3498db')
    buffer = io.BytesIO()
    img.save(buffer, 'PNG')
    return buffer.getvalue()


# Run benchmarks
if __name__ == "__main__":
    benchmark = ImageBenchmark()
    
    # Test data
    test_image = create_test_image(1920, 1080)
    
    # Benchmark thumbnail generation
    from thumbnail.thumbnail_generator import ThumbnailGenerator, ThumbnailConfig
    
    generator = ThumbnailGenerator()
    config = ThumbnailConfig(width=300, height=200)
    
    def thumb_benchmark():
        generator.generate(test_image, config)
    
    result = benchmark.run_benchmark("Thumbnail Generation (1920x1080 -> 300x200)", 
                                      thumb_benchmark, iterations=50)
    
    # Benchmark optimization
    from optimizer.image_optimizer import ImageOptimizer
    
    optimizer = ImageOptimizer()
    
    def optimize_benchmark():
        optimizer.optimize(test_image, target_format='webp')
    
    result = benchmark.run_benchmark("Image Optimization (PNG -> WebP)", 
                                      optimize_benchmark, iterations=30)
    
    # Benchmark chart generation
    from image_generator.chart_generator import ChartImageGenerator, ChartConfig, ExportOptions
    
    chart_gen = ChartImageGenerator(ChartConfig(width=800, height=600))
    chart_data = {
        "labels": ["A", "B", "C", "D", "E"],
        "datasets": [{"label": "Test", "data": [10, 20, 15, 25, 30]}]
    }
    
    def chart_benchmark():
        chart_gen.generate_line_chart(chart_data, ExportOptions())
    
    result = benchmark.run_benchmark("Line Chart Generation (800x600)", 
                                      chart_benchmark, iterations=20)
    
    benchmark.print_results()
```

---

## 13. Testing Strategy

### 13.1 Test Coverage Plan

```python
# /mnt/okcomputer/output/resilience_ai_analysis/code/tests/test_image_processing.py
"""
Test suite for image processing components
"""

import unittest
import io
from pathlib import Path
from PIL import Image
import numpy as np


class TestChartGenerator(unittest.TestCase):
    """Test chart image generation"""
    
    def setUp(self):
        from image_generator.chart_generator import ChartImageGenerator, ChartConfig
        self.generator = ChartImageGenerator(ChartConfig(width=400, height=300))
        self.sample_data = {
            "labels": ["A", "B", "C"],
            "datasets": [{"label": "Test", "data": [10, 20, 15]}]
        }
    
    def test_line_chart_generation(self):
        """Test line chart generation"""
        from image_generator.chart_generator import ExportOptions
        
        image_bytes = self.generator.generate_line_chart(self.sample_data, ExportOptions())
        
        # Verify it's a valid image
        img = Image.open(io.BytesIO(image_bytes))
        self.assertEqual(img.format, 'PNG')
        self.assertEqual(img.width, 400)
        self.assertEqual(img.height, 300)
    
    def test_bar_chart_generation(self):
        """Test bar chart generation"""
        from image_generator.chart_generator import ExportOptions
        
        image_bytes = self.generator.generate_bar_chart(self.sample_data, ExportOptions())
        
        img = Image.open(io.BytesIO(image_bytes))
        self.assertEqual(img.format, 'PNG')
    
    def test_pie_chart_generation(self):
        """Test pie chart generation"""
        from image_generator.chart_generator import ExportOptions
        
        pie_data = {
            "labels": ["A", "B", "C"],
            "values": [30, 40, 30]
        }
        
        image_bytes = self.generator.generate_pie_chart(pie_data, ExportOptions())
        
        img = Image.open(io.BytesIO(image_bytes))
        self.assertEqual(img.format, 'PNG')
    
    def test_base64_conversion(self):
        """Test base64 encoding"""
        from image_generator.chart_generator import ExportOptions
        
        image_bytes = self.generator.generate_line_chart(self.sample_data, ExportOptions())
        base64_str = self.generator.to_base64(image_bytes)
        
        self.assertIsInstance(base64_str, str)
        self.assertGreater(len(base64_str), 0)


class TestImageOptimizer(unittest.TestCase):
    """Test image optimization"""
    
    def setUp(self):
        from optimizer.image_optimizer import ImageOptimizer
        self.optimizer = ImageOptimizer()
        
        # Create test image
        self.test_image = Image.new('RGB', (1000, 1000), color='#3498db')
        buffer = io.BytesIO()
        self.test_image.save(buffer, 'PNG')
        self.test_bytes = buffer.getvalue()
    
    def test_png_to_webp_conversion(self):
        """Test PNG to WebP conversion"""
        optimized, result = self.optimizer.optimize(
            self.test_bytes,
            target_format='webp'
        )
        
        self.assertTrue(result.success)
        self.assertLess(result.optimized_size, result.original_size)
        self.assertGreater(result.compression_ratio, 0)
    
    def test_jpeg_optimization(self):
        """Test JPEG optimization"""
        # Create JPEG first
        buffer = io.BytesIO()
        self.test_image.save(buffer, 'JPEG', quality=95)
        jpeg_bytes = buffer.getvalue()
        
        optimized, result = self.optimizer.optimize(
            jpeg_bytes,
            target_format='jpeg'
        )
        
        self.assertTrue(result.success)
    
    def test_batch_optimization(self):
        """Test batch optimization"""
        images = [self.test_bytes] * 5
        
        results = self.optimizer.batch_optimize(images, max_workers=2)
        
        self.assertEqual(len(results), 5)
        self.assertTrue(all(r[1].success for r in results))


class TestThumbnailGenerator(unittest.TestCase):
    """Test thumbnail generation"""
    
    def setUp(self):
        from thumbnail.thumbnail_generator import ThumbnailGenerator
        self.generator = ThumbnailGenerator()
        
        # Create test image
        self.test_image = Image.new('RGB', (1920, 1080), color='#3498db')
        buffer = io.BytesIO()
        self.test_image.save(buffer, 'PNG')
        self.test_bytes = buffer.getvalue()
    
    def test_fit_strategy(self):
        """Test FIT thumbnail strategy"""
        from thumbnail.thumbnail_generator import ThumbnailConfig, ThumbnailStrategy
        
        config = ThumbnailConfig(
            width=200,
            height=200,
            strategy=ThumbnailStrategy.FIT
        )
        
        result = self.generator.generate(self.test_bytes, config)
        
        self.assertLessEqual(result.width, 200)
        self.assertLessEqual(result.height, 200)
        self.assertGreater(len(result.image_bytes), 0)
    
    def test_fill_strategy(self):
        """Test FILL thumbnail strategy"""
        from thumbnail.thumbnail_generator import ThumbnailConfig, ThumbnailStrategy
        
        config = ThumbnailConfig(
            width=200,
            height=200,
            strategy=ThumbnailStrategy.FILL
        )
        
        result = self.generator.generate(self.test_bytes, config)
        
        self.assertEqual(result.width, 200)
        self.assertEqual(result.height, 200)
    
    def test_thumbnail_set_generation(self):
        """Test generating multiple thumbnail sizes"""
        sizes = [(100, 100), (200, 200), (400, 400)]
        
        results = self.generator.generate_set(self.test_bytes, sizes)
        
        self.assertEqual(len(results), 3)
        self.assertIn('100x100', results)
        self.assertIn('200x200', results)
        self.assertIn('400x400', results)


class TestCache(unittest.TestCase):
    """Test caching system"""
    
    def setUp(self):
        from cache.image_cache import MultiLayerCache, CacheConfig
        
        config = CacheConfig(
            l1_max_size_mb=10,
            l2_enabled=False,
            l3_path='/tmp/test_cache'
        )
        self.cache = MultiLayerCache(config)
        self.test_data = b"test image data" * 100
    
    def test_cache_set_and_get(self):
        """Test basic cache operations"""
        key = "test_key"
        
        # Set
        self.cache.set(key, self.test_data)
        
        # Get
        retrieved = self.cache.get(key)
        
        self.assertEqual(retrieved, self.test_data)
    
    def test_cache_miss(self):
        """Test cache miss"""
        retrieved = self.cache.get("nonexistent_key")
        
        self.assertIsNone(retrieved)
    
    def test_cache_stats(self):
        """Test cache statistics"""
        self.cache.set("key1", self.test_data)
        self.cache.get("key1")
        self.cache.get("key1")
        self.cache.get("nonexistent")
        
        stats = self.cache.get_all_stats()
        
        self.assertIn('l1', stats)
        self.assertIn('l3', stats)


class TestStorage(unittest.TestCase):
    """Test storage system"""
    
    def setUp(self):
        from storage.storage_manager import StorageManager, StorageConfig, StorageBackend
        
        config = StorageConfig(
            backend=StorageBackend.LOCAL,
            local_path=Path('/tmp/test_storage')
        )
        self.storage = StorageManager(config)
        self.test_image = b"test image data"
    
    def test_store_and_retrieve(self):
        """Test store and retrieve operations"""
        result = self.storage.store_image(self.test_image, key="test_img", format="png")
        
        retrieved = self.storage.get_image(result.key)
        
        self.assertEqual(retrieved, self.test_image)
    
    def test_store_chart(self):
        """Test chart storage"""
        result = self.storage.store_chart(self.test_image, "line", "test_chart")
        
        self.assertEqual(result.metadata.get('type'), 'chart')
        self.assertEqual(result.metadata.get('chart_type'), 'line')
    
    def test_exists(self):
        """Test existence check"""
        result = self.storage.store_image(self.test_image, format="png")
        
        self.assertTrue(self.storage.image_exists(result.key))
        self.assertFalse(self.storage.image_exists("nonexistent"))


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestChartGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestImageOptimizer))
    suite.addTests(loader.loadTestsFromTestCase(TestThumbnailGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestCache))
    suite.addTests(loader.loadTestsFromTestCase(TestStorage))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
```

---

## 14. Implementation Priority

### 14.1 Priority Matrix

| Component | Priority | Effort | Impact | Dependencies |
|-----------|----------|--------|--------|--------------|
| **Chart Generator** | P0 | Medium | High | None |
| **Image Optimizer** | P0 | Low | High | None |
| **Thumbnail Generator** | P0 | Low | High | None |
| **Format Converter** | P0 | Low | Medium | None |
| **L1 Memory Cache** | P0 | Low | High | None |
| **Export API** | P1 | Medium | High | Chart Generator |
| **L3 Disk Cache** | P1 | Low | Medium | None |
| **Batch Processor** | P1 | Medium | Medium | Optimizer |
| **Local Storage** | P1 | Low | Medium | None |
| **Responsive Images** | P2 | Medium | Medium | Thumbnail Generator |
| **Metadata Manager** | P2 | Medium | Low | None |
| **L2 Redis Cache** | P2 | Medium | Medium | None |
| **S3 Storage** | P2 | Medium | Medium | None |
| **CDN Integration** | P3 | High | Medium | S3 Storage |
| **HTML Renderer** | P3 | High | Low | None |

### 14.2 Implementation Roadmap

**Phase 1 (Week 1-2): Core Generation**
- Chart Image Generator
- Visualization Generator
- Basic Export API

**Phase 2 (Week 3-4): Optimization**
- Image Optimizer
- Format Converter
- Thumbnail Generator

**Phase 3 (Week 5-6): Caching & Storage**
- L1 Memory Cache
- L3 Disk Cache
- Local Storage Provider

**Phase 4 (Week 7-8): Advanced Features**
- Batch Processor
- Responsive Image Handler
- Metadata Manager

**Phase 5 (Week 9-10): Scale & Polish**
- L2 Redis Cache
- S3 Storage
- CDN Integration
- Performance Tuning

### 14.3 File Structure

```
/mnt/okcomputer/output/resilience_ai_analysis/code/
├── image_generator/
│   ├── __init__.py
│   ├── chart_generator.py
│   ├── visualization_generator.py
│   └── templates/
├── optimizer/
│   ├── __init__.py
│   ├── image_optimizer.py
│   └── format_converter.py
├── thumbnail/
│   ├── __init__.py
│   └── thumbnail_generator.py
├── cache/
│   ├── __init__.py
│   └── image_cache.py
├── storage/
│   ├── __init__.py
│   └── storage_manager.py
├── metadata/
│   ├── __init__.py
│   └── metadata_manager.py
├── responsive/
│   ├── __init__.py
│   └── responsive_handler.py
├── batch/
│   ├── __init__.py
│   └── batch_processor.py
├── api/
│   ├── __init__.py
│   └── export_api.py
├── performance/
│   └── benchmarks.py
└── tests/
    └── test_image_processing.py
```

---

## Summary

This comprehensive image processing architecture for ResilienceAI provides:

1. **Multi-format Generation**: Charts, visualizations, and thumbnails in PNG, JPEG, WebP, SVG, PDF
2. **Intelligent Optimization**: Format-specific optimization with quality control
3. **Flexible Thumbnails**: 5 strategies (fit, fill, pad, smart crop, entropy)
4. **Multi-layer Caching**: L1 (memory), L2 (Redis), L3 (disk) for optimal performance
5. **RESTful API**: Complete export endpoints with async batch processing
6. **Responsive Images**: Automatic srcset generation for optimal delivery
7. **Metadata Management**: EXIF, XMP, and custom metadata handling
8. **Multi-backend Storage**: Local, S3, CDN support
9. **Performance Focus**: Benchmarking and optimization strategies
10. **Comprehensive Testing**: Unit tests for all components

**Key Metrics:**
- Target cache hit rate: >90%
- Image compression: 50-80% size reduction
- Thumbnail generation: <100ms for typical images
- Chart generation: <500ms for complex charts
- API response time: <200ms p95

---

*Document generated for ResilienceAI Image Processing Architecture*
*Version 1.0 - Implementation Ready*
