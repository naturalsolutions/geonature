"""Routes API pour le chatbot GeoNature."""

from __future__ import annotations

from typing import Optional

from flask import request
from flask_login import login_required
from flask_smorest import Blueprint as SmorestBlueprint

from .agent import run_assistant
from .schemas import ChatRequestSchema, ChatResponseSchema

chatbot_routes = SmorestBlueprint(
    "chatbot",
    __name__,
    url_prefix="/chatbot",
    description="Assistant conversationnel GeoNature",
)
chatbot_routes.DOC_TAGS = ["Assistant"]


def _extract_token(auth_header: Optional[str]) -> Optional[str]:
    if not auth_header:
        return None
    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1]
    return None


@chatbot_routes.route("/message", methods=["POST"])
@login_required
@chatbot_routes.arguments(ChatRequestSchema)
@chatbot_routes.response(200, ChatResponseSchema)
def post_message(payload):
    """Génère une réponse à partir de l'historique fourni."""

    auth_header = request.headers.get("Authorization")
    user_token = _extract_token(auth_header)
    result = run_assistant(history=payload["messages"], user_token=user_token)
    return result
