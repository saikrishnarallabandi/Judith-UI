# ✨ Custom LLM Chat Interface

A professional AI chat interface with advanced memory system and data analysis capabilities. Features OpenAI GPT-4o-mini integration, semantic memory with FAISS, and comprehensive data analysis tools.

## ✨ Features

### 🤖 **AI Chat & Memory**
- **OpenAI GPT-4o-mini Integration** - Real AI responses with fallback mode
- **Semantic Memory System** - FAISS-based vector storage with sentence transformers
- **Context-Aware Responses** - AI remembers previous conversations and files
- **Memory Search** - Query past conversations and data analysis results

### � **Data Analysis & Visualization**
- **File Upload Support** - Excel (.xlsx), CSV, and JSON files
- **Interactive Charts** - Histograms, scatter plots, bar charts, line graphs, heatmaps
- **Data Querying** - Ask questions about your data in natural language
- **Chart Suggestions** - AI recommends best visualizations for your data
- **Plotly Integration** - Interactive, responsive charts in chat

### �💬 **Professional Chat Interface**
- **Modern UI** - Clean, professional design similar to ChatGPT
- **Conversation Management** - Create, switch, and delete conversations
- **Persistent History** - All conversations saved locally with memory integration
- **Responsive Design** - Works perfectly on desktop and mobile
- **Real-time Chat** - Streaming responses with token tracking

## 🚀 Quick Start

### Prerequisites
- Node.js (v16 or higher)
- Python (v3.8 or higher) 
- OpenAI API key (for GPT-4o-mini)
- CUDA-compatible GPU (optional, for faster memory system)

### Setup

