# Federated Learning for ResilienceAI

## Executive Summary

Federated Learning (FL) enables ResilienceAI to train machine learning models across decentralized data sources without centralizing sensitive data. This approach is critical for disaster response scenarios where data privacy, network constraints, and multi-organizational collaboration are paramount.

**Key Benefits for ResilienceAI:**
- **Privacy Preservation**: Raw disaster data never leaves local devices/organizations
- **Collaborative Intelligence**: Multiple agencies contribute to global models
- **Network Efficiency**: Only model updates transmitted, not raw data
- **Regulatory Compliance**: Meets data sovereignty requirements
- **Real-time Adaptation**: Continuous learning from distributed field sensors

---

## 1. Federated Learning Architecture

### 1.1 Core Architecture Patterns

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    RESILIENCEAI FEDERATED LEARNING ARCHITECTURE             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     Secure Channels      ┌─────────────────┐          │
│  │   CENTRAL       │◄────────────────────────►│   CLIENT 1      │          │
│  │   SERVER        │    (Encrypted Updates)   │  (Fire Dept)    │          │
│  │                 │◄────────────────────────►│   ┌─────────┐   │          │
│  │  ┌───────────┐  │    ┌──────────────┐      │   │ Local   │   │          │
│  │  │ Global    │  │◄───┤  Aggregation │      │   │ Model   │   │          │
│  │  │   Model   │  │    │   Engine     │      │   │  v2.1   │   │          │
│  │  │   v3.0    │  │    └──────────────┘      │   └─────────┘   │          │
│  │  └───────────┘  │                          │   ┌─────────┐   │          │
│  │  ┌───────────┐  │◄────────────────────────►│   │ Private │   │          │
│  │  │  Secure   │  │                          │   │  Data   │   │          │
│  │  │ Aggregator│  │◄────────────────────────►│   └─────────┘   │          │
│  │  └───────────┘  │                          └─────────────────┘          │
│  │  ┌───────────┐  │                                                       │
│  │  │ Incentive │  │◄────────────────────────►┌─────────────────┐          │
│  │  │  Manager  │  │                          │   CLIENT 2      │          │
│  │  └───────────┘  │                          │  (Red Cross)    │          │
│  │  ┌───────────┐  │◄────────────────────────►│   ┌─────────┐   │          │
│  │  │  Model    │  │                          │   │ Local   │   │          │
│  │  │ Registry  │  │◄────────────────────────►│   │ Model   │   │          │
│  │  └───────────┘  │                          │   │  v2.8   │   │          │
│  └─────────────────┘                          │   └─────────┘   │          │
│                                               │   ┌─────────┐   │          │
│                                               │   │ Private │   │          │
│                                               │   │  Data   │   │          │
│                                               │   └─────────┘   │          │
│                                               └─────────────────┘          │
│                                                                             │
│                                               ┌─────────────────┐          │
│                                               │   CLIENT N      │          │
│                                               │ (Field Sensors) │          │
│                                               │   ┌─────────┐   │          │
│                                               │   │ Local   │   │          │
│                                               │   │ Model   │   │          │
│                                               │   │  v2.5   │   │          │
│                                               │   └─────────┘   │          │
│                                               │   ┌─────────┐   │          │
│                                               │   │ Private │   │          │
│                                               │   │  Data   │   │          │
│                                               │   └─────────┘   │          │
│                                               └─────────────────┘          │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 1.2 System Components

| Component | Description | Technology Options |
|-----------|-------------|-------------------|
| **Central Server** | Orchestrates training, aggregates updates | TensorFlow Federated, PySyft, Flower |
| **Clients** | Local training on private data | Edge devices, mobile, on-premise servers |
| **Secure Aggregator** | Cryptographically secure model aggregation | Secure Multi-Party Computation (SMPC) |
| **Differential Privacy Engine** | Adds statistical noise for privacy | Opacus, TensorFlow Privacy |
| **Communication Layer** | Encrypted transmission of updates | TLS 1.3, gRPC, WebSockets |
| **Incentive Manager** | Tracks contributions and rewards | Blockchain, reputation systems |

### 1.3 Architecture Types for ResilienceAI

#### A. Cross-Device Federated Learning
**Use Case**: Field sensors, mobile apps, drones collecting disaster data
```python
class CrossDeviceFL:
    """
    For thousands of edge devices with intermittent connectivity
    """
    def __init__(self):
        self.client_selection_rate = 0.1  # Sample 10% of devices
        self.local_epochs = 5
        self.batch_size = 32
        
    def training_round(self):
        # Select subset of available clients
        selected_clients = self.select_clients(fraction=0.1)
        
        # Broadcast global model
        global_model = self.server.get_model()
        
        # Parallel local training
        updates = []
        for client in selected_clients:
            update = client.train(global_model, epochs=5)
            updates.append(update)
        
        # Secure aggregation
        aggregated = self.secure_aggregate(updates)
        self.server.update_model(aggregated)
```

#### B. Cross-Silo Federated Learning
**Use Case**: Collaboration between fire departments, hospitals, emergency services
```python
class CrossSiloFL:
    """
    For organizations with reliable infrastructure
    """
    def __init__(self):
        self.organizations = ['fire_dept', 'hospital', 'red_cross', 'police']
        self.sync_frequency = 'hourly'
        self.full_participation = True
        
    def collaborative_training(self):
        # All organizations participate
        for org in self.organizations:
            local_update = org.train_local_model()
            encrypted_update = self.encrypt(local_update)
            self.submit_to_aggregator(encrypted_update)
        
        # Differential privacy aggregation
        global_update = self.dp_aggregate(
            noise_multiplier=1.1,
            max_grad_norm=1.0
        )
        
        return global_update
```

#### C. Hierarchical Federated Learning
**Use Case**: Multi-level disaster response (local → regional → national)
```python
class HierarchicalFL:
    """
    Tiered aggregation for large-scale deployment
    """
    def __init__(self):
        self.tiers = {
            'edge': [],      # Field devices
            'local': [],     # City/County level
            'regional': [],  # State/Province level
            'national': []   # Federal level
        }
    
    def hierarchical_aggregation(self):
        # Edge to Local
        for local_hub in self.tiers['local']:
            edge_updates = self.collect_from_edges(local_hub)
            local_model = self.aggregate(edge_updates)
            local_hub.set_model(local_model)
        
        # Local to Regional
        for regional_hub in self.tiers['regional']:
            local_updates = self.collect_from_locals(regional_hub)
            regional_model = self.aggregate(local_updates)
            regional_hub.set_model(regional_model)
        
        # Regional to National
        national_update = self.aggregate([
            hub.get_model() for hub in self.tiers['regional']
        ])
        
        return national_update
```

---

## 2. Privacy Preservation Mechanisms

### 2.1 Differential Privacy (DP)

Differential Privacy provides mathematical guarantees that individual data points cannot be identified from model updates.

