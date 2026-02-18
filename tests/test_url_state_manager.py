"""
Tests for URL State Manager

Run with: pytest tests/test_url_state_manager.py -v
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from urllib.parse import parse_qs
from state.url_state_manager import URLStateManager


def test_decode_missouri_gemini():
    """Test: ?focus_state=Missouri&selected_model=gemini-pro"""
    query_params = {
        'focus_state': 'Missouri',
        'selected_model': 'gemini-pro'
    }
    decoded = URLStateManager.decode_state(query_params)
    assert decoded['focus_state'] == 'Missouri'
    assert decoded['selected_model'] == 'gemini-pro'


def test_decode_texas_infra():
    """Test: ?focus_state=Texas&show_infra_gaps=true"""
    query_params = {
        'focus_state': 'Texas',
        'show_infra_gaps': 'true'
    }
    decoded = URLStateManager.decode_state(query_params)
    assert decoded['focus_state'] == 'Texas'
    assert decoded['show_infra_gaps'] == True


def test_fips_set_encoding():
    """Test FIPS set encoding and decoding"""
    mock_state = {
        'agent_config': {
            'focus_state': 'Missouri',
            'selected_model': 'gemini-pro',
            'reasoning_effort': 'Medium'
        },
        'query_highlighted_fips': {'29001', '29002', '29003'}
    }
    encoded = URLStateManager.encode_state(mock_state)
    
    # Parse back
    parsed = parse_qs(encoded)
    query_params = {k: v[0] for k, v in parsed.items()}
    decoded = URLStateManager.decode_state(query_params)
    
    assert decoded['query_highlighted_fips'] == {'29001', '29002', '29003'}


def test_boolean_parsing():
    """Test various boolean value formats"""
    # True values
    for val in ['true', 'True', '1', 'yes', 'on']:
        query_params = {'show_infra_gaps': val}
        decoded = URLStateManager.decode_state(query_params)
        assert decoded['show_infra_gaps'] == True, f'Failed for {val}'
    
    # False values
    for val in ['false', 'False', '0', 'no', 'off']:
        query_params = {'show_infra_gaps': val}
        decoded = URLStateManager.decode_state(query_params)
        assert decoded['show_infra_gaps'] == False, f'Failed for {val}'


def test_defaults_excluded():
    """Test that default values are excluded from URL"""
    mock_state = {
        'agent_config': {
            'focus_state': 'Missouri',  # default
            'selected_model': 'gemini-pro',  # default
            'reasoning_effort': 'Medium'  # default
        },
        'color_scale': 'viridis',  # default
        'query_highlighted_fips': set()  # empty
    }
    encoded = URLStateManager.encode_state(mock_state)
    assert encoded == '', 'Should be empty for all defaults'


def test_complex_state_encoding():
    """Test complex state with multiple parameters"""
    mock_state = {
        'agent_config': {
            'focus_state': 'Texas',
            'selected_model': 'nemotron-3-nano',
            'reasoning_effort': 'High'
        },
        'color_scale': 'plasma',
        'map_color': 'poverty_pct',
        'show_infra_gaps': False,
        'query_highlighted_fips': {'48001', '48002'}
    }
    encoded = URLStateManager.encode_state(mock_state)
    
    assert 'focus_state=Texas' in encoded
    assert 'selected_model=nemotron-3-nano' in encoded
    assert 'reasoning_effort=High' in encoded
    assert 'color_scale=plasma' in encoded
    assert 'map_color=poverty_pct' in encoded
    assert 'show_infra_gaps=false' in encoded
    assert '48001' in encoded and '48002' in encoded


def test_shareable_url():
    """Test shareable URL generation"""
    mock_state = {
        'agent_config': {
            'focus_state': 'Texas',
            'selected_model': 'gemini-pro',
            'reasoning_effort': 'Medium'
        },
        'color_scale': 'viridis',
    }
    url = URLStateManager.get_shareable_url(mock_state)
    assert url.startswith('?')
    assert 'focus_state=Texas' in url


def test_get_nested_value():
    """Test getting values from nested session state"""
    state = {
        'agent_config': {
            'focus_state': 'Missouri',
            'selected_model': 'gemini-pro'
        },
        'color_scale': 'plasma'
    }
    
    # From agent_config
    assert URLStateManager._get_nested_value(state, 'focus_state') == 'Missouri'
    assert URLStateManager._get_nested_value(state, 'selected_model') == 'gemini-pro'
    
    # From root
    assert URLStateManager._get_nested_value(state, 'color_scale') == 'plasma'
    
    # Non-existent
    assert URLStateManager._get_nested_value(state, 'nonexistent') is None


def test_set_nested_value():
    """Test setting values in nested session state"""
    state = {}
    
    # Should go to agent_config
    URLStateManager._set_nested_value(state, 'focus_state', 'Texas')
    assert state['agent_config']['focus_state'] == 'Texas'
    
    # Should go to root
    URLStateManager._set_nested_value(state, 'color_scale', 'cividis')
    assert state['color_scale'] == 'cividis'


if __name__ == '__main__':
    print("Running URL State Manager tests...")
    test_decode_missouri_gemini()
    print("PASS: test_decode_missouri_gemini")
    test_decode_texas_infra()
    print("PASS: test_decode_texas_infra")
    test_fips_set_encoding()
    print("PASS: test_fips_set_encoding")
    test_boolean_parsing()
    print("PASS: test_boolean_parsing")
    test_defaults_excluded()
    print("PASS: test_defaults_excluded")
    test_complex_state_encoding()
    print("PASS: test_complex_state_encoding")
    test_shareable_url()
    print("PASS: test_shareable_url")
    test_get_nested_value()
    print("PASS: test_get_nested_value")
    test_set_nested_value()
    print("PASS: test_set_nested_value")
    print("\n=== All tests passed! ===")
