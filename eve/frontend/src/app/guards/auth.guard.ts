import { Injectable } from '@angular/core';
import { CanActivate, Router, ActivatedRouteSnapshot, RouterStateSnapshot } from '@angular/router';
import { AuthService } from '../services/auth.service';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot
  ): boolean {
    // Allow access to login page without authentication
    if (route.routeConfig?.path === 'login') {
      if (this.authService.isLoggedIn()) {
        // If authenticated, redirect to events
        this.router.navigate(['/events']);
        return false;
      }
      return true;
    }

    // For all other routes, require authentication
    if (this.authService.isLoggedIn()) {
      return true;
    }

    // Store attempted URL for redirection after login
    this.router.navigate(['/login'], {
      queryParams: { returnUrl: state.url }
    });
    return false;
  }
}