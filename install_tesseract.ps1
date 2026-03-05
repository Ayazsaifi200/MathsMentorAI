# Tesseract OCR Installation Script for Windows
# Run this script in PowerShell as Administrator

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Tesseract OCR Installation Script" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "⚠️  Please run this script as Administrator" -ForegroundColor Yellow
    Write-Host "   Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Pause
    exit
}

Write-Host "Checking for existing Tesseract installation..." -ForegroundColor Yellow

# Check if Tesseract is already installed
try {
    $tesseractPath = (Get-Command tesseract -ErrorAction Stop).Source
    Write-Host "✅ Tesseract is already installed at: $tesseractPath" -ForegroundColor Green
    & tesseract --version
    Write-Host ""
    Write-Host "Installation complete! Please restart your Streamlit app." -ForegroundColor Green
    Pause
    exit
} catch {
    Write-Host "❌ Tesseract not found in PATH" -ForegroundColor Red
}

Write-Host ""
Write-Host "Installing Tesseract OCR using Scoop..." -ForegroundColor Yellow
Write-Host ""

# Check if Scoop is installed
try {
    $scoopVersion = scoop --version
    Write-Host "✅ Scoop is already installed (version $scoopVersion)" -ForegroundColor Green
} catch {
    Write-Host "📦 Installing Scoop package manager..." -ForegroundColor Yellow
    try {
        Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Invoke-RestMethod get.scoop.sh | Invoke-Expression
        Write-Host "✅ Scoop installed successfully" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to install Scoop: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Please install Tesseract manually:" -ForegroundColor Yellow
        Write-Host "1. Visit: https://github.com/UB-Mannheim/tesseract/releases" -ForegroundColor Cyan
        Write-Host "2. Download tesseract-ocr-w64-setup-*.exe" -ForegroundColor Cyan
        Write-Host "3. Run the installer and check 'Add to PATH'" -ForegroundColor Cyan
        Pause
        exit
    }
}

Write-Host ""
Write-Host "📥 Installing Tesseract OCR..." -ForegroundColor Yellow

try {
    scoop install tesseract
    Write-Host ""
    Write-Host "✅ Tesseract installed successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Verifying installation..." -ForegroundColor Yellow
    & tesseract --version
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Installation Complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Restart your Streamlit application" -ForegroundColor White
    Write-Host "2. Go to the 📷 Image tab" -ForegroundColor White
    Write-Host "3. The 'Extract Text from Image' button will now be active" -ForegroundColor White
    Write-Host ""
} catch {
    Write-Host "❌ Failed to install Tesseract: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install manually:" -ForegroundColor Yellow
    Write-Host "1. Visit: https://github.com/UB-Mannheim/tesseract/releases" -ForegroundColor Cyan
    Write-Host "2. Download tesseract-ocr-w64-setup-*.exe" -ForegroundColor Cyan
    Write-Host "3. Run the installer and check 'Add to PATH'" -ForegroundColor Cyan
}

Write-Host ""
Pause
