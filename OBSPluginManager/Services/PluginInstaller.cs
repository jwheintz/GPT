using System;
using System.IO;
using System.IO.Compression;
using System.Linq;
using System.Net.Http;
using System.Threading.Tasks;
using OBSPluginManager.Models;
using OBSPluginManager.Services;

namespace OBSPluginManager.Services
{
    public class PluginInstaller
    {
        private readonly OBSProcessManager _processManager;
        private readonly string _archiveBasePath;

        public PluginInstaller(OBSProcessManager processManager)
        {
            _processManager = processManager;
            _archiveBasePath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "PluginArchives");
            Directory.CreateDirectory(_archiveBasePath);
        }

        public async Task<bool> InstallPlugin(Plugin plugin, InstalledPlugin? existingPlugin = null)
        {
            if (_processManager.IsOBSRunning())
            {
                throw new InvalidOperationException("Cannot install plugins while OBS is running. Please close OBS first.");
            }

            try
            {
                // Archive existing plugin if it exists
                if (existingPlugin != null && Directory.Exists(existingPlugin.Path))
                {
                    await ArchivePlugin(existingPlugin);
                }

                // Download plugin
                var tempPath = await DownloadPlugin(plugin);
                if (string.IsNullOrEmpty(tempPath))
                {
                    throw new Exception("Failed to download plugin");
                }

                // Extract and install
                var obsPath = _processManager.GetOBSInstallPath();
                if (string.IsNullOrEmpty(obsPath))
                {
                    throw new Exception("OBS installation path not found");
                }

                var targetPath = DetermineTargetPath(obsPath, plugin.Name, existingPlugin?.PluginType ?? "obs-plugins");
                
                // Extract plugin
                ExtractPlugin(tempPath, targetPath);

                // Clean up temp file
                File.Delete(tempPath);

                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error installing plugin {plugin.Name}: {ex.Message}");
                throw;
            }
        }

        private async Task<string> DownloadPlugin(Plugin plugin)
        {
            if (string.IsNullOrEmpty(plugin.DownloadUrl))
            {
                throw new Exception($"No download URL available for plugin {plugin.Name}");
            }

            var tempPath = Path.Combine(Path.GetTempPath(), $"obs-plugin-{Guid.NewGuid()}.zip");

            using (var httpClient = new HttpClient())
            {
                httpClient.Timeout = TimeSpan.FromMinutes(10);
                var response = await httpClient.GetAsync(plugin.DownloadUrl);
                response.EnsureSuccessStatusCode();

                using (var fileStream = new FileStream(tempPath, FileMode.Create))
                {
                    await response.Content.CopyToAsync(fileStream);
                }
            }

            return tempPath;
        }

        private void ExtractPlugin(string zipPath, string targetPath)
        {
            // Ensure target directory exists
            Directory.CreateDirectory(targetPath);

            using (var archive = ZipFile.OpenRead(zipPath))
            {
                // Find the plugin directory structure
                var entries = archive.Entries.Where(e => !string.IsNullOrEmpty(e.Name)).ToList();

                // Check if there's a single root directory containing the plugin
                var rootDirs = entries.Select(e => e.FullName.Split('/')[0]).Distinct().ToList();
                
                if (rootDirs.Count == 1 && rootDirs[0] != Path.GetFileName(targetPath))
                {
                    // Extract to temp first, then move
                    var tempExtract = Path.Combine(Path.GetTempPath(), Guid.NewGuid().ToString());
                    ZipFile.ExtractToDirectory(zipPath, tempExtract);
                    
                    var extractedPluginPath = Path.Combine(tempExtract, rootDirs[0]);
                    if (Directory.Exists(extractedPluginPath))
                    {
                        // Copy contents to target
                        CopyDirectory(extractedPluginPath, targetPath);
                        Directory.Delete(tempExtract, true);
                    }
                }
                else
                {
                    // Extract directly
                    ZipFile.ExtractToDirectory(zipPath, targetPath, true);
                }
            }
        }

        private void CopyDirectory(string sourceDir, string targetDir)
        {
            Directory.CreateDirectory(targetDir);

            foreach (var file in Directory.GetFiles(sourceDir))
            {
                var targetFile = Path.Combine(targetDir, Path.GetFileName(file));
                File.Copy(file, targetFile, true);
            }

            foreach (var subdir in Directory.GetDirectories(sourceDir))
            {
                var targetSubdir = Path.Combine(targetDir, Path.GetFileName(subdir));
                CopyDirectory(subdir, targetSubdir);
            }
        }

