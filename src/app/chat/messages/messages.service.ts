import { inject, Injectable, signal } from '@angular/core';
import { environment } from '../../../environments/environment';
import { HttpClient } from '@angular/common/http';
import { MatDialog } from '@angular/material/dialog';
import { Message } from './messages.model';
import { ChatApiService, ChatResponse } from '../api.service';
import { RealPersonDialogComponent } from '../../menu/real-person-dialog/real-person-dialog.component';

@Injectable({
  providedIn: 'root',
})
export class MessagesService {
  private http = inject(HttpClient);
  private apiService = inject(ChatApiService);
  private dialog = inject(MatDialog);

  public messages = signal<Message[]>([]);
  private conversationId: string | null = null;

  addUserMessage(content: string) {
    const userMessage: Message = {
      id: this.messages().length + 1,
      from: 'user',
      content: content,
      timestamp: new Date(),
    };
    this.messages.update((messages) => [...messages, userMessage]);
  }

  addMessage(content: string) {
    this.addUserMessage(content);

    // Check for keywords to escalate
    if (
      content.toLowerCase().includes('mitarbeiter') ||
      content.toLowerCase().includes('real person')
    ) {
      setTimeout(() => this.openRealPersonDialog(), 1000);
      return;
    }

    // Generate a bot response
    this.apiService.sendMessage(content, this.conversationId).subscribe({
      next: (response: ChatResponse) => {
        this.conversationId = response.conversation_id;

        if (response.action === 'open_real_person_dialog') {
          this.addBotMessage(
            "It seems I'm unable to help you with this. Let me connect you to a human."
          );
          setTimeout(() => this.openRealPersonDialog(), 1000);
        } else if (response.message) {
          this.addBotMessage(response.message);
        }
      },
      error: (error) => this.handleError(error),
    });
  }

  addBotMessage(content: string) {
    const botAnswer: Message = {
      id: this.messages().length + 1,
      from: 'bot',
      content: content,
      timestamp: new Date(),
    };
    this.messages.update((messages) => [...messages, botAnswer]);
  }

  openRealPersonDialog() {
    const dialogRef = this.dialog.open(RealPersonDialogComponent);

    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        const lastMessage =
          this.messages().slice(-1)[0]?.content || 'No last message';
        this.escalateToHuman(lastMessage, result);
      }
    });
  }

  escalateToHuman(message: string, email: string) {
    const payload = {
      message: message,
      conversation_id: this.conversationId,
      email: email,
    };

    this.http.post(`${environment.apiUrl}/api/escalate`, payload).subscribe({
      next: (response) => {
        console.log('Escalation sent to backend successfully', response);
        this.addBotMessage(
          'Thank you for your message. We will get back to you shortly.'
        );
        setTimeout(() => {
          window.location.reload();
        }, 5000);
      },
      error: (error) => {
        console.error('Error escalating to backend:', error);
      },
    });
  }

  resetMessages() {
    this.messages.set([]);
    this.conversationId = null;
    console.log('SERVICE: Messages reset');
  }

  setLanguagePreference(instruction: string) {
    this.apiService.sendMessage(instruction, this.conversationId).subscribe({
      next: (response) => {
        console.log('Language preference updated');
        if (response.message) {
          this.addBotMessage(response.message);
        }
      },
      error: (error) => this.handleError(error),
    });
  }

  private handleError(error: any) {
    console.error('Error:', error);
    const errorMessage: Message = {
      id: this.messages().length + 1,
      from: 'bot',
      content: 'Sorry, I encountered an error. Please try again later.',
      timestamp: new Date(),
    };
    this.messages.update((messages) => [...messages, errorMessage]);
  }
}
