import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { catchError, map } from 'rxjs/operators';
import { Event, EventDTO, fromEventDTO, toEventDTO } from '../models/event.model';
import { environment } from '../../environments/environment';
import { ErrorService } from './error.service';

@Injectable({
  providedIn: 'root'
})
export class EventService {
  private apiUrl = `${environment.apiUrl}/events`;

  constructor(
    private http: HttpClient,
    private errorService: ErrorService
  ) {}

  getEvents(): Observable<Event[]> {
    return this.http.get<EventDTO[]>(this.apiUrl)
      .pipe(
        map(dtos => dtos.map(dto => fromEventDTO(dto))),
        catchError(err => this.errorService.handleError(err))
      );
  }

  getUpcomingEvents(): Observable<Event[]> {
    return this.http.get<EventDTO[]>(`${this.apiUrl}/upcoming`)
      .pipe(
        map(dtos => dtos.map(dto => fromEventDTO(dto))),
        catchError(err => this.errorService.handleError(err))
      );
  }

  getMyEvents(): Observable<Event[]> {
    return this.http.get<EventDTO[]>(`${this.apiUrl}/my`)
      .pipe(
        map(dtos => dtos.map(dto => fromEventDTO(dto))),
        catchError(err => this.errorService.handleError(err))
      );
  }

  getEvent(id: number): Observable<Event> {
    return this.http.get<EventDTO>(`${this.apiUrl}/${id}`)
      .pipe(
        map(dto => fromEventDTO(dto)),
        catchError(err => this.errorService.handleError(err))
      );
  }

  createEvent(event: Event): Observable<Event> {
    const dto = toEventDTO(event);
    return this.http.post<EventDTO>(this.apiUrl, dto)
      .pipe(
        map(responseDto => fromEventDTO(responseDto)),
        catchError(err => this.errorService.handleError(err))
      );
  }

  updateEvent(id: number, event: Event): Observable<Event> {
    const dto = toEventDTO(event);
    return this.http.put<EventDTO>(`${this.apiUrl}/${id}`, dto)
      .pipe(
        map(responseDto => fromEventDTO(responseDto)),
        catchError(err => this.errorService.handleError(err))
      );
  }

  deleteEvent(id: number): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`)
      .pipe(catchError(err => this.errorService.handleError(err)));
  }
}