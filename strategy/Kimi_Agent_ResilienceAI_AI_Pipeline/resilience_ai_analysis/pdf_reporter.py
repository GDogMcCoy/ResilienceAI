"""
ResilienceAI - PDF Report Generator
Generate professional PDF reports from vulnerability data
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from io import BytesIO
import base64
from config import PROCESSED_DIR, REPORTS_DIR, FIGURES_DIR

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib.colors import HexColor, black, white, grey
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image, ListFlowable, ListItem, KeepTogether
    )
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.graphics.charts.linecharts import HorizontalLineChart
    HAS_REPORTLAB = True
except ImportError:
    HAS_REPORTLAB = False

try:
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.use('Agg')
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


class PDFReporter:
    """Generate professional PDF reports"""
    
    # Color scheme
    COLORS = {
        'primary': HexColor('#1e3c72'),
        'secondary': HexColor('#2a5298'),
        'accent': HexColor('#ffc107'),
        'success': HexColor('#28a745'),
        'warning': HexColor('#ffc107'),
        'danger': HexColor('#dc3545'),
        'text': HexColor('#333333'),
        'light': HexColor('#f8f9fa'),
        'border': HexColor('#dee2e6')
    }
    
    # Risk colors
    RISK_COLORS = {
        'High': HexColor('#dc3545'),
        'Medium': HexColor('#ffc107'),
        'Low': HexColor('#28a745'),
        'Critical': HexColor('#721c24')
    }
    
    def __init__(self, df=None):
        """Initialize reporter with county data"""
        if df is None:
            path = PROCESSED_DIR / "county_features.csv"
            if path.exists():
                self.df = pd.read_csv(path, dtype={"fips": str})
            else:
                self.df = None
        else:
            self.df = df
        
        self.styles = self._create_styles()
    
    def _create_styles(self):
        """Create paragraph styles"""
        styles = getSampleStyleSheet()
        
        # Custom styles
        styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=self.COLORS['primary'],
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='CustomSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            textColor=grey,
            alignment=TA_CENTER,
            spaceAfter=20
        ))
        
        styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=self.COLORS['primary'],
            spaceAfter=12,
            spaceBefore=20
        ))
        
        styles.add(ParagraphStyle(
            name='SubSectionHeader',
            parent=styles['Heading3'],
            fontSize=13,
            textColor=self.COLORS['secondary'],
            spaceAfter=10,
            spaceBefore=15
        ))
        
        styles.add(ParagraphStyle(
            name='BodyText',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            spaceAfter=10
        ))
        
        styles.add(ParagraphStyle(
            name='TableHeader',
            parent=styles['Normal'],
            fontSize=9,
            textColor=white,
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='TableCell',
            parent=styles['Normal'],
            fontSize=8,
            alignment=TA_LEFT
        ))
        
        styles.add(ParagraphStyle(
            name='MetricValue',
            parent=styles['Normal'],
            fontSize=20,
            textColor=self.COLORS['primary'],
            alignment=TA_CENTER
        ))
        
        styles.add(ParagraphStyle(
            name='MetricLabel',
            parent=styles['Normal'],
            fontSize=9,
            textColor=grey,
            alignment=TA_CENTER
        ))
        
        return styles
    
    def generate_executive_report(
        self,
        output_path: str = None,
        filters: Dict[str, Any] = None,
        include_charts: bool = True
    ) -> Dict:
        """
        Generate executive briefing report
        
        Args:
            output_path: Output file path
            filters: Filters to apply
            include_charts: Include charts in report
            
        Returns:
            Dictionary with report metadata
        """
        if not HAS_REPORTLAB:
            return {"error": "reportlab not installed. Run: pip install reportlab"}
        
        if self.df is None:
            return {"error": "Data not loaded"}
        
        # Apply filters
        df = self.df.copy()
        if filters:
            df = self._apply_filters(df, filters)
        
        # Create output path
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = REPORTS_DIR / f"executive_report_{timestamp}.pdf"
        
        # Create document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        
        # Build story
        story = []
        
        # Title page
        story.extend(self._build_title_page("Executive Briefing", "Disaster Vulnerability Assessment"))
        story.append(PageBreak())
        
        # Executive Summary
        story.extend(self._build_executive_summary(df))
        story.append(PageBreak())
        
        # Key Metrics
        story.extend(self._build_key_metrics(df))
        
        # Risk Distribution
        story.extend(self._build_risk_distribution(df, include_charts))
        story.append(PageBreak())
        
        # Top Risk Counties
        story.extend(self._build_top_counties(df))
        story.append(PageBreak())
        
        # Infrastructure Analysis
        story.extend(self._build_infrastructure_analysis(df))
        
        # Recommendations
        story.extend(self._build_recommendations(df))
        
        # Build PDF
        doc.build(story)
        
        return {
            "output_path": str(output_path),
            "page_count": len(story) // 5,  # Approximate
            "row_count": len(df)
        }
    
    def generate_county_profile(
        self,
        fips: str,
        output_path: str = None
    ) -> Dict:
        """
        Generate detailed county profile report
        
        Args:
            fips: County FIPS code
            output_path: Output file path
            
        Returns:
            Dictionary with report metadata
        """
        if not HAS_REPORTLAB:
            return {"error": "reportlab not installed"}
        
        county_data = self.df[self.df['fips'] == fips]
        if county_data.empty:
            return {"error": f"County {fips} not found"}
        
        county = county_data.iloc[0]
        
        if output_path is None:
            output_path = REPORTS_DIR / f"county_profile_{fips}.pdf"
        
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=letter,
            rightMargin=0.75*inch,
            leftMargin=0.75*inch,
            topMargin=1*inch,
            bottomMargin=1*inch
        )
        
        story = []
        
        # Title
        story.extend(self._build_title_page(
            county['county_name'],
            "County Vulnerability Profile"
        ))
        story.append(PageBreak())
        
        # Overview
        story.append(Paragraph("County Overview", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.2*inch))
        
        overview_data = [
            ['FIPS Code', str(county['fips'])],
            ['Risk Score', f"{county['risk_score']:.3f}"],
            ['Risk Level', county['risk_level']],
            ['Population', f"{int(county['total_population']):,}"],
        ]
        
        if 'vulnerability_index' in county:
            overview_data.append(['Vulnerability Index', f"{county['vulnerability_index']:.3f}"])
        if 'isolation_index' in county:
            overview_data.append(['Isolation Index', f"{county['isolation_index']:.3f}"])
        
        overview_table = Table(overview_data, colWidths=[2.5*inch, 3*inch])
        overview_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), self.COLORS['light']),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLORS['text']),
            ('ALIGN', (0, 0), (0, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, self.COLORS['border']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(overview_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Demographics
        if any(c in county for c in ['poverty_pct', 'elderly_pct', 'disability_pct']):
            story.append(Paragraph("Demographics", self.styles['SectionHeader']))
            demo_data = [['Indicator', 'Value']]
            
            if 'poverty_pct' in county:
                demo_data.append(['Poverty Rate', f"{county['poverty_pct']:.1f}%"])
            if 'elderly_pct' in county:
                demo_data.append(['Elderly Population', f"{county['elderly_pct']:.1f}%"])
            if 'disability_pct' in county:
                demo_data.append(['Disability Rate', f"{county['disability_pct']:.1f}%"])
            if 'uninsured_pct' in county:
                demo_data.append(['Uninsured Rate', f"{county['uninsured_pct']:.1f}%"])
            
            demo_table = Table(demo_data, colWidths=[2.5*inch, 3*inch])
            demo_table.setStyle(self._get_table_style())
            story.append(demo_table)
            story.append(Spacer(1, 0.3*inch))
        
        # Infrastructure
        story.append(Paragraph("Infrastructure Access", self.styles['SectionHeader']))
        infra_data = [['Facility Type', 'Distance (km)', 'Count Within 50km']]
        
        infra_cols = [
            ('dist_nearest_hospitals_km', 'count_hospitals_50km', 'Hospital'),
            ('dist_nearest_fire_stations_km', 'count_fire_stations_50km', 'Fire Station'),
            ('dist_nearest_ems_stations_km', 'count_ems_stations_50km', 'EMS Station'),
        ]
        
        for dist_col, count_col, name in infra_cols:
            if dist_col in county:
                dist = f"{county[dist_col]:.1f}" if pd.notna(county[dist_col]) else 'N/A'
                count = int(county[count_col]) if count_col in county and pd.notna(county[count_col]) else 0
                infra_data.append([name, dist, count])
        
        infra_table = Table(infra_data, colWidths=[2*inch, 1.5*inch, 2*inch])
        infra_table.setStyle(self._get_table_style())
        story.append(infra_table)
        
        # Build PDF
        doc.build(story)
        
        return {
            "output_path": str(output_path),
            "county": county['county_name'],
            "fips": fips
        }
    
    def _build_title_page(self, title: str, subtitle: str) -> List:
        """Build title page elements"""
        elements = []
        
        # Spacer for vertical centering
        elements.append(Spacer(1, 2*inch))
        
        # Logo placeholder (would use actual image)
        elements.append(Paragraph("RESILIENCEAI", ParagraphStyle(
            name='Logo',
            fontSize=36,
            textColor=self.COLORS['primary'],
            alignment=TA_CENTER,
            spaceAfter=30
        )))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Title
        elements.append(Paragraph(title, self.styles['CustomTitle']))
        
        # Subtitle
        elements.append(Paragraph(subtitle, self.styles['CustomSubtitle']))
        
        elements.append(Spacer(1, 0.5*inch))
        
        # Date
        elements.append(Paragraph(
            datetime.now().strftime('%B %d, %Y'),
            ParagraphStyle(
                name='Date',
                fontSize=12,
                textColor=grey,
                alignment=TA_CENTER
            )
        ))
        
        elements.append(Spacer(1, 2*inch))
        
        # Footer
        elements.append(Paragraph(
            "Confidential - For Internal Use Only",
            ParagraphStyle(
                name='Footer',
                fontSize=9,
                textColor=grey,
                alignment=TA_CENTER
            )
        ))
        
        return elements
    
    def _build_executive_summary(self, df: pd.DataFrame) -> List:
        """Build executive summary section"""
        elements = []
        
        elements.append(Paragraph("Executive Summary", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        summary_text = f"""
        This report provides a comprehensive analysis of disaster vulnerability across 
        <b>{len(df):,} counties</b>. The analysis identifies <b>{(df['risk_score'] >= 0.7).sum()} high-risk counties</b> 
        requiring immediate attention and intervention.
        """
        
        elements.append(Paragraph(summary_text, self.styles['BodyText']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Key findings
        elements.append(Paragraph("Key Findings:", self.styles['SubSectionHeader']))
        
        findings = []
        
        # Risk distribution
        risk_dist = df['risk_level'].value_counts()
        for level in ['High', 'Medium', 'Low']:
            if level in risk_dist:
                findings.append(f"{risk_dist[level]} counties ({risk_dist[level]/len(df)*100:.1f}%) at {level} risk")
        
        # Infrastructure gaps
        if 'zero_redundancy_flag' in df.columns:
            zero_redundancy = df['zero_redundancy_flag'].sum()
            if zero_redundancy > 0:
                findings.append(f"{int(zero_redundancy)} counties with zero infrastructure redundancy")
        
        # Compound risk
        if 'compound_risk_flag' in df.columns:
            compound_risk = df['compound_risk_flag'].sum()
            if compound_risk > 0:
                findings.append(f"{int(compound_risk)} counties with compound risk factors")
        
        for finding in findings:
            elements.append(Paragraph(f"• {finding}", self.styles['BodyText']))
        
        return elements
    
    def _build_key_metrics(self, df: pd.DataFrame) -> List:
        """Build key metrics section"""
        elements = []
        
        elements.append(Paragraph("Key Metrics", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Create metrics grid
        metrics = [
            ('Total Counties', f"{len(df):,}"),
            ('High Risk', f"{(df['risk_score'] >= 0.7).sum():,}"),
            ('Avg Risk Score', f"{df['risk_score'].mean():.3f}"),
            ('Population at Risk', f"{df[df['risk_score'] >= 0.7]['total_population'].sum():,}"),
        ]
        
        # Create table for metrics
        metric_data = []
        for i in range(0, len(metrics), 2):
            row = []
            for j in range(2):
                if i + j < len(metrics):
                    label, value = metrics[i + j]
                    row.extend([value, label])
                else:
                    row.extend(['', ''])
            metric_data.append(row)
        
        metric_table = Table(metric_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 1.5*inch])
        metric_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),
            ('ALIGN', (2, 0), (2, -1), 'CENTER'),
            ('FONTSIZE', (0, 0), (0, -1), 18),
            ('FONTSIZE', (2, 0), (2, -1), 18),
            ('TEXTCOLOR', (0, 0), (0, -1), self.COLORS['primary']),
            ('TEXTCOLOR', (2, 0), (2, -1), self.COLORS['primary']),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (1, 0), (1, -1), 9),
            ('FONTSIZE', (3, 0), (3, -1), 9),
            ('TEXTCOLOR', (1, 0), (1, -1), grey),
            ('TEXTCOLOR', (3, 0), (3, -1), grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ]))
        
        elements.append(metric_table)
        elements.append(Spacer(1, 0.3*inch))
        
        return elements
    
    def _build_risk_distribution(self, df: pd.DataFrame, include_charts: bool) -> List:
        """Build risk distribution section"""
        elements = []
        
        elements.append(Paragraph("Risk Distribution", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Risk distribution table
        risk_dist = df['risk_level'].value_counts()
        
        risk_data = [['Risk Level', 'Count', 'Percentage']]
        for level in ['High', 'Medium', 'Low']:
            if level in risk_dist:
                count = risk_dist[level]
                pct = count / len(df) * 100
                risk_data.append([level, f"{count:,}", f"{pct:.1f}%"])
        
        risk_table = Table(risk_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        risk_table.setStyle(self._get_table_style())
        elements.append(risk_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add chart if available
        if include_charts and HAS_MATPLOTLIB:
            chart_path = self._create_risk_chart(df)
            if chart_path:
                elements.append(Paragraph("Risk Distribution Chart", self.styles['SubSectionHeader']))
                img = Image(str(chart_path), width=5*inch, height=3*inch)
                elements.append(img)
        
        return elements
    
    def _build_top_counties(self, df: pd.DataFrame, n: int = 15) -> List:
        """Build top risk counties section"""
        elements = []
        
        elements.append(Paragraph(f"Top {n} Highest Risk Counties", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        top_counties = df.nlargest(n, 'risk_score')
        
        # Table data
        table_data = [['Rank', 'County', 'Risk Score', 'Risk Level', 'Population']]
        
        for idx, (_, row) in enumerate(top_counties.iterrows(), 1):
            table_data.append([
                str(idx),
                row['county_name'],
                f"{row['risk_score']:.3f}",
                row['risk_level'],
                f"{int(row['total_population']):,}"
            ])
        
        # Create table
        county_table = Table(table_data, colWidths=[0.5*inch, 2.5*inch, 1*inch, 1*inch, 1.2*inch])
        county_table.setStyle(self._get_table_style())
        elements.append(county_table)
        
        return elements
    
    def _build_infrastructure_analysis(self, df: pd.DataFrame) -> List:
        """Build infrastructure analysis section"""
        elements = []
        
        elements.append(Paragraph("Infrastructure Gap Analysis", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Distance metrics
        elements.append(Paragraph("Average Distance to Facilities", self.styles['SubSectionHeader']))
        
        dist_data = [['Facility Type', 'Mean Distance (km)', 'Median Distance (km)']]
        
        dist_cols = [
            ('dist_nearest_hospitals_km', 'Hospital'),
            ('dist_nearest_fire_stations_km', 'Fire Station'),
            ('dist_nearest_ems_stations_km', 'EMS Station'),
        ]
        
        for col, name in dist_cols:
            if col in df.columns:
                mean_dist = df[col].mean()
                median_dist = df[col].median()
                dist_data.append([
                    name,
                    f"{mean_dist:.1f}",
                    f"{median_dist:.1f}"
                ])
        
        dist_table = Table(dist_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
        dist_table.setStyle(self._get_table_style())
        elements.append(dist_table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Zero redundancy counties
        if 'zero_redundancy_flag' in df.columns:
            zero_red = df[df['zero_redundancy_flag'] == True]
            if len(zero_red) > 0:
                elements.append(Paragraph(
                    f"Counties with Zero Infrastructure Redundancy ({len(zero_red)})",
                    self.styles['SubSectionHeader']
                ))
                
                red_data = [['County', 'Risk Score', 'Population']]
                for _, row in zero_red.head(10).iterrows():
                    red_data.append([
                        row['county_name'],
                        f"{row['risk_score']:.3f}",
                        f"{int(row['total_population']):,}"
                    ])
                
                red_table = Table(red_data, colWidths=[3*inch, 1*inch, 1.2*inch])
                red_table.setStyle(self._get_table_style())
                elements.append(red_table)
        
        return elements
    
    def _build_recommendations(self, df: pd.DataFrame) -> List:
        """Build recommendations section"""
        elements = []
        
        elements.append(Paragraph("Strategic Recommendations", self.styles['SectionHeader']))
        elements.append(Spacer(1, 0.2*inch))
        
        # Generate recommendations based on data
        recommendations = self._generate_recommendations(df)
        
        for category, items in recommendations.items():
            elements.append(Paragraph(category, self.styles['SubSectionHeader']))
            for item in items:
                elements.append(Paragraph(f"• {item}", self.styles['BodyText']))
            elements.append(Spacer(1, 0.1*inch))
        
        return elements
    
    def _generate_recommendations(self, df: pd.DataFrame) -> Dict[str, List]:
        """Generate recommendations based on data"""
        recommendations = {
            'Immediate Actions (0-6 months)': [],
            'Short-term Initiatives (6-18 months)': [],
            'Long-term Strategy (18+ months)': []
        }
        
        # High risk counties
        high_risk = df[df['risk_score'] >= 0.7]
        if len(high_risk) > 0:
            recommendations['Immediate Actions (0-6 months)'].append(
                f"Deploy emergency resources to {len(high_risk)} high-risk counties"
            )
        
        # Zero redundancy
        if 'zero_redundancy_flag' in df.columns:
            zero_red = df[df['zero_redundancy_flag'] == True]
            if len(zero_red) > 0:
                recommendations['Immediate Actions (0-6 months)'].append(
                    f"Address infrastructure gaps in {len(zero_red)} counties with zero redundancy"
                )
        
        # Compound risk
        if 'compound_risk_flag' in df.columns:
            compound = df[df['compound_risk_flag'] == True]
            if len(compound) > 0:
                recommendations['Short-term Initiatives (6-18 months)'].append(
                    f"Develop multi-hazard preparedness plans for {len(compound)} counties with compound risk"
                )
        
        # General recommendations
        recommendations['Long-term Strategy (18+ months)'].extend([
            "Implement predictive risk monitoring system",
            "Establish mutual aid agreements between high-risk counties",
            "Develop community resilience training programs"
        ])
        
        return recommendations
    
    def _create_risk_chart(self, df: pd.DataFrame) -> Optional[Path]:
        """Create risk distribution chart"""
        if not HAS_MATPLOTLIB:
            return None
        
        risk_dist = df['risk_level'].value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 5))
        
        colors = ['#dc3545' if l == 'High' else '#ffc107' if l == 'Medium' else '#28a745' 
                  for l in risk_dist.index]
        
        ax.bar(risk_dist.index, risk_dist.values, color=colors)
        ax.set_xlabel('Risk Level')
        ax.set_ylabel('Number of Counties')
        ax.set_title('Risk Distribution')
        
        # Add value labels
        for i, v in enumerate(risk_dist.values):
            ax.text(i, v, str(v), ha='center', va='bottom')
        
        chart_path = FIGURES_DIR / f'risk_chart_{datetime.now().strftime("%Y%m%d%H%M%S")}.png'
        plt.tight_layout()
        plt.savefig(chart_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return chart_path
    
    def _get_table_style(self) -> TableStyle:
        """Get standard table style"""
        return TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('TEXTCOLOR', (0, 0), (-1, 0), white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), white),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.COLORS['text']),
            ('ALIGN', (0, 1), (0, -1), 'LEFT'),
            ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('GRID', (0, 0), (-1, -1), 1, self.COLORS['border']),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ])
    
    def _apply_filters(self, df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
        """Apply filters to dataframe"""
        result = df.copy()
        
        if 'state' in filters:
            result = result[result['county_name'].str.contains(f', {filters["state"]}$', regex=True, na=False)]
        
        if 'risk_level' in filters:
            result = result[result['risk_level'] == filters['risk_level']]
        
        if 'min_risk_score' in filters:
            result = result[result['risk_score'] >= filters['min_risk_score']]
        
        return result


def main():
    """CLI for PDF report generation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate PDF reports")
    parser.add_argument("--type", choices=['executive', 'county'], default='executive',
                        help="Report type")
    parser.add_argument("--output", "-o", help="Output file path")
    parser.add_argument("--state", help="Filter by state")
    parser.add_argument("--fips", help="County FIPS (for county report)")
    parser.add_argument("--min-risk", type=float, help="Minimum risk score")
    parser.add_argument("--no-charts", action="store_true", help="Exclude charts")
    
    args = parser.parse_args()
    
    reporter = PDFReporter()
    
    if reporter.df is None:
        print("Error: County data not found. Run pipeline first.")
        return
    
    filters = {}
    if args.state:
        filters['state'] = args.state
    if args.min_risk:
        filters['min_risk_score'] = args.min_risk
    
    if args.type == 'executive':
        result = reporter.generate_executive_report(
            output_path=args.output,
            filters=filters if filters else None,
            include_charts=not args.no_charts
        )
    else:
        if not args.fips:
            print("Error: --fips required for county report")
            return
        result = reporter.generate_county_profile(
            fips=args.fips,
            output_path=args.output
        )
    
    if "error" in result:
        print(f"Error: {result['error']}")
    else:
        print(f"Report generated: {result['output_path']}")


if __name__ == "__main__":
    main()
