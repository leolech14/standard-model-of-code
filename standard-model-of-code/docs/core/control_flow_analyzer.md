# Control Flow Analyzer

> **Mirror**: [`control_flow_analyzer.py`](../../../src/core/control_flow_analyzer.py)
> **Role**: Core Component

## Purpose
*(Auto-generated summary based on code structure)*

## Architecture
### Classes
- **`ControlFlowMetrics`**: No docstring

### Functions
- **`analyze_control_flow`**: Analyze control flow metrics for a parsed tree.
- **`calculate_cyclomatic_complexity`**: Calculate cyclomatic complexity (McCabe metric).
- **`calculate_cyclomatic_complexity.visit`**: No docstring
- **`calculate_nesting_depth`**: Calculate maximum nesting depth.
- **`calculate_nesting_depth.visit`**: No docstring
- **`_get_detailed_metrics`**: Get detailed control flow metrics.
- **`_get_detailed_metrics.visit`**: No docstring
- **`analyze_function_complexity`**: Analyze control flow metrics for a single function node.
- **`analyze_function_complexity.visit`**: No docstring
- **`get_complexity_rating`**: Get human-readable complexity rating.
- **`get_nesting_rating`**: Get human-readable nesting rating.
