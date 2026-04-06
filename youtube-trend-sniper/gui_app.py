"""
YouTube Trend Sniper - Enhanced GUI Version
Features: Line charts, Dark/Light mode, Auto-refresh, Clickable video links,
Trending hashtags, Separate chart window, Organized data storage, Color-coded charts
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import webbrowser
import requests
import json
from datetime import datetime, timedelta
from collections import defaultdict
import threading
import time
import os
import re

# Try to import matplotlib for charts
try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.dates import DateFormatter, DayLocator
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

# YouTube API Configuration
API_KEY = "AIzaSyBYJadz_1zfW5mU2ZbFPEEF5-hG9Lsf0P8"
BASE_URL = "https://www.googleapis.com/youtube/v3"

# Data folder
DATA_FOLDER = "data"

# Faceless-friendly niche keywords
FACELESS_NICHES = {
    "Gaming": ["gaming", "gameplay", "walkthrough", "no commentary", "speedrun", "minecraft", "roblox", "valorant", "fortnite", "apex"],
    "Tech": ["tech review", "software tutorial", "screen recording", "productivity", "how to", "tutorial", "guide"],
    "Finance": ["crypto", "stock market", "trading", "finance", "investing", "money", "chart analysis"],
    "AI Art": ["AI art", "midjourney", "stable diffusion", "ai generated", "digital art", "generative art"],
    "Educational": ["facts", "educational", "explained", "documentary", "science", "history"],
    "ASMR": ["ASMR", "relaxing", "ambient", "sounds", "sleep", "meditation"],
    "Motivation": ["motivation", "inspiration", "quotes", "success", "mindset"],
    "Compilations": ["compilation", "best moments", "funny moments", "fails", "highlights"],
    "Music": ["lofi", "ambient music", "study music", "focus music", "beats"],
    "Animation": ["animation", "animated", "3d", "motion graphics", "visual effects"]
}

# Chart colors (distinct, vibrant)
CHART_COLORS = [
    "#e94560",  # Red/Pink - Hot
    "#f39c12",  # Orange - Rising
    "#27ae60",  # Green - Stable
    "#3498db",  # Blue
    "#9b59b6",  # Purple
    "#1abc9c",  # Teal
    "#e74c3c",  # Red
    "#f1c40f",  # Yellow
    "#16a085",  # Dark Teal
    "#8e44ad",  # Dark Purple
]

# Theme colors
DARK_THEME = {
    "bg": "#1a1a2e",
    "fg": "#ffffff",
    "table_bg": "#16213e",
    "table_fg": "#ffffff",
    "header_bg": "#0f3460",
    "header_fg": "#ffffff",
    "hot": "#e94560",
    "rising": "#f39c12",
    "stable": "#27ae60",
    "button_bg": "#0f3460",
    "button_fg": "#ffffff",
    "chart_bg": "#1a1a2e",
    "link_color": "#3498db",
    "tag_bg": "#0f3460"
}

LIGHT_THEME = {
    "bg": "#f5f6fa",
    "fg": "#2c3e50",
    "table_bg": "#ffffff",
    "table_fg": "#2c3e50",
    "header_bg": "#3498db",
    "header_fg": "#ffffff",
    "hot": "#e74c3c",
    "rising": "#f39c12",
    "stable": "#27ae60",
    "button_bg": "#3498db",
    "button_fg": "#ffffff",
    "chart_bg": "#ffffff",
    "link_color": "#2980b9",
    "tag_bg": "#3498db"
}


class ChartWindow:
    """Separate window for detailed chart viewing"""

    def __init__(self, parent, historical_data, theme):
        self.window = tk.Toplevel(parent)
        self.window.title("📊 Detailed Trend Analysis")
        self.window.geometry("1200x800")
        self.window.configure(bg=theme["bg"])

        self.historical_data = historical_data
        self.theme = theme

        self.create_ui()
        self.update_chart()

    def create_ui(self):
        """Create the chart window UI"""
        # Title
        title = tk.Label(
            self.window,
            text="📊 7-DAY TREND ANALYSIS - DETAILED VIEW",
            font=("Arial", 18, "bold"),
            bg=self.theme["bg"],
            fg=self.theme["fg"]
        )
        title.pack(pady=20)

        # Chart frame
        chart_frame = tk.Frame(self.window, bg=self.theme["bg"])
        chart_frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.fig, (self.ax1, self.ax2) = plt.subplots(2, 1, figsize=(10, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        # Stats panel
        stats_frame = tk.Frame(self.window, bg=self.theme["bg"])
        stats_frame.pack(fill="x", padx=20, pady=10)

        self.stats_text = scrolledtext.ScrolledText(
            stats_frame,
            height=8,
            font=("Arial", 10),
            bg=self.theme["table_bg"],
            fg=self.theme["fg"],
            relief="flat",
            padx=10,
            pady=10
        )
        self.stats_text.pack(fill="both", expand=True)

        # Apply theme
        self.fig.patch.set_facecolor(self.theme["chart_bg"])

    def update_chart(self):
        """Update the charts with detailed analysis"""
        if not MATPLOTLIB_AVAILABLE:
            return

        self.ax1.clear()
        self.ax2.clear()

        # Get last 7 days of data
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)

        # Collect trend scores over time
        trend_history = defaultdict(list)
        dates = sorted([d for d in self.historical_data.keys() if d >= seven_days_ago])

        for date in dates:
            for niche, data in self.historical_data[date].items():
                if "avg_score" in data:
                    trend_history[niche].append((date, data["avg_score"]))

        # Sort by average score
        sorted_niches = sorted(
            trend_history.items(),
            key=lambda x: sum(v[1] for v in x[1]) / len(x[1]) if x[1] else 0,
            reverse=True
        )[:5]

        # Chart 1: Line chart for top 5 niches
        for i, (niche, data_points) in enumerate(sorted_niches):
            if data_points:
                dates_list = [dp[0] for dp in data_points]
                scores = [dp[1] for dp in data_points]
                color = CHART_COLORS[i % len(CHART_COLORS)]
                self.ax1.plot(dates_list, scores, marker='o', linewidth=3,
                            markersize=8, label=niche, color=color)
                self.ax1.fill_between(dates_list, scores, alpha=0.2, color=color)

        self.ax1.set_xlabel('Date', color=self.theme["fg"], fontsize=12)
        self.ax1.set_ylabel('Trend Score', color=self.theme["fg"], fontsize=12)
        self.ax1.set_title('Top 5 Niches - 7 Day Performance', color=self.theme["fg"],
                         fontsize=14, fontweight='bold')
        self.ax1.legend(loc='best', fontsize=10)
        self.ax1.grid(True, alpha=0.3, linestyle='--')
        self.ax1.xaxis.set_major_formatter(DateFormatter('%m-%d'))
        self.ax1.xaxis.set_major_locator(DayLocator(interval=1))

        # Chart 2: Bar chart comparison
        if dates:
            latest_date = dates[-1]
            current_scores = []
            niche_names = []
            colors = []

            for i, (niche, data_points) in enumerate(sorted_niches):
                if data_points:
                    latest_score = data_points[-1][1]
                    current_scores.append(latest_score)
                    niche_names.append(niche)
                    colors.append(CHART_COLORS[i % len(CHART_COLORS)])

            bars = self.ax2.bar(niche_names, current_scores, color=colors, alpha=0.8)
            self.ax2.set_xlabel('Niche', color=self.theme["fg"], fontsize=12)
            self.ax2.set_ylabel('Current Trend Score', color=self.theme["fg"], fontsize=12)
            self.ax2.set_title('Current Performance Comparison', color=self.theme["fg"],
                             fontsize=14, fontweight='bold')

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                self.ax2.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:,.0f}',
                            ha='center', va='bottom', fontsize=9)

        # Apply theme colors to both charts
        for ax in [self.ax1, self.ax2]:
            ax.set_facecolor(self.theme["chart_bg"])
            ax.tick_params(colors=self.theme["fg"], labelsize=10)
            ax.xaxis.label.set_color(self.theme["fg"])
            ax.yaxis.label.set_color(self.theme["fg"])
            ax.title.set_color(self.theme["fg"])
            for spine in ax.spines.values():
                spine.set_color(self.theme["fg"])

        self.canvas.draw()

        # Update stats
        self.update_stats(sorted_niches)

    def update_stats(self, sorted_niches):
        """Update the stats panel"""
        self.stats_text.config(state="normal")
        self.stats_text.delete("1.0", "end")

        stats_text = "📊 DETAILED ANALYSIS STATS\n\n"

        for i, (niche, data_points) in enumerate(sorted_niches):
            if data_points:
                scores = [dp[1] for dp in data_points]
                avg_score = sum(scores) / len(scores)
                max_score = max(scores)
                min_score = min(scores)
                growth = ((scores[-1] - scores[0]) / scores[0] * 100) if len(scores) > 1 and scores[0] > 0 else 0

                emoji = "🔥" if i < 3 else "📈" if i < 6 else "📊"
                stats_text += f"{emoji} {niche.upper()}\n"
                stats_text += f"   Average Score: {avg_score:,.0f}\n"
                stats_text += f"   Peak Score: {max_score:,.0f}\n"
                stats_text += f"   7-Day Growth: {growth:+.1f}%\n"
                stats_text += f"   Data Points: {len(data_points)}\n\n"

        self.stats_text.insert("1.0", stats_text)
        self.stats_text.config(state="disabled")


class YouTubeTrendSniper:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Trend Sniper 🎯")
        self.root.geometry("1500x950")

        self.current_theme = DARK_THEME
        self.results = {}
        self.auto_refresh = True
        self.refresh_interval = 20 * 60  # 20 minutes
        self.last_refresh = None
        self.historical_data = {}
        self.top_hashtags = {}

        # Ensure data folder exists
        os.makedirs(DATA_FOLDER, exist_ok=True)

        self.load_historical_data()
        self.create_ui()
        self.start_auto_refresh()
        self.analyze_trends()

    def load_historical_data(self):
        """Load historical data from data folder"""
        try:
            if os.path.exists(DATA_FOLDER):
                for filename in os.listdir(DATA_FOLDER):
                    if filename.startswith("trend_analysis_") and filename.endswith(".json"):
                        filepath = os.path.join(DATA_FOLDER, filename)
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                            date_str = filename.replace("trend_analysis_", "").replace(".json", "")
                            timestamp = datetime.strptime(date_str, "%Y%m%d_%H%M%S")
                            self.historical_data[timestamp] = data

        except Exception as e:
            print(f"Error loading historical data: {e}")

    def create_ui(self):
        """Create the main UI"""
        self.apply_theme()

        # Top frame with title and controls
        top_frame = tk.Frame(self.root, bg=self.current_theme["bg"])
        top_frame.pack(fill="x", padx=10, pady=10)

        # Title
        title_label = tk.Label(
            top_frame,
            text="🎯 YouTube Trend Sniper Pro",
            font=("Arial", 26, "bold"),
            bg=self.current_theme["bg"],
            fg=self.current_theme["fg"]
        )
        title_label.pack(side="left", padx=10)

        # Controls frame
        controls_frame = tk.Frame(top_frame, bg=self.current_theme["bg"])
        controls_frame.pack(side="right", padx=10)

        # Theme toggle button
        self.theme_btn = tk.Button(
            controls_frame,
            text="🌙 Dark",
            command=self.toggle_theme,
            font=("Arial", 11, "bold"),
            bg=self.current_theme["button_bg"],
            fg=self.current_theme["button_fg"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.theme_btn.pack(side="left", padx=3)

        # Refresh button
        refresh_btn = tk.Button(
            controls_frame,
            text="🔄 Refresh",
            command=self.manual_refresh,
            font=("Arial", 11, "bold"),
            bg=self.current_theme["button_bg"],
            fg=self.current_theme["button_fg"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )
        refresh_btn.pack(side="left", padx=3)

        # Chart window button
        self.chart_btn = tk.Button(
            controls_frame,
            text="📊 Full Chart",
            command=self.open_chart_window,
            font=("Arial", 11, "bold"),
            bg=self.current_theme["button_bg"],
            fg=self.current_theme["button_fg"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.chart_btn.pack(side="left", padx=3)

        # 7-day trend button
        self.trend_btn = tk.Button(
            controls_frame,
            text="📈 7-Day Trend",
            command=self.open_7day_trend,
            font=("Arial", 11, "bold"),
            bg=self.current_theme["button_bg"],
            fg=self.current_theme["button_fg"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )
        self.trend_btn.pack(side="left", padx=3)

        # Data folder button
        data_btn = tk.Button(
            controls_frame,
            text="📁 Data",
            command=self.open_data_folder,
            font=("Arial", 11, "bold"),
            bg=self.current_theme["button_bg"],
            fg=self.current_theme["button_fg"],
            relief="flat",
            padx=12,
            pady=6,
            cursor="hand2"
        )
        data_btn.pack(side="left", padx=3)

        # Auto-refresh toggle
        self.auto_refresh_var = tk.BooleanVar(value=True)
        self.auto_refresh_cb = tk.Checkbutton(
            controls_frame,
            text="Auto-refresh (20m)",
            variable=self.auto_refresh_var,
            command=self.toggle_auto_refresh,
            font=("Arial", 10, "bold"),
            bg=self.current_theme["bg"],
            fg=self.current_theme["fg"],
            selectcolor=self.current_theme["header_bg"],
            activebackground=self.current_theme["bg"],
            activeforeground=self.current_theme["fg"],
            cursor="hand2"
        )
        self.auto_refresh_cb.pack(side="left", padx=8)

        # Last refresh label
        self.refresh_label = tk.Label(
            controls_frame,
            text="Last: --:--:--",
            font=("Arial", 10),
            bg=self.current_theme["bg"],
            fg=self.current_theme["fg"]
        )
        self.refresh_label.pack(side="left", padx=5)

        # Main content frame
        content_frame = tk.Frame(self.root, bg=self.current_theme["bg"])
        content_frame.pack(fill="both", expand=True, padx=10, pady=5)

        # Left panel - Main table
        left_panel = tk.Frame(content_frame, bg=self.current_theme["bg"])
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 5))

        # Table title
        table_title = tk.Label(
            left_panel,
            text="📊 TREND ANALYSIS",
            font=("Arial", 14, "bold"),
            bg=self.current_theme["bg"],
            fg=self.current_theme["fg"]
        )
        table_title.pack(pady=(0, 10))

        # Create main table
        self.create_main_table(left_panel)

        # Right panel - Side panels
        right_panel = tk.Frame(content_frame, bg=self.current_theme["bg"])
        right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

        # Recommendation panel
        self.create_recommendation_panel(right_panel)

        # Hashtags panel
        self.create_hashtags_panel(right_panel)

        # Mini chart panel
        self.create_mini_chart_panel(right_panel)

        # Content ideas panel
        self.create_content_ideas_panel(right_panel)

    def create_main_table(self, parent):
        """Create the main trend analysis table"""
        table_frame = tk.Frame(parent, bg=self.current_theme["bg"])
        table_frame.pack(fill="both", expand=True)

        scrollbar = tk.Scrollbar(table_frame)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(
            table_frame,
            columns=("Rank", "Niche", "Growth", "Trend Score", "Total Views", "Top Video", "Link"),
            show="headings",
            yscrollcommand=scrollbar.set,
            selectmode="browse"
        )

        scrollbar.config(command=self.tree.yview)

        # Column headings and widths
        columns = [
            ("Rank", 70, "center"),
            ("Niche", 120, "center"),
            ("Growth", 100, "center"),
            ("Trend Score", 130, "center"),
            ("Total Views", 130, "center"),
            ("Top Video", 400, "w"),
            ("Link", 100, "center")
        ]

        for col, width, align in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor=align)

        # Click handler for links
        self.tree.bind("<Double-1>", self.on_table_double_click)

        self.style_treeview()
        self.tree.pack(fill="both", expand=True)

    def on_table_double_click(self, event):
        """Handle double-click on table rows"""
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            values = item["values"]
            if len(values) >= 7 and values[6] != "N/A":
                video_id = values[6]
                url = f"https://youtube.com/watch?v={video_id}"
                webbrowser.open(url)

    def create_recommendation_panel(self, parent):
        """Create the recommendation panel"""
        rec_frame = tk.LabelFrame(
            parent,
            text="💡 TOP RECOMMENDATION",
            font=("Arial", 12, "bold"),
            bg=self.current_theme["bg"],
            fg=self.current_theme["fg"],
            padx=10,
            pady=10
        )
        rec_frame.pack(fill="x", pady=(0, 8))

        self.rec_label = tk.Label(
            rec_frame,
            text="Analyzing trends...",
            font=("Arial", 10),
            bg=self.current_theme["bg"],
            fg=self.current_theme["fg"],
            justify="left",
            wraplength=500
        )
        self.rec_label.pack()

    def create_hashtags_panel(self, parent):
        """Create the trending hashtags panel"""
        tags_frame = tk.LabelFrame(
            parent,
            text="#️⃣ TRENDING HASHTAGS",
            font=("Arial", 12, "bold"),
            bg=self.current_theme["bg"],
            fg=self.current_theme["fg"],
            padx=10,
            pady=10
        )
        tags_frame.pack(fill="x", pady=(0, 8))

        self.tags_text = scrolledtext.ScrolledText(
            tags_frame,
            height=5,
            font=("Arial", 9),
            bg=self.current_theme["table_bg"],
            fg=self.current_theme["fg"],
            relief="flat",
            padx=8,
            pady=8
        )
        self.tags_text.pack(fill="both", expand=True)
        self.tags_text.insert("1.0", "Hashtags will appear here...")
        self.tags_text.config(state="disabled")

    def create_mini_chart_panel(self, parent):
        """Create the mini chart panel"""
        chart_frame = tk.LabelFrame(
            parent,
            text="📈 QUICK TREND",
            font=("Arial", 12, "bold"),
            bg=self.current_theme["bg"],
            fg=self.current_theme["fg"],
            padx=10,
            pady=10
        )
        chart_frame.pack(fill="both", expand=True, pady=(0, 8))

        if MATPLOTLIB_AVAILABLE:
            self.fig_mini, self.ax_mini = plt.subplots(figsize=(5, 3), dpi=100)
            self.canvas_mini = FigureCanvasTkAgg(self.fig_mini, master=chart_frame)
            self.canvas_mini.get_tk_widget().pack(fill="both", expand=True)
        else:
            no_chart = tk.Label(
                chart_frame,
                text="Install matplotlib: pip install matplotlib",
                font=("Arial", 10),
                bg=self.current_theme["bg"],
                fg=self.current_theme["fg"]
            )
            no_chart.pack(pady=15)

    def create_content_ideas_panel(self, parent):
        """Create the content ideas panel"""
        ideas_frame = tk.LabelFrame(
            parent,
            text="📋 CONTENT IDEAS",
            font=("Arial", 12, "bold"),
            bg=self.current_theme["bg"],
            fg=self.current_theme["fg"],
            padx=10,
            pady=10
        )
        ideas_frame.pack(fill="x", pady=(0, 8))

        self.ideas_text = scrolledtext.ScrolledText(
            ideas_frame,
            height=6,
            font=("Arial", 9),
            bg=self.current_theme["table_bg"],
            fg=self.current_theme["fg"],
            relief="flat",
            padx=8,
            pady=8
        )
        self.ideas_text.pack(fill="both", expand=True)
        self.ideas_text.insert("1.0", "Content ideas will appear here...")
        self.ideas_text.config(state="disabled")

    def apply_theme(self):
        """Apply the current theme to the UI"""
        self.root.configure(bg=self.current_theme["bg"])

    def toggle_theme(self):
        """Toggle between dark and light theme"""
        if self.current_theme == DARK_THEME:
            self.current_theme = LIGHT_THEME
            self.theme_btn.config(text="☀️ Light")
        else:
            self.current_theme = DARK_THEME
            self.theme_btn.config(text="🌙 Dark")

        self.apply_theme()
        self.style_treeview()
        self.update_mini_chart()

        # Update all labels
        for widget in self.root.winfo_children():
            self._update_widget_theme(widget)

    def _update_widget_theme(self, widget):
        """Recursively update widget themes"""
        try:
            if isinstance(widget, (tk.Label, tk.LabelFrame)):
                widget.config(bg=self.current_theme["bg"], fg=self.current_theme["fg"])
            elif isinstance(widget, tk.Frame):
                widget.config(bg=self.current_theme["bg"])
            elif isinstance(widget, tk.Checkbutton):
                widget.config(bg=self.current_theme["bg"], fg=self.current_theme["fg"])
            elif isinstance(widget, tk.Button):
                widget.config(bg=self.current_theme["button_bg"], fg=self.current_theme["button_fg"])

            for child in widget.winfo_children():
                self._update_widget_theme(child)
        except:
            pass

    def style_treeview(self):
        """Style the treeview based on current theme"""
        style = ttk.Style()

        if self.current_theme == DARK_THEME:
            style.theme_use("clam")
            style.configure("Treeview",
                          background=self.current_theme["table_bg"],
                          foreground=self.current_theme["table_fg"],
                          fieldbackground=self.current_theme["table_bg"],
                          rowheight=35)
            style.configure("Treeview.Heading",
                          background=self.current_theme["header_bg"],
                          foreground=self.current_theme["header_fg"],
                          font=("Arial", 11, "bold"))
            style.map("Treeview",
                     background=[("selected", self.current_theme["hot"])],
                     foreground=[("selected", "white")])
        else:
            style.theme_use("default")
            style.configure("Treeview",
                          background=self.current_theme["table_bg"],
                          foreground=self.current_theme["table_fg"],
                          rowheight=35)
            style.configure("Treeview.Heading",
                          background=self.current_theme["header_bg"],
                          foreground=self.current_theme["header_fg"],
                          font=("Arial", 11, "bold"))
            style.map("Treeview",
                     background=[("selected", self.current_theme["hot"])],
                     foreground=[("selected", "white")])

        self.tree.update()

    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        self.auto_refresh = self.auto_refresh_var.get()

    def start_auto_refresh(self):
        """Start the auto-refresh timer"""
        def refresh_loop():
            while True:
                if self.auto_refresh:
                    self.root.after(0, self.analyze_trends)
                time.sleep(self.refresh_interval)

        refresh_thread = threading.Thread(target=refresh_loop, daemon=True)
        refresh_thread.start()

    def manual_refresh(self):
        """Manually refresh the analysis"""
        self.analyze_trends()

    def open_chart_window(self):
        """Open detailed chart window"""
        if not self.historical_data:
            messagebox.showinfo("Info", "No historical data available yet. Run analysis first.")
            return

        ChartWindow(self.root, self.historical_data, self.current_theme)

    def open_7day_trend(self):
        """Open 7-day trend analysis"""
        self.open_chart_window()

    def open_data_folder(self):
        """Open the data folder"""
        import subprocess
        import platform

        data_path = os.path.join(os.getcwd(), DATA_FOLDER)
        os.makedirs(data_path, exist_ok=True)

        try:
            if platform.system() == "Windows":
                subprocess.Popen(f'explorer "{data_path}"')
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", data_path])
            else:  # Linux
                subprocess.Popen(["xdg-open", data_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open data folder: {str(e)}")

    def analyze_trends(self):
        """Main analysis function"""
        def run_analysis():
            try:
                self.root.after(0, lambda: self.rec_label.config(text="🔄 Analyzing..."))

                results = self._analyze_niches()

                if results:
                    self.root.after(0, lambda: self.update_ui(results))
                    self.save_results(results)
                else:
                    self.root.after(0, lambda: self.rec_label.config(text="❌ No results"))

            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"Analysis failed: {str(e)}"))

        analysis_thread = threading.Thread(target=run_analysis, daemon=True)
        analysis_thread.start()

    def _analyze_niches(self):
        """Analyze all niches"""
        results = {}
        niche_hashtags = {}

        for niche, keywords in FACELESS_NICHES.items():
            niche_videos = []
            hashtags = set()

            for keyword in keywords[:3]:
                videos = self.search_videos(keyword, max_results=10)
                for video in videos:
                    # Extract hashtags from title and description
                    title = video["snippet"]["title"]
                    description = video["snippet"].get("description", "")

                    # Find hashtags
                    hashtags.update(self.extract_hashtags(title))
                    hashtags.update(self.extract_hashtags(description))

                niche_videos.extend(videos)

            if niche_videos:
                scores = [self.calculate_video_score(v) for v in niche_videos]
                avg_score = sum(scores) / len(scores)
                total_views = sum(int(v["statistics"].get("viewCount", 0)) for v in niche_videos)
                top_video = max(niche_videos, key=lambda v: int(v["statistics"].get("viewCount", 0)))

                results[niche] = {
                    "avg_score": avg_score,
                    "total_views": total_views,
                    "video_count": len(niche_videos),
                    "top_video": top_video,
                    "hashtags": list(hashtags)[:15]  # Top 15 hashtags
                }

                niche_hashtags[niche] = list(hashtags)[:15]

        self.top_hashtags = niche_hashtags
        return results

    def extract_hashtags(self, text):
        """Extract hashtags from text"""
        # Find hashtags (including #)
        hashtags = re.findall(r'#\w+', text.lower())

        # Also find common tags without #
        words = re.findall(r'\b\w+\b', text.lower())
        common_tags = [w for w in words if len(w) > 3 and w in words]

        return hashtags + [f"#{tag}" for tag in common_tags if len(tag) > 4]

    def search_videos(self, query, max_results=20):
        """Search for videos"""
        url = f"{BASE_URL}/search"
        params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "order": "viewCount",
            "maxResults": max_results,
            "key": API_KEY
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            video_ids = [item["id"]["videoId"] for item in response.json().get("items", [])]
            return self.get_video_stats(video_ids)
        except:
            return []

    def get_video_stats(self, video_ids):
        """Get video statistics"""
        url = f"{BASE_URL}/videos"
        params = {
            "part": "snippet,statistics",
            "id": ",".join(video_ids[:50]),
            "key": API_KEY
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json().get("items", [])
        except:
            return []

    def calculate_video_score(self, video):
        """Calculate video score"""
        views = int(video["statistics"].get("viewCount", 0))
        published_date = video["snippet"]["publishedAt"]
        pub_dt = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
        days_ago = (datetime.now(pub_dt.tzinfo) - pub_dt).days
        if days_ago == 0:
            days_ago = 0.1
        return views / days_ago

    def update_ui(self, results):
        """Update the UI with results"""
        self.results = results

        # Update last refresh time
        self.last_refresh = datetime.now()
        self.refresh_label.config(text=f"Last: {self.last_refresh.strftime('%H:%M:%S')}")

        # Clear and update table
        for item in self.tree.get_children():
            self.tree.delete(item)

        sorted_niches = sorted(results.items(), key=lambda x: x[1]["avg_score"], reverse=True)

        for i, (niche, data) in enumerate(sorted_niches, 1):
            score = data["avg_score"]
            views = data["total_views"]
            top_video = data["top_video"]

            if i <= 3:
                growth = "🔥 HOT"
                growth_color = self.current_theme["hot"]
            elif i <= 6:
                growth = "⬆️ RISING"
                growth_color = self.current_theme["rising"]
            else:
                growth = "📊 STABLE"
                growth_color = self.current_theme["stable"]

            video_id = top_video.get("id", "N/A")
            video_title = top_video['snippet']['title'][:35] + "..."

            self.tree.insert("", "end", values=(
                f"#{i}",
                niche.upper(),
                growth,
                f"{score:,.0f}",
                f"{views:,}",
                video_title,
                video_id if video_id != "N/A" else "N/A"
            ))

        # Update recommendation
        if sorted_niches:
            top_niche = sorted_niches[0]
            niche_name = top_niche[0].upper()
            top_video = top_niche[1]["top_video"]
            top_views = int(top_video["statistics"]["viewCount"])

            rec_text = (
                f"🎯 Best Niche: {niche_name}\n\n"
                f"Highest growth rate & velocity.\n"
                f"Perfect for AI content!\n\n"
                f"📈 Top: {top_video['snippet']['title'][:45]}...\n"
                f"👁️ Views: {top_views:,}"
            )
            self.rec_label.config(text=rec_text)

            # Update hashtags
            hashtags = top_niche[1].get("hashtags", [])
            tags_text = " ".join(hashtags[:20]) if hashtags else "No hashtags found"
            self.tags_text.config(state="normal")
            self.tags_text.delete("1.0", "end")
            self.tags_text.insert("1.0", tags_text)
            self.tags_text.config(state="disabled")

            # Update content ideas
            ideas = self.get_content_ideas(top_niche[0])
            self.ideas_text.config(state="normal")
            self.ideas_text.delete("1.0", "end")
            self.ideas_text.insert("1.0", "\n".join(ideas))
            self.ideas_text.config(state="disabled")

        # Update mini chart
        self.update_mini_chart()

    def update_mini_chart(self):
        """Update the mini chart"""
        if not MATPLOTLIB_AVAILABLE or not self.historical_data:
            return

        self.ax_mini.clear()

        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)

        trend_history = defaultdict(list)
        dates = sorted([d for d in self.historical_data.keys() if d >= seven_days_ago])

        for date in dates:
            for niche, data in self.historical_data[date].items():
                if "avg_score" in data:
                    trend_history[niche].append((date, data["avg_score"]))

        sorted_niches = sorted(
            trend_history.items(),
            key=lambda x: sum(v[1] for v in x[1]) / len(x[1]) if x[1] else 0,
            reverse=True
        )[:5]

        for i, (niche, data_points) in enumerate(sorted_niches):
            if data_points:
                dates_list = [dp[0] for dp in data_points]
                scores = [dp[1] for dp in data_points]
                color = CHART_COLORS[i % len(CHART_COLORS)]
                self.ax_mini.plot(dates_list, scores, marker='o', linewidth=2,
                                markersize=6, label=niche, color=color)

        self.ax_mini.set_xlabel('Date', color=self.theme["fg"], fontsize=9)
        self.ax_mini.set_ylabel('Score', color=self.theme["fg"], fontsize=9)
        self.ax_mini.set_title('7-Day Trend', color=self.theme["fg"], fontsize=11, fontweight='bold')
        self.ax_mini.legend(loc='best', fontsize=8)
        self.ax_mini.grid(True, alpha=0.3)

        # Apply theme colors
        self.fig_mini.patch.set_facecolor(self.current_theme["chart_bg"])
        self.ax_mini.set_facecolor(self.current_theme["chart_bg"])
        self.ax_mini.tick_params(colors=self.theme["fg"], labelsize=8)
        self.ax_mini.xaxis.label.set_color(self.theme["fg"])
        self.ax_mini.yaxis.label.set_color(self.theme["fg"])
        self.ax_mini.title.set_color(self.theme["fg"])
        for spine in self.ax_mini.spines.values():
            spine.set_color(self.theme["fg"])

        self.canvas_mini.draw()

    def get_content_ideas(self, niche):
        """Get content ideas for a niche"""
        ideas = {
            "Gaming": [
                "• No-commentary gameplay walkthroughs",
                "• Speedrun tutorials and guides",
                "• Epic moment compilations",
                "• Game tips and tricks videos"
            ],
            "Tech": [
                "• Software review screen recordings",
                "• Productivity tool tutorials",
                "• Tech news with AI voiceover",
                "• How-to guides with screen capture"
            ],
            "Finance": [
                "• Stock chart analysis with AI voice",
                "• Crypto news animations",
                "• Investment breakdowns",
                "• Market trends visualized"
            ],
            "AI Art": [
                "• AI art generation showcases",
                "• Tool comparisons and reviews",
                "• Tutorial series",
                "• Prompt engineering guides"
            ],
            "Educational": [
                "• Animated explainers",
                "• Fact compilations",
                "• History timelines",
                "• Science visualizations"
            ],
            "ASMR": [
                "• Sound design videos",
                "• Ambient soundscapes",
                "• Relaxing visuals",
                "• Sleep aid content"
            ],
            "Motivation": [
                "• AI-generated quote videos",
                "• Success story animations",
                "• Daily motivation clips",
                "• Mindset advice"
            ],
            "Compilations": [
                "• Best of series compilations",
                "• Funny moment edits",
                "• Trend compilation videos",
                "• Viral clip collections"
            ],
            "Music": [
                "• Lofi beats with visuals",
                "• Study music playlists",
                "• Ambient sound mixes",
                "• Genre compilations"
            ],
            "Animation": [
                "• Short animated stories",
                "• Motion graphics showcases",
                "• 3D animation tutorials",
                "• Visual effects demos"
            ]
        }
        return ideas.get(niche, ["• Create unique content in this niche"])

    def save_results(self, results):
        """Save results to JSON file in data folder"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"trend_analysis_{timestamp}.json"
        filepath = os.path.join(DATA_FOLDER, filename)

        save_data = {}
        for niche, data in results.items():
            save_data[niche] = {
                "avg_score": data["avg_score"],
                "total_views": data["total_views"],
                "video_count": data["video_count"],
                "top_video_title": data["top_video"]["snippet"]["title"],
                "top_video_views": int(data["top_video"]["statistics"]["viewCount"]),
                "hashtags": data.get("hashtags", [])
            }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(save_data, f, indent=2)

            # Add to historical data
            self.historical_data[datetime.now()] = save_data

            # Keep only last 30 days of data
            cutoff = datetime.now() - timedelta(days=30)
            self.historical_data = {k: v for k, v in self.historical_data.items() if k >= cutoff}

        except Exception as e:
            print(f"Error saving results: {e}")


def main():
    root = tk.Tk()
    app = YouTubeTrendSniper(root)
    root.mainloop()


if __name__ == "__main__":
    main()