```python
import torch
import torch.nn as nn
from opacus import PrivacyEngine
from opacus.validators import ModuleValidator

class DifferentiallyPrivateTrainer:
    """
    Differential Privacy training for ResilienceAI
    """
    def __init__(
        self,
        model: nn.Module,
        target_epsilon: float = 3.0,      # Privacy budget
        target_delta: float = 1e-5,        # Failure probability
        max_grad_norm: float = 1.0,        # Gradient clipping
        noise_multiplier: float = 1.1      # Noise level
    ):
        self.model = ModuleValidator.fix(model)
        self.target_epsilon = target_epsilon
        self.target_delta = target_delta
        self.max_grad_norm = max_grad_norm
        self.noise_multiplier = noise_multiplier
        
    def setup_private_training(
        self,
        optimizer: torch.optim.Optimizer,
        data_loader: torch.utils.data.DataLoader
    ):
        """
        Configure differentially private training
        """
        self.privacy_engine = PrivacyEngine()
        
        self.model, self.optimizer, self.data_loader = \
            self.privacy_engine.make_private_with_epsilon(
                module=self.model,
                optimizer=optimizer,
                data_loader=data_loader,
                target_epsilon=self.target_epsilon,
                target_delta=self.target_delta,
                epochs=10,
                max_grad_norm=self.max_grad_norm
            )
    
    def train_epoch(self) -> dict:
        """
        Train for one epoch with privacy guarantees
        """
        self.model.train()
        total_loss = 0
        
        for batch_idx, (data, target) in enumerate(self.data_loader):
            self.optimizer.zero_grad()
            output = self.model(data)
            loss = nn.functional.cross_entropy(output, target)
            loss.backward()
            self.optimizer.step()
            total_loss += loss.item()
        
        # Get current privacy spend
        epsilon = self.privacy_engine.get_epsilon(self.target_delta)
        
        return {
            'loss': total_loss / len(self.data_loader),
            'epsilon': epsilon,
            'delta': self.target_delta
        }
```

### 2.2 Privacy Budget Management

```python
class PrivacyBudgetManager:
    """
    Manages privacy budget across federated learning rounds
    """
    def __init__(
        self,
        total_epsilon: float = 10.0,    # Total privacy budget
        total_delta: float = 1e-5,
        num_rounds: int = 100
    ):
        self.total_epsilon = total_epsilon
        self.total_delta = total_delta
        self.num_rounds = num_rounds
        self.epsilon_per_round = total_epsilon / num_rounds
        self.rounds_completed = 0
        
    def get_round_budget(self) -> tuple:
        """
        Calculate privacy budget for current round
        """
        remaining_epsilon = self.total_epsilon - (
            self.rounds_completed * self.epsilon_per_round
        )
        
        if remaining_epsilon <= 0:
            raise PrivacyBudgetExhausted(
                "Privacy budget exhausted. Cannot continue training."
            )
        
        return self.epsilon_per_round, self.total_delta
    
    def spend_budget(self, actual_epsilon: float):
        """
        Record actual privacy spend
        """
        self.rounds_completed += 1
        self.actual_epsilon_spent = actual_epsilon
        
    def get_accounting_report(self) -> dict:
        """
        Generate privacy accounting report
        """
        return {
            'total_epsilon_budget': self.total_epsilon,
            'epsilon_spent': self.rounds_completed * self.epsilon_per_round,
            'epsilon_remaining': self.total_epsilon - 
                (self.rounds_completed * self.epsilon_per_round),
            'rounds_completed': self.rounds_completed,
            'rounds_remaining': self.num_rounds - self.rounds_completed,
            'budget_utilization': (
                self.rounds_completed / self.num_rounds
            ) * 100
        }
```

### 2.3 Local Differential Privacy

```python
class LocalDifferentialPrivacy:
    """
    Add noise locally before sending updates
    """
    def __init__(self, epsilon: float = 1.0):
        self.epsilon = epsilon
        self.sensitivity = 1.0  # For gradient clipping at 1.0
        
    def add_laplace_noise(self, gradient: torch.Tensor) -> torch.Tensor:
        """
        Add Laplace noise for LDP
        """
        scale = self.sensitivity / self.epsilon
        noise = torch.distributions.Laplace(0, scale).sample(gradient.shape)
        return gradient + noise
    
    def add_gaussian_noise(
        self,
        gradient: torch.Tensor,
        delta: float = 1e-5
    ) -> torch.Tensor:
        """
        Add Gaussian noise for (ε,δ)-DP
        """
        sigma = self.sensitivity * torch.sqrt(
            2 * torch.log(torch.tensor(1.25 / delta))
        ) / self.epsilon
        noise = torch.randn_like(gradient) * sigma
        return gradient + noise
    
    def privatize_update(
        self,
        model_update: dict,
        mechanism: str = 'gaussian'
    ) -> dict:
        """
        Apply LDP to entire model update
        """
        privatized = {}
        for name, param in model_update.items():
            if mechanism == 'laplace':
                privatized[name] = self.add_laplace_noise(param)
            elif mechanism == 'gaussian':
                privatized[name] = self.add_gaussian_noise(param)
            else:
                raise ValueError(f"Unknown mechanism: {mechanism}")
        return privatized
```

---

## 3. Secure Aggregation

### 3.1 Secure Multi-Party Computation (SMPC)

```python
import torch
import torch.nn as nn
from typing import List, Dict
import secrets

class SecureAggregator:
    """
    Secure aggregation using secret sharing
    """
    def __init__(self, num_clients: int, threshold: int):
        self.num_clients = num_clients
        self.threshold = threshold  # Minimum clients needed for reconstruction
        self.prime = 2**61 - 1  # Large prime for modular arithmetic
        
    def generate_shares(self, value: float, num_shares: int) -> List[int]:
        """
        Generate Shamir secret shares
        """
        # Generate random coefficients for polynomial
        coefficients = [secrets.randbelow(self.prime) 
                       for _ in range(self.threshold - 1)]
        
        shares = []
        for x in range(1, num_shares + 1):
            # Evaluate polynomial at point x
            y = value
            for power, coeff in enumerate(coefficients, 1):
                y += coeff * (x ** power)
            shares.append((x, y % self.prime))
        
        return shares
    
    def lagrange_interpolation(self, shares: List[tuple], x: int = 0) -> float:
        """
        Reconstruct secret using Lagrange interpolation
        """
        result = 0
        for i, (xi, yi) in enumerate(shares):
            numerator = 1
            denominator = 1
            for j, (xj, _) in enumerate(shares):
                if i != j:
                    numerator *= (x - xj)
                    denominator *= (xi - xj)
            lagrange_coeff = numerator / denominator
            result += yi * lagrange_coeff
        
        return result % self.prime
    
    def secure_aggregate_updates(
        self,
        client_updates: List[Dict[str, torch.Tensor]]
    ) -> Dict[str, torch.Tensor]:
        """
        Securely aggregate model updates without revealing individual updates
        """
        aggregated = {}
        
        # For each parameter
        for param_name in client_updates[0].keys():
            # Flatten all client updates for this parameter
            flattened_updates = []
            shapes = []
            
            for update in client_updates:
                flat = update[param_name].flatten()
                shapes.append(update[param_name].shape)
                flattened_updates.append(flat)
            
            # Stack updates
            stacked = torch.stack(flattened_updates)
            
            # Generate pairwise masks for privacy
            num_clients = len(client_updates)
            masks = torch.zeros_like(stacked)
            
            for i in range(num_clients):
                for j in range(i + 1, num_clients):
                    # Generate shared random mask
                    seed = secrets.randbits(128)
                    torch.manual_seed(seed)
                    mask = torch.randn_like(stacked[i])
                    
                    masks[i] += mask
                    masks[j] -= mask  # Masks cancel out in aggregation
            
            # Apply masks and aggregate
            masked_updates = stacked + masks
            aggregated_flat = masked_updates.sum(dim=0)
            
            # Reshape to original shape
            aggregated[param_name] = aggregated_flat.reshape(shapes[0])
        
        return aggregated
```

### 3.2 Homomorphic Encryption for Aggregation

