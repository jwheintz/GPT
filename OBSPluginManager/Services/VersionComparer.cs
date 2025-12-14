using System;
using System.Linq;

namespace OBSPluginManager.Services
{
    public class VersionComparer
    {
        public int CompareVersions(string version1, string version2)
        {
            if (string.IsNullOrEmpty(version1) || version1 == "Unknown")
                return -1;
            if (string.IsNullOrEmpty(version2) || version2 == "Unknown")
                return 1;

            try
            {
                var v1Parts = version1.Split('.').Select(int.Parse).ToArray();
                var v2Parts = version2.Split('.').Select(int.Parse).ToArray();

                int maxLength = Math.Max(v1Parts.Length, v2Parts.Length);
                
                for (int i = 0; i < maxLength; i++)
                {
                    int v1Part = i < v1Parts.Length ? v1Parts[i] : 0;
                    int v2Part = i < v2Parts.Length ? v2Parts[i] : 0;

                    if (v1Part < v2Part) return -1;
                    if (v1Part > v2Part) return 1;
                }

                return 0;
            }
            catch
            {
                // Fallback to string comparison
                return string.Compare(version1, version2, StringComparison.OrdinalIgnoreCase);
            }
        }

        public bool IsNewer(string newVersion, string currentVersion)
        {
            return CompareVersions(newVersion, currentVersion) > 0;
        }

        public bool IsOlder(string oldVersion, string currentVersion)
        {
            return CompareVersions(oldVersion, currentVersion) < 0;
        }

        public bool AreEqual(string version1, string version2)
        {
            return CompareVersions(version1, version2) == 0;
        }
    }
}
