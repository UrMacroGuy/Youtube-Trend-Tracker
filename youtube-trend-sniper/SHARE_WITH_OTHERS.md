# YouTube Trend Sniper - Share Instructions

## 📦 How to Share This App

### Quick Share (Zip File)
1. The zip file `YouTube_Trend_Sniper.zip` is ready to share
2. Send it via any method: email, Discord, Google Drive, etc.
3. Recipient extracts and runs `run_gui.bat`

### What's Included
- ✅ gui_app.py - Main application
- ✅ run_gui.bat - Launcher for Windows
- ✅ app.py - Terminal version (backup)
- ✅ run.bat - Terminal launcher
- ✅ data/ folder - Stores analytics (empty initially)
- ✅ notes.md - Project notes
- ✅ README.md - Instructions

## 🚀 For Recipient - How to Use

### Step 1: Extract
1. Extract the zip file to any folder
2. Double-click `run_gui.bat`

### Step 2: First Run Requirements
The app needs Python installed. If they don't have it:
1. Go to python.org/downloads
2. Download Python 3.12 or newer
3. Run installer - CHECK "Add to PATH"
4. Restart and run `run_gui.bat` again

### Step 3: Optional Dependencies
For full chart features:
```
pip install matplotlib requests
```

## 🔑 Important Notes

### API Key
The app includes a YouTube API key. If sharing publicly:
- The recipient should get their own key at console.cloud.google.com
- Replace the key in gui_app.py line ~35

### Data Folder
- All analytics are saved in `data/` folder
- Files named: `trend_analysis_YYYYMMDD_HHMMSS.json`
- Can be shared for historical analysis

## 📧 Email Template for Sharing

```
Hey!

I found this awesome YouTube trend analyzer that finds the best
faceless niches to grow channels. It's super useful for AI content!

Features:
- 🔍 Analyzes 10+ faceless-friendly niches
- 📊 Tracks growth rates and view velocity
- 🎯 Finds trending hashtags
- 📈 Shows 7-day trend history
- 🌙 Beautiful dark/light mode UI

How to use:
1. Extract the zip file
2. Double-click run_gui.bat
3. Wait 30 seconds for analysis
4. See which niches are hot!

It's perfect for finding opportunities in animation, gaming,
educational content, and more.

Let me know if you have questions!

[Your name]
```

## 🌐 Other Sharing Methods

### Create Executable (.exe)
To make it run without Python:
```
pip install pyinstaller
pyinstaller --onefile --windowed gui_app.py
```

### GitHub Repository
1. Create repo at github.com
2. Upload all files
3. Share the repo link

### Direct File Sharing
- Google Drive: Upload and share link
- Discord: Drag and drop the zip file
- Email: Attach the zip file
- WeTransfer: For larger files

---
Made with ❤️ for faceless YouTube success!