```python
class HomomorphicEncryptionAggregator:
    """
    Use homomorphic encryption for secure aggregation
    """
    def __init__(self, poly_modulus_degree: int = 4096):
        try:
            import tenseal as ts
            self.ts = ts
            
            # Create TenSEAL context
            self.context = ts.context(
                ts.SCHEME_TYPE.CKKS,
                poly_modulus_degree=poly_modulus_degree,
                coeff_mod_bit_sizes=[60, 40, 40, 60]
            )
            self.context.global_scale = 2**40
            self.context.generate_galois_keys()
            
        except ImportError:
            raise ImportError("Install tenseal: pip install tenseal")
    
    def encrypt_update(
        self,
        model_update: Dict[str, torch.Tensor]
    ) -> Dict[str, 'ts.CKKSVector']:
        """
        Encrypt model update using CKKS
        """
        encrypted = {}
        for name, param in model_update.items():
            # Flatten and convert to list
            flat = param.flatten().tolist()
            # Encrypt
            encrypted[name] = self.ts.ckks_vector(self.context, flat)
        return encrypted
    
    def aggregate_encrypted(
        self,
        encrypted_updates: List[Dict[str, 'ts.CKKSVector']]
    ) -> Dict[str, 'ts.CKKSVector']:
        """
        Aggregate encrypted updates (homomorphically)
        """
        aggregated = {}
        
        for param_name in encrypted_updates[0].keys():
            # Sum encrypted vectors
            result = encrypted_updates[0][param_name]
            for update in encrypted_updates[1:]:
                result = result + update[param_name]
            
            # Average
            aggregated[param_name] = result * (1.0 / len(encrypted_updates))
        
        return aggregated
    
    def decrypt_aggregate(
        self,
        encrypted_aggregate: Dict[str, 'ts.CKKSVector'],
        original_shapes: Dict[str, tuple]
    ) -> Dict[str, torch.Tensor]:
        """
        Decrypt aggregated result
        """
        decrypted = {}
        for name, enc_vector in encrypted_aggregate.items():
            # Decrypt to list
            dec_list = enc_vector.decrypt()
            # Convert to tensor and reshape
            dec_tensor = torch.tensor(dec_list)
            decrypted[name] = dec_tensor.reshape(original_shapes[name])
        
        return decrypted
```

---

## 4. Model Aggregation Strategies

### 4.1 Federated Averaging (FedAvg)

```python
import torch
import torch.nn as nn
from typing import List, Dict, Tuple
from collections import OrderedDict

class FederatedAveraging:
    """
    FedAvg: Federated Averaging algorithm (McMahan et al., 2017)
    """
    def __init__(self):
        self.round = 0
        
    def aggregate(
        self,
        client_updates: List[Tuple[Dict[str, torch.Tensor], int]],
        global_model: nn.Module
    ) -> nn.Module:
        """
        Aggregate client updates using weighted averaging
        
        Args:
            client_updates: List of (model_state_dict, num_samples) tuples
            global_model: Current global model
            
        Returns:
            Updated global model
        """
        total_samples = sum(num_samples for _, num_samples in client_updates)
        
        # Initialize aggregated state
        aggregated_state = OrderedDict()
        
        # Weighted average of client updates
        for client_state, num_samples in client_updates:
            weight = num_samples / total_samples
            
            for param_name, param_value in client_state.items():
                if param_name not in aggregated_state:
                    aggregated_state[param_name] = torch.zeros_like(param_value)
                aggregated_state[param_name] += weight * param_value
        
        # Update global model
        global_model.load_state_dict(aggregated_state)
        self.round += 1
        
        return global_model
    
    def aggregate_with_momentum(
        self,
        client_updates: List[Tuple[Dict[str, torch.Tensor], int]],
        global_model: nn.Module,
        momentum: float = 0.9,
        velocity: Dict[str, torch.Tensor] = None
    ) -> Tuple[nn.Module, Dict[str, torch.Tensor]]:
        """
        FedAvg with momentum for faster convergence
        """
        if velocity is None:
            velocity = {
                name: torch.zeros_like(param)
                for name, param in global_model.state_dict().items()
            }
        
        total_samples = sum(num_samples for _, num_samples in client_updates)
        
        # Compute weighted average
        delta = OrderedDict()
        for client_state, num_samples in client_updates:
            weight = num_samples / total_samples
            for param_name, param_value in client_state.items():
                if param_name not in delta:
                    delta[param_name] = torch.zeros_like(param_value)
                delta[param_name] += weight * param_value
        
        # Apply momentum
        for param_name in delta.keys():
            velocity[param_name] = (
                momentum * velocity[param_name] + 
                (1 - momentum) * delta[param_name]
            )
        
        # Update global model
        new_state = OrderedDict()
        current_state = global_model.state_dict()
        for param_name in current_state.keys():
            new_state[param_name] = current_state[param_name] + velocity[param_name]
        
        global_model.load_state_dict(new_state)
        
        return global_model, velocity
```

### 4.2 Federated Learning with Adaptive Optimization

```python
class FedAdam:
    """
    Federated Learning with Adam optimizer at server
    """
    def __init__(
        self,
        lr: float = 0.001,
        beta1: float = 0.9,
        beta2: float = 0.999,
        epsilon: float = 1e-8,
        tau: float = 0.001  # Server learning rate
    ):
        self.lr = lr
        self.beta1 = beta1
        self.beta2 = beta2
        self.epsilon = epsilon
        self.tau = tau
        self.m = None  # First moment
        self.v = None  # Second moment
        self.t = 0     # Time step
        
    def aggregate(
        self,
        client_updates: List[Tuple[Dict[str, torch.Tensor], int]],
        global_model: nn.Module
    ) -> nn.Module:
        """
        Aggregate using Adam optimizer
        """
        total_samples = sum(num_samples for _, num_samples in client_updates)
        
        # Compute weighted average of client updates
        delta = OrderedDict()
        for client_state, num_samples in client_updates:
            weight = num_samples / total_samples
            for param_name, param_value in client_state.items():
                if param_name not in delta:
                    delta[param_name] = torch.zeros_like(param_value)
                delta[param_name] += weight * param_value
        
        # Initialize moments if needed
        if self.m is None:
            self.m = {
                name: torch.zeros_like(tensor)
                for name, tensor in delta.items()
            }
            self.v = {
                name: torch.zeros_like(tensor)
                for name, tensor in delta.items()
            }
        
        self.t += 1
        
        # Adam update
        new_state = OrderedDict()
        current_state = global_model.state_dict()
        
        for param_name in delta.keys():
            # Update biased first moment
            self.m[param_name] = (
                self.beta1 * self.m[param_name] + 
                (1 - self.beta1) * delta[param_name]
            )
            
            # Update biased second moment
            self.v[param_name] = (
                self.beta2 * self.v[param_name] + 
                (1 - self.beta2) * (delta[param_name] ** 2)
            )
            
            # Bias correction
            m_hat = self.m[param_name] / (1 - self.beta1 ** self.t)
            v_hat = self.v[param_name] / (1 - self.beta2 ** self.t)
            
            # Update parameter
            update = self.tau * m_hat / (torch.sqrt(v_hat) + self.epsilon)
            new_state[param_name] = current_state[param_name] + update
        
        global_model.load_state_dict(new_state)
        
        return global_model
```

### 4.3 Personalized Federated Learning

