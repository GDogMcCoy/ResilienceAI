"""
ResilienceAI - URL State Manager

Synchronizes session state with URL query parameters to enable
bookmarking and sharing of specific analysis views.
"""

import streamlit as st
from urllib.parse import urlencode, parse_qs
from typing import Dict, Any, Set, Optional, List, Union
import json


class URLStateManager:
    """
    Synchronizes session state with URL query parameters.
    
    This enables users to bookmark and share specific analysis views
    by encoding relevant state into URL query parameters.
    
    Example URLs:
        - ?focus_state=Missouri&selected_model=gemini-pro
        - ?focus_state=Texas&show_infra_gaps=true&map_color=risk_score
    """
    
    # Keys that should be persisted to/from URL
    # Format: (state_key, default_value, encode_type)
    PERSISTENT_CONFIG = {
        # Focus state (e.g., "Missouri", "Texas")
        'focus_state': {'default': 'Missouri', 'type': 'string'},
        # Selected LLM model
        'selected_model': {'default': 'gemini-pro', 'type': 'string'},
        # Color scale for accessibility (global color scheme)
        'color_scale': {'default': 'viridis', 'type': 'string'},
        # Map color column (which metric to color the map by)
        'map_color': {'default': 'risk_score', 'type': 'string'},
        # Reasoning effort level
        'reasoning_effort': {'default': 'Medium', 'type': 'string'},
        # Show infrastructure gaps overlay
        'show_infra_gaps': {'default': True, 'type': 'bool'},
        # Query-highlighted FIPS codes (comma-separated)
        'query_highlighted_fips': {'default': '', 'type': 'set'},
    }
    
    @staticmethod
    def _get_nested_value(state: Dict, key: str) -> Any:
        """Get value from session state, checking both root and agent_config."""
        # Check root session state first
        if key in state:
            return state[key]
        # Check agent_config for nested keys
        if 'agent_config' in state and key in state['agent_config']:
            return state['agent_config'][key]
        return None
    
    @staticmethod
    def _set_nested_value(state: Dict, key: str, value: Any) -> None:
        """Set value in session state, checking both root and agent_config."""
        # Check if key belongs in agent_config
        if key in ['focus_state', 'selected_model', 'reasoning_effort', 'lm_url', 'lm_key', 'gemini_key']:
            if 'agent_config' not in state:
                state['agent_config'] = {}
            state['agent_config'][key] = value
        else:
            state[key] = value
    
    @staticmethod
    def _encode_value(value: Any, encode_type: str) -> str:
        """Encode a value to string based on its type."""
        if value is None:
            return ''
        
        if encode_type == 'set':
            if isinstance(value, (set, list, tuple)):
                # Filter out empty values and join with comma
                items = [str(v) for v in value if v]
                return ','.join(items) if items else ''
            elif isinstance(value, str):
                return value
            else:
                return str(value) if value else ''
        
        elif encode_type == 'bool':
            if isinstance(value, bool):
                return 'true' if value else 'false'
            elif isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'on')
            else:
                return 'true' if value else 'false'
        
        elif encode_type == 'string':
            return str(value) if value else ''
        
        else:
            return str(value) if value else ''
    
    @staticmethod
    def _decode_value(value: str, encode_type: str) -> Any:
        """Decode a string value based on its type."""
        if not value:
            return None
        
        if encode_type == 'set':
            if not value:
                return set()
            # Split by comma and filter empty strings
            items = [v.strip() for v in value.split(',') if v.strip()]
            return set(items)
        
        elif encode_type == 'bool':
            return value.lower() in ('true', '1', 'yes', 'on')
        
        elif encode_type == 'string':
            return value
        
        else:
            return value
    
    @classmethod
    def encode_state(cls, state: Optional[Dict] = None) -> str:
        """
        Encode relevant state to URL query string.
        
        Args:
            state: Session state dictionary (defaults to st.session_state)
            
        Returns:
            URL-encoded query string
        """
        if state is None:
            state = st.session_state
        
        params = {}
        
        for key, config in cls.PERSISTENT_CONFIG.items():
            value = cls._get_nested_value(state, key)
            
            # Skip None values
            if value is None:
                continue
            
            # Skip default values to keep URL clean
            default = config['default']
            encode_type = config['type']
            
            encoded = cls._encode_value(value, encode_type)
            
            # Don't include empty strings or default values
            if encoded and encoded != cls._encode_value(default, encode_type):
                params[key] = encoded
        
        return urlencode(params) if params else ''
    
    @classmethod
    def decode_state(cls, query_params: Dict[str, Union[str, List[str]]]) -> Dict[str, Any]:
        """
        Decode URL query params to state dictionary.
        
        Args:
            query_params: Query parameters from st.query_params
            
        Returns:
            Dictionary of decoded state values
        """
        decoded = {}
        
        for key, config in cls.PERSISTENT_CONFIG.items():
            if key not in query_params:
                continue
            
            raw_value = query_params[key]
            
            # Handle both single values and lists
            if isinstance(raw_value, list):
                if not raw_value:
                    continue
                raw_value = raw_value[0]
            
            if not raw_value:
                continue
            
            encode_type = config['type']
            decoded[key] = cls._decode_value(str(raw_value), encode_type)
        
        return decoded
    
    @classmethod
    def sync_from_url(cls) -> Dict[str, Any]:
        """
        Read state from URL on page load and apply to session state.
        
        Returns:
            Dictionary of applied state changes
        """
        try:
            # Get query params from Streamlit
            query_params = st.query_params
            
            if not query_params:
                return {}
            
            # Decode params
            decoded = cls.decode_state(query_params)
            
            if not decoded:
                return {}
            
            # Apply to session state
            applied = {}
            for key, value in decoded.items():
                if value is not None:
                    cls._set_nested_value(st.session_state, key, value)
                    applied[key] = value
            
            return applied
            
        except Exception as e:
            # Silently fail on errors to maintain backward compatibility
            return {}
    
    @classmethod
    def sync_to_url(cls, state: Optional[Dict] = None) -> None:
        """
        Push current state to URL bar.
        
        Args:
            state: Session state dictionary (defaults to st.session_state)
        """
        try:
            query_string = cls.encode_state(state)
            
            # Parse the query string back to dict for st.query_params
            if query_string:
                params = parse_qs(query_string)
                # Convert single-item lists to strings for Streamlit
                params = {k: v[0] if len(v) == 1 else v for k, v in params.items()}
            else:
                params = {}
            
            # Update query params (this updates the URL without page reload)
            st.query_params.update(params)
            
        except Exception as e:
            # Silently fail on errors to maintain backward compatibility
            pass
    
    @classmethod
    def get_shareable_url(cls, state: Optional[Dict] = None) -> str:
        """
        Generate a shareable URL with current state encoded.
        
        Args:
            state: Session state dictionary (defaults to st.session_state)
            
        Returns:
            Full URL with encoded state
        """
        query_string = cls.encode_state(state)
        
        # Get the base URL from the current page
        # Note: In Streamlit, we can't easily get the full URL,
        # so we return just the query string portion
        return f"?{query_string}" if query_string else ""
    
    @classmethod
    def clear_url_params(cls) -> None:
        """Clear all URL query parameters."""
        try:
            st.query_params.clear()
        except Exception:
            pass
