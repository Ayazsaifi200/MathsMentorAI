# Tesseract OCR Installation Guide

## Why Tesseract is Needed
Tesseract OCR is required to extract text from math problem images. Without it, the image input feature cannot function.

## Windows Installation (Recommended)

### Option 1: Direct Download
1. Download the installer from: https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe
2. Run the installer
3. **Important:** During installation, select "Add to PATH" option
4. Default installation path: `C:\Program Files\Tesseract-OCR`
5. Complete the installation

### Option 2: GitHub Release
1. Visit: https://github.com/UB-Mannheim/tesseract/wiki
2. Download the latest Windows installer (tesseract-ocr-w64-setup-*.exe)
3. Run and follow the installation wizard
4. Ensure "Add to PATH" is checked

## Verify Installation

After installation, open a new PowerShell window and run:
```powershell
tesseract --version
```

You should see output like:
```
tesseract 5.3.3
```

## Configure Python to Use Tesseract

If Tesseract is not in your PATH, you can manually configure it in `src/config.py`:

```python
# Add this line with your Tesseract installation path
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## Restart Application

After installing Tesseract:
1. Close any running Streamlit instances
2. Restart the MathMentor AI application
3. The image extraction feature should now work

## Test OCR Functionality

1. Go to the 📷 Image tab in the app
2. Upload a clear image of a math problem
3. Click "🔍 Extract Text from Image"
4. The extracted text should appear in the text area below

## Troubleshooting

### "Tesseract is not recognized"
- Restart your terminal/PowerShell
- Manually add Tesseract to PATH:
  - Open System Environment Variables
  - Edit PATH variable
  - Add: `C:\Program Files\Tesseract-OCR`
  - Restart PowerShell

### "No text detected"
- Ensure the image has clear, readable text
- Try a higher resolution image
- Ensure good contrast between text and background
- Rotate the image if text is sideways

### Still not working?
- Check `src/config.py` has correct `TESSERACT_PATH`
- Reinstall Tesseract with "Add to PATH" option checked
- Contact support with error logs
