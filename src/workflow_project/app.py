import gradio as gr
import base64
import logging
import uuid
import asyncio
import tempfile
import os
from pathlib import Path

# There are tools set here dependent on environment variables
from workflow_project.graph import app as graph  # noqa
from workflow_project.graph import langfuse_handler
from workflow_project.utils import get_fixed_mermaid_data


logger = logging.getLogger(__name__)


async def chat_fn(as_is_solution: str, proposed_solution: str, progress=gr.Progress()):
    if not as_is_solution:
        raise gr.Error("As-Is solution cannot be blank")

    try:
        progress(0, desc="Initializing workflow generation...")
        
        async for msg in graph.astream(
            {"proposed_solution": proposed_solution, "as_is_solution": as_is_solution},
            config={
                "callbacks": [langfuse_handler],
                "configurable": {"thread_id": str(uuid.uuid4())},
            },
            stream_mode="updates",
        ):
            progress(0.5, desc="Processing with AI model...")
            print(f"The msg from LLM {msg}")
            content = msg.get("generate_graph", {}).get("messages", {}).content
            content, code = get_fixed_mermaid_data(content)
            print(f"Fixed content is {content}\n\n")
            if content:
                progress(1.0, desc="Diagram generation complete!")
                yield content, code

    except Exception:
        logger.exception("Exception occurred")
        user_error_message = (
            "There was an error processing your request. Please try again."
        )
        yield user_error_message, gr.skip(), False


def download_mermaid_code(mermaid_output):
    """Generate downloadable mermaid code file"""
    if not mermaid_output:
        return None
    
    # Extract just the mermaid code from the markdown format
    if "```mermaid" in mermaid_output:
        start = mermaid_output.find("```mermaid") + 10
        end = mermaid_output.find("```", start)
        mermaid_code = mermaid_output[start:end].strip()
    else:
        mermaid_code = mermaid_output
    
    # Create a temporary file
    import tempfile
    import os
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.mmd', delete=False) as f:
        f.write(mermaid_code)
        return f.name

async def convert_mermaid_to_png(mermaid_output):
    """Convert mermaid diagram to PNG using playwright"""
    if not mermaid_output:
        return None
    
    try:
        from playwright.async_api import async_playwright
        
        # Extract mermaid code
        if "```mermaid" in mermaid_output:
            start = mermaid_output.find("```mermaid") + 10
            end = mermaid_output.find("```", start)
            mermaid_code = mermaid_output[start:end].strip()
        else:
            mermaid_code = mermaid_output.strip()
        
        # Create HTML with mermaid diagram
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 40px;
                    background: white;
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }}
                .mermaid {{
                    background: white !important;
                    max-width: 100%;
                }}
            </style>
        </head>
        <body>
            <div class="mermaid">
                {mermaid_code}
            </div>
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'default',
                    background: '#ffffff',
                    flowchart: {{
                        useMaxWidth: true,
                        htmlLabels: true
                    }}
                }});
                
                // Ensure the diagram is fully rendered before screenshot
                setTimeout(() => {{
                    document.body.setAttribute('data-ready', 'true');
                }}, 2000);
            </script>
        </body>
        </html>
        """
        
        # Write HTML to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            html_path = f.name
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(viewport={'width': 1200, 'height': 800})
                
                # Load the HTML file
                await page.goto(f"file://{html_path}")
                
                # Wait for mermaid to render completely
                await page.wait_for_function("document.body.getAttribute('data-ready') === 'true'", timeout=15000)
                
                # Wait for the SVG to be present
                await page.wait_for_selector('.mermaid svg', timeout=10000)
                
                # Create output PNG file
                png_path = tempfile.mktemp(suffix='.png')
                
                # Take screenshot of the mermaid diagram only
                mermaid_element = page.locator('.mermaid')
                await mermaid_element.screenshot(path=png_path, omit_background=True)
                
                await browser.close()
                
                return png_path
        finally:
            # Clean up HTML file
            if os.path.exists(html_path):
                os.unlink(html_path)
                
    except ImportError:
        gr.Warning("Playwright is not installed. Please install it to use PNG export.")
        return None
    except Exception as e:
        print(f"PNG conversion error details: {e}")  # Debug info
        gr.Warning(f"Error converting to PNG: {str(e)}")
        return None


async def convert_mermaid_to_pdf(mermaid_output):
    """Convert mermaid diagram to PDF using playwright"""
    if not mermaid_output:
        return None
    
    try:
        from playwright.async_api import async_playwright
        
        # Extract mermaid code
        if "```mermaid" in mermaid_output:
            start = mermaid_output.find("```mermaid") + 10
            end = mermaid_output.find("```", start)
            mermaid_code = mermaid_output[start:end].strip()
        else:
            mermaid_code = mermaid_output.strip()
        
        # Create HTML with mermaid diagram
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.min.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 40px;
                    background: white;
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                }}
                .mermaid {{
                    background: white !important;
                    max-width: 100%;
                }}
                @media print {{
                    body {{
                        min-height: auto;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="mermaid">
                {mermaid_code}
            </div>
            <script>
                mermaid.initialize({{
                    startOnLoad: true,
                    theme: 'default',
                    background: '#ffffff',
                    flowchart: {{
                        useMaxWidth: true,
                        htmlLabels: true
                    }}
                }});
                
                // Ensure the diagram is fully rendered before PDF generation
                setTimeout(() => {{
                    document.body.setAttribute('data-ready', 'true');
                }}, 2000);
            </script>
        </body>
        </html>
        """
        
        # Write HTML to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            f.write(html_content)
            html_path = f.name
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                
                # Load the HTML file
                await page.goto(f"file://{html_path}")
                
                # Wait for mermaid to render completely
                await page.wait_for_function("document.body.getAttribute('data-ready') === 'true'", timeout=15000)
                
                # Wait for the SVG to be present
                await page.wait_for_selector('.mermaid svg', timeout=10000)
                
                # Create output PDF file
                pdf_path = tempfile.mktemp(suffix='.pdf')
                
                # Generate PDF
                await page.pdf(
                    path=pdf_path,
                    format='A4',
                    print_background=True,
                    margin={'top': '20px', 'right': '20px', 'bottom': '20px', 'left': '20px'}
                )
                
                await browser.close()
                
                return pdf_path
        finally:
            # Clean up HTML file
            if os.path.exists(html_path):
                os.unlink(html_path)
                
    except ImportError:
        gr.Warning("Playwright is not installed. Please install it to use PDF export.")
        return None
    except Exception as e:
        print(f"PDF conversion error details: {e}")  # Debug info
        gr.Warning(f"Error converting to PDF: {str(e)}")
        return None


