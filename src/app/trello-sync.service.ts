import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, catchError, of } from 'rxjs';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class TrelloSyncService {
  private apiUrl = environment.apiUrl;
  private http = inject(HttpClient);

  /**
   * Sync all unsaved conversations to Trello
   * @returns Observable with the sync results
   */
  syncConversationsToTrello(): Observable<any> {
    return this.http.post<any>(`${this.apiUrl}/api/sync/trello`, {}).pipe(
      catchError((error) => {
        console.error('Error syncing conversations to Trello:', error);
        return of({ error: error.message });
      })
    );
  }
}
