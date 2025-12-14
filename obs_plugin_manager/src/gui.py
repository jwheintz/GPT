"""
OBS Plugin Manager GUI.
Main graphical user interface using CustomTkinter for a modern look.
"""

import os
import sys
import logging
import threading
import webbrowser
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any, Callable

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    import customtkinter as ctk
    from PIL import Image
    HAS_CTK = True
except ImportError:
    HAS_CTK = False
    import tkinter as tk
    from tkinter import ttk, messagebox, filedialog
    logger.warning("CustomTkinter not available, using standard tkinter")


class OBSPluginManagerGUI:
    """Main GUI application for OBS Plugin Manager."""
    
    def __init__(self):
        # Initialize components
        from .config import get_config
        from .database import PluginDatabase
        from .obs_scanner import OBSScanner
        from .process_manager import ProcessManager
        from .plugin_manager import PluginManager
        from .catalog_refresh import CatalogRefresher
        
        self.config = get_config()
        self.db = PluginDatabase()
        self.scanner = OBSScanner(self.config)
        self.process_manager = ProcessManager()
        self.plugin_manager = PluginManager(self.config)
        self.catalog_refresher = CatalogRefresher(self.db)
        
        # State
        self.obs_running = False
        self.installed_plugins = []
        self.catalog_plugins = []
        
        # Create main window
        if HAS_CTK:
            self._create_ctk_window()
        else:
            self._create_tk_window()
    
    def _create_ctk_window(self):
        """Create CustomTkinter window."""
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("OBS Plugin Manager")
        self.root.geometry(f"{self.config.config.window_width}x{self.config.config.window_height}")
        self.root.minsize(900, 600)
        
        # Create main layout
        self._create_sidebar()
        self._create_main_content()
        self._create_status_bar()
        
        # Start background tasks
        self._start_obs_monitor()
        
        # Initial data load
        self.root.after(100, self._initial_load)
    
    def _create_tk_window(self):
        """Create standard tkinter window as fallback."""
        self.root = tk.Tk()
        self.root.title("OBS Plugin Manager")
        self.root.geometry(f"{self.config.config.window_width}x{self.config.config.window_height}")
        self.root.minsize(900, 600)
        
        # Create main layout with ttk
        self._create_sidebar_tk()
        self._create_main_content_tk()
        self._create_status_bar_tk()
        
        # Start background tasks
        self._start_obs_monitor()
        
        # Initial data load
        self.root.after(100, self._initial_load)
    
    def _create_sidebar(self):
        """Create sidebar navigation (CustomTkinter)."""
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        self.sidebar.pack_propagate(False)
        
        # Logo/Title
        title_label = ctk.CTkLabel(
            self.sidebar,
            text="OBS Plugin\nManager",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title_label.pack(pady=(20, 30))
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("installed", "📦 Installed", self._show_installed),
            ("catalog", "📚 Plugin Catalog", self._show_catalog),
            ("updates", "🔄 Updates", self._show_updates),
            ("suggestions", "💡 Suggestions", self._show_suggestions),
            ("settings", "⚙️ Settings", self._show_settings),
        ]
        
        for key, text, command in nav_items:
            btn = ctk.CTkButton(
                self.sidebar,
                text=text,
                command=command,
                anchor="w",
                font=ctk.CTkFont(size=14),
                height=40,
                corner_radius=5
            )
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_buttons[key] = btn
        
        # Spacer
        spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)
        
        # OBS Status
        self.obs_status_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.obs_status_frame.pack(fill="x", padx=10, pady=10)
        
        self.obs_status_label = ctk.CTkLabel(
            self.obs_status_frame,
            text="🔴 OBS: Checking...",
            font=ctk.CTkFont(size=12)
        )
        self.obs_status_label.pack()
        
        self.kill_obs_btn = ctk.CTkButton(
            self.obs_status_frame,
            text="Kill OBS",
            command=self._kill_obs,
            fg_color="red",
            hover_color="darkred",
            height=30
        )
        self.kill_obs_btn.pack(pady=(5, 0))
        self.kill_obs_btn.pack_forget()  # Hidden initially
    
    def _create_sidebar_tk(self):
        """Create sidebar navigation (standard tkinter)."""
        self.sidebar = ttk.Frame(self.root, width=200)
        self.sidebar.pack(side="left", fill="y", padx=0, pady=0)
        
        # Title
        title_label = ttk.Label(
            self.sidebar,
            text="OBS Plugin\nManager",
            font=('Helvetica', 16, 'bold')
        )
        title_label.pack(pady=(20, 30))
        
        # Navigation buttons
        self.nav_buttons = {}
        
        nav_items = [
            ("installed", "Installed Plugins", self._show_installed),
            ("catalog", "Plugin Catalog", self._show_catalog),
            ("updates", "Check Updates", self._show_updates),
            ("suggestions", "Suggestions", self._show_suggestions),
            ("settings", "Settings", self._show_settings),
        ]
        
        for key, text, command in nav_items:
            btn = ttk.Button(self.sidebar, text=text, command=command)
            btn.pack(fill="x", padx=10, pady=5)
            self.nav_buttons[key] = btn
        
        # OBS Status
        self.obs_status_label = ttk.Label(self.sidebar, text="OBS: Checking...")
        self.obs_status_label.pack(pady=10)
        
        self.kill_obs_btn = ttk.Button(self.sidebar, text="Kill OBS", command=self._kill_obs)
    
    def _create_main_content(self):
        """Create main content area (CustomTkinter)."""
        self.main_frame = ctk.CTkFrame(self.root, corner_radius=0)
        self.main_frame.pack(side="left", fill="both", expand=True, padx=0, pady=0)
        
        # Content frames for different views
        self.content_frames = {}
        
        # Create each content frame
        self._create_installed_frame()
        self._create_catalog_frame()
        self._create_updates_frame()
        self._create_suggestions_frame()
        self._create_settings_frame()
        
        # Show installed by default
        self._show_installed()
    
    def _create_main_content_tk(self):
        """Create main content area (standard tkinter)."""
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(side="left", fill="both", expand=True)
        
        # Content frames for different views
        self.content_frames = {}
        
        # Create each content frame
        self._create_installed_frame_tk()
        self._create_catalog_frame_tk()
        self._create_updates_frame_tk()
        self._create_suggestions_frame_tk()
        self._create_settings_frame_tk()
        
        # Show installed by default
        self._show_installed()
    
    def _create_installed_frame(self):
        """Create installed plugins view (CustomTkinter)."""
        frame = ctk.CTkFrame(self.main_frame)
        self.content_frames['installed'] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(header, text="Installed Plugins", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left")
        
        refresh_btn = ctk.CTkButton(header, text="🔄 Refresh", command=self._refresh_installed, width=100)
        refresh_btn.pack(side="right")
        
        # Search
        search_frame = ctk.CTkFrame(frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.installed_search = ctk.CTkEntry(search_frame, placeholder_text="Search installed plugins...", width=300)
        self.installed_search.pack(side="left")
        self.installed_search.bind("<KeyRelease>", self._filter_installed)
        
        # Plugins list
        self.installed_list_frame = ctk.CTkScrollableFrame(frame)
        self.installed_list_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def _create_installed_frame_tk(self):
        """Create installed plugins view (standard tkinter)."""
        frame = ttk.Frame(self.main_frame)
        self.content_frames['installed'] = frame
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill="x", padx=20, pady=10)
        
        title = ttk.Label(header, text="Installed Plugins", font=('Helvetica', 18, 'bold'))
        title.pack(side="left")
        
        refresh_btn = ttk.Button(header, text="Refresh", command=self._refresh_installed)
        refresh_btn.pack(side="right")
        
        # List using Treeview
        columns = ('Name', 'Version', 'Status')
        self.installed_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            self.installed_tree.heading(col, text=col)
            self.installed_tree.column(col, width=150)
        
        self.installed_tree.pack(fill="both", expand=True, padx=20, pady=10)
    
    def _create_catalog_frame(self):
        """Create plugin catalog view (CustomTkinter)."""
        frame = ctk.CTkFrame(self.main_frame)
        self.content_frames['catalog'] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(header, text="Plugin Catalog", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left")
        
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right")
        
        refresh_btn = ctk.CTkButton(btn_frame, text="🔄 Refresh Catalog", command=self._refresh_catalog, width=140)
        refresh_btn.pack(side="left", padx=5)
        
        # Search and filter
        search_frame = ctk.CTkFrame(frame, fg_color="transparent")
        search_frame.pack(fill="x", padx=20, pady=10)
        
        self.catalog_search = ctk.CTkEntry(search_frame, placeholder_text="Search plugins...", width=300)
        self.catalog_search.pack(side="left")
        self.catalog_search.bind("<KeyRelease>", self._filter_catalog)
        
        # Category filter
        self.category_var = ctk.StringVar(value="All Categories")
        categories = ["All Categories", "streaming", "recording", "sources", "filters", 
                     "audio", "video", "automation", "integration", "utility", "other"]
        
        self.category_menu = ctk.CTkOptionMenu(
            search_frame,
            variable=self.category_var,
            values=categories,
            command=self._filter_by_category
        )
        self.category_menu.pack(side="left", padx=10)
        
        # Plugin list
        self.catalog_list_frame = ctk.CTkScrollableFrame(frame)
        self.catalog_list_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def _create_catalog_frame_tk(self):
        """Create plugin catalog view (standard tkinter)."""
        frame = ttk.Frame(self.main_frame)
        self.content_frames['catalog'] = frame
        
        # Header
        header = ttk.Frame(frame)
        header.pack(fill="x", padx=20, pady=10)
        
        title = ttk.Label(header, text="Plugin Catalog", font=('Helvetica', 18, 'bold'))
        title.pack(side="left")
        
        refresh_btn = ttk.Button(header, text="Refresh Catalog", command=self._refresh_catalog)
        refresh_btn.pack(side="right")
        
        # List
        columns = ('Name', 'Author', 'Version', 'Category')
        self.catalog_tree = ttk.Treeview(frame, columns=columns, show='headings')
        
        for col in columns:
            self.catalog_tree.heading(col, text=col)
        
        self.catalog_tree.pack(fill="both", expand=True, padx=20, pady=10)
    
    def _create_updates_frame(self):
        """Create updates view (CustomTkinter)."""
        frame = ctk.CTkFrame(self.main_frame)
        self.content_frames['updates'] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(header, text="Available Updates", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left")
        
        check_btn = ctk.CTkButton(header, text="🔄 Check for Updates", command=self._check_updates, width=150)
        check_btn.pack(side="right")
        
        # Updates list
        self.updates_list_frame = ctk.CTkScrollableFrame(frame)
        self.updates_list_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # No updates label
        self.no_updates_label = ctk.CTkLabel(
            self.updates_list_frame,
            text="Click 'Check for Updates' to scan for available updates.",
            font=ctk.CTkFont(size=14)
        )
        self.no_updates_label.pack(pady=50)
    
    def _create_updates_frame_tk(self):
        """Create updates view (standard tkinter)."""
        frame = ttk.Frame(self.main_frame)
        self.content_frames['updates'] = frame
        
        title = ttk.Label(frame, text="Available Updates", font=('Helvetica', 18, 'bold'))
        title.pack(pady=10)
        
        check_btn = ttk.Button(frame, text="Check for Updates", command=self._check_updates)
        check_btn.pack(pady=10)
        
        self.updates_tree = ttk.Treeview(frame, columns=('Name', 'Current', 'Latest'), show='headings')
        for col in ('Name', 'Current', 'Latest'):
            self.updates_tree.heading(col, text=col)
        self.updates_tree.pack(fill="both", expand=True, padx=20, pady=10)
    
    def _create_suggestions_frame(self):
        """Create suggestions view (CustomTkinter)."""
        frame = ctk.CTkFrame(self.main_frame)
        self.content_frames['suggestions'] = frame
        
        # Header
        header = ctk.CTkFrame(frame, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        title = ctk.CTkLabel(header, text="Suggested Plugins", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(side="left")
        
        # Description
        desc = ctk.CTkLabel(
            frame,
            text="Based on popular and recommended plugins you haven't installed yet.",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        desc.pack(padx=20, anchor="w")
        
        # Suggestions list
        self.suggestions_list_frame = ctk.CTkScrollableFrame(frame)
        self.suggestions_list_frame.pack(fill="both", expand=True, padx=20, pady=10)
    
    def _create_suggestions_frame_tk(self):
        """Create suggestions view (standard tkinter)."""
        frame = ttk.Frame(self.main_frame)
        self.content_frames['suggestions'] = frame
        
        title = ttk.Label(frame, text="Suggested Plugins", font=('Helvetica', 18, 'bold'))
        title.pack(pady=10)
        
        self.suggestions_tree = ttk.Treeview(frame, columns=('Name', 'Category', 'Reason'), show='headings')
        for col in ('Name', 'Category', 'Reason'):
            self.suggestions_tree.heading(col, text=col)
        self.suggestions_tree.pack(fill="both", expand=True, padx=20, pady=10)
    
    def _create_settings_frame(self):
        """Create settings view (CustomTkinter)."""
        frame = ctk.CTkFrame(self.main_frame)
        self.content_frames['settings'] = frame
        
        # Header
        title = ctk.CTkLabel(frame, text="Settings", font=ctk.CTkFont(size=24, weight="bold"))
        title.pack(padx=20, pady=(20, 20), anchor="w")
        
        # Settings content
        settings_scroll = ctk.CTkScrollableFrame(frame)
        settings_scroll.pack(fill="both", expand=True, padx=20, pady=10)
        
        # OBS Path
        obs_frame = ctk.CTkFrame(settings_scroll)
        obs_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(obs_frame, text="OBS Installation Path:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        path_frame = ctk.CTkFrame(obs_frame, fg_color="transparent")
        path_frame.pack(fill="x", padx=10, pady=5)
        
        self.obs_path_entry = ctk.CTkEntry(path_frame, width=400)
        self.obs_path_entry.pack(side="left")
        self.obs_path_entry.insert(0, self.config.config.obs_install_path or "Not detected")
        
        browse_btn = ctk.CTkButton(path_frame, text="Browse", command=self._browse_obs_path, width=80)
        browse_btn.pack(side="left", padx=5)
        
        detect_btn = ctk.CTkButton(path_frame, text="Auto-detect", command=self._detect_obs_path, width=100)
        detect_btn.pack(side="left", padx=5)
        
        # Archive Settings
        archive_frame = ctk.CTkFrame(settings_scroll)
        archive_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(archive_frame, text="Archive Settings:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        archive_count_frame = ctk.CTkFrame(archive_frame, fg_color="transparent")
        archive_count_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(archive_count_frame, text="Keep last").pack(side="left")
        self.archive_count_var = ctk.StringVar(value=str(self.config.config.max_archive_versions))
        archive_spinbox = ctk.CTkEntry(archive_count_frame, textvariable=self.archive_count_var, width=50)
        archive_spinbox.pack(side="left", padx=5)
        ctk.CTkLabel(archive_count_frame, text="versions for rollback").pack(side="left")
        
        # Actions
        actions_frame = ctk.CTkFrame(settings_scroll)
        actions_frame.pack(fill="x", pady=10)
        
        ctk.CTkLabel(actions_frame, text="Maintenance:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=5)
        
        btn_frame = ctk.CTkFrame(actions_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        cleanup_btn = ctk.CTkButton(btn_frame, text="Clean Temp Files", command=self._cleanup_temp)
        cleanup_btn.pack(side="left", padx=5)
        
        export_btn = ctk.CTkButton(btn_frame, text="Export Catalog", command=self._export_catalog)
        export_btn.pack(side="left", padx=5)
        
        import_btn = ctk.CTkButton(btn_frame, text="Import Catalog", command=self._import_catalog)
        import_btn.pack(side="left", padx=5)
        
        # Save button
        save_btn = ctk.CTkButton(frame, text="Save Settings", command=self._save_settings)
        save_btn.pack(pady=20)
    
    def _create_settings_frame_tk(self):
        """Create settings view (standard tkinter)."""
        frame = ttk.Frame(self.main_frame)
        self.content_frames['settings'] = frame
        
        title = ttk.Label(frame, text="Settings", font=('Helvetica', 18, 'bold'))
        title.pack(pady=10)
        
        # OBS Path
        ttk.Label(frame, text="OBS Installation Path:").pack(anchor="w", padx=20)
        self.obs_path_entry = ttk.Entry(frame, width=50)
        self.obs_path_entry.pack(padx=20, pady=5)
        self.obs_path_entry.insert(0, self.config.config.obs_install_path or "Not detected")
        
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="Browse", command=self._browse_obs_path).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Auto-detect", command=self._detect_obs_path).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Save", command=self._save_settings).pack(side="left", padx=5)
    
    def _create_status_bar(self):
        """Create status bar (CustomTkinter)."""
        self.status_bar = ctk.CTkFrame(self.root, height=30, corner_radius=0)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ctk.CTkLabel(self.status_bar, text="Ready", font=ctk.CTkFont(size=12))
        self.status_label.pack(side="left", padx=10)
        
        self.progress_bar = ctk.CTkProgressBar(self.status_bar, width=200)
        self.progress_bar.pack(side="right", padx=10)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # Hidden initially
    
    def _create_status_bar_tk(self):
        """Create status bar (standard tkinter)."""
        self.status_bar = ttk.Frame(self.root)
        self.status_bar.pack(side="bottom", fill="x")
        
        self.status_label = ttk.Label(self.status_bar, text="Ready")
        self.status_label.pack(side="left", padx=10)
    
    def _show_frame(self, frame_name: str):
        """Show a specific content frame."""
        # Hide all frames
        for name, frame in self.content_frames.items():
            frame.pack_forget()
        
        # Show selected frame
        if frame_name in self.content_frames:
            self.content_frames[frame_name].pack(fill="both", expand=True)
        
        # Update nav button states (CustomTkinter)
        if HAS_CTK:
            for name, btn in self.nav_buttons.items():
                if name == frame_name:
                    btn.configure(fg_color=("gray75", "gray25"))
                else:
                    btn.configure(fg_color=("gray70", "gray30"))
    
    def _show_installed(self):
        """Show installed plugins view."""
        self._show_frame('installed')
        self._refresh_installed()
    
    def _show_catalog(self):
        """Show plugin catalog view."""
        self._show_frame('catalog')
        self._load_catalog()
    
    def _show_updates(self):
        """Show updates view."""
        self._show_frame('updates')
    
    def _show_suggestions(self):
        """Show suggestions view."""
        self._show_frame('suggestions')
        self._load_suggestions()
    
    def _show_settings(self):
        """Show settings view."""
        self._show_frame('settings')
    
    def _initial_load(self):
        """Initial data loading."""
        self._refresh_installed()
        self._update_obs_status()
    
    def _set_status(self, message: str):
        """Update status bar message."""
        if HAS_CTK:
            self.status_label.configure(text=message)
        else:
            self.status_label.configure(text=message)
    
    def _show_progress(self, show: bool = True):
        """Show/hide progress bar."""
        if HAS_CTK:
            if show:
                self.progress_bar.pack(side="right", padx=10)
            else:
                self.progress_bar.pack_forget()
    
    def _refresh_installed(self):
        """Refresh installed plugins list."""
        self._set_status("Scanning installed plugins...")
        
        def scan():
            plugins = self.scanner.scan_plugins()
            self.installed_plugins = plugins
            self.root.after(0, lambda: self._display_installed_plugins(plugins))
        
        threading.Thread(target=scan, daemon=True).start()
    
    def _display_installed_plugins(self, plugins):
        """Display installed plugins in the list."""
        # Clear existing
        if HAS_CTK:
            for widget in self.installed_list_frame.winfo_children():
                widget.destroy()
            
            if not plugins:
                label = ctk.CTkLabel(
                    self.installed_list_frame,
                    text="No plugins found. OBS may not be installed or no third-party plugins are detected.",
                    font=ctk.CTkFont(size=14)
                )
                label.pack(pady=50)
                self._set_status("No plugins found")
                return
            
            for plugin in plugins:
                self._create_installed_plugin_card(plugin)
            
            self._set_status(f"Found {len(plugins)} installed plugins")
        else:
            # Standard tkinter
            for item in self.installed_tree.get_children():
                self.installed_tree.delete(item)
            
            for plugin in plugins:
                status = "✓ Up to date"
                if plugin.matched_catalog_id:
                    catalog_plugin = self.db.get_plugin(plugin.matched_catalog_id)
                    if catalog_plugin and self._is_update_available(plugin.version, catalog_plugin.latest_version):
                        status = "⬆️ Update available"
                
                self.installed_tree.insert('', 'end', values=(plugin.name, plugin.version, status))
            
            self._set_status(f"Found {len(plugins)} installed plugins")
    
    def _create_installed_plugin_card(self, plugin):
        """Create a card for an installed plugin (CustomTkinter)."""
        card = ctk.CTkFrame(self.installed_list_frame)
        card.pack(fill="x", pady=5)
        
        # Left: Plugin info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        name_label = ctk.CTkLabel(info_frame, text=plugin.name, font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(anchor="w")
        
        version_text = f"Version: {plugin.version}"
        if plugin.matched_catalog_id:
            catalog_plugin = self.db.get_plugin(plugin.matched_catalog_id)
            if catalog_plugin and self._is_update_available(plugin.version, catalog_plugin.latest_version):
                version_text += f"  →  {catalog_plugin.latest_version} available"
        
        version_label = ctk.CTkLabel(info_frame, text=version_text, text_color="gray")
        version_label.pack(anchor="w")
        
        path_label = ctk.CTkLabel(info_frame, text=f"📁 {plugin.dll_path}", text_color="gray", font=ctk.CTkFont(size=11))
        path_label.pack(anchor="w")
        
        # Right: Actions
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(side="right", padx=10, pady=10)
        
        if plugin.matched_catalog_id:
            catalog_plugin = self.db.get_plugin(plugin.matched_catalog_id)
            if catalog_plugin:
                if self._is_update_available(plugin.version, catalog_plugin.latest_version):
                    update_btn = ctk.CTkButton(
                        actions_frame,
                        text="Update",
                        command=lambda p=plugin: self._update_plugin(p),
                        width=80,
                        fg_color="green",
                        hover_color="darkgreen"
                    )
                    update_btn.pack(pady=2)
        
        # Rollback button
        archives = self.plugin_manager.get_archive_info(plugin.matched_catalog_id or plugin.name)
        if archives:
            rollback_btn = ctk.CTkButton(
                actions_frame,
                text="Rollback",
                command=lambda p=plugin: self._show_rollback_dialog(p),
                width=80
            )
            rollback_btn.pack(pady=2)
        
        uninstall_btn = ctk.CTkButton(
            actions_frame,
            text="Uninstall",
            command=lambda p=plugin: self._uninstall_plugin(p),
            width=80,
            fg_color="red",
            hover_color="darkred"
        )
        uninstall_btn.pack(pady=2)
    
    def _load_catalog(self):
        """Load plugin catalog."""
        self._set_status("Loading plugin catalog...")
        
        plugins = self.db.get_all_plugins()
        self.catalog_plugins = plugins
        self._display_catalog_plugins(plugins)
    
    def _display_catalog_plugins(self, plugins):
        """Display catalog plugins."""
        if HAS_CTK:
            for widget in self.catalog_list_frame.winfo_children():
                widget.destroy()
            
            if not plugins:
                label = ctk.CTkLabel(self.catalog_list_frame, text="No plugins in catalog. Click 'Refresh Catalog' to fetch plugins.")
                label.pack(pady=50)
                return
            
            for plugin in plugins:
                self._create_catalog_plugin_card(plugin)
            
            self._set_status(f"Showing {len(plugins)} plugins")
        else:
            for item in self.catalog_tree.get_children():
                self.catalog_tree.delete(item)
            
            for plugin in plugins:
                self.catalog_tree.insert('', 'end', values=(plugin.name, plugin.author, plugin.latest_version, plugin.category))
    
    def _create_catalog_plugin_card(self, plugin):
        """Create a card for a catalog plugin (CustomTkinter)."""
        card = ctk.CTkFrame(self.catalog_list_frame)
        card.pack(fill="x", pady=5)
        
        # Left: Plugin info
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        # Name with badges
        name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_frame.pack(anchor="w")
        
        name_label = ctk.CTkLabel(name_frame, text=plugin.name, font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(side="left")
        
        if plugin.is_recommended:
            rec_badge = ctk.CTkLabel(name_frame, text="⭐ Recommended", text_color="gold", font=ctk.CTkFont(size=11))
            rec_badge.pack(side="left", padx=5)
        elif plugin.is_popular:
            pop_badge = ctk.CTkLabel(name_frame, text="🔥 Popular", text_color="orange", font=ctk.CTkFont(size=11))
            pop_badge.pack(side="left", padx=5)
        
        desc_label = ctk.CTkLabel(info_frame, text=plugin.description[:100] + "..." if len(plugin.description) > 100 else plugin.description, text_color="gray")
        desc_label.pack(anchor="w")
        
        meta_text = f"by {plugin.author} | v{plugin.latest_version} | {plugin.category}"
        meta_label = ctk.CTkLabel(info_frame, text=meta_text, text_color="gray", font=ctk.CTkFont(size=11))
        meta_label.pack(anchor="w")
        
        # Right: Actions
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(side="right", padx=10, pady=10)
        
        # Check if installed
        is_installed = any(p.matched_catalog_id == plugin.id for p in self.installed_plugins)
        
        if is_installed:
            installed_label = ctk.CTkLabel(actions_frame, text="✓ Installed", text_color="green")
            installed_label.pack(pady=2)
        else:
            install_btn = ctk.CTkButton(
                actions_frame,
                text="Install",
                command=lambda p=plugin: self._install_plugin(p),
                width=80,
                fg_color="green",
                hover_color="darkgreen"
            )
            install_btn.pack(pady=2)
        
        if plugin.github_url:
            github_btn = ctk.CTkButton(
                actions_frame,
                text="GitHub",
                command=lambda url=plugin.github_url: webbrowser.open(url),
                width=80
            )
            github_btn.pack(pady=2)
    
    def _filter_installed(self, event=None):
        """Filter installed plugins by search."""
        query = self.installed_search.get().lower() if HAS_CTK else ""
        
        if not query:
            self._display_installed_plugins(self.installed_plugins)
            return
        
        filtered = [p for p in self.installed_plugins if query in p.name.lower()]
        self._display_installed_plugins(filtered)
    
    def _filter_catalog(self, event=None):
        """Filter catalog plugins by search."""
        query = self.catalog_search.get().lower() if HAS_CTK else ""
        
        if not query:
            self._display_catalog_plugins(self.catalog_plugins)
            return
        
        filtered = [p for p in self.catalog_plugins if query in p.name.lower() or query in p.description.lower()]
        self._display_catalog_plugins(filtered)
    
    def _filter_by_category(self, category):
        """Filter catalog by category."""
        if category == "All Categories":
            self._display_catalog_plugins(self.catalog_plugins)
        else:
            filtered = [p for p in self.catalog_plugins if p.category == category]
            self._display_catalog_plugins(filtered)
    
    def _check_updates(self):
        """Check for plugin updates."""
        self._set_status("Checking for updates...")
        
        def check():
            updates = self.scanner.check_updates()
            self.root.after(0, lambda: self._display_updates(updates))
        
        threading.Thread(target=check, daemon=True).start()
    
    def _display_updates(self, updates):
        """Display available updates."""
        if HAS_CTK:
            for widget in self.updates_list_frame.winfo_children():
                widget.destroy()
            
            if not updates:
                label = ctk.CTkLabel(
                    self.updates_list_frame,
                    text="✓ All plugins are up to date!",
                    font=ctk.CTkFont(size=16),
                    text_color="green"
                )
                label.pack(pady=50)
                self._set_status("All plugins are up to date")
                return
            
            for update in updates:
                self._create_update_card(update)
            
            self._set_status(f"Found {len(updates)} updates available")
        else:
            for item in self.updates_tree.get_children():
                self.updates_tree.delete(item)
            
            for update in updates:
                self.updates_tree.insert('', 'end', values=(update['plugin_name'], update['current_version'], update['latest_version']))
    
    def _create_update_card(self, update):
        """Create a card for an available update."""
        card = ctk.CTkFrame(self.updates_list_frame)
        card.pack(fill="x", pady=5)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        name_label = ctk.CTkLabel(info_frame, text=update['plugin_name'], font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(anchor="w")
        
        version_text = f"{update['current_version']}  →  {update['latest_version']}"
        version_label = ctk.CTkLabel(info_frame, text=version_text, font=ctk.CTkFont(size=14))
        version_label.pack(anchor="w")
        
        if update.get('release_date'):
            date_label = ctk.CTkLabel(info_frame, text=f"Released: {update['release_date']}", text_color="gray")
            date_label.pack(anchor="w")
        
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(side="right", padx=10, pady=10)
        
        update_btn = ctk.CTkButton(
            actions_frame,
            text="Update",
            command=lambda u=update: self._do_update(u),
            width=100,
            fg_color="green",
            hover_color="darkgreen"
        )
        update_btn.pack()
    
    def _load_suggestions(self):
        """Load plugin suggestions."""
        self._set_status("Loading suggestions...")
        
        def load():
            suggestions = self.scanner.get_suggestions()
            self.root.after(0, lambda: self._display_suggestions(suggestions))
        
        threading.Thread(target=load, daemon=True).start()
    
    def _display_suggestions(self, suggestions):
        """Display plugin suggestions."""
        if HAS_CTK:
            for widget in self.suggestions_list_frame.winfo_children():
                widget.destroy()
            
            if not suggestions:
                label = ctk.CTkLabel(
                    self.suggestions_list_frame,
                    text="No suggestions available. You have most popular plugins installed!",
                    font=ctk.CTkFont(size=14)
                )
                label.pack(pady=50)
                return
            
            for suggestion in suggestions:
                self._create_suggestion_card(suggestion)
            
            self._set_status(f"Found {len(suggestions)} suggestions")
        else:
            for item in self.suggestions_tree.get_children():
                self.suggestions_tree.delete(item)
            
            for s in suggestions:
                self.suggestions_tree.insert('', 'end', values=(s['name'], s['category'], s['reason']))
    
    def _create_suggestion_card(self, suggestion):
        """Create a card for a plugin suggestion."""
        card = ctk.CTkFrame(self.suggestions_list_frame)
        card.pack(fill="x", pady=5)
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        
        name_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        name_frame.pack(anchor="w")
        
        name_label = ctk.CTkLabel(name_frame, text=suggestion['name'], font=ctk.CTkFont(size=16, weight="bold"))
        name_label.pack(side="left")
        
        reason_color = "gold" if suggestion['reason'] == "Recommended" else "orange"
        reason_label = ctk.CTkLabel(name_frame, text=f"  {suggestion['reason']}", text_color=reason_color)
        reason_label.pack(side="left")
        
        desc_label = ctk.CTkLabel(info_frame, text=suggestion['description'], text_color="gray")
        desc_label.pack(anchor="w")
        
        meta_text = f"by {suggestion['author']} | {suggestion['category']}"
        meta_label = ctk.CTkLabel(info_frame, text=meta_text, text_color="gray", font=ctk.CTkFont(size=11))
        meta_label.pack(anchor="w")
        
        actions_frame = ctk.CTkFrame(card, fg_color="transparent")
        actions_frame.pack(side="right", padx=10, pady=10)
        
        install_btn = ctk.CTkButton(
            actions_frame,
            text="Install",
            command=lambda s=suggestion: self._install_from_suggestion(s),
            width=80,
            fg_color="green",
            hover_color="darkgreen"
        )
        install_btn.pack()
    
    def _refresh_catalog(self):
        """Refresh plugin catalog from online sources."""
        self._set_status("Refreshing catalog from GitHub...")
        self._show_progress(True)
        
        def refresh():
            def progress_cb(current, total, message):
                percent = current / total if total > 0 else 0
                self.root.after(0, lambda: self._update_refresh_progress(percent, message))
            
            result = self.catalog_refresher.refresh_all(progress_callback=progress_cb)
            self.root.after(0, lambda: self._on_catalog_refreshed(result))
        
        threading.Thread(target=refresh, daemon=True).start()
    
    def _update_refresh_progress(self, percent, message):
        """Update refresh progress."""
        if HAS_CTK:
            self.progress_bar.set(percent)
        self._set_status(message)
    
    def _on_catalog_refreshed(self, result):
        """Handle catalog refresh completion."""
        self._show_progress(False)
        self._set_status(f"Catalog updated: {result.plugins_added} added, {result.plugins_updated} updated")
        self._load_catalog()
    
    # OBS Process Management
    def _start_obs_monitor(self):
        """Start monitoring OBS process status."""
        def monitor():
            while True:
                self.root.after(0, self._update_obs_status)
                import time
                time.sleep(2)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
    
    def _update_obs_status(self):
        """Update OBS running status display."""
        is_running = self.process_manager.is_obs_running()
        self.obs_running = is_running
        
        if HAS_CTK:
            if is_running:
                self.obs_status_label.configure(text="🟢 OBS: Running", text_color="green")
                self.kill_obs_btn.pack(pady=(5, 0))
            else:
                self.obs_status_label.configure(text="🔴 OBS: Not Running", text_color="red")
                self.kill_obs_btn.pack_forget()
        else:
            status_text = "OBS: Running" if is_running else "OBS: Not Running"
            self.obs_status_label.configure(text=status_text)
            
            if is_running:
                self.kill_obs_btn.pack(pady=5)
            else:
                self.kill_obs_btn.pack_forget()
    
    def _kill_obs(self):
        """Kill OBS process."""
        if HAS_CTK:
            dialog = ctk.CTkInputDialog(text="Are you sure you want to kill OBS? Type 'yes' to confirm:", title="Kill OBS")
            response = dialog.get_input()
            if response and response.lower() == 'yes':
                self._set_status("Killing OBS...")
                success = self.process_manager.kill_obs()
                if success:
                    self._set_status("OBS terminated")
                else:
                    self._set_status("Failed to kill OBS")
        else:
            if messagebox.askyesno("Kill OBS", "Are you sure you want to kill OBS?"):
                self.process_manager.kill_obs()
    
    # Plugin Operations
    def _install_plugin(self, plugin):
        """Install a plugin from catalog."""
        if self.obs_running:
            self._show_obs_running_error()
            return
        
        self._set_status(f"Installing {plugin.name}...")
        self._show_progress(True)
        
        def install():
            def progress_cb(progress):
                percent = progress.percent / 100
                self.root.after(0, lambda: self.progress_bar.set(percent) if HAS_CTK else None)
            
            result = self.plugin_manager.download_and_install(
                plugin.id,
                plugin.download_url,
                plugin.latest_version,
                progress_callback=progress_cb
            )
            self.root.after(0, lambda: self._on_install_complete(result))
        
        threading.Thread(target=install, daemon=True).start()
    
    def _install_from_suggestion(self, suggestion):
        """Install a suggested plugin."""
        plugin = self.db.get_plugin(suggestion['plugin_id'])
        if plugin:
            self._install_plugin(plugin)
    
    def _update_plugin(self, plugin):
        """Update an installed plugin."""
        if self.obs_running:
            self._show_obs_running_error()
            return
        
        catalog_plugin = self.db.get_plugin(plugin.matched_catalog_id)
        if catalog_plugin:
            self._set_status(f"Updating {plugin.name}...")
            self._show_progress(True)
            
            def update():
                def progress_cb(progress):
                    percent = progress.percent / 100
                    self.root.after(0, lambda: self.progress_bar.set(percent) if HAS_CTK else None)
                
                result = self.plugin_manager.download_and_install(
                    catalog_plugin.id,
                    catalog_plugin.download_url,
                    catalog_plugin.latest_version,
                    progress_callback=progress_cb
                )
                self.root.after(0, lambda: self._on_install_complete(result))
            
            threading.Thread(target=update, daemon=True).start()
    
    def _do_update(self, update_info):
        """Perform a plugin update."""
        if self.obs_running:
            self._show_obs_running_error()
            return
        
        plugin = self.db.get_plugin(update_info['plugin_id'])
        if plugin:
            self._install_plugin(plugin)
    
    def _on_install_complete(self, result):
        """Handle installation completion."""
        self._show_progress(False)
        
        if result.success:
            self._set_status(f"✓ {result.message}")
            self._refresh_installed()
        else:
            self._set_status(f"✗ {result.message}")
            if HAS_CTK:
                dialog = ctk.CTkInputDialog(text=result.message, title="Installation Failed")
            else:
                messagebox.showerror("Installation Failed", result.message)
    
    def _uninstall_plugin(self, plugin):
        """Uninstall a plugin."""
        if self.obs_running:
            self._show_obs_running_error()
            return
        
        # Confirm
        if HAS_CTK:
            dialog = ctk.CTkInputDialog(
                text=f"Type 'uninstall' to confirm removing {plugin.name}:",
                title="Confirm Uninstall"
            )
            response = dialog.get_input()
            if response != 'uninstall':
                return
        else:
            if not messagebox.askyesno("Confirm Uninstall", f"Are you sure you want to uninstall {plugin.name}?"):
                return
        
        self._set_status(f"Uninstalling {plugin.name}...")
        
        result = self.plugin_manager.uninstall_plugin(plugin.matched_catalog_id or plugin.name)
        
        if result.success:
            self._set_status(f"✓ {plugin.name} uninstalled")
            self._refresh_installed()
        else:
            self._set_status(f"✗ {result.message}")
    
    def _show_rollback_dialog(self, plugin):
        """Show rollback version selection dialog."""
        if self.obs_running:
            self._show_obs_running_error()
            return
        
        archives = self.plugin_manager.get_archive_info(plugin.matched_catalog_id or plugin.name)
        
        if not archives:
            self._set_status("No archived versions available for rollback")
            return
        
        if HAS_CTK:
            # Create rollback dialog
            dialog = ctk.CTkToplevel(self.root)
            dialog.title(f"Rollback {plugin.name}")
            dialog.geometry("400x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            label = ctk.CTkLabel(dialog, text="Select version to rollback to:", font=ctk.CTkFont(size=14))
            label.pack(pady=10)
            
            # Version list
            version_frame = ctk.CTkScrollableFrame(dialog)
            version_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            for archive in archives:
                btn = ctk.CTkButton(
                    version_frame,
                    text=f"v{archive['version']} ({archive['archive_date'][:10]})",
                    command=lambda v=archive['version']: self._do_rollback(plugin, v, dialog)
                )
                btn.pack(fill="x", pady=5)
            
            cancel_btn = ctk.CTkButton(dialog, text="Cancel", command=dialog.destroy)
            cancel_btn.pack(pady=10)
    
    def _do_rollback(self, plugin, version, dialog=None):
        """Perform rollback to specific version."""
        if dialog:
            dialog.destroy()
        
        self._set_status(f"Rolling back {plugin.name} to v{version}...")
        
        result = self.plugin_manager.rollback_plugin(plugin.matched_catalog_id or plugin.name, version)
        
        if result.success:
            self._set_status(f"✓ {result.message}")
            self._refresh_installed()
        else:
            self._set_status(f"✗ {result.message}")
    
    def _show_obs_running_error(self):
        """Show error when trying to modify while OBS is running."""
        if HAS_CTK:
            dialog = ctk.CTkToplevel(self.root)
            dialog.title("OBS is Running")
            dialog.geometry("400x150")
            dialog.transient(self.root)
            dialog.grab_set()
            
            label = ctk.CTkLabel(
                dialog,
                text="⚠️ Cannot modify plugins while OBS is running.\n\nPlease close OBS first or use 'Kill OBS' button.",
                font=ctk.CTkFont(size=14)
            )
            label.pack(pady=20)
            
            btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
            btn_frame.pack(pady=10)
            
            kill_btn = ctk.CTkButton(
                btn_frame,
                text="Kill OBS",
                command=lambda: [self._kill_obs(), dialog.destroy()],
                fg_color="red",
                hover_color="darkred"
            )
            kill_btn.pack(side="left", padx=5)
            
            close_btn = ctk.CTkButton(btn_frame, text="OK", command=dialog.destroy)
            close_btn.pack(side="left", padx=5)
        else:
            messagebox.showwarning(
                "OBS is Running",
                "Cannot modify plugins while OBS is running.\nPlease close OBS first."
            )
    
    # Settings
    def _browse_obs_path(self):
        """Browse for OBS installation path."""
        if HAS_CTK:
            from tkinter import filedialog
        
        path = filedialog.askdirectory(title="Select OBS Installation Folder")
        if path:
            self.obs_path_entry.delete(0, 'end')
            self.obs_path_entry.insert(0, path)
    
    def _detect_obs_path(self):
        """Auto-detect OBS installation path."""
        path = self.config.detect_obs_installation()
        if path:
            self.obs_path_entry.delete(0, 'end')
            self.obs_path_entry.insert(0, path)
            self._set_status(f"Detected OBS at: {path}")
        else:
            self._set_status("Could not detect OBS installation")
    
    def _save_settings(self):
        """Save settings."""
        obs_path = self.obs_path_entry.get()
        
        if obs_path and obs_path != "Not detected":
            if self.config.set_obs_path(obs_path):
                self._set_status("Settings saved")
            else:
                self._set_status("Invalid OBS path")
                return
        
        # Save archive count
        if HAS_CTK:
            try:
                count = int(self.archive_count_var.get())
                self.config.config.max_archive_versions = count
            except ValueError:
                pass
        
        self.config.save()
        self._set_status("Settings saved successfully")
    
    def _cleanup_temp(self):
        """Clean up temporary files."""
        count = self.plugin_manager.cleanup_temp_files()
        self._set_status(f"Cleaned up {count} temporary files")
    
    def _export_catalog(self):
        """Export catalog to file."""
        if HAS_CTK:
            from tkinter import filedialog
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json")],
            title="Export Catalog"
        )
        
        if filepath:
            self.catalog_refresher.export_to_file(filepath)
            self._set_status(f"Catalog exported to {filepath}")
    
    def _import_catalog(self):
        """Import catalog from file."""
        if HAS_CTK:
            from tkinter import filedialog
        
        filepath = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json")],
            title="Import Catalog"
        )
        
        if filepath:
            result = self.catalog_refresher.import_from_file(filepath)
            self._set_status(f"Imported {result.plugins_added} plugins")
            self._load_catalog()
    
    def _is_update_available(self, current: str, latest: str) -> bool:
        """Check if update is available."""
        from packaging import version
        import re
        
        try:
            current_clean = re.sub(r'[^0-9.]', '', current)
            latest_clean = re.sub(r'[^0-9.]', '', latest)
            
            if not current_clean or not latest_clean:
                return False
            
            return version.parse(latest_clean) > version.parse(current_clean)
        except Exception:
            return current != latest and current != "Unknown"
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


def main():
    """Main entry point."""
    app = OBSPluginManagerGUI()
    app.run()


if __name__ == "__main__":
    main()
