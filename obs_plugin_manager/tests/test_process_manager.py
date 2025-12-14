"""Tests for the process manager module."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestProcessManager:
    """Tests for ProcessManager class."""
    
    @pytest.fixture
    def process_manager(self):
        """Create ProcessManager instance."""
        from process_manager import ProcessManager
        return ProcessManager()
    
    def test_is_obs_running(self, process_manager):
        """Test OBS running check."""
        # This should return a boolean
        result = process_manager.is_obs_running()
        assert isinstance(result, bool)
    
    def test_get_obs_process(self, process_manager):
        """Test getting OBS process info."""
        # Should return None or OBSProcess
        result = process_manager.get_obs_process()
        
        if result is not None:
            assert hasattr(result, 'pid')
            assert hasattr(result, 'name')
    
    def test_get_process_info(self, process_manager):
        """Test getting process info dict."""
        info = process_manager.get_process_info()
        
        assert 'running' in info
        assert 'message' in info
        assert isinstance(info['running'], bool)
    
    def test_require_obs_not_running_when_not_running(self, process_manager):
        """Test require_obs_not_running when OBS is not running."""
        if not process_manager.is_obs_running():
            # Should not raise
            result = process_manager.require_obs_not_running()
            assert result is True
    
    def test_require_obs_not_running_when_running(self, process_manager):
        """Test require_obs_not_running raises when OBS is running."""
        if process_manager.is_obs_running():
            with pytest.raises(RuntimeError):
                process_manager.require_obs_not_running()


class TestOBSProcess:
    """Tests for OBSProcess dataclass."""
    
    def test_obs_process_creation(self):
        """Test creating OBSProcess instance."""
        from process_manager import OBSProcess
        
        process = OBSProcess(
            pid=1234,
            name="obs64.exe",
            exe_path="C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe",
            create_time=1700000000.0,
            status="running",
            memory_mb=500.0,
            cpu_percent=5.0
        )
        
        assert process.pid == 1234
        assert process.name == "obs64.exe"
        assert process.memory_mb == 500.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
