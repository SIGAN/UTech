import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;
  private sessionId = new BehaviorSubject<string | null>(localStorage.getItem('sessionId'));
  private userEmail = new BehaviorSubject<string | null>(localStorage.getItem('userEmail'));

  constructor(private http: HttpClient) { }

  login(email: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/login`, { email }).pipe(
      tap((response: any) => {
        localStorage.setItem('sessionId', response.session_id);
        localStorage.setItem('userEmail', email);
        this.sessionId.next(response.session_id);
        this.userEmail.next(email);
      })
    );
  }

  logout(): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/logout`, {}).pipe(
      tap(() => {
        this.clearLocalStorage();
      })
    );
  }

  isLoggedIn(): boolean {
    return !!this.sessionId.value;
  }

  getSessionId(): string | null {
    return this.sessionId.value;
  }

  getUserEmail(): string | null {
    return this.userEmail.value;
  }

  getCurrentUserEmail(): string | null {
    return this.userEmail.value;
  }

  public clearLocalStorage(): void {
    localStorage.removeItem('sessionId');
    localStorage.removeItem('userEmail');
    this.sessionId.next(null);
    this.userEmail.next(null);
  }
}