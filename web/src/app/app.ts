import { Component, inject } from '@angular/core';
import { Router, RouterLink, RouterOutlet } from '@angular/router';
import { AuthService } from './auth/auth.service';

// The shell: a header that is always there, and <router-outlet> where the current page goes.
@Component({
  selector: 'app-root',
  imports: [RouterOutlet, RouterLink],
  templateUrl: './app.html',
})
export class App {
  protected readonly auth = inject(AuthService);
  private readonly router = inject(Router);

  logout() {
    this.auth.logout().subscribe(() => this.router.navigate(['/login']));
  }
}
