"""
YouTube Trend Sniper - Find Faceless-Friendly Niches
Beautiful version with Rich library for colorful output
"""

import sys
import io
import json
from datetime import datetime, timedelta
from collections import defaultdict

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text
from rich.columns import Columns
from rich.layout import Layout
from rich.align import Align
from rich import box

# Initialize Rich console
console = Console()

# YouTube API Configuration
API_KEY = "AIzaSyBYJadz_1zfW5mU2ZbFPEEF5-hG9Lsf0P8"
BASE_URL = "https://www.googleapis.com/youtube/v3"

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


def get_trending_videos(region="US", max_results=50):
    """Fetch trending videos from YouTube API"""
    url = f"{BASE_URL}/videos"
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": region,
        "maxResults": max_results,
        "key": API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        console.print(f"[red]Error fetching trending videos: {e}[/red]")
        return []


def search_videos(query, max_results=20):
    """Search for videos in a specific niche"""
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
        response = requests.get(url, params=params)
        response.raise_for_status()
        video_ids = [item["id"]["videoId"] for item in response.json().get("items", [])]

        # Get detailed stats for videos
        stats = get_video_stats(video_ids)
        return stats
    except Exception as e:
        console.print(f"[red]Error searching videos: {e}[/red]")
        return []


def get_video_stats(video_ids):
    """Get statistics for specific videos"""
    url = f"{BASE_URL}/videos"
    params = {
        "part": "snippet,statistics",
        "id": ",".join(video_ids[:50]),  # Max 50 per request
        "key": API_KEY
    }

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json().get("items", [])
    except Exception as e:
        console.print(f"[red]Error getting video stats: {e}[/red]")
        return []


def calculate_video_score(video):
    """Calculate a score for a video based on views and recency"""
    views = int(video["statistics"].get("viewCount", 0))
    published_date = video["snippet"]["publishedAt"]

    # Calculate days since published
    pub_dt = datetime.fromisoformat(published_date.replace("Z", "+00:00"))
    days_ago = (datetime.now(pub_dt.tzinfo) - pub_dt).days

    # Score favors recent videos with high views
    if days_ago == 0:
        days_ago = 0.1  # Avoid division by zero

    return views / days_ago


def analyze_niches():
    """Analyze all niches and return top performers"""
    results = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console
    ) as progress:

        task = progress.add_task("[cyan]Analyzing YouTube trends...", total=len(FACELESS_NICHES))

        for niche, keywords in FACELESS_NICHES.items():
            progress.update(task, description=f"[cyan]Analyzing {niche}...")

            niche_videos = []
            for keyword in keywords[:3]:  # Check top 3 keywords per niche
                videos = search_videos(keyword, max_results=10)
                niche_videos.extend(videos)

            if niche_videos:
                # Calculate average score for this niche
                scores = [calculate_video_score(v) for v in niche_videos]
                avg_score = sum(scores) / len(scores)
                total_views = sum(int(v["statistics"].get("viewCount", 0)) for v in niche_videos)

                # Find top video in niche
                top_video = max(niche_videos, key=lambda v: int(v["statistics"].get("viewCount", 0)))

                results[niche] = {
                    "avg_score": avg_score,
                    "total_views": total_views,
                    "video_count": len(niche_videos),
                    "top_video": top_video
                }

            progress.advance(task)

    return results


