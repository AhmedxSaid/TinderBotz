# Installation Guide

## Quick Installation

1. **Run the setup script:**
   ```bash
   cd bumble-bot
   python setup.py
   ```

2. **If setup fails, install manually:**
   ```bash
   cd bumble-bot
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Test the installation:**
   ```bash
   python test_opera_gx.py
   ```

## Manual Installation (Alternative)

If the automated setup doesn't work, follow these steps:

### 1. Create Virtual Environment
```bash
cd bumble-bot
python -m venv venv
venv\Scripts\activate  # Windows
# or source venv/bin/activate  # Linux/Mac
```

### 2. Install Dependencies
```bash
pip install selenium webdriver-manager opencv-python mediapipe numpy Pillow requests fake-useragent
```

### 3. Verify Installation
```bash
python -c "import selenium, cv2, mediapipe, numpy, PIL, requests; print('All imports successful')"
```

## Troubleshooting

### Permission Errors
If you get permission errors during installation:
```bash
pip install --user selenium webdriver-manager opencv-python mediapipe numpy Pillow requests fake-useragent
```

### Missing Dependencies
If specific packages fail to install:
- **OpenCV**: `pip install opencv-python`
- **MediaPipe**: `pip install mediapipe`
- **Selenium**: `pip install selenium`
- **Webdriver Manager**: `pip install webdriver-manager`

### Virtual Environment Issues
If virtual environment creation fails:
- Ensure Python is in your PATH
- Try: `python -m pip install --upgrade pip`
- Check Python version: `python --version` (must be 3.10+)

## Verification

After installation, verify everything works:
```bash
python test_opera_gx.py
```

Expected output should show:
- ✅ Opera GX found
- ✅ Dependencies installed
- ✅ Configuration valid
- ✅ All imports successful