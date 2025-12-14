using System;
using System.Collections.Generic;
using System.Net.Http;
using System.Threading.Tasks;
using Newtonsoft.Json;
using OBSPluginManager.Models;

namespace OBSPluginManager.Services
{
    /// <summary>
    /// Service for updating the plugin catalog from external sources
    /// Can be extended to support BarRaider API, GitHub releases, etc.
    /// </summary>
    public class PluginCatalogUpdater
    {
        private readonly PluginDatabase _database;
        private readonly HttpClient _httpClient;

        public PluginCatalogUpdater(PluginDatabase database)
        {
            _database = database;
            _httpClient = new HttpClient();
            _httpClient.Timeout = TimeSpan.FromMinutes(5);
        }

        /// <summary>
        /// Updates the catalog from a JSON endpoint
        /// </summary>
        public async Task<bool> UpdateFromJsonUrl(string url)
        {
            try
            {
                var response = await _httpClient.GetStringAsync(url);
                var plugins = JsonConvert.DeserializeObject<List<Plugin>>(response);
                
                if (plugins != null)
                {
                    foreach (var plugin in plugins)
                    {
                        plugin.LastUpdated = DateTime.Now;
                        _database.AddOrUpdatePlugin(plugin);
                    }
                    return true;
                }
                return false;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error updating catalog from URL: {ex.Message}");
                return false;
            }
        }

        /// <summary>
        /// Updates the catalog from BarRaider API (example implementation)
        /// This is a placeholder - implement based on actual BarRaider API documentation
        /// </summary>
        public async Task<bool> UpdateFromBarRaiderApi(string apiKey = null)
        {
            // TODO: Implement BarRaider API integration
            // Example structure:
            // var url = $"https://api.barraider.com/obs-plugins?key={apiKey}";
            // return await UpdateFromJsonUrl(url);
            
            throw new NotImplementedException("BarRaider API integration not yet implemented");
        }

        /// <summary>
        /// Updates the catalog from GitHub releases
        /// Searches for OBS plugins in a specific organization or user
        /// </summary>
        public async Task<bool> UpdateFromGitHubReleases(string owner, string repo)
        {
            try
            {
                var url = $"https://api.github.com/repos/{owner}/{repo}/releases/latest";
                _httpClient.DefaultRequestHeaders.Add("User-Agent", "OBSPluginManager/1.0");
                
                var response = await _httpClient.GetStringAsync(url);
                var release = JsonConvert.DeserializeObject<GitHubRelease>(response);
                
                if (release != null && release.Assets != null && release.Assets.Count > 0)
                {
                    var plugin = new Plugin
                    {
                        Name = repo,
                        LatestVersion = release.TagName.TrimStart('v'),
                        DownloadUrl = release.Assets[0].BrowserDownloadUrl,
                        RepositoryUrl = release.HtmlUrl,
                        LastUpdated = DateTime.Now,
                        Source = "GitHub"
                    };
                    
                    _database.AddOrUpdatePlugin(plugin);
                    return true;
                }
                return false;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error updating from GitHub: {ex.Message}");
                return false;
            }
        }

        private class GitHubRelease
        {
            [JsonProperty("tag_name")]
            public string TagName { get; set; } = string.Empty;

            [JsonProperty("html_url")]
            public string HtmlUrl { get; set; } = string.Empty;

            [JsonProperty("assets")]
            public List<GitHubAsset> Assets { get; set; } = new();
        }

        private class GitHubAsset
        {
            [JsonProperty("browser_download_url")]
            public string BrowserDownloadUrl { get; set; } = string.Empty;
        }
    }
}
