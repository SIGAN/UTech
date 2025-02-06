import { Injectable } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { MatSnackBar } from '@angular/material/snack-bar';
import { environment } from '../../environments/environment';

export interface ApiError {
  detail: string;
}

@Injectable({
  providedIn: 'root'
})
export class ErrorService {
  private config = environment.errorConfig;

  constructor(private snackBar: MatSnackBar) {}

  handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = this.config.defaultErrorMessage;

    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = error.error.message;
    } else {
      // Server-side error
      if (error.error?.detail) {
        errorMessage = error.error.detail;
      } else {
        switch (error.status) {
          case 400:
            errorMessage = 'Invalid request';
            break;
          case 401:
            errorMessage = 'Unauthorized - please log in';
            break;
          case 403:
            errorMessage = 'You are not authorized to perform this action';
            break;
          case 404:
            errorMessage = 'Resource not found';
            break;
          case 500:
            errorMessage = 'Server error';
            break;
        }
      }
    }

    this.showError(errorMessage);
    return throwError(() => new Error(errorMessage));
  }

  showError(message: string): void {
    this.snackBar.open(message, 'Close', {
      duration: this.config.errorDisplayDuration,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
      panelClass: [this.config.errorSnackbarClass]
    });
  }
}