```python
class PersonalizedFL:
    """
    Personalized FL for heterogeneous clients
    """
    def __init__(
        self,
        global_model: nn.Module,
        num_clients: int,
        personalization_layers: List[str] = ['fc1', 'fc2']
    ):
        self.global_model = global_model
        self.num_clients = num_clients
        self.personalization_layers = personalization_layers
        
        # Each client has personalized layers
        self.personalized_models = {
            i: self._create_personalized_model()
            for i in range(num_clients)
        }
    
    def _create_personalized_model(self) -> nn.Module:
        """Create model with personalized layers"""
        # Clone global model
        personalized = type(self.global_model)(
            *self.global_model.__init_args__
        ) if hasattr(self.global_model, '__init_args__') else \
            self._clone_model(self.global_model)
        return personalized
    
    def _clone_model(self, model: nn.Module) -> nn.Module:
        """Clone a PyTorch model"""
        import copy
        return copy.deepcopy(model)
    
    def aggregate_partial(
        self,
        client_updates: List[Tuple[int, Dict[str, torch.Tensor], int]]
    ):
        """
        Aggregate only shared layers
        
        Args:
            client_updates: List of (client_id, state_dict, num_samples)
        """
        # Separate shared and personalized parameters
        shared_updates = []
        
        for client_id, state_dict, num_samples in client_updates:
            shared_state = {
                name: param for name, param in state_dict.items()
                if not any(pl in name for pl in self.personalization_layers)
            }
            shared_updates.append((shared_state, num_samples))
        
        # Aggregate shared parameters
        total_samples = sum(num_samples for _, num_samples in shared_updates)
        aggregated_shared = OrderedDict()
        
        for state_dict, num_samples in shared_updates:
            weight = num_samples / total_samples
            for name, param in state_dict.items():
                if name not in aggregated_shared:
                    aggregated_shared[name] = torch.zeros_like(param)
                aggregated_shared[name] += weight * param
        
        # Update global model
        current_state = self.global_model.state_dict()
        new_state = OrderedDict(current_state)
        new_state.update(aggregated_shared)
        self.global_model.load_state_dict(new_state)
        
        # Update personalized models
        for client_id, state_dict, _ in client_updates:
            self.personalized_models[client_id].load_state_dict(state_dict)
    
    def get_client_model(self, client_id: int) -> nn.Module:
        """Get model for specific client (global + personalized)"""
        return self.personalized_models[client_id]
```

---

## 5. Distributed Training Implementation

### 5.1 Complete Federated Learning System

```python
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from typing import List, Dict, Callable, Optional
import copy
import json
from dataclasses import dataclass
from enum import Enum
import asyncio
from concurrent.futures import ThreadPoolExecutor

class ClientStatus(Enum):
    IDLE = "idle"
    TRAINING = "training"
    UPLOADING = "uploading"
    ERROR = "error"

@dataclass
class FLConfig:
    """Federated Learning Configuration"""
    num_rounds: int = 100
    clients_per_round: int = 10
    local_epochs: int = 5
    local_batch_size: int = 32
    learning_rate: float = 0.01
    aggregation_strategy: str = "fedavg"
    dp_enabled: bool = True
    dp_epsilon: float = 3.0
    dp_delta: float = 1e-5
    secure_aggregation: bool = True
    evaluation_interval: int = 5
    checkpoint_interval: int = 10

class FederatedClient:
    """
    Federated Learning Client
    """
    def __init__(
        self,
        client_id: str,
        model: nn.Module,
        train_data: Dataset,
        config: FLConfig,
        device: str = 'cpu'
    ):
        self.client_id = client_id
        self.model = model.to(device)
        self.train_data = train_data
        self.config = config
        self.device = device
        self.status = ClientStatus.IDLE
        self.data_size = len(train_data)
        
        self.train_loader = DataLoader(
            train_data,
            batch_size=config.local_batch_size,
            shuffle=True
        )
        
    def train_round(
        self,
        global_state: Dict[str, torch.Tensor]
    ) -> Dict[str, torch.Tensor]:
        """
        Perform local training round
        """
        self.status = ClientStatus.TRAINING
        
        # Load global model
        self.model.load_state_dict(global_state)
        self.model.train()
        
        # Setup optimizer
        optimizer = optim.SGD(
            self.model.parameters(),
            lr=self.config.learning_rate
        )
        
        # Setup DP if enabled
        if self.config.dp_enabled:
            try:
                from opacus import PrivacyEngine
                privacy_engine = PrivacyEngine()
                self.model, optimizer, self.train_loader = \
                    privacy_engine.make_private_with_epsilon(
                        module=self.model,
                        optimizer=optimizer,
                        data_loader=self.train_loader,
                        target_epsilon=self.config.dp_epsilon,
                        target_delta=self.config.dp_delta,
                        epochs=self.config.local_epochs,
                        max_grad_norm=1.0
                    )
            except ImportError:
                print("Warning: Opacus not installed, training without DP")
        
        # Local training
        for epoch in range(self.config.local_epochs):
            for batch_idx, (data, target) in enumerate(self.train_loader):
                data, target = data.to(self.device), target.to(self.device)
                
                optimizer.zero_grad()
                output = self.model(data)
                loss = nn.functional.cross_entropy(output, target)
                loss.backward()
                optimizer.step()
        
        self.status = ClientStatus.IDLE
        
        # Return updated model state
        return copy.deepcopy(self.model.state_dict())
    
    def evaluate(
        self,
        test_data: Dataset
    ) -> Dict[str, float]:
        """
        Evaluate local model
        """
        self.model.eval()
        test_loader = DataLoader(test_data, batch_size=64)
        
        correct = 0
        total = 0
        test_loss = 0
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.model(data)
                test_loss += nn.functional.cross_entropy(
                    output, target, reduction='sum'
                ).item()
                pred = output.argmax(dim=1)
                correct += pred.eq(target).sum().item()
                total += target.size(0)
        
        return {
            'loss': test_loss / total,
            'accuracy': 100.0 * correct / total
        }

class FederatedServer:
    """
    Federated Learning Server
    """
    def __init__(
        self,
        model: nn.Module,
        config: FLConfig,
        device: str = 'cpu'
    ):
        self.global_model = model.to(device)
        self.config = config
        self.device = device
        self.clients: Dict[str, FederatedClient] = {}
        self.round = 0
        self.history = {
            'train_loss': [],
            'test_accuracy': [],
            'round_time': []
        }
        
        # Initialize aggregator
        if config.aggregation_strategy == "fedavg":
            self.aggregator = FederatedAveraging()
        elif config.aggregation_strategy == "fedadam":
            self.aggregator = FedAdam()
        else:
            raise ValueError(f"Unknown strategy: {config.aggregation_strategy}")
        
        # Secure aggregation
        if config.secure_aggregation:
            self.secure_aggregator = SecureAggregator(
                num_clients=config.clients_per_round,
                threshold=config.clients_per_round // 2
            )
    
    def register_client(self, client: FederatedClient):
        """Register a client with the server"""
        self.clients[client.client_id] = client
    
    def select_clients(self, fraction: float = 0.1) -> List[str]:
        """
        Select subset of clients for training round
        """
        import random
        num_clients = max(1, int(len(self.clients) * fraction))
        return random.sample(list(self.clients.keys()), num_clients)
    
    def training_round(self) -> Dict[str, float]:
        """
        Execute one federated learning round
        """
        import time
        start_time = time.time()
        
        # Select clients
        selected_clients = self.select_clients(
            self.config.clients_per_round / len(self.clients)
        )
        
        # Get global model state
        global_state = copy.deepcopy(self.global_model.state_dict())
        
        # Collect client updates
        client_updates = []
        
        for client_id in selected_clients:
            client = self.clients[client_id]
            
            # Client trains locally
            client_state = client.train_round(global_state)
            
            # Add to updates
            client_updates.append((client_state, client.data_size))
        
        # Aggregate updates
        self.global_model = self.aggregator.aggregate(
            client_updates,
            self.global_model
        )
        
        self.round += 1
        round_time = time.time() - start_time
        
        return {
            'round': self.round,
            'clients_participated': len(selected_clients),
            'round_time': round_time
        }
    
    def evaluate_global_model(
        self,
        test_data: Dataset
    ) -> Dict[str, float]:
        """
        Evaluate global model on test data
        """
        self.global_model.eval()
        test_loader = DataLoader(test_data, batch_size=64)
        
        correct = 0
        total = 0
        test_loss = 0
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(self.device), target.to(self.device)
                output = self.global_model(data)
                test_loss += nn.functional.cross_entropy(
                    output, target, reduction='sum'
                ).item()
                pred = output.argmax(dim=1)
                correct += pred.eq(target).sum().item()
                total += target.size(0)
        
        metrics = {
            'loss': test_loss / total,
            'accuracy': 100.0 * correct / total
        }
        
        self.history['test_accuracy'].append(metrics['accuracy'])
        
        return metrics
    
    def train(
        self,
        test_data: Optional[Dataset] = None
    ) -> Dict:
        """
        Run complete federated training
        """
        print(f"Starting Federated Learning Training")
        print(f"Total rounds: {self.config.num_rounds}")
        print(f"Clients: {len(self.clients)}")
        print(f"Clients per round: {self.config.clients_per_round}")
        
        for round_num in range(self.config.num_rounds):
            # Training round
            round_info = self.training_round()
            
            # Evaluation
            if test_data and round_num % self.config.evaluation_interval == 0:
                metrics = self.evaluate_global_model(test_data)
                print(f"Round {round_num}: Accuracy = {metrics['accuracy']:.2f}%")
            
            # Checkpoint
            if round_num % self.config.checkpoint_interval == 0:
                self.save_checkpoint(f"checkpoint_round_{round_num}.pt")
        
        return self.history
    
    def save_checkpoint(self, path: str):
        """Save model checkpoint"""
        torch.save({
            'round': self.round,
            'model_state_dict': self.global_model.state_dict(),
            'history': self.history,
            'config': self.config
        }, path)
    
    def load_checkpoint(self, path: str):
        """Load model checkpoint"""
        checkpoint = torch.load(path)
        self.round = checkpoint['round']
        self.global_model.load_state_dict(checkpoint['model_state_dict'])
        self.history = checkpoint['history']
```

