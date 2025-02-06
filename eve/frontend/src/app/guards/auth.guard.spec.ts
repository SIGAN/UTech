import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import { AuthGuard } from './auth.guard';

describe('AuthGuard', () => {
  let guard: AuthGuard;
  let authService: jasmine.SpyObj<AuthService>;
  let router: jasmine.SpyObj<Router>;

  beforeEach(() => {
    const authServiceSpy = jasmine.createSpyObj('AuthService', ['isLoggedIn']);
    const routerSpy = jasmine.createSpyObj('Router', ['navigate']);

    TestBed.configureTestingModule({
      providers: [
        AuthGuard,
        { provide: AuthService, useValue: authServiceSpy },
        { provide: Router, useValue: routerSpy }
      ]
    });

    guard = TestBed.inject(AuthGuard);
    authService = TestBed.inject(AuthService) as jasmine.SpyObj<AuthService>;
    router = TestBed.inject(Router) as jasmine.SpyObj<Router>;
  });

  it('should be created', () => {
    expect(guard).toBeTruthy();
  });

  it('should allow access to login page when not authenticated', () => {
    authService.isLoggedIn.and.returnValue(false);
    
    const result = guard.canActivate(
      { routeConfig: { path: 'login' } } as any,
      { url: '/login' } as any
    );

    expect(result).toBe(true);
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('should redirect to events when accessing login page while authenticated', () => {
    authService.isLoggedIn.and.returnValue(true);
    
    const result = guard.canActivate(
      { routeConfig: { path: 'login' } } as any,
      { url: '/login' } as any
    );

    expect(result).toBe(false);
    expect(router.navigate).toHaveBeenCalledWith(['/events']);
  });

  it('should allow access to protected route when authenticated', () => {
    authService.isLoggedIn.and.returnValue(true);
    
    const result = guard.canActivate(
      { routeConfig: { path: 'events' } } as any,
      { url: '/events' } as any
    );

    expect(result).toBe(true);
    expect(router.navigate).not.toHaveBeenCalled();
  });

  it('should redirect to login when accessing protected route without authentication', () => {
    authService.isLoggedIn.and.returnValue(false);
    
    const result = guard.canActivate(
      { routeConfig: { path: 'events' } } as any,
      { url: '/events' } as any
    );

    expect(result).toBe(false);
    expect(router.navigate).toHaveBeenCalledWith(['/login'], {
      queryParams: { returnUrl: '/events' }
    });
  });

  it('should preserve query parameters when redirecting to login', () => {
    authService.isLoggedIn.and.returnValue(false);
    
    const result = guard.canActivate(
      { routeConfig: { path: 'events' } } as any,
      { url: '/events/1?view=details' } as any
    );

    expect(result).toBe(false);
    expect(router.navigate).toHaveBeenCalledWith(['/login'], {
      queryParams: { returnUrl: '/events/1?view=details' }
    });
  });
});