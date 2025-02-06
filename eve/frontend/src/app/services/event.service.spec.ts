import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { EventService } from './event.service';
import { Event, EventDTO } from '../models/event.model';
import { environment } from '../../environments/environment';
import { ErrorService } from './error.service';
import { MatSnackBar } from '@angular/material/snack-bar';
import { mockEvent, mockEventDTO, mockErrorResponse, TEST_DATE_LOCAL, TEST_DATE_UTC } from '../testing/test-helpers';

describe('EventService', () => {
  let service: EventService;
  let httpMock: HttpTestingController;
  let errorService: jasmine.SpyObj<ErrorService>;
  const API_URL = `${environment.apiUrl}/events`;

  beforeEach(() => {
    const errorServiceSpy = jasmine.createSpyObj('ErrorService', ['handleError']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        EventService,
        { provide: ErrorService, useValue: errorServiceSpy },
        { provide: MatSnackBar, useValue: snackBarSpy }
      ]
    });
    service = TestBed.inject(EventService);
    httpMock = TestBed.inject(HttpTestingController);
    errorService = TestBed.inject(ErrorService) as jasmine.SpyObj<ErrorService>;
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getEvents', () => {
    it('should return events list with converted dates', () => {
      const mockDTOs: EventDTO[] = [mockEventDTO];
      const expectedEvents: Event[] = [mockEvent];

      service.getEvents().subscribe(events => {
        expect(events).toEqual(expectedEvents);
        expect(events[0].start_time).toEqual(TEST_DATE_LOCAL);
      });

      const req = httpMock.expectOne(API_URL);
      expect(req.request.method).toBe('GET');
      req.flush(mockDTOs);
    });

    it('should handle server error', () => {
      service.getEvents().subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(API_URL);
      req.flush(mockErrorResponse.serverError.error, mockErrorResponse.serverError);
    });
  });

  describe('getUpcomingEvents', () => {
    it('should return upcoming events with converted dates', () => {
      const mockDTOs: EventDTO[] = [mockEventDTO];
      const expectedEvents: Event[] = [mockEvent];

      service.getUpcomingEvents().subscribe(events => {
        expect(events).toEqual(expectedEvents);
        expect(events[0].start_time).toEqual(TEST_DATE_LOCAL);
      });

      const req = httpMock.expectOne(`${API_URL}/upcoming`);
      expect(req.request.method).toBe('GET');
      req.flush(mockDTOs);
    });

    it('should handle server error', () => {
      service.getUpcomingEvents().subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/upcoming`);
      req.flush(mockErrorResponse.serverError.error, mockErrorResponse.serverError);
    });
  });

  describe('getMyEvents', () => {
    it('should return user events with converted dates', () => {
      const mockDTOs: EventDTO[] = [mockEventDTO];
      const expectedEvents: Event[] = [mockEvent];

      service.getMyEvents().subscribe(events => {
        expect(events).toEqual(expectedEvents);
        expect(events[0].start_time).toEqual(TEST_DATE_LOCAL);
      });

      const req = httpMock.expectOne(`${API_URL}/my`);
      expect(req.request.method).toBe('GET');
      req.flush(mockDTOs);
    });

    it('should handle unauthorized error', () => {
      service.getMyEvents().subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/my`);
      req.flush(mockErrorResponse.unauthorized.error, mockErrorResponse.unauthorized);
    });
  });

  describe('getEvent', () => {
    it('should return single event with converted dates', () => {
      service.getEvent(1).subscribe(event => {
        expect(event).toEqual(mockEvent);
        expect(event.start_time).toEqual(TEST_DATE_LOCAL);
      });

      const req = httpMock.expectOne(`${API_URL}/1`);
      expect(req.request.method).toBe('GET');
      req.flush(mockEventDTO);
    });

    it('should handle not found error', () => {
      service.getEvent(999).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/999`);
      req.flush(mockErrorResponse.notFound.error, mockErrorResponse.notFound);
    });
  });

  describe('createEvent', () => {
    it('should create event with converted dates', () => {
      const newEvent = { ...mockEvent };
      delete newEvent.id;

      service.createEvent(newEvent).subscribe(event => {
        expect(event).toEqual(mockEvent);
        expect(event.start_time).toEqual(TEST_DATE_LOCAL);
      });

      const req = httpMock.expectOne(API_URL);
      expect(req.request.method).toBe('POST');
      // Verify the request sends UTC times
      expect(req.request.body.start_time).toBe(TEST_DATE_UTC);
      req.flush(mockEventDTO);
    });

    it('should handle validation error', () => {
      const invalidEvent = { ...mockEvent, title: '' };
      delete invalidEvent.id;

      service.createEvent(invalidEvent).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(API_URL);
      req.flush(
        { detail: 'title cannot be empty' },
        { status: 400, statusText: 'Bad Request' }
      );
    });
  });

  describe('updateEvent', () => {
    it('should update event with converted dates', () => {
      service.updateEvent(1, mockEvent).subscribe(event => {
        expect(event).toEqual(mockEvent);
        expect(event.start_time).toEqual(TEST_DATE_LOCAL);
      });

      const req = httpMock.expectOne(`${API_URL}/1`);
      expect(req.request.method).toBe('PUT');
      // Verify the request sends UTC times
      expect(req.request.body.start_time).toBe(TEST_DATE_UTC);
      req.flush(mockEventDTO);
    });

    it('should handle unauthorized update', () => {
      service.updateEvent(1, mockEvent).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/1`);
      req.flush(mockErrorResponse.forbidden.error, mockErrorResponse.forbidden);
    });

    it('should handle not found error', () => {
      service.updateEvent(999, mockEvent).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/999`);
      req.flush(mockErrorResponse.notFound.error, mockErrorResponse.notFound);
    });
  });

  describe('deleteEvent', () => {
    it('should delete event', () => {
      service.deleteEvent(1).subscribe(response => {
        expect(response).toBeNull();
      });

      const req = httpMock.expectOne(`${API_URL}/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });

    it('should handle unauthorized delete', () => {
      service.deleteEvent(1).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/1`);
      expect(req.request.method).toBe('DELETE');
      req.flush(mockErrorResponse.forbidden.error, mockErrorResponse.forbidden);
    });

    it('should handle not found error', () => {
      service.deleteEvent(999).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/999`);
      expect(req.request.method).toBe('DELETE');
      req.flush(mockErrorResponse.notFound.error, mockErrorResponse.notFound);
    });
  });

  describe('error handling', () => {
    it('should handle validation errors', () => {
      const invalidEvent = {
        ...mockEvent,
        title: '',
        start_time: new Date('2024-01-01'),
        end_time: new Date('2023-01-01')
      };

      service.createEvent(invalidEvent).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(API_URL);
      req.flush(
        { detail: 'Invalid request data' },
        { status: 400, statusText: 'Bad Request' }
      );
    });

    it('should handle server errors with proper messages', () => {
      service.getEvents().subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(API_URL);
      req.flush(mockErrorResponse.serverError.error, mockErrorResponse.serverError);
    });

    it('should handle network errors', () => {
      service.getEvents().subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(API_URL);
      req.error(new ErrorEvent('Network error'));
    });
  });
});