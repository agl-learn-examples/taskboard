import { Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Task } from './task';
import { TaskItem } from './task-item';
import { TaskService } from './task.service';

// The /tasks page: loads the team's tasks and shows one task item per task.
@Component({
  selector: 'app-task-list-page',
  imports: [TaskItem, RouterLink],
  templateUrl: './task-list-page.html',
})
export class TaskListPage {
  private readonly tasks = inject(TaskService);

  readonly items = signal<Task[]>([]);
  readonly total = signal(0);
  readonly loading = signal(true);
  readonly error = signal('');

  constructor() {
    this.tasks.list().subscribe({
      next: (page) => {
        this.items.set(page.items);
        this.total.set(page.total);
        this.loading.set(false);
      },
      error: () => {
        this.error.set('Could not load the tasks. Is the API running?');
        this.loading.set(false);
      },
    });
  }

  toggle(task: Task) {
    this.tasks.update(task.id, { done: !task.done }).subscribe({
      next: (saved) => this.items.update((list) => list.map((t) => (t.id === saved.id ? saved : t))),
      error: (err) => this.error.set(err.error?.error ?? 'Could not save the task.'),
    });
  }
}