---

## 6. Communication Efficiency

### 6.1 Model Compression Techniques

```python
class ModelCompression:
    """
    Compress model updates for efficient communication
    """
    
    @staticmethod
    def quantize_updates(
        updates: Dict[str, torch.Tensor],
        num_bits: int = 8
    ) -> Dict[str, torch.Tensor]:
        """
        Quantize model updates to reduce communication cost
        """
        quantized = {}
        
        for name, param in updates.items():
            # Find min and max
            min_val = param.min()
            max_val = param.max()
            
            # Quantize to num_bits
            levels = 2 ** num_bits - 1
            scaled = (param - min_val) / (max_val - min_val) * levels
            quantized_param = torch.round(scaled).to(torch.uint8)
            
            # Store with metadata for dequantization
            quantized[name] = {
                'values': quantized_param,
                'min': min_val,
                'max': max_val,
                'shape': param.shape
            }
        
        return quantized
    
    @staticmethod
    def dequantize_updates(
        quantized: Dict,
        num_bits: int = 8
    ) -> Dict[str, torch.Tensor]:
        """
        Dequantize model updates
        """
        dequantized = {}
        levels = 2 ** num_bits - 1
        
        for name, data in quantized.items():
            values = data['values'].float()
            min_val = data['min']
            max_val = data['max']
            
            # Dequantize
            dequantized[name] = (values / levels) * (max_val - min_val) + min_val
            dequantized[name] = dequantized[name].reshape(data['shape'])
        
        return dequantized
    
    @staticmethod
    def sparsify_updates(
        updates: Dict[str, torch.Tensor],
        sparsity: float = 0.9
    ) -> Dict[str, torch.Tensor]:
        """
        Sparsify updates by keeping only top-k values
        """
        sparsified = {}
        
        for name, param in updates.items():
            # Flatten
            flat = param.flatten()
            
            # Find threshold for top-k
            k = int((1 - sparsity) * flat.numel())
            threshold = torch.topk(torch.abs(flat), k).values.min()
            
            # Create sparse mask
            mask = torch.abs(param) >= threshold
            
            # Apply mask
            sparsified[name] = param * mask
        
        return sparsified
    
    @staticmethod
    def encode_sparse_updates(
        sparse_updates: Dict[str, torch.Tensor]
    ) -> Dict:
        """
        Encode sparse updates efficiently
        """
        encoded = {}
        
        for name, param in sparse_updates.items():
            # Find non-zero indices and values
            non_zero = param.nonzero()
            values = param[non_zero[:, 0], non_zero[:, 1]]
            
            encoded[name] = {
                'indices': non_zero,
                'values': values,
                'shape': param.shape
            }
        
        return encoded
```

### 6.2 Adaptive Communication

```python
class AdaptiveCommunication:
    """
    Adapt communication frequency based on training progress
    """
    def __init__(
        self,
        initial_interval: int = 1,
        min_interval: int = 1,
        max_interval: int = 10,
        accuracy_threshold: float = 0.01
    ):
        self.interval = initial_interval
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.accuracy_threshold = accuracy_threshold
        self.prev_accuracy = 0
        self.rounds_since_update = 0
    
    def should_communicate(
        self,
        current_accuracy: float
    ) -> bool:
        """
        Determine if communication should happen this round
        """
        self.rounds_since_update += 1
        
        # Check if enough rounds have passed
        if self.rounds_since_update < self.interval:
            return False
        
        # Check if model has improved enough
        accuracy_change = abs(current_accuracy - self.prev_accuracy)
        
        if accuracy_change < self.accuracy_threshold:
            # Model converging, increase interval
            self.interval = min(self.interval + 1, self.max_interval)
        else:
            # Model still improving, decrease interval
            self.interval = max(self.interval - 1, self.min_interval)
        
        self.prev_accuracy = current_accuracy
        self.rounds_since_update = 0
        
        return True
    
    def get_compression_ratio(self, round_num: int) -> float:
        """
        Get compression ratio based on training progress
        """
        # Start with high compression, reduce as training progresses
        if round_num < 10:
            return 0.1  # 90% compression
        elif round_num < 50:
            return 0.3  # 70% compression
        else:
            return 0.5  # 50% compression
```

---

## 7. Incentive Mechanisms

### 7.1 Contribution-Based Rewards

