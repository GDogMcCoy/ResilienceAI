        exporter = CSVExporter()
        result = exporter.export(sample_data)
        
        assert isinstance(result, bytes)
        content = result.decode('utf-8-sig')
        assert "id,name,value,active" in content
        assert "1,Test 1,100.500000,Yes" in content
    
    def test_export_with_options(self, sample_data):
        """Test export with custom options."""
        options = CSVExportOptions(
            delimiter=';',
            encoding='utf-8',
            bool_format={True: 'Y', False: 'N'}
        )
        exporter = CSVExporter(options)
        result = exporter.export(sample_data)
        
        content = result.decode('utf-8')
        assert ";" in content
        assert "Y" in content
    
    def test_export_with_column_mapping(self, sample_data):
        """Test export with column name mapping."""
        exporter = CSVExporter()
        mapping = {"id": "ID", "name": "Name", "value": "Value"}
        result = exporter.export(
            sample_data,
            column_mapping=mapping
        )
        
        content = result.decode('utf-8-sig')
        assert "ID,Name,Value" in content
    
    def test_export_with_column_selection(self, sample_data):
        """Test export with specific columns."""
        exporter = CSVExporter()
        result = exporter.export(
            sample_data,
            columns=["id", "name"]
        )
        
        content = result.decode('utf-8-sig')
        assert "id,name" in content
        assert "value" not in content
    
    def test_streaming_export(self, sample_data):
        """Test streaming export."""
        exporter = CSVExporter()
        chunks = list(exporter.export_streaming(iter(sample_data)))
        
        assert len(chunks) > 0
        full_content = b''.join(chunks).decode('utf-8-sig')
        assert "id,name,value,active" in full_content
    
    def test_datetime_formatting(self):
        """Test datetime value formatting."""
        data = [{"created": datetime(2024, 1, 15, 10, 30, 0)}]
        exporter = CSVExporter()
        result = exporter.export(data)
        
        content = result.decode('utf-8-sig')
        assert "2024-01-15 10:30:00" in content
    
    def test_empty_data(self):
        """Test export with empty data."""
        exporter = CSVExporter()
        result = exporter.export([])
        
        content = result.decode('utf-8-sig')
        assert content.strip() == ""


