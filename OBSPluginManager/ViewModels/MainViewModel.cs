using System;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Linq;
using System.Runtime.CompilerServices;
using System.Threading.Tasks;
using System.Windows.Input;
using OBSPluginManager.Models;
using OBSPluginManager.Services;

namespace OBSPluginManager.ViewModels
{
    public class MainViewModel : INotifyPropertyChanged
    {
        private readonly OBSProcessManager _processManager;
        private readonly PluginDatabase _database;
        private readonly PluginScanner _scanner;
        private readonly VersionComparer _versionComparer;
        private readonly PluginInstaller _installer;

        private string _statusMessage = "Ready";
        private bool _isOBSRunning;
        private bool _isScanning;
        private InstalledPlugin? _selectedInstalledPlugin;
        private Plugin? _selectedCatalogPlugin;

        public MainViewModel()
        {
            _processManager = new OBSProcessManager();
            _database = new PluginDatabase();
            _scanner = new PluginScanner(_processManager);
            _versionComparer = new VersionComparer();
            _installer = new PluginInstaller(_processManager);

            // Seed initial data if database is empty
            var seeder = new PluginCatalogSeeder(_database);
            if (_database.GetAllPlugins().Count == 0)
            {
                seeder.SeedInitialData();
            }

            InstalledPlugins = new ObservableCollection<InstalledPlugin>();
            CatalogPlugins = new ObservableCollection<Plugin>();
            SuggestedPlugins = new ObservableCollection<Plugin>();

            RefreshOBSStatusCommand = new RelayCommand(_ => RefreshOBSStatus());
            KillOBSCommand = new RelayCommand(_ => KillOBS(), _ => IsOBSRunning);
            ScanPluginsCommand = new RelayCommand(async _ => await ScanPlugins(), _ => !IsScanning);
            RefreshCatalogCommand = new RelayCommand(async _ => await RefreshCatalog());
            InstallPluginCommand = new RelayCommand(async _ => await InstallSelectedPlugin(), _ => SelectedCatalogPlugin != null && !IsOBSRunning);
            UpdatePluginCommand = new RelayCommand(async _ => await UpdateSelectedPlugin(), _ => SelectedInstalledPlugin != null && SelectedInstalledPlugin.HasUpdate && !IsOBSRunning);
            RollbackPluginCommand = new RelayCommand(async _ => await RollbackSelectedPlugin(), _ => SelectedInstalledPlugin != null && !IsOBSRunning);

            // Initial load
            RefreshOBSStatus();
            LoadCatalog();
        }

        public ObservableCollection<InstalledPlugin> InstalledPlugins { get; }
        public ObservableCollection<Plugin> CatalogPlugins { get; }
        public ObservableCollection<Plugin> SuggestedPlugins { get; }

        public string StatusMessage
        {
            get => _statusMessage;
            set { _statusMessage = value; OnPropertyChanged(); }
        }

        public bool IsOBSRunning
        {
            get => _isOBSRunning;
            set { _isOBSRunning = value; OnPropertyChanged(); OnPropertyChanged(nameof(OBSStatusText)); }
        }

        public string OBSStatusText => IsOBSRunning ? "OBS is Running" : "OBS is Not Running";

        public bool IsScanning
        {
            get => _isScanning;
            set { _isScanning = value; OnPropertyChanged(); }
        }

        public InstalledPlugin? SelectedInstalledPlugin
        {
            get => _selectedInstalledPlugin;
            set { _selectedInstalledPlugin = value; OnPropertyChanged(); }
        }

        public Plugin? SelectedCatalogPlugin
        {
            get => _selectedCatalogPlugin;
            set { _selectedCatalogPlugin = value; OnPropertyChanged(); }
        }

        public ICommand RefreshOBSStatusCommand { get; }
        public ICommand KillOBSCommand { get; }
        public ICommand ScanPluginsCommand { get; }
        public ICommand RefreshCatalogCommand { get; }
        public ICommand InstallPluginCommand { get; }
        public ICommand UpdatePluginCommand { get; }
        public ICommand RollbackPluginCommand { get; }

        public void RefreshOBSStatus()
        {
            IsOBSRunning = _processManager.IsOBSRunning();
            StatusMessage = IsOBSRunning ? "OBS is currently running" : "OBS is not running";
        }

        public void KillOBS()
        {
            if (_processManager.KillOBS())
            {
                RefreshOBSStatus();
                StatusMessage = "OBS has been closed";
            }
            else
            {
                StatusMessage = "Failed to close OBS";
            }
        }

        public async Task ScanPlugins()
        {
            IsScanning = true;
            StatusMessage = "Scanning for installed plugins...";

            try
            {
                await Task.Run(() =>
                {
                    var plugins = _scanner.ScanInstalledPlugins();
                    
                    System.Windows.Application.Current.Dispatcher.Invoke(() =>
                    {
                        InstalledPlugins.Clear();
                        foreach (var plugin in plugins)
                        {
                            // Check for updates
                            var catalogPlugin = _database.GetPluginByName(plugin.Name);
                            if (catalogPlugin != null)
                            {
                                plugin.HasUpdate = _versionComparer.IsNewer(catalogPlugin.LatestVersion, plugin.Version);
                                plugin.LatestVersion = catalogPlugin.LatestVersion;
                            }

                            InstalledPlugins.Add(plugin);
                        }

                        StatusMessage = $"Found {plugins.Count} installed plugin(s)";
                    });
                });
            }
            catch (Exception ex)
            {
                StatusMessage = $"Error scanning plugins: {ex.Message}";
            }
            finally
            {
                IsScanning = false;
            }
        }

