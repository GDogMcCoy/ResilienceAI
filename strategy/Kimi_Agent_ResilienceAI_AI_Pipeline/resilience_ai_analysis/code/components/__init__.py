"""
ResilienceAI Dashboard Components
Modular UI components for enhanced dashboard functionality
"""

from typing import Dict, Type, Callable, Optional
from pathlib import Path
import importlib
import pkgutil

# Component registry for dynamic loading
COMPONENT_REGISTRY: Dict[str, Type] = {}

def register_component(name: str) -> Callable:
    """Decorator to register a component class."""
    def decorator(cls: Type) -> Type:
        COMPONENT_REGISTRY[name] = cls
        return cls
    return decorator

def get_component(name: str) -> Optional[Type]:
    """Retrieve a registered component by name."""
    return COMPONENT_REGISTRY.get(name)

def list_components() -> Dict[str, Type]:
    """List all registered components."""
    return COMPONENT_REGISTRY.copy()

def discover_components():
    """Auto-discover and register all components in the package."""
    package_dir = Path(__file__).parent
    for _, module_name, _ in pkgutil.iter_modules([str(package_dir)]):
        if module_name.startswith('_'):
            continue
        try:
            importlib.import_module(f".{module_name}", __package__)
        except Exception as e:
            print(f"Warning: Failed to import component module {module_name}: {e}")

# Auto-discover components on package import
discover_components()
