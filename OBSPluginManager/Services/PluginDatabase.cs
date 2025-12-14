using System;
using System.Collections.Generic;
using System.Data;
using System.IO;
using System.Linq;
using Microsoft.Data.Sqlite;
using OBSPluginManager.Models;

namespace OBSPluginManager.Services
{
    public class PluginDatabase
    {
        private readonly string _connectionString;

        public PluginDatabase()
        {
            var dbPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "PluginsDatabase.db");
            _connectionString = $"Data Source={dbPath}";
            InitializeDatabase();
        }

        private void InitializeDatabase()
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();

            var command = connection.CreateCommand();
            command.CommandText = @"
                CREATE TABLE IF NOT EXISTS Plugins (
                    Id INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL UNIQUE,
                    Author TEXT,
                    Description TEXT,
                    LatestVersion TEXT NOT NULL,
                    DownloadUrl TEXT,
                    RepositoryUrl TEXT,
                    IsSuggested INTEGER DEFAULT 0,
                    Category TEXT,
                    LastUpdated TEXT,
                    Source TEXT
                );

                CREATE INDEX IF NOT EXISTS idx_plugins_name ON Plugins(Name);
                CREATE INDEX IF NOT EXISTS idx_plugins_suggested ON Plugins(IsSuggested);
            ";

            command.ExecuteNonQuery();
        }

        public void AddOrUpdatePlugin(Plugin plugin)
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();

            var command = connection.CreateCommand();
            command.CommandText = @"
                INSERT INTO Plugins (Name, Author, Description, LatestVersion, DownloadUrl, RepositoryUrl, IsSuggested, Category, LastUpdated, Source)
                VALUES ($name, $author, $description, $version, $downloadUrl, $repoUrl, $isSuggested, $category, $lastUpdated, $source)
                ON CONFLICT(Name) DO UPDATE SET
                    Author = excluded.Author,
                    Description = excluded.Description,
                    LatestVersion = excluded.LatestVersion,
                    DownloadUrl = excluded.DownloadUrl,
                    RepositoryUrl = excluded.RepositoryUrl,
                    IsSuggested = excluded.IsSuggested,
                    Category = excluded.Category,
                    LastUpdated = excluded.LastUpdated,
                    Source = excluded.Source;
            ";

            command.Parameters.AddWithValue("$name", plugin.Name);
            command.Parameters.AddWithValue("$author", plugin.Author ?? "");
            command.Parameters.AddWithValue("$description", plugin.Description ?? "");
            command.Parameters.AddWithValue("$version", plugin.LatestVersion);
            command.Parameters.AddWithValue("$downloadUrl", plugin.DownloadUrl ?? "");
            command.Parameters.AddWithValue("$repoUrl", plugin.RepositoryUrl ?? "");
            command.Parameters.AddWithValue("$isSuggested", plugin.IsSuggested ? 1 : 0);
            command.Parameters.AddWithValue("$category", plugin.Category ?? "");
            command.Parameters.AddWithValue("$lastUpdated", plugin.LastUpdated.ToString("O"));
            command.Parameters.AddWithValue("$source", plugin.Source ?? "");

            command.ExecuteNonQuery();
        }

        public List<Plugin> GetAllPlugins()
        {
            var plugins = new List<Plugin>();

            using var connection = new SqliteConnection(_connectionString);
            connection.Open();

            var command = connection.CreateCommand();
            command.CommandText = "SELECT * FROM Plugins ORDER BY Name";

            using var reader = command.ExecuteReader();
            while (reader.Read())
            {
                plugins.Add(MapPluginFromReader(reader));
            }

            return plugins;
        }

        public List<Plugin> GetSuggestedPlugins()
        {
            var plugins = new List<Plugin>();

            using var connection = new SqliteConnection(_connectionString);
            connection.Open();

            var command = connection.CreateCommand();
            command.CommandText = "SELECT * FROM Plugins WHERE IsSuggested = 1 ORDER BY Name";

            using var reader = command.ExecuteReader();
            while (reader.Read())
            {
                plugins.Add(MapPluginFromReader(reader));
            }

            return plugins;
        }

        public Plugin? GetPluginByName(string name)
        {
            using var connection = new SqliteConnection(_connectionString);
            connection.Open();

            var command = connection.CreateCommand();
            command.CommandText = "SELECT * FROM Plugins WHERE Name = $name";
            command.Parameters.AddWithValue("$name", name);

            using var reader = command.ExecuteReader();
            if (reader.Read())
            {
                return MapPluginFromReader(reader);
            }

            return null;
        }

        private Plugin MapPluginFromReader(SqliteDataReader reader)
        {
            return new Plugin
            {
                Id = reader.GetInt32("Id"),
                Name = reader.GetString("Name"),
                Author = reader.IsDBNull("Author") ? "" : reader.GetString("Author"),
                Description = reader.IsDBNull("Description") ? "" : reader.GetString("Description"),
                LatestVersion = reader.GetString("LatestVersion"),
                DownloadUrl = reader.IsDBNull("DownloadUrl") ? "" : reader.GetString("DownloadUrl"),
                RepositoryUrl = reader.IsDBNull("RepositoryUrl") ? "" : reader.GetString("RepositoryUrl"),
                IsSuggested = reader.GetInt32("IsSuggested") == 1,
                Category = reader.IsDBNull("Category") ? "" : reader.GetString("Category"),
                LastUpdated = DateTime.Parse(reader.GetString("LastUpdated")),
                Source = reader.IsDBNull("Source") ? "" : reader.GetString("Source")
            };
        }

        public void RefreshFromJson(string jsonData)
        {
            try
            {
                var plugins = Newtonsoft.Json.JsonConvert.DeserializeObject<List<Plugin>>(jsonData);
                if (plugins != null)
                {
                    foreach (var plugin in plugins)
                    {
                        AddOrUpdatePlugin(plugin);
                    }
                }
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error refreshing database from JSON: {ex.Message}");
                throw;
            }
        }
    }
}
