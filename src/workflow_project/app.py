import gradio as gr

import logging
import uuid


# There are tools set here dependent on environment variables
from workflow_project.graph import app as graph  # noqa
from workflow_project.graph import langfuse_handler
from workflow_project.utils import get_fixed_mermaid_data


logger = logging.getLogger(__name__)


async def chat_fn(as_is_solution: str, proposed_solution: str):
    if not as_is_solution:
        raise gr.Error("As-Is solution cannot be blank")

    try:
        async for msg in graph.astream(
            {"proposed_solution": proposed_solution, "as_is_solution": as_is_solution},
            config={
                "callbacks": [langfuse_handler],
                "configurable": {"thread_id": str(uuid.uuid4())},
            },
            stream_mode="updates",
        ):
            print(f"The msg from LLM {msg}")
            content = msg.get("generate_graph", {}).get("messages", {}).content
            content, code = get_fixed_mermaid_data(content)
            print(f"Fixed content is {content}\n\n")
            if content:
                yield content, code

    except Exception:
        logger.exception("Exception occurred")
        user_error_message = (
            "There was an error processing your request. Please try again."
        )
        yield user_error_message, gr.skip(), False


def clear_inputs():
    return "", "", "", ""


def create_app():
    """Create and return the Gradio application"""
    logger.info("Creating the interface")
    app = gr.Blocks(title="ProHance Workflow", theme="gstaff/xkcd")
    
    with app:
        with gr.Column(scale=10):
            gr.Markdown(
                """
                    <h1 align="center">ProHance Workflow Process Generator</h1>
                    """
            )
        as_is = gr.Textbox(label="AS-IS SOLUTION")
        proposed_solution = gr.Textbox(label="PROPOSED SOLUTION")

        with gr.Row():
            llm_out = gr.Textbox(label="LLM OUTPUT", visible=False)
            mermaid_diag_out = gr.Markdown(label="MERMAID DIAGRAM")

        generate_wf = gr.Button("Generate Process Flow")
        custom_clear_btn = gr.Button("Clear")

        generate_wf.click(
            fn=chat_fn,
            inputs=[as_is, proposed_solution],
            outputs=[llm_out, mermaid_diag_out],
            api_name="generate_mermaid",
        )
        custom_clear_btn.click(
            fn=clear_inputs,
            outputs=[as_is, proposed_solution, llm_out, mermaid_diag_out],
        )
    
    return app


# Create the app instance for WSGI hosting
app = create_app()


if __name__ == "__main__":
    logger.info("Starting the interface")
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=True
    )
