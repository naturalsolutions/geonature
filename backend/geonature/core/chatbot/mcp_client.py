"""Client interne pour les outils GeoNature exposés via MCP.

Ce module reprend la logique du serveur MCP dédié afin de pouvoir
orchestrer les appels depuis l'API GeoNature avec un jeton utilisateur
spécifique à chaque requête.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import requests
from flask import current_app, request


LOGGER = logging.getLogger(__name__)

_DEFAULT_TIMEOUT = 60.0


class MCPClientError(RuntimeError):
    """Erreur lors d'un appel vers une route GeoNature utilisée par le chatbot."""


def _get_timeout() -> float:
    raw = os.getenv("GEONATURE_MCP_TIMEOUT")
    if raw:
        try:
            return float(raw)
        except ValueError as exc:  # pragma: no cover
            raise ValueError("GEONATURE_MCP_TIMEOUT doit être numérique") from exc
    return _DEFAULT_TIMEOUT


def _build_base_url(prefix: str, fallback: Optional[str]) -> str:
    base_url = current_app.config.get(prefix)
    if not base_url:
        base_url = fallback
    if not base_url:
        # Fallback sur l'URL courante de la requête
        base_url = request.url_root.rstrip("/")
    return base_url.rstrip("/")


def _build_headers(user_token: Optional[str]) -> Dict[str, str]:
    headers = {"Accept": "application/json"}
    if user_token:
        headers["Authorization"] = f"Bearer {user_token}"
    return headers


def call_synthese_for_web(
    *,
    user_token: Optional[str],
    filters: Optional[Dict[str, Any]] = None,
    limit: Optional[int] = None,
    output_format: Optional[str] = None,
) -> Dict[str, Any]:
    """Appelle la route ``/synthese/for_web`` et renvoie le JSON résultat."""

    timeout = _get_timeout()
    fallback = None
    api_endpoint = current_app.config.get("API_ENDPOINT")
    if api_endpoint:
        fallback = api_endpoint.rstrip("/") + "/synthese"
    else:
        fallback = request.url_root.rstrip("/") + "/synthese"

    synthese_base = _build_base_url("CHATBOT_SYNTHESE_BASE_URL", fallback)
    url = f"{synthese_base}/for_web"
    params: Dict[str, Any] = {}
    if limit is not None:
        params["limit"] = limit
    if output_format:
        params["format"] = output_format

    LOGGER.debug(
        "Chatbot -> synthese/for_web request filters=%s limit=%s format=%s",
        bool(filters),
        limit,
        output_format,
    )

    try:
        response = requests.request(
            "POST" if filters else "GET",
            url,
            params=params or None,
            json=filters,
            headers=_build_headers(user_token),
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        LOGGER.error(
            "Erreur synthese/for_web %s -> %s : %s",
            url,
            exc.response.status_code if exc.response else "?",
            exc.response.text if exc.response else str(exc),
        )
        status = exc.response.status_code if exc.response else "?"
        raise MCPClientError(f"Erreur API synthese: {status}") from exc

    return response.json()


def call_geo_info(
    *,
    user_token: Optional[str],
    geometry: Dict[str, Any],
    area_type: Optional[str] = None,
    id_type: Optional[int] = None,
) -> Dict[str, Any]:
    """Appelle la route ``/geo/info`` et renvoie la réponse JSON."""

    timeout = _get_timeout()
    fallback = None
    api_endpoint = current_app.config.get("API_ENDPOINT")
    if api_endpoint:
        fallback = api_endpoint.rstrip("/") + "/geo"
    else:
        fallback = request.url_root.rstrip("/") + "/geo"

    geo_base = _build_base_url("CHATBOT_GEO_BASE_URL", fallback)
    url = f"{geo_base}/info"

    payload: Dict[str, Any] = {"geometry": geometry}
    if area_type:
        payload["area_type"] = area_type
    if id_type is not None:
        payload["id_type"] = id_type

    LOGGER.debug(
        "Chatbot -> geo/info payload keys=%s",
        list(payload.keys()),
    )

    try:
        response = requests.post(
            url,
            json=payload,
            headers=_build_headers(user_token),
            timeout=timeout,
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        LOGGER.error(
            "Erreur geo/info %s -> %s : %s",
            url,
            exc.response.status_code if exc.response else "?",
            exc.response.text if exc.response else str(exc),
        )
        status = exc.response.status_code if exc.response else "?"
        raise MCPClientError(f"Erreur API geo/info: {status}") from exc

    return response.json()
