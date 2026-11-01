import { Component, input, output } from '@angular/core';
import { RouterLink } from '@angular/router';
import { Task } from './task';

// One row of the list, used as <li app-task-item [task]="...">. It gets its task from the parent
// (input) and tells the parent when the checkbox is clicked (output); it never calls the API itself.
@Component({
  selector: 'li[app-task-item]',
  imports: [RouterLink],
  templateUrl: './task-item.html',
  host: { class: 'task', '[class.done]': 'task().done', 'data-testid': 'task-item' },
})
export class TaskItem {
  readonly task = input.required<Task>();
  readonly toggled = output<Task>();
}
