import { inject, Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { map, Observable } from 'rxjs';
import { Message } from './messages/messages.model';
import { environment } from '../../environments/environment';

export interface ChatResponse {
  message?: string;
  action?: string;
  conversation_id: string;
}

@Injectable({
  providedIn: 'root',
})
export class ChatApiService {
  private http = inject(HttpClient);
  private apiUrl = environment.apiUrl;

  sendMessage(
    userMessage: string,
    conversationId: string | null
  ): Observable<ChatResponse> {
    const payload: any = { message: userMessage };
    if (conversationId) {
      payload.conversation_id = conversationId;
    }

    return this.http.post<ChatResponse>(`${this.apiUrl}/api/chat`, payload);
  }
}
