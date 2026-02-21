#!/bin/bash
# Quick Start Script for AI Data Dictionary Backend (Linux/Mac)

echo "🚀 AI Data Dictionary - Quick Start"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
    echo ""
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate
echo ""

# Check if requirements are installed
echo "📚 Checking dependencies..."
if ! pip list | grep -q "fastapi"; then
    echo "📥 Installing dependencies (this may take a few minutes)..."
    pip install -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found!"
    echo "📝 Creating .env from template..."
    cp .env.example .env
    
    echo ""
    echo "🔑 Generating secure keys..."
    python scripts/generate_keys.py
    echo ""
    
    echo "⚠️  IMPORTANT: Edit .env file and update:"
    echo "   - ENCRYPTION_KEY (copy from output above)"
    echo "   - JWT_SECRET_KEY (copy from output above)"
    echo "   - OPENAI_API_KEY (your OpenAI API key)"
    echo "   - DATABASE_URL (if different from default)"
    echo ""
    read -p "Press Enter after you've updated the .env file..."
fi

# Check if database is initialized
echo "🗄️  Checking database..."
read -p "Do you want to initialize the database? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📊 Initializing database..."
    python scripts/init_db.py
    echo ""
fi

# Start the application
echo ""
echo "🎉 Starting the application..."
echo ""
echo "📍 API will be available at:"
echo "   - Main API: http://localhost:8000"
echo "   - Interactive Docs: http://localhost:8000/docs"
echo "   - Alternative Docs: http://localhost:8000/redoc"
echo ""
echo "🔐 Default credentials:"
echo "   - Email: admin@example.com"
echo "   - Password: admin123"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

python src/main.py
