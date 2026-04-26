import anthropic
from fastapi import APIRouter, HTTPException

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent import run_agent_loop

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = await run_agent_loop(request.api_key, request.messages)
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=401, detail="Invalid API key.")
    except anthropic.RateLimitError:
        raise HTTPException(status_code=429, detail="Rate limited. Try again shortly.")
    except anthropic.APIError as e:
        raise HTTPException(status_code=502, detail=f"Anthropic API error: {e.message}")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return ChatResponse(response=response)
