# Script to clean up ONNX Runtime libraries and reinstall GPU version cleanly
# สคริปต์ล้างค่าไลบรารี ONNX Runtime และติดตั้งเวอร์ชัน GPU ใหม่ให้สะอาด

Write-Host "Cleaning up ONNX Runtime libraries..." -ForegroundColor Yellow

# Get the project root directory
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $PSScriptRoot
Set-Location $ProjectRoot

# Activate virtual environment
$venv_activate = ".\.venv\Scripts\activate.ps1"
if (Test-Path $venv_activate) {
    . $venv_activate
} else {
    Write-Host "Virtual environment not found!" -ForegroundColor Red
    exit 1
}

# Uninstall all versions
Write-Host "Uninstalling existing packages..." -ForegroundColor Cyan
pip uninstall onnxruntime onnxruntime-gpu onnxruntime-directml -y

# Reinstall ONLY GPU version
Write-Host "Installing onnxruntime-gpu..." -ForegroundColor Green
pip install onnxruntime-gpu==1.23.2

# Check installation
Write-Host "Verifying installation..." -ForegroundColor Cyan
pip list | findstr onnxruntime

Write-Host "Done! Please verify that only 'onnxruntime-gpu' is listed above." -ForegroundColor Green
Write-Host "Then run your program again." -ForegroundColor Yellow
