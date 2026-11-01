import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';
import { AuthService } from './auth.service';

// Pages that need a login: not logged in? Go to /login instead.
// The guard only steers the browser; the gateway and API still check the token on every request.
export const authGuard: CanActivateFn = () => {
  const auth = inject(AuthService);
  return auth.isLoggedIn() || inject(Router).parseUrl('/login');
};
