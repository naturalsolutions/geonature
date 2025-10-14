"""Orchestrateur simplifié pour le chatbot GeoNature."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from . import mcp_client
from .llm import llm_completion, LLMConfigurationError

LOGGER = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "Tu es l'assistant GeoNature. Réponds en français. "
    "Tu disposes des outils `fetch_synthese_for_web`, `fetch_info_geo`, `generate_report`, "
    "`list_geonature_docs` et `read_geonature_doc` pour récupérer ou exporter des données "
    "ou consulter la documentation GeoNature. Tu peux produire des rapports JSON ou PDF. "
    "Utilise un ton professionnel et cite les limites de connaissance si nécessaire."
)


FUNCTIONS = [
    {
        "name": "fetch_synthese_for_web",
        "description": "Récupère des observations via la route GeoNature /synthese/for_web.",
        "parameters": {
            "type": "object",
            "properties": {
                "filters": {
                    "type": "object",
                    "description": "Filtres JSON à transmettre à la route.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Nombre maximal de résultats.",
                },
                "output_format": {
                    "type": "string",
                    "enum": [
                        "ungrouped_geom",
                        "grouped_geom",
                        "grouped_geom_by_areas",
                    ],
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "fetch_info_geo",
        "description": "Retourne les intersections RefGeo et l'altitude min/max.",
        "parameters": {
            "type": "object",
            "properties": {
                "geometry": {
                    "type": "object",
                    "description": "Géométrie GeoJSON.",
                    "required": ["type"],
                },
                "area_type": {"type": "string"},
                "id_type": {"type": "integer"},
            },
            "required": ["geometry"],
            "additionalProperties": False,
        },
    },
    {
        "name": "generate_report",
        "description": (
            "Génère un rapport téléchargeable dans MinIO à partir des données synthèse et "
            "retourne les métadonnées nécessaires au téléchargement."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "filters": {
                    "type": "object",
                    "description": "Filtres JSON à transmettre à la route synthèse.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Nombre maximal de résultats à inclure dans le rapport.",
                },
                "report_type": {
                    "type": "string",
                    "description": "Étiquette humaine du rapport (ex: synthese_site).",
                },
                "format": {
                    "type": "string",
                    "enum": ["json", "pdf"],
                    "description": "Format de sortie souhaité (JSON par défaut, PDF disponible).",
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "list_geonature_docs",
        "description": "Liste les pages de la documentation GeoNature disponibles côté serveur MCP.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Terme de recherche facultatif pour filtrer les pages.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Nombre maximal de résultats (défaut 50).",
                },
            },
            "additionalProperties": False,
        },
    },
    {
        "name": "read_geonature_doc",
        "description": "Récupère le contenu d'une page de documentation GeoNature.",
        "parameters": {
            "type": "object",
            "properties": {
                "target": {
                    "type": "string",
                    "description": "URI de ressource ou chemin relatif retourné par list_geonature_docs.",
                },
                "as_text": {
                    "type": "boolean",
                    "description": "Retourner le contenu brut texte (défaut true).",
                },
            },
            "required": ["target"],
            "additionalProperties": False,
        },
    },
]


def _prepare_messages(history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
    ]
    for item in history:
        role = item.get("role")
        content = item.get("content")
        name = item.get("name")
        tool_call_id = item.get("tool_call_id")
        if role not in {"user", "assistant"}:
            LOGGER.warning("Role inconnu dans l'historique: %s", role)
            continue
        message: Dict[str, Any] = {"role": role, "content": content}
        messages.append(message)
    return messages


def _handle_tool_call(
    *,
    user_token: Optional[str],
    name: str,
    arguments: Dict[str, Any],
) -> Dict[str, Any]:
    LOGGER.info("Exécution outil %s", name)
    if name == "fetch_synthese_for_web":
        return mcp_client.call_synthese_for_web(user_token=user_token, **arguments)
    if name == "fetch_info_geo":
        return mcp_client.call_geo_info(user_token=user_token, **arguments)
    if name == "generate_report":
        return mcp_client.generate_report(user_token=user_token, **arguments)
    if name == "list_geonature_docs":
        return mcp_client.list_geonature_docs(**arguments)
    if name == "read_geonature_doc":
        return mcp_client.read_geonature_doc(**arguments)
    raise ValueError(f"Outil inconnu: {name}")


def run_assistant(
    *,
    history: List[Dict[str, Any]],
    user_token: Optional[str],
) -> Dict[str, Any]:
    """Boucle principale agent + outils."""

    messages = _prepare_messages(history)
    tool_events: List[Dict[str, Any]] = []

    try:
        response = llm_completion(messages, functions=FUNCTIONS)
    except LLMConfigurationError as exc:
        LOGGER.warning("LLM non disponible: %s", exc)
        return {
            "answer": (
                "Le service d'intelligence artificielle n'est pas configuré. "
                "Veuillez contacter un administrateur."
            ),
            "tool_calls": tool_events,
            "error": str(exc),
        }

    choices = response.get("choices", [])
    if not choices:
        return {
            "answer": "Je n'ai pas compris la demande.",
            "tool_calls": tool_events,
        }

    message = choices[0].get("message", {})
    finish_reason = choices[0].get("finish_reason")

    # Gestion des tool calls
    if finish_reason == "tool_calls" and message.get("tool_calls"):
        # On conserve le message assistant initial contenant la requête d'outils
        messages.append(message)
        for tool_call in message["tool_calls"]:
            function = tool_call.get("function", {})
            name = function.get("name")
            arguments_raw = function.get("arguments")
            tool_call_id = tool_call.get("id")
            try:
                arguments = json.loads(arguments_raw) if arguments_raw else {}
            except json.JSONDecodeError:
                LOGGER.error("Arguments outil invalides: %s", arguments_raw)
                continue
            try:
                tool_result = _handle_tool_call(
                    user_token=user_token,
                    name=name,
                    arguments=arguments,
                )
            except Exception as exc:  # pragma: no cover - dépend d'API externe
                LOGGER.exception("Erreur outil %s", name)
                tool_events.append(
                    {
                        "name": name,
                        "error": str(exc),
                    }
                )
                messages.append(
                    {
                        "role": "tool",
                        "name": name,
                        "tool_call_id": tool_call_id,
                        "content": json.dumps({"error": str(exc)}),
                    }
                )
            else:
                tool_events.append({"name": name, "result": tool_result})
                messages.append(
                    {
                        "role": "tool",
                        "name": name,
                        "tool_call_id": tool_call_id,
                        "content": json.dumps(tool_result),
                    }
                )
        try:
            followup = llm_completion(messages)
        except LLMConfigurationError as exc:
            LOGGER.warning("LLM indisponible après tool call: %s", exc)
            return {
                "answer": "Impossible de finaliser la réponse (LLM indisponible).",
                "tool_calls": tool_events,
                "error": str(exc),
            }
        follow_choice = followup.get("choices", [{}])[0]
        final_message = follow_choice.get("message", {})
        return {
            "answer": final_message.get("content", ""),
            "tool_calls": tool_events,
        }

    return {
        "answer": message.get("content", ""),
        "tool_calls": tool_events,
    }
