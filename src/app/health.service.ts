import { inject, Injectable } from '@angular/core';
import { environment } from '../environments/environment';
import { HttpClient } from '@angular/common/http';
import { catchError, map } from 'rxjs';
import { Observable, of } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class HealthService {
  private apiUrl = environment.apiUrl;

  http = inject(HttpClient);

  checkHealth(): Observable<boolean> {
    return this.http.get<any>(`${this.apiUrl}/api/health`).pipe(
      map((response) => response.status === 'ok'),
      catchError((error) => {
        console.error('Health check failed:', error);
        return of(false);
      })
    );
  }
}