1. **Get OpenAI API Key**
   - Visit [OpenAI API](https://platform.openai.com/api-keys)
   - Create a new API key
   - Copy the key for the next step

2. **Configure Environment**
   ```bash
   # Copy environment template
   cp backend/.env.example backend/.env
   
   # Edit the .env file and add your OpenAI API key
   # OPENAI_API_KEY=your_actual_api_key_here
   ```

3. **One-Command Setup & Start**
   ```bash
   # Install dependencies and start both frontend and backend
   npm start
   ```

## 🌐 Access URLs
- **Frontend**: http://localhost:5174
- **Backend API**: http://localhost:8000  
- **API Documentation**: http://localhost:8000/docs
- **Memory Stats**: http://localhost:8000/api/memory/stats

## 🧠 Memory System

The chat interface includes a sophisticated memory system:

- **Semantic Search**: Uses sentence-transformers (all-MiniLM-L6-v2) for embedding generation
- **FAISS Vector Database**: Efficient similarity search and retrieval
- **CUDA Support**: Automatically uses GPU acceleration when available
- **Persistent Storage**: Memories saved to disk and restored on restart
- **Context Integration**: Relevant memories automatically included in responses

### Memory Features
- Conversation history tracking
- File upload and analysis memory
- Chart creation and data analysis memory  
- Semantic search across all stored memories
- Memory statistics and recent activity tracking

## 📊 Data Analysis Capabilities

Upload files and interact with your data through natural language:

### Supported File Formats
- **Excel files** (.xlsx) - Handles complex spreadsheets with multiple sheets
- **CSV files** (.csv) - Standard comma-separated values
- **JSON files** (.json) - Structured data files

### Analysis Features
- **Data Summary**: Row/column counts, data types, missing values
- **Statistical Analysis**: Descriptive statistics, correlations
- **Data Querying**: Ask questions like "how many rows?" or "show unique values"
- **Smart Visualizations**: AI suggests best chart types for your data

### Available Chart Types
- **Histograms** - Distribution analysis
- **Scatter Plots** - Relationship exploration  
- **Bar Charts** - Category comparisons
- **Line Charts** - Trend analysis
- **Correlation Heatmaps** - Variable relationships
- **Box Plots** - Statistical summaries

## 🛠️ Tech Stack

### Frontend
- **React 18** + **TypeScript** - Modern component-based UI
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first styling
- **Radix UI** + **shadcn/ui** - Accessible component library
- **Plotly.js** - Interactive data visualizations

### Backend  
- **Python 3.8+** + **FastAPI** - High-performance API framework
- **OpenAI GPT-4o-mini** - Latest efficient GPT model
- **FAISS** - Facebook AI Similarity Search for vectors
- **sentence-transformers** - Semantic embedding generation
- **pandas** + **matplotlib** + **plotly** - Data analysis and visualization
- **uvicorn** - ASGI server for FastAPI

### Architecture
- **Modular Design**: Clean separation between core GPT client and memory/data features
- **gptclient.py**: Pure OpenAI API integration
- **llm_client.py**: Memory-enhanced orchestrator with data analysis
- **memory_system.py**: FAISS-based semantic memory management
- **data_tools.py**: File processing and visualization generation

## 📚 Development

### Available Scripts
- `npm start` - Install dependencies and run both frontend & backend
- `npm run dev:frontend` - Frontend development server only
- `npm run dev:backend` - Backend development server only  
- `npm run build` - Build frontend for production
- `npm run setup` - Install all dependencies

### Development Workflow
1. **Start Development**: `npm start` runs both services concurrently
2. **Frontend Only**: For UI development without backend changes
3. **Backend Only**: For API development and testing
4. **Memory Management**: Memory automatically saves every 10 conversations
5. **File Testing**: Upload sample CSV/Excel files to test data analysis

### API Endpoints

#### Core Chat
- `POST /api/chat` - Send message and get AI response
- `GET /api/health` - Server health check with memory stats

#### Memory System  
- `GET /api/memory/stats` - Memory statistics and breakdown
- `POST /api/memory/search` - Search stored memories
- `GET /api/memory/recent` - Recent conversations and analyses

#### Data Analysis
- `POST /api/upload` - Upload CSV/Excel/JSON files for analysis
- `GET /api/data/info` - Current data summary and statistics
- `POST /api/data/query` - Query data with natural language
- `POST /api/data/visualize` - Create charts and visualizations

### Memory System Testing

```bash
# Test memory search
curl -X POST "http://localhost:8000/api/memory/search" \
     -H "Content-Type: application/json" \
     -d '{"query": "data analysis", "k": 5}'

# Get memory statistics  
curl "http://localhost:8000/api/memory/stats"
```

### File Structure

```
├── src/                          # React frontend
│   ├── components/
│   │   ├── ChatInput.tsx         # Message input with file upload
│   │   ├── ChatMessages.tsx      # Message display with chart rendering
│   │   └── ChatSidebar.tsx       # Conversation management
│   └── lib/
│       └── llm-client.ts         # Frontend API client
├── backend/                      # Python backend
│   ├── main.py                   # FastAPI server with all endpoints
│   ├── gptclient.py              # Core OpenAI GPT-4o-mini client
│   ├── llm_client.py             # Memory-enhanced LLM orchestrator
│   ├── memory_system.py          # FAISS-based semantic memory
│   ├── data_tools.py             # File processing and visualization
│   └── memory_store/             # Persistent memory storage
└── package.json                  # Concurrent frontend/backend scripts
```

## 🎯 Usage Examples

### Basic Chat
1. Start the application with `npm start`
2. Navigate to http://localhost:5174
3. Ask any question - the AI will respond and remember the conversation

### Data Analysis Workflow
1. Click the file upload button in the chat input
2. Upload a CSV, Excel, or JSON file
3. Ask questions like:
   - "How many rows and columns are there?"
   - "Show me a histogram of the age column"
   - "What's the correlation between price and quantity?"
   - "Create a scatter plot of X vs Y"
   - "Suggest the best chart for this data"

### Memory Features
- Ask "What did we discuss before?" to see conversation history
- Say "Remember when we talked about..." to search memories
- Upload files and the AI will remember analysis results
- Memory persists between sessions and server restarts

## 🔧 Configuration

### Environment Variables (backend/.env)
```bash
# Required
OPENAI_API_KEY=your_openai_api_key_here

# Optional  
OPENAI_ORG_ID=your_organization_id
MAX_TOKENS=1000
TEMPERATURE=0.7
MEMORY_STORE_PATH=./memory_store
CUDA_VISIBLE_DEVICES=0  # For GPU acceleration
```

### Memory System Configuration
- **Vector Dimension**: 384 (all-MiniLM-L6-v2 embeddings)
- **Similarity Threshold**: 0.3 (adjustable in memory searches)
- **Auto-Save Frequency**: Every 10 conversations
- **Storage Format**: JSON with timestamp and metadata

For detailed technical documentation, see [README_COMPLETE.md](README_COMPLETE.md)

## 📄 License
MIT License - see LICENSE file for details.
