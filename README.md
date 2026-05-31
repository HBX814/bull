# Bull-AI Research: Hybrid Equity Research Generator & MCP Server

Bull-AI Research is an advanced, automated, enterprise-grade equity research generation platform. By ingestion of corporate filings, earnings summaries, and CSV historical datasets, Bull-AI leverages structured LLM analysis through **Groq (Llama-3.3-70b-versatile)** to compile comprehensive, Geojit-style multi-page PDF retail research reports, complete with matplotlib-rendered financial charts.

The backend is built as a **hybrid FastAPI / Model Context Protocol (MCP) server**, letting you interact with it either via the rich React web frontend or directly as a tool inside any MCP-aware LLM client (such as Claude Desktop).

---

## 🏗️ Architecture & Stack

The codebase is split into two clean components:

### 1. Backend Server (`/backend`)
- **Web App**: Built with **FastAPI**, serving standard JSON REST endpoints for the frontend.
- **MCP Integration**: Fully integrates the official Anthropic **FastMCP** SDK.
  - **SSE Transport**: Mounted under `/mcp`, allowing web clients to call tools over HTTP.
  - **Stdio Transport**: Allows external LLM clients to run the backend as a tool-providing subprocess.
- **Database**: Powered by **MongoDB Atlas** (using the non-blocking asynchronous `motor` driver).
- **Text Processing**: Utilizes `pdfplumber` for structured PDF text extraction, along with `pandas` for handling CSV sheets.
- **Report Lab & Matplotlib**: Compiles extracted data into custom multi-page PDF templates containing matplotlib charts (Revenue, EBITDA, PAT, Segment performance).

### 2. Frontend Interface (`/frontend`)
- **Framework**: Modern **React** structured via **Craco** (Create React App Configuration Override).
- **Styling**: Sleek modern styling using **Tailwind CSS** and customized UI primitives.
- **Client routing**: Orchestrated using **Axios** with robust state hooks.

---

## 🛠️ Exposed MCP Tools

When connected as an MCP server, Bull-AI exposes the following high-level tools to your LLM agent:

| Tool Name | Parameters | Description |
| :--- | :--- | :--- |
| `mcp_health_check` | *None* | Verifies system health and Groq API configuration. |
| `mcp_generate_report` | `company_name` (str), `files` (array of filename/content dicts) | Generates a Geojit-style multi-page research PDF from text/CSV files, saves it, and logs metadata in MongoDB Atlas. |
| `mcp_list_reports` | `limit` (int, default=20) | Fetches a list of recently generated research reports from MongoDB Atlas. |
| `mcp_download_report` | `report_id` (str) | Retrieves the metadata and base64-encoded PDF bytes for a specific report. |

---

## 🚀 Getting Started

### Prerequisites
- **Node.js** (v18+ recommended)
- **Python** (v3.10+ recommended)
- **Groq API Key** (obtain from the [Groq Console](https://console.groq.com/))
- **MongoDB Atlas** Connection String

---

### 💻 1. Backend Setup & Run

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and configure your environment variables in `.env`:
   Create a `.env` file containing:
   ```env
   MONGO_URL=your_mongodb_atlas_url_here
   DB_NAME=bull_ai
   GROQ_API_KEY=your_groq_api_key_here
   GROQ_MODEL=llama-3.3-70b-versatile
   ```
3. Initialize the Python virtual environment and install packages:
   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # On Windows PowerShell
   pip install -r requirements.txt
   ```
4. **Run as REST API Server** (Frontend-compatible):
   ```bash
   .venv\Scripts\python server.py
   ```
   *The server starts listening on `http://localhost:8000`.*

5. **Run as Stdio MCP Subprocess**:
   ```bash
   .venv\Scripts\python server.py --mcp
   ```

---

### 🎨 2. Frontend Setup & Run

1. Navigate to the frontend directory:
   ```bash
   cd ../frontend
   ```
2. Set up your environment variables:
   Create a `.env` file containing:
   ```env
   REACT_APP_BACKEND_URL=http://localhost:8000
   ```
3. Install frontend dependencies:
   ```bash
   npm install --legacy-peer-deps
   npm install ajv --legacy-peer-deps
   ```
4. Start the development server:
   ```bash
   npm start
   ```
   *The web interface loads at `http://localhost:3000`.*

---

## 🤖 3. Connecting to Claude Desktop (MCP)

To let your desktop Claude app call Bull-AI tools to generate or inspect reports, edit your Claude Desktop configuration file:

- **Path**: `%APPDATA%\Claude\claude_desktop_config.json`

Add the following config under `mcpServers`:

```json
{
  "mcpServers": {
    "bull-ai-research": {
      "command": "c:/Users/harsh/OneDrive/Desktop/BullAI/backend/.venv/Scripts/python.exe",
      "args": [
        "c:/Users/harsh/OneDrive/Desktop/BullAI/backend/server.py",
        "--mcp"
      ],
      "env": {
        "MONGO_URL": "your_mongodb_atlas_url_here",
        "DB_NAME": "bull_ai",
        "GROQ_API_KEY": "your_groq_api_key_here",
        "GROQ_MODEL": "llama-3.3-70b-versatile"
      }
    }
  }
}
```

Restart Claude Desktop, and you will see the **hammer icon** 🛠️ enabling standard Bull-AI equity tools!
