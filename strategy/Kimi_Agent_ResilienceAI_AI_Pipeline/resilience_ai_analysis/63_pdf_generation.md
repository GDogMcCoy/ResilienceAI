# ResilienceAI PDF Generation System

## Executive Summary

This document provides a comprehensive design for PDF generation capabilities in ResilienceAI, covering report generation, executive briefings, and export functionality. The system is designed to handle complex multi-page reports with embedded charts, tables, and rich formatting while maintaining performance and accessibility standards.

---

## Table of Contents

1. [PDF Architecture Overview](#1-pdf-architecture-overview)
2. [Library Selection & Comparison](#2-library-selection--comparison)
3. [Core PDF Generation Engine](#3-core-pdf-generation-engine)
4. [Report Templates](#4-report-templates)
5. [Chart & Table Embedding](#5-chart--table-embedding)
6. [Multi-Page Report Handling](#6-multi-page-report-handling)
7. [Styling & Formatting System](#7-styling--formatting-system)
8. [Header/Footer Management](#8-headerfooter-management)
9. [PDF Export API](#9-pdf-export-api)
10. [Batch PDF Generation](#10-batch-pdf-generation)
11. [PDF Compression](#11-pdf-compression)
12. [PDF Accessibility](#12-pdf-accessibility)
13. [Performance Tuning](#13-performance-tuning)
14. [Testing Strategy](#14-testing-strategy)
15. [Implementation Priority](#15-implementation-priority)

---

## 1. PDF Architecture Overview

### 1.1 System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ResilienceAI PDF Generation System                   │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐          │
│  │   Report API    │    │  Export API     │    │  Batch API      │          │
│  │   (FastAPI)     │    │  (FastAPI)      │    │  (FastAPI)      │          │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘          │
│           │                      │                      │                   │
│           └──────────────────────┼──────────────────────┘                   │
│                                  │                                           │
│                    ┌─────────────▼─────────────┐                            │
│                    │    PDF Generation Core    │                            │
│                    │    ┌─────────────────┐    │                            │
│                    │    │  Template Engine │   │                            │
│                    │    │  Style Manager   │   │                            │
│                    │    │  Content Builder │   │                            │
│                    │    └─────────────────┘    │                            │
│                    └─────────────┬─────────────┘                            │
│                                  │                                           │
│        ┌─────────────────────────┼─────────────────────────┐                │
│        │                         │                         │                │
│  ┌─────▼─────┐           ┌──────▼──────┐          ┌──────▼──────┐          │
│  │ ReportLab │           │  WeasyPrint │          │  Chart Gen  │          │
│  │  Engine   │           │   Engine    │          │  (Matplotlib│          │
│  │           │           │             │          │  /Plotly)   │          │
│  └───────────┘           └─────────────┘          └─────────────┘          │
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐    │
│  │                      Output & Storage Layer                          │    │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐    │    │
│  │  │  Local   │  │   S3     │  │  CDN     │  │  Compression     │    │    │
│  │  │ Storage  │  │ Storage  │  │ Delivery │  │  & Optimization  │    │    │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Component Responsibilities

| Component | Responsibility | Technology |
|-----------|----------------|------------|
| Template Engine | Manage report templates, variable substitution | Jinja2 + Custom |
| Style Manager | Handle CSS/styles, themes, branding | CSS + Python |
| Content Builder | Assemble content sections, charts, tables | Python |
| ReportLab Engine | Low-level PDF generation, precise control | ReportLab |
| WeasyPrint Engine | HTML-to-PDF conversion, complex layouts | WeasyPrint |
| Chart Generator | Create charts from data | Matplotlib/Plotly |
| Compression Service | Optimize PDF size | pikepdf/PyPDF2 |
| Accessibility Service | Add tags, alt text, structure | ReportLab + pikepdf |

---

## 2. Library Selection & Comparison

### 2.1 Library Comparison Matrix

| Feature | ReportLab | WeasyPrint | fpdf2 | pdfkit | Recommendation |
|---------|-----------|------------|-------|--------|----------------|
| **HTML to PDF** | No | Yes | No | Yes | WeasyPrint |
| **Pythonic API** | Yes | Yes | Yes | No | ReportLab/fpdf2 |
| **Complex Layouts** | Good | Excellent | Limited | Good | WeasyPrint |
| **Chart Embedding** | Native | Via HTML | Limited | Via HTML | ReportLab |
| **Performance** | Fast | Medium | Fast | Medium | ReportLab |
| **Memory Usage** | Low | Medium | Low | Medium | ReportLab |
| **PDF/A Support** | Yes | Yes | No | No | ReportLab |
| **Accessibility** | Good | Good | Limited | Limited | ReportLab |
| **Table Support** | Good | Excellent | Basic | Good | WeasyPrint |
| **Multi-column** | Manual | CSS | Manual | CSS | WeasyPrint |
| **Font Handling** | Excellent | Good | Good | Good | ReportLab |
| **License** | BSD | BSD | LGPL | MIT | Both acceptable |

### 2.2 Recommended Hybrid Approach

```python
# /app/pdf/generation/strategy.py
"""
PDF Generation Strategy Pattern
Uses different engines based on report complexity
"""
from enum import Enum
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod


class PDFEngine(Enum):
    """Available PDF generation engines"""
    REPORTLAB = "reportlab"      # For data-heavy, chart-focused reports
    WEASYPRINT = "weasyprint"    # For HTML-rich, layout-focused reports
    HYBRID = "hybrid"            # Combines both approaches


class ReportComplexity(Enum):
    """Report complexity levels"""
    SIMPLE = "simple"            # Single page, basic content
    STANDARD = "standard"        # Multi-page, charts, tables
    COMPLEX = "complex"          # Rich layouts, multiple sections
    EXECUTIVE = "executive"      # Premium formatting, branding


class PDFGenerationStrategy(ABC):
    """Abstract base class for PDF generation strategies"""
    
    @abstractmethod
    def generate(self, report_data: Dict[str, Any], output_path: str) -> str:
        pass
    
    @abstractmethod
    def supports_charts(self) -> bool:
        pass
    
    @abstractmethod
    def supports_html(self) -> bool:
        pass


class StrategySelector:
    """Selects optimal PDF generation strategy"""
    
    @staticmethod
    def select_engine(
        complexity: ReportComplexity,
        has_html_content: bool = False,
        chart_count: int = 0,
        page_estimate: int = 1
    ) -> PDFEngine:
        """
        Select optimal PDF engine based on requirements
        
        Decision Matrix:
        - HTML-heavy content → WeasyPrint
        - Many charts, precise control → ReportLab
        - Mixed requirements → Hybrid
        """
        if has_html_content and chart_count < 3:
            return PDFEngine.WEASYPRINT
        elif chart_count > 5 or complexity == ReportComplexity.EXECUTIVE:
            return PDFEngine.REPORTLAB
        elif has_html_content and chart_count >= 3:
            return PDFEngine.HYBRID
        else:
            return PDFEngine.REPORTLAB
```

---

## 3. Core PDF Generation Engine

### 3.1 Base PDF Generator Class

```python
# /app/pdf/generation/base.py
"""
Base PDF Generator with common functionality
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, BinaryIO, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import io
import logging

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF

logger = logging.getLogger(__name__)


@dataclass
class PDFMargins:
    """PDF page margins"""
    top: float = 72      # 1 inch
    bottom: float = 72   # 1 inch
    left: float = 72     # 1 inch
    right: float = 72    # 1 inch
    
    @classmethod
    def narrow(cls) -> 'PDFMargins':
        return cls(top=36, bottom=36, left=36, right=36)
    
    @classmethod
    def wide(cls) -> 'PDFMargins':
        return cls(top=108, bottom=108, left=108, right=108)


@dataclass
class PDFMetadata:
    """PDF document metadata"""
    title: str
    author: str = "ResilienceAI"
    subject: str = ""
    keywords: List[str] = None
    creator: str = "ResilienceAI PDF Generator"
    creation_date: datetime = None
    
    def __post_init__(self):
        if self.keywords is None:
            self.keywords = []
        if self.creation_date is None:
            self.creation_date = datetime.now()


@dataclass
class PageSettings:
    """Page configuration settings"""
    size: tuple = letter
    margins: PDFMargins = None
    orientation: str = "portrait"
    
    def __post_init__(self):
        if self.margins is None:
            self.margins = PDFMargins()
    
    @property
    def width(self) -> float:
        return self.size[0] if self.orientation == "portrait" else self.size[1]
    
    @property
    def height(self) -> float:
        return self.size[1] if self.orientation == "portrait" else self.size[0]
    
    @property
    def content_width(self) -> float:
        return self.width - self.margins.left - self.margins.right
    
    @property
    def content_height(self) -> float:
        return self.height - self.margins.top - self.margins.bottom


class BasePDFGenerator(ABC):
    """
    Base class for all PDF generators
    Provides common functionality and interface
    """
    
    def __init__(
        self,
        metadata: PDFMetadata,
        page_settings: PageSettings = None,
        template_name: Optional[str] = None
    ):
        self.metadata = metadata
        self.page_settings = page_settings or PageSettings()
        self.template_name = template_name
        self.styles = self._initialize_styles()
        self.elements: List[Any] = []
        
    def _initialize_styles(self) -> Dict[str, ParagraphStyle]:
        """Initialize default paragraph styles"""
        base_styles = getSampleStyleSheet()
        
        # Custom styles for ResilienceAI branding
        custom_styles = {
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Title'],
                fontSize=24,
                leading=30,
                textColor=colors.HexColor('#1a365d'),
                spaceAfter=30,
                fontName='Helvetica-Bold'
            ),
            'Heading1': ParagraphStyle(
                'CustomH1',
                parent=base_styles['Heading1'],
                fontSize=18,
                leading=24,
                textColor=colors.HexColor('#2c5282'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            ),
            'Heading2': ParagraphStyle(
                'CustomH2',
                parent=base_styles['Heading2'],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor('#2d3748'),
                spaceAfter=10,
                spaceBefore=10,
                fontName='Helvetica-Bold'
            ),
            'Heading3': ParagraphStyle(
                'CustomH3',
                parent=base_styles['Heading3'],
                fontSize=12,
                leading=16,
                textColor=colors.HexColor('#4a5568'),
                spaceAfter=8,
                spaceBefore=8,
                fontName='Helvetica-Bold'
            ),
            'BodyText': ParagraphStyle(
                'CustomBody',
                parent=base_styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#1a202c'),
                spaceAfter=6,
                fontName='Helvetica'
            ),
            'Caption': ParagraphStyle(
                'Caption',
                parent=base_styles['Normal'],
                fontSize=9,
                leading=12,
                textColor=colors.HexColor('#718096'),
                alignment=1,  # Center
                spaceBefore=6,
                fontName='Helvetica-Oblique'
            ),
            'AlertHigh': ParagraphStyle(
                'AlertHigh',
                parent=base_styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#c53030'),
                backColor=colors.HexColor('#fed7d7'),
                spaceAfter=6,
                leftIndent=10,
                rightIndent=10,
                fontName='Helvetica-Bold'
            ),
            'AlertMedium': ParagraphStyle(
                'AlertMedium',
                parent=base_styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#c05621'),
                backColor=colors.HexColor('#feebc8'),
                spaceAfter=6,
                leftIndent=10,
                rightIndent=10,
                fontName='Helvetica-Bold'
            ),
            'AlertLow': ParagraphStyle(
                'AlertLow',
                parent=base_styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#276749'),
                backColor=colors.HexColor('#c6f6d5'),
                spaceAfter=6,
                leftIndent=10,
                rightIndent=10,
                fontName='Helvetica-Bold'
            ),
        }
        
        return {**base_styles, **custom_styles}
    
    @abstractmethod
    def generate(self, output_path: Optional[str] = None) -> Union[str, bytes]:
        """
        Generate the PDF document
        
        Args:
            output_path: Path to save PDF, or None to return bytes
            
        Returns:
            Path to saved PDF or PDF bytes
        """
        pass
    
    def add_element(self, element: Any) -> 'BasePDFGenerator':
        """Add element to document"""
        self.elements.append(element)
        return self
    
    def add_paragraph(
        self,
        text: str,
        style: str = 'BodyText',
        space_after: Optional[float] = None
    ) -> 'BasePDFGenerator':
        """Add paragraph to document"""
        para = Paragraph(text, self.styles[style])
        self.elements.append(para)
        if space_after:
            self.elements.append(Spacer(1, space_after))
        return self
    
    def add_spacer(self, height: float) -> 'BasePDFGenerator':
        """Add vertical spacer"""
        self.elements.append(Spacer(1, height))
        return self
    
    def add_page_break(self) -> 'BasePDFGenerator':
        """Add page break"""
        self.elements.append(PageBreak())
        return self
    
    def add_heading(self, text: str, level: int = 1) -> 'BasePDFGenerator':
        """Add heading to document"""
        style_name = f'Heading{level}'
        if style_name not in self.styles:
            style_name = 'Heading1'
        self.elements.append(Paragraph(text, self.styles[style_name]))
        return self
```

### 3.2 ReportLab PDF Generator Implementation

```python
# /app/pdf/generation/reportlab_engine.py
"""
ReportLab-based PDF generation engine
Optimized for data-heavy reports with charts and tables
"""
from typing import Optional, List, Dict, Any, BinaryIO, Union, Callable
from io import BytesIO
from pathlib import Path
import logging

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch, mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    Image, PageBreak, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.utils import ImageReader

from .base import BasePDFGenerator, PDFMetadata, PageSettings, PDFMargins

logger = logging.getLogger(__name__)


class HeaderFooterCanvas(canvas.Canvas):
    """Custom canvas with header/footer support"""
    
    def __init__(self, *args, **kwargs):
        self.header_func = kwargs.pop('header_func', None)
        self.footer_func = kwargs.pop('footer_func', None)
        self.header_data = kwargs.pop('header_data', {})
        self.footer_data = kwargs.pop('footer_data', {})
        super().__init__(*args, **kwargs)
        self.pages = []
    
    def showPage(self):
        self.pages.append(dict(self.__dict__))
        self._startPage()
    
    def save(self):
        page_count = len(self.pages)
        for page_num, page in enumerate(self.pages, 1):
            self.__dict__.update(page)
            if self.header_func:
                self.header_func(self, page_num, page_count, self.header_data)
            if self.footer_func:
                self.footer_func(self, page_num, page_count, self.footer_data)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)


class ReportLabPDFGenerator(BasePDFGenerator):
    """
    ReportLab-based PDF generator
    Best for: Charts, precise layouts, data-heavy reports
    """
    
    def __init__(
        self,
        metadata: PDFMetadata,
        page_settings: PageSettings = None,
        template_name: Optional[str] = None,
        header_func: Optional[Callable] = None,
        footer_func: Optional[Callable] = None
    ):
        super().__init__(metadata, page_settings, template_name)
        self.header_func = header_func
        self.footer_func = footer_func
        self.temp_images: List[str] = []  # Track temp image files
        
    def generate(
        self,
        output_path: Optional[str] = None,
        return_bytes: bool = False
    ) -> Union[str, bytes]:
        """
        Generate PDF using ReportLab
        
        Args:
            output_path: Path to save PDF
            return_bytes: If True, return PDF as bytes
            
        Returns:
            Path to saved PDF or PDF bytes
        """
        buffer = BytesIO()
        
        # Create document template
        doc = SimpleDocTemplate(
            buffer,
            pagesize=self.page_settings.size,
            rightMargin=self.page_settings.margins.right,
            leftMargin=self.page_settings.margins.left,
            topMargin=self.page_settings.margins.top,
            bottomMargin=self.page_settings.margins.bottom,
        )
        
        # Build document with metadata
        doc.title = self.metadata.title
        doc.author = self.metadata.author
        doc.subject = self.metadata.subject
        doc.creator = self.metadata.creator
        doc.keywords = ', '.join(self.metadata.keywords) if self.metadata.keywords else ''
        
        try:
            # Build the document
            doc.build(
                self.elements,
                canvasmaker=lambda *args, **kwargs: HeaderFooterCanvas(
                    *args,
                    header_func=self.header_func,
                    footer_func=self.footer_func,
                    header_data={'metadata': self.metadata},
                    footer_data={'metadata': self.metadata},
                    **kwargs
                )
            )
            
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            # Save to file or return bytes
            if output_path:
                Path(output_path).parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as f:
                    f.write(pdf_bytes)
                logger.info(f"PDF saved to: {output_path}")
                return output_path
            
            if return_bytes:
                return pdf_bytes
            
            return pdf_bytes
            
        finally:
            # Cleanup temp images
            self._cleanup_temp_images()
    
    def _cleanup_temp_images(self):
        """Remove temporary image files"""
        import os
        for img_path in self.temp_images:
            try:
                if os.path.exists(img_path):
                    os.remove(img_path)
            except Exception as e:
                logger.warning(f"Failed to cleanup temp image {img_path}: {e}")
    
    def add_table(
        self,
        data: List[List[Any]],
        col_widths: Optional[List[float]] = None,
        style: Optional[TableStyle] = None,
        repeat_rows: int = 1,
        space_after: float = 12
    ) -> 'ReportLabPDFGenerator':
        """
        Add styled table to document
        
        Args:
            data: Table data as list of rows
            col_widths: Optional column widths
            style: Optional custom table style
            repeat_rows: Number of header rows to repeat
            space_after: Space after table
        """
        if not data:
            return self
        
        # Default table style
        if style is None:
            style = TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f7fafc')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ])
        
        # Convert data to strings and create Paragraphs for wrapping
        table_data = []
        for row_idx, row in enumerate(data):
            table_row = []
            for col in row:
                if row_idx == 0:
                    # Header row - bold
                    table_row.append(Paragraph(str(col), self.styles['Heading3']))
                else:
                    table_row.append(Paragraph(str(col), self.styles['BodyText']))
            table_data.append(table_row)
        
        # Calculate column widths if not provided
        if col_widths is None:
            content_width = self.page_settings.content_width
            num_cols = len(data[0]) if data else 1
            col_widths = [content_width / num_cols] * num_cols
        
        table = Table(table_data, colWidths=col_widths, repeatRows=repeat_rows)
        table.setStyle(style)
        
        self.elements.append(KeepTogether([table, Spacer(1, space_after)]))
        return self
    
    def add_chart_image(
        self,
        image_data: Union[str, bytes, BytesIO],
        width: Optional[float] = None,
        height: Optional[float] = None,
        caption: Optional[str] = None,
        align: str = 'CENTER'
    ) -> 'ReportLabPDFGenerator':
        """
        Add chart/image to document
        
        Args:
            image_data: Path to image, bytes, or BytesIO
            width: Image width (defaults to content width)
            height: Image height (auto if not specified)
            caption: Optional caption
            align: Alignment (LEFT, CENTER, RIGHT)
        """
        content_width = self.page_settings.content_width
        
        # Set default width
        if width is None:
            width = content_width * 0.9
        
        # Handle different input types
        if isinstance(image_data, str):
            img = Image(image_data, width=width, height=height)
        elif isinstance(image_data, bytes):
            img_reader = ImageReader(BytesIO(image_data))
            img = Image(img_reader, width=width, height=height)
        elif isinstance(image_data, BytesIO):
            img_reader = ImageReader(image_data)
            img = Image(img_reader, width=width, height=height)
        else:
            raise ValueError("image_data must be path, bytes, or BytesIO")
        
        # Alignment
        if align == 'CENTER':
            img.hAlign = 'CENTER'
        elif align == 'LEFT':
            img.hAlign = 'LEFT'
        elif align == 'RIGHT':
            img.hAlign = 'RIGHT'
        
        self.elements.append(img)
        
        # Add caption if provided
        if caption:
            self.elements.append(Spacer(1, 6))
            self.elements.append(Paragraph(caption, self.styles['Caption']))
        
        self.elements.append(Spacer(1, 12))
        return self
    
    def add_alert_box(
        self,
        message: str,
        level: str = 'medium',
        title: Optional[str] = None
    ) -> 'ReportLabPDFGenerator':
        """
        Add alert/notification box
        
        Args:
            message: Alert message
            level: Alert level (high, medium, low)
            title: Optional alert title
        """
        style_map = {
            'high': 'AlertHigh',
            'medium': 'AlertMedium',
            'low': 'AlertLow'
        }
        style_name = style_map.get(level.lower(), 'AlertMedium')
        
        alert_text = message
        if title:
            alert_text = f"<b>{title}</b><br/>{message}"
        
        self.elements.append(Paragraph(alert_text, self.styles[style_name]))
        self.elements.append(Spacer(1, 12))
        return self
    
    def add_bullet_list(
        self,
        items: List[str],
        bullet_type: str = 'bullet',
        space_after: float = 12
    ) -> 'ReportLabPDFGenerator':
        """Add bullet list to document"""
        list_items = [ListItem(Paragraph(item, self.styles['BodyText'])) 
                      for item in items]
        bullet_list = ListFlowable(
            list_items,
            bulletType=bullet_type,
            leftIndent=20
        )
        self.elements.append(bullet_list)
        self.elements.append(Spacer(1, space_after))
        return self
```

---

## 4. Report Templates

### 4.1 Template System Architecture

```python
# /app/pdf/templates/registry.py
"""
PDF Template Registry and Management
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


class ReportType(Enum):
    """Types of reports supported"""
    EXECUTIVE_SUMMARY = "executive_summary"
    RISK_ASSESSMENT = "risk_assessment"
    INCIDENT_REPORT = "incident_report"
    COMPLIANCE_AUDIT = "compliance_audit"
    VULNERABILITY_SCAN = "vulnerability_scan"
    THREAT_INTELLIGENCE = "threat_intelligence"
    BUSINESS_IMPACT = "business_impact"
    CUSTOM = "custom"


class TemplateCategory(Enum):
    """Template categories"""
    SECURITY = "security"
    COMPLIANCE = "compliance"
    OPERATIONAL = "operational"
    EXECUTIVE = "executive"
    TECHNICAL = "technical"


@dataclass
class TemplateSection:
    """Template section definition"""
    name: str
    title: str
    required: bool = True
    order: int = 0
    content_type: str = "text"  # text, table, chart, mixed
    default_content: Optional[str] = None
    style_override: Optional[Dict[str, Any]] = None


@dataclass
class ReportTemplate:
    """Report template definition"""
    id: str
    name: str
    description: str
    report_type: ReportType
    category: TemplateCategory
    sections: List[TemplateSection] = field(default_factory=list)
    page_settings: Dict[str, Any] = field(default_factory=dict)
    header_template: Optional[str] = None
    footer_template: Optional[str] = None
    css_overrides: Optional[str] = None
    version: str = "1.0.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'report_type': self.report_type.value,
            'category': self.category.value,
            'sections': [
                {
                    'name': s.name,
                    'title': s.title,
                    'required': s.required,
                    'order': s.order,
                    'content_type': s.content_type,
                    'default_content': s.default_content,
                    'style_override': s.style_override
                }
                for s in self.sections
            ],
            'page_settings': self.page_settings,
            'header_template': self.header_template,
            'footer_template': self.footer_template,
            'css_overrides': self.css_overrides,
            'version': self.version
        }


class TemplateRegistry:
    """
    Central registry for all PDF templates
    """
    
    _instance = None
    _templates: Dict[str, ReportTemplate] = {}
    _custom_templates_path: Path = Path("/app/pdf/templates/custom")
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize_default_templates()
        return cls._instance
    
    def _initialize_default_templates(self):
        """Initialize built-in templates"""
        # Executive Summary Template
        self.register_template(ReportTemplate(
            id="executive_summary_v1",
            name="Executive Summary",
            description="High-level executive briefing with key metrics and recommendations",
            report_type=ReportType.EXECUTIVE_SUMMARY,
            category=TemplateCategory.EXECUTIVE,
            sections=[
                TemplateSection("cover", "Cover Page", required=True, order=0),
                TemplateSection("executive_summary", "Executive Summary", required=True, order=1),
                TemplateSection("key_metrics", "Key Metrics", required=True, order=2, content_type="chart"),
                TemplateSection("risk_overview", "Risk Overview", required=True, order=3, content_type="mixed"),
                TemplateSection("recommendations", "Recommendations", required=True, order=4),
                TemplateSection("next_steps", "Next Steps", required=False, order=5),
            ],
            page_settings={
                'orientation': 'portrait',
                'margins': {'top': 72, 'bottom': 72, 'left': 72, 'right': 72}
            }
        ))
        
        # Risk Assessment Template
        self.register_template(ReportTemplate(
            id="risk_assessment_v1",
            name="Risk Assessment Report",
            description="Comprehensive risk assessment with detailed analysis",
            report_type=ReportType.RISK_ASSESSMENT,
            category=TemplateCategory.SECURITY,
            sections=[
                TemplateSection("cover", "Cover Page", required=True, order=0),
                TemplateSection("methodology", "Assessment Methodology", required=True, order=1),
                TemplateSection("asset_inventory", "Asset Inventory", required=True, order=2, content_type="table"),
                TemplateSection("threat_analysis", "Threat Analysis", required=True, order=3, content_type="mixed"),
                TemplateSection("vulnerability_assessment", "Vulnerability Assessment", required=True, order=4, content_type="mixed"),
                TemplateSection("risk_matrix", "Risk Matrix", required=True, order=5, content_type="chart"),
                TemplateSection("risk_register", "Risk Register", required=True, order=6, content_type="table"),
                TemplateSection("mitigation_plan", "Mitigation Plan", required=True, order=7),
                TemplateSection("appendix", "Appendix", required=False, order=8),
            ],
            page_settings={
                'orientation': 'portrait',
                'margins': {'top': 72, 'bottom': 72, 'left': 72, 'right': 72}
            }
        ))
        
        # Incident Report Template
        self.register_template(ReportTemplate(
            id="incident_report_v1",
            name="Incident Response Report",
            description="Detailed incident response documentation",
            report_type=ReportType.INCIDENT_REPORT,
            category=TemplateCategory.SECURITY,
            sections=[
                TemplateSection("cover", "Incident Report", required=True, order=0),
                TemplateSection("incident_summary", "Incident Summary", required=True, order=1),
                TemplateSection("timeline", "Incident Timeline", required=True, order=2, content_type="table"),
                TemplateSection("impact_assessment", "Impact Assessment", required=True, order=3),
                TemplateSection("response_actions", "Response Actions", required=True, order=4, content_type="table"),
                TemplateSection("evidence", "Evidence Collection", required=True, order=5),
                TemplateSection("lessons_learned", "Lessons Learned", required=True, order=6),
                TemplateSection("recommendations", "Recommendations", required=True, order=7),
            ],
            page_settings={
                'orientation': 'portrait',
                'margins': {'top': 72, 'bottom': 72, 'left': 72, 'right': 72}
            }
        ))
        
        # Vulnerability Scan Report Template
        self.register_template(ReportTemplate(
            id="vulnerability_scan_v1",
            name="Vulnerability Scan Report",
            description="Technical vulnerability scan results",
            report_type=ReportType.VULNERABILITY_SCAN,
            category=TemplateCategory.TECHNICAL,
            sections=[
                TemplateSection("cover", "Vulnerability Scan Report", required=True, order=0),
                TemplateSection("scan_summary", "Scan Summary", required=True, order=1),
                TemplateSection("executive_summary", "Executive Summary", required=True, order=2),
                TemplateSection("findings_summary", "Findings Summary", required=True, order=3, content_type="chart"),
                TemplateSection("critical_findings", "Critical Findings", required=True, order=4, content_type="table"),
                TemplateSection("high_findings", "High Severity Findings", required=True, order=5, content_type="table"),
                TemplateSection("medium_findings", "Medium Severity Findings", required=False, order=6, content_type="table"),
                TemplateSection("low_findings", "Low Severity Findings", required=False, order=7, content_type="table"),
                TemplateSection("remediation_plan", "Remediation Plan", required=True, order=8),
                TemplateSection("technical_details", "Technical Details", required=False, order=9),
            ],
            page_settings={
                'orientation': 'portrait',
                'margins': {'top': 72, 'bottom': 72, 'left': 72, 'right': 72}
            }
        ))
        
        # Compliance Audit Template
        self.register_template(ReportTemplate(
            id="compliance_audit_v1",
            name="Compliance Audit Report",
            description="Regulatory compliance assessment report",
            report_type=ReportType.COMPLIANCE_AUDIT,
            category=TemplateCategory.COMPLIANCE,
            sections=[
                TemplateSection("cover", "Compliance Audit Report", required=True, order=0),
                TemplateSection("executive_summary", "Executive Summary", required=True, order=1),
                TemplateSection("scope", "Audit Scope", required=True, order=2),
                TemplateSection("methodology", "Audit Methodology", required=True, order=3),
                TemplateSection("framework_mapping", "Framework Mapping", required=True, order=4, content_type="table"),
                TemplateSection("control_assessment", "Control Assessment", required=True, order=5, content_type="table"),
                TemplateSection("findings", "Audit Findings", required=True, order=6, content_type="mixed"),
                TemplateSection("compliance_score", "Compliance Score", required=True, order=7, content_type="chart"),
                TemplateSection("gap_analysis", "Gap Analysis", required=True, order=8),
                TemplateSection("remediation", "Remediation Roadmap", required=True, order=9),
                TemplateSection("certification", "Auditor Certification", required=False, order=10),
            ],
            page_settings={
                'orientation': 'portrait',
                'margins': {'top': 72, 'bottom': 72, 'left': 72, 'right': 72}
            }
        ))
    
    def register_template(self, template: ReportTemplate) -> None:
        """Register a new template"""
        self._templates[template.id] = template
    
    def get_template(self, template_id: str) -> Optional[ReportTemplate]:
        """Get template by ID"""
        return self._templates.get(template_id)
    
    def list_templates(
        self,
        category: Optional[TemplateCategory] = None,
        report_type: Optional[ReportType] = None
    ) -> List[ReportTemplate]:
        """List templates with optional filtering"""
        templates = list(self._templates.values())
        
        if category:
            templates = [t for t in templates if t.category == category]
        
        if report_type:
            templates = [t for t in templates if t.report_type == report_type]
        
        return templates
    
    def load_custom_templates(self) -> int:
        """Load custom templates from directory"""
        count = 0
        if not self._custom_templates_path.exists():
            return count
        
        for template_file in self._custom_templates_path.glob("*.json"):
            try:
                with open(template_file, 'r') as f:
                    data = json.load(f)
                # Convert dict to ReportTemplate
                template = self._dict_to_template(data)
                self.register_template(template)
                count += 1
            except Exception as e:
                print(f"Failed to load template {template_file}: {e}")
        
        return count
    
    def _dict_to_template(self, data: Dict[str, Any]) -> ReportTemplate:
        """Convert dictionary to ReportTemplate"""
        sections = [
            TemplateSection(**s) for s in data.get('sections', [])
        ]
        
        return ReportTemplate(
            id=data['id'],
            name=data['name'],
            description=data['description'],
            report_type=ReportType(data['report_type']),
            category=TemplateCategory(data['category']),
            sections=sections,
            page_settings=data.get('page_settings', {}),
            header_template=data.get('header_template'),
            footer_template=data.get('footer_template'),
            css_overrides=data.get('css_overrides'),
            version=data.get('version', '1.0.0')
        )


# Global template registry instance
template_registry = TemplateRegistry()
```

### 4.2 Template Builder

```python
# /app/pdf/templates/builder.py
"""
Template-based PDF Report Builder
"""
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass
import logging

from .registry import template_registry, ReportTemplate, TemplateSection
from ..generation.reportlab_engine import ReportLabPDFGenerator
from ..generation.base import PDFMetadata, PageSettings, PDFMargins

logger = logging.getLogger(__name__)


@dataclass
class SectionContent:
    """Content for a template section"""
    section_name: str
    title: Optional[str] = None
    paragraphs: List[str] = None
    table_data: Optional[List[List[Any]]] = None
    chart_image: Optional[bytes] = None
    chart_caption: Optional[str] = None
    bullet_points: List[str] = None
    alert_message: Optional[str] = None
    alert_level: str = "medium"
    custom_content: Optional[Any] = None
    
    def __post_init__(self):
        if self.paragraphs is None:
            self.paragraphs = []
        if self.bullet_points is None:
            self.bullet_points = []


class TemplateBuilder:
    """
    Builds PDF reports from templates
    """
    
    def __init__(self, template_id: str):
        self.template = template_registry.get_template(template_id)
        if not self.template:
            raise ValueError(f"Template not found: {template_id}")
        
        self.section_contents: Dict[str, SectionContent] = {}
        self.metadata: Optional[PDFMetadata] = None
        self.page_settings: Optional[PageSettings] = None
        
    def set_metadata(self, metadata: PDFMetadata) -> 'TemplateBuilder':
        """Set PDF metadata"""
        self.metadata = metadata
        return self
    
    def set_page_settings(self, settings: PageSettings) -> 'TemplateBuilder':
        """Set page settings"""
        self.page_settings = settings
        return self
    
    def add_section_content(
        self,
        section_name: str,
        content: SectionContent
    ) -> 'TemplateBuilder':
        """Add content for a section"""
        self.section_contents[section_name] = content
        return self
    
    def build(self) -> ReportLabPDFGenerator:
        """
        Build the PDF report from template
        
        Returns:
            Configured ReportLabPDFGenerator ready to generate
        """
        if not self.metadata:
            raise ValueError("Metadata must be set before building")
        
        # Use template page settings or defaults
        page_settings = self.page_settings or self._build_page_settings()
        
        # Create generator
        generator = ReportLabPDFGenerator(
            metadata=self.metadata,
            page_settings=page_settings,
            template_name=self.template.id
        )
        
        # Build sections in order
        sorted_sections = sorted(
            self.template.sections,
            key=lambda s: s.order
        )
        
        for section in sorted_sections:
            content = self.section_contents.get(section.name)
            
            if section.required and not content:
                logger.warning(f"Required section '{section.name}' has no content")
            
            if content:
                self._render_section(generator, section, content)
            elif section.default_content:
                # Use default content
                generator.add_heading(section.title, level=1)
                generator.add_paragraph(section.default_content)
        
        return generator
    
    def _build_page_settings(self) -> PageSettings:
        """Build page settings from template"""
        ps = self.template.page_settings
        
        margins = PDFMargins(
            top=ps.get('margins', {}).get('top', 72),
            bottom=ps.get('margins', {}).get('bottom', 72),
            left=ps.get('margins', {}).get('left', 72),
            right=ps.get('margins', {}).get('right', 72)
        )
        
        return PageSettings(
            orientation=ps.get('orientation', 'portrait'),
            margins=margins
        )
    
    def _render_section(
        self,
        generator: ReportLabPDFGenerator,
        section: TemplateSection,
        content: SectionContent
    ):
        """Render a section with its content"""
        # Section heading
        title = content.title or section.title
        generator.add_heading(title, level=1)
        generator.add_spacer(6)
        
        # Alert message if present
        if content.alert_message:
            generator.add_alert_box(
                content.alert_message,
                level=content.alert_level,
                title=f"{section.title} Alert"
            )
        
        # Paragraphs
        for paragraph in content.paragraphs:
            generator.add_paragraph(paragraph)
        
        # Bullet points
        if content.bullet_points:
            generator.add_bullet_list(content.bullet_points)
        
        # Table
        if content.table_data:
            generator.add_table(content.table_data)
        
        # Chart
        if content.chart_image:
            generator.add_chart_image(
                content.chart_image,
                caption=content.chart_caption
            )
        
        # Custom content
        if content.custom_content:
            generator.add_element(content.custom_content)
        
        # Add spacing after section
        generator.add_spacer(12)
```

---

## 5. Chart & Table Embedding

### 5.1 Chart Generation Service

```python
# /app/pdf/charts/generator.py
"""
Chart generation service for PDF embedding
Supports multiple chart types and styling
"""
from typing import Optional, List, Dict, Any, Tuple, Union
from dataclasses import dataclass
from io import BytesIO
import logging

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.figure import Figure
from matplotlib.axes import Axes
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ChartColors:
    """ResilienceAI brand colors for charts"""
    PRIMARY = '#2c5282'
    SECONDARY = '#38a169'
    ACCENT = '#ed8936'
    DANGER = '#e53e3e'
    WARNING = '#d69e2e'
    INFO = '#3182ce'
    
    # Severity colors
    CRITICAL = '#c53030'
    HIGH = '#dd6b20'
    MEDIUM = '#d69e2e'
    LOW = '#38a169'
    INFO_SEVERITY = '#4299e1'
    
    # Palette
    PALETTE = [
        '#2c5282', '#38a169', '#ed8936', '#e53e3e',
        '#805ad5', '#38b2ac', '#d53f8c', '#718096'
    ]


@dataclass
class ChartConfig:
    """Chart configuration"""
    width: float = 8  # inches
    height: float = 5  # inches
    dpi: int = 150
    title: Optional[str] = None
    xlabel: Optional[str] = None
    ylabel: Optional[str] = None
    show_legend: bool = True
    legend_position: str = 'best'
    grid: bool = True
    grid_alpha: float = 0.3
    style: str = 'seaborn-v0_8-whitegrid'
    
    def __post_init__(self):
        plt.style.use(self.style)


class ChartGenerator:
    """
    Generate charts for PDF embedding
    """
    
    def __init__(self, config: ChartConfig = None):
        self.config = config or ChartConfig()
    
    def _create_figure(self) -> Tuple[Figure, Axes]:
        """Create figure with configured size"""
        fig, ax = plt.subplots(
            figsize=(self.config.width, self.config.height),
            dpi=self.config.dpi
        )
        return fig, ax
    
    def _apply_styling(self, ax: Axes, title: Optional[str] = None):
        """Apply consistent styling"""
        if title or self.config.title:
            ax.set_title(title or self.config.title, fontsize=14, fontweight='bold')
        
        if self.config.xlabel:
            ax.set_xlabel(self.config.xlabel, fontsize=10)
        
        if self.config.ylabel:
            ax.set_ylabel(self.config.ylabel, fontsize=10)
        
        if self.config.grid:
            ax.grid(True, alpha=self.config.grid_alpha, linestyle='--')
        
        if self.config.show_legend:
            ax.legend(loc=self.config.legend_position)
        
        # Tight layout
        plt.tight_layout()
    
    def to_bytes(self, fig: Figure) -> bytes:
        """Convert figure to PNG bytes"""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=self.config.dpi, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        return buffer.getvalue()
    
    def create_risk_matrix(
        self,
        risks: List[Dict[str, Any]],
        title: str = "Risk Matrix"
    ) -> bytes:
        """
        Create risk assessment matrix
        
        Args:
            risks: List of risk dicts with 'impact', 'likelihood', 'name', 'severity'
            title: Chart title
            
        Returns:
            PNG image bytes
        """
        fig, ax = self._create_figure()
        
        # Create background grid
        impact_levels = ['Low', 'Medium', 'High', 'Critical']
        likelihood_levels = ['Rare', 'Unlikely', 'Possible', 'Likely', 'Almost Certain']
        
        # Background colors for risk zones
        colors = [
            ['#c6f6d5', '#c6f6d5', '#feebc8', '#fed7d7'],
            ['#c6f6d5', '#feebc8', '#feebc8', '#fed7d7'],
            ['#feebc8', '#feebc8', '#fed7d7', '#fed7d7'],
            ['#feebc8', '#fed7d7', '#fed7d7', '#fc8181'],
            ['#fed7d7', '#fed7d7', '#fc8181', '#fc8181']
        ]
        
        for i, row in enumerate(colors):
            for j, color in enumerate(row):
                rect = mpatches.Rectangle(
                    (j - 0.5, i - 0.5), 1, 1,
                    linewidth=1, edgecolor='white', facecolor=color
                )
                ax.add_patch(rect)
        
        # Plot risks
        severity_colors = {
            'critical': ChartColors.CRITICAL,
            'high': ChartColors.HIGH,
            'medium': ChartColors.MEDIUM,
            'low': ChartColors.LOW
        }
        
        for risk in risks:
            impact = risk.get('impact', 1) - 1  # 0-indexed
            likelihood = risk.get('likelihood', 1) - 1
            severity = risk.get('severity', 'medium').lower()
            name = risk.get('name', 'Unknown')
            
            ax.scatter(
                impact, likelihood,
                c=severity_colors.get(severity, ChartColors.INFO),
                s=200, alpha=0.8, edgecolors='white', linewidth=2,
                label=name if len(risks) <= 5 else None
            )
            
            # Add label for each point
            ax.annotate(
                name[:15] + '...' if len(name) > 15 else name,
                (impact, likelihood),
                xytext=(5, 5), textcoords='offset points',
                fontsize=8, alpha=0.8
            )
        
        ax.set_xlim(-0.5, 3.5)
        ax.set_ylim(-0.5, 4.5)
        ax.set_xticks(range(4))
        ax.set_yticks(range(5))
        ax.set_xticklabels(impact_levels)
        ax.set_yticklabels(likelihood_levels)
        ax.set_xlabel('Impact', fontsize=11, fontweight='bold')
        ax.set_ylabel('Likelihood', fontsize=11, fontweight='bold')
        
        self._apply_styling(ax, title)
        
        return self.to_bytes(fig)
    
    def create_severity_pie(
        self,
        data: Dict[str, int],
        title: str = "Findings by Severity"
    ) -> bytes:
        """
        Create severity distribution pie chart
        
        Args:
            data: Dict mapping severity to count
            title: Chart title
            
        Returns:
            PNG image bytes
        """
        fig, ax = self._create_figure()
        
        severity_order = ['critical', 'high', 'medium', 'low', 'info']
        colors_map = {
            'critical': ChartColors.CRITICAL,
            'high': ChartColors.HIGH,
            'medium': ChartColors.MEDIUM,
            'low': ChartColors.LOW,
            'info': ChartColors.INFO_SEVERITY
        }
        
        # Filter and order data
        labels = []
        values = []
        colors = []
        
        for sev in severity_order:
            if sev in data and data[sev] > 0:
                labels.append(sev.capitalize())
                values.append(data[sev])
                colors.append(colors_map[sev])
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(
            values,
            labels=labels,
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            explode=[0.05] * len(values),
            shadow=True
        )
        
        # Style text
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        self._apply_styling(ax, title)
        
        return self.to_bytes(fig)
    
    def create_trend_line(
        self,
        dates: List[str],
        values: List[float],
        title: str = "Trend Analysis",
        ylabel: str = "Count"
    ) -> bytes:
        """
        Create trend line chart
        
        Args:
            dates: Date labels
            values: Values for each date
            title: Chart title
            ylabel: Y-axis label
            
        Returns:
            PNG image bytes
        """
        fig, ax = self._create_figure()
        
        x = range(len(dates))
        
        ax.plot(
            x, values,
            color=ChartColors.PRIMARY,
            linewidth=2.5,
            marker='o',
            markersize=8,
            markerfacecolor=ChartColors.ACCENT,
            markeredgecolor='white',
            markeredgewidth=2
        )
        
        ax.fill_between(x, values, alpha=0.3, color=ChartColors.PRIMARY)
        
        ax.set_xticks(x)
        ax.set_xticklabels(dates, rotation=45, ha='right')
        ax.set_ylabel(ylabel, fontsize=11, fontweight='bold')
        
        self._apply_styling(ax, title)
        
        return self.to_bytes(fig)
    
    def create_compliance_bar(
        self,
        frameworks: List[str],
        scores: List[float],
        title: str = "Compliance Scores"
    ) -> bytes:
        """
        Create compliance score bar chart
        
        Args:
            frameworks: Framework names
            scores: Compliance scores (0-100)
            title: Chart title
            
        Returns:
            PNG image bytes
        """
        fig, ax = self._create_figure()
        
        # Color based on score
        bar_colors = []
        for score in scores:
            if score >= 80:
                bar_colors.append(ChartColors.LOW)
            elif score >= 60:
                bar_colors.append(ChartColors.MEDIUM)
            elif score >= 40:
                bar_colors.append(ChartColors.HIGH)
            else:
                bar_colors.append(ChartColors.CRITICAL)
        
        bars = ax.barh(frameworks, scores, color=bar_colors, edgecolor='white', linewidth=2)
        
        # Add score labels
        for bar, score in zip(bars, scores):
            width = bar.get_width()
            ax.text(
                width + 2, bar.get_y() + bar.get_height()/2,
                f'{score:.1f}%',
                ha='left', va='center', fontweight='bold', fontsize=10
            )
        
        ax.set_xlim(0, 110)
        ax.set_xlabel('Compliance Score (%)', fontsize=11, fontweight='bold')
        ax.axvline(x=80, color=ChartColors.LOW, linestyle='--', alpha=0.5, label='Target (80%)')
        ax.axvline(x=60, color=ChartColors.MEDIUM, linestyle='--', alpha=0.5, label='Minimum (60%)')
        
        self._apply_styling(ax, title)
        
        return self.to_bytes(fig)
    
    def create_stacked_bar(
        self,
        categories: List[str],
        data: Dict[str, List[int]],
        title: str = "Stacked Analysis"
    ) -> bytes:
        """
        Create stacked bar chart
        
        Args:
            categories: X-axis categories
            data: Dict mapping series name to values
            title: Chart title
            
        Returns:
            PNG image bytes
        """
        fig, ax = self._create_figure()
        
        x = np.arange(len(categories))
        width = 0.6
        
        bottom = np.zeros(len(categories))
        colors = ChartColors.PALETTE[:len(data)]
        
        for i, (series_name, values) in enumerate(data.items()):
            ax.bar(
                x, values, width,
                label=series_name,
                bottom=bottom,
                color=colors[i],
                edgecolor='white',
                linewidth=1
            )
            bottom += np.array(values)
        
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.set_ylabel('Count', fontsize=11, fontweight='bold')
        
        self._apply_styling(ax, title)
        
        return self.to_bytes(fig)
    
    def create_gauge_chart(
        self,
        value: float,
        max_value: float = 100,
        title: str = "Score Gauge"
    ) -> bytes:
        """
        Create gauge/score chart
        
        Args:
            value: Current value
            max_value: Maximum value
            title: Chart title
            
        Returns:
            PNG image bytes
        """
        fig, ax = self._create_figure()
        
        # Create semi-circle gauge
        theta = np.linspace(0, np.pi, 100)
        
        # Background arc
        ax.fill_between(
            np.cos(theta), np.sin(theta),
            alpha=0.1, color='gray'
        )
        
        # Color zones
        zone_colors = [ChartColors.CRITICAL, ChartColors.HIGH, ChartColors.MEDIUM, ChartColors.LOW]
        zone_starts = [0, 0.25, 0.5, 0.75]
        zone_ends = [0.25, 0.5, 0.75, 1.0]
        
        for color, start, end in zip(zone_colors, zone_starts, zone_ends):
            start_idx = int(start * 100)
            end_idx = int(end * 100)
            ax.fill_between(
                np.cos(theta[start_idx:end_idx]),
                np.sin(theta[start_idx:end_idx]),
                alpha=0.3, color=color
            )
        
        # Needle
        percentage = value / max_value
        needle_angle = np.pi * (1 - percentage)
        ax.arrow(
            0, 0,
            0.8 * np.cos(needle_angle),
            0.8 * np.sin(needle_angle),
            head_width=0.05,
            head_length=0.1,
            fc='black',
            ec='black',
            linewidth=2
        )
        
        # Center text
        ax.text(0, -0.3, f'{value:.1f}', ha='center', va='center',
                fontsize=36, fontweight='bold')
        ax.text(0, -0.5, f'/ {max_value}', ha='center', va='center',
                fontsize=14, color='gray')
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.6, 1.2)
        ax.set_aspect('equal')
        ax.axis('off')
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=20)
        
        return self.to_bytes(fig)


### 5.2 Advanced Table Generation

```python
# /app/pdf/tables/generator.py
"""
Advanced table generation for PDF reports
"""
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT


@dataclass
class ColumnDef:
    """Column definition"""
    name: str
    header: str
    width: Optional[float] = None
    align: str = 'left'
    formatter: Optional[Callable] = None
    style_override: Optional[Dict[str, Any]] = None


@dataclass
class TableConfig:
    """Table configuration"""
    header_bg_color: str = '#2c5282'
    header_text_color: str = '#ffffff'
    row_bg_colors: Tuple[str, str] = ('#f7fafc', '#ffffff')
    border_color: str = '#e2e8f0'
    font_size: int = 9
    header_font_size: int = 10
    padding: int = 8
    repeat_rows: int = 1
    

class AdvancedTableGenerator:
    """
    Generate sophisticated tables for PDF reports
    """
    
    def __init__(self, config: TableConfig = None):
        self.config = config or TableConfig()
    
    def create_table(
        self,
        columns: List[ColumnDef],
        data: List[Dict[str, Any]],
        total_row: Optional[Dict[str, Any]] = None,
        summary_text: Optional[str] = None
    ) -> Table:
        """
        Create styled table with advanced features
        
        Args:
            columns: Column definitions
            data: Row data as list of dicts
            total_row: Optional totals row
            summary_text: Optional summary text
            
        Returns:
            Styled Table object
        """
        # Build header row
        header_row = [col.header for col in columns]
        
        # Build data rows
        table_data = [header_row]
        
        for row in data:
            row_data = []
            for col in columns:
                value = row.get(col.name, '')
                if col.formatter:
                    value = col.formatter(value)
                row_data.append(str(value))
            table_data.append(row_data)
        
        # Add total row if provided
        if total_row:
            total_data = []
            for col in columns:
                value = total_row.get(col.name, '')
                if col.formatter:
                    value = col.formatter(value)
                total_data.append(str(value))
            table_data.append(total_data)
        
        # Calculate column widths
        col_widths = [col.width for col in columns]
        
        # Create table
        table = Table(table_data, colWidths=col_widths, repeatRows=self.config.repeat_rows)
        
        # Apply styling
        style = self._build_table_style(len(table_data), len(columns), total_row is not None)
        table.setStyle(style)
        
        return table
    
    def _build_table_style(
        self,
        row_count: int,
        col_count: int,
        has_total: bool
    ) -> TableStyle:
        """Build comprehensive table style"""
        style_commands = [
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(self.config.header_bg_color)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor(self.config.header_text_color)),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), self.config.header_font_size),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), self.config.padding),
            ('TOPPADDING', (0, 0), (-1, 0), self.config.padding),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor(self.config.border_color)),
            ('BOX', (0, 0), (-1, -1), 1, colors.HexColor(self.config.border_color)),
            
            # Body styling
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), self.config.font_size),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 1), (-1, -1), self.config.padding - 2),
            ('BOTTOMPADDING', (0, 1), (-1, -1), self.config.padding - 2),
        ]
        
        # Alternating row colors
        for i in range(1, row_count):
            bg_color = self.config.row_bg_colors[i % 2]
            style_commands.append(
                ('BACKGROUND', (0, i), (-1, i), colors.HexColor(bg_color))
            )
        
        # Total row styling
        if has_total:
            style_commands.extend([
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#edf2f7')),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('LINEABOVE', (0, -1), (-1, -1), 1, colors.HexColor('#2c5282')),
            ])
        
        return TableStyle(style_commands)
    
    def create_severity_table(
        self,
        findings: List[Dict[str, Any]],
        include_description: bool = True
    ) -> Table:
        """
        Create vulnerability findings table with severity styling
        
        Args:
            findings: List of finding dicts
            include_description: Whether to include description column
            
        Returns:
            Styled Table
        """
        columns = [
            ColumnDef('id', 'ID', width=60, align='center'),
            ColumnDef('severity', 'Severity', width=80, align='center'),
            ColumnDef('title', 'Title', width=200),
        ]
        
        if include_description:
            columns.append(ColumnDef('description', 'Description', width=250))
        
        columns.extend([
            ColumnDef('cvss', 'CVSS', width=50, align='center'),
            ColumnDef('status', 'Status', width=80, align='center'),
        ])
        
        # Format data
        formatted_data = []
        for finding in findings:
            formatted_data.append({
                'id': finding.get('id', 'N/A'),
                'severity': finding.get('severity', 'Unknown').upper(),
                'title': finding.get('title', 'Untitled'),
                'description': finding.get('description', '')[:100] + '...' if include_description else '',
                'cvss': f"{finding.get('cvss_score', 0):.1f}",
                'status': finding.get('status', 'Open')
            })
        
        table = self.create_table(columns, formatted_data)
        
        # Add severity color coding
        style_commands = list(table._style._cmds)
        
        severity_colors = {
            'CRITICAL': ('#fed7d7', '#c53030'),
            'HIGH': ('#feebc8', '#dd6b20'),
            'MEDIUM': ('#fefcbf', '#d69e2e'),
            'LOW': ('#c6f6d5', '#38a169'),
        }
        
        for row_idx, finding in enumerate(findings, start=1):
            severity = finding.get('severity', 'Unknown').upper()
            if severity in severity_colors:
                bg_color, text_color = severity_colors[severity]
                style_commands.extend([
                    ('BACKGROUND', (1, row_idx), (1, row_idx), colors.HexColor(bg_color)),
                    ('TEXTCOLOR', (1, row_idx), (1, row_idx), colors.HexColor(text_color)),
                    ('FONTNAME', (1, row_idx), (1, row_idx), 'Helvetica-Bold'),
                ])
        
        table.setStyle(TableStyle(style_commands))
        return table
    
    def create_risk_register_table(
        self,
        risks: List[Dict[str, Any]]
    ) -> Table:
        """
        Create risk register table
        
        Args:
            risks: List of risk dicts
            
        Returns:
            Styled Table
        """
        columns = [
            ColumnDef('id', 'Risk ID', width=60),
            ColumnDef('description', 'Risk Description', width=200),
            ColumnDef('category', 'Category', width=80),
            ColumnDef('probability', 'Probability', width=70, align='center'),
            ColumnDef('impact', 'Impact', width=60, align='center'),
            ColumnDef('score', 'Score', width=50, align='center'),
            ColumnDef('owner', 'Owner', width=80),
            ColumnDef('status', 'Status', width=70, align='center'),
        ]
        
        # Format data
        formatted_data = []
        for risk in risks:
            prob = risk.get('probability', 1)
            impact = risk.get('impact', 1)
            score = prob * impact
            
            formatted_data.append({
                'id': risk.get('id', 'R-XXX'),
                'description': risk.get('description', '')[:80] + '...',
                'category': risk.get('category', 'General'),
                'probability': f"{prob}/5",
                'impact': f"{impact}/5",
                'score': str(score),
                'owner': risk.get('owner', 'Unassigned'),
                'status': risk.get('status', 'Active')
            })
        
        return self.create_table(columns, formatted_data)


# Utility formatters
def format_currency(value: float, currency: str = '$') -> str:
    """Format as currency"""
    return f"{currency}{value:,.2f}"

def format_percentage(value: float, decimals: int = 1) -> str:
    """Format as percentage"""
    return f"{value:.{decimals}f}%"

def format_date(value: Any, fmt: str = '%Y-%m-%d') -> str:
    """Format date"""
    if hasattr(value, 'strftime'):
        return value.strftime(fmt)
    return str(value)

def format_number(value: float, decimals: int = 0) -> str:
    """Format number with commas"""
    return f"{value:,.{decimals}f}"
```

---

## 6. Multi-Page Report Handling

### 6.1 Page Management System

```python
# /app/pdf/generation/pagination.py
"""
Multi-page report pagination and management
"""
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

from reportlab.platypus import PageBreak, KeepTogether, CondPageBreak
from reportlab.lib.units import inch

logger = logging.getLogger(__name__)


class PageSection(Enum):
    """Page section types"""
    COVER = "cover"
    TOC = "table_of_contents"
    EXECUTIVE_SUMMARY = "executive_summary"
    BODY = "body"
    APPENDIX = "appendix"
    BACK_COVER = "back_cover"


@dataclass
class PageInfo:
    """Information about a page"""
    number: int
    section: PageSection
    title: Optional[str] = None
    has_header: bool = True
    has_footer: bool = True
    page_number_format: str = "numeric"  # numeric, roman, alpha


@dataclass
class PaginationConfig:
    """Pagination configuration"""
    min_lines_before_break: int = 3
    keep_together_threshold: float = 4 * inch
    orphan_control: bool = True
    widow_control: bool = True
    section_breaks: bool = True


class PageManager:
    """
    Manages multi-page report pagination
    """
    
    def __init__(self, config: PaginationConfig = None):
        self.config = config or PaginationConfig()
        self.sections: List[Tuple[PageSection, List[Any]]] = []
        self.current_section: Optional[PageSection] = None
        self.current_elements: List[Any] = []
    
    def start_section(
        self,
        section: PageSection,
        force_new_page: bool = True
    ) -> 'PageManager':
        """Start a new document section"""
        # Save current section
        if self.current_section and self.current_elements:
            self.sections.append((self.current_section, self.current_elements))
        
        self.current_section = section
        self.current_elements = []
        
        if force_new_page and self.sections:
            self.current_elements.append(PageBreak())
        
        return self
    
    def add_element(
        self,
        element: Any,
        keep_together: bool = False
    ) -> 'PageManager':
        """Add element to current section"""
        if keep_together:
            element = KeepTogether(element, maxHeight=self.config.keep_together_threshold)
        
        self.current_elements.append(element)
        return self
    
    def add_elements(self, elements: List[Any]) -> 'PageManager':
        """Add multiple elements"""
        for element in elements:
            self.add_element(element)
        return self
    
    def add_conditional_break(self, space_required: float = 2 * inch):
        """Add conditional page break"""
        self.current_elements.append(CondPageBreak(space_required))
        return self
    
    def get_all_elements(self) -> List[Any]:
        """Get all elements with proper pagination"""
        all_elements = []
        
        # Save final section
        if self.current_section and self.current_elements:
            self.sections.append((self.current_section, self.current_elements))
        
        for section, elements in self.sections:
            all_elements.extend(elements)
        
        return all_elements
    
    def estimate_page_count(
        self,
        content_height: float,
        page_height: float
    ) -> int:
        """Estimate total page count"""
        # Rough estimation based on content
        return max(1, int(content_height / (page_height * 0.8)))


class TableOfContentsGenerator:
    """
    Generate table of contents for multi-page reports
    """
    
    def __init__(self, title: str = "Table of Contents"):
        self.title = title
        self.entries: List[Dict[str, Any]] = []
    
    def add_entry(
        self,
        title: str,
        level: int = 1,
        page_number: Optional[int] = None
    ) -> 'TableOfContentsGenerator':
        """Add TOC entry"""
        self.entries.append({
            'title': title,
            'level': level,
            'page_number': page_number
        })
        return self
    
    def generate_toc_data(self) -> List[List[str]]:
        """Generate TOC table data"""
        data = [['Section', 'Page']]
        
        for entry in self.entries:
            indent = '    ' * (entry['level'] - 1)
            title = f"{indent}{entry['title']}"
            page = str(entry.get('page_number', '...'))
            data.append([title, page])
        
        return data
    
    def create_toc_table(self, table_generator) -> Any:
        """Create TOC as table"""
        from reportlab.platypus import Table, TableStyle
        from reportlab.lib import colors
        
        data = self.generate_toc_data()
        
        table = Table(data, colWidths=[400, 50])
        
        style = TableStyle([
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2c5282')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ])
        
        table.setStyle(style)
        return table


class CoverPageGenerator:
    """
    Generate professional cover pages
    """
    
    def __init__(self, branding_config: Dict[str, Any] = None):
        self.branding = branding_config or {}
    
    def generate_cover_elements(
        self,
        title: str,
        subtitle: Optional[str] = None,
        report_date: Optional[str] = None,
        organization: Optional[str] = None,
        classification: Optional[str] = None,
        logo_path: Optional[str] = None
    ) -> List[Any]:
        """Generate cover page elements"""
        from reportlab.platypus import Paragraph, Spacer, Image, Table
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        elements = []
        
        # Logo
        if logo_path:
            try:
                logo = Image(logo_path, width=2*inch, height=1*inch)
                elements.append(logo)
                elements.append(Spacer(1, 1*inch))
            except:
                pass
        
        # Classification banner
        if classification:
            class_style = ParagraphStyle(
                'Classification',
                fontSize=14,
                textColor=colors.white,
                backColor=colors.HexColor('#c53030') if 'CONFIDENTIAL' in classification.upper() else colors.HexColor('#d69e2e'),
                alignment=1,  # Center
                spaceAfter=20,
                spaceBefore=20,
                padding=10
            )
            elements.append(Paragraph(classification.upper(), class_style))
        
        # Title
        title_style = ParagraphStyle(
            'CoverTitle',
            fontSize=32,
            leading=40,
            textColor=colors.HexColor('#1a365d'),
            alignment=1,  # Center
            spaceAfter=20,
            fontName='Helvetica-Bold'
        )
        elements.append(Paragraph(title, title_style))
        
        # Subtitle
        if subtitle:
            subtitle_style = ParagraphStyle(
                'CoverSubtitle',
                fontSize=16,
                leading=22,
                textColor=colors.HexColor('#4a5568'),
                alignment=1,
                spaceAfter=30
            )
            elements.append(Paragraph(subtitle, subtitle_style))
        
        elements.append(Spacer(1, 1*inch))
        
        # Metadata table
        meta_data = []
        if organization:
            meta_data.append(['Organization:', organization])
        if report_date:
            meta_data.append(['Date:', report_date])
        meta_data.append(['Generated by:', 'ResilienceAI'])
        
        if meta_data:
            meta_table = Table(meta_data, colWidths=[100, 250])
            meta_table.setStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ])
            elements.append(meta_table)
        
        return elements
```

---

## 7. Styling & Formatting System

### 7.1 Theme and Style Management

```python
# /app/pdf/styling/themes.py
"""
PDF theming and styling system
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY


class ColorScheme(Enum):
    """Predefined color schemes"""
    CORPORATE = "corporate"
    SECURITY = "security"
    HEALTHCARE = "healthcare"
    FINANCIAL = "financial"
    DARK = "dark"
    HIGH_CONTRAST = "high_contrast"


@dataclass
class ThemeColors:
    """Theme color palette"""
    primary: str = '#2c5282'
    secondary: str = '#38a169'
    accent: str = '#ed8936'
    danger: str = '#e53e3e'
    warning: str = '#d69e2e'
    success: str = '#38a169'
    info: str = '#3182ce'
    
    # Text colors
    text_primary: str = '#1a202c'
    text_secondary: str = '#4a5568'
    text_muted: str = '#718096'
    
    # Background colors
    bg_primary: str = '#ffffff'
    bg_secondary: str = '#f7fafc'
    bg_tertiary: str = '#edf2f7'
    
    # Border colors
    border_light: str = '#e2e8f0'
    border_medium: str = '#cbd5e0'
    
    # Severity colors
    critical: str = '#c53030'
    high: str = '#dd6b20'
    medium: str = '#d69e2e'
    low: str = '#38a169'


@dataclass
class Typography:
    """Typography settings"""
    font_family: str = 'Helvetica'
    font_family_bold: str = 'Helvetica-Bold'
    font_family_italic: str = 'Helvetica-Oblique'
    
    # Font sizes
    size_title: int = 24
    size_h1: int = 18
    size_h2: int = 14
    size_h3: int = 12
    size_body: int = 10
    size_small: int = 9
    size_caption: int = 8
    
    # Line heights
    leading_title: int = 30
    leading_h1: int = 24
    leading_h2: int = 18
    leading_h3: int = 16
    leading_body: int = 14


@dataclass
class Spacing:
    """Spacing settings"""
    xs: float = 4
    sm: float = 8
    md: float = 12
    lg: float = 18
    xl: float = 24
    xxl: float = 36


@dataclass
class PDFTheme:
    """Complete PDF theme"""
    name: str
    colors: ThemeColors = field(default_factory=ThemeColors)
    typography: Typography = field(default_factory=Typography)
    spacing: Spacing = field(default_factory=Spacing)
    
    # Custom styles
    custom_styles: Dict[str, Dict[str, Any]] = field(default_factory=dict)


class ThemeManager:
    """
    Manage PDF themes
    """
    
    # Predefined themes
    THEMES = {
        ColorScheme.CORPORATE: PDFTheme(
            name="Corporate",
            colors=ThemeColors(
                primary='#1a365d',
                secondary='#2c5282',
                accent='#3182ce',
                danger='#c53030',
                warning='#d69e2e',
                success='#38a169'
            )
        ),
        ColorScheme.SECURITY: PDFTheme(
            name="Security",
            colors=ThemeColors(
                primary='#1a202c',
                secondary='#2d3748',
                accent='#e53e3e',
                danger='#c53030',
                warning='#dd6b20',
                success='#276749',
                critical='#9b2c2c',
                high='#c05621',
                medium='#d69e2e',
                low='#38a169'
            )
        ),
        ColorScheme.HEALTHCARE: PDFTheme(
            name="Healthcare",
            colors=ThemeColors(
                primary='#2b6cb0',
                secondary='#38b2ac',
                accent='#4299e1',
                danger='#e53e3e',
                warning='#ecc94b',
                success='#48bb78'
            )
        ),
        ColorScheme.FINANCIAL: PDFTheme(
            name="Financial",
            colors=ThemeColors(
                primary='#276749',
                secondary='#2f855a',
                accent='#38a169',
                danger='#c53030',
                warning='#d69e2e',
                success='#276749'
            )
        ),
        ColorScheme.HIGH_CONTRAST: PDFTheme(
            name="High Contrast",
            colors=ThemeColors(
                primary='#000000',
                secondary='#333333',
                accent='#0066cc',
                danger='#cc0000',
                warning='#ff6600',
                success='#006600',
                text_primary='#000000',
                text_secondary='#333333',
                bg_primary='#ffffff',
                border_light='#000000'
            )
        ),
    }
    
    @classmethod
    def get_theme(cls, scheme: ColorScheme) -> PDFTheme:
        """Get theme by color scheme"""
        return cls.THEMES.get(scheme, cls.THEMES[ColorScheme.CORPORATE])
    
    @classmethod
    def create_paragraph_styles(cls, theme: PDFTheme) -> Dict[str, ParagraphStyle]:
        """Create paragraph styles from theme"""
        t = theme.typography
        c = theme.colors
        
        return {
            'Title': ParagraphStyle(
                'ThemeTitle',
                fontName=t.font_family_bold,
                fontSize=t.size_title,
                leading=t.leading_title,
                textColor=colors.HexColor(c.primary),
                spaceAfter=theme.spacing.lg
            ),
            'Heading1': ParagraphStyle(
                'ThemeH1',
                fontName=t.font_family_bold,
                fontSize=t.size_h1,
                leading=t.leading_h1,
                textColor=colors.HexColor(c.primary),
                spaceAfter=theme.spacing.md,
                spaceBefore=theme.spacing.lg
            ),
            'Heading2': ParagraphStyle(
                'ThemeH2',
                fontName=t.font_family_bold,
                fontSize=t.size_h2,
                leading=t.leading_h2,
                textColor=colors.HexColor(c.secondary),
                spaceAfter=theme.spacing.sm,
                spaceBefore=theme.spacing.md
            ),
            'Heading3': ParagraphStyle(
                'ThemeH3',
                fontName=t.font_family_bold,
                fontSize=t.size_h3,
                leading=t.leading_h3,
                textColor=colors.HexColor(c.text_primary),
                spaceAfter=theme.spacing.sm,
                spaceBefore=theme.spacing.sm
            ),
            'BodyText': ParagraphStyle(
                'ThemeBody',
                fontName=t.font_family,
                fontSize=t.size_body,
                leading=t.leading_body,
                textColor=colors.HexColor(c.text_primary),
                spaceAfter=theme.spacing.sm
            ),
            'BodyTextBold': ParagraphStyle(
                'ThemeBodyBold',
                fontName=t.font_family_bold,
                fontSize=t.size_body,
                leading=t.leading_body,
                textColor=colors.HexColor(c.text_primary),
                spaceAfter=theme.spacing.sm
            ),
            'Caption': ParagraphStyle(
                'ThemeCaption',
                fontName=t.font_family_italic,
                fontSize=t.size_caption,
                leading=t.size_caption + 2,
                textColor=colors.HexColor(c.text_muted),
                alignment=TA_CENTER
            ),
            'AlertCritical': ParagraphStyle(
                'ThemeAlertCritical',
                fontName=t.font_family_bold,
                fontSize=t.size_body,
                leading=t.leading_body,
                textColor=colors.HexColor(c.critical),
                backColor=colors.HexColor('#fed7d7'),
                leftIndent=theme.spacing.sm,
                rightIndent=theme.spacing.sm,
                spaceAfter=theme.spacing.md
            ),
            'AlertHigh': ParagraphStyle(
                'ThemeAlertHigh',
                fontName=t.font_family_bold,
                fontSize=t.size_body,
                leading=t.leading_body,
                textColor=colors.HexColor(c.high),
                backColor=colors.HexColor('#feebc8'),
                leftIndent=theme.spacing.sm,
                rightIndent=theme.spacing.sm,
                spaceAfter=theme.spacing.md
            ),
            'AlertMedium': ParagraphStyle(
                'ThemeAlertMedium',
                fontName=t.font_family,
                fontSize=t.size_body,
                leading=t.leading_body,
                textColor=colors.HexColor(c.warning),
                backColor=colors.HexColor('#fefcbf'),
                leftIndent=theme.spacing.sm,
                rightIndent=theme.spacing.sm,
                spaceAfter=theme.spacing.md
            ),
            'AlertLow': ParagraphStyle(
                'ThemeAlertLow',
                fontName=t.font_family,
                fontSize=t.size_body,
                leading=t.leading_body,
                textColor=colors.HexColor(c.low),
                backColor=colors.HexColor('#c6f6d5'),
                leftIndent=theme.spacing.sm,
                rightIndent=theme.spacing.sm,
                spaceAfter=theme.spacing.md
            ),
        }
```

---

## 8. Header/Footer Management

### 8.1 Header/Footer System

```python
# /app/pdf/generation/headers_footers.py
"""
Header and footer management for PDF reports
"""
from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from enum import Enum
from reportlab.lib import colors
from reportlab.lib.units import inch, mm
from reportlab.pdfgen.canvas import Canvas
import datetime


class HeaderStyle(Enum):
    """Header style options"""
    NONE = "none"
    SIMPLE = "simple"
    DETAILED = "detailed"
    BRANDED = "branded"


class FooterStyle(Enum):
    """Footer style options"""
    NONE = "none"
    SIMPLE = "simple"
    DETAILED = "detailed"
    BRANDED = "branded"


@dataclass
class HeaderConfig:
    """Header configuration"""
    style: HeaderStyle = HeaderStyle.SIMPLE
    show_logo: bool = False
    logo_path: Optional[str] = None
    show_title: bool = True
    show_date: bool = False
    show_classification: bool = False
    classification_text: Optional[str] = None
    height: float = 0.5 * inch
    line_color: str = '#e2e8f0'


@dataclass
class FooterConfig:
    """Footer configuration"""
    style: FooterStyle = FooterStyle.SIMPLE
    show_page_numbers: bool = True
    show_date: bool = True
    show_copyright: bool = True
    copyright_text: str = "© ResilienceAI"
    show_confidentiality: bool = False
    confidentiality_text: Optional[str] = None
    height: float = 0.5 * inch
    line_color: str = '#e2e8f0'


class HeaderFooterManager:
    """
    Manage headers and footers for PDF documents
    """
    
    def __init__(
        self,
        header_config: HeaderConfig = None,
        footer_config: FooterConfig = None
    ):
        self.header_config = header_config or HeaderConfig()
        self.footer_config = footer_config or FooterConfig()
    
    def create_header_function(
        self,
        document_title: str,
        metadata: Dict[str, Any] = None
    ) -> Callable:
        """
        Create header drawing function
        
        Returns a function that can be passed to ReportLab canvas
        """
        config = self.header_config
        
        def draw_header(canvas: Canvas, page_num: int, page_count: int, data: Dict):
            """Draw header on each page"""
            if config.style == HeaderStyle.NONE:
                return
            
            width = canvas._pagesize[0]
            height = canvas._pagesize[1]
            header_y = height - config.height
            
            # Draw classification banner if enabled
            if config.show_classification and config.classification_text:
                banner_height = 20
                canvas.setFillColor(colors.HexColor('#c53030'))
                canvas.rect(0, height - banner_height, width, banner_height, fill=1, stroke=0)
                canvas.setFillColor(colors.white)
                canvas.setFont('Helvetica-Bold', 10)
                canvas.drawCentredString(width/2, height - banner_height + 6, 
                                         config.classification_text.upper())
                header_y -= banner_height
            
            # Draw header line
            canvas.setStrokeColor(colors.HexColor(config.line_color))
            canvas.setLineWidth(0.5)
            canvas.line(72, header_y, width - 72, header_y)
            
            # Draw content based on style
            if config.style == HeaderStyle.SIMPLE:
                # Simple: just title
                if config.show_title:
                    canvas.setFillColor(colors.HexColor('#2c5282'))
                    canvas.setFont('Helvetica-Bold', 10)
                    canvas.drawString(72, header_y - 15, document_title)
                
                if config.show_date:
                    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
                    canvas.setFont('Helvetica', 9)
                    canvas.setFillColor(colors.HexColor('#718096'))
                    canvas.drawRightString(width - 72, header_y - 15, date_str)
            
            elif config.style == HeaderStyle.DETAILED:
                # Detailed: title, section, date
                if config.show_title:
                    canvas.setFillColor(colors.HexColor('#2c5282'))
                    canvas.setFont('Helvetica-Bold', 10)
                    canvas.drawString(72, header_y - 15, document_title)
                
                # Page info
                canvas.setFont('Helvetica', 9)
                canvas.setFillColor(colors.HexColor('#718096'))
                page_info = f"Page {page_num} of {page_count}"
                canvas.drawCentredString(width/2, header_y - 15, page_info)
                
                if config.show_date:
                    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
                    canvas.drawRightString(width - 72, header_y - 15, date_str)
            
            elif config.style == HeaderStyle.BRANDED:
                # Branded: logo, title, page number
                if config.show_logo and config.logo_path:
                    try:
                        canvas.drawImage(config.logo_path, 72, header_y - 25, 
                                        width=0.8*inch, height=0.4*inch, preserveAspectRatio=True)
                    except:
                        pass
                
                if config.show_title:
                    canvas.setFillColor(colors.HexColor('#1a365d'))
                    canvas.setFont('Helvetica-Bold', 11)
                    canvas.drawString(150, header_y - 15, document_title)
                
                canvas.setFont('Helvetica', 9)
                canvas.setFillColor(colors.HexColor('#718096'))
                canvas.drawRightString(width - 72, header_y - 15, f"Page {page_num}")
        
        return draw_header
    
    def create_footer_function(
        self,
        document_title: str = "",
        metadata: Dict[str, Any] = None
    ) -> Callable:
        """
        Create footer drawing function
        
        Returns a function that can be passed to ReportLab canvas
        """
        config = self.footer_config
        
        def draw_footer(canvas: Canvas, page_num: int, page_count: int, data: Dict):
            """Draw footer on each page"""
            if config.style == FooterStyle.NONE:
                return
            
            width = canvas._pagesize[0]
            footer_y = config.height - 20
            
            # Draw footer line
            canvas.setStrokeColor(colors.HexColor(config.line_color))
            canvas.setLineWidth(0.5)
            canvas.line(72, footer_y + 10, width - 72, footer_y + 10)
            
            # Draw content based on style
            if config.style == FooterStyle.SIMPLE:
                # Simple: page numbers and copyright
                canvas.setFillColor(colors.HexColor('#718096'))
                canvas.setFont('Helvetica', 8)
                
                if config.show_page_numbers:
                    canvas.drawCentredString(width/2, footer_y - 5, 
                                            f"Page {page_num} of {page_count}")
                
                if config.show_copyright:
                    canvas.drawRightString(width - 72, footer_y - 5, config.copyright_text)
            
            elif config.style == FooterStyle.DETAILED:
                # Detailed: copyright, page numbers, date
                canvas.setFillColor(colors.HexColor('#718096'))
                canvas.setFont('Helvetica', 8)
                
                # Left: copyright
                if config.show_copyright:
                    canvas.drawString(72, footer_y - 5, config.copyright_text)
                
                # Center: page numbers
                if config.show_page_numbers:
                    canvas.drawCentredString(width/2, footer_y - 5, 
                                            f"Page {page_num} of {page_count}")
                
                # Right: date
                if config.show_date:
                    date_str = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
                    canvas.drawRightString(width - 72, footer_y - 5, date_str)
            
            elif config.style == FooterStyle.BRANDED:
                # Branded: logo mark, page numbers, confidentiality
                canvas.setFillColor(colors.HexColor('#718096'))
                canvas.setFont('Helvetica', 8)
                
                # Left: brand mark
                canvas.setFillColor(colors.HexColor('#2c5282'))
                canvas.setFont('Helvetica-Bold', 8)
                canvas.drawString(72, footer_y - 5, "ResilienceAI")
                
                # Center: page numbers
                canvas.setFillColor(colors.HexColor('#718096'))
                canvas.setFont('Helvetica', 8)
                if config.show_page_numbers:
                    canvas.drawCentredString(width/2, footer_y - 5, 
                                            f"{page_num} / {page_count}")
                
                # Right: confidentiality
                if config.show_confidentiality and config.confidentiality_text:
                    canvas.setFillColor(colors.HexColor('#c53030'))
                    canvas.setFont('Helvetica-Bold', 8)
                    canvas.drawRightString(width - 72, footer_y - 5, 
                                          config.confidentiality_text.upper())
            
            # Draw confidentiality banner if enabled
            if config.show_confidentiality and config.confidentiality_text:
                banner_height = 15
                canvas.setFillColor(colors.HexColor('#c53030'))
                canvas.rect(0, 0, width, banner_height, fill=1, stroke=0)
                canvas.setFillColor(colors.white)
                canvas.setFont('Helvetica-Bold', 8)
                canvas.drawCentredString(width/2, 4, config.confidentiality_text.upper())
        
        return draw_footer
    
    @classmethod
    def executive_config(cls, classification: Optional[str] = None) -> 'HeaderFooterManager':
        """Create executive report header/footer config"""
        return cls(
            header_config=HeaderConfig(
                style=HeaderStyle.BRANDED,
                show_title=True,
                show_classification=classification is not None,
                classification_text=classification
            ),
            footer_config=FooterConfig(
                style=FooterStyle.BRANDED,
                show_page_numbers=True,
                show_confidentiality=classification is not None,
                confidentiality_text=classification
            )
        )
    
    @classmethod
    def technical_config(cls) -> 'HeaderFooterManager':
        """Create technical report header/footer config"""
        return cls(
            header_config=HeaderConfig(
                style=HeaderStyle.DETAILED,
                show_title=True,
                show_date=True
            ),
            footer_config=FooterConfig(
                style=FooterStyle.DETAILED,
                show_page_numbers=True,
                show_date=True,
                show_copyright=True
            )
        )
    
    @classmethod
    def minimal_config(cls) -> 'HeaderFooterManager':
        """Create minimal header/footer config"""
        return cls(
            header_config=HeaderConfig(style=HeaderStyle.NONE),
            footer_config=FooterConfig(
                style=FooterStyle.SIMPLE,
                show_page_numbers=True
            )
        )
```



---

## 9. PDF Export API

### 9.1 FastAPI Export Endpoints

```python
# /app/api/v1/endpoints/pdf_export.py
"""
PDF Export API Endpoints
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field
from datetime import datetime
import io
import logging

from app.core.security import get_current_user
from app.models.user import User
from app.pdf.generation.reportlab_engine import ReportLabPDFGenerator
from app.pdf.generation.base import PDFMetadata, PageSettings
from app.pdf.templates.builder import TemplateBuilder, SectionContent
from app.pdf.charts.generator import ChartGenerator, ChartConfig
from app.pdf.tables.generator import AdvancedTableGenerator
from app.pdf.export_service import PDFExportService

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response Models

class PDFExportRequest(BaseModel):
    """PDF export request"""
    report_type: str = Field(..., description="Type of report to generate")
    template_id: Optional[str] = Field(None, description="Specific template to use")
    title: str = Field(..., description="Report title")
    subtitle: Optional[str] = None
    data: Dict[str, Any] = Field(default_factory=dict, description="Report data")
    include_charts: bool = True
    include_tables: bool = True
    page_size: str = "letter"  # letter, a4, legal
    orientation: str = "portrait"  # portrait, landscape
    
    class Config:
        json_schema_extra = {
            "example": {
                "report_type": "risk_assessment",
                "title": "Q4 2024 Risk Assessment Report",
                "data": {
                    "organization": "Acme Corp",
                    "assessment_date": "2024-12-01",
                    "risks": []
                }
            }
        }


class PDFExportResponse(BaseModel):
    """PDF export response"""
    success: bool
    message: str
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    page_count: Optional[int] = None
    download_token: Optional[str] = None


class BatchExportRequest(BaseModel):
    """Batch PDF export request"""
    exports: List[PDFExportRequest]
    compress: bool = True
    delivery_method: str = "download"  # download, email, storage
    email_address: Optional[str] = None


class BatchExportResponse(BaseModel):
    """Batch export response"""
    job_id: str
    status: str
    total_exports: int
    completed_exports: int = 0
    failed_exports: int = 0
    download_url: Optional[str] = None


class ExportStatusResponse(BaseModel):
    """Export job status"""
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: float
    message: Optional[str] = None
    download_url: Optional[str] = None
    expires_at: Optional[datetime] = None


# API Endpoints

@router.post("/export", response_model=PDFExportResponse)
async def export_pdf(
    request: PDFExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> PDFExportResponse:
    """
    Export single PDF report
    
    Generates a PDF report based on the provided configuration and data.
    """
    try:
        export_service = PDFExportService()
        
        result = await export_service.generate_pdf(
            request=request,
            user_id=str(current_user.id),
            background_tasks=background_tasks
        )
        
        return PDFExportResponse(
            success=True,
            message="PDF generated successfully",
            file_url=result.get("file_url"),
            file_size=result.get("file_size"),
            page_count=result.get("page_count"),
            download_token=result.get("download_token")
        )
        
    except Exception as e:
        logger.error(f"PDF export failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")


@router.post("/export/batch", response_model=BatchExportResponse)
async def batch_export_pdf(
    request: BatchExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
) -> BatchExportResponse:
    """
    Export multiple PDFs in batch
    
    Creates a batch job for generating multiple PDF reports.
    """
    try:
        export_service = PDFExportService()
        
        job = await export_service.create_batch_job(
            request=request,
            user_id=str(current_user.id)
        )
        
        # Start batch processing in background
        background_tasks.add_task(
            export_service.process_batch_job,
            job_id=job["job_id"]
        )
        
        return BatchExportResponse(
            job_id=job["job_id"],
            status="pending",
            total_exports=len(request.exports)
        )
        
    except Exception as e:
        logger.error(f"Batch export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch export failed: {str(e)}")


@router.get("/export/status/{job_id}", response_model=ExportStatusResponse)
async def get_export_status(
    job_id: str,
    current_user: User = Depends(get_current_user)
) -> ExportStatusResponse:
    """
    Get status of batch export job
    """
    export_service = PDFExportService()
    status = await export_service.get_job_status(job_id)
    
    if not status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return ExportStatusResponse(**status)


@router.get("/export/download/{token}")
async def download_pdf(token: str):
    """
    Download generated PDF using token
    """
    export_service = PDFExportService()
    
    file_info = await export_service.validate_download_token(token)
    if not file_info:
        raise HTTPException(status_code=404, detail="Invalid or expired download token")
    
    return FileResponse(
        path=file_info["path"],
        filename=file_info["filename"],
        media_type="application/pdf"
    )


@router.get("/export/stream/{report_id}")
async def stream_pdf(
    report_id: str,
    current_user: User = Depends(get_current_user)
):
    """
    Stream PDF report directly
    
    Useful for large reports that shouldn't be stored temporarily.
    """
    try:
        export_service = PDFExportService()
        
        pdf_bytes = await export_service.generate_pdf_stream(
            report_id=report_id,
            user_id=str(current_user.id)
        )
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=report_{report_id}.pdf"
            }
        )
        
    except Exception as e:
        logger.error(f"PDF stream failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF stream failed: {str(e)}")


@router.get("/templates")
async def list_templates(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    """
    List available PDF templates
    """
    from app.pdf.templates.registry import template_registry
    
    templates = template_registry.list_templates()
    
    if category:
        templates = [t for t in templates if t.category.value == category]
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "description": t.description,
            "category": t.category.value,
            "report_type": t.report_type.value,
            "sections": [s.name for s in t.sections]
        }
        for t in templates
    ]


@router.post("/export/preview")
async def preview_pdf(
    request: PDFExportRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Generate PDF preview (first page only)
    
    Useful for quick preview before full export.
    """
    try:
        export_service = PDFExportService()
        
        preview_bytes = await export_service.generate_preview(
            request=request,
            user_id=str(current_user.id)
        )
        
        return StreamingResponse(
            io.BytesIO(preview_bytes),
            media_type="application/pdf"
        )
        
    except Exception as e:
        logger.error(f"PDF preview failed: {e}")
        raise HTTPException(status_code=500, detail=f"PDF preview failed: {str(e)}")


# Export Service Implementation

class PDFExportService:
    """
    PDF Export Service
    Handles PDF generation, storage, and delivery
    """
    
    def __init__(self):
        self.storage_path = "/app/storage/pdfs"
        self.temp_path = "/app/storage/temp"
        self.chart_generator = ChartGenerator()
        self.table_generator = AdvancedTableGenerator()
    
    async def generate_pdf(
        self,
        request: PDFExportRequest,
        user_id: str,
        background_tasks=None
    ) -> Dict[str, Any]:
        """Generate single PDF report"""
        
        # Create metadata
        metadata = PDFMetadata(
            title=request.title,
            author=f"ResilienceAI - User {user_id}",
            subject=request.subtitle or request.report_type,
            keywords=[request.report_type, "security", "report"]
        )
        
        # Build PDF using template
        builder = TemplateBuilder(
            template_id=request.template_id or f"{request.report_type}_v1"
        )
        
        builder.set_metadata(metadata)
        
        # Add sections based on report type
        if request.report_type == "risk_assessment":
            await self._build_risk_assessment(builder, request.data)
        elif request.report_type == "vulnerability_scan":
            await self._build_vulnerability_scan(builder, request.data)
        elif request.report_type == "executive_summary":
            await self._build_executive_summary(builder, request.data)
        else:
            await self._build_generic_report(builder, request.data)
        
        # Generate PDF
        generator = builder.build()
        pdf_bytes = generator.generate(return_bytes=True)
        
        # Save to storage
        filename = f"{request.report_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = f"{self.storage_path}/{filename}"
        
        import os
        os.makedirs(self.storage_path, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(pdf_bytes)
        
        # Generate download token
        download_token = self._generate_download_token(file_path, filename)
        
        return {
            "file_url": f"/api/v1/pdf/export/download/{download_token}",
            "file_size": len(pdf_bytes),
            "page_count": len(generator.elements) // 5,  # Rough estimate
            "download_token": download_token
        }
    
    async def _build_risk_assessment(
        self,
        builder: TemplateBuilder,
        data: Dict[str, Any]
    ):
        """Build risk assessment report sections"""
        
        # Executive Summary
        builder.add_section_content("executive_summary", SectionContent(
            section_name="executive_summary",
            title="Executive Summary",
            paragraphs=[
                f"This risk assessment was conducted for {data.get('organization', 'the organization')} "
                f"on {data.get('assessment_date', 'the specified date')}.",
                f"A total of {len(data.get('risks', []))} risks were identified and analyzed."
            ]
        ))
        
        # Risk Matrix Chart
        if data.get('risks'):
            chart_bytes = self.chart_generator.create_risk_matrix(
                data['risks'],
                title="Risk Distribution Matrix"
            )
            builder.add_section_content("risk_matrix", SectionContent(
                section_name="risk_matrix",
                title="Risk Matrix",
                chart_image=chart_bytes,
                chart_caption="Risk distribution by impact and likelihood"
            ))
        
        # Risk Register Table
        if data.get('risks'):
            table = self.table_generator.create_risk_register_table(data['risks'])
            builder.add_section_content("risk_register", SectionContent(
                section_name="risk_register",
                title="Risk Register",
                custom_content=table
            ))
    
    async def _build_vulnerability_scan(
        self,
        builder: TemplateBuilder,
        data: Dict[str, Any]
    ):
        """Build vulnerability scan report sections"""
        
        findings = data.get('findings', [])
        
        # Severity distribution chart
        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0, 'info': 0}
        for f in findings:
            sev = f.get('severity', 'info').lower()
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        chart_bytes = self.chart_generator.create_severity_pie(
            severity_counts,
            title="Findings by Severity"
        )
        
        builder.add_section_content("findings_summary", SectionContent(
            section_name="findings_summary",
            title="Findings Summary",
            chart_image=chart_bytes,
            chart_caption="Distribution of vulnerabilities by severity level"
        ))
        
        # Findings tables by severity
        for severity in ['critical', 'high', 'medium']:
            sev_findings = [f for f in findings if f.get('severity', '').lower() == severity]
            if sev_findings:
                table = self.table_generator.create_severity_table(sev_findings)
                builder.add_section_content(
                    f"{severity}_findings",
                    SectionContent(
                        section_name=f"{severity}_findings",
                        title=f"{severity.capitalize()} Severity Findings",
                        custom_content=table
                    )
                )
    
    async def _build_executive_summary(
        self,
        builder: TemplateBuilder,
        data: Dict[str, Any]
    ):
        """Build executive summary report sections"""
        
        # Key metrics
        builder.add_section_content("key_metrics", SectionContent(
            section_name="key_metrics",
            title="Key Metrics",
            paragraphs=[
                f"Total Assets: {data.get('total_assets', 'N/A')}",
                f"Critical Risks: {data.get('critical_risks', 'N/A')}",
                f"Open Vulnerabilities: {data.get('open_vulnerabilities', 'N/A')}",
                f"Compliance Score: {data.get('compliance_score', 'N/A')}%"
            ]
        ))
        
        # Recommendations
        builder.add_section_content("recommendations", SectionContent(
            section_name="recommendations",
            title="Recommendations",
            bullet_points=data.get('recommendations', [])
        ))
    
    async def _build_generic_report(
        self,
        builder: TemplateBuilder,
        data: Dict[str, Any]
    ):
        """Build generic report sections"""
        
        for key, value in data.items():
            if isinstance(value, str):
                builder.add_section_content(key, SectionContent(
                    section_name=key,
                    title=key.replace('_', ' ').title(),
                    paragraphs=[value]
                ))
    
    def _generate_download_token(self, file_path: str, filename: str) -> str:
        """Generate secure download token"""
        import secrets
        import hashlib
        import time
        
        token_data = f"{file_path}:{filename}:{time.time()}:{secrets.token_hex(16)}"
        return hashlib.sha256(token_data.encode()).hexdigest()[:32]
    
    async def create_batch_job(self, request: BatchExportRequest, user_id: str) -> Dict[str, Any]:
        """Create batch export job"""
        import uuid
        
        job_id = str(uuid.uuid4())
        
        # Store job in database/cache
        # Implementation depends on your storage backend
        
        return {"job_id": job_id}
    
    async def process_batch_job(self, job_id: str):
        """Process batch export job"""
        # Implementation for batch processing
        pass
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get batch job status"""
        # Implementation for job status retrieval
        pass
    
    async def validate_download_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate download token"""
        # Implementation for token validation
        pass
    
    async def generate_pdf_stream(self, report_id: str, user_id: str) -> bytes:
        """Generate PDF as stream"""
        # Implementation for streaming generation
        pass
    
    async def generate_preview(self, request: PDFExportRequest, user_id: str) -> bytes:
        """Generate PDF preview (first page only)"""
        # Implementation for preview generation
        pass
```

---

## 10. Batch PDF Generation

### 10.1 Batch Processing System

```python
# /app/pdf/batch/processor.py
"""
Batch PDF generation processor
"""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import asyncio
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class BatchJobStatus(Enum):
    """Batch job status"""
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BatchJob:
    """Batch job definition"""
    id: str
    status: BatchJobStatus
    total_items: int
    completed_items: int = 0
    failed_items: int = 0
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    items: List[Dict[str, Any]] = None
    results: List[Dict[str, Any]] = None
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.items is None:
            self.items = []
        if self.results is None:
            self.results = []
    
    @property
    def progress(self) -> float:
        if self.total_items == 0:
            return 0.0
        return (self.completed_items + self.failed_items) / self.total_items


class BatchProcessor:
    """
    Batch PDF generation processor
    Handles parallel processing of multiple PDF exports
    """
    
    def __init__(
        self,
        max_workers: int = 4,
        use_processes: bool = False,
        chunk_size: int = 10
    ):
        self.max_workers = max_workers
        self.use_processes = use_processes
        self.chunk_size = chunk_size
        self.jobs: Dict[str, BatchJob] = {}
        self.executor_class = ProcessPoolExecutor if use_processes else ThreadPoolExecutor
    
    def create_job(self, items: List[Dict[str, Any]]) -> BatchJob:
        """Create new batch job"""
        job = BatchJob(
            id=str(uuid.uuid4()),
            status=BatchJobStatus.PENDING,
            total_items=len(items),
            items=items
        )
        self.jobs[job.id] = job
        return job
    
    async def process_job(
        self,
        job_id: str,
        processor_func: Callable[[Dict[str, Any]], Dict[str, Any]],
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> BatchJob:
        """
        Process batch job
        
        Args:
            job_id: Job identifier
            processor_func: Function to process each item
            progress_callback: Optional callback for progress updates
            
        Returns:
            Completed batch job
        """
        job = self.jobs.get(job_id)
        if not job:
            raise ValueError(f"Job not found: {job_id}")
        
        job.status = BatchJobStatus.PROCESSING
        job.started_at = datetime.now()
        
        try:
            # Process items in chunks
            chunks = self._chunk_items(job.items, self.chunk_size)
            
            for chunk in chunks:
                # Process chunk in parallel
                chunk_results = await self._process_chunk(chunk, processor_func)
                
                # Update job with results
                for result in chunk_results:
                    if result.get('success'):
                        job.completed_items += 1
                    else:
                        job.failed_items += 1
                    job.results.append(result)
                
                # Report progress
                if progress_callback:
                    progress_callback(job_id, job.progress)
                
                # Check for cancellation
                if job.status == BatchJobStatus.CANCELLED:
                    break
            
            # Mark completed
            if job.status != BatchJobStatus.CANCELLED:
                job.status = BatchJobStatus.COMPLETED
            
        except Exception as e:
            logger.error(f"Batch job {job_id} failed: {e}")
            job.status = BatchJobStatus.FAILED
            job.error_message = str(e)
        
        finally:
            job.completed_at = datetime.now()
        
        return job
    
    def _chunk_items(self, items: List[Any], chunk_size: int) -> List[List[Any]]:
        """Split items into chunks"""
        return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]
    
    async def _process_chunk(
        self,
        chunk: List[Dict[str, Any]],
        processor_func: Callable
    ) -> List[Dict[str, Any]]:
        """Process a chunk of items in parallel"""
        loop = asyncio.get_event_loop()
        
        with self.executor_class(max_workers=self.max_workers) as executor:
            # Submit all tasks
            futures = [
                loop.run_in_executor(executor, self._wrap_processor, processor_func, item)
                for item in chunk
            ]
            
            # Gather results
            results = await asyncio.gather(*futures, return_exceptions=True)
            
            # Process results
            processed_results = []
            for result in results:
                if isinstance(result, Exception):
                    processed_results.append({
                        'success': False,
                        'error': str(result)
                    })
                else:
                    processed_results.append(result)
            
            return processed_results
    
    def _wrap_processor(
        self,
        processor_func: Callable,
        item: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Wrap processor function with error handling"""
        try:
            result = processor_func(item)
            return {'success': True, 'result': result}
        except Exception as e:
            logger.error(f"Item processing failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_job(self, job_id: str) -> Optional[BatchJob]:
        """Get job by ID"""
        return self.jobs.get(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a running job"""
        job = self.jobs.get(job_id)
        if job and job.status in [BatchJobStatus.PENDING, BatchJobStatus.PROCESSING]:
            job.status = BatchJobStatus.CANCELLED
            return True
        return False
    
    def cleanup_old_jobs(self, max_age_hours: int = 24):
        """Remove old completed jobs"""
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        jobs_to_remove = [
            job_id for job_id, job in self.jobs.items()
            if job.completed_at and job.completed_at < cutoff
        ]
        
        for job_id in jobs_to_remove:
            del self.jobs[job_id]


class BatchReportGenerator:
    """
    Specialized batch generator for reports
    """
    
    def __init__(self, processor: BatchProcessor = None):
        self.processor = processor or BatchProcessor()
    
    async def generate_reports(
        self,
        report_requests: List[Dict[str, Any]],
        on_progress: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Generate multiple reports in batch
        
        Args:
            report_requests: List of report generation requests
            on_progress: Optional progress callback
            
        Returns:
            Batch job results
        """
        # Create batch job
        job = self.processor.create_job(report_requests)
        
        # Define processor function
        def process_report(request: Dict[str, Any]) -> Dict[str, Any]:
            from app.pdf.export_service import PDFExportService
            
            service = PDFExportService()
            # Generate individual report
            # This would call the actual generation logic
            return {
                'report_id': request.get('report_id'),
                'file_path': f"/path/to/report_{request.get('report_id')}.pdf"
            }
        
        # Process job
        completed_job = await self.processor.process_job(
            job.id,
            process_report,
            on_progress
        )
        
        return {
            'job_id': completed_job.id,
            'status': completed_job.status.value,
            'total': completed_job.total_items,
            'completed': completed_job.completed_items,
            'failed': completed_job.failed_items,
            'results': completed_job.results
        }
    
    async def generate_scheduled_reports(
        self,
        schedule_config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate scheduled reports
        
        Args:
            schedule_config: Schedule configuration
            
        Returns:
            Generation results
        """
        # Get reports due for generation
        reports_due = self._get_reports_due(schedule_config)
        
        if not reports_due:
            return {'status': 'no_reports_due', 'count': 0}
        
        # Generate in batch
        return await self.generate_reports(reports_due)
    
    def _get_reports_due(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of reports due for generation"""
        # Implementation would query database for scheduled reports
        return []


# Celery task for background processing
"""
# /app/pdf/batch/tasks.py
from celery import shared_task
from app.pdf.batch.processor import BatchProcessor, BatchJobStatus

@shared_task(bind=True, max_retries=3)
def process_batch_pdf_job(self, job_id: str):
    '''Celery task for batch PDF processing'''
    from app.pdf.export_service import PDFExportService
    
    processor = BatchProcessor()
    service = PDFExportService()
    
    def process_item(item):
        return service.generate_pdf_sync(item['request'], item['user_id'])
    
    async def run():
        job = await processor.process_job(job_id, process_item)
        return job
    
    import asyncio
    job = asyncio.run(run())
    
    if job.status == BatchJobStatus.FAILED:
        # Retry on failure
        raise self.retry(countdown=60)
    
    return {
        'job_id': job.id,
        'status': job.status.value,
        'completed': job.completed_items,
        'failed': job.failed_items
    }
"""
```

---

## 11. PDF Compression

### 11.1 Compression Service

```python
# /app/pdf/compression/service.py
"""
PDF compression and optimization service
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging
import os
import tempfile

logger = logging.getLogger(__name__)


class CompressionLevel(Enum):
    """Compression level options"""
    NONE = "none"           # No compression
    LOW = "low"             # Minimal compression, best quality
    MEDIUM = "medium"       # Balanced compression
    HIGH = "high"           # Maximum compression, may reduce quality
    MAXIMUM = "maximum"     # Aggressive compression


@dataclass
class CompressionResult:
    """Compression operation result"""
    original_size: int
    compressed_size: int
    compression_ratio: float
    output_path: str
    method_used: str
    success: bool
    error_message: Optional[str] = None
    
    @property
    def size_reduction(self) -> str:
        reduction = self.original_size - self.compressed_size
        return f"{reduction / 1024 / 1024:.2f} MB"
    
    @property
    def percentage_reduction(self) -> str:
        if self.original_size == 0:
            return "0%"
        pct = (1 - self.compressed_size / self.original_size) * 100
        return f"{pct:.1f}%"


class PDFCompressionService:
    """
    PDF compression and optimization service
    """
    
    def __init__(self):
        self.compression_methods = {
            'pikepdf': self._compress_with_pikepdf,
            'pypdf': self._compress_with_pypdf,
            'ghostscript': self._compress_with_ghostscript,
        }
    
    async def compress(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        level: CompressionLevel = CompressionLevel.MEDIUM,
        method: Optional[str] = None
    ) -> CompressionResult:
        """
        Compress PDF file
        
        Args:
            input_path: Path to input PDF
            output_path: Path for output PDF (optional)
            level: Compression level
            method: Specific compression method (auto-detected if None)
            
        Returns:
            Compression result
        """
        original_size = os.path.getsize(input_path)
        
        if not output_path:
            output_path = input_path.replace('.pdf', '_compressed.pdf')
        
        try:
            # Select compression method
            if method and method in self.compression_methods:
                compress_func = self.compression_methods[method]
            else:
                compress_func = self._select_best_method(input_path, level)
            
            # Perform compression
            await compress_func(input_path, output_path, level)
            
            compressed_size = os.path.getsize(output_path)
            
            return CompressionResult(
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=original_size / compressed_size if compressed_size > 0 else 0,
                output_path=output_path,
                method_used=compress_func.__name__,
                success=True
            )
            
        except Exception as e:
            logger.error(f"PDF compression failed: {e}")
            return CompressionResult(
                original_size=original_size,
                compressed_size=original_size,
                compression_ratio=1.0,
                output_path=input_path,
                method_used="none",
                success=False,
                error_message=str(e)
            )
    
    def _select_best_method(self, input_path: str, level: CompressionLevel) -> callable:
        """Select best compression method based on file characteristics"""
        # Check if Ghostscript is available (best for image-heavy PDFs)
        if self._ghostscript_available():
            return self._compress_with_ghostscript
        
        # Check if pikepdf is available (best for modern PDFs)
        try:
            import pikepdf
            return self._compress_with_pikepdf
        except ImportError:
            pass
        
        # Fallback to PyPDF
        return self._compress_with_pypdf
    
    def _ghostscript_available(self) -> bool:
        """Check if Ghostscript is available"""
        import shutil
        return shutil.which('gs') is not None
    
    async def _compress_with_pikepdf(
        self,
        input_path: str,
        output_path: str,
        level: CompressionLevel
    ):
        """Compress using pikepdf"""
        import pikepdf
        
        pdf = pikepdf.open(input_path)
        
        # Set compression parameters based on level
        if level == CompressionLevel.LOW:
            stream_mode = pikepdf.StreamDecodeLevel.specialized
        elif level == CompressionLevel.MEDIUM:
            stream_mode = pikepdf.StreamDecodeLevel.generalized
        else:
            stream_mode = pikepdf.StreamDecodeLevel.all
        
        # Save with compression
        pdf.save(
            output_path,
            compress_streams=True,
            object_stream_mode=pikepdf.ObjectStreamMode.generate,
            stream_decode_level=stream_mode
        )
        pdf.close()
    
    async def _compress_with_pypdf(
        self,
        input_path: str,
        output_path: str,
        level: CompressionLevel
    ):
        """Compress using PyPDF2"""
        from PyPDF2 import PdfReader, PdfWriter
        
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        # Set compression
        if level in [CompressionLevel.HIGH, CompressionLevel.MAXIMUM]:
            for page in writer.pages:
                page.compress_content_streams()
        
        with open(output_path, 'wb') as f:
            writer.write(f)
    
    async def _compress_with_ghostscript(
        self,
        input_path: str,
        output_path: str,
        level: CompressionLevel
    ):
        """Compress using Ghostscript"""
        import subprocess
        
        # Map compression levels to Ghostscript settings
        quality_settings = {
            CompressionLevel.LOW: '/prepress',
            CompressionLevel.MEDIUM: '/ebook',
            CompressionLevel.HIGH: '/screen',
            CompressionLevel.MAXIMUM: '/screen',
        }
        
        pdf_settings = quality_settings.get(level, '/ebook')
        
        cmd = [
            'gs',
            '-sDEVICE=pdfwrite',
            '-dCompatibilityLevel=1.4',
            f'-dPDFSETTINGS={pdf_settings}',
            '-dNOPAUSE',
            '-dQUIET',
            '-dBATCH',
            f'-sOutputFile={output_path}',
            input_path
        ]
        
        subprocess.run(cmd, check=True)
    
    async def optimize_images(
        self,
        input_path: str,
        output_path: str,
        max_image_resolution: int = 150,
        jpeg_quality: int = 85
    ) -> CompressionResult:
        """
        Optimize images within PDF
        
        Args:
            input_path: Input PDF path
            output_path: Output PDF path
            max_image_resolution: Maximum DPI for images
            jpeg_quality: JPEG quality (0-100)
            
        Returns:
            Compression result
        """
        try:
            import fitz  # PyMuPDF
            
            original_size = os.path.getsize(input_path)
            
            doc = fitz.open(input_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                images = page.get_images()
                
                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    
                    # Process image
                    from PIL import Image
                    import io
                    
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Resize if too large
                    max_size = (max_image_resolution * 8, max_image_resolution * 11)
                    image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    # Convert to RGB if necessary
                    if image.mode in ('RGBA', 'LA', 'P'):
                        image = image.convert('RGB')
                    
                    # Save as optimized JPEG
                    output = io.BytesIO()
                    image.save(output, format='JPEG', quality=jpeg_quality, optimize=True)
                    
                    # Replace image in PDF
                    doc.update_stream(xref, output.getvalue())
            
            doc.save(output_path, garbage=4, deflate=True)
            doc.close()
            
            compressed_size = os.path.getsize(output_path)
            
            return CompressionResult(
                original_size=original_size,
                compressed_size=compressed_size,
                compression_ratio=original_size / compressed_size if compressed_size > 0 else 0,
                output_path=output_path,
                method_used="image_optimization",
                success=True
            )
            
        except Exception as e:
            logger.error(f"Image optimization failed: {e}")
            raise
    
    async def compress_batch(
        self,
        file_paths: List[str],
        level: CompressionLevel = CompressionLevel.MEDIUM,
        output_dir: Optional[str] = None
    ) -> List[CompressionResult]:
        """
        Compress multiple PDFs
        
        Args:
            file_paths: List of PDF file paths
            level: Compression level
            output_dir: Output directory (optional)
            
        Returns:
            List of compression results
        """
        results = []
        
        for file_path in file_paths:
            if output_dir:
                filename = os.path.basename(file_path)
                output_path = os.path.join(output_dir, filename)
            else:
                output_path = None
            
            result = await self.compress(file_path, output_path, level)
            results.append(result)
        
        return results
    
    def get_compression_stats(self, results: List[CompressionResult]) -> Dict[str, Any]:
        """Get statistics for batch compression"""
        total_original = sum(r.original_size for r in results)
        total_compressed = sum(r.compressed_size for r in results)
        successful = sum(1 for r in results if r.success)
        
        return {
            'total_files': len(results),
            'successful': successful,
            'failed': len(results) - successful,
            'total_original_size_mb': total_original / 1024 / 1024,
            'total_compressed_size_mb': total_compressed / 1024 / 1024,
            'total_reduction_mb': (total_original - total_compressed) / 1024 / 1024,
            'average_reduction_percent': (
                (1 - total_compressed / total_original) * 100 if total_original > 0 else 0
            )
        }
```

---

## 12. PDF Accessibility

### 12.1 Accessibility Service

```python
# /app/pdf/accessibility/service.py
"""
PDF accessibility (PDF/UA) service
Ensures PDFs meet accessibility standards
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class AccessibilityStandard(Enum):
    """PDF accessibility standards"""
    PDF_UA = "PDF/UA"           # ISO 14289
    WCAG_2_1_A = "WCAG 2.1 A"
    WCAG_2_1_AA = "WCAG 2.1 AA"
    WCAG_2_1_AAA = "WCAG 2.1 AAA"
    SECTION_508 = "Section 508"


@dataclass
class AccessibilityCheck:
    """Accessibility check result"""
    rule: str
    passed: bool
    severity: str  # error, warning, info
    message: str
    remediation: Optional[str] = None


@dataclass
class AccessibilityReport:
    """Accessibility validation report"""
    standard: AccessibilityStandard
    checks: List[AccessibilityCheck]
    score: float  # 0-100
    compliant: bool
    
    @property
    def error_count(self) -> int:
        return sum(1 for c in self.checks if c.severity == 'error')
    
    @property
    def warning_count(self) -> int:
        return sum(1 for c in self.checks if c.severity == 'warning')


class PDFAccessibilityService:
    """
    PDF accessibility service
    Adds and validates accessibility features
    """
    
    def __init__(self):
        self.required_tags = [
            'Document', 'Part', 'Sect', 'Div', 'BlockQuote', 
            'Caption', 'TOC', 'TOCI', 'Index', 'NonStruct',
            'Private', 'P', 'H', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6',
            'L', 'LI', 'Lbl', 'LBody', 'Table', 'TR', 'TH', 'TD',
            'THead', 'TBody', 'TFoot', 'Span', 'Quote', 'Note',
            'Reference', 'BibEntry', 'Code', 'Link', 'Annot',
            'Ruby', 'RB', 'RT', 'RP', 'Warichu', 'WT', 'WP',
            'Figure', 'Formula', 'Form'
        ]
    
    async def make_accessible(
        self,
        input_path: str,
        output_path: str,
        title: str,
        language: str = "en-US",
        standard: AccessibilityStandard = AccessibilityStandard.PDF_UA
    ) -> bool:
        """
        Make PDF accessible
        
        Args:
            input_path: Input PDF path
            output_path: Output PDF path
            title: Document title
            language: Document language
            standard: Accessibility standard to meet
            
        Returns:
            True if successful
        """
        try:
            import pikepdf
            
            pdf = pikepdf.open(input_path)
            
            # Set document metadata
            with pdf.open_metadata() as meta:
                meta['dc:title'] = title
                meta['dc:language'] = language
            
            # Mark as PDF/UA if applicable
            if standard == AccessibilityStandard.PDF_UA:
                pdf.root.UF = "Universal Accessibility"
            
            # Add document structure
            self._add_structure_tree(pdf)
            
            # Add alternate text to images
            self._add_image_alt_text(pdf)
            
            # Set language
            pdf.root.Lang = language
            
            # Save
            pdf.save(output_path)
            pdf.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Accessibility enhancement failed: {e}")
            return False
    
    def _add_structure_tree(self, pdf):
        """Add document structure tree"""
        # This is a simplified implementation
        # Full implementation would require analyzing document content
        pass
    
    def _add_image_alt_text(self, pdf):
        """Add alternate text to images"""
        # Implementation would iterate through images and add alt text
        pass
    
    async def validate(
        self,
        pdf_path: str,
        standard: AccessibilityStandard = AccessibilityStandard.PDF_UA
    ) -> AccessibilityReport:
        """
        Validate PDF accessibility
        
        Args:
            pdf_path: PDF file path
            standard: Standard to validate against
            
        Returns:
            Accessibility validation report
        """
        checks = []
        
        try:
            import pikepdf
            pdf = pikepdf.open(pdf_path)
            
            # Check 1: Document has title
            has_title = self._check_document_title(pdf)
            checks.append(AccessibilityCheck(
                rule="Document must have title",
                passed=has_title,
                severity='error' if not has_title else 'info',
                message="Document title is present" if has_title else "Document is missing title",
                remediation="Add document title using document metadata" if not has_title else None
            ))
            
            # Check 2: Language specified
            has_language = self._check_language(pdf)
            checks.append(AccessibilityCheck(
                rule="Document language must be specified",
                passed=has_language,
                severity='error' if not has_language else 'info',
                message="Language is specified" if has_language else "Language is not specified",
                remediation="Set document language property" if not has_language else None
            ))
            
            # Check 3: Tagged content
            is_tagged = self._check_tagged_content(pdf)
            checks.append(AccessibilityCheck(
                rule="Content must be tagged",
                passed=is_tagged,
                severity='error' if not is_tagged else 'info',
                message="Content is properly tagged" if is_tagged else "Content is not tagged",
                remediation="Add structure tags to document content" if not is_tagged else None
            ))
            
            # Check 4: Reading order
            has_reading_order = self._check_reading_order(pdf)
            checks.append(AccessibilityCheck(
                rule="Reading order must be defined",
                passed=has_reading_order,
                severity='warning' if not has_reading_order else 'info',
                message="Reading order is defined" if has_reading_order else "Reading order may need verification",
                remediation="Verify and correct reading order if necessary" if not has_reading_order else None
            ))
            
            # Check 5: Images have alt text
            images_have_alt = self._check_image_alt_text(pdf)
            checks.append(AccessibilityCheck(
                rule="Images must have alternate text",
                passed=images_have_alt,
                severity='error' if not images_have_alt else 'info',
                message="All images have alternate text" if images_have_alt else "Some images missing alternate text",
                remediation="Add alternate text to all images" if not images_have_alt else None
            ))
            
            # Check 6: Tables have headers
            tables_have_headers = self._check_table_headers(pdf)
            checks.append(AccessibilityCheck(
                rule="Tables should have headers",
                passed=tables_have_headers,
                severity='warning' if not tables_have_headers else 'info',
                message="Tables have proper headers" if tables_have_headers else "Some tables may be missing headers",
                remediation="Add header rows to tables" if not tables_have_headers else None
            ))
            
            pdf.close()
            
        except Exception as e:
            logger.error(f"Accessibility validation failed: {e}")
            checks.append(AccessibilityCheck(
                rule="Validation execution",
                passed=False,
                severity='error',
                message=f"Validation failed: {str(e)}"
            ))
        
        # Calculate score
        error_count = sum(1 for c in checks if c.severity == 'error' and not c.passed)
        warning_count = sum(1 for c in checks if c.severity == 'warning' and not c.passed)
        
        total_weight = len(checks)
        error_weight = 2
        warning_weight = 1
        
        penalty = (error_count * error_weight + warning_count * warning_weight)
        score = max(0, 100 - (penalty / total_weight * 100))
        
        return AccessibilityReport(
            standard=standard,
            checks=checks,
            score=score,
            compliant=score >= 95 and error_count == 0
        )
    
    def _check_document_title(self, pdf) -> bool:
        """Check if document has title"""
        try:
            with pdf.open_metadata() as meta:
                return bool(meta.get('dc:title'))
        except:
            return False
    
    def _check_language(self, pdf) -> bool:
        """Check if language is specified"""
        try:
            return hasattr(pdf.root, 'Lang') and pdf.root.Lang
        except:
            return False
    
    def _check_tagged_content(self, pdf) -> bool:
        """Check if content is tagged"""
        try:
            return hasattr(pdf.root, 'StructTreeRoot')
        except:
            return False
    
    def _check_reading_order(self, pdf) -> bool:
        """Check if reading order is defined"""
        # Simplified check
        return True
    
    def _check_image_alt_text(self, pdf) -> bool:
        """Check if images have alt text"""
        # Simplified check - would need to iterate through images
        return True
    
    def _check_table_headers(self, pdf) -> bool:
        """Check if tables have headers"""
        # Simplified check
        return True
    
    def generate_remediation_report(
        self,
        report: AccessibilityReport
    ) -> str:
        """Generate human-readable remediation report"""
        lines = [
            f"PDF Accessibility Report - {report.standard.value}",
            f"Score: {report.score:.1f}/100",
            f"Compliant: {'Yes' if report.compliant else 'No'}",
            "",
            "Issues Found:",
            ""
        ]
        
        failed_checks = [c for c in report.checks if not c.passed]
        
        if not failed_checks:
            lines.append("No accessibility issues found!")
        else:
            for i, check in enumerate(failed_checks, 1):
                lines.append(f"{i}. {check.rule}")
                lines.append(f"   Severity: {check.severity.upper()}")
                lines.append(f"   Issue: {check.message}")
                if check.remediation:
                    lines.append(f"   Remediation: {check.remediation}")
                lines.append("")
        
        return "\n".join(lines)


class AccessiblePDFGenerator:
    """
    Generator that creates accessible PDFs by default
    """
    
    def __init__(self, accessibility_service: PDFAccessibilityService = None):
        self.accessibility = accessibility_service or PDFAccessibilityService()
    
    async def generate(
        self,
        content: Dict[str, Any],
        output_path: str,
        title: str,
        language: str = "en-US"
    ) -> str:
        """
        Generate accessible PDF
        
        Args:
            content: PDF content definition
            output_path: Output file path
            title: Document title
            language: Document language
            
        Returns:
            Path to generated PDF
        """
        # First generate standard PDF
        temp_path = output_path + '.temp.pdf'
        
        # Generate PDF using standard generator
        # ... generation logic ...
        
        # Then make it accessible
        success = await self.accessibility.make_accessible(
            temp_path,
            output_path,
            title,
            language
        )
        
        # Cleanup temp file
        import os
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        if success:
            return output_path
        else:
            raise RuntimeError("Failed to create accessible PDF")
```



---

## 13. Performance Tuning

### 13.1 Performance Optimization Strategies

```python
# /app/pdf/performance/optimizer.py
"""
PDF generation performance optimization
"""
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass
from functools import lru_cache
import time
import logging
import psutil
import os

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for PDF generation"""
    generation_time_ms: float
    memory_usage_mb: float
    cpu_percent: float
    page_count: int
    file_size_kb: float
    elements_count: int


class PDFPerformanceOptimizer:
    """
    Performance optimization for PDF generation
    """
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.optimization_enabled = True
    
    def measure_performance(self, func: Callable) -> Callable:
        """Decorator to measure function performance"""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            process = psutil.Process(os.getpid())
            mem_before = process.memory_info().rss / 1024 / 1024
            
            result = func(*args, **kwargs)
            
            end_time = time.time()
            mem_after = process.memory_info().rss / 1024 / 1024
            
            metrics = PerformanceMetrics(
                generation_time_ms=(end_time - start_time) * 1000,
                memory_usage_mb=mem_after - mem_before,
                cpu_percent=process.cpu_percent(),
                page_count=getattr(result, 'page_count', 0),
                file_size_kb=getattr(result, 'file_size', 0) / 1024,
                elements_count=getattr(result, 'elements_count', 0)
            )
            
            self.metrics_history.append(metrics)
            logger.info(f"PDF Generation: {metrics.generation_time_ms:.0f}ms, "
                       f"Memory: {metrics.memory_usage_mb:.1f}MB")
            
            return result
        
        return wrapper
    
    def get_average_metrics(self) -> Dict[str, float]:
        """Get average performance metrics"""
        if not self.metrics_history:
            return {}
        
        return {
            'avg_generation_time_ms': sum(m.generation_time_ms for m in self.metrics_history) / len(self.metrics_history),
            'avg_memory_usage_mb': sum(m.memory_usage_mb for m in self.metrics_history) / len(self.metrics_history),
            'avg_cpu_percent': sum(m.cpu_percent for m in self.metrics_history) / len(self.metrics_history),
            'avg_file_size_kb': sum(m.file_size_kb for m in self.metrics_history) / len(self.metrics_history),
        }


class ImageOptimization:
    """Image optimization for PDFs"""
    
    @staticmethod
    def optimize_for_pdf(
        image_path: str,
        output_path: str,
        max_width: int = 1200,
        max_height: int = 1600,
        quality: int = 85,
        dpi: int = 150
    ) -> Dict[str, Any]:
        """
        Optimize image for PDF embedding
        
        Args:
            image_path: Input image path
            output_path: Output image path
            max_width: Maximum width in pixels
            max_height: Maximum height in pixels
            quality: JPEG quality (0-100)
            dpi: Target DPI
            
        Returns:
            Optimization result
        """
        from PIL import Image
        import os
        
        original_size = os.path.getsize(image_path)
        
        with Image.open(image_path) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if img.mode in ('RGBA', 'LA'):
                    background.paste(img, mask=img.split()[-1])
                    img = background
                else:
                    img = img.convert('RGB')
            
            # Resize if too large
            img.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            
            # Set DPI
            img.info['dpi'] = (dpi, dpi)
            
            # Save optimized
            img.save(output_path, 'JPEG', quality=quality, optimize=True)
        
        optimized_size = os.path.getsize(output_path)
        
        return {
            'original_size_kb': original_size / 1024,
            'optimized_size_kb': optimized_size / 1024,
            'reduction_percent': (1 - optimized_size / original_size) * 100,
            'dimensions': img.size
        }
    
    @staticmethod
    @lru_cache(maxsize=128)
    def get_optimal_dpi(content_width_inches: float, pixel_width: int) -> int:
        """Calculate optimal DPI for image"""
        return min(300, max(72, int(pixel_width / content_width_inches)))


class FontOptimization:
    """Font optimization for PDFs"""
    
    # Font subsetting - only include used characters
    @staticmethod
    def subset_font(
        font_path: str,
        characters_used: str,
        output_path: str
    ) -> bool:
        """
        Create font subset with only used characters
        
        Args:
            font_path: Original font path
            characters_used: String of characters used in document
            output_path: Output subset font path
            
        Returns:
            True if successful
        """
        try:
            from fontTools.subset import Subsetter, Options
            from fontTools.ttLib import TTFont
            
            font = TTFont(font_path)
            
            options = Options()
            options.layout_features = ['*']
            options.name_IDs = ['*']
            options.name_legacy = True
            options.name_languages = ['*']
            options.obfuscate_names = False
            options.notdef_outline = True
            options.recalc_bounds = True
            options.recalc_timestamp = True
            options.canonical_order = True
            
            subsetter = Subsetter(options=options)
            subsetter.populate(text=characters_used)
            subsetter.subset(font)
            
            font.save(output_path)
            return True
            
        except Exception as e:
            logger.error(f"Font subsetting failed: {e}")
            return False


class CachingStrategy:
    """Caching strategies for PDF generation"""
    
    def __init__(self, cache_dir: str = "/app/cache/pdfs"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cache_key(self, *args, **kwargs) -> str:
        """Generate cache key from arguments"""
        import hashlib
        import json
        
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True)
        return hashlib.sha256(key_data.encode()).hexdigest()
    
    def get_cached_pdf(self, cache_key: str) -> Optional[str]:
        """Get cached PDF if exists"""
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pdf")
        if os.path.exists(cache_path):
            return cache_path
        return None
    
    def cache_pdf(self, cache_key: str, pdf_path: str) -> str:
        """Cache generated PDF"""
        cache_path = os.path.join(self.cache_dir, f"{cache_key}.pdf")
        import shutil
        shutil.copy(pdf_path, cache_path)
        return cache_path
    
    def clear_cache(self, max_age_hours: int = 24):
        """Clear old cached PDFs"""
        from datetime import datetime, timedelta
        
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        
        for filename in os.listdir(self.cache_dir):
            filepath = os.path.join(self.cache_dir, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            if file_time < cutoff:
                os.remove(filepath)


class StreamingGenerator:
    """
    Memory-efficient streaming PDF generation
    For very large reports
    """
    
    def __init__(self, chunk_size: int = 100):
        self.chunk_size = chunk_size
    
    async def generate_streaming(
        self,
        data_source,
        output_path: str,
        template_id: str
    ):
        """
        Generate PDF in streaming fashion
        
        Args:
            data_source: Async iterator of data chunks
            output_path: Output PDF path
            template_id: Template to use
        """
        from reportlab.platypus import SimpleDocTemplate
        from reportlab.lib.pagesizes import letter
        
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        elements = []
        
        chunk_count = 0
        async for chunk in data_source:
            # Process chunk
            chunk_elements = self._process_chunk(chunk, template_id)
            elements.extend(chunk_elements)
            
            chunk_count += 1
            
            # Build intermediate document every N chunks to free memory
            if chunk_count % self.chunk_size == 0:
                doc.build(elements)
                elements = []  # Clear elements
        
        # Build final document
        if elements:
            doc.build(elements)
    
    def _process_chunk(self, chunk: Dict, template_id: str) -> List:
        """Process data chunk into PDF elements"""
        # Implementation depends on template
        return []


# Performance Configuration
PERFORMANCE_CONFIG = {
    # Image optimization
    'image_max_width': 1200,
    'image_max_height': 1600,
    'image_quality': 85,
    'image_dpi': 150,
    
    # Font optimization
    'subset_fonts': True,
    'embed_fonts': False,  # Use standard fonts when possible
    
    # Caching
    'enable_caching': True,
    'cache_ttl_hours': 24,
    
    # Memory management
    'max_elements_per_build': 1000,
    'streaming_threshold_pages': 50,
    
    # Parallel processing
    'max_workers': 4,
    'chunk_size': 10,
    
    # Compression
    'auto_compress': True,
    'compression_level': 'medium',
}
```

---

## 14. Testing Strategy

### 14.1 Test Suite

```python
# /app/pdf/tests/test_pdf_generation.py
"""
PDF generation test suite
"""
import pytest
import os
import tempfile
from unittest.mock import Mock, patch
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Paragraph

from app.pdf.generation.reportlab_engine import ReportLabPDFGenerator
from app.pdf.generation.base import PDFMetadata, PageSettings
from app.pdf.charts.generator import ChartGenerator, ChartConfig
from app.pdf.tables.generator import AdvancedTableGenerator, ColumnDef
from app.pdf.templates.builder import TemplateBuilder, SectionContent
from app.pdf.compression.service import PDFCompressionService, CompressionLevel
from app.pdf.accessibility.service import PDFAccessibilityService


class TestPDFGeneration:
    """Test PDF generation functionality"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_metadata(self):
        """Sample PDF metadata"""
        return PDFMetadata(
            title="Test Report",
            author="Test Author",
            subject="Test Subject",
            keywords=["test", "pdf"]
        )
    
    def test_basic_pdf_generation(self, temp_dir, sample_metadata):
        """Test basic PDF generation"""
        output_path = os.path.join(temp_dir, "test.pdf")
        
        generator = ReportLabPDFGenerator(metadata=sample_metadata)
        generator.add_heading("Test Heading", level=1)
        generator.add_paragraph("This is a test paragraph.")
        
        result = generator.generate(output_path=output_path)
        
        assert os.path.exists(result)
        assert os.path.getsize(result) > 0
    
    def test_table_generation(self, temp_dir, sample_metadata):
        """Test table generation"""
        output_path = os.path.join(temp_dir, "table_test.pdf")
        
        generator = ReportLabPDFGenerator(metadata=sample_metadata)
        
        data = [
            ["Header 1", "Header 2", "Header 3"],
            ["Row 1 Col 1", "Row 1 Col 2", "Row 1 Col 3"],
            ["Row 2 Col 1", "Row 2 Col 2", "Row 2 Col 3"],
        ]
        
        generator.add_table(data)
        result = generator.generate(output_path=output_path)
        
        assert os.path.exists(result)
    
    def test_chart_generation(self, temp_dir):
        """Test chart generation"""
        chart_gen = ChartGenerator(ChartConfig(width=6, height=4))
        
        risks = [
            {'name': 'Risk 1', 'impact': 3, 'likelihood': 4, 'severity': 'high'},
            {'name': 'Risk 2', 'impact': 2, 'likelihood': 2, 'severity': 'medium'},
        ]
        
        chart_bytes = chart_gen.create_risk_matrix(risks)
        
        assert chart_bytes is not None
        assert len(chart_bytes) > 0
    
    def test_template_builder(self, temp_dir, sample_metadata):
        """Test template builder"""
        output_path = os.path.join(temp_dir, "template_test.pdf")
        
        builder = TemplateBuilder("executive_summary_v1")
        builder.set_metadata(sample_metadata)
        
        builder.add_section_content("executive_summary", SectionContent(
            section_name="executive_summary",
            title="Executive Summary",
            paragraphs=["This is the executive summary."]
        ))
        
        generator = builder.build()
        result = generator.generate(output_path=output_path)
        
        assert os.path.exists(result)


class TestPDFCompression:
    """Test PDF compression"""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_pdf(self, temp_dir):
        """Create sample PDF for compression tests"""
        from reportlab.pdfgen import canvas
        
        pdf_path = os.path.join(temp_dir, "sample.pdf")
        c = canvas.Canvas(pdf_path)
        c.drawString(100, 700, "Test PDF for compression")
        c.save()
        
        return pdf_path
    
    @pytest.mark.asyncio
    async def test_compression(self, temp_dir, sample_pdf):
        """Test PDF compression"""
        output_path = os.path.join(temp_dir, "compressed.pdf")
        
        service = PDFCompressionService()
        result = await service.compress(
            sample_pdf,
            output_path,
            level=CompressionLevel.MEDIUM
        )
        
        assert result.success
        assert os.path.exists(output_path)


class TestPDFAccessibility:
    """Test PDF accessibility"""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    @pytest.fixture
    def sample_pdf(self, temp_dir):
        """Create sample PDF for accessibility tests"""
        from reportlab.pdfgen import canvas
        
        pdf_path = os.path.join(temp_dir, "sample.pdf")
        c = canvas.Canvas(pdf_path)
        c.setTitle("Accessible Test PDF")
        c.drawString(100, 700, "Test PDF")
        c.save()
        
        return pdf_path
    
    @pytest.mark.asyncio
    async def test_accessibility_validation(self, temp_dir, sample_pdf):
        """Test accessibility validation"""
        service = PDFAccessibilityService()
        
        report = await service.validate(sample_pdf)
        
        assert report is not None
        assert report.score >= 0
        assert report.score <= 100


class TestPerformance:
    """Test performance characteristics"""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_large_report_generation(self, temp_dir):
        """Test generation of large reports"""
        import time
        
        metadata = PDFMetadata(title="Large Report")
        generator = ReportLabPDFGenerator(metadata=metadata)
        
        # Add many elements
        for i in range(100):
            generator.add_heading(f"Section {i}", level=2)
            generator.add_paragraph(f"This is paragraph {i} with some content.")
        
        output_path = os.path.join(temp_dir, "large_report.pdf")
        
        start_time = time.time()
        generator.generate(output_path=output_path)
        elapsed = time.time() - start_time
        
        # Should complete in reasonable time
        assert elapsed < 30  # 30 seconds max
        assert os.path.getsize(output_path) > 0


# Integration Tests

@pytest.mark.integration
class TestPDFIntegration:
    """Integration tests for PDF system"""
    
    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def test_end_to_end_report_generation(self, temp_dir):
        """Test complete report generation workflow"""
        # 1. Create metadata
        metadata = PDFMetadata(
            title="Security Assessment Report",
            author="ResilienceAI",
            subject="Quarterly Security Assessment"
        )
        
        # 2. Build using template
        builder = TemplateBuilder("risk_assessment_v1")
        builder.set_metadata(metadata)
        
        # 3. Add content sections
        builder.add_section_content("executive_summary", SectionContent(
            section_name="executive_summary",
            title="Executive Summary",
            paragraphs=[
                "This report summarizes the security assessment findings.",
                "Key areas of concern have been identified and documented."
            ]
        ))
        
        # 4. Generate PDF
        generator = builder.build()
        output_path = os.path.join(temp_dir, "final_report.pdf")
        generator.generate(output_path=output_path)
        
        # 5. Compress
        compressor = PDFCompressionService()
        compressed_path = os.path.join(temp_dir, "final_report_compressed.pdf")
        
        import asyncio
        result = asyncio.run(compressor.compress(
            output_path,
            compressed_path,
            CompressionLevel.MEDIUM
        ))
        
        # 6. Validate accessibility
        accessibility = PDFAccessibilityService()
        report = asyncio.run(accessibility.validate(compressed_path))
        
        # Assertions
        assert os.path.exists(compressed_path)
        assert result.success
        assert report.score > 50  # Basic accessibility


# Load Tests

@pytest.mark.load
class TestPDFLoad:
    """Load tests for PDF generation"""
    
    @pytest.mark.parametrize("num_reports", [10, 50, 100])
    def test_concurrent_generation(self, temp_dir, num_reports):
        """Test concurrent PDF generation"""
        import concurrent.futures
        import time
        
        def generate_single(i):
            metadata = PDFMetadata(title=f"Report {i}")
            generator = ReportLabPDFGenerator(metadata=metadata)
            generator.add_heading(f"Report {i}", level=1)
            generator.add_paragraph("Test content")
            
            output_path = os.path.join(temp_dir, f"report_{i}.pdf")
            return generator.generate(output_path=output_path)
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(generate_single, i) for i in range(num_reports)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        elapsed = time.time() - start_time
        
        # All reports should be generated
        assert len(results) == num_reports
        assert all(os.path.exists(r) for r in results)
        
        # Performance check
        avg_time = elapsed / num_reports
        print(f"Average generation time: {avg_time:.2f}s per report")


# Benchmark Tests

@pytest.mark.benchmark
class TestPDFBenchmark:
    """Benchmark tests"""
    
    def test_chart_generation_benchmark(self, benchmark):
        """Benchmark chart generation"""
        chart_gen = ChartGenerator()
        
        risks = [
            {'name': f'Risk {i}', 'impact': i % 4 + 1, 'likelihood': i % 5 + 1, 
             'severity': ['low', 'medium', 'high', 'critical'][i % 4]}
            for i in range(50)
        ]
        
        result = benchmark(chart_gen.create_risk_matrix, risks)
        assert result is not None
```

### 14.2 Test Configuration

```yaml
# /app/pdf/tests/pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
markers =
    integration: Integration tests
    load: Load tests
    benchmark: Benchmark tests
    slow: Slow tests
```

---

## 15. Implementation Priority

### 15.1 Priority Matrix

| Component | Priority | Effort | Impact | Phase |
|-----------|----------|--------|--------|-------|
| **Core PDF Engine (ReportLab)** | P0 | Medium | High | Phase 1 |
| **Basic Report Templates** | P0 | Medium | High | Phase 1 |
| **Chart Generation** | P0 | Low | High | Phase 1 |
| **Table Generation** | P0 | Low | High | Phase 1 |
| **Export API** | P0 | Medium | High | Phase 1 |
| **Headers/Footers** | P1 | Low | Medium | Phase 2 |
| **Multi-page Handling** | P1 | Medium | Medium | Phase 2 |
| **Styling System** | P1 | Low | Medium | Phase 2 |
| **Batch Generation** | P1 | Medium | Medium | Phase 2 |
| **PDF Compression** | P2 | Low | Low | Phase 3 |
| **Accessibility** | P2 | Medium | Medium | Phase 3 |
| **Advanced Templates** | P2 | Medium | Medium | Phase 3 |
| **Performance Tuning** | P3 | High | Medium | Phase 4 |
| **WeasyPrint Integration** | P3 | Medium | Low | Phase 4 |

### 15.2 Implementation Roadmap

```
Phase 1: Core Foundation (Weeks 1-3)
├── Week 1: PDF Engine Setup
│   ├── ReportLab integration
│   ├── Base generator classes
│   └── Basic styling
│
├── Week 2: Content Generation
│   ├── Chart generation (matplotlib)
│   ├── Table generation
│   └── Text/paragraph handling
│
└── Week 3: Templates & API
    ├── Basic templates (3-5 types)
    ├── Export API endpoints
    └── Integration tests

Phase 2: Enhanced Features (Weeks 4-6)
├── Week 4: Layout & Formatting
│   ├── Headers/footers
│   ├── Multi-page handling
│   └── Pagination
│
├── Week 5: Advanced Templates
│   ├── Template registry
│   ├── Template builder
│   └── Custom templates
│
└── Week 6: Batch Processing
    ├── Batch generator
    ├── Background tasks
    └── Job management

Phase 3: Optimization (Weeks 7-8)
├── Week 7: Compression & Size
│   ├── PDF compression
│   ├── Image optimization
│   └── Font subsetting
│
└── Week 8: Accessibility
    ├── PDF/UA compliance
    ├── Alt text support
    └── Validation tools

Phase 4: Advanced Features (Weeks 9-10)
├── Week 9: Performance
│   ├── Caching
│   ├── Streaming generation
│   └── Parallel processing
│
└── Week 10: WeasyPrint
    ├── HTML-to-PDF conversion
    ├── Complex layouts
    └── CSS styling
```

### 15.3 File Structure

```
/app/pdf/
├── __init__.py
├── config.py                    # PDF configuration
│
├── generation/                  # PDF generation core
│   ├── __init__.py
│   ├── base.py                  # Base generator classes
│   ├── reportlab_engine.py      # ReportLab implementation
│   ├── weasyprint_engine.py     # WeasyPrint implementation
│   ├── headers_footers.py       # Header/footer management
│   └── pagination.py            # Multi-page handling
│
├── templates/                   # Template system
│   ├── __init__.py
│   ├── registry.py              # Template registry
│   ├── builder.py               # Template builder
│   ├── loader.py                # Template loader
│   └── definitions/             # Template definitions
│       ├── executive_summary.py
│       ├── risk_assessment.py
│       ├── vulnerability_scan.py
│       └── incident_report.py
│
├── charts/                      # Chart generation
│   ├── __init__.py
│   ├── generator.py             # Chart generator
│   ├── configs.py               # Chart configurations
│   └── styles.py                # Chart styles
│
├── tables/                      # Table generation
│   ├── __init__.py
│   ├── generator.py             # Table generator
│   ├── formatters.py            # Cell formatters
│   └── styles.py                # Table styles
│
├── styling/                     # Styling system
│   ├── __init__.py
│   ├── themes.py                # Theme definitions
│   ├── colors.py                # Color palettes
│   └── typography.py            # Font management
│
├── compression/                 # PDF compression
│   ├── __init__.py
│   ├── service.py               # Compression service
│   ├── image_optimizer.py       # Image optimization
│   └── font_optimizer.py        # Font optimization
│
├── accessibility/               # PDF accessibility
│   ├── __init__.py
│   ├── service.py               # Accessibility service
│   ├── validator.py             # Validation tools
│   └── remediaton.py            # Remediation tools
│
├── batch/                       # Batch processing
│   ├── __init__.py
│   ├── processor.py             # Batch processor
│   ├── scheduler.py             # Job scheduler
│   └── tasks.py                 # Celery tasks
│
├── performance/                 # Performance optimization
│   ├── __init__.py
│   ├── optimizer.py             # Performance optimizer
│   ├── caching.py               # Caching strategies
│   └── streaming.py             # Streaming generation
│
├── export/                      # Export functionality
│   ├── __init__.py
│   ├── service.py               # Export service
│   ├── formats.py               # Export formats
│   └── delivery.py              # Delivery methods
│
└── tests/                       # Test suite
    ├── __init__.py
    ├── conftest.py
    ├── test_generation.py
    ├── test_templates.py
    ├── test_charts.py
    ├── test_tables.py
    ├── test_compression.py
    ├── test_accessibility.py
    ├── test_batch.py
    └── test_performance.py
```

### 15.4 Dependencies

```txt
# Core PDF Libraries
reportlab>=4.0.0
Pillow>=10.0.0
matplotlib>=3.7.0

# Optional PDF Libraries
weasyprint>=60.0
pikepdf>=8.0.0
PyPDF2>=3.0.0
pymupdf>=1.23.0

# Font Handling
fonttools>=4.40.0

# Performance
psutil>=5.9.0

# Testing
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-benchmark>=4.0.0
```

---

## Appendix A: Quick Reference

### A.1 Common Code Patterns

```python
# Generate a simple PDF
from app.pdf.generation.base import PDFMetadata, PageSettings
from app.pdf.generation.reportlab_engine import ReportLabPDFGenerator

metadata = PDFMetadata(title="My Report")
generator = ReportLabPDFGenerator(metadata=metadata)
generator.add_heading("Hello World", level=1)
generator.add_paragraph("This is my report.")
generator.generate(output_path="report.pdf")

# Generate with charts
from app.pdf.charts.generator import ChartGenerator

chart_gen = ChartGenerator()
chart_bytes = chart_gen.create_risk_matrix(risks)
generator.add_chart_image(chart_bytes, caption="Risk Matrix")

# Use templates
from app.pdf.templates.builder import TemplateBuilder, SectionContent

builder = TemplateBuilder("risk_assessment_v1")
builder.set_metadata(metadata)
builder.add_section_content("executive_summary", SectionContent(
    section_name="executive_summary",
    title="Executive Summary",
    paragraphs=["Summary text here."]
))
generator = builder.build()
generator.generate(output_path="report.pdf")
```

### A.2 Configuration Options

```python
# PDF Configuration
PDF_CONFIG = {
    'default_page_size': 'letter',
    'default_orientation': 'portrait',
    'default_margins': {'top': 72, 'bottom': 72, 'left': 72, 'right': 72},
    'image_dpi': 150,
    'image_quality': 85,
    'font_subsetting': True,
    'auto_compress': True,
    'compression_level': 'medium',
    'enable_accessibility': True,
    'cache_enabled': True,
    'cache_ttl_hours': 24,
}
```

---

## Summary

This document provides a comprehensive design for PDF generation capabilities in ResilienceAI, including:

1. **Architecture**: Hybrid approach using ReportLab for data-heavy reports and WeasyPrint for HTML-rich layouts
2. **Templates**: Pre-built templates for common report types (risk assessment, vulnerability scan, executive summary)
3. **Charts**: Matplotlib-based chart generation with ResilienceAI branding
4. **Tables**: Advanced table generation with severity styling
5. **Multi-page**: Pagination, TOC, and section management
6. **Styling**: Theme system with color schemes and typography
7. **Headers/Footers**: Configurable headers and footers with branding
8. **Export API**: FastAPI endpoints for single and batch exports
9. **Batch Processing**: Parallel processing with job management
10. **Compression**: Multiple compression methods for optimal file sizes
11. **Accessibility**: PDF/UA compliance and validation
12. **Performance**: Caching, streaming, and optimization strategies
13. **Testing**: Comprehensive test suite with unit, integration, and load tests

The implementation follows a phased approach, prioritizing core functionality first and adding advanced features in subsequent phases.

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: ResilienceAI Engineering Team*
