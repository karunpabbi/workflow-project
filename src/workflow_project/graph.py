from dotenv import load_dotenv

load_dotenv()
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import SystemMessage

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from workflow_project.prompts import prompt_comparison, prompt_as_is

DEFAULT_MODEL = "gpt-4o"
DEFAULT_PROVIDER = "openai"


from langfuse.langchain import CallbackHandler

# Initialize the Langfuse handler
langfuse_handler = CallbackHandler()


def load_chat_model(model: str, provider: str) -> BaseChatModel:
    return init_chat_model(model, model_provider=provider)


llm = load_chat_model(DEFAULT_MODEL, DEFAULT_PROVIDER)


class WorkflowState(MessagesState):
    proposed_solution: str
    as_is_solution: str


features = """ 
PROCESS DEFINTION:
    1. Process Modify/Add New: Create or modify an existing process.
    2. Process Details: Define process details like job number, supervisor, and formatting.
    3. Activity Details: Configure activities and sub-activities for the process.
    4. Custom Attribute Mapping: Create and map custom attribute groups, and define which attributes are visible during task creation.
    5. State Definition: Define state list (active/inactive), set state flow transitions, and manage state-level attribute visibility.
    6. Skill Group Mapping: Map skill groups to processes, set job targets (group/user), choose allocation algorithm & mode, and define transfer rules.
    7. Prioritization Rules: Configure prioritization rules based on custom/standard attribute weights.
    8. Allocation Rules: Define allocation rules using standard/custom attributes.
    9. Activity Mapping: Map productive activities for the process.
    10. Custom Task Form: Select standard attributes to be visible or hidden in the job form.
    11. Quality Checklist: Create a checklist of quality elements with severity and pass/fail criteria.
    12. SLA Conditions: Define SLA conditions using date attributes.
    13. Task Linking: Set rules to link tasks across same/different processes based on attributes.
    14. Notification: Configure notifications with conditions, frequency, channels, and recipients.
CUSTOM ATTRIBUTE:
    15. Field Configurations: Define field type (text, dropdown, checkbox, etc.), add options, set default values, specify value type/length, mark mandatory/optional, control editability, and activate/deactivate fields.
TEAM AND SKILL GROUPS
    16. Team & Skill Group Details: Define team name/description and add/remove users in skill groups.
SCHEDULER TEMPLATE
    17. Template Setup: Configure recurrence patterns, schedule times, and set active/inactive status.
USER ROLE
    18. Administrator Role: Manage users, menu permissions, action permissions, and display permissions.
    19. Supervisor Role: Manage users, menu permissions, action permissions, and display permissions.
    20. Associate Role: Manage menu permissions, action permissions, and display permissions.
"""


def generate_graph(state: WorkflowState):
    # - Output only the Mermaid.js code — no extra explanation or comments.
    prompt = prompt_comparison.format(
        as_is_solution=state["as_is_solution"],
        proposed_solution=state["proposed_solution"],
        features=features,
    )
    if not state["proposed_solution"].strip():
        print("AS IS PROCESS................")
        prompt = prompt_as_is.format(
            as_is_solution=state["as_is_solution"],
        )

    messages = [SystemMessage(content=prompt)] + state["messages"]
    response = llm.invoke(messages)
    return {"messages": response}


workflow = StateGraph(state_schema=WorkflowState)
workflow.add_node("generate_graph", generate_graph)

workflow.add_edge(START, "generate_graph")
workflow.add_edge("generate_graph", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