def display_results(results):
    """Display analysis results in a beautiful format"""

    # Title Panel
    title = Text()
    title.append("🎯 ", style="bold red")
    title.append("YOUTUBE TREND SNIPER", style="bold white")
    title.append(" 🎯", style="bold red")

    console.print()
    console.print(Panel(title, border_style="bold blue", padding=(1, 2)))

    # Date panel
    date_text = f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    console.print(Panel(date_text, border_style="dim", padding=(0, 2)))

    console.print()

    # Sort by score
    sorted_niches = sorted(results.items(), key=lambda x: x[1]["avg_score"], reverse=True)

    # Create results table
    table = Table(title="📊 FACELESS NICHE ANALYSIS", show_header=True, header_style="bold magenta", box=box.ROUNDED)

    table.add_column("Rank", style="cyan", width=8)
    table.add_column("Niche", style="bold white", width=15)
    table.add_column("Growth", width=10)
    table.add_column("Trend Score", style="green", width=15)
    table.add_column("Total Views", style="yellow", width=18)
    table.add_column("Top Video", style="blue", width=40)

    for i, (niche, data) in enumerate(sorted_niches, 1):
        score = data["avg_score"]
        views = data["total_views"]
        count = data["video_count"]
        top_video = data["top_video"]

        # Growth indicator with colors
        if i <= 3:
            growth = "🔥 HOT"
            growth_style = "bold red"
        elif i <= 6:
            growth = "⬆️ RISING"
            growth_style = "bold yellow"
        else:
            growth = "📊 STABLE"
            growth_style = "green"

        # Format numbers
        score_text = f"{score:,.0f}"
        views_text = f"{views:,}"

        # Truncate title
        title_text = top_video['snippet']['title'][:38] + "..."

        table.add_row(
            f"#{i}",
            niche.upper(),
            Text(growth, style=growth_style),
            score_text,
            views_text,
            title_text
        )

    console.print(table)
    console.print()

    # Recommendation Panel
    if sorted_niches:
        top_niche = sorted_niches[0]
        niche_name = top_niche[0].upper()
        top_video = top_niche[1]["top_video"]
        top_views = int(top_video["statistics"]["viewCount"])

        rec_text = Text()
        rec_text.append("\n🎯 Best Faceless Niche Right Now: ", style="bold white")
        rec_text.append(f"{niche_name}", style="bold red")
        rec_text.append("\n\n", style="")
        rec_text.append("   This niche has the highest growth rate and view velocity.\n", style="dim")
        rec_text.append("   Perfect for AI-generated content with no face/voice needed.\n\n", style="dim")
        rec_text.append("   📈 Top Performing Video: ", style="yellow")
        rec_text.append(f"{top_video['snippet']['title'][:50]}...\n", style="white")
        rec_text.append(f"   👁️  Views: ", style="yellow")
        rec_text.append(f"{top_views:,}", style="bold green")

        console.print(Panel(rec_text, border_style="bold green", title="💡 RECOMMENDATION", padding=(1, 2)))

        # Content Ideas Panel
        console.print()
        content_text = generate_content_ideas_text(top_niche[0])
        console.print(Panel(content_text, border_style="bold cyan", title="📋 CONTENT IDEAS", padding=(1, 2)))

    # Footer
    footer = Text()
    footer.append("💾 Results saved! Run this script daily to track trends. ", style="dim")
    footer.append("🚀", style="red")

    console.print()
    console.print(Panel(footer, border_style="dim", padding=(0, 2)))
    console.print()


def generate_content_ideas_text(niche):
    """Generate content ideas for the top niche"""
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

    text = Text()
    for idea in ideas.get(niche, ["• Create unique content in this niche"]):
        text.append(idea + "\n", style="white")

    return text


def main():
    """Main application"""

    # Welcome screen
    welcome = Panel(
        Text("Finding the best faceless niches for you...", style="bold cyan"),
        title="🚀 YouTube Trend Sniper",
        border_style="bold cyan",
        padding=(1, 2)
    )
    console.print()
    console.print(welcome)

    # Analyze niches
    results = analyze_niches()

    # Display results
    if results:
        display_results(results)
    else:
        console.print("\n[red]❌ No results found. Check your API key and try again.[/red]\n")

    # Save results to file
    save_results(results)


def save_results(results):
    """Save results to JSON file for later reference"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"trend_analysis_{timestamp}.json"

    save_data = {}
    for niche, data in results.items():
        save_data[niche] = {
            "avg_score": data["avg_score"],
            "total_views": data["total_views"],
            "video_count": data["video_count"],
            "top_video_title": data["top_video"]["snippet"]["title"],
            "top_video_views": int(data["top_video"]["statistics"]["viewCount"])
        }

    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(save_data, f, indent=2)

        console.print(f"[green]💾 Results saved to: {filename}[/green]")
    except Exception as e:
        console.print(f"[red]⚠️ Could not save results: {e}[/red]")


if __name__ == "__main__":
    console.clear()
    main()