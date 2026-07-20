"""
Main tools registry.
Import all your individual tool modules here and aggregate them.
"""

from .weather import WEATHER_TOOLS, WEATHER_FUNCTIONS
from .calculator import CALCULATOR_TOOLS, CALCULATOR_FUNCTIONS

# 1. Aggregate all tool schemas
TOOLS = []
TOOLS.extend(WEATHER_TOOLS)
TOOLS.extend(CALCULATOR_TOOLS)

# 2. Aggregate all tool implementations
AVAILABLE_FUNCTIONS = {}
AVAILABLE_FUNCTIONS.update(WEATHER_FUNCTIONS)
AVAILABLE_FUNCTIONS.update(CALCULATOR_FUNCTIONS)
