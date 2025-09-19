# ProHance Workflow Process Generator

A web application that generates visual workflow process diagrams using AI, built with Gradio and LangChain.

## Features

- **AS-IS vs TO-BE Process Comparison**: Input current and proposed solutions
- **AI-Powered Analysis**: Uses GPT-4o to analyze workflow improvements
- **Mermaid Diagram Generation**: Creates visual flowcharts automatically
- **Real-time Monitoring**: Integrated with Langfuse for observability
- **Web Interface**: Clean, intuitive Gradio-based UI

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd workflow-project
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv workflow_env
   source workflow_env/bin/activate  # On Windows: workflow_env\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   LANGFUSE_PUBLIC_KEY=your_langfuse_public_key_here
   LANGFUSE_SECRET_KEY=your_langfuse_secret_key_here
   LANGFUSE_HOST=https://us.cloud.langfuse.com
   MERMAID_API_KEY=your_mermaid_api_key_here
   ```

5. **Run the application**
   ```bash
   PYTHONPATH=src python src/workflow_project/app.py
   ```

6. **Access the application**
   - Local: http://localhost:7860
   - Public: The app will provide a shareable link

## PythonAnywhere Deployment

For hosting on PythonAnywhere, see [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

### Quick Deployment Steps:

1. **Upload files to PythonAnywhere**
2. **Install dependencies**:
   ```bash
   pip3.10 install --user -r requirements.txt
   ```
3. **Configure WSGI** (see DEPLOYMENT.md)
4. **Set environment variables**
5. **Reload web app**

## Project Structure

```
workflow-project/
├── src/
│   └── workflow_project/
│       ├── __init__.py
│       ├── app.py          # Main Gradio application
│       ├── graph.py        # LangGraph workflow
│       ├── prompts.py      # AI prompts
│       └── utils.py        # Utility functions
├── tests/                  # Test files
├── .env                    # Environment variables (not in git)
├── requirements.txt        # Python dependencies
├── wsgi.py                # WSGI application for hosting
├── test_imports.py        # Import test script
├── setup.sh               # Setup script for PythonAnywhere
├── DEPLOYMENT.md          # Deployment guide
└── README.md              # This file
```

## Usage

1. **Enter AS-IS Solution**: Describe your current manual process
2. **Enter Proposed Solution** (optional): Describe the improved process
3. **Generate Process Flow**: Click the button to create a Mermaid diagram
4. **View Results**: See the generated workflow diagram

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o | Yes |
| `LANGFUSE_PUBLIC_KEY` | Langfuse public key for monitoring | Yes |
| `LANGFUSE_SECRET_KEY` | Langfuse secret key for monitoring | Yes |
| `LANGFUSE_HOST` | Langfuse host URL | Yes |
| `MERMAID_API_KEY` | Mermaid API key for diagrams | Optional |

## Development

### Running Tests
```bash
python test_imports.py
```

### Local Development Server
```bash
source workflow_env/bin/activate
PYTHONPATH=src python src/workflow_project/app.py
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and support, please check the deployment guide or create an issue in the repository.
