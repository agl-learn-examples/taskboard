import { expect, test } from '@playwright/test';

// These tests start logged in as Priya (the saved login from auth.setup.ts).
// Every new task gets a title no other run has used, so running the tests again never finds an old task.
function uniqueTitle(name: string) {
  return `${name} ${Date.now()}`;
}

test('create a task, edit it and mark it done', async ({ page }) => {
  const title = uniqueTitle('Write the release notes');
  const newTitle = uniqueTitle('Write and send the release notes');

  // create
  await page.goto('/tasks');
  await page.getByTestId('new-task').click(); // the header has a "New task" link too: the test id picks this one
  await expect(page.getByRole('heading', { name: 'New task' })).toBeVisible();
  await page.getByLabel('Title').fill(title);
  await page.getByLabel('Priority').selectOption('high');
  await page.getByRole('button', { name: 'Save' }).click();

  // it is in the list
  await expect(page).toHaveURL('/tasks');
  const row = page.getByTestId('task-item').filter({ hasText: title });
  await expect(row).toBeVisible();
  await expect(row.getByTestId('task-priority')).toHaveText('high');

  // edit
  await row.getByRole('link', { name: `Edit ${title}` }).click();
  await expect(page.getByRole('heading', { name: 'Edit task' })).toBeVisible();
  await expect(page.getByLabel('Title')).toHaveValue(title); // wait for the task to load before changing it
  await page.getByLabel('Title').fill(newTitle);
  await page.getByRole('button', { name: 'Save' }).click();
  await expect(page).toHaveURL('/tasks');
  const editedRow = page.getByTestId('task-item').filter({ hasText: newTitle });
  await expect(editedRow).toBeVisible();

  // mark it done, then reload: the API kept it
  await editedRow.getByRole('checkbox', { name: `Done: ${newTitle}` }).check();
  await expect(editedRow).toHaveClass(/done/); // the row turns "done" only when the API has saved it
  await page.reload();
  await expect(page.getByRole('checkbox', { name: `Done: ${newTitle}` })).toBeChecked();
});

test('the form will not save a task without a title', async ({ page }) => {
  await page.goto('/tasks/new');
  await page.getByRole('button', { name: 'Save' }).click();

  await expect(page.getByText('The title is required.')).toBeVisible();
  await expect(page).toHaveURL('/tasks/new');
});
