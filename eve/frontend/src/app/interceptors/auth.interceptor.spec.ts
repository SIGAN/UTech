import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { HTTP_INTERCEPTORS, HttpClient, HttpErrorResponse } from '@angular/common/http';
import { throwError } from 'rxjs';
import { Router } from '@angular/router';
import { AuthInterceptor } from './auth.interceptor';
import { AuthService } from '../services/auth.service';
import { ErrorService } from '../services/error.service';
import { mockErrorResponse } from '../testing/test-helpers';

describe('AuthInterceptor', () => {
  let httpMock: HttpTestingController;
  let httpClient: HttpClient;
  let authService: jasmine.SpyObj<AuthService>;
  let errorService: jasmine.SpyObj<ErrorService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(() => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['getSessionId', 'clearLocalStorage']);
    const errorServiceSpy = jasmine.createSpyObj('ErrorService', ['handleError']);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    errorServiceSpy.handleError.and.callFake((error: HttpErrorResponse) => throwError(() => error));

    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [
        {
          provide: HTTP_INTERCEPTORS,
          useClass: AuthInterceptor,
          multi: true
        },
        { provide: AuthService, useValue: authServiceSpy },
        { provide: ErrorService, useValue: errorServiceSpy },
        { provide: Router, useValue: routerSpy }
      ]
    });

    // Ensure services are initialized in test context
    TestBed.runInInjectionContext(() => {
      httpClient = TestBed.inject(HttpClient);
      httpMock = TestBed.inject(HttpTestingController);
      authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
      errorService = TestBed.inject(ErrorService) as jasmine.SpyObj<ErrorService>;
      router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
    });
  });

  afterEach(() => {
    httpMock.verify();
  });

  it('should add Authorization header when session exists', () => {
    const testSessionId = 'test-session-id';
    authService.getSessionId.and.returnValue(testSessionId);

    httpClient.get('/api/test').subscribe();

    const req = httpMock.expectOne('/api/test');
    expect(req.request.headers.has('Authorization')).toBeTrue();
    expect(req.request.headers.get('Authorization')).toBe(testSessionId);
    req.flush({});
  });

  it('should not add Authorization header for login request', () => {
    const testSessionId = 'test-session-id';
    authService.getSessionId.and.returnValue(testSessionId);

    httpClient.post('/api/auth/login', {}).subscribe();

    const httpRequest = httpMock.expectOne('/api/auth/login');
    expect(httpRequest.request.headers.has('Authorization')).toBeFalse();
  });

  it('should not add Authorization header when no session exists', () => {
    authService.getSessionId.and.returnValue(null);

    httpClient.get('/api/test').subscribe();

    const httpRequest = httpMock.expectOne('/api/test');
    expect(httpRequest.request.headers.has('Authorization')).toBeFalse();
  });

  it('should handle 401 error by clearing session and redirecting to login', (done) => {
    authService.getSessionId.and.returnValue('test-session-id');

    httpClient.get('/api/test').subscribe({
      next: () => fail('should have failed with 401'),
      error: (error: HttpErrorResponse) => {
        expect(error.status).toBe(401);
        expect(authService.clearLocalStorage).toHaveBeenCalled();
        expect(router.navigate).toHaveBeenCalledWith(['/login'], {
          queryParams: { returnUrl: undefined }
        });
        done();
      }
    });

    const req = httpMock.expectOne('/api/test');
    req.flush('Unauthorized', { status: 401, statusText: 'Unauthorized' });
  });

  it('should handle 403 errors as auth errors', () => {
    authService.getSessionId.and.returnValue('test-session-id');
    errorService.handleError.and.returnValue(throwError(() => mockErrorResponse.forbidden));

    httpClient.get('/api/test').subscribe({
      error: (error) => {
        expect(errorService.handleError).not.toHaveBeenCalled();
        expect(authService.clearLocalStorage).toHaveBeenCalled();
        expect(router.navigate).toHaveBeenCalledWith(['/login'], {
          queryParams: { returnUrl: undefined }
        });
      }
    });

    const httpRequest = httpMock.expectOne('/api/test');
    httpRequest.flush(mockErrorResponse.forbidden.error, mockErrorResponse.forbidden);
  });

  it('should handle 404 errors with error service', () => {
    authService.getSessionId.and.returnValue('test-session-id');
    errorService.handleError.and.returnValue(throwError(() => mockErrorResponse.notFound));

    httpClient.get('/api/test').subscribe({
      error: (error) => {
        expect(errorService.handleError).toHaveBeenCalled();
        expect(authService.clearLocalStorage).not.toHaveBeenCalled();
        expect(router.navigate).not.toHaveBeenCalled();
      }
    });

    const httpRequest = httpMock.expectOne('/api/test');
    httpRequest.flush(mockErrorResponse.notFound.error, mockErrorResponse.notFound);
  });

  it('should handle server errors with error service', () => {
    authService.getSessionId.and.returnValue('test-session-id');
    errorService.handleError.and.returnValue(throwError(() => mockErrorResponse.serverError));

    httpClient.get('/api/test').subscribe({
      error: (error) => {
        expect(errorService.handleError).toHaveBeenCalled();
        expect(authService.clearLocalStorage).not.toHaveBeenCalled();
        expect(router.navigate).not.toHaveBeenCalled();
      }
    });

    const httpRequest = httpMock.expectOne('/api/test');
    httpRequest.flush(mockErrorResponse.serverError.error, mockErrorResponse.serverError);
  });
});