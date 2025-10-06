"""Schémas Marshmallow pour l'API chatbot."""

from __future__ import annotations

from marshmallow import Schema, fields, validate


class ChatMessageSchema(Schema):
    role = fields.String(required=True, validate=validate.OneOf(["user", "assistant", "tool"]))
    content = fields.String(required=True)
    name = fields.String(required=False, allow_none=True)


class ChatRequestSchema(Schema):
    messages = fields.List(fields.Nested(ChatMessageSchema), required=True, validate=validate.Length(min=1))


class ToolCallSchema(Schema):
    name = fields.String(required=True)
    result = fields.Dict(required=False)
    error = fields.String(required=False)


class ChatResponseSchema(Schema):
    answer = fields.String(required=True)
    tool_calls = fields.List(fields.Nested(ToolCallSchema), required=True)
    error = fields.String(required=False)