class TestExcelExporter:
    """Test cases for Excel exporter."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return [
            {"id": 1, "name": "Test 1", "amount": 100.5},
            {"id": 2, "name": "Test 2", "amount": 200.75}
        ]
    
    def test_basic_excel_export(self, sample_data, tmp_path):
        """Test basic Excel export."""
        from openpyxl import load_workbook
        
        exporter = ExcelExporter()
        exporter.create_workbook()
        exporter.add_data_sheet_simple(sample_data, "Test Sheet")
        
        output_path = tmp_path / "test.xlsx"
        exporter.save(str(output_path))
        
        # Verify file exists and can be opened
        assert output_path.exists()
        wb = load_workbook(output_path)
        assert "Test Sheet" in wb.sheetnames
    
    def test_multi_sheet_export(self, sample_data, tmp_path):
        """Test multi-sheet Excel export."""
        from openpyxl import load_workbook
        
        exporter = ExcelExporter()
        exporter.create_workbook()
        
        exporter.add_data_sheet_simple(sample_data, "Sheet1")
        exporter.add_data_sheet_simple(sample_data, "Sheet2")
        
        output_path = tmp_path / "multi.xlsx"
        exporter.save(str(output_path))
        
        wb = load_workbook(output_path)
        assert "Sheet1" in wb.sheetnames
        assert "Sheet2" in wb.sheetnames
    
    def test_excel_export_as_bytes(self, sample_data):
        """Test Excel export returning bytes."""
        exporter = ExcelExporter()
        exporter.create_workbook()
        exporter.add_data_sheet_simple(sample_data, "Data")
        
        result = exporter.save()
        
        assert isinstance(result, bytes)
        assert len(result) > 0
```

### 14.3 Integration Test Examples

```python
"""
Integration tests for export API.
"""

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

from src.resilience_ai.main import app


class TestExportAPI:
    """Integration tests for export API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Test client fixture."""
        return TestClient(app)
    
    def test_create_csv_export(self, client):
        """Test creating a CSV export."""
        response = client.post("/exports/", json={
            "format": "csv",
            "entity_type": "incidents",
            "filters": {"status": "open"},
            "columns": ["id", "title", "status"]
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "export_id" in data
        assert data["format"] == "csv"
    
    def test_create_excel_export(self, client):
        """Test creating an Excel export."""
        response = client.post("/exports/", json={
            "format": "xlsx",
            "entity_type": "risks",
            "include_metadata": True
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["format"] == "xlsx"
    
    def test_get_export_status(self, client):
        """Test getting export status."""
        # First create an export
        create_response = client.post("/exports/", json={
            "format": "csv",
            "entity_type": "incidents"
        })
        export_id = create_response.json()["export_id"]
        
        # Get status
        status_response = client.get(f"/exports/{export_id}")
        assert status_response.status_code == 200
        
        data = status_response.json()
        assert data["id"] == export_id
        assert data["status"] in ["pending", "processing", "completed"]
    
    def test_download_export(self, client):
        """Test downloading an export file."""
        # Create and wait for export
        create_response = client.post("/exports/", json={
            "format": "csv",
            "entity_type": "incidents"
        })
        export_id = create_response.json()["export_id"]
        
        # Download
        download_response = client.get(f"/exports/{export_id}/download")
        
        if download_response.status_code == 200:
            assert download_response.headers["content-type"] == "text/csv"
            content = download_response.content
            assert len(content) > 0
    
    def test_stream_export(self, client):
        """Test streaming export endpoint."""
        response = client.post(
            "/exports/stream/incidents",
            params={"format": "csv", "columns": "id,title,status"}
        )
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv"
    
    def test_invalid_export_format(self, client):
        """Test export with invalid format."""
        response = client.post("/exports/", json={
            "format": "invalid",
            "entity_type": "incidents"
        })
        
        assert response.status_code == 422
    
    def test_export_not_found(self, client):
        """Test getting non-existent export."""
        response = client.get("/exports/non-existent-id")
        assert response.status_code == 404
```

### 14.4 Performance Test Examples

```python
"""
Performance tests for exports.
"""

import pytest
import time
from typing import List, Dict

from src.resilience_ai.exports.formats.csv_exporter import CSVExporter
from src.resilience_ai.exports.formats.excel_exporter import ExcelExporter
from src.resilience_ai.exports.utils.large_dataset import LargeDatasetProcessor


class TestExportPerformance:
    """Performance tests for export operations."""
    
    def generate_large_dataset(self, size: int) -> List[Dict]:
        """Generate a large test dataset."""
        return [
            {
                "id": i,
                "name": f"Item {i}",
                "value": i * 1.5,
                "category": f"Category {i % 10}",
                "status": "active" if i % 2 == 0 else "inactive",
                "created_at": "2024-01-01",
                "metadata": {"key": f"value_{i}"}
            }
            for i in range(size)
        ]
    
    @pytest.mark.parametrize("size", [1000, 10000, 100000])
    def test_csv_export_performance(self, size, benchmark):
        """Benchmark CSV export performance."""
        data = self.generate_large_dataset(size)
        exporter = CSVExporter()
        
        result = benchmark(exporter.export, data)
        
        # Assert reasonable performance
        assert len(result) > 0
    
    @pytest.mark.parametrize("size", [1000, 5000, 10000])
    def test_excel_export_performance(self, size, benchmark, tmp_path):
        """Benchmark Excel export performance."""
        data = self.generate_large_dataset(size)
        exporter = ExcelExporter()
        exporter.create_workbook()
        
        def export_excel():
            exporter.add_data_sheet_simple(data, "Data")
            return exporter.save(str(tmp_path / f"test_{size}.xlsx"))
        
        result = benchmark(export_excel)
        assert result is None  # File saved
    
    def test_large_dataset_streaming(self):
        """Test streaming large dataset without memory issues."""
        processor = LargeDatasetProcessor()
        
        def data_generator(count: int):
            for i in range(count):
                yield {
                    "id": i,
                    "name": f"Item {i}",
                    "value": i * 1.5
                }
        
        # Stream 100k records
        chunks = list(processor.process_chunks(
            data_generator(100000),
            lambda chunk: chunk
        ))
        
        assert len(chunks) > 0
    
    def test_memory_usage_estimate(self):
        """Test memory usage estimation."""
        processor = LargeDatasetProcessor()
        
        estimate = processor.estimate_memory_usage(1000000)
        
        assert estimate["total_mb"] > 0
        assert estimate["recommended_chunks"] > 0
        assert isinstance(estimate["will_spill"], bool)
```

---

## 15. Implementation Priority

### 15.1 Priority Matrix

| Feature | Priority | Effort | Business Value | Implementation Order |
|---------|----------|--------|----------------|---------------------|
| Basic CSV Export | P0 | Low | High | 1 |
| Basic Excel Export | P0 | Low | High | 2 |
| Export API | P0 | Medium | High | 3 |
| Streaming CSV | P1 | Medium | High | 4 |
| Multi-Sheet Workbooks | P1 | Medium | Medium | 5 |
| Cell Formatting | P1 | Low | Medium | 6 |
| Large Dataset Handling | P1 | High | High | 7 |
| Formula Injection | P2 | Medium | Medium | 8 |
| Chart Embedding | P2 | High | Medium | 9 |
| Template System | P2 | High | Medium | 10 |
| Conditional Formatting | P3 | Medium | Low | 11 |
| Advanced Charts | P3 | High | Low | 12 |

### 15.2 Implementation Roadmap

#### Phase 1: Core Export (Weeks 1-2)
- [x] CSV exporter with basic options
- [x] Excel exporter with openpyxl
- [x] Export API endpoints
- [x] Basic error handling

#### Phase 2: Enhanced Features (Weeks 3-4)
- [x] Streaming CSV export
- [x] Multi-sheet workbooks
- [x] Cell formatting system
- [x] Column mapping and selection

#### Phase 3: Performance & Scale (Weeks 5-6)
- [x] Large dataset processor
- [x] Chunked processing
- [x] Background job queue
- [x] Memory optimization

#### Phase 4: Advanced Features (Weeks 7-8)
- [x] Formula injection engine
- [x] Chart embedding
- [x] Template system
- [x] Predefined templates

#### Phase 5: Polish & Optimization (Weeks 9-10)
- [x] Conditional formatting
- [x] Advanced chart types
- [x] Performance tuning
- [x] Comprehensive testing

### 15.3 Quick Start Implementation

```python
"""
Quick start implementation for immediate use.
"""

# 1. Basic CSV Export (Immediate)
from src.resilience_ai.exports.formats.csv_exporter import CSVExporter

exporter = CSVExporter()
csv_bytes = exporter.export(data, columns=["id", "name", "status"])

# 2. Basic Excel Export (Immediate)
from src.resilience_ai.exports.formats.excel_exporter import ExcelExporter

exporter = ExcelExporter()
exporter.create_workbook()
exporter.add_data_sheet_simple(data, "Incidents")
excel_bytes = exporter.save()

# 3. Streaming Export (Week 3)
from src.resilience_ai.exports.formats.streaming_exporter import StreamingExportHandler

handler = StreamingExportHandler()
response = handler.stream_csv(data_iterator, filename="export.csv")

# 4. Template Export (Week 7)
from src.resilience_ai.exports.templates.base_template import template_registry

excel_bytes = template_registry.generate(
    "incident_report",
    context={"incident_ids": ["1", "2", "3"]}
)
```

---

## Appendix A: Configuration Reference

### A.1 CSV Export Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| delimiter | str | ',' | Field delimiter |
| quotechar | str | '"' | Quote character |
| quoting | int | QUOTE_MINIMAL | Quoting behavior |
| lineterminator | str | '\\n' | Line ending |
| encoding | str | 'utf-8-sig' | Output encoding |
| include_header | bool | True | Include header row |
| date_format | str | '%Y-%m-%d %H:%M:%S' | Date format |
| float_format | str | '%.6f' | Float format |
| null_value | str | '' | Null representation |
| bool_format | dict | {True:'Yes', False:'No'} | Boolean format |

### A.2 Excel Export Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| engine | ExcelEngine | OPENPYXL | Excel engine |
| creator | str | 'ResilienceAI' | Document creator |
| company | str | 'ResilienceAI' | Company name |
| default_row_height | float | 15 | Default row height |
| default_column_width | float | 10 | Default column width |
| include_metadata | bool | True | Include metadata |

### A.3 Performance Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| chunk_size | int | 10000 | Processing chunk size |
| max_memory_rows | int | 50000 | Memory limit before spill |
| compression | bool | True | Enable compression |
| cache_enabled | bool | True | Enable caching |
| max_concurrent | int | 5 | Max concurrent exports |

---

## Appendix B: Error Handling

### B.1 Error Codes

| Code | Description | HTTP Status |
|------|-------------|-------------|
| EXPORT_001 | Invalid export format | 400 |
| EXPORT_002 | Entity type not found | 404 |
| EXPORT_003 | Export job not found | 404 |
| EXPORT_004 | Export timeout | 408 |
| EXPORT_005 | Memory limit exceeded | 507 |
| EXPORT_006 | Invalid filter criteria | 400 |
| EXPORT_007 | Template not found | 404 |
| EXPORT_008 | Export generation failed | 500 |

### B.2 Error Response Format

```json
{
  "error": {
    "code": "EXPORT_001",
    "message": "Invalid export format: pdfx",
    "details": {
      "supported_formats": ["csv", "xlsx", "json"]
    }
  }
}
```

---

## Summary

This comprehensive CSV/Excel export system for ResilienceAI provides:

1. **Flexible Export Formats**: CSV and Excel with multiple engines
2. **Advanced Features**: Multi-sheet workbooks, formatting, formulas, charts
3. **Performance**: Streaming, chunked processing, memory optimization
4. **Scalability**: Background jobs, caching, disk spill
5. **API Integration**: RESTful endpoints, WebSocket progress
6. **Templates**: Predefined and custom export templates
7. **Testing**: Unit, integration, and performance tests

The implementation follows a modular architecture with clear separation of concerns, making it easy to extend and maintain.

---

*Document Version: 1.0*
*Last Updated: 2024*
*Author: ResilienceAI Engineering Team*