        public async Task RefreshCatalog()
        {
            StatusMessage = "Refreshing plugin catalog...";
            try
            {
                // In a real implementation, this would fetch from BarRaider API or other sources
                // For now, we'll just reload from database
                await Task.Run(() =>
                {
                    var plugins = _database.GetAllPlugins();
                    var suggested = _database.GetSuggestedPlugins();

                    System.Windows.Application.Current.Dispatcher.Invoke(() =>
                    {
                        CatalogPlugins.Clear();
                        SuggestedPlugins.Clear();

                        foreach (var plugin in plugins)
                        {
                            CatalogPlugins.Add(plugin);
                        }

                        foreach (var plugin in suggested)
                        {
                            SuggestedPlugins.Add(plugin);
                        }

                        StatusMessage = $"Catalog refreshed: {plugins.Count} plugin(s) available";
                    });
                });
            }
            catch (Exception ex)
            {
                StatusMessage = $"Error refreshing catalog: {ex.Message}";
            }
        }

        public async Task InstallSelectedPlugin()
        {
            if (SelectedCatalogPlugin == null) return;

            StatusMessage = $"Installing {SelectedCatalogPlugin.Name}...";
            try
            {
                var existing = InstalledPlugins.FirstOrDefault(p => p.Name == SelectedCatalogPlugin.Name);
                await _installer.InstallPlugin(SelectedCatalogPlugin, existing);
                
                StatusMessage = $"{SelectedCatalogPlugin.Name} installed successfully";
                await ScanPlugins(); // Refresh installed plugins
            }
            catch (Exception ex)
            {
                StatusMessage = $"Error installing plugin: {ex.Message}";
            }
        }

        public async Task UpdateSelectedPlugin()
        {
            if (SelectedInstalledPlugin == null) return;

            var catalogPlugin = _database.GetPluginByName(SelectedInstalledPlugin.Name);
            if (catalogPlugin == null)
            {
                StatusMessage = $"Plugin {SelectedInstalledPlugin.Name} not found in catalog";
                return;
            }

            StatusMessage = $"Updating {SelectedInstalledPlugin.Name}...";
            try
            {
                await _installer.InstallPlugin(catalogPlugin, SelectedInstalledPlugin);
                StatusMessage = $"{SelectedInstalledPlugin.Name} updated successfully";
                await ScanPlugins(); // Refresh installed plugins
            }
            catch (Exception ex)
            {
                StatusMessage = $"Error updating plugin: {ex.Message}";
            }
        }

        public async Task RollbackSelectedPlugin()
        {
            if (SelectedInstalledPlugin == null) return;

            var versions = _installer.GetAvailableRollbackVersions(SelectedInstalledPlugin.Name);
            if (versions.Count == 0)
            {
                StatusMessage = $"No rollback versions available for {SelectedInstalledPlugin.Name}";
                return;
            }

            // Use the most recent version for rollback
            var versionToRollback = versions.OrderByDescending(v => v).First();
            
            StatusMessage = $"Rolling back {SelectedInstalledPlugin.Name} to version {versionToRollback}...";
            try
            {
                _installer.RollbackPlugin(SelectedInstalledPlugin.Name, versionToRollback);
                StatusMessage = $"{SelectedInstalledPlugin.Name} rolled back successfully";
                await ScanPlugins(); // Refresh installed plugins
            }
            catch (Exception ex)
            {
                StatusMessage = $"Error rolling back plugin: {ex.Message}";
            }
        }

        private void LoadCatalog()
        {
            var plugins = _database.GetAllPlugins();
            var suggested = _database.GetSuggestedPlugins();

            CatalogPlugins.Clear();
            SuggestedPlugins.Clear();

            foreach (var plugin in plugins)
            {
                CatalogPlugins.Add(plugin);
            }

            foreach (var plugin in suggested)
            {
                SuggestedPlugins.Add(plugin);
            }
        }

        public event PropertyChangedEventHandler? PropertyChanged;

        protected virtual void OnPropertyChanged([CallerMemberName] string? propertyName = null)
        {
            PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
        }
    }

    public class RelayCommand : ICommand
    {
        private readonly Action<object?> _execute;
        private readonly Func<object?, bool>? _canExecute;

        public RelayCommand(Action<object?> execute, Func<object?, bool>? canExecute = null)
        {
            _execute = execute ?? throw new ArgumentNullException(nameof(execute));
            _canExecute = canExecute;
        }

        public event EventHandler? CanExecuteChanged
        {
            add { CommandManager.RequerySuggested += value; }
            remove { CommandManager.RequerySuggested -= value; }
        }

        public bool CanExecute(object? parameter) => _canExecute?.Invoke(parameter) ?? true;

        public void Execute(object? parameter) => _execute(parameter);
    }
}
