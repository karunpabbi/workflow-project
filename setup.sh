#!/bin/bash
# Setup script for PythonAnywhere deployment

echo "🚀 Setting up ProHance Workflow Process Generator for PythonAnywhere..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the project root directory."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip3.10 install --user -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Please create one with your API keys:"
    echo "   - OPENAI_API_KEY"
    echo "   - LANGFUSE_PUBLIC_KEY"
    echo "   - LANGFUSE_SECRET_KEY"
    echo "   - LANGFUSE_HOST"
    echo "   - MERMAID_API_KEY"
else
    echo "✅ Found .env file"
fi

# Test import
echo "🧪 Testing imports..."
cd src
python3.10 -c "
try:
    from workflow_project.app import app
    print('✅ All imports successful!')
except ImportError as e:
    print(f'❌ Import error: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo "🎉 Setup complete! Your app is ready for PythonAnywhere deployment."
    echo ""
    echo "Next steps:"
    echo "1. Configure your WSGI file as described in DEPLOYMENT.md"
    echo "2. Set up your web app in PythonAnywhere dashboard"
    echo "3. Reload your web app"
else
    echo "❌ Setup failed. Please check the error messages above."
    exit 1
fi