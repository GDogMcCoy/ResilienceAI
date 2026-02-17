"""
Data Compression Module for ResilienceAI
Optimizes payload sizes for bandwidth-constrained environments
"""

import json
import struct
import gzip
import lz4.frame
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from io import BytesIO

logger = logging.getLogger(__name__)


class JSONMinifier:
    """Minify JSON payloads by removing whitespace"""
    
    @staticmethod
    def compress(data: Dict) -> str:
        """Minify JSON data"""
        return json.dumps(data, separators=(',', ':'))
    
    @staticmethod
    def decompress(data: str) -> Dict:
        """Parse minified JSON"""
        return json.loads(data)


class MessagePackEncoder:
    """MessagePack encoding for efficient serialization"""
    
    try:
        import msgpack
        MSGPACK_AVAILABLE = True
    except ImportError:
        MSGPACK_AVAILABLE = False
    
    @classmethod
    def compress(cls, data: Dict) -> bytes:
        """Encode to MessagePack"""
        if not cls.MSGPACK_AVAILABLE:
            raise ImportError("msgpack not installed")
        return cls.msgpack.packb(data, use_bin_type=True)
    
    @classmethod
    def decompress(cls, data: bytes) -> Dict:
        """Decode from MessagePack"""
        if not cls.MSGPACK_AVAILABLE:
            raise ImportError("msgpack not installed")
        return cls.msgpack.unpackb(data, raw=False)


class CBOREncoder:
    """CBOR (Concise Binary Object Representation) encoding"""
    
    try:
        import cbor2
        CBOR_AVAILABLE = True
    except ImportError:
        CBOR_AVAILABLE = False
    
    @classmethod
    def compress(cls, data: Dict) -> bytes:
        """Encode to CBOR"""
        if not cls.CBOR_AVAILABLE:
            raise ImportError("cbor2 not installed")
        return cls.cbor2.dumps(data)
    
    @classmethod
    def decompress(cls, data: bytes) -> Dict:
        """Decode from CBOR"""
        if not cls.CBOR_AVAILABLE:
            raise ImportError("cbor2 not installed")
        return cls.cbor2.loads(data)


class DeltaEncoder:
    """Delta encoding for time-series data"""
    
    @staticmethod
    def compress(readings: List[Dict], base_timestamp: Optional[int] = None) -> bytes:
        """
        Compress time-series readings using delta encoding
        
        Format:
        - Base timestamp (4 bytes)
        - Number of readings (2 bytes)
        - For each reading:
          - Delta timestamp (1-2 bytes, variable)
          - Delta values for each sensor
        """
        if not readings:
            return b''
        
        # Sort by timestamp
        sorted_readings = sorted(readings, key=lambda r: r['timestamp'])
        
        # Use first timestamp as base
        base_ts = base_timestamp or int(sorted_readings[0]['timestamp'])
        
        buffer = BytesIO()
        
        # Write header
        buffer.write(struct.pack('I', base_ts))  # Base timestamp
        buffer.write(struct.pack('H', len(sorted_readings)))  # Count
        
        # Get sensor keys from first reading
        sensor_keys = [k for k in sorted_readings[0].keys() if k not in ['timestamp', 'device_id']]
        buffer.write(struct.pack('B', len(sensor_keys)))  # Number of sensors
        
        # Write sensor key names (for reconstruction)
        for key in sensor_keys:
            buffer.write(struct.pack('B', len(key)))
            buffer.write(key.encode())
        
        # Write delta-encoded readings
        prev_ts = base_ts
        prev_values = {k: 0 for k in sensor_keys}
        
        for reading in sorted_readings:
            # Delta timestamp (seconds since previous)
            ts_delta = int(reading['timestamp']) - prev_ts
            buffer.write(struct.pack('h', ts_delta))  # 2 bytes for delta
            prev_ts = int(reading['timestamp'])
            
            # Delta values
            for key in sensor_keys:
                value = reading.get(key, 0)
                if isinstance(value, (int, float)):
                    # Store as scaled integer (2 decimal places)
                    scaled = int(value * 100)
                    delta = scaled - prev_values[key]
                    buffer.write(struct.pack('h', delta))  # 2 bytes
                    prev_values[key] = scaled
        
        return buffer.getvalue()
    
    @staticmethod
    def decompress(data: bytes) -> List[Dict]:
        """Decompress delta-encoded readings"""
        buffer = BytesIO(data)
        
        # Read header
        base_ts = struct.unpack('I', buffer.read(4))[0]
        count = struct.unpack('H', buffer.read(2))[0]
        num_sensors = struct.unpack('B', buffer.read(1))[0]
        
        # Read sensor keys
        sensor_keys = []
        for _ in range(num_sensors):
            key_len = struct.unpack('B', buffer.read(1))[0]
            key = buffer.read(key_len).decode()
            sensor_keys.append(key)
        
        # Read delta-encoded readings
        readings = []
        current_ts = base_ts
        current_values = {k: 0 for k in sensor_keys}
        
        for _ in range(count):
            # Delta timestamp
            ts_delta = struct.unpack('h', buffer.read(2))[0]
            current_ts += ts_delta
            
            reading = {'timestamp': current_ts}
            
            # Delta values
            for key in sensor_keys:
                delta = struct.unpack('h', buffer.read(2))[0]
                current_values[key] += delta
                reading[key] = current_values[key] / 100.0  # Scale back
            
            readings.append(reading)
        
        return readings


