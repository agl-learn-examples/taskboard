import { HttpClient } from '@angular/common/http';
import { Injectable, inject } from '@angular/core';
import { Observable } from 'rxjs';
import { Task, TaskInput, TaskPage } from './task';

// Every call to the tasks API in one place. The paths start with /v1: the gateway sends them on to the API.
// Components never build URLs themselves; they ask this service.
@Injectable({ providedIn: 'root' })
export class TaskService {
  private readonly http = inject(HttpClient);

  // shortcut: only the first 100 tasks, newest first; add paging when a team has more
  list(): Observable<TaskPage> {
    return this.http.get<TaskPage>('/v1/tasks', { params: { sort: '-created_at', per_page: 100 } });
  }

  get(id: number): Observable<Task> {
    return this.http.get<Task>(`/v1/tasks/${id}`);
  }

  create(task: TaskInput): Observable<Task> {
    return this.http.post<Task>('/v1/tasks', task);
  }

  // PATCH changes only the fields we send (PUT would reset the others, like board_id, to defaults)
  update(id: number, changes: Partial<TaskInput>): Observable<Task> {
    return this.http.patch<Task>(`/v1/tasks/${id}`, changes);
  }
}
