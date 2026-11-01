import { TestBed } from '@angular/core/testing';
import { provideHttpClient } from '@angular/common/http';
import { HttpTestingController, provideHttpClientTesting } from '@angular/common/http/testing';
import { AuthService } from './auth.service';

// No real API here: HttpTestingController catches each request and lets the test answer it.
describe('AuthService', () => {
  let auth: AuthService;
  let http: HttpTestingController;

  beforeEach(() => {
    localStorage.clear();
    TestBed.configureTestingModule({ providers: [provideHttpClient(), provideHttpClientTesting()] });
    auth = TestBed.inject(AuthService);
    http = TestBed.inject(HttpTestingController);
  });

  afterEach(() => http.verify()); // no request left unanswered

  it('starts logged out', () => {
    expect(auth.isLoggedIn()).toBe(false);
  });

  it('logs in and keeps the tokens', () => {
    auth.login('priya@blueleaf.example', 'demo-password-123').subscribe();

    const req = http.expectOne('/v1/auth/login');
    expect(req.request.method).toBe('POST');
    expect(req.request.body).toEqual({ email: 'priya@blueleaf.example', password: 'demo-password-123' });
    req.flush({ access_token: 'acc', refresh_token: 'ref', token_type: 'Bearer', expires_in: 900 });

    expect(auth.isLoggedIn()).toBe(true);
    expect(auth.accessToken()).toBe('acc');
    expect(localStorage.getItem('taskboard.refresh_token')).toBe('ref');
  });

  it('stays logged out after a wrong password', () => {
    let failed = false;
    auth.login('priya@blueleaf.example', 'wrong').subscribe({ error: () => (failed = true) });

    http.expectOne('/v1/auth/login').flush({ error: 'wrong email or password' }, { status: 401, statusText: 'Unauthorized' });

    expect(failed).toBe(true);
    expect(auth.isLoggedIn()).toBe(false);
  });

  it('logs out: sends the refresh token, then forgets both tokens even if the API fails', () => {
    localStorage.setItem('taskboard.access_token', 'acc');
    localStorage.setItem('taskboard.refresh_token', 'ref');
    auth = TestBed.runInInjectionContext(() => new AuthService()); // a fresh one reads the stored token
    expect(auth.isLoggedIn()).toBe(true);

    auth.logout().subscribe();
    const req = http.expectOne('/v1/auth/logout');
    expect(req.request.body).toEqual({ refresh_token: 'ref' });
    req.flush(null, { status: 503, statusText: 'Service Unavailable' });

    expect(auth.isLoggedIn()).toBe(false);
    expect(localStorage.getItem('taskboard.access_token')).toBeNull();
  });
});
