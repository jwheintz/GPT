# Contributing to OBS Plugin Manager

Thank you for your interest in contributing to OBS Plugin Manager! This document provides guidelines and information for contributors.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Your environment (Windows version, Python version, OBS version)
- Any error messages or logs

### Suggesting Features

We welcome feature suggestions! Please:
- Check if the feature has already been requested
- Clearly describe the feature and its use case
- Explain how it would benefit users
- Consider if it aligns with the project's goals

### Adding Plugins to the Catalog

To add a new plugin to the built-in catalog:

1. **Verify the plugin**:
   - Must be publicly available
   - Should be stable and actively maintained
   - Must work with current OBS versions
   - Should have a clear installation method

2. **Required information**:
   ```python
   {
       "name": "plugin-identifier",
       "display_name": "Plugin Display Name",
       "description": "Clear description of what the plugin does",
       "author": "Author Name",
       "category": "Category",  # Integration, Effects, Sources, Output, Audio, Automation, Transitions
       "homepage_url": "https://github.com/...",
       "download_url": "https://github.com/.../releases/latest",
       "is_recommended": False  # True only for widely-used, stable plugins
   }
   ```

3. **Add to `plugin_repository.py`**:
   - Add the plugin entry to the `POPULAR_PLUGINS` list
   - Follow the existing format
   - Ensure URLs are correct and accessible

4. **Test the plugin**:
   - Install it using the manager
   - Verify it appears correctly
   - Test version detection if possible

### Code Contributions

#### Setting Up Development Environment

1. Fork the repository
2. Clone your fork:
   ```bash
   git clone https://github.com/your-username/obs-plugin-manager.git
   cd obs-plugin-manager
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

#### Code Style Guidelines

- **Python Version**: Target Python 3.8+
- **Formatting**: Follow PEP 8 style guide
- **Documentation**: Use docstrings for all functions and classes
- **Type Hints**: Use type hints where appropriate
- **Comments**: Explain why, not what (code should be self-explanatory)

#### Code Structure

The project is organized into modules:

- `database.py` - SQLite database management
- `obs_manager.py` - OBS process and installation detection
- `plugin_scanner.py` - Plugin detection and version extraction
- `plugin_repository.py` - Plugin catalog and update checking
- `plugin_installer.py` - Download, install, backup, and rollback
- `gui.py` - Tkinter GUI application

#### Making Changes

1. **Keep changes focused**: One feature or fix per PR
2. **Test thoroughly**: Test on Windows with OBS installed
3. **Update documentation**: Update README if behavior changes
4. **Follow existing patterns**: Match the style of existing code

#### Testing Checklist

Before submitting:
- [ ] Code runs without errors
- [ ] OBS detection works
- [ ] Plugin scanning works
- [ ] Installation/removal works
- [ ] Rollback functionality works
- [ ] GUI updates correctly
- [ ] No crashes or exceptions
- [ ] Tested with OBS running and not running

### Submitting Changes

1. **Commit your changes**:
   ```bash
   git add .
   git commit -m "Description of changes"
   ```

2. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

3. **Create a Pull Request**:
   - Provide clear description of changes
   - Reference any related issues
   - Explain testing performed
   - Include screenshots for UI changes

## Development Guidelines

### Adding New Features

When adding features:
1. Consider user experience
2. Maintain safety features (OBS status checking)
3. Handle errors gracefully
4. Provide user feedback (status messages, dialogs)
5. Update documentation

### Error Handling

- Always catch specific exceptions
- Log errors appropriately
- Show user-friendly error messages
- Never crash silently

### Database Changes

If modifying the database schema:
1. Consider backward compatibility
2. Provide migration if needed
3. Update database version
4. Test with existing databases

### GUI Changes

When modifying the GUI:
1. Maintain consistent style
2. Ensure responsive layout
3. Test window resizing
4. Consider accessibility
5. Provide tooltips for complex features

## Code Review Process

1. **Automated checks**: Code will be reviewed for style and basic functionality
2. **Manual review**: Maintainers will review design and implementation
3. **Testing**: Changes should be tested on Windows
4. **Feedback**: Address review comments promptly
5. **Approval**: At least one maintainer approval required

## Areas for Contribution

### High Priority
- Plugin compatibility database
- Better version detection algorithms
- Support for more plugin repositories
- Improved error handling and logging
- Performance optimizations

### Medium Priority
- Plugin dependency management
- Configuration management
- Scheduled updates
- Plugin conflict detection
- Import/export plugin lists

### Low Priority
- Alternative UI themes
- Command-line interface
- Plugin usage statistics
- Automated testing suite

## Plugin Repository Standards

### Recommended Plugins

A plugin should be marked as "recommended" only if:
- Widely used in the OBS community
- Stable and well-maintained
- Active development or complete
- Clear documentation
- No major known issues

### Plugin Categories

Current categories:
- **Integration**: External service integrations (WebSocket, MIDI, etc.)
- **Effects**: Visual effects and filters
- **Sources**: New source types
- **Output**: Streaming/recording outputs
- **Audio**: Audio processing and effects
- **Automation**: Automated scene switching, etc.
- **Transitions**: Scene transitions

### Version Detection

When adding plugins, note:
- Version detection works best with standard Windows DLL version info
- GitHub releases should have clear version tags (v1.2.3 format)
- Download URLs should point to stable releases

## Documentation

### Code Documentation

Use clear docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When this exception occurs
    """
    pass
```

### User Documentation

When adding features:
- Update README.md with feature description
- Update GETTING_STARTED.md with usage instructions
- Add troubleshooting info if applicable
- Include examples where helpful

## Community

### Communication

- Be respectful and constructive
- Help others when possible
- Share knowledge and experiences
- Report issues promptly

### Recognition

Contributors will be recognized in:
- README.md contributors section
- Release notes for significant contributions
- Project documentation

## License

By contributing, you agree that your contributions will be licensed under the same terms as the project.

## Questions?

If you have questions about contributing:
1. Check existing documentation
2. Look through issues for similar questions
3. Create a new issue with your question

---

Thank you for helping make OBS Plugin Manager better!
