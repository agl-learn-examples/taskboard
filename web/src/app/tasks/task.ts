// One task, as the API sends it (GET /v1/tasks/<id>)
export type Priority = 'low' | 'normal' | 'high';

export interface Task {
  id: number;
  title: string;
  done: boolean;
  priority: Priority;
  board_id: number | null;
}

// One page of tasks (GET /v1/tasks)
export interface TaskPage {
  items: Task[];
  page: number;
  per_page: number;
  total: number;
}

// What we send to create or change a task
export interface TaskInput {
  title: string;
  priority: Priority;
  done?: boolean;
}