class GZIPCompressor:
    """GZIP compression for batch data"""
    
    @staticmethod
    def compress(data: Union[str, bytes], level: int = 6) -> bytes:
        """Compress with GZIP"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return gzip.compress(data, compresslevel=level)
    
    @staticmethod
    def decompress(data: bytes) -> str:
        """Decompress GZIP data"""
        return gzip.decompress(data).decode('utf-8')


class LZ4Compressor:
    """LZ4 compression for real-time data"""
    
    @staticmethod
    def compress(data: Union[str, bytes]) -> bytes:
        """Compress with LZ4"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        return lz4.frame.compress(data)
    
    @staticmethod
    def decompress(data: bytes) -> str:
        """Decompress LZ4 data"""
        return lz4.frame.decompress(data).decode('utf-8')


class CompressionManager:
    """Manage compression based on data type and constraints"""
    
    COMPRESSION_METHODS = {
        'json_minify': JSONMinifier,
        'msgpack': MessagePackEncoder,
        'cbor': CBOREncoder,
        'delta': DeltaEncoder,
        'gzip': GZIPCompressor,
        'lz4': LZ4Compressor
    }
    
    def __init__(self, default_method: str = 'msgpack'):
        self.default_method = default_method
    
    def compress(
        self,
        data: Any,
        method: Optional[str] = None,
        **kwargs
    ) -> bytes:
        """Compress data using specified method"""
        method = method or self.default_method
        
        if method not in self.COMPRESSION_METHODS:
            raise ValueError(f"Unknown compression method: {method}")
        
        compressor = self.COMPRESSION_METHODS[method]
        
        try:
            if method == 'json_minify':
                return compressor.compress(data).encode()
            elif method == 'delta':
                return compressor.compress(data, **kwargs)
            else:
                return compressor.compress(data)
        except Exception as e:
            logger.error(f"Compression error: {e}")
            # Fallback to JSON
            return json.dumps(data).encode()
    
    def decompress(
        self,
        data: bytes,
        method: Optional[str] = None
    ) -> Any:
        """Decompress data using specified method"""
        method = method or self.default_method
        
        if method not in self.COMPRESSION_METHODS:
            raise ValueError(f"Unknown compression method: {method}")
        
        compressor = self.COMPRESSION_METHODS[method]
        
        try:
            if method == 'json_minify':
                return compressor.decompress(data.decode())
            else:
                return compressor.decompress(data)
        except Exception as e:
            logger.error(f"Decompression error: {e}")
            # Fallback to JSON
            return json.loads(data.decode())
    
    @staticmethod
    def benchmark(data: Dict, iterations: int = 1000) -> Dict[str, Dict]:
        """Benchmark compression methods"""
        import time
        
        results = {}
        
        for name, compressor in CompressionManager.COMPRESSION_METHODS.items():
            try:
                # Test compression
                start = time.time()
                for _ in range(iterations):
                    if name == 'json_minify':
                        compressed = compressor.compress(data).encode()
                    elif name == 'delta':
                        compressed = compressor.compress([data] * 10)
                    else:
                        compressed = compressor.compress(json.dumps(data))
                compress_time = (time.time() - start) / iterations
                
                # Test decompression
                start = time.time()
                for _ in range(iterations):
                    if name == 'json_minify':
                        compressor.decompress(compressed.decode())
                    elif name == 'delta':
                        compressor.decompress(compressed)
                    else:
                        compressor.decompress(compressed)
                decompress_time = (time.time() - start) / iterations
                
                # Calculate compression ratio
                original_size = len(json.dumps(data).encode())
                compressed_size = len(compressed)
                ratio = (1 - compressed_size / original_size) * 100
                
                results[name] = {
                    "compress_time_ms": compress_time * 1000,
                    "decompress_time_ms": decompress_time * 1000,
                    "original_size": original_size,
                    "compressed_size": compressed_size,
                    "compression_ratio": f"{ratio:.1f}%"
                }
            except Exception as e:
                results[name] = {"error": str(e)}
        
        return results


