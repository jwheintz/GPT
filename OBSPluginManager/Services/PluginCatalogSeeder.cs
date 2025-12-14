using System;
using System.Collections.Generic;
using OBSPluginManager.Models;

namespace OBSPluginManager.Services
{
    public class PluginCatalogSeeder
    {
        private readonly PluginDatabase _database;

        public PluginCatalogSeeder(PluginDatabase database)
        {
            _database = database;
        }

        public void SeedInitialData()
        {
            // Sample popular OBS plugins - in production, this would be loaded from BarRaider API or similar
            var plugins = new List<Plugin>
            {
                new Plugin
                {
                    Name = "Advanced Scene Switcher",
                    Author = "WarmUpTill",
                    Description = "An automated scene switcher for OBS Studio with many advanced features",
                    LatestVersion = "1.25.0",
                    DownloadUrl = "https://github.com/WarmUpTill/SceneSwitcher/releases/latest",
                    RepositoryUrl = "https://github.com/WarmUpTill/SceneSwitcher",
                    IsSuggested = true,
                    Category = "Automation",
                    LastUpdated = DateTime.Now.AddDays(-5),
                    Source = "GitHub"
                },
                new Plugin
                {
                    Name = "Move Transition",
                    Author = "exeldro",
                    Description = "Move sources to a new position during scene transition",
                    LatestVersion = "2.5.0",
                    DownloadUrl = "https://github.com/exeldro/obs-move-transition/releases/latest",
                    RepositoryUrl = "https://github.com/exeldro/obs-move-transition",
                    IsSuggested = true,
                    Category = "Transitions",
                    LastUpdated = DateTime.Now.AddDays(-10),
                    Source = "GitHub"
                },
                new Plugin
                {
                    Name = "Source Record",
                    Author = "exeldro",
                    Description = "Record individual sources in OBS Studio",
                    LatestVersion = "1.3.0",
                    DownloadUrl = "https://github.com/exeldro/obs-source-record/releases/latest",
                    RepositoryUrl = "https://github.com/exeldro/obs-source-record",
                    IsSuggested = false,
                    Category = "Recording",
                    LastUpdated = DateTime.Now.AddDays(-15),
                    Source = "GitHub"
                },
                new Plugin
                {
                    Name = "StreamFX",
                    Author = "Xaymar",
                    Description = "A collection of effects and sources for OBS Studio",
                    LatestVersion = "0.12.0",
                    DownloadUrl = "https://github.com/Xaymar/obs-StreamFX/releases/latest",
                    RepositoryUrl = "https://github.com/Xaymar/obs-StreamFX",
                    IsSuggested = true,
                    Category = "Effects",
                    LastUpdated = DateTime.Now.AddDays(-3),
                    Source = "GitHub"
                },
                new Plugin
                {
                    Name = "WebSocket API",
                    Author = "Palakis",
                    Description = "WebSocket API for OBS Studio",
                    LatestVersion = "5.0.0",
                    DownloadUrl = "https://github.com/obsproject/obs-websocket/releases/latest",
                    RepositoryUrl = "https://github.com/obsproject/obs-websocket",
                    IsSuggested = true,
                    Category = "API",
                    LastUpdated = DateTime.Now.AddDays(-1),
                    Source = "GitHub"
                },
                new Plugin
                {
                    Name = "Dual Output",
                    Author = "obsproject",
                    Description = "Dual output plugin for OBS Studio",
                    LatestVersion = "1.0.0",
                    DownloadUrl = "https://github.com/obsproject/obs-studio/releases/latest",
                    RepositoryUrl = "https://github.com/obsproject/obs-studio",
                    IsSuggested = false,
                    Category = "Output",
                    LastUpdated = DateTime.Now.AddDays(-20),
                    Source = "GitHub"
                },
                new Plugin
                {
                    Name = "Source Copy",
                    Author = "exeldro",
                    Description = "Copy sources between scenes",
                    LatestVersion = "1.2.0",
                    DownloadUrl = "https://github.com/exeldro/obs-source-copy/releases/latest",
                    RepositoryUrl = "https://github.com/exeldro/obs-source-copy",
                    IsSuggested = false,
                    Category = "Utility",
                    LastUpdated = DateTime.Now.AddDays(-7),
                    Source = "GitHub"
                },
                new Plugin
                {
                    Name = "BarRaider Stream Deck Plugin",
                    Author = "BarRaider",
                    Description = "Stream Deck integration for OBS Studio",
                    LatestVersion = "2.0.0",
                    DownloadUrl = "https://github.com/BarRaider/streamdeck-obs/releases/latest",
                    RepositoryUrl = "https://github.com/BarRaider/streamdeck-obs",
                    IsSuggested = true,
                    Category = "Integration",
                    LastUpdated = DateTime.Now.AddDays(-2),
                    Source = "BarRaider"
                }
            };

            foreach (var plugin in plugins)
            {
                _database.AddOrUpdatePlugin(plugin);
            }
        }
    }
}
