# Quick Start Script for Windows PowerShell
# Autonomous Ocean Forecasting Agent - AWS AI Agent Hackathon

Write-Host "🌊 Autonomous Ocean Forecasting Agent - Quick Start" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+ from python.org" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Choose your path:" -ForegroundColor Yellow
Write-Host "1. Quick Demo (No AWS - 5 minutes)" -ForegroundColor Cyan
Write-Host "2. Full AWS Deployment (30 minutes)" -ForegroundColor Cyan
Write-Host "3. Just install dependencies" -ForegroundColor Cyan
Write-Host ""

$choice = Read-Host "Enter choice (1, 2, or 3)"

if ($choice -eq "1") {
    Write-Host ""
    Write-Host "🚀 Setting up Quick Demo..." -ForegroundColor Green
    Write-Host ""
    
    # Create virtual environment
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    
    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
    
    # Install minimal dependencies for demo
    Write-Host "Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
    pip install streamlit --quiet
    
    Write-Host ""
    Write-Host "✅ Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Starting Streamlit demo..." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📝 Instructions:" -ForegroundColor Cyan
    Write-Host "1. Web interface will open in your browser" -ForegroundColor White
    Write-Host "2. Check the 'Demo Mode' checkbox" -ForegroundColor White
    Write-Host "3. Select 'Cape Town Harbor' location" -ForegroundColor White
    Write-Host "4. Click 'Analyze Ocean Conditions'" -ForegroundColor White
    Write-Host "5. Watch the AI agent in action!" -ForegroundColor White
    Write-Host ""
    Write-Host "Press Ctrl+C to stop the demo" -ForegroundColor Yellow
    Write-Host ""
    
    Start-Sleep -Seconds 3
    streamlit run app.py
}
elseif ($choice -eq "2") {
    Write-Host ""
    Write-Host "🏗️ Full AWS Deployment Path" -ForegroundColor Green
    Write-Host ""
    
    # Create virtual environment
    Write-Host "Step 1/6: Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    
    # Activate virtual environment
    Write-Host "Step 2/6: Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
    
    # Install all dependencies
    Write-Host "Step 3/6: Installing all dependencies..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    Write-Host ""
    Write-Host "Step 4/6: AWS Configuration Required" -ForegroundColor Yellow
    Write-Host "Run these commands:" -ForegroundColor Cyan
    Write-Host "  aws configure sso --profile ocean-agent" -ForegroundColor White
    Write-Host "  aws sts get-caller-identity --profile ocean-agent" -ForegroundColor White
    Write-Host ""
    
    $awsConfigured = Read-Host "Have you configured AWS? (y/n)"
    
    if ($awsConfigured -eq "y") {
        Write-Host ""
        Write-Host "Step 5/6: Deploy to AWS" -ForegroundColor Yellow
        Write-Host "Run deployment script:" -ForegroundColor Cyan
        Write-Host "  bash deploy.sh" -ForegroundColor White
        Write-Host ""
        Write-Host "OR follow manual steps in QUICKSTART.md" -ForegroundColor White
        Write-Host ""
        
        Write-Host "Step 6/6: Launch Web Interface" -ForegroundColor Yellow
        Write-Host "After AWS deployment, run:" -ForegroundColor Cyan
        Write-Host "  streamlit run app.py" -ForegroundColor White
        Write-Host ""
        
        Write-Host "✅ Ready for full deployment!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📚 See QUICKSTART.md for detailed instructions" -ForegroundColor Cyan
    } else {
        Write-Host ""
        Write-Host "⚠️ Please configure AWS first:" -ForegroundColor Yellow
        Write-Host "1. Install AWS CLI: https://aws.amazon.com/cli/" -ForegroundColor White
        Write-Host "2. Run: aws configure sso --profile ocean-agent" -ForegroundColor White
        Write-Host "3. Re-run this script" -ForegroundColor White
    }
}
elseif ($choice -eq "3") {
    Write-Host ""
    Write-Host "📦 Installing Dependencies Only" -ForegroundColor Green
    Write-Host ""
    
    # Create virtual environment
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    
    # Activate virtual environment
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\.venv\Scripts\Activate.ps1
    
    # Install all dependencies
    Write-Host "Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    pip install -r requirements.txt
    
    Write-Host ""
    Write-Host "✅ Dependencies installed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. For demo: streamlit run app.py" -ForegroundColor White
    Write-Host "2. For AWS deployment: See QUICKSTART.md" -ForegroundColor White
}
else {
    Write-Host "Invalid choice. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "🎉 Setup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "📖 Documentation:" -ForegroundColor Yellow
Write-Host "  • PROJECT_SUMMARY.md - Overview and next steps" -ForegroundColor White
Write-Host "  • QUICKSTART.md - Fast track deployment (30 min)" -ForegroundColor White
Write-Host "  • README.md - Complete documentation" -ForegroundColor White
Write-Host "  • VIDEO_SCRIPT.md - Demo video script" -ForegroundColor White
Write-Host "  • SUBMISSION_CHECKLIST.md - Devpost submission" -ForegroundColor White
Write-Host ""
Write-Host "🏆 AWS AI Agent Global Hackathon 2025" -ForegroundColor Cyan
Write-Host "Deadline: October 23, 2025 @ 1:00 AM GMT+1" -ForegroundColor Yellow
Write-Host ""
Write-Host "Good luck! 🚀🌊" -ForegroundColor Green
Write-Host ""
