# PythonAnywhere Deployment Guide

## Prerequisites
1. PythonAnywhere account (free or paid)
2. Your project files uploaded to PythonAnywhere

## Deployment Steps

### 1. Upload Files to PythonAnywhere
- Upload all project files to your PythonAnywhere account
- Recommended location: `/home/yourusername/workflow-project/`

### 2. Install Dependencies
Open a Bash console on PythonAnywhere and run:
```bash
cd ~/workflow-project
pip3.10 install --user -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in your project root with your API keys:
```bash
# Copy your .env file or create it manually
cp .env.example .env
# Edit the .env file with your actual API keys
nano .env
```

### 4. Configure Web App
1. Go to the "Web" tab in your PythonAnywhere dashboard
2. Click "Add a new web app"
3. Choose "Manual configuration"
4. Select Python 3.10
5. Configure the following settings:

#### Source code:
```
/home/yourusername/workflow-project/src
```

#### Working directory:
```
/home/yourusername/workflow-project
```

#### WSGI configuration file:
Edit `/var/www/yourusername_pythonanywhere_com_wsgi.py` and replace its content with:

```python
import sys
import os
from pathlib import Path

# Add your project directory to sys.path
project_root = Path('/home/yourusername/workflow-project')
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'src'))

# Set the working directory
os.chdir(str(project_root))

# Load environment variables
from dotenv import load_dotenv
load_dotenv(project_root / '.env')

# Import and create the application
from workflow_project.app import app

# For Gradio apps, we need to get the WSGI app
application = app.app
```

### 5. Static Files (Optional)
If you have static files, configure them in the "Static files" section:
- URL: `/static/`
- Directory: `/home/yourusername/workflow-project/static/`

### 6. Environment Variables in PythonAnywhere
Alternatively, you can set environment variables in the WSGI file directly:
```python
os.environ['OPENAI_API_KEY'] = 'your_openai_api_key_here'
os.environ['LANGFUSE_PUBLIC_KEY'] = 'your_langfuse_public_key_here'
os.environ['LANGFUSE_SECRET_KEY'] = 'your_langfuse_secret_key_here'
os.environ['LANGFUSE_HOST'] = 'https://us.cloud.langfuse.com'
```

### 7. Reload and Test
1. Click "Reload" button on the Web tab
2. Visit your domain: `https://yourusername.pythonanywhere.com`

## Troubleshooting

### Common Issues:
1. **Import errors**: Check sys.path configuration in WSGI file
2. **Environment variables not loaded**: Ensure .env file exists and is readable
3. **Gradio not starting**: Check that the WSGI application is correctly configured

### Logs:
Check error logs in:
- Error log: `/var/log/yourusername.pythonanywhere.com.error.log`
- Server log: `/var/log/yourusername.pythonanywhere.com.server.log`

### Testing locally:
You can test the WSGI configuration locally:
```bash
cd ~/workflow-project
python3.10 wsgi.py
```

## Notes
- PythonAnywhere free accounts have limited CPU seconds
- For production use, consider a paid account
- The application will be available at: `https://yourusername.pythonanywhere.com`