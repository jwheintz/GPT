using System;

namespace OBSPluginManager.Models
{
    public class Plugin
    {
        public int Id { get; set; }
        public string Name { get; set; } = string.Empty;
        public string Author { get; set; } = string.Empty;
        public string Description { get; set; } = string.Empty;
        public string LatestVersion { get; set; } = string.Empty;
        public string DownloadUrl { get; set; } = string.Empty;
        public string RepositoryUrl { get; set; } = string.Empty;
        public bool IsSuggested { get; set; }
        public string Category { get; set; } = string.Empty;
        public DateTime LastUpdated { get; set; }
        public string Source { get; set; } = string.Empty; // e.g., "BarRaider", "GitHub", etc.
    }
}
