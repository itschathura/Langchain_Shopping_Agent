import base64
import json
from typing import Any, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from app.agent.graph import shopping_graph

router = APIRouter(prefix="/api/chat", tags=["Agent Chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., description="Customer message or grocery query")
    user_id: int = Field(default=1, description="Customer unique ID")
    image_base64: Optional[str] = Field(None, description="Optional base64-encoded image string")
    stream: bool = Field(default=False, description="Enable SSE streaming output")


class ChatResponse(BaseModel):
    response: str
    guardrail_status: dict[str, Any]
    user_id: int


@router.post("", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Execute LangGraph shopping agent with multimodal text and optional base64 image."""
    try:
        user_message = HumanMessage(content=request.message)

        # Execute compiled LangGraph workflow
        result = shopping_graph.invoke({
            "messages": [user_message],
            "user_id": request.user_id,
            "image_data": request.image_base64,
        })

        last_msg = result["messages"][-1]
        response_text = last_msg.content if isinstance(last_msg, AIMessage) else str(last_msg.content)

        return ChatResponse(
            response=response_text,
            guardrail_status=result.get("guardrail_status", {"passed": True}),
            user_id=request.user_id,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")


@router.post("/upload", response_model=ChatResponse)
async def chat_with_file_upload(
    message: str = Form(...),
    user_id: int = Form(1),
    file: Optional[UploadFile] = File(None),
):
    """Handle multipart chat requests with direct image file upload (PNG/JPEG)."""
    image_base64 = None
    if file:
        file_bytes = await file.read()
        image_base64 = base64.b64encode(file_bytes).decode("utf-8")

    return await chat_endpoint(
        ChatRequest(
            message=message,
            user_id=user_id,
            image_base64=image_base64,
            stream=False,
        )
    )


@router.post("/stream")
async def chat_stream_endpoint(request: ChatRequest):
    """Server-Sent Events (SSE) streaming endpoint for real-time chat UI responses."""
    async def event_generator():
        try:
            user_message = HumanMessage(content=request.message)
            result = shopping_graph.invoke({
                "messages": [user_message],
                "user_id": request.user_id,
                "image_data": request.image_base64,
            })

            last_msg = result["messages"][-1]
            response_text = last_msg.content if isinstance(last_msg, AIMessage) else str(last_msg.content)

            # Stream words/tokens to simulate live typing
            words = response_text.split(" ")
            for i, word in enumerate(words):
                token = word if i == len(words) - 1 else word + " "
                yield {
                    "event": "message",
                    "data": json.dumps({"token": token, "done": False}),
                }

            yield {
                "event": "done",
                "data": json.dumps({
                    "token": "",
                    "done": True,
                    "guardrail_status": result.get("guardrail_status", {}),
                }),
            }
        except Exception as e:
            yield {
                "event": "error",
                "data": json.dumps({"error": str(e)}),
            }

    return EventSourceResponse(event_generator())

