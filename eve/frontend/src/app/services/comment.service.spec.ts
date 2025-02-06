import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { CommentService } from './comment.service';
import { mockComment, mockErrorResponse } from '../testing/test-helpers';
import { environment } from '../../environments/environment';
import { ErrorService } from './error.service';
import { MatSnackBar } from '@angular/material/snack-bar';

describe('CommentService', () => {
  let service: CommentService;
  let httpMock: HttpTestingController;
  let errorService: jasmine.SpyObj<ErrorService>;
  const API_URL = `${environment.apiUrl}/events`;

  beforeEach(() => {
    const errorServiceSpy = jasmine.createSpyObj('ErrorService', ['handleError']);
    const snackBarSpy = jasmine.createSpyObj('MatSnackBar', ['open']);

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        CommentService,
        { provide: ErrorService, useValue: errorServiceSpy },
        { provide: MatSnackBar, useValue: snackBarSpy }
      ]
    });
    service = TestBed.inject(CommentService);
    httpMock = TestBed.inject(HttpTestingController);
    errorService = TestBed.inject(ErrorService) as jasmine.SpyObj<ErrorService>;
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('getEventComments', () => {
    it('should return comments for an event', () => {
      const mockComments = [mockComment];
      const eventId = 1;

      service.getEventComments(eventId).subscribe(comments => {
        expect(comments).toEqual(mockComments);
      });

      const req = httpMock.expectOne(`${API_URL}/${eventId}/comments`);
      expect(req.request.method).toBe('GET');
      req.flush(mockComments);
    });
  });

  describe('createComment', () => {
    it('should create a comment', () => {
      const eventId = 1;
      const newComment = {
        message: 'Test Comment',
        rating: 5
      };

      service.createComment(eventId, newComment).subscribe(comment => {
        expect(comment).toEqual(mockComment);
      });

      const req = httpMock.expectOne(`${API_URL}/${eventId}/comments`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual(newComment);
      req.flush(mockComment);
    });
  });

  describe('updateComment', () => {
    it('should update a comment', () => {
      const eventId = 1;
      const commentId = 1;
      const updateData = {
        message: 'Updated Comment',
        rating: 4
      };

      service.updateComment(eventId, commentId, updateData).subscribe(comment => {
        expect(comment).toEqual({ ...mockComment, ...updateData });
      });

      const req = httpMock.expectOne(`${API_URL}/${eventId}/comments/${commentId}`);
      expect(req.request.method).toBe('PUT');
      expect(req.request.body).toEqual(updateData);
      req.flush({ ...mockComment, ...updateData });
    });
  });

  describe('deleteComment', () => {
    it('should delete a comment', () => {
      const eventId = 1;
      const commentId = 1;

      service.deleteComment(eventId, commentId).subscribe(response => {
        expect(response).toBeNull();
      });

      const req = httpMock.expectOne(`${API_URL}/${eventId}/comments/${commentId}`);
      expect(req.request.method).toBe('DELETE');
      req.flush(null);
    });

    it('should handle unauthorized delete', () => {
      const eventId = 1;
      const commentId = 1;

      service.deleteComment(eventId, commentId).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/${eventId}/comments/${commentId}`);
      expect(req.request.method).toBe('DELETE');
      req.flush(mockErrorResponse.forbidden.error, mockErrorResponse.forbidden);
    });
  });

  describe('error handling', () => {
    it('should handle 403 error on update', () => {
      const eventId = 1;
      const commentId = 1;
      const updateData = {
        message: 'Updated Comment',
        rating: 4
      };

      service.updateComment(eventId, commentId, updateData).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/${eventId}/comments/${commentId}`);
      expect(req.request.method).toBe('PUT');
      req.flush(mockErrorResponse.forbidden.error, mockErrorResponse.forbidden);
    });

    it('should handle 404 error', () => {
      const eventId = 999;
      const commentId = 999;

      service.getEventComments(eventId).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/${eventId}/comments`);
      expect(req.request.method).toBe('GET');
      req.flush(mockErrorResponse.notFound.error, mockErrorResponse.notFound);
    });

    it('should handle server error', () => {
      const eventId = 1;

      service.getEventComments(eventId).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/${eventId}/comments`);
      expect(req.request.method).toBe('GET');
      req.flush(mockErrorResponse.serverError.error, mockErrorResponse.serverError);
    });

    it('should handle validation error on create', () => {
      const eventId = 1;
      const invalidComment = {
        message: '',  // Empty message should fail validation
        rating: 10    // Invalid rating value
      };

      service.createComment(eventId, invalidComment).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/${eventId}/comments`);
      req.flush(
        { detail: 'Invalid request data' },
        { status: 400, statusText: 'Bad Request' }
      );
    });

    it('should handle network errors', () => {
      const eventId = 1;

      service.getEventComments(eventId).subscribe({
        error: (error) => {
          expect(errorService.handleError).toHaveBeenCalled();
        }
      });

      const req = httpMock.expectOne(`${API_URL}/${eventId}/comments`);
      req.error(new ErrorEvent('Network error'));
    });
  });
});