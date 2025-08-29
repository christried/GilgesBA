import { Component, inject, OnInit } from '@angular/core';
import { MatCardModule } from '@angular/material/card';

import { ChatComponent } from './chat/chat.component';
import { MenuComponent } from './menu/menu.component';
import { HealthService } from './health.service';
import { MessagesService } from './chat/messages/messages.service';
import { TrelloSyncService } from './trello-sync.service';

@Component({
  selector: 'app-root',
  imports: [ChatComponent, MenuComponent, MatCardModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css',
})
export class AppComponent implements OnInit {
  backendStatus: boolean = false;
  title = 'app';
  healthService = inject(HealthService);
  messagesService = inject(MessagesService);
  trelloSyncService = inject(TrelloSyncService);

  ngOnInit(): void {
    this.checkApiHealth();
  }

  checkApiHealth() {
    this.healthService.checkHealth().subscribe({
      next: (isHealthy) => {
        this.backendStatus = isHealthy;
        if (this.backendStatus) {
          console.log('Backend is running!');
          // Trigger Trello synchronization in the background
          this.syncConversationsToTrello();
        }
      },
      error: (err) => {
        console.error('Error checking health:', err);
        this.backendStatus = false;
      },
    });
  }

  /**
   * Synchronize unsaved conversations to Trello
   * This runs asynchronously and shouldnt block the application if it takes too long
   */
  private syncConversationsToTrello(): void {
    console.log('Starting Trello synchronization in the background...');
    this.trelloSyncService.syncConversationsToTrello().subscribe({
      next: (result) => {
        console.log('Trello synchronization completed:', result);
        if (result.error) {
          console.error('Sync error:', result.error);
        } else {
          console.log(
            `Synced ${result.success} conversations, skipped ${result.skipped}, failed ${result.failed}`
          );
        }
      },
      error: (error) => {
        console.error('Error during Trello synchronization:', error);
      },
    });
  }
}
