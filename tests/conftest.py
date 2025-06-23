"""
Pytest configuration and fixtures for contact reconciliation tests.
"""

import pytest
import sys
import os

# Add the app directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

# Set environment variables for testing
os.environ["TESTING"] = "true"
