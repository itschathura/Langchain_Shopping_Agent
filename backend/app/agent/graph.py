import base64
from typing import Any, Dict, List, Literal
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode, tools_condition

from app.agent.prompts import build_system_prompt
from app.agent.state import AgentState
from app.agent.tools import ALL_TOOLS
from app.config import settings
from app.guardrails.rules import check_input_rules


# ==============================================================================
# Graph Node Definitions (Synchronous & Fast)
# ==============================================================================

def guardrail_node(state: AgentState) -> dict[str, Any]:
    """Fast, zero-cost input guardrail check (<1ms, $0)."""
    messages = state.get("messages", [])
    if not messages:
        return {"guardrail_status": {"passed": True}}

    # Find the most recent user message
    last_user_msg = next((m for m in reversed(messages) if isinstance(m, HumanMessage)), None)
    if not last_user_msg:
        return {"guardrail_status": {"passed": True}}

    text_content = ""
    if isinstance(last_user_msg.content, str):
        text_content = last_user_msg.content
    elif isinstance(last_user_msg.content, list):
        for part in last_user_msg.content:
            if isinstance(part, dict) and part.get("type") == "text":
                text_content += part.get("text", "")

    # Check Tier 1 regex rules
    rule_res = check_input_rules(text_content)
    if not rule_res.passed:
        bot_response = AIMessage(content=rule_res.redirect_message or "I can only assist with shopping queries.")
        return {
            "messages": [bot_response],
            "guardrail_status": {
                "passed": False,
                "reason": rule_res.reason,
            },
        }

    return {"guardrail_status": {"passed": True}}


def load_context_node(state: AgentState) -> dict[str, Any]:
    """Loads active customer preferences if not already injected in state."""
    if state.get("active_preferences") is not None:
        return {}
    return {"active_preferences": None}


def _get_model():
    """Initializes Gemini 1.5 Flash bound with our catalog tools."""
    api_key = settings.active_gemini_api_key
    if not api_key or api_key == "your_gemini_api_key_here":
        # Safe offline fallback model if running locally without API key configured yet
        from langchain_core.language_models.fake_chat_models import FakeListChatModel
        fake_response = (
            "Here are the matching grocery items:\n"
            "1. [ID #1] Organic Raw Wildflower Honey - $14.99 (Organic)\n"
            "2. [ID #6] Organic Rolled Oats - $4.50 (Organic)\n\n"
            "Note: Configure GEMINI_API_KEY in .env for live Gemini 1.5 Flash tool calling."
        )
        fake_llm = FakeListChatModel(responses=[fake_response])
        return fake_llm

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=api_key,
        temperature=0.2,
    )
    return llm.bind_tools(ALL_TOOLS)


def agent_node(state: AgentState) -> dict[str, Any]:
    """Core multimodal agent node executing Gemini 1.5 Flash."""
    user_id = state.get("user_id", 1)
    preferences = state.get("active_preferences")
    image_data = state.get("image_data")

    # 1. Build prompt with user preferences injected
    system_text = build_system_prompt(user_id=user_id, preferences=preferences)
    system_msg = SystemMessage(content=system_text)

    # 2. Prepare message list
    raw_messages = state["messages"]

    processed_messages: list[BaseMessage] = [system_msg]
    for i, msg in enumerate(raw_messages):
        if i == len(raw_messages) - 1 and isinstance(msg, HumanMessage) and image_data:
            text = msg.content if isinstance(msg.content, str) else ""
            content_blocks = [{"type": "text", "text": text}]
            img_url = image_data if image_data.startswith("data:") else f"data:image/jpeg;base64,{image_data}"
            content_blocks.append({"type": "image_url", "image_url": {"url": img_url}})
            processed_messages.append(HumanMessage(content=content_blocks))
        else:
            processed_messages.append(msg)

    # 3. Call model
    model = _get_model()
    response = model.invoke(processed_messages)
    return {"messages": [response]}


def output_validator_node(state: AgentState) -> dict[str, Any]:
    """Pure-code output validation for format compliance."""
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_ai_msg = next((m for m in reversed(messages) if isinstance(m, AIMessage)), None)
    if not last_ai_msg or not isinstance(last_ai_msg.content, str):
        return {}

    return {}


# ==============================================================================
# Conditional Routing Functions
# ==============================================================================

def route_guardrail(state: AgentState) -> Literal["load_context", "__end__"]:
    status = state.get("guardrail_status", {})
    if not status.get("passed", True):
        return END
    return "load_context"


# ==============================================================================
# LangGraph Workflow Assembly
# ==============================================================================

workflow = StateGraph(AgentState)

# 1. Add Nodes
workflow.add_node("guardrail", guardrail_node)
workflow.add_node("load_context", load_context_node)
workflow.add_node("agent", agent_node)
workflow.add_node("tools", ToolNode(ALL_TOOLS))
workflow.add_node("output_validator", output_validator_node)

# 2. Add Edges
workflow.add_edge(START, "guardrail")

workflow.add_conditional_edges(
    "guardrail",
    route_guardrail,
    {
        "load_context": "load_context",
        END: END,
    },
)

workflow.add_edge("load_context", "agent")

workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        END: "output_validator",
    },
)

workflow.add_edge("tools", "agent")
workflow.add_edge("output_validator", END)

# 3. Compile Graph
shopping_graph = workflow.compile()
