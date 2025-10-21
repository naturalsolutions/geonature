"""Orchestrateur simplifié pour le chatbot GeoNature."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from . import mcp_client
from .llm import llm_completion, LLMConfigurationError

LOGGER = logging.getLogger(__name__)

_JSON_DECODER = json.JSONDecoder()

SYSTEM_PROMPT = (
    "Tu es l'assistant GeoNature. Réponds en français.\n"
    "- Tu peux appeler les outils `fetch_synthese_for_web`, `fetch_info_geo`, `generate_report`, "
    "`list_geonature_docs`, `read_geonature_doc` pour récupérer/expliquer des données ou générer un rapport.\n"
    "- IMPORTANT : la réponse **affichée à l’utilisateur** doit être un texte naturel en français, jamais du JSON brut "
    "(sauf si l’utilisateur le demande explicitement).\n"
    "- Style : clair, concis, pro et chaleureux. Quand il y a des chiffres, reformule en phrase ou en tableau Markdown.\n"
    "- Structure par défaut :\n"
    "  1) TL;DR (1 phrase), 2) Détails (2–6 puces), 3) Prochaines étapes (facultatif).\n"
    "- Lorsque l’utilisateur veut un rapport PDF personnalisé, utilise le paramètre `layout` de l’outil `generate_report` pour décrire titres, sections, tableau, notes, etc., ou pose les questions nécessaires.\n"
    "- Si une valeur est incertaine, dis-le. Si des limites s’appliquent (périmètre d’accès, échantillon), indique-les."
)

COMPOSE_SYSTEM = (
    "Tu vas maintenant FORMULER la réponse utilisateur en français naturel, sans exposer de JSON brut.\n"
    "- Ne montre pas les objets/structures JSON ; utilise des phrases et, si utile, un petit tableau Markdown.\n"
    "- Style : clair, concis, pro et chaleureux.\n"
    "- Structure : TL;DR, puis puces de détails, puis prochaines étapes (si utile).\n"
    "- Si l’utilisateur a demandé un rapport JSON/PDF, confirme le lien ou l’état, mais ne colle pas le JSON."
)



def _extract_layout_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Tente d'extraire un objet JSON représentant un layout depuis un texte libre."""

    if not text:
        return None

    idx = 0
    length = len(text)
    while idx < length:
        char = text[idx]
        if char not in "{[":
            idx += 1
            continue
        try:
            obj, end = _JSON_DECODER.raw_decode(text, idx)
        except json.JSONDecodeError:
            idx += 1
            continue
        idx = end
        if isinstance(obj, dict):
            keys = set(obj.keys())
            if keys & {"header", "summary", "table", "notes", "footnote", "sections"}:
                return obj
    return None


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
                "layout": {
                    "type": "object",
                    "description": (
                        "Options de mise en page pour un rapport PDF (sections, tableau, notes, etc.)."
                    ),
                    "additionalProperties": True,
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
        layout_arg = arguments.get("layout")
        if layout_arg is not None and not isinstance(layout_arg, str):
            try:
                arguments["layout"] = json.dumps(layout_arg, ensure_ascii=False)
            except (TypeError, ValueError) as exc:
                LOGGER.warning("Layout non sérialisable ignoré: %s", exc)
                arguments.pop("layout", None)
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

    last_user_message = ""
    for item in reversed(history):
        if item.get("role") == "user":
            last_user_message = item.get("content", "")
            break

    messages = _prepare_messages(history)
    tool_events: List[Dict[str, Any]] = []

    try:
        response = llm_completion(messages, functions=FUNCTIONS, temperature=0.3)
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
                if name == "generate_report":
                    layout_arg = arguments.pop("layout", None)
                    layout_obj: Optional[Dict[str, Any]] = None
                    if isinstance(layout_arg, str):
                        try:
                            parsed_layout = json.loads(layout_arg)
                        except json.JSONDecodeError:
                            LOGGER.debug("Layout fourni non JSON: %s", layout_arg)
                        else:
                            if isinstance(parsed_layout, dict):
                                layout_obj = parsed_layout
                    elif isinstance(layout_arg, dict):
                        layout_obj = layout_arg

                    if layout_obj is None:
                        extracted_layout = _extract_layout_from_text(last_user_message)
                        if extracted_layout is not None:
                            layout_obj = extracted_layout
                            LOGGER.debug(
                                "Layout extrait automatiquement depuis la requête utilisateur (%s clés)",
                                len(extracted_layout),
                            )

                    layout_payload: Optional[str]
                    if layout_obj is None:
                        layout_payload = None
                    else:
                        try:
                            layout_payload = json.dumps(layout_obj, ensure_ascii=False)
                        except (TypeError, ValueError) as exc:
                            LOGGER.warning("Impossible de sérialiser le layout en JSON: %s", exc)
                            layout_payload = None

                    LOGGER.info(
                        "Layout préparé pour generate_report: %s",
                        "string" if layout_payload is not None else "none",
                    )

                    if layout_payload is not None:
                        arguments["layout"] = layout_payload

                    tool_result = _handle_tool_call(
                        user_token=user_token,
                        name=name,
                        arguments=arguments,
                    )
                else:
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
                # 2) Passe COMPOSE : forcer la rédaction texte
                messages.append({"role": "system", "content": COMPOSE_SYSTEM})
                followup = llm_completion(messages, temperature=0.7)
        except LLMConfigurationError as exc:
                LOGGER.warning("LLM indisponible après tool call: %s", exc)
                return {"answer": "Impossible de finaliser la réponse (LLM indisponible).", "tool_calls": tool_events, "error": str(exc)}
        follow_choice = followup.get("choices", [{}])[0]
        final_message = follow_choice.get("message", {})
        return {"answer": final_message.get("content", ""), "tool_calls": tool_events}

    # Pas de tool calls : si la réponse ressemble à du JSON, on compose en texte
    raw_answer = (message.get("content", "") or "").strip()
    if raw_answer.startswith("{") or raw_answer.startswith("["):
        messages.append({"role": "assistant", "content": raw_answer})
        messages.append({"role": "system", "content": COMPOSE_SYSTEM})
        try:
            composed = llm_completion(messages,temperature=0.7)
            composed_msg = composed.get("choices", [{}])[0].get("message", {})
            return {"answer": composed_msg.get("content", "") or raw_answer, "tool_calls": tool_events}
        except Exception:
            return {"answer": raw_answer, "tool_calls": tool_events}

    return {"answer": raw_answer, "tool_calls": tool_events}
