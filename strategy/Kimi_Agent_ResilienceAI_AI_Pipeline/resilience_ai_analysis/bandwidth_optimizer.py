"""
Bandwidth Optimization for ResilienceAI Edge
============================================
Techniques to minimize bandwidth usage in edge-cloud communication.
"""

import gzip
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


class CompressionAlgorithm(Enum):
    """Supported compression algorithms"""
    GZIP = "gzip"
    LZ4 = "lz4"
    ZSTD = "zstd"
    BROTLI = "brotli"
    NONE = "none"


@dataclass
class CompressionResult:
    """Result of compression operation"""
    original_size: int
    compressed_size: int
    algorithm: CompressionAlgorithm
    compression_ratio: float
    compression_time_ms: float


class DataCompressor:
    """Intelligent data compression for edge communication"""
    
    def __init__(self, default_algorithm: CompressionAlgorithm = CompressionAlgorithm.ZSTD):
        self.default_algorithm = default_algorithm
        self.compression_stats = {}
        
    def compress(self, data: Any, algorithm: Optional[CompressionAlgorithm] = None):
        """Compress data with specified algorithm"""
        import time
        
        algo = algorithm or self.default_algorithm
        start_time = time.time()
        
        if not isinstance(data, (bytes, str)):
            serialized = json.dumps(data).encode('utf-8')
        elif isinstance(data, str):
            serialized = data.encode('utf-8')
        else:
            serialized = data
            
        original_size = len(serialized)
        
        if algo == CompressionAlgorithm.GZIP:
            compressed = gzip.compress(serialized, compresslevel=6)
        elif algo == CompressionAlgorithm.LZ4:
            import lz4.frame
            compressed = lz4.frame.compress(serialized)
        elif algo == CompressionAlgorithm.ZSTD:
            import zstandard
            compressor = zstandard.ZstdCompressor(level=3)
            compressed = compressor.compress(serialized)
        elif algo == CompressionAlgorithm.BROTLI:
            import brotli
            compressed = brotli.compress(serialized)
        else:
            compressed = serialized
            
        compressed_size = len(compressed)
        compression_time = (time.time() - start_time) * 1000
        
        result = CompressionResult(
            original_size=original_size,
            compressed_size=compressed_size,
            algorithm=algo,
            compression_ratio=original_size / max(compressed_size, 1),
            compression_time_ms=compression_time
        )
        
        self._update_stats(algo, result)
        return result, compressed
        
    def decompress(self, compressed_data: bytes, algorithm: CompressionAlgorithm):
        """Decompress data"""
        if algorithm == CompressionAlgorithm.GZIP:
            return gzip.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.LZ4:
            import lz4.frame
            return lz4.frame.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.ZSTD:
            import zstandard
            decompressor = zstandard.ZstdDecompressor()
            return decompressor.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.BROTLI:
            import brotli
            return brotli.decompress(compressed_data)
        else:
            return compressed_data
            
    def _update_stats(self, algorithm: CompressionAlgorithm, result: CompressionResult):
        """Update compression statistics"""
        if algorithm not in self.compression_stats:
            self.compression_stats[algorithm] = {
                "total_original": 0,
                "total_compressed": 0,
                "count": 0
            }
        self.compression_stats[algorithm]["total_original"] += result.original_size
        self.compression_stats[algorithm]["total_compressed"] += result.compressed_size
        self.compression_stats[algorithm]["count"] += 1
        
    def select_optimal_algorithm(self, data_size: int, data_type: str) -> CompressionAlgorithm:
        """Select optimal compression algorithm based on data characteristics"""
        if data_size < 1024:
            return CompressionAlgorithm.LZ4
        if data_size > 10 * 1024 * 1024:
            return CompressionAlgorithm.ZSTD
        if data_type in ["json", "text", "xml"]:
            return CompressionAlgorithm.BROTLI
        return CompressionAlgorithm.ZSTD


class SelectiveSyncManager:
    """Manages selective synchronization to minimize bandwidth"""
    
    def __init__(self):
        self.sync_rules = {}
        
    def define_sync_rule(self, data_type: str, sync_conditions: Dict[str, Any], priority: int = 5):
        """Define sync rules for a data type"""
        self.sync_rules[data_type] = {
            "conditions": sync_conditions,
            "priority": priority
        }
        
    def should_sync(self, data_type: str, data: Any, network_quality: float) -> bool:
        """Determine if data should be synced based on rules"""
        if data_type not in self.sync_rules:
            return True
            
        rules = self.sync_rules[data_type]
        conditions = rules["conditions"]
        
        if "min_network_quality" in conditions:
            if network_quality < conditions["min_network_quality"]:
                return False
                
        if "max_age_seconds" in conditions and "timestamp" in data:
            import time
            age = time.time() - data["timestamp"]
            if age > conditions["max_age_seconds"]:
                return False
                
        if "min_significance" in conditions and "significance" in data:
            if data["significance"] < conditions["min_significance"]:
                return False
                
        return True


class DeltaEncoder:
    """Encodes only changes (deltas) instead of full data"""
    
    @staticmethod
    def encode_delta(previous: Dict, current: Dict) -> Dict:
        """Encode delta between two data states"""
        delta = {"_type": "delta", "changes": {}}
        
        all_keys = set(previous.keys()) | set(current.keys())
        
        for key in all_keys:
            if key not in previous:
                delta["changes"][key] = {"op": "add", "value": current[key]}
            elif key not in current:
                delta["changes"][key] = {"op": "delete"}
            elif previous[key] != current[key]:
                if isinstance(previous[key], dict) and isinstance(current[key], dict):
                    nested_delta = DeltaEncoder.encode_delta(previous[key], current[key])
                    if nested_delta["changes"]:
                        delta["changes"][key] = {"op": "update", "delta": nested_delta}
                else:
                    delta["changes"][key] = {"op": "update", "value": current[key]}
                    
        return delta
        
    @staticmethod
    def apply_delta(base: Dict, delta: Dict) -> Dict:
        """Apply delta to base data"""
        result = base.copy()
        
        for key, change in delta.get("changes", {}).items():
            op = change["op"]
            
            if op == "add":
                result[key] = change["value"]
            elif op == "delete":
                result.pop(key, None)
            elif op == "update":
                if "delta" in change:
                    result[key] = DeltaEncoder.apply_delta(result.get(key, {}), change["delta"])
                else:
                    result[key] = change["value"]
                    
        return result


class ImageOptimizer:
    """Optimizes images for transmission from edge"""
    
    @staticmethod
    def optimize_for_transmission(image_data: bytes, target_size_kb: int = 100) -> bytes:
        """Optimize image for transmission"""
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(image_data))
        
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        current_size_kb = len(image_data) / 1024
        scale_factor = min(1.0, (target_size_kb / current_size_kb) ** 0.5)
        
        new_width = int(img.width * scale_factor)
        new_height = int(img.height * scale_factor)
        
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        quality = 95
        
        while quality > 20:
            output.seek(0)
            output.truncate()
            img.save(output, format='JPEG', quality=quality, optimize=True)
            
            if output.tell() / 1024 <= target_size_kb:
                break
                
            quality -= 5
            
        return output.getvalue()
        
    @staticmethod
    def create_thumbnail(image_data: bytes, max_size: int = 256) -> bytes:
        """Create thumbnail for quick preview"""
        from PIL import Image
        import io
        
        img = Image.open(io.BytesIO(image_data))
        img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
        
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=70, optimize=True)
        return output.getvalue()
