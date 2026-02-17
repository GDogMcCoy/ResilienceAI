"""
Edge ML Inference Optimization for ResilienceAI
===============================================
Optimized ML inference for resource-constrained edge devices.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import time


class ModelFormat(Enum):
    """Supported model formats for edge deployment"""
    TFLITE = "tflite"
    ONNX = "onnx"
    TORCHSCRIPT = "torchscript"
    TENSORRT = "tensorrt"
    OPENVINO = "openvino"
    COREML = "coreml"


@dataclass
class InferenceConfig:
    """Configuration for edge inference"""
    model_path: str
    model_format: ModelFormat
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    batch_size: int = 1
    num_threads: int = 4
    use_gpu: bool = False
    use_npu: bool = False
    quantization: Optional[str] = None
    cache_results: bool = True
    max_cache_size: int = 1000


class EdgeInferenceEngine:
    """High-performance inference engine for edge devices"""
    
    def __init__(self, config: InferenceConfig):
        self.config = config
        self.interpreter = None
        self.input_details = None
        self.output_details = None
        self.inference_cache = {}
        self.metrics = {
            "total_inferences": 0,
            "cache_hits": 0,
            "avg_latency_ms": 0,
            "total_latency_ms": 0
        }
        
    def load_model(self):
        """Load optimized model based on format"""
        if self.config.model_format == ModelFormat.TFLITE:
            self._load_tflite()
        elif self.config.model_format == ModelFormat.ONNX:
            self._load_onnx()
        elif self.config.model_format == ModelFormat.TORCHSCRIPT:
            self._load_torchscript()
            
    def _load_tflite(self):
        """Load TensorFlow Lite model"""
        import tensorflow as tf
        
        delegates = []
        if self.config.use_gpu:
            try:
                gpu_delegate = tf.lite.experimental.load_delegate('libgpu_delegate.so')
                delegates.append(gpu_delegate)
            except:
                pass
                
        self.interpreter = tf.lite.Interpreter(
            model_path=self.config.model_path,
            num_threads=self.config.num_threads,
            experimental_delegates=delegates
        )
        
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
    def _load_onnx(self):
        """Load ONNX model with optimizations"""
        import onnxruntime as ort
        
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = self.config.num_threads
        sess_options.inter_op_num_threads = self.config.num_threads
        sess_options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
        
        providers = ['CPUExecutionProvider']
        if self.config.use_gpu:
            providers.insert(0, 'CUDAExecutionProvider')
            
        self.interpreter = ort.InferenceSession(
            self.config.model_path,
            sess_options,
            providers=providers
        )
        
    def _load_torchscript(self):
        """Load TorchScript model"""
        import torch
        
        self.interpreter = torch.jit.load(self.config.model_path)
        self.interpreter.eval()
        
        if self.config.use_gpu and torch.cuda.is_available():
            self.interpreter = self.interpreter.cuda()
            
    def predict(self, input_data: np.ndarray) -> Dict[str, Any]:
        """Run inference with caching and metrics"""
        start_time = time.time()
        
        if self.config.cache_results:
            cache_key = self._get_cache_key(input_data)
            if cache_key in self.inference_cache:
                self.metrics["cache_hits"] += 1
                return {
                    "predictions": self.inference_cache[cache_key],
                    "latency_ms": 0,
                    "cached": True
                }
        
        processed_input = self._preprocess(input_data)
        
        if self.config.model_format == ModelFormat.TFLITE:
            results = self._infer_tflite(processed_input)
        elif self.config.model_format == ModelFormat.ONNX:
            results = self._infer_onnx(processed_input)
        elif self.config.model_format == ModelFormat.TORCHSCRIPT:
            results = self._infer_torchscript(processed_input)
        else:
            raise ValueError(f"Unsupported model format: {self.config.model_format}")
            
        predictions = self._postprocess(results)
        
        if self.config.cache_results:
            self._update_cache(cache_key, predictions)
            
        latency_ms = (time.time() - start_time) * 1000
        self.metrics["total_inferences"] += 1
        self.metrics["total_latency_ms"] += latency_ms
        self.metrics["avg_latency_ms"] = (
            self.metrics["total_latency_ms"] / self.metrics["total_inferences"]
        )
        
        return {
            "predictions": predictions,
            "latency_ms": latency_ms,
            "cached": False
        }
        
    def _get_cache_key(self, input_data: np.ndarray) -> str:
        """Generate cache key for input"""
        import hashlib
        return hashlib.md5(input_data.tobytes()).hexdigest()
        
    def _update_cache(self, key: str, predictions: Any):
        """Update inference cache with LRU eviction"""
        if len(self.inference_cache) >= self.config.max_cache_size:
            oldest_key = next(iter(self.inference_cache))
            del self.inference_cache[oldest_key]
        self.inference_cache[key] = predictions
        
    def _preprocess(self, input_data: np.ndarray) -> np.ndarray:
        """Preprocess input for model"""
        return input_data.astype(np.float32)
        
    def _postprocess(self, raw_output: np.ndarray) -> Dict[str, Any]:
        """Postprocess model output"""
        return {"raw_output": raw_output.tolist()}
        
    def _infer_tflite(self, input_data: np.ndarray) -> np.ndarray:
        """Run TFLite inference"""
        self.interpreter.set_tensor(self.input_details[0]['index'], input_data)
        self.interpreter.invoke()
        return self.interpreter.get_tensor(self.output_details[0]['index'])
        
    def _infer_onnx(self, input_data: np.ndarray) -> np.ndarray:
        """Run ONNX inference"""
        input_name = self.interpreter.get_inputs()[0].name
        outputs = self.interpreter.run(None, {input_name: input_data})
        return outputs[0]
        
    def _infer_torchscript(self, input_data: np.ndarray) -> np.ndarray:
        """Run TorchScript inference"""
        import torch
        tensor = torch.from_numpy(input_data)
        if self.config.use_gpu:
            tensor = tensor.cuda()
        with torch.no_grad():
            output = self.interpreter(tensor)
        return output.cpu().numpy()
        
    def get_metrics(self) -> Dict[str, Any]:
        """Get inference metrics"""
        return self.metrics.copy()


class ModelOptimizer:
    """Optimizes models for edge deployment"""
    
    @staticmethod
    def quantize_model(input_path: str, output_path: str, quantization: str = "int8"):
        """Quantize model for edge deployment"""
        import tensorflow as tf
        
        converter = tf.lite.TFLiteConverter.from_saved_model(input_path)
        
        if quantization == "int8":
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.representative_dataset = ModelOptimizer._representative_dataset
        elif quantization == "fp16":
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            converter.target_spec.supported_types = [tf.float16]
            
        tflite_model = converter.convert()
        
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
            
    @staticmethod
    def _representative_dataset():
        """Generate representative dataset for quantization"""
        for _ in range(100):
            data = np.random.rand(1, 224, 224, 3).astype(np.float32)
            yield [data]
            
    @staticmethod
    def benchmark_model(model_path: str, model_format: ModelFormat, iterations: int = 100) -> Dict:
        """Benchmark model performance"""
        config = InferenceConfig(
            model_path=model_path,
            model_format=model_format,
            input_shape=(1, 224, 224, 3),
            output_shape=(1, 1000)
        )
        
        engine = EdgeInferenceEngine(config)
        engine.load_model()
        
        dummy_input = np.random.rand(1, 224, 224, 3).astype(np.float32)
        for _ in range(10):
            engine.predict(dummy_input)
            
        latencies = []
        for _ in range(iterations):
            result = engine.predict(dummy_input)
            latencies.append(result["latency_ms"])
            
        return {
            "avg_latency_ms": np.mean(latencies),
            "min_latency_ms": np.min(latencies),
            "max_latency_ms": np.max(latencies),
            "p95_latency_ms": np.percentile(latencies, 95),
            "throughput_fps": 1000 / np.mean(latencies)
        }
