"""
GUI Application - Main graphical user interface for OBS Plugin Manager.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import re
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from .obs_manager import OBSManager
from .plugin_scanner import PluginScanner
from .plugin_repository import PluginRepository
from .plugin_installer import PluginInstaller
from .database import PluginDatabase
from .local_repository import LocalRepository
from .discovery import PluginDiscovery


class OBSPluginManagerGUI:
    """Main GUI application for OBS Plugin Manager."""
    
    def __init__(self, root: tk.Tk):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("OBS Plugin Manager")
        self.root.geometry("1200x800")
        
        # Initialize components
        self.obs_manager = OBSManager()
        self.plugin_scanner = None
        self.plugin_repository = PluginRepository()
        self.plugin_installer = None
        self.database = PluginDatabase()
        self.local_repository = LocalRepository()
        self.discovery = PluginDiscovery()
        
        # State variables
        self.installed_plugins = []
        self.available_plugins = []
        self.discovery_plugins = {
            "github_new": [], "github_popular": [], "github_trending": [], "github_scripts": [],
            "obs_site_plugins": [], "obs_site_scripts": [],
            "combined_popular": []
        }
        self.current_tab = None
        
        # Setup UI
        self._setup_ui()
        self._check_obs_installation()
        self._load_initial_data()
    
    def _setup_ui(self):
        """Setup the user interface."""
        # Menu bar
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh", command=self._refresh_all)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Check OBS Status", command=self._check_obs_status)
        tools_menu.add_command(label="Kill OBS", command=self._kill_obs)
        tools_menu.add_separator()
        tools_menu.add_command(label="Scan Plugins", command=self._scan_plugins)
        tools_menu.add_command(label="Check for Updates", command=self._check_updates)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)
        
        # Status bar at top
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.status_frame, text="OBS Status:").pack(side=tk.LEFT, padx=5)
        self.obs_status_label = ttk.Label(self.status_frame, text="Checking...", foreground="orange")
        self.obs_status_label.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(self.status_frame, text="Installation:").pack(side=tk.LEFT, padx=20)
        self.obs_path_label = ttk.Label(self.status_frame, text="Not found", foreground="red")
        self.obs_path_label.pack(side=tk.LEFT, padx=5)
        
        self.kill_obs_button = ttk.Button(self.status_frame, text="Kill OBS", command=self._kill_obs)
        self.kill_obs_button.pack(side=tk.RIGHT, padx=5)
        
        # Main notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self._create_installed_tab()
        self._create_available_tab()
        self._create_discovery_tab()
        self._create_updates_tab()
        self._create_history_tab()
        self._create_repository_tab()
        
        # Bottom status bar
        self.bottom_status = ttk.Label(self.root, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.bottom_status.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_installed_tab(self):
        """Create the installed plugins tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Installed Plugins")
        
        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Refresh", command=self._scan_plugins).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Remove", command=self._remove_selected_plugin).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Rollback", command=self._rollback_plugin).pack(side=tk.LEFT, padx=2)
        
        # Plugin list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for installed plugins
        columns = ("name", "version", "size", "path")
        self.installed_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings")
        
        self.installed_tree.heading("#0", text="Plugin")
        self.installed_tree.heading("name", text="Name")
        self.installed_tree.heading("version", text="Version")
        self.installed_tree.heading("size", text="Size")
        self.installed_tree.heading("path", text="Path")
        
        self.installed_tree.column("#0", width=200)
        self.installed_tree.column("name", width=150)
        self.installed_tree.column("version", width=100)
        self.installed_tree.column("size", width=100)
        self.installed_tree.column("path", width=400)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.installed_tree.yview)
        self.installed_tree.configure(yscrollcommand=scrollbar.set)
        
        self.installed_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Details panel
        details_frame = ttk.LabelFrame(frame, text="Plugin Details")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.installed_details = scrolledtext.ScrolledText(details_frame, height=8, wrap=tk.WORD)
        self.installed_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.installed_tree.bind("<<TreeviewSelect>>", self._on_installed_select)
    
    def _create_available_tab(self):
        """Create the available plugins tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Available Plugins")
        
        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Label(toolbar, text="Category:").pack(side=tk.LEFT, padx=5)
        self.category_var = tk.StringVar(value="All")
        category_combo = ttk.Combobox(toolbar, textvariable=self.category_var, width=15)
        category_combo['values'] = ["All"] + self.plugin_repository.get_categories()
        category_combo.pack(side=tk.LEFT, padx=5)
        category_combo.bind("<<ComboboxSelected>>", lambda e: self._filter_available_plugins())
        
        ttk.Label(toolbar, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind("<KeyRelease>", lambda e: self._filter_available_plugins())
        
        ttk.Button(toolbar, text="Refresh Catalog", command=self._refresh_catalog).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Install Selected", command=self._install_selected_plugin).pack(side=tk.RIGHT, padx=5)
        
        # Plugin list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("author", "category", "version")
        self.available_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings")
        
        self.available_tree.heading("#0", text="Plugin")
        self.available_tree.heading("author", text="Author")
        self.available_tree.heading("category", text="Category")
        self.available_tree.heading("version", text="Latest Version")
        
        self.available_tree.column("#0", width=250)
        self.available_tree.column("author", width=150)
        self.available_tree.column("category", width=120)
        self.available_tree.column("version", width=120)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.available_tree.yview)
        self.available_tree.configure(yscrollcommand=scrollbar.set)
        
        self.available_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Details panel
        details_frame = ttk.LabelFrame(frame, text="Plugin Information")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.available_details = scrolledtext.ScrolledText(details_frame, height=8, wrap=tk.WORD)
        self.available_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.available_tree.bind("<<TreeviewSelect>>", self._on_available_select)
    
    def _create_discovery_tab(self):
        """Create the discovery tab for new/popular/trending plugins."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🔍 Discover")
        
        # Toolbar with refresh options
        toolbar = ttk.Frame(frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Label(toolbar, text="Source:").pack(side=tk.LEFT, padx=5)
        
        self.discovery_source = tk.StringVar(value="combined")
        source_frame = ttk.Frame(toolbar)
        source_frame.pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(source_frame, text="Combined", variable=self.discovery_source, value="combined",
                       command=self._switch_discovery_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(source_frame, text="GitHub", variable=self.discovery_source, value="github",
                       command=self._switch_discovery_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(source_frame, text="OBS Site", variable=self.discovery_source, value="obs_site",
                       command=self._switch_discovery_mode).pack(side=tk.LEFT)
        
        ttk.Label(toolbar, text="  |  Mode:").pack(side=tk.LEFT, padx=5)
        
        self.discovery_mode = tk.StringVar(value="popular")
        mode_frame = ttk.Frame(toolbar)
        mode_frame.pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Popular", variable=self.discovery_mode, value="popular",
                       command=self._switch_discovery_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="New", variable=self.discovery_mode, value="new", 
                       command=self._switch_discovery_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Trending", variable=self.discovery_mode, value="trending",
                       command=self._switch_discovery_mode).pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Scripts", variable=self.discovery_mode, value="scripts",
                       command=self._switch_discovery_mode).pack(side=tk.LEFT)
        
        ttk.Button(toolbar, text="Refresh Live Data", command=self._refresh_discovery).pack(side=tk.RIGHT, padx=5)
        
        # Status label
        self.discovery_status = ttk.Label(toolbar, text="", foreground="blue")
        self.discovery_status.pack(side=tk.RIGHT, padx=10)
        
        # Discovery list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("author", "stars", "category", "updated")
        self.discovery_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings")
        
        self.discovery_tree.heading("#0", text="Plugin/Script")
        self.discovery_tree.heading("author", text="Author")
        self.discovery_tree.heading("stars", text="⭐ Stars")
        self.discovery_tree.heading("category", text="Category")
        self.discovery_tree.heading("updated", text="Last Updated")
        
        self.discovery_tree.column("#0", width=250)
        self.discovery_tree.column("author", width=150)
        self.discovery_tree.column("stars", width=100)
        self.discovery_tree.column("category", width=120)
        self.discovery_tree.column("updated", width=150)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.discovery_tree.yview)
        self.discovery_tree.configure(yscrollcommand=scrollbar.set)
        
        self.discovery_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Details panel
        details_frame = ttk.LabelFrame(frame, text="Details & Links")
        details_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.discovery_details = scrolledtext.ScrolledText(details_frame, height=8, wrap=tk.WORD)
        self.discovery_details.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Action buttons
        action_frame = ttk.Frame(details_frame)
        action_frame.pack(pady=5)
        
        ttk.Button(action_frame, text="Open Homepage", command=self._open_discovery_homepage).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Add to Catalog", command=self._add_discovery_to_catalog).pack(side=tk.LEFT, padx=5)
        
        self.discovery_tree.bind("<<TreeviewSelect>>", self._on_discovery_select)
    
    def _create_repository_tab(self):
        """Create the local repository tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📦 Local Repo")
        
        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Refresh", command=self._refresh_repository).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Cleanup Orphaned Files", command=self._cleanup_repository).pack(side=tk.LEFT, padx=5)
        
        # Stats frame
        stats_frame = ttk.LabelFrame(frame, text="Repository Statistics")
        stats_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.repo_stats_text = ttk.Label(stats_frame, text="Loading repository stats...")
        self.repo_stats_text.pack(padx=10, pady=10)
        
        # Repository list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Tabs for plugins and scripts
        repo_notebook = ttk.Notebook(list_frame)
        repo_notebook.pack(fill=tk.BOTH, expand=True)
        
        # Plugins tab
        plugins_frame = ttk.Frame(repo_notebook)
        repo_notebook.add(plugins_frame, text="Plugins")
        
        columns = ("version", "versions", "size", "added")
        self.repo_plugins_tree = ttk.Treeview(plugins_frame, columns=columns, show="tree headings")
        
        self.repo_plugins_tree.heading("#0", text="Plugin Name")
        self.repo_plugins_tree.heading("version", text="Latest Version")
        self.repo_plugins_tree.heading("versions", text="Versions Stored")
        self.repo_plugins_tree.heading("size", text="Size")
        self.repo_plugins_tree.heading("added", text="Added")
        
        scrollbar1 = ttk.Scrollbar(plugins_frame, orient=tk.VERTICAL, command=self.repo_plugins_tree.yview)
        self.repo_plugins_tree.configure(yscrollcommand=scrollbar1.set)
        
        self.repo_plugins_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar1.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Scripts tab
        scripts_frame = ttk.Frame(repo_notebook)
        repo_notebook.add(scripts_frame, text="Scripts")
        
        self.repo_scripts_tree = ttk.Treeview(scripts_frame, columns=columns, show="tree headings")
        
        self.repo_scripts_tree.heading("#0", text="Script Name")
        self.repo_scripts_tree.heading("version", text="Latest Version")
        self.repo_scripts_tree.heading("versions", text="Versions Stored")
        self.repo_scripts_tree.heading("size", text="Size")
        self.repo_scripts_tree.heading("added", text="Added")
        
        scrollbar2 = ttk.Scrollbar(scripts_frame, orient=tk.VERTICAL, command=self.repo_scripts_tree.yview)
        self.repo_scripts_tree.configure(yscrollcommand=scrollbar2.set)
        
        self.repo_scripts_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar2.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _create_updates_tab(self):
        """Create the updates tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Updates")
        
        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Check for Updates", command=self._check_updates).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Update Selected", command=self._update_selected_plugin).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Update All", command=self._update_all_plugins).pack(side=tk.LEFT, padx=5)
        
        # Updates list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("current_version", "latest_version", "status")
        self.updates_tree = ttk.Treeview(list_frame, columns=columns, show="tree headings")
        
        self.updates_tree.heading("#0", text="Plugin")
        self.updates_tree.heading("current_version", text="Current Version")
        self.updates_tree.heading("latest_version", text="Latest Version")
        self.updates_tree.heading("status", text="Status")
        
        self.updates_tree.column("#0", width=250)
        self.updates_tree.column("current_version", width=150)
        self.updates_tree.column("latest_version", width=150)
        self.updates_tree.column("status", width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.updates_tree.yview)
        self.updates_tree.configure(yscrollcommand=scrollbar.set)
        
        self.updates_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Info label
        info_label = ttk.Label(frame, text="No updates checked yet. Click 'Check for Updates' to scan for available updates.")
        info_label.pack(padx=5, pady=5)
    
    def _create_history_tab(self):
        """Create the history tab."""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="History")
        
        # Toolbar
        toolbar = ttk.Frame(frame)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)
        
        ttk.Button(toolbar, text="Refresh", command=self._load_history).pack(side=tk.LEFT, padx=5)
        ttk.Button(toolbar, text="Clear History", command=self._clear_history).pack(side=tk.LEFT, padx=5)
        
        # History list
        list_frame = ttk.Frame(frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        columns = ("plugin", "action", "version", "timestamp", "status")
        self.history_tree = ttk.Treeview(list_frame, columns=columns, show="headings")
        
        self.history_tree.heading("plugin", text="Plugin")
        self.history_tree.heading("action", text="Action")
        self.history_tree.heading("version", text="Version")
        self.history_tree.heading("timestamp", text="Timestamp")
        self.history_tree.heading("status", text="Status")
        
        self.history_tree.column("plugin", width=200)
        self.history_tree.column("action", width=150)
        self.history_tree.column("version", width=100)
        self.history_tree.column("timestamp", width=200)
        self.history_tree.column("status", width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def _check_obs_installation(self):
        """Check if OBS is installed and update UI."""
        if self.obs_manager.is_obs_installed():
            obs_path = self.obs_manager.get_obs_path()
            self.obs_path_label.config(text=str(obs_path), foreground="green")
            
            # Initialize scanner and installer
            plugin_dirs = self.obs_manager.get_plugin_directories()
            self.plugin_scanner = PluginScanner(plugin_dirs)
            self.plugin_installer = PluginInstaller(plugin_dirs)
        else:
            self.obs_path_label.config(text="Not found", foreground="red")
            messagebox.showwarning(
                "OBS Not Found",
                "OBS Studio installation not detected. Some features will be unavailable."
            )
    
    def _check_obs_status(self):
        """Check if OBS is running."""
        if self.obs_manager.is_obs_running():
            self.obs_status_label.config(text="Running", foreground="red")
            messagebox.showinfo("OBS Status", "OBS Studio is currently running.")
        else:
            self.obs_status_label.config(text="Not Running", foreground="green")
            messagebox.showinfo("OBS Status", "OBS Studio is not running.")
    
    def _kill_obs(self):
        """Kill OBS process."""
        if not self.obs_manager.is_obs_running():
            messagebox.showinfo("OBS Status", "OBS is not running.")
            return
        
        if messagebox.askyesno("Kill OBS", "Are you sure you want to terminate OBS Studio?"):
            success, message = self.obs_manager.kill_obs()
            if success:
                self.obs_status_label.config(text="Not Running", foreground="green")
                messagebox.showinfo("Success", message)
            else:
                messagebox.showerror("Error", message)
    
    def _load_initial_data(self):
        """Load initial data."""
        # Load available plugins
        self._load_available_plugins()
        
        # Scan installed plugins
        if self.plugin_scanner:
            self._scan_plugins()
        
        # Load history
        self._load_history()
        
        # Load repository
        self._refresh_repository()
        
        # Load discovery (cached data)
        self._update_discovery_list()
        
        # Update OBS status
        self._update_obs_status()
    
    def _update_obs_status(self):
        """Update OBS status in UI."""
        if self.obs_manager.is_obs_running():
            self.obs_status_label.config(text="Running ⚠️", foreground="red")
        else:
            self.obs_status_label.config(text="Not Running ✓", foreground="green")
        
        # Schedule next update
        self.root.after(2000, self._update_obs_status)
    
    def _scan_plugins(self):
        """Scan for installed plugins."""
        if not self.plugin_scanner:
            messagebox.showwarning("Error", "Cannot scan plugins - OBS installation not found.")
            return
        
        self.set_status("Scanning plugins...")
        
        def scan_thread():
            plugins = self.plugin_scanner.scan_plugins()
            self.installed_plugins = plugins
            
            # Update database
            for plugin in plugins:
                self.database.add_installed_plugin(
                    plugin['name'],
                    plugin.get('version', 'Unknown'),
                    plugin['path']
                )
            
            self.root.after(0, self._update_installed_list)
            self.root.after(0, lambda: self.set_status(f"Found {len(plugins)} installed plugins"))
        
        threading.Thread(target=scan_thread, daemon=True).start()
    
    def _update_installed_list(self):
        """Update the installed plugins list."""
        # Clear current items
        for item in self.installed_tree.get_children():
            self.installed_tree.delete(item)
        
        # Add plugins
        for plugin in self.installed_plugins:
            size_kb = plugin['size'] / 1024
            self.installed_tree.insert(
                "",
                tk.END,
                text=plugin['filename'],
                values=(
                    plugin['name'],
                    plugin.get('version', 'Unknown'),
                    f"{size_kb:.1f} KB",
                    plugin['path']
                )
            )
    
    def _load_available_plugins(self):
        """Load available plugins from repository."""
        self.available_plugins = self.plugin_repository.get_popular_plugins()
        self._update_available_list()
    
    def _update_available_list(self):
        """Update the available plugins list."""
        # Clear current items
        for item in self.available_tree.get_children():
            self.available_tree.delete(item)
        
        # Filter plugins
        category = self.category_var.get()
        search = self.search_var.get().lower()
        
        for plugin in self.available_plugins:
            # Apply filters
            if category != "All" and plugin.get("category") != category:
                continue
            
            if search and search not in plugin['name'].lower() and search not in plugin.get('display_name', '').lower():
                continue
            
            # Check if installed
            is_installed = any(p['name'].lower() == plugin['name'].lower() for p in self.installed_plugins)
            display_name = plugin.get('display_name', plugin['name'])
            if is_installed:
                display_name += " [INSTALLED]"
            
            # Add recommended badge
            if plugin.get('is_recommended'):
                display_name = "⭐ " + display_name
            
            self.available_tree.insert(
                "",
                tk.END,
                text=display_name,
                values=(
                    plugin.get('author', 'Unknown'),
                    plugin.get('category', 'Unknown'),
                    plugin.get('latest_version', 'Check online')
                ),
                tags=('installed',) if is_installed else ()
            )
    
    def _filter_available_plugins(self):
        """Filter available plugins based on search and category."""
        self._update_available_list()
    
    def _refresh_catalog(self):
        """Refresh plugin catalog."""
        self.set_status("Refreshing catalog...")
        
        def refresh_thread():
            for plugin in self.available_plugins:
                updated = self.plugin_repository.refresh_plugin_info(plugin)
                # Update in list
                for i, p in enumerate(self.available_plugins):
                    if p['name'] == updated['name']:
                        self.available_plugins[i] = updated
                        break
            
            self.root.after(0, self._update_available_list)
            self.root.after(0, lambda: self.set_status("Catalog refreshed"))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def _check_updates(self):
        """Check for plugin updates."""
        if not self.plugin_scanner:
            messagebox.showwarning("Error", "Cannot check updates - OBS installation not found.")
            return
        
        self.set_status("Checking for updates...")
        
        def check_thread():
            updates = self.plugin_repository.check_for_updates(self.installed_plugins)
            
            self.root.after(0, lambda: self._show_updates(updates))
            self.root.after(0, lambda: self.set_status(f"Found {len(updates)} update(s) available"))
        
        threading.Thread(target=check_thread, daemon=True).start()
    
    def _show_updates(self, updates: List[Dict]):
        """Show available updates."""
        # Clear current items
        for item in self.updates_tree.get_children():
            self.updates_tree.delete(item)
        
        # Add updates
        for update in updates:
            self.updates_tree.insert(
                "",
                tk.END,
                text=update['plugin']['name'],
                values=(
                    update['current_version'],
                    update['latest_version'],
                    "Update available"
                )
            )
        
        if not updates:
            messagebox.showinfo("Updates", "All plugins are up to date!")
    
    def _install_selected_plugin(self):
        """Install the selected plugin."""
        if self.obs_manager.is_obs_running():
            messagebox.showerror("Error", "Cannot install plugins while OBS is running. Please close OBS first.")
            return
        
        selection = self.available_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a plugin to install.")
            return
        
        item = self.available_tree.item(selection[0])
        plugin_name = item['text'].replace("⭐ ", "").replace(" [INSTALLED]", "")
        
        # Find plugin in catalog
        plugin = None
        for p in self.available_plugins:
            if p.get('display_name', p['name']) == plugin_name or p['name'] in plugin_name:
                plugin = p
                break
        
        if not plugin:
            messagebox.showerror("Error", "Plugin not found in catalog.")
            return
        
        if not plugin.get('download_url'):
            messagebox.showerror("Error", "No download URL available for this plugin.")
            return
        
        # Confirm installation
        if not messagebox.askyesno("Install Plugin", f"Install {plugin.get('display_name', plugin['name'])}?"):
            return
        
        # Show progress window
        self._show_install_progress(plugin)
    
    def _show_install_progress(self, plugin: Dict):
        """Show installation progress window."""
        progress_window = tk.Toplevel(self.root)
        progress_window.title("Installing Plugin")
        progress_window.geometry("500x150")
        progress_window.transient(self.root)
        progress_window.grab_set()
        
        ttk.Label(progress_window, text=f"Installing {plugin.get('display_name', plugin['name'])}...").pack(pady=10)
        
        progress_var = tk.StringVar(value="Preparing...")
        progress_label = ttk.Label(progress_window, textvariable=progress_var)
        progress_label.pack(pady=5)
        
        progress_bar = ttk.Progressbar(progress_window, mode='determinate', length=400)
        progress_bar.pack(pady=10)
        
        def update_progress(message: str, percent: int):
            progress_var.set(message)
            progress_bar['value'] = percent
            progress_window.update()
        
        def install_thread():
            success, message = self.plugin_installer.install_from_url(
                plugin['download_url'],
                plugin['name'],
                update_progress
            )
            
            if success:
                self.database.add_history_entry(
                    plugin['name'],
                    "install",
                    plugin.get('latest_version', ''),
                    success=True,
                    notes=message
                )
            
            progress_window.destroy()
            
            if success:
                messagebox.showinfo("Success", f"Plugin installed successfully!\n\n{message}")
                self._scan_plugins()  # Refresh installed list
            else:
                messagebox.showerror("Error", f"Installation failed:\n{message}")
        
        threading.Thread(target=install_thread, daemon=True).start()
    
    def _remove_selected_plugin(self):
        """Remove the selected plugin."""
        if self.obs_manager.is_obs_running():
            messagebox.showerror("Error", "Cannot remove plugins while OBS is running. Please close OBS first.")
            return
        
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a plugin to remove.")
            return
        
        item = self.installed_tree.item(selection[0])
        plugin_name = item['values'][0]
        
        # Find plugin info
        plugin = self.plugin_scanner.get_plugin_by_name(plugin_name)
        if not plugin:
            messagebox.showerror("Error", "Plugin information not found.")
            return
        
        # Confirm removal
        if not messagebox.askyesno("Remove Plugin", f"Remove {plugin_name}?\n\nA backup will be created for rollback."):
            return
        
        # Remove plugin
        success, message = self.plugin_installer.remove_plugin(plugin, create_backup=True)
        
        if success:
            self.database.add_history_entry(plugin_name, "remove", plugin.get('version', ''), success=True)
            messagebox.showinfo("Success", message)
            self._scan_plugins()
        else:
            messagebox.showerror("Error", message)
    
    def _rollback_plugin(self):
        """Rollback a plugin to previous version."""
        if self.obs_manager.is_obs_running():
            messagebox.showerror("Error", "Cannot rollback plugins while OBS is running. Please close OBS first.")
            return
        
        selection = self.installed_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a plugin to rollback.")
            return
        
        item = self.installed_tree.item(selection[0])
        plugin_name = item['values'][0]
        
        # Get available archives
        archives = self.plugin_installer.get_archive_list(plugin_name)
        
        if not archives:
            messagebox.showinfo("No Archives", "No backup archives available for this plugin.")
            return
        
        # Show archive selection dialog
        self._show_archive_selection(plugin_name, archives)
    
    def _show_archive_selection(self, plugin_name: str, archives: List[Dict]):
        """Show archive selection dialog."""
        dialog = tk.Toplevel(self.root)
        dialog.title(f"Rollback {plugin_name}")
        dialog.geometry("600x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ttk.Label(dialog, text=f"Select a version to restore for {plugin_name}:").pack(pady=10)
        
        # Archive list
        list_frame = ttk.Frame(dialog)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ("version", "date", "files")
        tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=8)
        
        tree.heading("version", text="Version")
        tree.heading("date", text="Archived Date")
        tree.heading("files", text="Files")
        
        for archive in archives:
            tree.insert(
                "",
                tk.END,
                values=(
                    archive.get('version', 'Unknown'),
                    archive.get('archived_date', 'Unknown'),
                    archive.get('file_count', 0)
                )
            )
        
        tree.pack(fill=tk.BOTH, expand=True)
        
        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        
        def restore():
            selection = tree.selection()
            if not selection:
                messagebox.showwarning("No Selection", "Please select an archive to restore.")
                return
            
            index = tree.index(selection[0])
            archive = archives[index]
            
            # Restore from archive
            success, message = self.plugin_installer.restore_from_archive(
                Path(archive['archive_path']),
                plugin_name
            )
            
            if success:
                self.database.add_history_entry(
                    plugin_name,
                    "rollback",
                    archive.get('version', ''),
                    success=True
                )
                messagebox.showinfo("Success", message)
                dialog.destroy()
                self._scan_plugins()
            else:
                messagebox.showerror("Error", message)
        
        ttk.Button(button_frame, text="Restore", command=restore).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)
    
    def _update_selected_plugin(self):
        """Update the selected plugin."""
        # Similar to install but checks current version
        messagebox.showinfo("Update Plugin", "This feature will update the selected plugin.")
    
    def _update_all_plugins(self):
        """Update all plugins with available updates."""
        messagebox.showinfo("Update All", "This feature will update all plugins with available updates.")
    
    def _load_history(self):
        """Load installation history."""
        # Clear current items
        for item in self.history_tree.get_children():
            self.history_tree.delete(item)
        
        # Load history from database
        history = self.database.get_history(limit=100)
        
        for entry in history:
            self.history_tree.insert(
                "",
                tk.END,
                values=(
                    entry['plugin_name'],
                    entry['action'],
                    entry.get('version', ''),
                    entry['timestamp'],
                    "✓" if entry['success'] else "✗"
                )
            )
    
    def _clear_history(self):
        """Clear installation history."""
        if messagebox.askyesno("Clear History", "Are you sure you want to clear the installation history?"):
            # This would require a method in the database class
            messagebox.showinfo("Info", "History cleared (feature not fully implemented).")
    
    def _on_installed_select(self, event):
        """Handle selection in installed plugins list."""
        selection = self.installed_tree.selection()
        if not selection:
            return
        
        item = self.installed_tree.item(selection[0])
        plugin_name = item['values'][0]
        
        # Find plugin details
        plugin = self.plugin_scanner.get_plugin_by_name(plugin_name)
        if plugin:
            details = f"Name: {plugin['name']}\n"
            details += f"Filename: {plugin['filename']}\n"
            details += f"Version: {plugin.get('version', 'Unknown')}\n"
            details += f"Path: {plugin['path']}\n"
            details += f"Size: {plugin['size'] / 1024:.1f} KB\n"
            details += f"Hash: {plugin.get('hash', 'N/A')}\n"
            
            self.installed_details.delete(1.0, tk.END)
            self.installed_details.insert(1.0, details)
    
    def _on_available_select(self, event):
        """Handle selection in available plugins list."""
        selection = self.available_tree.selection()
        if not selection:
            return
        
        item = self.available_tree.item(selection[0])
        plugin_name = item['text'].replace("⭐ ", "").replace(" [INSTALLED]", "")
        
        # Find plugin in catalog
        plugin = None
        for p in self.available_plugins:
            if p.get('display_name', p['name']) == plugin_name or p['name'] in plugin_name:
                plugin = p
                break
        
        if plugin:
            details = f"{plugin.get('display_name', plugin['name'])}\n\n"
            details += f"Author: {plugin.get('author', 'Unknown')}\n"
            details += f"Category: {plugin.get('category', 'Unknown')}\n"
            details += f"Latest Version: {plugin.get('latest_version', 'Check online')}\n\n"
            details += f"Description:\n{plugin.get('description', 'No description available')}\n\n"
            details += f"Homepage: {plugin.get('homepage_url', 'N/A')}\n"
            if plugin.get('is_recommended'):
                details += "\n⭐ Recommended Plugin"
            
            self.available_details.delete(1.0, tk.END)
            self.available_details.insert(1.0, details)
    
    def _refresh_all(self):
        """Refresh all data."""
        self._scan_plugins()
        self._load_available_plugins()
        self._load_history()
        self.set_status("Refreshed all data")
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            "About OBS Plugin Manager",
            "OBS Plugin Manager v1.0\n\n"
            "A comprehensive tool for managing OBS Studio plugins on Windows.\n\n"
            "Features:\n"
            "• Automatic plugin detection\n"
            "• Version checking and updates\n"
            "• Safe installation with OBS status checking\n"
            "• Automatic backups and rollback support\n"
            "• Popular plugin catalog\n\n"
            "Developed for OBS Studio users."
        )
    
    def set_status(self, message: str):
        """Set status bar message."""
        self.bottom_status.config(text=message)
    
    # Discovery tab methods
    def _switch_discovery_mode(self):
        """Switch between discovery modes."""
        mode = self.discovery_mode.get()
        self._update_discovery_list()
    
    def _refresh_discovery(self):
        """Refresh discovery data with live queries."""
        source = self.discovery_source.get()
        mode = self.discovery_mode.get()
        
        if source == "obs_site":
            self.set_status("Querying OBS website...")
            self.discovery_status.config(text="Querying OBS Resources...")
        elif source == "github":
            self.set_status("Querying GitHub API...")
            self.discovery_status.config(text="Querying GitHub...")
        else:
            self.set_status("Querying both sources...")
            self.discovery_status.config(text="Querying multiple sources...")
        
        def refresh_thread():
            try:
                cache_key = f"{source}_{mode}"
                
                if source == "combined" and mode == "popular":
                    plugins = self.discovery.discover_combined_popular(max_results=30, force_refresh=True)
                    self.discovery_plugins["combined_popular"] = plugins
                elif source == "obs_site":
                    if mode == "scripts":
                        plugins = self.discovery.discover_obs_website_scripts(max_results=50, force_refresh=True)
                        self.discovery_plugins["obs_site_scripts"] = plugins
                    else:
                        plugins = self.discovery.discover_obs_website_plugins(max_results=50, force_refresh=True)
                        self.discovery_plugins["obs_site_plugins"] = plugins
                elif source == "github":
                    if mode == "new":
                        plugins = self.discovery.discover_new_plugins(max_results=20, force_refresh=True)
                        self.discovery_plugins["github_new"] = plugins
                    elif mode == "popular":
                        plugins = self.discovery.discover_popular_plugins(max_results=20, force_refresh=True)
                        self.discovery_plugins["github_popular"] = plugins
                    elif mode == "trending":
                        plugins = self.discovery.discover_trending_plugins(max_results=20, force_refresh=True)
                        self.discovery_plugins["github_trending"] = plugins
                    elif mode == "scripts":
                        plugins = self.discovery.discover_obs_scripts(max_results=20, force_refresh=True)
                        self.discovery_plugins["github_scripts"] = plugins
                else:
                    plugins = []
                
                self.root.after(0, self._update_discovery_list)
                self.root.after(0, lambda: self.set_status(f"Found {len(plugins)} plugins/scripts from {source}"))
                self.root.after(0, lambda: self.discovery_status.config(text=f"Updated: {datetime.now().strftime('%H:%M')}"))
            except Exception as e:
                self.root.after(0, lambda: self.set_status(f"Discovery refresh failed: {str(e)}"))
                self.root.after(0, lambda: self.discovery_status.config(text="Error querying"))
        
        threading.Thread(target=refresh_thread, daemon=True).start()
    
    def _update_discovery_list(self):
        """Update the discovery list based on current source and mode."""
        # Clear current items
        for item in self.discovery_tree.get_children():
            self.discovery_tree.delete(item)
        
        source = self.discovery_source.get()
        mode = self.discovery_mode.get()
        cache_key = f"{source}_{mode}"
        
        # Get appropriate list
        plugins = []
        if source == "combined" and mode == "popular":
            if not self.discovery_plugins["combined_popular"]:
                self.discovery_plugins["combined_popular"] = self.discovery.discover_combined_popular()
            plugins = self.discovery_plugins["combined_popular"]
        elif source == "obs_site":
            if mode == "scripts":
                if not self.discovery_plugins["obs_site_scripts"]:
                    self.discovery_plugins["obs_site_scripts"] = self.discovery.discover_obs_website_scripts()
                plugins = self.discovery_plugins["obs_site_scripts"]
            else:
                if not self.discovery_plugins["obs_site_plugins"]:
                    self.discovery_plugins["obs_site_plugins"] = self.discovery.discover_obs_website_plugins()
                plugins = self.discovery_plugins["obs_site_plugins"]
        elif source == "github":
            if mode == "new":
                if not self.discovery_plugins["github_new"]:
                    self.discovery_plugins["github_new"] = self.discovery.discover_new_plugins()
                plugins = self.discovery_plugins["github_new"]
            elif mode == "popular":
                if not self.discovery_plugins["github_popular"]:
                    self.discovery_plugins["github_popular"] = self.discovery.discover_popular_plugins()
                plugins = self.discovery_plugins["github_popular"]
            elif mode == "trending":
                if not self.discovery_plugins["github_trending"]:
                    self.discovery_plugins["github_trending"] = self.discovery.discover_trending_plugins()
                plugins = self.discovery_plugins["github_trending"]
            elif mode == "scripts":
                if not self.discovery_plugins["github_scripts"]:
                    self.discovery_plugins["github_scripts"] = self.discovery.discover_obs_scripts()
                plugins = self.discovery_plugins["github_scripts"]
        
        # Add to tree
        for plugin in plugins:
            # Format updated date
            updated_str = plugin.get("updated_at", plugin.get("last_update", ""))
            if updated_str:
                try:
                    updated_dt = datetime.strptime(updated_str, "%Y-%m-%dT%H:%M:%SZ")
                    updated_display = updated_dt.strftime("%Y-%m-%d")
                except Exception:
                    updated_display = updated_str[:10] if len(updated_str) >= 10 else "Unknown"
            else:
                updated_display = "Unknown"
            
            display_name = plugin.get("display_name", plugin.get("name", "Unknown"))
            if plugin.get("is_script") or plugin.get("resource_type") == "script":
                display_name = "📜 " + display_name
            
            # Add source indicator
            plugin_source = plugin.get("source", "")
            if plugin_source:
                display_name = f"[{plugin_source}] {display_name}"
            
            # Get stars or rating
            stars_display = plugin.get("stars", 0)
            if not stars_display and "rating" in plugin:
                rating = plugin.get("rating", 0)
                downloads = plugin.get("downloads", 0)
                stars_display = f"{rating:.1f}⭐ ({downloads}dl)"
            
            self.discovery_tree.insert(
                "",
                tk.END,
                text=display_name,
                values=(
                    plugin.get("author", "Unknown"),
                    stars_display,
                    plugin.get("category", "Other"),
                    updated_display
                )
            )
        
        # Update status
        cache_info = self.discovery.get_cache_info()
        if cache_key in cache_info:
            age_hours = cache_info[cache_key].get("age_hours", 0)
            self.discovery_status.config(text=f"Cached {age_hours:.1f}h ago ({source})")
    
    def _on_discovery_select(self, event):
        """Handle selection in discovery list."""
        selection = self.discovery_tree.selection()
        if not selection:
            return
        
        item = self.discovery_tree.item(selection[0])
        plugin_name = item['text'].replace("📜 ", "")
        # Remove source prefix if present
        plugin_name = re.sub(r'^\[.*?\]\s*', '', plugin_name)
        
        # Get current source and mode
        source = self.discovery_source.get()
        mode = self.discovery_mode.get()
        cache_key = f"{source}_{mode}"
        
        # Find plugin in current list
        plugins = []
        if source == "combined":
            plugins = self.discovery_plugins["combined_popular"]
        elif source == "obs_site":
            if mode == "scripts":
                plugins = self.discovery_plugins.get("obs_site_scripts", [])
            else:
                plugins = self.discovery_plugins.get("obs_site_plugins", [])
        elif source == "github":
            if mode == "new":
                plugins = self.discovery_plugins.get("github_new", [])
            elif mode == "popular":
                plugins = self.discovery_plugins.get("github_popular", [])
            elif mode == "trending":
                plugins = self.discovery_plugins.get("github_trending", [])
            elif mode == "scripts":
                plugins = self.discovery_plugins.get("github_scripts", [])
        
        plugin = None
        for p in plugins:
            if p.get("display_name", p["name"]) == plugin_name:
                plugin = p
                break
        
        if plugin:
            details = f"{plugin.get('display_name', plugin.get('name', 'Unknown'))}\n"
            details += f"{'=' * 60}\n\n"
            
            # Source indicator
            plugin_source = plugin.get("source", "Unknown")
            details += f"Source: {plugin_source}\n"
            
            if plugin.get('full_name'):
                details += f"Repository: {plugin.get('full_name')}\n"
            
            details += f"Author: {plugin.get('author', 'Unknown')}\n"
            details += f"Category: {plugin.get('category', 'Other')}\n"
            
            # Show stars or rating depending on source
            if plugin.get("stars"):
                details += f"Stars: ⭐ {plugin.get('stars', 0)}\n"
            if plugin.get("rating"):
                details += f"Rating: {plugin.get('rating', 0):.1f}/5.0\n"
            if plugin.get("downloads"):
                details += f"Downloads: {plugin.get('downloads', 0):,}\n"
            
            if plugin.get("forks"):
                details += f"Forks: {plugin.get('forks', 0)}\n"
            if plugin.get("language"):
                details += f"Language: {plugin.get('language')}\n"
            if plugin.get("version"):
                details += f"Version: {plugin.get('version')}\n"
            
            # Type
            if plugin.get("is_script") or plugin.get("resource_type") == "script":
                details += f"Type: OBS Script\n"
            else:
                details += f"Type: OBS Plugin\n"
            
            # Last update
            last_update = plugin.get('updated_at', plugin.get('last_update', 'Unknown'))
            details += f"\nLast Updated: {last_update}\n"
            
            # Description
            details += f"\nDescription:\n{plugin.get('description', 'No description')}\n\n"
            
            # Links
            details += f"Homepage: {plugin.get('homepage_url', 'N/A')}\n"
            details += f"Download: {plugin.get('download_url', 'N/A')}\n"
            
            # Additional info
            if plugin.get("trending_score"):
                details += f"\nTrending Score: {plugin['trending_score']:.2f}\n"
            
            self.discovery_details.delete(1.0, tk.END)
            self.discovery_details.insert(1.0, details)
    
    def _open_discovery_homepage(self):
        """Open the homepage of selected discovery item."""
        selection = self.discovery_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a plugin/script to open.")
            return
        
        item = self.discovery_tree.item(selection[0])
        plugin_name = item['text'].replace("📜 ", "")
        plugin_name = re.sub(r'^\[.*?\]\s*', '', plugin_name)
        
        # Get current source and mode
        source = self.discovery_source.get()
        mode = self.discovery_mode.get()
        
        # Find plugin in current list
        plugins = []
        if source == "combined":
            plugins = self.discovery_plugins["combined_popular"]
        elif source == "obs_site":
            if mode == "scripts":
                plugins = self.discovery_plugins.get("obs_site_scripts", [])
            else:
                plugins = self.discovery_plugins.get("obs_site_plugins", [])
        elif source == "github":
            if mode == "new":
                plugins = self.discovery_plugins.get("github_new", [])
            elif mode == "popular":
                plugins = self.discovery_plugins.get("github_popular", [])
            elif mode == "trending":
                plugins = self.discovery_plugins.get("github_trending", [])
            elif mode == "scripts":
                plugins = self.discovery_plugins.get("github_scripts", [])
        
        plugin = None
        for p in plugins:
            if p.get("display_name", p["name"]) == plugin_name:
                plugin = p
                break
        
        if plugin and plugin.get("homepage_url"):
            import webbrowser
            webbrowser.open(plugin["homepage_url"])
    
    def _add_discovery_to_catalog(self):
        """Add discovered plugin to the main catalog."""
        selection = self.discovery_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a plugin/script to add.")
            return
        
        item = self.discovery_tree.item(selection[0])
        plugin_name = item['text'].replace("📜 ", "")
        plugin_name = re.sub(r'^\[.*?\]\s*', '', plugin_name)
        
        # Get current source and mode
        source = self.discovery_source.get()
        mode = self.discovery_mode.get()
        
        # Find plugin in current list
        plugins = []
        if source == "combined":
            plugins = self.discovery_plugins["combined_popular"]
        elif source == "obs_site":
            if mode == "scripts":
                plugins = self.discovery_plugins.get("obs_site_scripts", [])
            else:
                plugins = self.discovery_plugins.get("obs_site_plugins", [])
        elif source == "github":
            if mode == "new":
                plugins = self.discovery_plugins.get("github_new", [])
            elif mode == "popular":
                plugins = self.discovery_plugins.get("github_popular", [])
            elif mode == "trending":
                plugins = self.discovery_plugins.get("github_trending", [])
            elif mode == "scripts":
                plugins = self.discovery_plugins.get("github_scripts", [])
        
        plugin = None
        for p in plugins:
            if p.get("display_name", p.get("name")) == plugin_name:
                plugin = p
                break
        
        if plugin:
            # Add to database catalog
            success = self.database.add_plugin_to_catalog(
                name=plugin["name"],
                display_name=plugin.get("display_name", plugin["name"]),
                description=plugin.get("description", ""),
                author=plugin.get("author", ""),
                category=plugin.get("category", "Other"),
                download_url=plugin.get("download_url", ""),
                homepage_url=plugin.get("homepage_url", ""),
                is_recommended=False,
                metadata={"discovered": True, "stars": plugin.get("stars", 0)}
            )
            
            if success:
                messagebox.showinfo("Success", f"Added {plugin['name']} to catalog!")
                self._load_available_plugins()  # Refresh available plugins
            else:
                messagebox.showerror("Error", "Failed to add to catalog")
    
    # Repository tab methods
    def _refresh_repository(self):
        """Refresh the local repository view."""
        self.set_status("Refreshing local repository...")
        
        # Update stats
        stats = self.local_repository.get_repository_stats()
        stats_text = f"Total Plugins: {stats['total_plugins']}  |  "
        stats_text += f"Total Scripts: {stats['total_scripts']}  |  "
        stats_text += f"Total Versions: {stats['total_plugin_versions'] + stats['total_script_versions']}  |  "
        stats_text += f"Total Size: {stats['total_size_mb']:.2f} MB"
        self.repo_stats_text.config(text=stats_text)
        
        # Update plugins list
        for item in self.repo_plugins_tree.get_children():
            self.repo_plugins_tree.delete(item)
        
        plugins = self.local_repository.list_all_plugins()
        for plugin in plugins:
            size_mb = plugin['size'] / (1024 * 1024)
            added_date = plugin.get('latest_added', '')
            if added_date:
                try:
                    dt = datetime.fromisoformat(added_date)
                    added_display = dt.strftime("%Y-%m-%d")
                except Exception:
                    added_display = "Unknown"
            else:
                added_display = "Unknown"
            
            self.repo_plugins_tree.insert(
                "",
                tk.END,
                text=plugin['name'],
                values=(
                    plugin['latest_version'],
                    plugin['version_count'],
                    f"{size_mb:.2f} MB",
                    added_display
                )
            )
        
        # Update scripts list
        for item in self.repo_scripts_tree.get_children():
            self.repo_scripts_tree.delete(item)
        
        scripts = self.local_repository.list_all_scripts()
        for script in scripts:
            size_mb = script['size'] / (1024 * 1024)
            added_date = script.get('latest_added', '')
            if added_date:
                try:
                    dt = datetime.fromisoformat(added_date)
                    added_display = dt.strftime("%Y-%m-%d")
                except Exception:
                    added_display = "Unknown"
            else:
                added_display = "Unknown"
            
            self.repo_scripts_tree.insert(
                "",
                tk.END,
                text=script['name'],
                values=(
                    script['latest_version'],
                    script['version_count'],
                    f"{size_mb:.2f} MB",
                    added_display
                )
            )
        
        self.set_status(f"Repository: {stats['total_plugins']} plugins, {stats['total_scripts']} scripts")
    
    def _cleanup_repository(self):
        """Cleanup orphaned files in repository."""
        if messagebox.askyesno("Cleanup Repository", 
                              "This will remove files not referenced in the repository index.\n\nContinue?"):
            files_removed, space_freed = self.local_repository.cleanup_orphaned_files()
            space_mb = space_freed / (1024 * 1024)
            messagebox.showinfo("Cleanup Complete", 
                               f"Removed {files_removed} file(s)\nFreed {space_mb:.2f} MB")
            self._refresh_repository()


def main():
    """Main entry point."""
    root = tk.Tk()
    app = OBSPluginManagerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
