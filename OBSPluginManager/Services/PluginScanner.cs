using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.RegularExpressions;
using OBSPluginManager.Models;

namespace OBSPluginManager.Services
{
    public class PluginScanner
    {
        private readonly OBSProcessManager _processManager;

        public PluginScanner(OBSProcessManager processManager)
        {
            _processManager = processManager;
        }

        public List<InstalledPlugin> ScanInstalledPlugins()
        {
            var installedPlugins = new List<InstalledPlugin>();
            var obsPath = _processManager.GetOBSInstallPath();

            if (string.IsNullOrEmpty(obsPath) || !Directory.Exists(obsPath))
            {
                return installedPlugins;
            }

            // Scan obs-plugins directory (64-bit plugins)
            var obsPluginsPath = Path.Combine(obsPath, "obs-plugins");
            if (Directory.Exists(obsPluginsPath))
            {
                installedPlugins.AddRange(ScanPluginDirectory(obsPluginsPath, "obs-plugins"));
            }

            // Scan data/obs-plugins directory (32-bit plugins or data plugins)
            var dataPluginsPath = Path.Combine(obsPath, "data", "obs-plugins");
            if (Directory.Exists(dataPluginsPath))
            {
                installedPlugins.AddRange(ScanPluginDirectory(dataPluginsPath, "data/obs-plugins"));
            }

            return installedPlugins;
        }

        private List<InstalledPlugin> ScanPluginDirectory(string directory, string pluginType)
        {
            var plugins = new List<InstalledPlugin>();

            try
            {
                // Look for .dll files in subdirectories (common OBS plugin structure)
                var subdirectories = Directory.GetDirectories(directory);
                foreach (var subdir in subdirectories)
                {
                    var pluginName = Path.GetFileName(subdir);
                    var dllFiles = Directory.GetFiles(subdir, "*.dll", SearchOption.AllDirectories);

                    if (dllFiles.Length > 0)
                    {
                        // Try to extract version from the DLL or look for version info files
                        var version = ExtractVersionFromDirectory(subdir, pluginName);
                        var mainDll = dllFiles.FirstOrDefault(f => 
                            Path.GetFileName(f).StartsWith(pluginName, StringComparison.OrdinalIgnoreCase)) 
                            ?? dllFiles.First();

                        plugins.Add(new InstalledPlugin
                        {
                            Name = pluginName,
                            Version = version,
                            Path = subdir,
                            PluginType = pluginType,
                            InstalledDate = Directory.GetCreationTime(subdir)
                        });
                    }
                }

                // Also check for plugins directly in the directory
                var directDlls = Directory.GetFiles(directory, "*.dll");
                foreach (var dll in directDlls)
                {
                    var pluginName = Path.GetFileNameWithoutExtension(dll);
                    var version = ExtractVersionFromDll(dll);

                    plugins.Add(new InstalledPlugin
                    {
                        Name = pluginName,
                        Version = version,
                        Path = dll,
                        PluginType = pluginType,
                        InstalledDate = File.GetCreationTime(dll)
                    });
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error scanning plugin directory {directory}: {ex.Message}");
            }

            return plugins;
        }

        private string ExtractVersionFromDirectory(string directory, string pluginName)
        {
            // Try to find version.txt or similar files
            var versionFiles = new[] { "version.txt", "VERSION", "version", $"{pluginName}.version" };
            foreach (var versionFile in versionFiles)
            {
                var path = Path.Combine(directory, versionFile);
                if (File.Exists(path))
                {
                    try
                    {
                        var content = File.ReadAllText(path).Trim();
                        var match = Regex.Match(content, @"(\d+\.\d+\.\d+(?:\.\d+)?)");
                        if (match.Success)
                        {
                            return match.Groups[1].Value;
                        }
                        return content;
                    }
                    catch { }
                }
            }

            // Try to extract from directory name (e.g., "plugin-name-1.2.3")
            var dirMatch = Regex.Match(Path.GetFileName(directory), @"(\d+\.\d+\.\d+(?:\.\d+)?)");
            if (dirMatch.Success)
            {
                return dirMatch.Groups[1].Value;
            }

            return "Unknown";
        }

        private string ExtractVersionFromDll(string dllPath)
        {
            try
            {
                // Try to read version from file version info
                var versionInfo = System.Diagnostics.FileVersionInfo.GetVersionInfo(dllPath);
                if (!string.IsNullOrEmpty(versionInfo.FileVersion))
                {
                    return versionInfo.FileVersion;
                }
                if (!string.IsNullOrEmpty(versionInfo.ProductVersion))
                {
                    return versionInfo.ProductVersion;
                }
            }
            catch { }

            // Try to extract from filename
            var fileName = Path.GetFileNameWithoutExtension(dllPath);
            var match = Regex.Match(fileName, @"(\d+\.\d+\.\d+(?:\.\d+)?)");
            if (match.Success)
            {
                return match.Groups[1].Value;
            }

            return "Unknown";
        }
    }
}
