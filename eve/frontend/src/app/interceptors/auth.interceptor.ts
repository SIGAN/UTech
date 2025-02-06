import { Injectable } from '@angular/core';
import { HttpInterceptor, HttpRequest, HttpHandler, HttpEvent, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';
import { ErrorService } from '../services/error.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(
    private authService: AuthService,
    private router: Router,
    private errorService: ErrorService
  ) {}

  intercept(request: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const sessionId = this.authService.getSessionId();
    if (sessionId && !request.url.includes('api/auth/login')) {
      request = request.clone({
        setHeaders: {
          Authorization: sessionId
        }
      });
    }

    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        // Clear session on auth errors or session-related errors
        if (error.status === 401 || error.status === 403 || 
            error.error?.detail?.toLowerCase().includes('session') || 
            error.error?.detail?.toLowerCase().includes('unauthorized')) {
          this.authService.clearLocalStorage();
          // Store current URL for redirect after login
          const currentUrl = this.router.url;
          this.router.navigate(['/login'], {
            queryParams: { returnUrl: currentUrl }
          });
          return throwError(() => error);
        }
        return this.errorService.handleError(error);
      })
    );
  }
}