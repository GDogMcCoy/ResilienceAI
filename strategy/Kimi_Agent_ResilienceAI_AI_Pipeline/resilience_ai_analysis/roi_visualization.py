"""
ResilienceAI - ROI Visualization Module
Interactive visualizations for ROI analysis results.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple, Any
import warnings

# Try to import visualization libraries
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    warnings.warn("Plotly not available. Visualizations will be limited.")

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


class ROIVisualizer:
    """
    Create interactive ROI visualizations.

    Supports:
    - ROI heatmaps
    - Cost-effectiveness planes
    - Tornado diagrams
    - Budget allocation charts
    - Uncertainty distributions
    """

    def __init__(self, data: pd.DataFrame = None):
        """
        Initialize ROI visualizer.

        Args:
            data: ROI data DataFrame
        """
        self.data = data

    def create_roi_heatmap(
        self,
        row_col: str = "county_name",
        col_col: str = "intervention",
        value_col: str = "roi_score",
        title: str = "ROI Score by County and Intervention"
    ) -> Optional[Any]:
        """
        Create ROI heatmap.

        Args:
            row_col: Column for rows
            col_col: Column for columns
            value_col: Column for values
            title: Chart title

        Returns:
            Plotly figure or None
        """
        if not PLOTLY_AVAILABLE or self.data is None:
            return None

        pivot = self.data.pivot(index=row_col, columns=col_col, values=value_col)

        fig = px.imshow(
            pivot,
            labels=dict(x="Intervention", y="County", color="ROI Score"),
            x=pivot.columns,
            y=pivot.index,
            color_continuous_scale="RdYlGn",
            aspect="auto",
            title=title
        )

        fig.update_traces(
            hovertemplate="County: %{y}<br>Intervention: %{x}<br>ROI: %{z:.2f}"
        )

        return fig

    def create_cost_effectiveness_plane(
        self,
        cost_col: str = "cost",
        effectiveness_col: str = "effectiveness",
        label_col: str = "name",
        wtp_thresholds: Optional[List[float]] = None
    ) -> Optional[Any]:
        """
        Create cost-effectiveness plane.

        Args:
            cost_col: Cost column
            effectiveness_col: Effectiveness column
            label_col: Label column
            wtp_thresholds: WTP threshold lines to draw

        Returns:
            Plotly figure or None
        """
        if not PLOTLY_AVAILABLE or self.data is None:
            return None

        if wtp_thresholds is None:
            wtp_thresholds = [30_000, 50_000, 100_000]

        fig = go.Figure()

        # Add interventions
        fig.add_trace(go.Scatter(
            x=self.data[effectiveness_col],
            y=self.data[cost_col],
            mode='markers+text',
            text=self.data[label_col],
            textposition="top center",
            marker=dict(
                size=12,
                color=self.data[cost_col] / self.data[effectiveness_col],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="ICER")
            ),
            name="Interventions"
        ))

        # Add WTP lines
        x_max = self.data[effectiveness_col].max() * 1.1
        for wtp in wtp_thresholds:
            fig.add_trace(go.Scatter(
                x=[0, x_max],
                y=[0, x_max * wtp],
                mode='lines',
                line=dict(dash='dash', width=1),
                name=f"WTP = ${wtp:,.0f}"
            ))

        fig.update_layout(
            title="Cost-Effectiveness Plane",
            xaxis_title="Effectiveness (units)",
            yaxis_title="Cost ($)",
            showlegend=True
        )

        return fig

    def create_tornado_diagram(
        self,
        sensitivity_data: pd.DataFrame,
        parameter_col: str = "parameter",
        low_col: str = "npv_low",
        high_col: str = "npv_high",
        base_npv: float = 0
    ) -> Optional[Any]:
        """
        Create tornado diagram for sensitivity analysis.

        Args:
            sensitivity_data: Sensitivity analysis results
            parameter_col: Parameter name column
            low_col: Low value column
            high_col: High value column
            base_npv: Base case NPV

        Returns:
            Plotly figure or None
        """
        if not PLOTLY_AVAILABLE:
            return None

        # Sort by swing magnitude
        sensitivity_data = sensitivity_data.copy()
        sensitivity_data["swing"] = (
            sensitivity_data[high_col] - sensitivity_data[low_col]
        ).abs()
        sensitivity_data = sensitivity_data.sort_values("swing", ascending=True)

        fig = go.Figure()

        # Low values (left side)
        fig.add_trace(go.Bar(
            y=sensitivity_data[parameter_col],
            x=sensitivity_data[low_col] - base_npv,
            orientation='h',
            name='Low Value',
            marker_color='red'
        ))

        # High values (right side)
        fig.add_trace(go.Bar(
            y=sensitivity_data[parameter_col],
            x=sensitivity_data[high_col] - base_npv,
            orientation='h',
            name='High Value',
            marker_color='green'
        ))

        # Add base line
        fig.add_vline(x=0, line_width=2, line_color="black")

        fig.update_layout(
            title="Tornado Diagram - Sensitivity Analysis",
            xaxis_title="Impact on NPV ($)",
            yaxis_title="Parameter",
            barmode='overlay',
            showlegend=True
        )

        return fig

    def create_budget_allocation_sunburst(
        self,
        allocation_data: Dict
    ) -> Optional[Any]:
        """
        Create sunburst chart for budget allocation.

        Args:
            allocation_data: Allocation result dictionary

        Returns:
            Plotly figure or None
        """
        if not PLOTLY_AVAILABLE:
            return None

        selected = allocation_data.get("selected_items", [])

        labels = ["Total Budget"]
        parents = [""]
        values = [allocation_data.get("total_cost", 0)]

        for item in selected:
            labels.append(item.get("name", "Unknown"))
            parents.append("Total Budget")
            values.append(item.get("cost", 0))

        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total"
        ))

        fig.update_layout(
            title="Budget Allocation",
            margin=dict(t=50, l=0, r=0, b=0)
        )

        return fig

    def create_uncertainty_distribution(
        self,
        simulation_results: pd.DataFrame,
        metric_col: str = "npv",
        title: str = "Uncertainty Distribution"
    ) -> Optional[Any]:
        """
        Create histogram of uncertainty distribution.

        Args:
            simulation_results: Monte Carlo simulation results
            metric_col: Metric column to visualize
            title: Chart title

        Returns:
            Plotly figure or None
        """
        if not PLOTLY_AVAILABLE:
            return None

        values = simulation_results[metric_col].dropna()

        # Calculate statistics
        mean = values.mean()
        median = values.median()
        ci_low = values.quantile(0.025)
        ci_high = values.quantile(0.975)

        fig = go.Figure()

        # Histogram
        fig.add_trace(go.Histogram(
            x=values,
            nbinsx=50,
            name="Distribution",
            opacity=0.7
        ))

        # Mean line
        fig.add_vline(x=mean, line_width=2, line_color="red", 
                     annotation_text=f"Mean: ${mean:,.0f}")

        # Median line
        fig.add_vline(x=median, line_width=2, line_color="green",
                     annotation_text=f"Median: ${median:,.0f}")

        # 95% CI
        fig.add_vrect(x0=ci_low, x1=ci_high, 
                     fillcolor="blue", opacity=0.1,
                     annotation_text="95% CI")

        fig.update_layout(
            title=title,
            xaxis_title=metric_col.upper(),
            yaxis_title="Frequency",
            showlegend=False
        )

        return fig

    def create_efficiency_frontier(
        self,
        interventions: pd.DataFrame,
        cost_col: str = "cost",
        effectiveness_col: str = "effectiveness",
        label_col: str = "name"
    ) -> Optional[Any]:
        """
        Create efficiency frontier plot.

        Args:
            interventions: Interventions DataFrame
            cost_col: Cost column
            effectiveness_col: Effectiveness column
            label_col: Label column

        Returns:
            Plotly figure or None
        """
        if not PLOTLY_AVAILABLE:
            return None

        # Sort by cost
        sorted_data = interventions.sort_values(cost_col)

        # Find efficient points
        efficient_points = []
        max_effectiveness = 0

        for _, row in sorted_data.iterrows():
            if row[effectiveness_col] > max_effectiveness:
                efficient_points.append(row)
                max_effectiveness = row[effectiveness_col]

        efficient_df = pd.DataFrame(efficient_points)

        fig = go.Figure()

        # All points
        fig.add_trace(go.Scatter(
            x=interventions[effectiveness_col],
            y=interventions[cost_col],
            mode='markers',
            name='All Interventions',
            marker=dict(size=10, color='lightblue')
        ))

        # Efficient frontier
        if len(efficient_df) > 0:
            fig.add_trace(go.Scatter(
                x=efficient_df[effectiveness_col],
                y=efficient_df[cost_col],
                mode='lines+markers',
                name='Efficient Frontier',
                line=dict(color='red', width=2),
                marker=dict(size=12, color='red')
            ))

        fig.update_layout(
            title="Cost-Effectiveness Efficiency Frontier",
            xaxis_title="Effectiveness",
            yaxis_title="Cost ($)",
            showlegend=True
        )

        return fig

    def create_roi_dashboard_components(
        self,
        optimization_result: Dict,
        sensitivity_data: pd.DataFrame,
        simulation_results: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Create all dashboard components.

        Args:
            optimization_result: Optimization results
            sensitivity_data: Sensitivity analysis data
            simulation_results: Monte Carlo simulation results

        Returns:
            Dictionary of visualization components
        """
        components = {}

        # Budget allocation
        components["budget_allocation"] = self.create_budget_allocation_sunburst(
            optimization_result
        )

        # Tornado diagram
        components["tornado"] = self.create_tornado_diagram(sensitivity_data)

        # Uncertainty distribution
        components["uncertainty"] = self.create_uncertainty_distribution(
            simulation_results
        )

        # Efficiency frontier
        if self.data is not None:
            components["frontier"] = self.create_efficiency_frontier(self.data)

        return components


