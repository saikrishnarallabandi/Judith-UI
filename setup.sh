#!/bin/bash

# Custom LLM Chat Interface - Quick Start Script
echo "🚀 Custom LLM Chat Interface Setup"
echo "=================================="

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python is not installed. Please install Python first."
    exit 1
fi

# Check if pip is installed
if ! command -v pip &> /dev/null && ! command -v pip3 &> /dev/null; then
    echo "❌ pip is not installed. Please install pip first."
    exit 1
fi

echo "✅ Node.js and Python are installed"

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
npm install

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd backend

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit backend/.env and add your OpenAI API key"
fi

if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
else
    pip install -r requirements.txt
fi
cd ..

echo "✅ All dependencies installed successfully!"
echo ""
echo "🔑 IMPORTANT: Configure your OpenAI API key"
echo "   1. Edit backend/.env file"
echo "   2. Add: OPENAI_API_KEY=your_actual_api_key"
echo "   3. Get API key from: https://platform.openai.com/api-keys"
echo ""
echo "🌟 Quick Start Commands:"
echo "   npm start        - Run both frontend & backend"
echo "   npm run setup    - Re-install all dependencies"
echo ""
echo "🔗 URLs when running:"
echo "   Frontend: http://localhost:5174"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Ready to start! Run: npm start"
