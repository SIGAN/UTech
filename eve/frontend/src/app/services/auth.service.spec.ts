import { TestBed } from '@angular/core/testing';
import { HttpClientTestingModule, HttpTestingController } from '@angular/common/http/testing';
import { AuthService } from './auth.service';
import { environment } from '../../environments/environment';

describe('AuthService', () => {
  let service: AuthService;
  let httpMock: HttpTestingController;

  beforeEach(() => {
    TestBed.configureTestingModule({
      imports: [HttpClientTestingModule],
      providers: [AuthService]
    });
    service = TestBed.inject(AuthService);
    httpMock = TestBed.inject(HttpTestingController);
  });

  afterEach(() => {
    httpMock.verify();
    localStorage.clear();
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });

  describe('login', () => {
    it('should store session data and update BehaviorSubjects', () => {
      const testEmail = 'test@example.com';
      const testSessionId = 'test-session-id';

      service.login(testEmail).subscribe(response => {
        expect(response.session_id).toBe(testSessionId);
        expect(localStorage.getItem('sessionId')).toBe(testSessionId);
        expect(localStorage.getItem('userEmail')).toBe(testEmail);
        expect(service.getSessionId()).toBe(testSessionId);
        expect(service.getUserEmail()).toBe(testEmail);
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/login`);
      expect(req.request.method).toBe('POST');
      expect(req.request.body).toEqual({ email: testEmail });
      req.flush({ session_id: testSessionId });
    });
  });

  describe('logout', () => {
    it('should clear session data and update BehaviorSubjects', () => {
      // Setup initial state
      localStorage.setItem('sessionId', 'test-session');
      localStorage.setItem('userEmail', 'test@example.com');
      service.login('test@example.com').subscribe();
      httpMock.expectOne(`${environment.apiUrl}/auth/login`).flush({ session_id: 'test-session' });

      service.logout().subscribe(() => {
        expect(localStorage.getItem('sessionId')).toBeNull();
        expect(localStorage.getItem('userEmail')).toBeNull();
        expect(service.getSessionId()).toBeNull();
        expect(service.getUserEmail()).toBeNull();
      });

      const req = httpMock.expectOne(`${environment.apiUrl}/auth/logout`);
      expect(req.request.method).toBe('POST');
      expect(req.request.headers.get('Authorization')).toBe('test-session');
      req.flush({});
    });
  });

  describe('getSessionId', () => {
    it('should return session id from BehaviorSubject', () => {
      const testSessionId = 'test-session-id';
      service.login('test@example.com').subscribe();
      httpMock.expectOne(`${environment.apiUrl}/auth/login`).flush({ session_id: testSessionId });
      expect(service.getSessionId()).toBe(testSessionId);
    });

    it('should return null if no session id exists', () => {
      expect(service.getSessionId()).toBeNull();
    });
  });

  describe('getUserEmail', () => {
    it('should return user email from BehaviorSubject', () => {
      const testEmail = 'test@example.com';
      service.login(testEmail).subscribe();
      httpMock.expectOne(`${environment.apiUrl}/auth/login`).flush({ session_id: 'test-session' });
      expect(service.getUserEmail()).toBe(testEmail);
    });

    it('should return null if no user email exists', () => {
      expect(service.getUserEmail()).toBeNull();
    });
  });

  describe('isLoggedIn', () => {
    it('should return true if session id exists', () => {
      service.login('test@example.com').subscribe();
      httpMock.expectOne(`${environment.apiUrl}/auth/login`).flush({ session_id: 'test-session' });
      expect(service.isLoggedIn()).toBeTrue();
    });

    it('should return false if no session id exists', () => {
      expect(service.isLoggedIn()).toBeFalse();
    });
  });
});