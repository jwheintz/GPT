class ObsPluginManagerError(Exception):
    """Base error for obs-plugin-manager."""


class ObsRunningError(ObsPluginManagerError):
    """Raised when an operation would write to OBS while OBS is running."""


class CatalogError(ObsPluginManagerError):
    """Catalog/database errors."""


class InstallError(ObsPluginManagerError):
    """Installation/update/rollback errors."""
