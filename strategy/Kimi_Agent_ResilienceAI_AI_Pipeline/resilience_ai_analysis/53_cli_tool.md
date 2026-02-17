# ResilienceAI CLI Tool Design

## Executive Summary

This document provides a comprehensive design for the ResilienceAI Command-Line Interface (CLI), built using **Typer** for modern Python CLI development. The CLI enables developers to interact with ResilienceAI services, manage configurations, run simulations, and automate workflows from the command line.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Command Structure](#2-command-structure)
3. [Implementation](#3-implementation)
4. [Configuration Management](#4-configuration-management)
5. [Output Formatting](#5-output-formatting)
6. [Progress Indicators](#6-progress-indicators)
7. [Interactive Prompts](#7-interactive-prompts)
8. [Shell Completion](#8-shell-completion)
9. [Error Handling](#9-error-handling)
10. [Logging System](#10-logging-system)
11. [Testing Strategy](#11-testing-strategy)
12. [Distribution](#12-distribution)
13. [Integration Guide](#13-integration-guide)
14. [Implementation Priority](#14-implementation-priority)

---

## 1. Architecture Overview

### 1.1 Framework Selection: Typer

**Why Typer over Click:**

| Feature | Typer | Click |
|---------|-------|-------|
| Type hints | Native | Manual |
| Auto-completion | Built-in | Requires plugin |
| Documentation | Auto-generated | Manual |
| Learning curve | Low | Medium |
| IDE support | Excellent | Good |
| Modern Python | 3.7+ | 3.6+ |

**Decision:** Use **Typer** for its modern Python type hint integration and reduced boilerplate.

### 1.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     ResilienceAI CLI                            │
├─────────────────────────────────────────────────────────────────┤
│  Entry Point (resilience-ai)                                    │
│  ├── Main CLI App (typer.Typer)                                 │
│  │   ├── auth commands                                          │
│  │   ├── config commands                                        │
│  │   ├── model commands                                         │
│  │   ├── simulation commands                                    │
│  │   ├── analysis commands                                      │
│  │   ├── workflow commands                                      │
│  │   └── system commands                                         │
│  └── Shared Components                                          │
│      ├── Configuration Manager                                  │
│      ├── API Client                                             │
│      ├── Output Formatters                                      │
│      ├── Progress Indicators                                    │
│      └── Error Handlers                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 1.3 Project Structure

```
resilienceai-cli/
├── pyproject.toml              # Project configuration
├── README.md                   # Documentation
├── CHANGELOG.md                # Version history
├── LICENSE                     # License file
├── src/
│   └── resilienceai/
│       ├── __init__.py         # Package initialization
│       ├── __main__.py         # Entry point
│       ├── cli.py              # Main CLI application
│       ├── commands/           # Command modules
│       │   ├── __init__.py
│       │   ├── auth.py         # Authentication commands
│       │   ├── config.py       # Configuration commands
│       │   ├── model.py        # Model management
│       │   ├── simulation.py   # Simulation commands
│       │   ├── analysis.py     # Analysis commands
│       │   ├── workflow.py     # Workflow automation
│       │   └── system.py       # System commands
│       ├── core/               # Core functionality
│       │   ├── __init__.py
│       │   ├── config.py       # Configuration management
│       │   ├── client.py       # API client
│       │   ├── exceptions.py   # Custom exceptions
│       │   └── constants.py    # Constants
│       ├── formatters/         # Output formatters
│       │   ├── __init__.py
│       │   ├── json.py
│       │   ├── csv.py
│       │   ├── table.py
│       │   └── yaml.py
│       ├── utils/              # Utilities
│       │   ├── __init__.py
│       │   ├── console.py      # Console utilities
│       │   ├── progress.py     # Progress indicators
│       │   ├── prompts.py      # Interactive prompts
│       │   └── validators.py   # Input validators
│       └── plugins/            # Plugin system
│           ├── __init__.py
│           └── base.py
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_commands/
│   │   ├── test_core/
│   │   └── test_utils/
│   └── integration/
└── docs/                       # Documentation
    ├── usage.md
    ├── configuration.md
    └── api.md
```

---

## 2. Command Structure

### 2.1 Command Hierarchy

```
resilience-ai (rai)
├── auth                          # Authentication commands
│   ├── login                     # Login to ResilienceAI
│   ├── logout                    # Logout
│   ├── status                    # Check auth status
│   └── token                     # Token management
│       ├── refresh               # Refresh access token
│       └── revoke                # Revoke token
├── config                        # Configuration management
│   ├── get <key>                 # Get configuration value
│   ├── set <key> <value>         # Set configuration value
│   ├── list                      # List all configurations
│   ├── reset                     # Reset to defaults
│   └── validate                  # Validate configuration
├── model                         # Model management
│   ├── list                      # List available models
│   ├── info <model_id>           # Get model information
│   ├── pull <model_id>           # Download model
│   ├── push <path>               # Upload model
│   ├── delete <model_id>         # Delete model
│   └── validate <path>           # Validate model
├── simulation                    # Simulation commands
│   ├── run <config>              # Run simulation
│   ├── list                      # List simulations
│   ├── status <id>               # Get simulation status
│   ├── logs <id>                 # Get simulation logs
│   ├── stop <id>                 # Stop simulation
│   ├── resume <id>               # Resume simulation
│   ├── clone <id>                # Clone simulation
│   └── delete <id>               # Delete simulation
├── analysis                      # Analysis commands
│   ├── run <simulation_id>       # Run analysis
│   ├── list                      # List analyses
│   ├── export <id>               # Export analysis results
│   ├── compare <id1> <id2>       # Compare analyses
│   └── visualize <id>            # Generate visualizations
├── workflow                      # Workflow automation
│   ├── list                      # List workflows
│   ├── create <name>             # Create workflow
│   ├── run <name>                # Execute workflow
│   ├── schedule <name>           # Schedule workflow
│   ├── logs <name>               # View workflow logs
│   └── delete <name>             # Delete workflow
└── system                        # System commands
    ├── status                    # System status
    ├── health                    # Health check
    ├── version                   # CLI version
    ├── update                    # Check for updates
    └── doctor                    # Diagnostic tool
```

### 2.2 Command Naming Conventions

| Pattern | Example | Usage |
|---------|---------|-------|
| Noun + Verb | `model list` | Actions on resources |
| Single word | `login`, `status` | Common operations |
| Hyphenated | `health-check` | Multi-word commands |
| CRUD pattern | `create`, `read`, `update`, `delete` | Resource management |

---

## 3. Implementation

### 3.1 Main CLI Application

**File:** `src/resilienceai/cli.py`

```python
"""ResilienceAI CLI - Main Application"""

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from resilienceai.commands import auth, config, model, simulation, analysis, workflow, system
from resilienceai.core.config import settings
from resilienceai.utils.console import get_console
from resilienceai import __version__

# Create main CLI app
app = typer.Typer(
    name="resilience-ai",
    help="ResilienceAI CLI - Command-line interface for ResilienceAI platform",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=True,
)

# Add subcommands
app.add_typer(auth.app, name="auth", help="Authentication commands")
app.add_typer(config.app, name="config", help="Configuration management")
app.add_typer(model.app, name="model", help="Model management")
app.add_typer(simulation.app, name="simulation", help="Simulation commands")
app.add_typer(analysis.app, name="analysis", help="Analysis commands")
app.add_typer(workflow.app, name="workflow", help="Workflow automation")
app.add_typer(system.app, name="system", help="System commands")

console = get_console()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(None, "--version", "-v", help="Show version", is_eager=True),
    verbose: int = typer.Option(0, "--verbose", "-v", count=True, help="Increase verbosity"),
    quiet: bool = typer.Option(False, "--quiet", "-q", help="Suppress output"),
    config_file: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
    output_format: str = typer.Option("table", "--output", "-o", help="Output format"),
    no_color: bool = typer.Option(False, "--no-color", help="Disable colors"),
):
    """ResilienceAI CLI - Command-line interface for the ResilienceAI platform."""
    if version:
        show_version()
        raise typer.Exit()
    
    ctx = typer.get_current_context()
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet
    ctx.obj["config_file"] = config_file
    ctx.obj["output_format"] = output_format
    ctx.obj["no_color"] = no_color
    
    if no_color:
        console._color_system = None


def show_version():
    """Display version information."""
    version_text = Text()
    version_text.append("ResilienceAI CLI\n", style="bold blue")
    version_text.append(f"Version: {__version__}\n", style="cyan")
    version_text.append(f"Python: {settings.python_version}\n", style="dim")
    version_text.append(f"Platform: {settings.platform}", style="dim")
    console.print(Panel(version_text, title="Version Info", border_style="blue"))


@app.command()
def welcome():
    """Display welcome message and quick start guide."""
    welcome_text = """
    [bold green]Welcome to ResilienceAI CLI![/bold green]
    
    [bold]Quick Start:[/bold]
    1. [cyan]Authenticate:[/cyan] $ resilience-ai auth login
    2. [cyan]Configure:[/cyan] $ resilience-ai config set api_url https://api.resilience.ai
    3. [cyan]List models:[/cyan] $ resilience-ai model list
    4. [cyan]Run simulation:[/cyan] $ resilience-ai simulation run config.yaml
    
    [dim]For more info: https://docs.resilience.ai/cli[/dim]
    """
    console.print(Panel(welcome_text, title="Welcome", border_style="green"))


if __name__ == "__main__":
    app()
```

### 3.2 Authentication Commands

**File:** `src/resilienceai/commands/auth.py`

```python
"""Authentication commands for ResilienceAI CLI"""

import typer
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

from resilienceai.core.client import ResilienceAIClient
from resilienceai.core.config import settings
from resilienceai.core.exceptions import AuthenticationError
from resilienceai.utils.console import get_console

app = typer.Typer(help="Authentication commands")
console = get_console()


@app.command()
def login(
    username: Optional[str] = typer.Option(None, "--username", "-u", help="Username"),
    password: Optional[str] = typer.Option(None, "--password", "-p", help="Password"),
    api_key: Optional[str] = typer.Option(None, "--api-key", "-k", help="API key"),
    sso: bool = typer.Option(False, "--sso", help="Use SSO"),
    force: bool = typer.Option(False, "--force", "-f", help="Force re-auth"),
):
    """Authenticate with ResilienceAI platform."""
    if not force and settings.is_authenticated():
        console.print("[yellow]Already authenticated. Use --force to re-authenticate.[/yellow]")
        raise typer.Exit(0)
    
    try:
        client = ResilienceAIClient()
        
        if sso:
            console.print("[blue]Initiating SSO authentication...[/blue]")
            client.authenticate_sso()
        elif api_key:
            client.authenticate_api_key(api_key)
        else:
            if not username:
                username = Prompt.ask("Username")
            if not password:
                password = Prompt.ask("Password", password=True)
            client.authenticate(username, password)
        
        settings.save_credentials(client.get_token())
        
        console.print(Panel(
            f"[green]Successfully authenticated as {client.get_user()['email']}[/green]",
            title="Login Successful", border_style="green"
        ))
    except AuthenticationError as e:
        console.print(f"[red]Authentication failed: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def logout(revoke: bool = typer.Option(True, "--revoke/--no-revoke"), all_sessions: bool = False):
    """Logout from ResilienceAI platform."""
    if not settings.is_authenticated():
        console.print("[yellow]Not currently authenticated.[/yellow]")
        raise typer.Exit(0)
    
    try:
        if revoke:
            client = ResilienceAIClient()
            client.logout(all_sessions=all_sessions)
        settings.clear_credentials()
        console.print("[green]Successfully logged out.[/green]")
    except Exception as e:
        console.print(f"[yellow]Warning: {e}[/yellow]")
        settings.clear_credentials()


@app.command()
def status(detailed: bool = typer.Option(False, "--detailed", "-d")):
    """Check authentication status."""
    if not settings.is_authenticated():
        console.print("[red]Not authenticated[/red]")
        raise typer.Exit(1)
    
    try:
        client = ResilienceAIClient()
        user = client.get_user()
        
        if detailed:
            from rich.table import Table
            table = Table(title="Authentication Status")
            table.add_column("Property", style="cyan")
            table.add_column("Value", style="green")
            table.add_row("Status", "Authenticated")
            table.add_row("User", user["email"])
            table.add_row("Organization", user.get("organization", "N/A"))
            console.print(table)
        else:
            console.print(f"[green]Authenticated as {user['email']}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)
```

### 3.3 Configuration Commands

**File:** `src/resilienceai/commands/config.py`

```python
"""Configuration management commands"""

import typer
from typing import Optional
from pathlib import Path
from rich.table import Table
from rich.panel import Panel

from resilienceai.core.config import settings
from resilienceai.utils.console import get_console

app = typer.Typer(help="Configuration management")
console = get_console()


@app.command()
def get(key: str, default: Optional[str] = None):
    """Get a configuration value."""
    value = settings.get(key, default)
    if value is not None:
        console.print(f"{key} = {value}")
    else:
        console.print(f"[yellow]Key '{key}' not found[/yellow]")
        raise typer.Exit(1)


@app.command()
def set(key: str, value: str, global_config: bool = typer.Option(False, "--global", "-g")):
    """Set a configuration value."""
    scope = "global" if global_config else "local"
    settings.set(key, value, global_=global_config)
    console.print(f"[green]Set {key} = {value} ({scope})[/green]")


@app.command(name="list")
def list_config(show_all: bool = False, format: str = "table"):
    """List all configuration values."""
    config_data = settings.get_all(include_defaults=show_all)
    
    if format == "table":
        table = Table(title="Configuration")
        table.add_column("Key", style="cyan")
        table.add_column("Value", style="green")
        table.add_column("Source", style="dim")
        for key, info in config_data.items():
            value = info["value"]
            source = info.get("source", "default")
            if "password" in key or "token" in key:
                value = "********"
            table.add_row(key, str(value), source)
        console.print(table)
    elif format == "json":
        import json
        console.print(json.dumps(config_data, indent=2))


@app.command()
def reset(key: Optional[str] = None, force: bool = False):
    """Reset configuration to defaults."""
    if not force:
        msg = f"Reset '{key}'?" if key else "Reset all configuration?"
        if not typer.confirm(msg):
            console.print("Cancelled.")
            raise typer.Exit(0)
    settings.reset(key)
    console.print("[green]Configuration reset.[/green]")


@app.command()
def validate():
    """Validate current configuration."""
    errors = settings.validate()
    if errors:
        console.print("[red]Configuration errors:[/red]")
        for error in errors:
            console.print(f"  • {error}")
        raise typer.Exit(1)
    else:
        console.print("[green]Configuration is valid.[/green]")
```

### 3.4 Model Management Commands

**File:** `src/resilienceai/commands/model.py`

```python
"""Model management commands"""

import typer
from typing import Optional, List
from pathlib import Path
from rich.table import Table
from rich.progress import Progress

from resilienceai.core.client import ResilienceAIClient
from resilienceai.core.exceptions import ModelError
from resilienceai.utils.console import get_console
from resilienceai.utils.progress import create_progress

app = typer.Typer(help="Model management")
console = get_console()


@app.command(name="list")
def list_models(
    tag: Optional[List[str]] = typer.Option(None, "--tag", "-t"),
    owner: Optional[str] = typer.Option(None, "--owner", "-o"),
    format: str = "table",
    limit: int = 50,
):
    """List available models."""
    try:
        client = ResilienceAIClient()
        with create_progress() as progress:
            task = progress.add_task("Fetching models...", total=None)
            models = client.list_models(tags=tag, owner=owner, limit=limit)
            progress.update(task, completed=True)
        
        if not models:
            console.print("[yellow]No models found.[/yellow]")
            return
        
        if format == "table":
            table = Table(title="Available Models")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Version", style="blue")
            table.add_column("Owner", style="magenta")
            table.add_column("Tags", style="yellow")
            for model in models:
                table.add_row(
                    model["id"], model["name"],
                    model.get("version", "N/A"),
                    model.get("owner", "N/A"),
                    ", ".join(model.get("tags", []))
                )
            console.print(table)
        elif format == "json":
            import json
            console.print(json.dumps(models, indent=2))
    except ModelError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def pull(model_id: str, output: Optional[Path] = None, force: bool = False):
    """Download a model."""
    try:
        client = ResilienceAIClient()
        model = client.get_model(model_id)
        dest = output or Path(f"{model_id}.zip")
        
        if dest.exists() and not force:
            if not typer.confirm(f"{dest} exists. Overwrite?"):
                raise typer.Exit(0)
        
        with create_download_progress() as progress:
            task = progress.add_task(f"Downloading {model_id}...", total=model.get("size", 0))
            client.download_model(model_id, dest, progress_callback=lambda n: progress.update(task, advance=n))
        
        console.print(f"[green]Downloaded to {dest}[/green]")
    except ModelError as e:
        console.print(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)


def format_size(size_bytes: int) -> str:
    """Format byte size to human readable."""
    if size_bytes == 0:
        return "0 B"
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} PB"
```

---

## 4. Configuration Management

### 4.1 Configuration Architecture

**File:** `src/resilienceai/core/config.py`

```python
"""Configuration management for ResilienceAI CLI"""

import os
import json
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field, asdict
from functools import lru_cache
import sys
import platform as pf


@dataclass
class Settings:
    """Application settings with defaults."""
    api_url: str = "https://api.resilience.ai/v1"
    api_timeout: int = 30
    api_retries: int = 3
    auth_token: Optional[str] = None
    refresh_token: Optional[str] = None
    default_format: str = "table"
    color_output: bool = True
    log_level: str = "INFO"
    log_file: Optional[str] = None
    models_dir: str = "~/.resilienceai/models"
    data_dir: str = "~/.resilienceai/data"
    cache_dir: str = "~/.resilienceai/cache"
    auto_update_check: bool = True
    telemetry_enabled: bool = True
    python_version: str = field(default_factory=lambda: sys.version)
    platform: str = field(default_factory=pf.platform)
    
    def get_valid_keys(self) -> List[str]:
        return list(asdict(self).keys())


class ConfigManager:
    """Manages configuration files and settings."""
    
    def __init__(self):
        self.settings = Settings()
        self._config_cache: Dict[str, Any] = {}
        self._load_configs()
    
    @property
    def global_config_path(self) -> Path:
        if os.name == "nt":
            config_dir = Path(os.environ.get("APPDATA", "")) / "ResilienceAI"
        else:
            config_dir = Path.home() / ".config" / "resilienceai"
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "config.yaml"
    
    @property
    def local_config_path(self) -> Path:
        return Path(".resilienceai.yaml")
    
    @property
    def credentials_path(self) -> Path:
        return self.global_config_path.parent / "credentials"
    
    def _load_configs(self):
        if self.global_config_path.exists():
            self._load_file(self.global_config_path)
        if self.local_config_path.exists():
            self._load_file(self.local_config_path)
        if self.credentials_path.exists():
            self._load_credentials()
        self._load_env_vars()
    
    def _load_file(self, path: Path):
        try:
            with open(path, "r") as f:
                data = yaml.safe_load(f) if path.suffix in [".yaml", ".yml"] else json.load(f)
            if data:
                for key, value in data.items():
                    if hasattr(self.settings, key):
                        setattr(self.settings, key, value)
                        self._config_cache[key] = {"value": value, "source": str(path)}
        except Exception as e:
            print(f"Warning: Failed to load config from {path}: {e}")
    
    def _load_credentials(self):
        try:
            import keyring
            token = keyring.get_password("resilienceai", "auth_token")
            if token:
                self.settings.auth_token = token
        except ImportError:
            try:
                with open(self.credentials_path, "r") as f:
                    creds = json.load(f)
                    self.settings.auth_token = creds.get("auth_token")
            except Exception:
                pass
    
    def _load_env_vars(self):
        env_mappings = {
            "RESILIENCEAI_API_URL": "api_url",
            "RESILIENCEAI_API_TIMEOUT": "api_timeout",
            "RESILIENCEAI_LOG_LEVEL": "log_level",
            "RESILIENCEAI_AUTH_TOKEN": "auth_token",
        }
        for env_var, config_key in env_mappings.items():
            value = os.environ.get(env_var)
            if value:
                if config_key in ["api_timeout", "api_retries"]:
                    value = int(value)
                elif config_key in ["color_output", "auto_update_check"]:
                    value = value.lower() in ["true", "1", "yes"]
                setattr(self.settings, config_key, value)
                self._config_cache[config_key] = {"value": value, "source": f"env:{env_var}"}
    
    def get(self, key: str, default: Any = None) -> Any:
        return getattr(self.settings, key, default)
    
    def set(self, key: str, value: Any, global_: bool = False):
        setattr(self.settings, key, value)
        config_path = self.global_config_path if global_ else self.local_config_path
        self._save_to_file(config_path, key, value)
    
    def _save_to_file(self, path: Path, key: str, value: Any):
        config = yaml.safe_load(path.read_text()) if path.exists() else {}
        config[key] = value
        with open(path, "w") as f:
            yaml.dump(config, f, default_flow_style=False)
    
    def get_all(self, include_defaults: bool = False) -> Dict[str, Dict[str, Any]]:
        result = {}
        settings_dict = asdict(self.settings)
        for key, value in settings_dict.items():
            if key in self._config_cache:
                result[key] = self._config_cache[key]
            elif include_defaults:
                result[key] = {"value": value, "source": "default"}
        return result
    
    def reset(self, key: Optional[str] = None):
        if key:
            default_value = getattr(Settings(), key, None)
            setattr(self.settings, key, default_value)
        else:
            self.settings = Settings()
        for path in [self.global_config_path, self.local_config_path]:
            if path.exists():
                config = yaml.safe_load(path.read_text()) or {}
                if key and key in config:
                    del config[key]
                elif not key:
                    config = {}
                with open(path, "w") as f:
                    yaml.dump(config, f, default_flow_style=False)
    
    def validate(self) -> List[str]:
        errors = []
        if not self.settings.api_url.startswith(("http://", "https://")):
            errors.append(f"Invalid API URL: {self.settings.api_url}")
        for path_attr in ["models_dir", "data_dir", "cache_dir"]:
            path = Path(getattr(self.settings, path_attr)).expanduser()
            try:
                path.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                errors.append(f"Cannot create {path_attr}: {e}")
        return errors
    
    def is_authenticated(self) -> bool:
        return self.settings.auth_token is not None
    
    def save_credentials(self, token: str):
        self.settings.auth_token = token
        try:
            import keyring
            keyring.set_password("resilienceai", "auth_token", token)
        except ImportError:
            with open(self.credentials_path, "w") as f:
                json.dump({"auth_token": token}, f)
            os.chmod(self.credentials_path, 0o600)
    
    def clear_credentials(self):
        self.settings.auth_token = None
        self.settings.refresh_token = None
        try:
            import keyring
            keyring.delete_password("resilienceai", "auth_token")
        except:
            pass
        if self.credentials_path.exists():
            self.credentials_path.unlink()
    
    def get_config_path(self, global_: bool = False) -> Path:
        return self.global_config_path if global_ else self.local_config_path


@lru_cache()
def get_settings() -> ConfigManager:
    return ConfigManager()


settings = get_settings()
```

---

## 5. Output Formatting

### 5.1 Formatter Base Classes

**File:** `src/resilienceai/formatters/base.py`

```python
"""Base formatter interface"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from enum import Enum


class OutputFormat(str, Enum):
    TABLE = "table"
    JSON = "json"
    YAML = "yaml"
    CSV = "csv"
    TSV = "tsv"


class BaseFormatter(ABC):
    def __init__(self, console=None):
        self.console = console
    
    @abstractmethod
    def format(self, data: Any, **kwargs) -> str:
        pass
    
    @abstractmethod
    def print(self, data: Any, **kwargs):
        pass


class FormatterRegistry:
    _formatters: Dict[OutputFormat, type] = {}
    
    @classmethod
    def register(cls, format: OutputFormat, formatter_class: type):
        cls._formatters[format] = formatter_class
    
    @classmethod
    def get_formatter(cls, format: OutputFormat, console=None):
        if format not in cls._formatters:
            raise ValueError(f"Unknown format: {format}")
        return cls._formatters[format](console)
```

### 5.2 Table Formatter

**File:** `src/resilienceai/formatters/table.py`

```python
"""Table output formatter using Rich"""

from typing import Any, Dict, List, Optional
from rich.table import Table
from rich.box import ROUNDED

from .base import BaseFormatter


class TableFormatter(BaseFormatter):
    BOX_STYLES = {"rounded": ROUNDED, "simple": "simple", "heavy": "heavy"}
    
    def format(self, data: List[Dict[str, Any]], columns: Optional[List[str]] = None,
               headers: Optional[Dict[str, str]] = None, title: Optional[str] = None,
               box_style: str = "rounded", **kwargs) -> Table:
        if not data:
            return Table(title=title or "No Data")
        
        if columns is None:
            columns = list(data[0].keys())
        
        box = self.BOX_STYLES.get(box_style, ROUNDED)
        table = Table(title=title, box=box, show_header=True)
        
        for col in columns:
            header = headers.get(col, col.replace("_", " ").title()) if headers else col.replace("_", " ").title()
            table.add_column(header)
        
        for row in data:
            values = [str(row.get(col, "")) for col in columns]
            table.add_row(*values)
        
        return table
    
    def print(self, data: Any, **kwargs):
        table = self.format(data, **kwargs)
        self.console.print(table)
```

### 5.3 JSON Formatter

**File:** `src/resilienceai/formatters/json.py`

```python
"""JSON output formatter"""

import json
from typing import Any
from rich.syntax import Syntax

from .base import BaseFormatter


class JSONFormatter(BaseFormatter):
    def format(self, data: Any, indent: int = 2, sort_keys: bool = False,
               compact: bool = False, **kwargs) -> str:
        if compact:
            return json.dumps(data, separators=(',', ':'), sort_keys=sort_keys)
        return json.dumps(data, indent=indent, sort_keys=sort_keys, default=str)
    
    def print(self, data: Any, **kwargs):
        json_str = self.format(data, **kwargs)
        syntax = Syntax(json_str, "json", theme="monokai")
        self.console.print(syntax)
```

### 5.4 CSV Formatter

**File:** `src/resilienceai/formatters/csv.py`

```python
"""CSV/TSV output formatter"""

import csv
import io
from typing import Any, Dict, List, Optional

from .base import BaseFormatter


class CSVFormatter(BaseFormatter):
    def format(self, data: List[Dict[str, Any]], delimiter: str = ",",
               columns: Optional[List[str]] = None, include_header: bool = True, **kwargs) -> str:
        if not data:
            return ""
        
        if columns is None:
            columns = list(data[0].keys())
        
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=columns, delimiter=delimiter, extrasaction='ignore')
        
        if include_header:
            writer.writeheader()
        
        for row in data:
            string_row = {k: str(v) if v is not None else "" for k, v in row.items()}
            writer.writerow(string_row)
        
        return output.getvalue()
    
    def print(self, data: Any, **kwargs):
        output = self.format(data, **kwargs)
        self.console.print(output)


class TSVFormatter(CSVFormatter):
    def format(self, data: Any, **kwargs) -> str:
        kwargs["delimiter"] = "\t"
        return super().format(data, **kwargs)
```

---

## 6. Progress Indicators

### 6.1 Progress Utilities

**File:** `src/resilienceai/utils/progress.py`

```python
"""Progress indicator utilities"""

from typing import Optional, Callable, Any
from contextlib import contextmanager
from rich.progress import (
    Progress, SpinnerColumn, TextColumn, BarColumn,
    DownloadColumn, TransferSpeedColumn, TimeRemainingColumn,
    TimeElapsedColumn, MofNCompleteColumn
)
from rich.console import Console

from resilienceai.utils.console import get_console


def create_progress(description: str = "Working...", console: Optional[Console] = None,
                    transient: bool = False, **kwargs) -> Progress:
    if console is None:
        console = get_console()
    
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(complete_style="green", finished_style="green"),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console, transient=transient, **kwargs
    )


def create_download_progress(console: Optional[Console] = None, **kwargs) -> Progress:
    if console is None:
        console = get_console()
    
    return Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(binary_units=True),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console, **kwargs
    )


class ProgressTracker:
    def __init__(self, total_steps: int, description: str = "Processing", console: Optional[Console] = None):
        self.total_steps = total_steps
        self.current_step = 0
        self.description = description
        self.console = console or get_console()
        self.progress = None
        self.task = None
    
    def __enter__(self):
        self.progress = create_progress(console=self.console)
        self.progress.start()
        self.task = self.progress.add_task(self.description, total=self.total_steps)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.progress.stop()
    
    def advance(self, steps: int = 1, description: Optional[str] = None):
        self.current_step += steps
        if description:
            self.progress.update(self.task, description=description)
        self.progress.update(self.task, advance=steps)


@contextmanager
def task_progress(description: str, console: Optional[Console] = None,
                  success_message: Optional[str] = None, error_message: Optional[str] = None):
    if console is None:
        console = get_console()
    
    progress = create_progress(console=console, transient=True)
    task = progress.add_task(description, total=None)
    
    class TaskContext:
        def __init__(self):
            self.completed = False
        
        def success(self, message: Optional[str] = None):
            self.completed = True
            if message:
                console.print(f"[green]✓[/green] {message}")
        
        def error(self, message: Optional[str] = None):
            if message:
                console.print(f"[red]✗[/red] {message}")
    
    context = TaskContext()
    
    try:
        progress.start()
        yield context
        if not context.completed and success_message:
            context.success(success_message)
    except Exception as e:
        if error_message:
            context.error(f"{error_message}: {e}")
        raise
    finally:
        progress.stop()


def show_spinner(message: str, console: Optional[Console] = None):
    if console is None:
        console = get_console()
    from rich.status import Status
    return console.status(message, spinner="dots")
```

---

## 7. Interactive Prompts

### 7.1 Prompt Utilities

**File:** `src/resilienceai/utils/prompts.py`

```python
"""Interactive prompt utilities"""

from typing import Any, List, Optional, Dict
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich import box

from resilienceai.utils.console import get_console


class TableSelectionPrompt:
    def __init__(self, items: List[Dict[str, Any]], title: str = "Select an item",
                 key_column: str = "id", display_columns: Optional[List[str]] = None,
                 console: Optional[Console] = None):
        self.items = items
        self.title = title
        self.key_column = key_column
        self.display_columns = display_columns or (list(items[0].keys()) if items else [])
        self.console = console or get_console()
    
    def show(self) -> Optional[str]:
        if not self.items:
            self.console.print("[yellow]No items to select.[/yellow]")
            return None
        
        table = Table(title=self.title, box=box.ROUNDED)
        table.add_column("#", style="cyan", justify="right")
        for col in self.display_columns:
            table.add_column(col.replace("_", " ").title())
        
        for i, item in enumerate(self.items, 1):
            row_values = [str(item.get(col, "")) for col in self.display_columns]
            table.add_row(str(i), *row_values)
        
        self.console.print(table)
        
        choice = IntPrompt.ask("Enter number", console=self.console, show_default=False)
        
        if 1 <= choice <= len(self.items):
            return self.items[choice - 1].get(self.key_column)
        else:
            self.console.print("[red]Invalid selection.[/red]")
            return None


class FormPrompt:
    def __init__(self, fields: List[Dict[str, Any]], title: str = "Please fill in the form",
                 console: Optional[Console] = None):
        self.fields = fields
        self.title = title
        self.console = console or get_console()
        self.values = {}
    
    def show(self) -> Dict[str, Any]:
        self.console.print(Panel(self.title, style="blue"))
        
        for field in self.fields:
            name = field["name"]
            field_type = field.get("type", "str")
            label = field.get("label", name.replace("_", " ").title())
            default = field.get("default")
            required = field.get("required", True)
            
            while True:
                try:
                    if field_type == "str":
                        value = Prompt.ask(label, default=default, console=self.console)
                    elif field_type == "password":
                        value = Prompt.ask(label, password=True, console=self.console)
                    elif field_type == "int":
                        value = IntPrompt.ask(label, default=default, console=self.console)
                    elif field_type == "float":
                        value = FloatPrompt.ask(label, default=default, console=self.console)
                    elif field_type == "bool":
                        value = Confirm.ask(label, default=default or False, console=self.console)
                    else:
                        value = Prompt.ask(label, console=self.console)
                    
                    if required and not value:
                        self.console.print("[red]This field is required[/red]")
                        continue
                    
                    self.values[name] = value
                    break
                except Exception as e:
                    self.console.print(f"[red]Error: {e}[/red]")
        
        return self.values


def confirm(message: str, default: bool = False, console: Optional[Console] = None) -> bool:
    return Confirm.ask(message, default=default, console=console or get_console())


def ask(message: str, default: Optional[str] = None, password: bool = False,
        console: Optional[Console] = None) -> str:
    return Prompt.ask(message, default=default, password=password, console=console or get_console())


def select_from_table(items: List[Dict[str, Any]], title: str = "Select an item",
                      key_column: str = "id", console: Optional[Console] = None) -> Optional[str]:
    prompt = TableSelectionPrompt(items, title=title, key_column=key_column,
                                  console=console or get_console())
    return prompt.show()
```

---

## 8. Shell Completion

### 8.1 Completion Configuration

**File:** `src/resilienceai/core/completion.py`

```python
"""Shell completion support for ResilienceAI CLI"""

import os
import sys
from pathlib import Path
from typing import Optional


class ShellCompletion:
    SUPPORTED_SHELLS = ["bash", "zsh", "fish"]
    
    @classmethod
    def install(cls, shell: Optional[str] = None) -> str:
        if shell is None:
            shell = cls._detect_shell()
        
        if shell not in cls.SUPPORTED_SHELLS:
            return f"Unsupported shell: {shell}"
        
        if shell == "bash":
            return cls._install_bash()
        elif shell == "zsh":
            return cls._install_zsh()
        elif shell == "fish":
            return cls._install_fish()
        
        return "Unknown error"
    
    @classmethod
    def _detect_shell(cls) -> str:
        shell_path = os.environ.get("SHELL", "")
        return Path(shell_path).name if shell_path else "bash"
    
    @classmethod
    def _install_bash(cls) -> str:
        completion_script = '''
_resilience_ai_completion() {
    local IFS=$'\\n'
    local response
    response=$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$COMP_CWORD _RESILIENCE_AI_COMPLETE=complete_bash $1)
    for completion in $response; do
        COMPREPLY+=("$completion")
    done
}
complete -F _resilience_ai_completion -o default resilience-ai rai
'''
        completion_dir = Path.home() / ".bash_completion.d"
        completion_dir.mkdir(parents=True, exist_ok=True)
        completion_file = completion_dir / "resilience-ai"
        
        with open(completion_file, "w") as f:
            f.write(completion_script)
        
        return f"Bash completion installed to: {completion_file}"
    
    @classmethod
    def _install_zsh(cls) -> str:
        zsh_completion_dir = Path.home() / ".zsh/completions"
        zsh_completion_dir.mkdir(parents=True, exist_ok=True)
        completion_file = zsh_completion_dir / "_resilience-ai"
        
        completion_script = '''
#compdef resilience-ai rai
_resilience_ai_completion() {
    local -a completions
    local response
    response=("$(env COMP_WORDS="${COMP_WORDS[*]}" COMP_CWORD=$((CURRENT-1)) _RESILIENCE_AI_COMPLETE=complete_zsh resilience-ai)")
    compadd -a completions
}
compdef _resilience_ai_completion resilience-ai rai
'''
        with open(completion_file, "w") as f:
            f.write(completion_script)
        
        return f"Zsh completion installed to: {completion_file}"
    
    @classmethod
    def _install_fish(cls) -> str:
        fish_dir = Path.home() / ".config/fish/completions"
        fish_dir.mkdir(parents=True, exist_ok=True)
        completion_file = fish_dir / "resilience-ai.fish"
        
        with open(completion_file, "w") as f:
            f.write('complete -c resilience-ai -c rai -a "(env _RESILIENCE_AI_COMPLETE=complete_fish resilience-ai)"\n')
        
        return f"Fish completion installed to: {completion_file}"
```

---

## 9. Error Handling

### 9.1 Custom Exceptions

**File:** `src/resilienceai/core/exceptions.py`

```python
"""Custom exceptions for ResilienceAI CLI"""

from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel


class ResilienceAIError(Exception):
    exit_code = 1
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None,
                 suggestion: Optional[str] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
        self.suggestion = suggestion
    
    def format_error(self) -> str:
        text = f"[red bold]Error:[/red bold] {self.message}"
        if self.details:
            text += "\n\n[dim]Details:[/dim]"
            for key, value in self.details.items():
                text += f"\n  [cyan]{key}:[/cyan] {value}"
        if self.suggestion:
            text += f"\n\n[green]Suggestion:[/green] {self.suggestion}"
        return text
    
    def print_error(self, console: Optional[Console] = None):
        from resilienceai.utils.console import get_console
        if console is None:
            console = get_console()
        console.print(Panel(self.format_error(), title=f"Error (exit: {self.exit_code})",
                           border_style="red"))


class AuthenticationError(ResilienceAIError):
    exit_code = 2
    def __init__(self, message: str, **kwargs):
        super().__init__(message, suggestion="Run 'resilience-ai auth login' to authenticate.", **kwargs)


class ConfigurationError(ResilienceAIError):
    exit_code = 3
    def __init__(self, message: str, **kwargs):
        super().__init__(message, suggestion="Run 'resilience-ai config validate' to check config.", **kwargs)


class APIError(ResilienceAIError):
    exit_code = 4
    def __init__(self, message: str, status_code: Optional[int] = None, **kwargs):
        details = kwargs.pop("details", {})
        if status_code:
            details["status_code"] = status_code
        suggestion = kwargs.pop("suggestion", None)
        if status_code == 401:
            suggestion = "Session expired. Try 'resilience-ai auth token refresh'."
        elif status_code == 403:
            suggestion = "Permission denied."
        elif status_code == 404:
            suggestion = "Resource not found."
        elif status_code and status_code >= 500:
            suggestion = "Server error. Try again later."
        super().__init__(message, details=details, suggestion=suggestion, **kwargs)


class ModelError(ResilienceAIError):
    exit_code = 5


class SimulationError(ResilienceAIError):
    exit_code = 6


class ValidationError(ResilienceAIError):
    exit_code = 7


class NetworkError(ResilienceAIError):
    exit_code = 8
    def __init__(self, message: str, **kwargs):
        super().__init__(message, suggestion="Check internet connection and try again.", **kwargs)


class NotFoundError(ResilienceAIError):
    exit_code = 10
    def __init__(self, resource_type: str, resource_id: str, **kwargs):
        super().__init__(f"{resource_type} '{resource_id}' not found",
                        suggestion=f"Use 'resilience-ai {resource_type.lower()} list' to see resources.",
                        **kwargs)


def handle_errors(func):
    import functools
    import typer
    
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ResilienceAIError as e:
            e.print_error()
            raise typer.Exit(e.exit_code)
        except Exception as e:
            error = ResilienceAIError(str(e), suggestion="Unexpected error. Please report it.")
            error.print_error()
            raise typer.Exit(1)
    
    return wrapper
```

---

## 10. Logging System

### 10.1 Logging Configuration

**File:** `src/resilienceai/core/logging.py`

```python
"""Logging configuration for ResilienceAI CLI"""

import logging
import sys
from pathlib import Path
from typing import Optional
from rich.logging import RichHandler
from rich.console import Console

from resilienceai.core.config import settings


class CLIFormatter(logging.Formatter):
    FORMATS = {
        logging.DEBUG: "[dim]%(message)s[/dim]",
        logging.INFO: "%(message)s",
        logging.WARNING: "[yellow]%(message)s[/yellow]",
        logging.ERROR: "[red]%(message)s[/red]",
        logging.CRITICAL: "[red bold]%(message)s[/red bold]",
    }
    
    def format(self, record: logging.LogRecord) -> str:
        log_fmt = self.FORMATS.get(record.levelno, self.FORMATS[logging.INFO])
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logging(level: Optional[str] = None, log_file: Optional[str] = None,
                  console: Optional[Console] = None, use_rich: bool = True) -> logging.Logger:
    if level is None:
        level = settings.get("log_level", "INFO")
    
    numeric_level = getattr(logging, level.upper(), logging.INFO)
    logger = logging.getLogger("resilienceai")
    logger.setLevel(numeric_level)
    logger.handlers = []
    
    if use_rich and console is not None:
        console_handler = RichHandler(console=console, show_time=numeric_level <= logging.DEBUG,
                                      show_path=numeric_level <= logging.DEBUG, rich_tracebacks=True)
    else:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(CLIFormatter())
    
    console_handler.setLevel(numeric_level)
    logger.addHandler(console_handler)
    
    if log_file:
        log_path = Path(log_file).expanduser()
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_path)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    if name:
        return logging.getLogger(f"resilienceai.{name}")
    return logging.getLogger("resilienceai")


class VerbosityController:
    LEVELS = {0: "WARNING", 1: "INFO", 2: "DEBUG", 3: "DEBUG"}
    
    @classmethod
    def set_verbosity(cls, verbosity: int):
        level = cls.LEVELS.get(min(verbosity, 3), "DEBUG")
        logger = get_logger()
        logger.setLevel(getattr(logging, level))
        for handler in logger.handlers:
            handler.setLevel(getattr(logging, level))
        return level
```

---

## 11. Testing Strategy

### 11.1 Test Structure

**File:** `tests/conftest.py`

```python
"""Pytest configuration and fixtures"""

import pytest
from pathlib import Path
from unittest.mock import Mock
from typer.testing import CliRunner

from resilienceai.cli import app
from resilienceai.core.config import ConfigManager


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def cli_app():
    return app


@pytest.fixture
def mock_config(tmp_path):
    config = ConfigManager()
    config.global_config_path = tmp_path / "config.yaml"
    config.credentials_path = tmp_path / "credentials"
    return config


@pytest.fixture
def mock_client():
    client = Mock()
    client.get_user.return_value = {"email": "test@example.com"}
    return client


@pytest.fixture(autouse=True)
def reset_settings():
    from resilienceai.core.config import get_settings
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()
```

### 11.2 Unit Tests Example

**File:** `tests/unit/test_commands/test_auth.py`

```python
"""Tests for authentication commands"""

import pytest
from unittest.mock import Mock, patch
from typer.testing import CliRunner

from resilienceai.cli import app


class TestAuthCommands:
    def test_login_success(self, runner):
        with patch('resilienceai.commands.auth.ResilienceAIClient') as mock_class:
            mock_client = Mock()
            mock_client.get_user.return_value = {"email": "test@example.com"}
            mock_client.get_token.return_value = "test_token"
            mock_class.return_value = mock_client
            
            result = runner.invoke(app, ["auth", "login", "--username", "test@example.com", "--password", "pass"])
            
            assert result.exit_code == 0
            assert "Successfully authenticated" in result.output
    
    def test_login_failure(self, runner):
        from resilienceai.core.exceptions import AuthenticationError
        
        with patch('resilienceai.commands.auth.ResilienceAIClient') as mock_class:
            mock_client = Mock()
            mock_client.authenticate.side_effect = AuthenticationError("Invalid")
            mock_class.return_value = mock_client
            
            result = runner.invoke(app, ["auth", "login", "--username", "test", "--password", "wrong"])
            
            assert result.exit_code == 1
            assert "Authentication failed" in result.output
    
    def test_logout(self, runner):
        with patch('resilienceai.core.config.settings') as mock_settings:
            mock_settings.is_authenticated.return_value = True
            result = runner.invoke(app, ["auth", "logout"])
            assert result.exit_code == 0
            assert "logged out" in result.output
```

---

## 12. Distribution

### 12.1 Package Configuration

**File:** `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "resilienceai-cli"
version = "1.0.0"
description = "Command-line interface for ResilienceAI platform"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.8"
authors = [{name = "ResilienceAI Team", email = "support@resilience.ai"}]
keywords = ["cli", "resilience", "ai", "simulation", "analysis"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Environment :: Console",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
]
dependencies = [
    "typer>=0.9.0",
    "rich>=13.0.0",
    "httpx>=0.24.0",
    "pydantic>=2.0.0",
    "pyyaml>=6.0",
    "keyring>=24.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.0.0",
    "pytest-cov>=4.0.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.0.0",
]
docs = [
    "mkdocs>=1.5.0",
    "mkdocs-material>=9.0.0",
]

[project.scripts]
resilience-ai = "resilienceai.cli:app"
rai = "resilienceai.cli:app"

[project.urls]
Homepage = "https://resilience.ai"
Documentation = "https://docs.resilience.ai/cli"
Repository = "https://github.com/resilienceai/cli"

[tool.black]
line-length = 100
target-version = ["py38", "py39", "py310", "py311", "py312"]

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.8"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-v --cov=resilienceai --cov-report=term-missing"
```

### 12.2 Build and Publish Makefile

**File:** `Makefile`

```makefile
.PHONY: install install-dev test lint format clean build publish docs

install:
	pip install -e .

install-dev:
	pip install -e ".[dev,docs]"
	pre-commit install

test:
	pytest

test-cov:
	pytest --cov=resilienceai --cov-report=html

lint:
	ruff check src tests
	mypy src

format:
	black src tests
	ruff check --fix src tests

clean:
	rm -rf build dist *.egg-info .pytest_cache .coverage htmlcov
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

publish-test: build
	python -m twine upload --repository testpypi dist/*

publish: build
	python -m twine upload dist/*

docs:
	mkdocs serve

docs-deploy:
	mkdocs gh-deploy
```

---

## 13. Integration Guide

### 13.1 Installation

```bash
# Install from PyPI
pip install resilienceai-cli

# Install with shell completion
pip install resilienceai-cli
resilience-ai --install-completion

# Install from source
git clone https://github.com/resilienceai/cli.git
cd cli
pip install -e ".[dev]"
```

### 13.2 Configuration

```bash
# Set API endpoint
resilience-ai config set api_url https://api.resilience.ai/v1

# Set default output format
resilience-ai config set default_format json

# Configure logging
resilience-ai config set log_level DEBUG
```

### 13.3 Authentication

```bash
# Login with username/password
resilience-ai auth login --username user@example.com

# Login with API key
resilience-ai auth login --api-key <your-api-key>

# Check authentication status
resilience-ai auth status --detailed
```

### 13.4 CI/CD Integration

**GitHub Actions Example:**

```yaml
name: ResilienceAI Workflow

on: [push, pull_request]

jobs:
  simulation:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install CLI
        run: pip install resilienceai-cli
      
      - name: Configure CLI
        run: resilience-ai config set api_url ${{ secrets.RESILIENCEAI_API_URL }}
      
      - name: Authenticate
        run: resilience-ai auth login --api-key ${{ secrets.RESILIENCEAI_API_KEY }}
      
      - name: Run Simulation
        run: |
          SIM_ID=$(resilience-ai simulation run simulation.yaml --format json | jq -r '.id')
          echo "Simulation ID: $SIM_ID"
          resilience-ai simulation status $SIM_ID --watch
          resilience-ai analysis export $SIM_ID --output results.json
      
      - name: Upload Results
        uses: actions/upload-artifact@v3
        with:
          name: simulation-results
          path: results.json
```

---

## 14. Implementation Priority

### Phase 1: Core Infrastructure (Weeks 1-2)
1. **Project Setup**
   - Package structure
   - Dependencies
   - Build configuration

2. **Core Components**
   - Configuration management
   - Logging system
   - Error handling
   - Console utilities

3. **Basic Commands**
   - `auth login/logout/status`
   - `config get/set/list`
   - `system version/health`

### Phase 2: Essential Commands (Weeks 3-4)
1. **Model Management**
   - `model list/info`
   - `model pull/push`
   - `model validate`

2. **Simulation Commands**
   - `simulation run`
   - `simulation list/status`
   - `simulation logs`

3. **Output Formatting**
   - Table formatter
   - JSON formatter
   - CSV formatter

### Phase 3: Advanced Features (Weeks 5-6)
1. **Progress Indicators**
   - Download/upload progress
   - Multi-step operations

2. **Interactive Prompts**
   - Selection prompts
   - Form prompts
   - Wizard prompts

3. **Analysis Commands**
   - `analysis run`
   - `analysis export`
   - `analysis compare`

### Phase 4: Polish & Distribution (Weeks 7-8)
1. **Shell Completion**
   - Bash completion
   - Zsh completion
   - Fish completion

2. **Testing**
   - Unit tests
   - Integration tests
   - Documentation

3. **Distribution**
   - PyPI package
   - Documentation site
   - Release automation

---

## Appendix A: Quick Reference

### Command Summary

| Command | Description |
|---------|-------------|
| `rai auth login` | Authenticate with ResilienceAI |
| `rai config list` | List configuration |
| `rai model list` | List available models |
| `rai simulation run` | Run a simulation |
| `rai analysis export` | Export analysis results |
| `rai system doctor` | Run diagnostics |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `RESILIENCEAI_API_URL` | API endpoint URL |
| `RESILIENCEAI_AUTH_TOKEN` | Authentication token |
| `RESILIENCEAI_LOG_LEVEL` | Logging level |

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Authentication error |
| 3 | Configuration error |
| 4 | API error |
| 5 | Model error |
| 6 | Simulation error |
| 7 | Validation error |
| 8 | Network error |
| 9 | Timeout error |
| 10 | Not found error |

---

*Document Version: 1.0*
*Last Updated: 2024*
