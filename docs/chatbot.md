# Assistant conversationnel GeoNature

Ce module fournit un chatbot intégré à l'interface GeoNature. Il repose
sur deux éléments :

1. **Outils GeoNature** – Réutilise les routes `/synthese/for_web` et
   `/geo/info` via le client MCP interne (`geonature.core.chatbot.mcp_client`).
2. **Fournisseur LLM** – Un modèle conversationnel externe (OpenAI par
   défaut) utilisé pour orchestrer les échanges et décider quand appeler
   les outils.

## Configuration côté backend

| Variable | Description | Défaut |
| --- | --- | --- |
| `CHATBOT_LLM_PROVIDER` | Fournisseur LLM à utiliser (`openai`) | `openai` |
| `OPENAI_API_KEY` | Clé API OpenAI | _obligatoire_ |
| `OPENAI_MODEL` | Modèle OpenAI | `gpt-4o-mini` |
| `OPENAI_API_URL` | URL de l'API Chat Completions | `https://api.openai.com/v1/chat/completions` |
| `CHATBOT_SYNTHESE_BASE_URL` | Base URL alternative pour `/synthese` | auto-détectée |
| `CHATBOT_GEO_BASE_URL` | Base URL alternative pour `/geo` | auto-détectée |
| `GEONATURE_MCP_TIMEOUT` | Timeout des appels internes (s) | `60` |

Le jeton JWT de l'utilisateur connecté est automatiquement récupéré
dans l'en-tête `Authorization` et transmis pour chaque appel d'outil.

## Lancement du serveur MCP externe

Si vous utilisez le projet de démonstration `mcp-server-demo`, assurez-vous
de renseigner `GEONATURE_API_TOKEN` à partir du jeton utilisateur
courant (disponible en localStorage `gn_id_token`).

```bash
uv run --env-file .env server.py fastmcp stdio
```

## Frontend

Un widget flottant (icône bulle en bas à droite) est ajouté à
l'interface principale (`app-chatbot-widget`). Il s'appuie sur
`ChatbotService` (`/chatbot/message`) et affiche les résultats des
outils sous forme de blocs JSON.

## Dépendances

- Backend : requiert l'accès sortant vers le fournisseur LLM et les
  routes GeoNature standards.
- Frontend : aucune dépendance additionnelle (utilise `FormsModule`).

## Tests

- Vérifier qu'un utilisateur authentifié peut ouvrir la bulle, poser une
  question et recevoir une réponse.
- Déconnecter l'utilisateur : le point de terminaison `/chatbot/message`
  renvoie `401` (protégé par `login_required`).
