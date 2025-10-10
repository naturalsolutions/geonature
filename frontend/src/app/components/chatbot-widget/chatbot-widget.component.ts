import { Component } from '@angular/core';
import { ChatbotService, ChatMessage } from '@geonature/services/chatbot.service';

interface DisplayMessage {
  role: 'user' | 'assistant' | 'tool';
  content: string;
  name?: string;
  downloadUrl?: string;
  filename?: string;
  meta?: Record<string, unknown>;
  contentType?: string;
}

@Component({
  selector: 'app-chatbot-widget',
  templateUrl: './chatbot-widget.component.html',
  styleUrls: ['./chatbot-widget.component.scss'],
})
export class ChatbotWidgetComponent {
  isOpen = false;
  isLoading = false;
  inputValue = '';
  lastError: string | null = null;
  messages: DisplayMessage[] = [
    {
      role: 'assistant',
      content: "Bonjour\u00a0! Je suis l'assistant GeoNature. Comment puis-je vous aider\u00a0?",
    },
  ];

  constructor(private chatbotService: ChatbotService) {}

  toggleWidget(): void {
    this.isOpen = !this.isOpen;
    if (this.isOpen) {
      this.lastError = null;
    }
  }

  closeWidget(): void {
    this.isOpen = false;
  }

  handleEnter(event: KeyboardEvent): void {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      this.sendMessage();
    }
  }

  sendMessage(): void {
    const content = this.inputValue.trim();
    if (!content || this.isLoading) {
      return;
    }
    this.messages.push({ role: 'user', content });
    this.inputValue = '';
    this.isLoading = true;
    this.lastError = null;

    const payload: ChatMessage[] = this.messages.map((msg) => ({
      role: msg.role,
      content: msg.content,
      name: msg.name,
    }));

    this.chatbotService.sendConversation(payload).subscribe({
      next: (response) => {
        response.tool_calls.forEach((toolCall) => {
          if (toolCall.result) {
            if (toolCall.name === 'generate_report' && toolCall.result.download_url) {
              const itemCount = toolCall.result.meta?.item_count;
              const limit = toolCall.result.meta?.limit;
              const format = toolCall.result.meta?.format;
              const parts: string[] = [];
              if (typeof format === 'string') {
                parts.push(format.toUpperCase());
              }
              if (typeof itemCount === 'number') {
                parts.push(`${itemCount} enregistrements`);
              }
              if (typeof limit === 'number') {
                parts.push(`limite ${limit}`);
              }
              const details = parts.length ? `(${parts.join(', ')})` : '';
              this.messages.push({
                role: 'tool',
                name: toolCall.name,
                content: `Rapport généré ${details}`.trim(),
                downloadUrl: toolCall.result.download_url,
                filename: toolCall.result.filename,
                contentType: toolCall.result.content_type,
                meta: toolCall.result.meta,
              });
            } else {
              this.messages.push({
                role: 'tool',
                name: toolCall.name,
                content: JSON.stringify(toolCall.result, null, 2),
              });
            }
          } else if (toolCall.error) {
            this.messages.push({
              role: 'tool',
              name: toolCall.name,
              content: `Erreur outil: ${toolCall.error}`,
            });
          }
        });
        this.messages.push({ role: 'assistant', content: response.answer });
        if (response.error) {
          this.lastError = response.error;
        }
      },
      error: (err) => {
        this.lastError = err?.error?.message || 'Le service chatbot est indisponible.';
        this.messages.push({
          role: 'assistant',
          content: "Je n'arrive pas à répondre pour le moment. Merci de réessayer plus tard.",
        });
      },
      complete: () => {
        this.isLoading = false;
      },
    });
  }
}
