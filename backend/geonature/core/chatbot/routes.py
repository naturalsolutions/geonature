"""Routes API pour le chatbot GeoNature."""

from __future__ import annotations

from typing import Optional
import logging

from flask import Blueprint, jsonify, request
from flask_login import login_required
from marshmallow import ValidationError

from .agent import run_assistant
from .schemas import ChatRequestSchema, ChatResponseSchema

chatbot_routes = Blueprint(
    "chatbot",
    __name__,
    url_prefix="/chatbot",
)

_request_schema = ChatRequestSchema()
_response_schema = ChatResponseSchema()
LOGGER = logging.getLogger(__name__)


def _extract_token(auth_header: Optional[str]) -> Optional[str]:
    if not auth_header:
        return None
    if auth_header.lower().startswith("bearer "):
        return auth_header.split(" ", 1)[1]
    return None


@chatbot_routes.route("/message", methods=["POST"])
@login_required
def post_message() -> tuple[dict, int]:
    """Génère une réponse à partir de l'historique fourni."""
    try:
        payload = _request_schema.load(request.get_json(force=True))
    except ValidationError as exc:
        return {"errors": exc.messages}, 400

    auth_header = request.headers.get("Authorization")
    user_token = _extract_token(auth_header)
    try:
        result = run_assistant(history=payload["messages"], user_token=user_token)
    except Exception as exc:  # pragma: no cover - dépend d'intégrations externes
        LOGGER.exception("Erreur inattendue lors du traitement du chatbot")
        details = str(exc).strip()
        message = (
            "Le service chatbot a rencontré une erreur interne. "
            "Consultez les logs serveur pour plus de détails."
        )
        response_payload = {"message": message}
        if details:
            response_payload["details"] = f"{type(exc).__name__}: {details}"
        return jsonify(response_payload), 500

    return jsonify(_response_schema.dump(result)), 200


@chatbot_routes.route("/message", methods=["OPTIONS"])
def options_message() -> tuple[str, int]:
    """Répond aux pré-vols CORS du frontend."""
    return "", 204
