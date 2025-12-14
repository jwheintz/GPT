using System;

namespace OBSPluginManager.Models
{
    public class InstalledPlugin
    {
        public string Name { get; set; } = string.Empty;
        public string Version { get; set; } = string.Empty;
        public string Path { get; set; } = string.Empty;
        public string PluginType { get; set; } = string.Empty; // "obs-plugins" or "data/obs-plugins"
        public DateTime InstalledDate { get; set; }
        public bool HasUpdate { get; set; }
        public string LatestVersion { get; set; } = string.Empty;
    }
}
