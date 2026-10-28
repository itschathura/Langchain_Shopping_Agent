from typing import Annotated, Any, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """The complete state managed by our LangGraph shopping workflow."""

    # Chat history with LangGraph message accumulator
    messages: Annotated[list[BaseMessage], add_messages]

    # Current user context
    user_id: int

    # Dynamically injected preferences from PostgreSQL
    active_preferences: Optional[dict[str, Any]]

    # Optional multimodal image (base64 or URL)
    image_data: Optional[str]

    # Guardrail tracking metadata
    guardrail_status: Optional[dict[str, Any]]

