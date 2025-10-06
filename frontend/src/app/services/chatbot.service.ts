import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import { ConfigService } from './config.service';

export interface ChatMessage {
  role: 'user' | 'assistant' | 'tool';
  content: string;
  name?: string;
}

export interface ChatResponse {
  answer: string;
  tool_calls: Array<{ name: string; result?: any; error?: string }>;
  error?: string;
}

@Injectable({ providedIn: 'root' })
export class ChatbotService {
  constructor(private http: HttpClient, private config: ConfigService) {}

  sendConversation(messages: ChatMessage[]): Observable<ChatResponse> {
    const url = `${this.config.API_ENDPOINT}/chatbot/message`;
    return this.http.post<ChatResponse>(url, { messages });
  }
}
