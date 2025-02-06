import { TestBed } from '@angular/core/testing';
import { MatSnackBar } from '@angular/material/snack-bar';
import { HttpErrorResponse } from '@angular/common/http';
import { ErrorService } from './error.service';

describe('ErrorService', () => {
  let service: ErrorService;
  let snackBarSpy: jasmine.SpyObj<MatSnackBar>;

  beforeEach(() => {
    const spy = jasmine.createSpyObj('MatSnackBar', ['open']);
    TestBed.configureTestingModule({
      providers: [
        ErrorService,
        { provide: MatSnackBar, useValue: spy }
      ]
    });
    service = TestBed.inject(ErrorService);
    snackBarSpy = TestBed.inject(MatSnackBar) as jasmine.SpyObj<MatSnackBar>;
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  it('should handle client-side error', () => {
    const errorEvent = new ErrorEvent('Client Error', { message: 'Test error' });
    const error = new HttpErrorResponse({ error: errorEvent });
    
    service.handleError(error).subscribe({
      error: (err) => {
        expect(err.message).toBe('Test error');
        expect(snackBarSpy.open).toHaveBeenCalledWith(
          'Test error',
          'Close',
          jasmine.any(Object)
        );
      }
    });
  });

  it('should handle server-side error with detail', () => {
    const error = new HttpErrorResponse({
      error: { detail: 'Not authorized' },
      status: 403
    });
    
    service.handleError(error).subscribe({
      error: (err) => {
        expect(err.message).toBe('Not authorized');
        expect(snackBarSpy.open).toHaveBeenCalledWith(
          'Not authorized',
          'Close',
          jasmine.any(Object)
        );
      }
    });
  });

  it('should handle server-side error without detail', () => {
    const error = new HttpErrorResponse({
      error: {},
      status: 403
    });
    
    service.handleError(error).subscribe({
      error: (err) => {
        expect(err.message).toBe('You are not authorized to perform this action');
        expect(snackBarSpy.open).toHaveBeenCalledWith(
          'You are not authorized to perform this action',
          'Close',
          jasmine.any(Object)
        );
      }
    });
  });

  it('should handle 404 error', () => {
    const error = new HttpErrorResponse({
      error: {},
      status: 404
    });
    
    service.handleError(error).subscribe({
      error: (err) => {
        expect(err.message).toBe('Resource not found');
        expect(snackBarSpy.open).toHaveBeenCalledWith(
          'Resource not found',
          'Close',
          jasmine.any(Object)
        );
      }
    });
  });

  it('should handle unknown server error', () => {
    const error = new HttpErrorResponse({
      error: {},
      status: 500
    });
    
    service.handleError(error).subscribe({
      error: (err) => {
        expect(err.message).toBe('Server error');
        expect(snackBarSpy.open).toHaveBeenCalledWith(
          'Server error',
          'Close',
          jasmine.any(Object)
        );
      }
    });
  });
});