```python
from dataclasses import dataclass
from typing import Dict, List
import numpy as np

@dataclass
class ContributionMetrics:
    """Metrics for calculating client contribution"""
    data_quality: float  # 0-1 score
    data_quantity: int   # Number of samples
    computation_time: float  # Time spent training
    model_improvement: float  # Improvement to global model
    participation_rate: float  # % of rounds participated

class IncentiveMechanism:
    """
    Reward clients based on their contributions
    """
    def __init__(
        self,
        total_reward_pool: float = 1000.0,
        quality_weight: float = 0.3,
        quantity_weight: float = 0.2,
        improvement_weight: float = 0.4,
        participation_weight: float = 0.1
    ):
        self.total_reward_pool = total_reward_pool
        self.weights = {
            'quality': quality_weight,
            'quantity': quantity_weight,
            'improvement': improvement_weight,
            'participation': participation_weight
        }
        self.client_contributions: Dict[str, List[ContributionMetrics]] = {}
        self.reputation_scores: Dict[str, float] = {}
    
    def calculate_contribution_score(
        self,
        metrics: ContributionMetrics
    ) -> float:
        """
        Calculate contribution score for a client
        """
        # Normalize metrics
        normalized_quality = metrics.data_quality
        normalized_quantity = min(metrics.data_quantity / 10000, 1.0)
        normalized_improvement = min(max(metrics.model_improvement, 0), 1.0)
        normalized_participation = metrics.participation_rate
        
        # Weighted sum
        score = (
            self.weights['quality'] * normalized_quality +
            self.weights['quantity'] * normalized_quantity +
            self.weights['improvement'] * normalized_improvement +
            self.weights['participation'] * normalized_participation
        )
        
        return score
    
    def distribute_rewards(
        self,
        round_num: int
    ) -> Dict[str, float]:
        """
        Distribute rewards to clients based on contributions
        """
        rewards = {}
        total_score = 0
        
        # Calculate scores for all clients
        scores = {}
        for client_id, metrics_list in self.client_contributions.items():
            if metrics_list:
                avg_metrics = ContributionMetrics(
                    data_quality=np.mean([m.data_quality for m in metrics_list]),
                    data_quantity=np.mean([m.data_quantity for m in metrics_list]),
                    computation_time=np.mean([m.computation_time for m in metrics_list]),
                    model_improvement=np.mean([m.model_improvement for m in metrics_list]),
                    participation_rate=np.mean([m.participation_rate for m in metrics_list])
                )
                score = self.calculate_contribution_score(avg_metrics)
                scores[client_id] = score
                total_score += score
        
        # Distribute rewards proportionally
        if total_score > 0:
            for client_id, score in scores.items():
                rewards[client_id] = (
                    score / total_score * self.total_reward_pool
                )
        
        return rewards
    
    def update_reputation(
        self,
        client_id: str,
        round_contribution: ContributionMetrics
    ):
        """
        Update client's reputation based on contribution
        """
        if client_id not in self.client_contributions:
            self.client_contributions[client_id] = []
        
        self.client_contributions[client_id].append(round_contribution)
        
        # Keep only last 10 contributions
        self.client_contributions[client_id] = \
            self.client_contributions[client_id][-10:]
        
        # Calculate reputation score (exponential moving average)
        current_score = self.calculate_contribution_score(round_contribution)
        
        if client_id not in self.reputation_scores:
            self.reputation_scores[client_id] = current_score
        else:
            # EMA with alpha = 0.3
            self.reputation_scores[client_id] = (
                0.3 * current_score + 
                0.7 * self.reputation_scores[client_id]
            )
    
    def get_reputation_tiers(self) -> Dict[str, List[str]]:
        """
        Categorize clients into reputation tiers
        """
        tiers = {
            'gold': [],
            'silver': [],
            'bronze': []
        }
        
        for client_id, score in self.reputation_scores.items():
            if score >= 0.8:
                tiers['gold'].append(client_id)
            elif score >= 0.5:
                tiers['silver'].append(client_id)
            else:
                tiers['bronze'].append(client_id)
        
        return tiers
```

### 7.2 Blockchain-Based Incentives

```python
class BlockchainIncentive:
    """
    Blockchain-based incentive system for federated learning
    """
    def __init__(self, contract_address: str = None):
        self.contract_address = contract_address
        self.transactions = []
        
    def record_contribution(
        self,
        client_id: str,
        contribution_hash: str,
        timestamp: float
    ) -> str:
        """
        Record contribution on blockchain
        """
        transaction = {
            'type': 'contribution',
            'client_id': client_id,
            'contribution_hash': contribution_hash,
            'timestamp': timestamp,
            'tx_hash': self._generate_tx_hash()
        }
        
        self.transactions.append(transaction)
        return transaction['tx_hash']
    
    def issue_reward(
        self,
        client_id: str,
        amount: float,
        round_num: int
    ) -> str:
        """
        Issue reward token to client
        """
        transaction = {
            'type': 'reward',
            'client_id': client_id,
            'amount': amount,
            'round': round_num,
            'timestamp': time.time(),
            'tx_hash': self._generate_tx_hash()
        }
        
        self.transactions.append(transaction)
        return transaction['tx_hash']
    
    def _generate_tx_hash(self) -> str:
        """Generate unique transaction hash"""
        import hashlib
        data = f"{time.time()}{secrets.token_hex(16)}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]
    
    def get_client_history(self, client_id: str) -> List[Dict]:
        """Get transaction history for a client"""
        return [
            tx for tx in self.transactions
            if tx.get('client_id') == client_id
        ]
```

---

## 8. Cross-Silo Learning for ResilienceAI

### 8.1 Multi-Organization Architecture

```python
class CrossSiloFederation:
    """
    Federated learning across multiple organizations
    """
    def __init__(self):
        self.organizations = {}
        self.global_model = None
        self.federation_rules = {
            'min_participants': 3,
            'consensus_threshold': 0.66,
            'data_validation': True,
            'audit_logging': True
        }
    
    def register_organization(
        self,
        org_id: str,
        org_type: str,  # 'fire_dept', 'hospital', 'police', etc.
        data_schema: Dict,
        compute_capacity: int,
        contact_info: Dict
    ):
        """
        Register an organization in the federation
        """
        self.organizations[org_id] = {
            'type': org_type,
            'data_schema': data_schema,
            'compute_capacity': compute_capacity,
            'contact': contact_info,
            'joined_at': time.time(),
            'participation_count': 0,
            'reputation_score': 1.0
        }
    
    def validate_data_compatibility(
        self,
        org_id: str,
        data_sample: Dict
    ) -> bool:
        """
        Validate that organization's data matches federation schema
        """
        org = self.organizations.get(org_id)
        if not org:
            return False
        
        required_fields = org['data_schema'].get('required', [])
        
        for field in required_fields:
            if field not in data_sample:
                return False
        
        return True
    
    def execute_federated_training(
        self,
        model_architecture: nn.Module,
        num_rounds: int
    ) -> nn.Module:
        """
        Execute training across all organizations
        """
        # Check minimum participants
        if len(self.organizations) < self.federation_rules['min_participants']:
            raise ValueError(
                f"Need at least {self.federation_rules['min_participants']} "
                f"organizations, got {len(self.organizations)}"
            )
        
        # Initialize global model
        self.global_model = model_architecture
        
        for round_num in range(num_rounds):
            print(f"=== Federation Round {round_num + 1}/{num_rounds} ===")
            
            # Collect updates from all organizations
            updates = []
            for org_id, org_info in self.organizations.items():
                try:
                    update = self._get_org_update(org_id)
                    updates.append((org_id, update))
                    org_info['participation_count'] += 1
                except Exception as e:
                    print(f"Failed to get update from {org_id}: {e}")
            
            # Check consensus threshold
            participation_rate = len(updates) / len(self.organizations)
            if participation_rate < self.federation_rules['consensus_threshold']:
                print(f"Warning: Participation rate {participation_rate:.2%} "
                      f"below threshold {self.federation_rules['consensus_threshold']:.2%}")
            
            # Aggregate updates
            if updates:
                self._aggregate_org_updates(updates)
            
            # Audit logging
            if self.federation_rules['audit_logging']:
                self._log_round(round_num, updates)
        
        return self.global_model
    
    def _get_org_update(self, org_id: str) -> Dict[str, torch.Tensor]:
        """Get model update from organization"""
        # In practice, this would communicate with organization's FL server
        pass
    
    def _aggregate_org_updates(
        self,
        updates: List[tuple]
    ):
        """Aggregate updates from organizations"""
        # Use FedAvg or other aggregation
        pass
    
    def _log_round(self, round_num: int, updates: List[tuple]):
        """Log round information for audit"""
        log_entry = {
            'round': round_num,
            'timestamp': time.time(),
            'participating_orgs': [org_id for org_id, _ in updates],
            'num_participants': len(updates)
        }
        # Store log entry
        print(f"Audit log: {log_entry}")
```