class ReportGenerator:
    """Generate ROI analysis reports."""

    def generate_executive_summary(
        self,
        optimization_result: Dict,
        budget: float,
        timeframe: int
    ) -> str:
        """Generate executive summary report."""

        report = f"""# Intervention ROI Analysis - Executive Summary

## Key Findings

| Metric | Value |
|--------|-------|
| Total Budget | ${budget:,.0f} |
| Timeframe | {timeframe} years |
| Total Investment | ${optimization_result.get('total_cost', 0):,.0f} |
| Total Benefit | {optimization_result.get('total_benefit', 0):,.0f} units |
| Budget Utilization | {optimization_result.get('budget_utilization', 0):.1%} |
| Optimization Algorithm | {optimization_result.get('algorithm', 'N/A')} |

## Selected Interventions

"""

        for i, item in enumerate(optimization_result.get('selected_items', [])[:10], 1):
            report += f"{i}. **{item.get('name', 'Unknown')}**"
            report += f" - Cost: ${item.get('cost', 0):,.0f}"
            report += f", Benefit: {item.get('benefit', 0):.0f}\n"

        return report

    def generate_detailed_report(
        self,
        county_analysis: pd.DataFrame,
        intervention_analysis: pd.DataFrame,
        sensitivity_results: pd.DataFrame
    ) -> str:
        """Generate detailed technical report."""

        report = """# Detailed ROI Analysis Report

## County-Level Analysis

"""
        report += county_analysis.to_markdown()

        report += """

## Intervention Analysis

"""
        report += intervention_analysis.to_markdown()

        report += """

## Sensitivity Analysis

"""
        report += sensitivity_results.to_markdown()

        return report


