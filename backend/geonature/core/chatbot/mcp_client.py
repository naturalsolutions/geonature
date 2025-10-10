"""Client MCP pour le chatbot GeoNature.

Ce module encapsule les appels au serveur MCP externe (FastMCP) afin que
l'orchestrateur du chatbot puisse invoquer les outils exposés et lire les
ressources (documentation). Le serveur MCP doit être démarré séparément,
accessible via SSE (`fastmcp sse`) ou tout autre transport supporté.
"""

from __future__ import annotations

import json
import logging
import os
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import lru_cache
from typing import Any, AsyncIterator, Dict, List, Optional

import anyio
import mcp.types as mcp_types
from flask import current_app
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client


LOGGER = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 60.0
_DEFAULT_MCP_SSE_URL = "http://127.0.0.1:8765/sse"
_CLIENT_INFO = mcp_types.Implementation(
    name="GeoNatureChatbot",
    version=os.getenv("GEONATURE_VERSION", "dev"),
)


class MCPClientError(RuntimeError):
    """Erreur lors d'un échange avec le serveur MCP."""


def _get_timeout() -> float:
    raw = os.getenv("GEONATURE_MCP_TIMEOUT")
    if not raw:
        return _DEFAULT_TIMEOUT
    try:
        return float(raw)
    except ValueError as exc:  # pragma: no cover
        raise ValueError("GEONATURE_MCP_TIMEOUT doit être numérique") from exc


def _get_mcp_sse_url() -> str:
    url = current_app.config.get("CHATBOT_MCP_SSE_URL") or os.getenv("GEONATURE_MCP_SSE_URL")
    return url or _DEFAULT_MCP_SSE_URL


def _get_service_token() -> Optional[str]:
    return current_app.config.get("CHATBOT_MCP_AUTH_TOKEN") or os.getenv("GEONATURE_MCP_AUTH_TOKEN")


def _build_headers(user_token: Optional[str]) -> Dict[str, str]:
    """Construit les en-têtes transmis au serveur MCP."""
    headers: Dict[str, str] = {}
    service_token = _get_service_token()
    if service_token:
        headers["Authorization"] = f"Bearer {service_token}"
    if user_token:
        headers["X-GeoNature-User-Token"] = user_token
    return headers


@asynccontextmanager
async def _open_session(user_token: Optional[str]) -> AsyncIterator[ClientSession]:
    """Ouvre une session MCP via SSE et réalise l'initialisation."""
    headers = _build_headers(user_token)
    timeout = _get_timeout()
    sse_url = _get_mcp_sse_url()

    async with sse_client(
        sse_url,
        headers=headers or None,
        timeout=timeout,
        sse_read_timeout=timeout,
    ) as streams:
        async with ClientSession(*streams, client_info=_CLIENT_INFO) as session:
            await session.initialize()
            yield session


async def _call_tool_async(
    tool_name: str,
    arguments: Dict[str, Any],
    *,
    user_token: Optional[str],
) -> Any:
    async with _open_session(user_token) as session:
        try:
            result = await session.call_tool(tool_name, arguments or None, read_timeout_seconds=None)
        except Exception as exc:  # pragma: no cover - dépend de la stack MCP
            raise MCPClientError(f"Echec appel outil {tool_name}: {exc}") from exc

        if result.isError:
            text_blocks = [
                block.text
                for block in getattr(result, "content", [])
                if hasattr(block, "type") and block.type == "text"
            ]
            details = "; ".join(text_blocks) if text_blocks else "réponse serveur inconnue"
            raise MCPClientError(f"Outil {tool_name} a renvoyé une erreur: {details}")

        structured = result.structuredContent
        if structured is not None:
            if isinstance(structured, dict) and set(structured.keys()) == {"result"}:
                return structured["result"]
            return structured

        payload = []
        for block in getattr(result, "content", []):
            block_dict = block.model_dump(mode="json", by_alias=True) if hasattr(block, "model_dump") else block
            if isinstance(block_dict, dict) and block_dict.get("type") == "text":
                text = block_dict.get("text", "")
                try:
                    payload.append(json.loads(text))
                except json.JSONDecodeError:
                    payload.append(text)
            else:
                payload.append(block_dict)

        if not payload:
            return None
        if len(payload) == 1:
            return payload[0]
        return payload


def _call_tool(
    tool_name: str,
    arguments: Dict[str, Any],
    *,
    user_token: Optional[str],
) -> Any:
    return anyio.run(_call_tool_async, tool_name, arguments, user_token=user_token)


def call_synthese_for_web(
    *,
    user_token: Optional[str],
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    output_format: Optional[str] = None,
) -> Dict[str, Any]:
    args: Dict[str, Any] = {}
    if filters:
        args["filters"] = json.dumps(filters, ensure_ascii=False)
    if limit is not None:
        args["limit"] = limit
    if output_format:
        args["output_format"] = output_format
    if user_token:
        args["api_token"] = user_token

    result = _call_tool("fetch_synthese_for_web", args, user_token=user_token)
    if not isinstance(result, dict):
        raise MCPClientError("Réponse inattendue de fetch_synthese_for_web")
    return result


def call_geo_info(
    *,
    user_token: Optional[str],
    geometry: Dict[str, Any],
    area_type: Optional[str] = None,
    id_type: Optional[int] = None,
) -> Dict[str, Any]:
    args: Dict[str, Any] = {"geometry": json.dumps(geometry, ensure_ascii=False)}
    if area_type:
        args["area_type"] = area_type
    if id_type is not None:
        args["id_type"] = id_type
    if user_token:
        args["api_token"] = user_token

    result = _call_tool("fetch_info_geo", args, user_token=user_token)
    if not isinstance(result, dict):
        raise MCPClientError("Réponse inattendue de fetch_info_geo")
    return result


def generate_report(
    *,
    user_token: Optional[str],
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    report_type: Optional[str] = None,
    format: Optional[str] = None,
) -> Dict[str, Any]:
    args: Dict[str, Any] = {}
    if filters:
        args["filters"] = json.dumps(filters, ensure_ascii=False)
    if limit is not None:
        args["limit"] = limit
    if report_type:
        args["report_type"] = report_type
    if format:
        args["format"] = format
    if user_token:
        args["api_token"] = user_token

    result = _call_tool("generate_report", args, user_token=user_token)
    if not isinstance(result, dict):
        raise MCPClientError("Réponse inattendue de generate_report")
    return result


def list_geonature_docs(
    query: Optional[str] = None,
    limit: int = 50,
) -> List[Dict[str, str]]:
    args: Dict[str, Any] = {"limit": limit}
    if query:
        args["query"] = query

    result = _call_tool("list_geonature_docs", args, user_token=None)
    if not isinstance(result, list):
        raise MCPClientError("Réponse inattendue de list_geonature_docs")
    return result  # type: ignore[return-value]


def read_geonature_doc(target: str, as_text: bool = True) -> Dict[str, Any]:
    args: Dict[str, Any] = {"target": target, "as_text": as_text}

    result = _call_tool("read_geonature_doc", args, user_token=None)
    if not isinstance(result, dict):
        raise MCPClientError("Réponse inattendue de read_geonature_doc")
    return result


@lru_cache(maxsize=128)
def load_document_resource(uri: str) -> Optional[str]:
    """Lecture directe d'une ressource MCP (doc) retournée sous forme de texte."""

    async def _read_async() -> Optional[str]:
        async with _open_session(user_token=None) as session:
            read = await session.read_resource(uri)
            for item in read.contents:
                if hasattr(item, "text"):
                    return item.text  # type: ignore[attr-defined]
            return None

    return anyio.run(_read_async)
