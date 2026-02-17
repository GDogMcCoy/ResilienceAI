# /mnt/okcomputer/output/resilience_ai_analysis/code/compression_engine.py
"""
Compression Engine for ResilienceAI
Provides multiple compression algorithms with automatic selection.
"""

import zstandard as zstd
import lz4.frame
import gzip
import brotli
import snappy
from typing import Dict, Optional, Tuple
from enum import Enum
import time


class CompressionAlgorithm(Enum):
    """Compression algorithm enumeration."""
    ZSTD = "zstd"
    LZ4 = "lz4"
    GZIP = "gzip"
    BROTLI = "brotli"
    SNAPPY = "snappy"
    NONE = "none"


class CompressionEngine:
    """Compression engine for ResilienceAI archival data."""
    
    # Algorithm characteristics
    ALGORITHM_CONFIG = {
        CompressionAlgorithm.ZSTD: {
            "compression_levels": range(1, 23),
            "default_level": 3,
            "typical_ratio": 3.5,
            "speed": "fast",
            "cpu_usage": "medium",
            "best_for": ["general", "large_files", "text"]
        },
        CompressionAlgorithm.LZ4: {
            "compression_levels": range(1, 13),
            "default_level": 1,
            "typical_ratio": 2.5,
            "speed": "very_fast",
            "cpu_usage": "low",
            "best_for": ["realtime", "streaming", "low_latency"]
        },
        CompressionAlgorithm.GZIP: {
            "compression_levels": range(1, 10),
            "default_level": 6,
            "typical_ratio": 3.0,
            "speed": "medium",
            "cpu_usage": "medium",
            "best_for": ["compatibility", "web", "legacy"]
        },
        CompressionAlgorithm.BROTLI: {
            "compression_levels": range(0, 12),
            "default_level": 4,
            "typical_ratio": 4.0,
            "speed": "slow",
            "cpu_usage": "high",
            "best_for": ["maximum_compression", "text", "web"]
        },
        CompressionAlgorithm.SNAPPY: {
            "compression_levels": [1],
            "default_level": 1,
            "typical_ratio": 2.0,
            "speed": "very_fast",
            "cpu_usage": "low",
            "best_for": ["realtime", "database", "low_cpu"]
        }
    }
    
    def __init__(self):
        self.stats = {
            "total_compressed": 0,
            "total_decompressed": 0,
            "bytes_saved": 0,
            "compression_time": 0.0
        }
    
    def analyze_data(self, data: bytes) -> Dict:
        """Analyze data to determine optimal compression strategy."""
        sample_size = min(len(data), 1024 * 1024)  # 1MB sample
        sample = data[:sample_size]
        
        # Check if data is already compressed
        compression_ratio = self._estimate_compressibility(sample)
        
        # Detect data type
        data_type = self._detect_data_type(sample)
        
        # Determine if compression is beneficial
        is_compressible = compression_ratio > 1.1
        
        return {
            "size_bytes": len(data),
            "sample_compressibility": compression_ratio,
            "data_type": data_type,
            "is_compressible": is_compressible,
            "recommended_algorithm": self._recommend_algorithm(data_type, len(data))
        }
    
    def _estimate_compressibility(self, sample: bytes) -> float:
        """Estimate how compressible data is."""
        # Quick compression test
        compressed = zstd.compress(sample, level=1)
        return len(sample) / len(compressed) if len(compressed) > 0 else 1.0
    
    def _detect_data_type(self, sample: bytes) -> str:
        """Detect type of data for compression optimization."""
        # Check for JSON
        try:
            import json
            json.loads(sample.decode('utf-8'))
            return "json"
        except:
            pass
        
        # Check for CSV
        if b',' in sample and b'\n' in sample:
            return "csv"
        
        # Check for text
        try:
            sample.decode('utf-8')
            return "text"
        except:
            pass
        
        # Check for binary patterns
        if sample[:4] in [b'\x89PNG', b'\xff\xd8\xff', b'PK\x03\x04']:
            return "already_compressed"
        
        return "binary"
    
    def _recommend_algorithm(self, data_type: str, size: int) -> CompressionAlgorithm:
        """Recommend compression algorithm based on data characteristics."""
        if data_type == "already_compressed":
            return CompressionAlgorithm.NONE
        
        if data_type in ["json", "csv", "text"]:
            if size > 100 * 1024 * 1024:  # > 100MB
                return CompressionAlgorithm.ZSTD
            else:
                return CompressionAlgorithm.LZ4
        
        if size > 1024 * 1024 * 1024:  # > 1GB
            return CompressionAlgorithm.ZSTD
        
        return CompressionAlgorithm.LZ4
    
    def compress(self, data: bytes, 
                 algorithm: Optional[CompressionAlgorithm] = None,
                 level: Optional[int] = None) -> Tuple[bytes, Dict]:
        """Compress data with specified or auto-selected algorithm."""
        start_time = time.time()
        
        # Auto-select algorithm if not specified
        if algorithm is None:
            analysis = self.analyze_data(data)
            algorithm = analysis["recommended_algorithm"]
        
        if algorithm == CompressionAlgorithm.NONE:
            return data, {
                "algorithm": "none",
                "original_size": len(data),
                "compressed_size": len(data),
                "ratio": 1.0,
                "time_seconds": 0.0
            }
        
        # Get default level if not specified
        if level is None:
            level = self.ALGORITHM_CONFIG[algorithm]["default_level"]
        
        # Compress based on algorithm
        if algorithm == CompressionAlgorithm.ZSTD:
            compressed = self._compress_zstd(data, level)
        elif algorithm == CompressionAlgorithm.LZ4:
            compressed = self._compress_lz4(data, level)
        elif algorithm == CompressionAlgorithm.GZIP:
            compressed = self._compress_gzip(data, level)
        elif algorithm == CompressionAlgorithm.BROTLI:
            compressed = self._compress_brotli(data, level)
        elif algorithm == CompressionAlgorithm.SNAPPY:
            compressed = self._compress_snappy(data)
        else:
            compressed = data
        
        elapsed = time.time() - start_time
        
        # Update stats
        self.stats["total_compressed"] += 1
        self.stats["bytes_saved"] += len(data) - len(compressed)
        self.stats["compression_time"] += elapsed
        
        return compressed, {
            "algorithm": algorithm.value,
            "level": level,
            "original_size": len(data),
            "compressed_size": len(compressed),
            "ratio": len(data) / len(compressed) if len(compressed) > 0 else 1.0,
            "time_seconds": elapsed
        }
    
    def decompress(self, data: bytes, 
                   algorithm: CompressionAlgorithm) -> Tuple[bytes, Dict]:
        """Decompress data with specified algorithm."""
        start_time = time.time()
        
        if algorithm == CompressionAlgorithm.NONE:
            return data, {"algorithm": "none", "time_seconds": 0.0}
        
        if algorithm == CompressionAlgorithm.ZSTD:
            decompressed = self._decompress_zstd(data)
        elif algorithm == CompressionAlgorithm.LZ4:
            decompressed = self._decompress_lz4(data)
        elif algorithm == CompressionAlgorithm.GZIP:
            decompressed = self._decompress_gzip(data)
        elif algorithm == CompressionAlgorithm.BROTLI:
            decompressed = self._decompress_brotli(data)
        elif algorithm == CompressionAlgorithm.SNAPPY:
            decompressed = self._decompress_snappy(data)
        else:
            decompressed = data
        
        elapsed = time.time() - start_time
        
        self.stats["total_decompressed"] += 1
        
        return decompressed, {
            "algorithm": algorithm.value,
            "compressed_size": len(data),
            "decompressed_size": len(decompressed),
            "time_seconds": elapsed
        }
    
    def _compress_zstd(self, data: bytes, level: int) -> bytes:
        """Compress using ZSTD."""
        compressor = zstd.ZstdCompressor(level=level)
        return compressor.compress(data)
    
    def _decompress_zstd(self, data: bytes) -> bytes:
        """Decompress using ZSTD."""
        decompressor = zstd.ZstdDecompressor()
        return decompressor.decompress(data)
    
    def _compress_lz4(self, data: bytes, level: int) -> bytes:
        """Compress using LZ4."""
        return lz4.frame.compress(data, compression_level=level)
    
    def _decompress_lz4(self, data: bytes) -> bytes:
        """Decompress using LZ4."""
        return lz4.frame.decompress(data)
    
    def _compress_gzip(self, data: bytes, level: int) -> bytes:
        """Compress using GZIP."""
        return gzip.compress(data, compresslevel=level)
    
    def _decompress_gzip(self, data: bytes) -> bytes:
        """Decompress using GZIP."""
        return gzip.decompress(data)
    
    def _compress_brotli(self, data: bytes, level: int) -> bytes:
        """Compress using Brotli."""
        return brotli.compress(data, quality=level)
    
    def _decompress_brotli(self, data: bytes) -> bytes:
        """Decompress using Brotli."""
        return brotli.decompress(data)
    
    def _compress_snappy(self, data: bytes) -> bytes:
        """Compress using Snappy."""
        return snappy.compress(data)
    
    def _decompress_snappy(self, data: bytes) -> bytes:
        """Decompress using Snappy."""
        return snappy.decompress(data)
    
    def get_stats(self) -> Dict:
        """Get compression statistics."""
        return self.stats.copy()


if __name__ == "__main__":
    # Example usage
    engine = CompressionEngine()
    
    # Sample data
    sample_data = b'{"incident_id": "INC-2024-001", "severity": "high", "description": "System anomaly detected"}' * 1000
    
    print(f"Original size: {len(sample_data)} bytes")
    
    # Analyze data
    analysis = engine.analyze_data(sample_data)
    print(f"\nAnalysis: {analysis}")
    
    # Compress with different algorithms
    for algo in [CompressionAlgorithm.ZSTD, CompressionAlgorithm.LZ4, CompressionAlgorithm.GZIP]:
        compressed, info = engine.compress(sample_data, algorithm=algo)
        print(f"\n{algo.value}:")
        print(f"  Compressed size: {info['compressed_size']} bytes")
        print(f"  Ratio: {info['ratio']:.2f}x")
        print(f"  Time: {info['time_seconds']*1000:.2f}ms")
    
    # Auto-select algorithm
    compressed, info = engine.compress(sample_data)
    print(f"\nAuto-selected ({info['algorithm']}):")
    print(f"  Compressed size: {info['compressed_size']} bytes")
    print(f"  Ratio: {info['ratio']:.2f}x")
