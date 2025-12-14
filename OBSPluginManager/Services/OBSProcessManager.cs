using System;
using System.Diagnostics;
using System.Linq;
using System.Management;

namespace OBSPluginManager.Services
{
    public class OBSProcessManager
    {
        private const string OBS_PROCESS_NAME = "obs64";
        private const string OBS32_PROCESS_NAME = "obs32";

        public bool IsOBSRunning()
        {
            return Process.GetProcessesByName(OBS_PROCESS_NAME).Length > 0 ||
                   Process.GetProcessesByName(OBS32_PROCESS_NAME).Length > 0;
        }

        public Process? GetOBSProcess()
        {
            var process = Process.GetProcessesByName(OBS_PROCESS_NAME).FirstOrDefault();
            if (process == null)
            {
                process = Process.GetProcessesByName(OBS32_PROCESS_NAME).FirstOrDefault();
            }
            return process;
        }

        public bool KillOBS()
        {
            try
            {
                var processes = Process.GetProcessesByName(OBS_PROCESS_NAME)
                    .Concat(Process.GetProcessesByName(OBS32_PROCESS_NAME));

                bool killed = false;
                foreach (var process in processes)
                {
                    try
                    {
                        process.Kill();
                        process.WaitForExit(5000);
                        killed = true;
                    }
                    catch (Exception ex)
                    {
                        System.Diagnostics.Debug.WriteLine($"Error killing OBS process: {ex.Message}");
                    }
                }

                return killed;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error in KillOBS: {ex.Message}");
                return false;
            }
        }

        public string? GetOBSInstallPath()
        {
            try
            {
                // Try to find OBS installation path from running process
                var process = GetOBSProcess();
                if (process != null)
                {
                    try
                    {
                        return System.IO.Path.GetDirectoryName(process.MainModule?.FileName);
                    }
                    catch
                    {
                        // May require admin privileges
                    }
                }

                // Try common installation paths
                var commonPaths = new[]
                {
                    Environment.GetFolderPath(Environment.SpecialFolder.ProgramFiles) + @"\obs-studio",
                    Environment.GetFolderPath(Environment.SpecialFolder.ProgramFilesX86) + @"\obs-studio",
                    Environment.GetFolderPath(Environment.SpecialFolder.LocalApplicationData) + @"\Programs\obs-studio",
                };

                foreach (var path in commonPaths)
                {
                    if (System.IO.Directory.Exists(path))
                    {
                        return path;
                    }
                }

                // Try registry lookup
                try
                {
                    using (var key = Microsoft.Win32.Registry.LocalMachine.OpenSubKey(@"SOFTWARE\OBS Studio"))
                    {
                        if (key != null)
                        {
                            var installPath = key.GetValue("InstallPath") as string;
                            if (!string.IsNullOrEmpty(installPath) && System.IO.Directory.Exists(installPath))
                            {
                                return installPath;
                            }
                        }
                    }
                }
                catch
                {
                    // Registry access may fail
                }

                return null;
            }
            catch (Exception ex)
            {
                System.Diagnostics.Debug.WriteLine($"Error getting OBS install path: {ex.Message}");
                return null;
            }
        }
    }
}
