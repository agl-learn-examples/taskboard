import { Component, signal } from '@angular/core';
import { TestBed } from '@angular/core/testing';
import { provideRouter } from '@angular/router';
import { Task } from './task';
import { TaskItem } from './task-item';

// A tiny parent component that uses <li app-task-item>, the way the list page does.
@Component({
  imports: [TaskItem],
  template: `<ul><li app-task-item [task]="task()" (toggled)="clicked = $event"></li></ul>`,
})
class Host {
  task = signal<Task>({ id: 7, title: 'Write the A5 notes', done: false, priority: 'high', board_id: null });
  clicked: Task | null = null;
}

describe('TaskItem', () => {
  beforeEach(() => {
    TestBed.configureTestingModule({ imports: [Host], providers: [provideRouter([])] });
  });

  it('shows the title, the priority and an edit link', async () => {
    const fixture = TestBed.createComponent(Host);
    await fixture.whenStable();
    const li: HTMLElement = fixture.nativeElement.querySelector('[data-testid="task-item"]');

    expect(li.querySelector('[data-testid="task-title"]')?.textContent).toBe('Write the A5 notes');
    expect(li.querySelector('[data-testid="task-priority"]')?.textContent).toBe('high');
    expect(li.querySelector('a')?.getAttribute('href')).toBe('/tasks/7/edit');
    expect(li.classList).not.toContain('done');
  });

  it('crosses out a done task', async () => {
    const fixture = TestBed.createComponent(Host);
    fixture.componentInstance.task.update((t) => ({ ...t, done: true }));
    await fixture.whenStable();

    expect(fixture.nativeElement.querySelector('li').classList).toContain('done');
  });

  it('tells the parent when the checkbox is clicked', async () => {
    const fixture = TestBed.createComponent(Host);
    await fixture.whenStable();

    fixture.nativeElement.querySelector('input[type="checkbox"]').click();

    expect(fixture.componentInstance.clicked?.id).toBe(7);
  });
});