# Utility functions for matplotlib fallback
def create_tornado_matplotlib(
    sensitivity_data: pd.DataFrame,
    base_npv: float = 0
) -> Optional[Any]:
    """Create tornado diagram using matplotlib."""
    if not MATPLOTLIB_AVAILABLE:
        return None

    fig, ax = plt.subplots(figsize=(10, 6))

    parameters = sensitivity_data["parameter"].values
    low_values = sensitivity_data["npv_low"].values - base_npv
    high_values = sensitivity_data["npv_high"].values - base_npv

    y_pos = np.arange(len(parameters))

    # Plot bars
    ax.barh(y_pos, low_values, color='red', alpha=0.7, label='Low Value')
    ax.barh(y_pos, high_values, color='green', alpha=0.7, label='High Value')

    ax.set_yticks(y_pos)
    ax.set_yticklabels(parameters)
    ax.axvline(x=0, color='black', linewidth=2)
    ax.set_xlabel('Impact on NPV ($)')
    ax.set_title('Tornado Diagram - Sensitivity Analysis')
    ax.legend()

    plt.tight_layout()
    return fig


if __name__ == "__main__":
    # Example usage
    data = pd.DataFrame({
        "name": ["Hospital", "EMS", "Fire", "Telehealth", "Prep"],
        "cost": [50_000_000, 2_000_000, 3_000_000, 250_000, 500_000],
        "effectiveness": [100, 30, 25, 20, 35],
        "roi_score": [85, 75, 70, 90, 80]
    })

    visualizer = ROIVisualizer(data)

    # Create cost-effectiveness plane
    fig = visualizer.create_cost_effectiveness_plane()
    if fig:
        fig.write_html("/mnt/okcomputer/output/resilience_ai_analysis/ce_plane.html")
        print("Created ce_plane.html")
