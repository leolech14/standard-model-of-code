"""
Tests for Pipeline Package - BaseStage, PipelineManager, and stage orchestration.
"""
import pytest
import sys
import os
from unittest.mock import MagicMock
from typing import Optional

# Add src/core to path for imports (same pattern as other tests)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'core'))

from pipeline import BaseStage, PipelineManager


# =============================================================================
# TEST FIXTURES
# =============================================================================

class MockStage(BaseStage):
    """A mock stage for testing."""

    def __init__(self, name: str = "mock_stage", stage_number: Optional[int] = None):
        self._name = name
        self._stage_number = stage_number
        self.execute_called = False
        self.execute_count = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def stage_number(self) -> Optional[int]:
        return self._stage_number

    def execute(self, state):
        self.execute_called = True
        self.execute_count += 1
        return state


class FailingInputStage(BaseStage):
    """A stage that fails input validation."""

    @property
    def name(self) -> str:
        return "failing_input"

    def execute(self, state):
        return state

    def validate_input(self, state) -> bool:
        return False


class FailingOutputStage(BaseStage):
    """A stage that fails output validation."""

    @property
    def name(self) -> str:
        return "failing_output"

    def execute(self, state):
        return state

    def validate_output(self, state) -> bool:
        return False


# =============================================================================
# BASESTAGE TESTS
# =============================================================================

class TestBaseStage:
    """Tests for BaseStage abstract class."""

    def test_mock_stage_has_name(self):
        stage = MockStage("test_name")
        assert stage.name == "test_name"

    def test_mock_stage_default_stage_number(self):
        stage = MockStage()
        assert stage.stage_number is None

    def test_mock_stage_with_stage_number(self):
        stage = MockStage("numbered", stage_number=5)
        assert stage.stage_number == 5

    def test_default_validate_input_returns_true(self):
        stage = MockStage()
        # validate_input should return True by default
        assert stage.validate_input(None) is True

    def test_default_validate_output_returns_true(self):
        stage = MockStage()
        # validate_output should return True by default
        assert stage.validate_output(None) is True

    def test_repr_without_stage_number(self):
        stage = MockStage("test_stage")
        repr_str = repr(stage)
        assert "MockStage" in repr_str
        assert "test_stage" in repr_str

    def test_repr_with_stage_number(self):
        stage = MockStage("test_stage", stage_number=3)
        repr_str = repr(stage)
        assert "MockStage" in repr_str
        assert "stage=3" in repr_str
        assert "test_stage" in repr_str


# =============================================================================
# PIPELINEMANAGER TESTS
# =============================================================================

class TestPipelineManager:
    """Tests for PipelineManager."""

    def test_empty_pipeline(self):
        manager = PipelineManager([])
        assert manager.list_stages() == []

    def test_pipeline_with_stages(self):
        stages = [MockStage("stage1"), MockStage("stage2")]
        manager = PipelineManager(stages)
        assert manager.list_stages() == ["stage1", "stage2"]

    def test_run_executes_all_stages(self):
        stage1 = MockStage("stage1")
        stage2 = MockStage("stage2")
        manager = PipelineManager([stage1, stage2])

        mock_state = MagicMock()
        manager.run(mock_state)

        assert stage1.execute_called
        assert stage2.execute_called

    def test_run_preserves_state_chain(self):
        """Each stage should receive the output of the previous stage."""
        stage1 = MockStage("stage1")
        stage2 = MockStage("stage2")
        manager = PipelineManager([stage1, stage2])

        mock_state = MagicMock()
        result = manager.run(mock_state)

        # Result should be the same object (stages don't create new states)
        assert result is mock_state

    def test_run_skips_failed_input_validation(self, capsys):
        """Stages that fail input validation should be skipped."""
        failing_stage = FailingInputStage()
        manager = PipelineManager([failing_stage])

        mock_state = MagicMock()
        manager.run(mock_state)

        # Check warning was printed
        captured = capsys.readouterr()
        assert "input validation failed" in captured.out

    def test_run_warns_on_failed_output_validation(self, capsys):
        """Stages that fail output validation should print a warning."""
        failing_stage = FailingOutputStage()
        manager = PipelineManager([failing_stage])

        mock_state = MagicMock()
        manager.run(mock_state)

        # Check warning was printed
        captured = capsys.readouterr()
        assert "output validation failed" in captured.out

    def test_run_stage_by_name(self):
        stage1 = MockStage("stage1")
        stage2 = MockStage("stage2")
        manager = PipelineManager([stage1, stage2])

        mock_state = MagicMock()
        manager.run_stage("stage2", mock_state)

        assert not stage1.execute_called
        assert stage2.execute_called

    def test_run_stage_not_found(self):
        manager = PipelineManager([MockStage("stage1")])
        with pytest.raises(ValueError, match="Stage not found"):
            manager.run_stage("nonexistent", MagicMock())

    def test_callbacks_are_called(self):
        """Test that stage callbacks are invoked."""
        stage = MockStage("test")
        started = []
        completed = []

        def on_start(s):
            started.append(s.name)

        def on_complete(s, duration_ms):
            completed.append((s.name, duration_ms))

        manager = PipelineManager(
            [stage],
            on_stage_start=on_start,
            on_stage_complete=on_complete,
        )

        manager.run(MagicMock())

        assert started == ["test"]
        assert len(completed) == 1
        assert completed[0][0] == "test"
        assert isinstance(completed[0][1], float)

    def test_repr(self):
        manager = PipelineManager([MockStage("a"), MockStage("b")])
        repr_str = repr(manager)
        assert "PipelineManager" in repr_str
        assert "stages=2" in repr_str


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestPipelineIntegration:
    """Integration tests for the full pipeline flow."""

    def test_stage_execution_order(self):
        """Verify stages execute in the order they were added."""
        execution_order = []

        class OrderTrackingStage(BaseStage):
            def __init__(self, name: str, order_list: list):
                self._name = name
                self._order_list = order_list

            @property
            def name(self) -> str:
                return self._name

            def execute(self, state):
                self._order_list.append(self._name)
                return state

        stages = [
            OrderTrackingStage("first", execution_order),
            OrderTrackingStage("second", execution_order),
            OrderTrackingStage("third", execution_order),
        ]

        manager = PipelineManager(stages)
        manager.run(MagicMock())

        assert execution_order == ["first", "second", "third"]

    def test_stage_can_modify_state(self):
        """Verify a stage can mutate the state object."""

        class EnrichingStage(BaseStage):
            @property
            def name(self) -> str:
                return "enricher"

            def execute(self, state):
                state.metadata["enriched"] = True
                return state

        manager = PipelineManager([EnrichingStage()])

        # Create a mock state with metadata dict
        mock_state = MagicMock()
        mock_state.metadata = {}

        manager.run(mock_state)

        assert mock_state.metadata.get("enriched") is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
