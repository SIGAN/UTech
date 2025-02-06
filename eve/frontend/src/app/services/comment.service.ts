import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { Comment } from '../models/comment.model';
import { environment } from '../../environments/environment';
import { ErrorService } from './error.service';

@Injectable({
  providedIn: 'root'
})
export class CommentService {
  private readonly API_URL = `${environment.apiUrl}/events`;

  constructor(
    private http: HttpClient,
    private errorService: ErrorService
  ) {}

  getEventComments(eventId: number): Observable<Comment[]> {
    return this.http.get<Comment[]>(`${this.API_URL}/${eventId}/comments`)
      .pipe(catchError(err => this.errorService.handleError(err)));
  }

  createComment(eventId: number, comment: Omit<Comment, 'id' | 'event_id' | 'user_id' | 'author_email'>): Observable<Comment> {
    return this.http.post<Comment>(`${this.API_URL}/${eventId}/comments`, comment)
      .pipe(catchError(err => this.errorService.handleError(err)));
  }

  updateComment(eventId: number, commentId: number, comment: Omit<Comment, 'id' | 'event_id' | 'user_id' | 'author_email'>): Observable<Comment> {
    return this.http.put<Comment>(`${this.API_URL}/${eventId}/comments/${commentId}`, comment)
      .pipe(catchError(err => this.errorService.handleError(err)));
  }

  deleteComment(eventId: number, commentId: number): Observable<void> {
    return this.http.delete<void>(`${this.API_URL}/${eventId}/comments/${commentId}`)
      .pipe(catchError(err => this.errorService.handleError(err)));
  }
}