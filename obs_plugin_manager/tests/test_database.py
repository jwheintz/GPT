"""Tests for the plugin database module."""

import pytest
import tempfile
import os
from pathlib import Path


class TestPluginDatabase:
    """Tests for PluginDatabase class."""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database for testing."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        from database import PluginDatabase
        
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = PluginDatabase(db_path)
        yield db
        
        # Cleanup
        os.unlink(db_path)
    
    def test_database_creation(self, temp_db):
        """Test that database is created with tables."""
        assert temp_db is not None
        assert Path(temp_db.db_path).exists()
    
    def test_default_plugins_populated(self, temp_db):
        """Test that default plugins are populated."""
        plugins = temp_db.get_all_plugins()
        assert len(plugins) > 0
    
    def test_get_popular_plugins(self, temp_db):
        """Test retrieving popular plugins."""
        plugins = temp_db.get_popular_plugins()
        assert all(p.is_popular for p in plugins)
    
    def test_get_recommended_plugins(self, temp_db):
        """Test retrieving recommended plugins."""
        plugins = temp_db.get_recommended_plugins()
        assert all(p.is_recommended for p in plugins)
    
    def test_search_plugins(self, temp_db):
        """Test plugin search."""
        results = temp_db.search_plugins("audio")
        assert len(results) > 0
        
        # Should find audio-related plugins
        names = [p.name.lower() for p in results]
        descriptions = [p.description.lower() for p in results]
        assert any('audio' in n or 'audio' in d for n, d in zip(names, descriptions))
    
    def test_get_plugin_by_id(self, temp_db):
        """Test retrieving specific plugin."""
        plugin = temp_db.get_plugin("obs-websocket")
        assert plugin is not None
        assert plugin.name == "OBS WebSocket"
    
    def test_get_plugins_by_category(self, temp_db):
        """Test filtering by category."""
        plugins = temp_db.get_plugins_by_category("audio")
        assert all(p.category == "audio" for p in plugins)
    
    def test_metadata(self, temp_db):
        """Test metadata storage."""
        temp_db.set_metadata("test_key", "test_value")
        value = temp_db.get_metadata("test_key")
        assert value == "test_value"
    
    def test_export_import_json(self, temp_db):
        """Test JSON export and import."""
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False, mode='w') as f:
            json_path = f.name
        
        try:
            # Export
            temp_db.export_catalog_to_json(json_path)
            assert Path(json_path).exists()
            
            # Import to new db
            with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
                db2_path = f.name
            
            from database import PluginDatabase
            db2 = PluginDatabase(db2_path)
            
            # Clear and reimport
            count = db2.import_catalog_from_json(json_path)
            assert count > 0
            
            os.unlink(db2_path)
        finally:
            os.unlink(json_path)


class TestPluginInfo:
    """Tests for PluginInfo dataclass."""
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        from database import PluginInfo
        
        plugin = PluginInfo(
            id="test-plugin",
            name="Test Plugin",
            description="A test plugin",
            author="Test Author",
            category="utility",
            latest_version="1.0.0",
            release_date="2024-01-01",
            download_url="https://example.com",
            github_url="https://github.com/test",
            homepage_url="https://example.com",
            dll_name="test.dll",
            additional_files="[]"
        )
        
        data = plugin.to_dict()
        
        assert data['id'] == "test-plugin"
        assert data['name'] == "Test Plugin"
        assert data['latest_version'] == "1.0.0"
    
    def test_from_dict(self):
        """Test creation from dictionary."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        from database import PluginInfo
        
        data = {
            'id': 'test-plugin',
            'name': 'Test Plugin',
            'description': 'A test',
            'author': 'Author',
            'category': 'utility',
            'latest_version': '2.0.0',
            'release_date': '2024-01-01',
            'download_url': 'https://example.com',
            'github_url': 'https://github.com/test',
            'homepage_url': 'https://example.com',
            'dll_name': 'test.dll',
            'additional_files': '[]',
            'is_popular': True,
            'is_recommended': False,
            'obs_min_version': '28.0.0',
            'obs_max_version': '',
            'added_date': '',
            'updated_date': ''
        }
        
        plugin = PluginInfo.from_dict(data)
        
        assert plugin.id == "test-plugin"
        assert plugin.latest_version == "2.0.0"
        assert plugin.is_popular is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
