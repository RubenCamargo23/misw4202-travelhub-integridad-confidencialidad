import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly AUTH_URL = 'http://localhost:8000';
  private token: string | null = null;

  constructor(private http: HttpClient, private router: Router) {}

  login(username: string, password: string): Observable<{ token: string }> {
    const body = new HttpParams()
      .set('username', username)
      .set('password', password);

    return this.http
      .post<{ token: string }>(`${this.AUTH_URL}/login`, body.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      })
      .pipe(tap((res) => { this.token = res.token; }));
  }

  logout(): void {
    this.token = null;
    this.router.navigate(['/login']);
  }

  getToken(): string | null {
    return this.token;
  }

  isLoggedIn(): boolean {
    return !!this.token;
  }

  getUsername(): string {
    if (!this.token) return '';
    try {
      const payload = JSON.parse(atob(this.token.split('.')[1]));
      return payload.sub ?? '';
    } catch {
      return '';
    }
  }
}
