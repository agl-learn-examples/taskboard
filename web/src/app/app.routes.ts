import { Routes } from '@angular/router';
import { authGuard } from './auth/auth.guard';
import { LoginPage } from './login/login-page';
import { TaskFormPage } from './tasks/task-form-page';
import { TaskListPage } from './tasks/task-list-page';

// Which component shows for which address. The browser never loads a new page: the router swaps components.
export const routes: Routes = [
  { path: 'login', component: LoginPage },
  { path: 'tasks', component: TaskListPage, canActivate: [authGuard] },
  { path: 'tasks/new', component: TaskFormPage, canActivate: [authGuard] },
  { path: 'tasks/:id/edit', component: TaskFormPage, canActivate: [authGuard] },
  { path: '', redirectTo: 'tasks', pathMatch: 'full' },
  { path: '**', redirectTo: 'tasks' },
];
