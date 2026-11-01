import { Component, OnInit, inject, input, numberAttribute, signal } from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { Priority } from './task';
import { TaskService } from './task.service';

// /tasks/new and /tasks/:id/edit share this form. With an id, it loads the task and saves changes;
// without one, it creates a task.
@Component({
  selector: 'app-task-form-page',
  imports: [ReactiveFormsModule, RouterLink],
  templateUrl: './task-form-page.html',
})
export class TaskFormPage implements OnInit {
  private readonly tasks = inject(TaskService);
  private readonly router = inject(Router);

  // the :id from the address (withComponentInputBinding in app.config.ts); undefined on /tasks/new
  readonly id = input(undefined, { transform: numberAttribute });

  readonly priorities: Priority[] = ['low', 'normal', 'high'];
  readonly error = signal('');
  readonly saving = signal(false);

  // The same rules as the API's TaskIn: a title of 1 to 200 characters (spaces alone do not count),
  // and a priority of low, normal or high. The API checks again: the browser is not to be trusted.
  readonly form = inject(FormBuilder).nonNullable.group({
    title: ['', [Validators.required, Validators.maxLength(200), Validators.pattern(/\S/)]],
    priority: ['normal' as Priority, Validators.required],
    done: [false],
  });

  ngOnInit() {
    const id = this.id();
    if (id) {
      this.tasks.get(id).subscribe({
        next: (task) => this.form.setValue({ title: task.title, priority: task.priority, done: task.done }),
        error: () => this.error.set('No such task.'),
      });
    }
  }

  save() {
    if (this.form.invalid) {
      this.form.markAllAsTouched(); // show every field's message
      return;
    }
    this.saving.set(true);
    const value = this.form.getRawValue();
    const id = this.id();
    const request = id ? this.tasks.update(id, value) : this.tasks.create(value);
    request.subscribe({
      next: () => this.router.navigate(['/tasks']),
      error: (err: HttpErrorResponse) => {
        // the API's error: {"error": "invalid input", "details": [{"field": "title", "message": "..."}]}
        const details = err.error?.details?.map((d: { field: string; message: string }) => `${d.field}: ${d.message}`);
        this.error.set(details?.join(', ') || err.error?.error || 'Could not save the task.');
        this.saving.set(false);
      },
    });
  }
}