        private string DetermineTargetPath(string obsPath, string pluginName, string pluginType)
        {
            if (pluginType == "data/obs-plugins")
            {
                return Path.Combine(obsPath, "data", "obs-plugins", pluginName);
            }
            else
            {
                return Path.Combine(obsPath, "obs-plugins", pluginName);
            }
        }

        private async Task ArchivePlugin(InstalledPlugin plugin)
        {
            try
            {
                var pluginArchivePath = Path.Combine(_archiveBasePath, plugin.Name);
                Directory.CreateDirectory(pluginArchivePath);

                // Keep only last 2 versions
                var existingArchives = Directory.GetDirectories(pluginArchivePath)
                    .Select(d => new { Path = d, Time = Directory.GetCreationTime(d) })
                    .OrderByDescending(x => x.Time)
                    .ToList();

                // Remove old archives beyond the last 2
                for (int i = 2; i < existingArchives.Count; i++)
                {
                    Directory.Delete(existingArchives[i].Path, true);
                }

                // Create new archive
                var archiveName = $"{plugin.Version}_{DateTime.Now:yyyyMMdd_HHmmss}";
                var archivePath = Path.Combine(pluginArchivePath, archiveName);
                Directory.CreateDirectory(archivePath);

                // Copy plugin files to archive
                if (Directory.Exists(plugin.Path))
                {
                    CopyDirectory(plugin.Path, archivePath);
                }
                else if (File.Exists(plugin.Path))
                {
                    var targetFile = Path.Combine(archivePath, Path.GetFileName(plugin.Path));
                    Directory.CreateDirectory(archivePath);
                    File.Copy(plugin.Path, targetFile, true);
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error archiving plugin {plugin.Name}: {ex.Message}");
            }
        }

        public bool RollbackPlugin(string pluginName, string version)
        {
            if (_processManager.IsOBSRunning())
            {
                throw new InvalidOperationException("Cannot rollback plugins while OBS is running. Please close OBS first.");
            }

            try
            {
                var pluginArchivePath = Path.Combine(_archiveBasePath, pluginName);
                if (!Directory.Exists(pluginArchivePath))
                {
                    throw new Exception($"No archive found for plugin {pluginName}");
                }

                // Find archive matching version
                var archives = Directory.GetDirectories(pluginArchivePath)
                    .Where(d => d.Contains(version))
                    .OrderByDescending(d => Directory.GetCreationTime(d))
                    .ToList();

                if (archives.Count == 0)
                {
                    throw new Exception($"No archive found for version {version} of plugin {pluginName}");
                }

                var archivePath = archives.First();
                var obsPath = _processManager.GetOBSInstallPath();
                if (string.IsNullOrEmpty(obsPath))
                {
                    throw new Exception("OBS installation path not found");
                }

                // Determine target path (try both locations)
                var targetPaths = new[]
                {
                    Path.Combine(obsPath, "obs-plugins", pluginName),
                    Path.Combine(obsPath, "data", "obs-plugins", pluginName)
                };

                var targetPath = targetPaths.FirstOrDefault(p => Directory.Exists(Path.GetDirectoryName(p) ?? ""));

                if (string.IsNullOrEmpty(targetPath))
                {
                    targetPath = targetPaths[0]; // Default to obs-plugins
                }

                // Restore from archive
                if (Directory.Exists(targetPath))
                {
                    Directory.Delete(targetPath, true);
                }

                CopyDirectory(archivePath, targetPath);

                return true;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error rolling back plugin {pluginName}: {ex.Message}");
                throw;
            }
        }

        public List<string> GetAvailableRollbackVersions(string pluginName)
        {
            var versions = new List<string>();
            var pluginArchivePath = Path.Combine(_archiveBasePath, pluginName);

            if (Directory.Exists(pluginArchivePath))
            {
                var archives = Directory.GetDirectories(pluginArchivePath)
                    .Select(d => Path.GetFileName(d))
                    .Where(f => f.Contains("_"))
                    .Select(f => f.Split('_')[0])
                    .Distinct()
                    .ToList();

                versions.AddRange(archives);
            }

            return versions;
        }
    }
}