def download_diagram_as_png(mermaid_output):
    """Wrapper function for gradio to download PNG"""
    if not mermaid_output:
        return None
    
    try:
        import asyncio
        # Run the async function
        png_path = asyncio.run(convert_mermaid_to_png(mermaid_output))
        return png_path
    except Exception as e:
        gr.Warning(f"Failed to convert diagram to PNG: {str(e)}")
        return None


def download_diagram_as_pdf(mermaid_output):
    """Wrapper function for gradio to download PDF"""
    if not mermaid_output:
        return None
    
    try:
        import asyncio
        # Run the async function
        pdf_path = asyncio.run(convert_mermaid_to_pdf(mermaid_output))
        return pdf_path
    except Exception as e:
        gr.Warning(f"Failed to convert diagram to PDF: {str(e)}")
        return None

def clear_inputs():
    return "", "", "", "", None


if __name__ == "__main__":
    logger.info("Starting the interface")
    
    # Custom CSS for professional styling with dynamic text color support
    custom_css = """
    .main-container {
        max-width: 1200px;
        margin: 0 auto;
        padding: 20px;
    }
    
    .header-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 15px;
        margin-bottom: 30px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .input-section {
        background: white;
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        margin-bottom: 20px;
    }
    
    .mermaid-container {
        background: white !important;
        padding: 20px;
        border-radius: 8px;
        border: 1px solid #e1e5e9;
        min-height: 400px;
        position: relative;
    }
    
    .mermaid-container .mermaid {
        background: white !important;
    }
    
    .mermaid-container svg {
        background: white !important;
    }
    
    /* Force mermaid text to be dark on white background */
    .mermaid-container .mermaid svg text {
        fill: #333333 !important;
        color: #333333 !important;
    }
    
    .mermaid-container .mermaid svg .node text {
        fill: #333333 !important;
        color: #333333 !important;
    }
    
    .mermaid-container .mermaid svg .edgeLabel text {
        fill: #333333 !important;
        color: #333333 !important;
    }
    
    .mermaid-container .mermaid svg .label text {
        fill: #333333 !important;
        color: #333333 !important;
    }
    
    /* Ensure node backgrounds are light for contrast */
    .mermaid-container .mermaid svg .node rect,
    .mermaid-container .mermaid svg .node circle,
    .mermaid-container .mermaid svg .node polygon {
        fill: #f9f9f9 !important;
        stroke: #333333 !important;
    }
    
    /* Style edge lines for better visibility */
    .mermaid-container .mermaid svg path.flowchart-link {
        stroke: #333333 !important;
    }
    
    .mermaid-container .mermaid svg .arrowheadPath {
        fill: #333333 !important;
        stroke: #333333 !important;
    }
    
    .download-section {
        background: #f8f9fa;
        padding: 20px;
        border-radius: 8px;
        margin-top: 20px;
        border-left: 4px solid #667eea;
    }
    
    .gradio-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .gradio-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Dark mode support - invert text color when in dark environment */
    @media (prefers-color-scheme: dark) {
        .mermaid-container {
            background: white !important;  /* Keep diagram background white regardless of system theme */
        }
        
        .mermaid-container .mermaid svg text {
            fill: #333333 !important;  /* Keep text dark on white background */
        }
    }
    """
    
    with gr.Blocks(
        title="ProHance Workflow", 
        theme=gr.themes.Soft(
            primary_hue="blue",
            secondary_hue="purple",
            neutral_hue="slate"
        ),
        css=custom_css
    ) as app:
        
        # Header Section
        gr.HTML("""
            <div class="header-section">
                <h1>ProHance Workflow Process Generator</h1>
            </div>
        """)
        
        with gr.Row():
            with gr.Column(scale=1):
                with gr.Group():
                    gr.Markdown("### 📝 **Input Solutions**")
                    
                    # Put the input fields side by side in columns
                    with gr.Row():
                        with gr.Column(scale=1):
                            as_is = gr.Textbox(
                                label="AS-IS SOLUTION",
                                placeholder="Describe your current business process or workflow...",
                                lines=6,
                                info="Detail your existing process flow, including steps, decision points, and stakeholders."
                            )
                        
                        with gr.Column(scale=1):
                            proposed_solution = gr.Textbox(
                                label="PROPOSED SOLUTION",
                                placeholder="Describe your proposed improvements or new process...",
                                lines=6,
                                info="Leave blank to analyze only the AS-IS solution, or describe your proposed changes."
                            )
                
                with gr.Row():
                    generate_wf = gr.Button(
                        "🚀 Generate Process Flow",
                        variant="primary",
                        size="lg"
                    )
                    custom_clear_btn = gr.Button(
                        "🗑️ Clear All",
                        variant="secondary"
                    )
        
        # Output Section
        gr.Markdown("### 📊 **Generated Workflow Diagram**")
        
        with gr.Row():
            llm_out = gr.Textbox(label="LLM OUTPUT", visible=False)
            
            with gr.Column():
                # Mermaid diagram with custom container to prevent dark mode
                mermaid_diag_out = gr.Markdown(
                    label="Process Flow Diagram",
                    elem_classes=["mermaid-container"]
                )
        
        # Download Section
        with gr.Group():
            gr.Markdown("### 💾 **Download Options**")
            gr.Markdown("*Download the diagram in your preferred format*")
            
            with gr.Row():
                '''
                download_code_btn = gr.Button(
                    "📄 Download Mermaid Code",
                    variant="secondary",
                    visible=False
                )
                '''
                download_png_btn = gr.Button(
                    "🖼️ Download as PNG", 
                    variant="secondary",
                    visible=False
                )
                download_pdf_btn = gr.Button(
                    "📋 Download as PDF",
                    variant="secondary", 
                    visible=False
                )
            
            download_file = gr.File(
                label="Download File",
                visible=False
            )

        # Event handlers
        generate_wf.click(
            fn=chat_fn,
            inputs=[as_is, proposed_solution],
            outputs=[llm_out, mermaid_diag_out],
            api_name="generate_mermaid",
            show_progress="full"
        ).then(
            # Show download buttons after diagram is generated
            lambda: [gr.update(visible=True), gr.update(visible=True), gr.update(visible=True)],
            outputs=[ download_png_btn, download_pdf_btn]
        )
        
        custom_clear_btn.click(
            fn=clear_inputs,
            outputs=[as_is, proposed_solution, llm_out, mermaid_diag_out, download_file]
        ).then(
            # Hide download buttons when clearing
            lambda: [gr.update(visible=False), gr.update(visible=False), gr.update(visible=False)],
            outputs=[download_png_btn, download_pdf_btn]
        )
        '''
        download_code_btn.click(
            fn=download_mermaid_code,
            inputs=[mermaid_diag_out],
            outputs=[download_file]
        ).then(
            lambda: gr.update(visible=True),
            outputs=[download_file]
        )'''
        
        download_png_btn.click(
            fn=download_diagram_as_png,
            inputs=[mermaid_diag_out],
            outputs=[download_file]
        ).then(
            lambda: gr.update(visible=True),
            outputs=[download_file]
        )
        
        download_pdf_btn.click(
            fn=download_diagram_as_pdf,
            inputs=[mermaid_diag_out],
            outputs=[download_file]
        ).then(
            lambda: gr.update(visible=True),
            outputs=[download_file]
        )
        


    # For Vercel deployment
    import os
    port = int(os.environ.get("PORT", 7870))
    
    if os.environ.get("VERCEL"):
        # Running on Vercel
        app.launch(
            server_name="0.0.0.0",
            server_port=port,
            share=False,
            show_error=True
        )
    else:
        # Running locally
        app.launch(
            server_name="0.0.0.0",
            server_port=7870,
            share=True
        )