---

## 9. Use Cases for ResilienceAI

### 9.1 Disaster Prediction Models

```python
class DisasterPredictionFL:
    """
    Federated learning for disaster prediction
    """
    def __init__(self):
        self.disaster_types = [
            'wildfire', 'flood', 'earthquake', 
            'hurricane', 'tornado', 'landslide'
        ]
    
    def create_prediction_model(self) -> nn.Module:
        """
        Create LSTM-based disaster prediction model
        """
        class DisasterPredictor(nn.Module):
            def __init__(self, input_dim=20, hidden_dim=128, num_classes=6):
                super().__init__()
                self.lstm = nn.LSTM(
                    input_dim, hidden_dim,
                    num_layers=2,
                    batch_first=True,
                    dropout=0.2
                )
                self.fc = nn.Sequential(
                    nn.Linear(hidden_dim, 64),
                    nn.ReLU(),
                    nn.Dropout(0.3),
                    nn.Linear(64, num_classes),
                    nn.Sigmoid()
                )
            
            def forward(self, x):
                lstm_out, _ = self.lstm(x)
                # Use last time step
                return self.fc(lstm_out[:, -1, :])
        
        return DisasterPredictor()
    
    def federated_training_pipeline(
        self,
        organizations: List[str],
        sensor_data_sources: Dict[str, Dataset]
    ):
        """
        Execute federated training for disaster prediction
        """
        # Create FL server
        model = self.create_prediction_model()
        config = FLConfig(
            num_rounds=50,
            clients_per_round=len(organizations),
            local_epochs=3,
            dp_enabled=True,
            dp_epsilon=2.0
        )
        
        server = FederatedServer(model, config)
        
        # Register clients
        for org_id in organizations:
            client_model = self.create_prediction_model()
            client = FederatedClient(
                client_id=org_id,
                model=client_model,
                train_data=sensor_data_sources[org_id],
                config=config
            )
            server.register_client(client)
        
        # Train
        history = server.train()
        
        return server.global_model, history
```

### 9.2 Resource Allocation Optimization

```python
class ResourceAllocationFL:
    """
    Federated learning for optimal resource allocation
    """
    def __init__(self):
        self.resource_types = [
            'personnel', 'vehicles', 'equipment',
            'medical', 'communications', 'supplies'
        ]
    
    def create_allocation_model(self) -> nn.Module:
        """
        Create reinforcement learning-based allocation model
        """
        class AllocationNetwork(nn.Module):
            def __init__(self, state_dim=50, action_dim=20):
                super().__init__()
                self.shared = nn.Sequential(
                    nn.Linear(state_dim, 256),
                    nn.ReLU(),
                    nn.Linear(256, 128),
                    nn.ReLU()
                )
                self.policy = nn.Linear(128, action_dim)
                self.value = nn.Linear(128, 1)
            
            def forward(self, state):
                features = self.shared(state)
                return self.policy(features), self.value(features)
        
        return AllocationNetwork()
```

### 9.3 Damage Assessment Models

```python
class DamageAssessmentFL:
    """
    Federated learning for automated damage assessment
    """
    def __init__(self):
        self.damage_levels = ['none', 'minor', 'moderate', 'major', 'destroyed']
    
    def create_assessment_model(self) -> nn.Module:
        """
        Create CNN-based damage assessment model
        """
        class DamageAssessmentCNN(nn.Module):
            def __init__(self, num_classes=5):
                super().__init__()
                self.features = nn.Sequential(
                    # Block 1
                    nn.Conv2d(3, 64, 3, padding=1),
                    nn.BatchNorm2d(64),
                    nn.ReLU(),
                    nn.Conv2d(64, 64, 3, padding=1),
                    nn.BatchNorm2d(64),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    
                    # Block 2
                    nn.Conv2d(64, 128, 3, padding=1),
                    nn.BatchNorm2d(128),
                    nn.ReLU(),
                    nn.Conv2d(128, 128, 3, padding=1),
                    nn.BatchNorm2d(128),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                    
                    # Block 3
                    nn.Conv2d(128, 256, 3, padding=1),
                    nn.BatchNorm2d(256),
                    nn.ReLU(),
                    nn.Conv2d(256, 256, 3, padding=1),
                    nn.BatchNorm2d(256),
                    nn.ReLU(),
                    nn.MaxPool2d(2),
                )
                
                self.classifier = nn.Sequential(
                    nn.AdaptiveAvgPool2d((1, 1)),
                    nn.Flatten(),
                    nn.Linear(256, 128),
                    nn.ReLU(),
                    nn.Dropout(0.5),
                    nn.Linear(128, num_classes)
                )
            
            def forward(self, x):
                x = self.features(x)
                return self.classifier(x)
        
        return DamageAssessmentCNN()
```

---

## 10. Technology Stack

### 10.1 Recommended Stack for ResilienceAI

| Layer | Technology | Purpose |
|-------|------------|---------|
| **ML Framework** | PyTorch | Model development |
| **FL Framework** | Flower / PySyft | Federated orchestration |
| **Privacy** | Opacus | Differential privacy |
| **Security** | TenSEAL / SPDZ | Homomorphic encryption, SMPC |
| **Communication** | gRPC / WebSockets | Client-server communication |
| **Storage** | IPFS / Distributed DB | Model versioning |
| **Blockchain** | Hyperledger Fabric | Incentive tracking |
| **Monitoring** | Prometheus/Grafana | FL metrics |

### 10.2 Flower Framework Integration

```python
# Flower-based implementation
import flwr as fl
from flwr.common import Parameters, FitRes
from typing import List, Tuple, Dict

class ResilienceAIClient(fl.client.NumPyClient):
    """
    Flower client for ResilienceAI
    """
    def __init__(self, model, trainloader, testloader):
        self.model = model
        self.trainloader = trainloader
        self.testloader = testloader
    
    def get_parameters(self, config):
        return [val.cpu().numpy() for val in self.model.state_dict().values()]
    
    def set_parameters(self, parameters):
        params_dict = zip(self.model.state_dict().keys(), parameters)
        state_dict = {k: torch.tensor(v) for k, v in params_dict}
        self.model.load_state_dict(state_dict, strict=True)
    
    def fit(self, parameters, config):
        self.set_parameters(parameters)
        train(self.model, self.trainloader, epochs=5)
        return self.get_parameters(config={}), len(self.trainloader.dataset), {}
    
    def evaluate(self, parameters, config):
        self.set_parameters(parameters)
        loss, accuracy = test(self.model, self.testloader)
        return float(loss), len(self.testloader.dataset), {"accuracy": float(accuracy)}

# Custom aggregation strategy
class SecureFedAvg(fl.server.strategy.FedAvg):
    """
    Secure federated averaging with differential privacy
    """
    def __init__(self, dp_epsilon=3.0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.dp_epsilon = dp_epsilon
    
    def aggregate_fit(
        self,
        server_round: int,
        results: List[Tuple[fl.server.client_proxy.ClientProxy, FitRes]],
        failures: List
    ) -> Tuple[Parameters, Dict]:
        """Aggregate with differential privacy"""
        # Call parent's aggregate_fit
        parameters, metrics = super().aggregate_fit(server_round, results, failures)
        
        # Add DP noise
        if parameters is not None:
            parameters = self._add_dp_noise(parameters)
        
        return parameters, metrics
    
    def _add_dp_noise(self, parameters: Parameters) -> Parameters:
        """Add differential privacy noise"""
        # Implementation of DP noise addition
        return parameters

# Start server
strategy = SecureFedAvg(
    fraction_fit=0.1,
    min_fit_clients=3,
    min_available_clients=10,
    dp_epsilon=3.0
)

fl.server.start_server(
    server_address="0.0.0.0:8080",
    config=fl.server.ServerConfig(num_rounds=100),
    strategy=strategy
)
```

