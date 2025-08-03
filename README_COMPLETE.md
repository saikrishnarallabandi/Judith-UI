# Custom LLM Chat Interface

A professional AI chat interface with a Python backend and React frontend, inspired by LibreChat.

## Architecture

- **Frontend**: React + TypeScript + Vite + Tailwind CSS
- **Backend**: Python + FastAPI + Custom LLM Client
- **UI Components**: Radix UI + shadcn/ui

## Quick Start

### Option 1: Single Command (Recommended)

```bash
# Install all dependencies (frontend + backend)
npm run setup

# Run both frontend and backend together
npm start
```

### Option 2: Manual Setup

#### 1. Start the Python Backend

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Start the FastAPI server
python main.py
```

The backend will be available at `http://localhost:8000`
- API documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/health`

#### 2. Start the Frontend

```bash
# In the root directory, install Node dependencies
npm install

# Start the development server
npm run dev
```

The frontend will be available at `http://localhost:5174`

## Features

### Chat Interface
- Real-time conversation with AI using custom Python backend
- Clean, professional interface similar to ChatGPT/Claude
- Message streaming simulation with loading indicators
- OpenAI-compatible API format

### Conversation Management
- Create, switch between, and delete multiple chat conversations
- Persistent conversation history using localStorage
- Automatic conversation title generation
- Conversation timestamps and organization

### Custom LLM Integration
- Python-based LLM client (`InvokeGPT` class)
- FastAPI backend with CORS support
- Fallback responses when backend is unavailable
- Token usage tracking and estimation

### Responsive Design
- Mobile-friendly sidebar that slides over content
- Touch-friendly interface with proper tap targets
- Professional color scheme with blue-gray primary colors
- Clean typography using Inter font family

## Project Structure

```
├── src/                          # React frontend
│   ├── components/               # React components
│   │   ├── ui/                  # shadcn/ui components
│   │   ├── ChatSidebar.tsx      # Conversation sidebar
│   │   ├── ChatMessages.tsx     # Message display
│   │   └── ChatInput.tsx        # Message input
│   ├── lib/                     # Utilities
│   │   ├── llm-client.ts        # TypeScript LLM client
│   │   └── utils.ts             # Helper functions
│   └── App.tsx                  # Main application
├── backend/                     # Python backend
│   ├── llm_client.py           # InvokeGPT class
│   ├── main.py                 # FastAPI server
│   └── requirements.txt        # Python dependencies
└── package.json                # Node.js dependencies
```

## API Endpoints

### POST /api/chat
OpenAI-compatible chat completion endpoint
```json
{
  "messages": [
    {"role": "user", "content": "Hello!"}
  ],
  "model": "custom-gpt",
  "max_tokens": 1000,
  "temperature": 0.7
}
```

### GET /api/models
List available models

### GET /api/health
Health check endpoint

## Development

### Backend Development
The `InvokeGPT` class in `backend/llm_client.py` is designed to be easily extended:

```python
# Example: Add your own LLM integration
class InvokeGPT:
    async def _generate_response(self, user_message: str, context: List[OpenAIMessage]) -> str:
        # Replace this with your actual LLM API calls
        # Examples: OpenAI, Anthropic, local models, etc.
        pass
```

### Frontend Development
The TypeScript client automatically falls back to simulated responses if the Python backend is unavailable, making development flexible.

### Scripts

#### Development Scripts
- `npm start` or `npm run dev:full` - **Run both frontend and backend together** 🚀
- `npm run dev:frontend` - Start only the React frontend
- `npm run dev:backend` - Start only the Python backend
- `npm run setup` - Install all dependencies (frontend + backend)
- `npm run install:backend` - Install only Python backend dependencies

#### Build Scripts
- `npm run build` - Build frontend for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint on frontend code

#### Utility Scripts
- `npm run kill` - Kill processes on port 5000
- `npm run optimize` - Optimize Vite dependencies

## Customization

### Colors
The interface uses a professional blue-gray color scheme defined in the PRD. Colors can be customized in `tailwind.config.js`.

### LLM Backend
Replace the response generation in `backend/llm_client.py` with your preferred LLM provider:
- OpenAI GPT models
- Anthropic Claude
- Local models (Ollama, etc.)
- Custom fine-tuned models

### UI Components
Built with shadcn/ui components that can be easily customized or replaced.

## License

MIT License - see LICENSE file for details.