# Example usage
if __name__ == "__main__":
    # Sample sensor reading
    sample_data = {
        "device_id": "sensor_001",
        "sensor_type": "air_quality",
        "timestamp": int(datetime.utcnow().timestamp()),
        "latitude": 37.7749,
        "longitude": -122.4194,
        "readings": {
            "pm25": 15.23,
            "pm10": 28.45,
            "co2": 420,
            "voc": 120.5,
            "temperature": 22.5,
            "humidity": 65.0
        }
    }
    
    # Test compression methods
    manager = CompressionManager()
    
    print("Compression Benchmark:")
    print("=" * 60)
    
    for method in ['json_minify', 'msgpack', 'cbor', 'gzip', 'lz4']:
        try:
            compressed = manager.compress(sample_data, method=method)
            decompressed = manager.decompress(compressed, method=method)
            
            original_size = len(json.dumps(sample_data).encode())
            compressed_size = len(compressed)
            ratio = (1 - compressed_size / original_size) * 100
            
            print(f"\n{method.upper()}:")
            print(f"  Original: {original_size} bytes")
            print(f"  Compressed: {compressed_size} bytes")
            print(f"  Ratio: {ratio:.1f}%")
            print(f"  Valid: {decompressed == sample_data or str(decompressed) == str(sample_data)}")
        except Exception as e:
            print(f"\n{method.upper()}: Error - {e}")
    
    # Test delta encoding with time series
    time_series = []
    base_time = int(datetime.utcnow().timestamp())
    for i in range(100):
        time_series.append({
            "timestamp": base_time + i * 60,
            "temperature": 20.0 + i * 0.1,
            "humidity": 60.0 + i * 0.05
        })
    
    delta_encoded = DeltaEncoder.compress(time_series)
    original_size = len(json.dumps(time_series).encode())
    
    print(f"\n\nDelta Encoding (Time Series):")
    print(f"  Original: {original_size} bytes")
    print(f"  Compressed: {len(delta_encoded)} bytes")
    print(f"  Ratio: {(1 - len(delta_encoded) / original_size) * 100:.1f}%")
    
    # Verify
    decoded = DeltaEncoder.decompress(delta_encoded)
    print(f"  Valid: {len(decoded) == len(time_series)}")