---

## 11. Practical Considerations

### 11.1 Deployment Checklist

```python
class FLDeploymentChecklist:
    """
    Pre-deployment checklist for ResilienceAI FL
    """
    CHECKLIST = {
        'security': [
            'Differential privacy configured',
            'Secure aggregation enabled',
            'TLS/SSL certificates installed',
            'Model update encryption verified',
            'Access controls implemented'
        ],
        'privacy': [
            'Privacy budget calculated',
            'Data minimization applied',
            'Consent mechanisms in place',
            'Audit logging enabled',
            'Data retention policy defined'
        ],
        'scalability': [
            'Client selection strategy defined',
            'Communication compression enabled',
            'Hierarchical aggregation configured',
            'Load balancing tested',
            'Failover mechanisms in place'
        ],
        'monitoring': [
            'FL metrics dashboard created',
            'Alert thresholds configured',
            'Model performance tracked',
            'Privacy budget monitored',
            'Network latency measured'
        ],
        'compliance': [
            'Data governance policies reviewed',
            'Cross-border data rules checked',
            'Industry regulations verified',
            'Documentation completed',
            'Stakeholder approvals obtained'
        ]
    }
    
    @classmethod
    def validate(cls) -> Dict[str, List[str]]:
        """Return checklist for validation"""
        return cls.CHECKLIST
```

### 11.2 Performance Optimization

```python
class FLPerformanceOptimizer:
    """
    Optimize federated learning performance
    """
    
    @staticmethod
    def optimize_client_selection(
        clients: List[FederatedClient],
        target_num: int,
        strategy: str = 'hybrid'
    ) -> List[FederatedClient]:
        """
        Optimize client selection for training round
        
        Strategies:
        - 'random': Random selection
        - 'round_robin': Cycle through all clients
        - 'performance': Select based on past performance
        - 'hybrid': Combine multiple strategies
        """
        if strategy == 'random':
            import random
            return random.sample(clients, min(target_num, len(clients)))
        
        elif strategy == 'round_robin':
            # Track last participation
            sorted_clients = sorted(
                clients,
                key=lambda c: c.last_participation
            )
            return sorted_clients[:target_num]
        
        elif strategy == 'performance':
            # Select based on data quality and past contributions
            scored_clients = [
                (c, c.data_quality_score * c.past_performance)
                for c in clients
            ]
            scored_clients.sort(key=lambda x: x[1], reverse=True)
            return [c for c, _ in scored_clients[:target_num]]
        
        elif strategy == 'hybrid':
            # 50% high performers, 30% random, 20% least recent
            high_perf = FLPerformanceOptimizer.optimize_client_selection(
                clients, int(target_num * 0.5), 'performance'
            )
            random_sel = FLPerformanceOptimizer.optimize_client_selection(
                [c for c in clients if c not in high_perf],
                int(target_num * 0.3), 'random'
            )
            round_robin = FLPerformanceOptimizer.optimize_client_selection(
                [c for c in clients if c not in high_perf + random_sel],
                int(target_num * 0.2), 'round_robin'
            )
            return high_perf + random_sel + round_robin
    
    @staticmethod
    def adaptive_learning_rate(
        base_lr: float,
        round_num: int,
        total_rounds: int,
        schedule: str = 'cosine'
    ) -> float:
        """
        Adaptive learning rate schedule
        """
        if schedule == 'cosine':
            import math
            return base_lr * 0.5 * (
                1 + math.cos(math.pi * round_num / total_rounds)
            )
        
        elif schedule == 'exponential':
            decay_rate = 0.95
            return base_lr * (decay_rate ** round_num)
        
        elif schedule == 'step':
            decay_factor = 0.5
            decay_interval = total_rounds // 5
            return base_lr * (decay_factor ** (round_num // decay_interval))
        
        return base_lr
```

---

## 12. Implementation Priority Order

### Phase 1: Foundation (Weeks 1-4)
1. **Basic FedAvg Implementation**
   - Set up Flower/PySyft framework
   - Implement simple client-server architecture
   - Test with synthetic disaster data

2. **Privacy Baseline**
   - Add gradient clipping
   - Implement basic differential privacy
   - Privacy budget tracking

### Phase 2: Security (Weeks 5-8)
3. **Secure Aggregation**
   - Implement SMPC protocols
   - Add homomorphic encryption option
   - Secure communication channels

4. **Authentication & Authorization**
   - Client authentication
   - Role-based access control
   - Audit logging

### Phase 3: Optimization (Weeks 9-12)
5. **Communication Efficiency**
   - Model compression
   - Sparse updates
   - Adaptive communication

6. **Advanced Aggregation**
   - FedAdam, FedProx
   - Personalized FL
   - Hierarchical aggregation

### Phase 4: Production (Weeks 13-16)
7. **Incentive System**
   - Contribution tracking
   - Reputation mechanism
   - Reward distribution

8. **Monitoring & Governance**
   - FL metrics dashboard
   - Privacy accounting
   - Compliance reporting

---

## 13. Summary

### Key Recommendations for ResilienceAI

1. **Start with Cross-Silo FL**: Focus on organization-level collaboration (fire departments, hospitals, emergency services) before edge device deployment.

2. **Privacy-First Design**: Implement differential privacy from day one with ε ≤ 3.0 for strong privacy guarantees.

3. **Secure by Default**: Use secure aggregation for all model updates to prevent reconstruction attacks.

4. **Incremental Deployment**: Begin with a single disaster type (e.g., wildfire prediction) before expanding to multi-hazard models.

5. **Federated Evaluation**: Implement privacy-preserving evaluation metrics that don't expose individual client data.

6. **Hybrid Architecture**: Combine hierarchical FL (regional → national) with cross-silo collaboration for maximum flexibility.

### Expected Benefits

| Metric | Improvement |
|--------|-------------|
| Data Privacy | 100% raw data stays local |
| Model Accuracy | 5-15% improvement over isolated training |
| Data Diversity | Access to 10x more training scenarios |
| Time to Deploy | 50% faster with pre-trained global models |
| Compliance | Automatic GDPR/HIPAA compliance |

---

## References

1. McMahan, B., et al. (2017). "Communication-Efficient Learning of Deep Networks from Decentralized Data"
2. Bonawitz, K., et al. (2017). "Practical Secure Aggregation for Privacy-Preserving Machine Learning"
3. Dwork, C., & Roth, A. (2014). "The Algorithmic Foundations of Differential Privacy"
4. Li, T., et al. (2020). "Federated Learning: Challenges, Methods, and Future Directions"
5. Kairouz, P., et al. (2021). "Advances and Open Problems in Federated Learning"

---

*Document Version: 1.0*
*Last Updated: 2024*
*For ResilienceAI Federated Learning Implementation*
