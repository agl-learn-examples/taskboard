import { HttpClient } from '@angular/common/http';
import { Injectable, computed, inject, signal } from '@angular/core';
import { Observable, catchError, finalize, map, of } from 'rxjs';

// What POST /v1/auth/login answers
export interface Tokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

const ACCESS = 'taskboard.access_token';
const REFRESH = 'taskboard.refresh_token';

// Logs in and out, and remembers the tokens in localStorage so a page reload keeps you logged in.
// shortcut: no automatic refresh; when the 15-minute access token runs out you log in again (see the interceptor).
@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly http = inject(HttpClient);
  private readonly token = signal<string | null>(localStorage.getItem(ACCESS));

  readonly isLoggedIn = computed(() => this.token() !== null);

  accessToken(): string | null {
    return this.token();
  }

  login(email: string, password: string): Observable<void> {
    return this.http.post<Tokens>('/v1/auth/login', { email, password }).pipe(
      map((tokens) => {
        localStorage.setItem(ACCESS, tokens.access_token);
        localStorage.setItem(REFRESH, tokens.refresh_token);
        this.token.set(tokens.access_token);
      }),
    );
  }

  // Tells the API to end the session, then forgets the tokens here, even if the API call fails.
  logout(): Observable<void> {
    const refresh_token = localStorage.getItem(REFRESH);
    return this.http.post<void>('/v1/auth/logout', { refresh_token }).pipe(
      catchError(() => of(undefined)),
      finalize(() => this.forget()),
    );
  }

  forget() {
    localStorage.removeItem(ACCESS);
    localStorage.removeItem(REFRESH);
    this.token.set(null);
  }
}
