from typing import Optional
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field

from app.config import settings


class GuardrailDecision(BaseModel):
    is_shopping_related: bool = Field(
        description="True if query is related to shopping, purchasing, products, grocery, food, diets, prices, cart, or order receipts. False if off-topic.",
    )
    confidence: float = Field(
        default=1.0,
        description="Confidence score between 0.0 and 1.0 for this classification.",
    )
    reason: str = Field(
        default="",
        description="Brief justification for why this query is or is not shopping-related.",
    )


CLASSIFIER_PROMPT = """You are a shopping assistant input classifier.
Analyze the user's message and determine if it is relevant to an e-commerce grocery store.

Relevant topics include:
- Finding, buying, or inquiring about grocery items, snacks, drinks, pantry goods, ingredients
- Asking about prices, organic/non-organic, dietary restrictions, gluten-free, vegan items
- Asking about past orders, receipts, or reordering items
- Setting dietary preferences, budgets, or price limits
- General greetings and polite conversational pleasantries directed at shopping (e.g. "hi", "can you help me?")

Irrelevant topics include:
- World news, history, politics, travel advice
- Math proofs, writing essays, software programming
- General philosophy, fiction, jokes, or gaming

User query: "{query}"
"""


async def classify_input_intent(query: str) -> GuardrailDecision:
    """Tier 2 Classifier using Gemini with structured output.
    
    Only invoked if borderline or needed. Falls back gracefully if API key is not configured.
    """
    api_key = settings.active_gemini_api_key
    if not api_key or api_key == "your_gemini_api_key_here":
        # Free tier fallback: default to True if no API key is set yet
        return GuardrailDecision(
            is_shopping_related=True,
            confidence=1.0,
            reason="API key not configured; bypassed Tier 2 to local execution",
        )

    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",
            google_api_key=api_key,
            temperature=0.0,
        )
        structured_llm = llm.with_structured_output(GuardrailDecision)
        decision: GuardrailDecision = await structured_llm.ainvoke(
            CLASSIFIER_PROMPT.format(query=query)
        )
        return decision
    except Exception as e:
        # Rate limit or connection fallback: fail open so user is not blocked
        return GuardrailDecision(
            is_shopping_related=True,
            confidence=0.5,
            reason=f"Classification fallback due to: {str(e)}",
        )

