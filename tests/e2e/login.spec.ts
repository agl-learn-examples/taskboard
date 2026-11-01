import { expect, test } from '@playwright/test';
import { LoginPage } from './pages/login-page';

// These tests need a logged-OUT browser, so they start with empty storage instead of the saved login.
// Only two of them really log in: the login limit is 10 a minute per address.
test.use({ storageState: { cookies: [], origins: [] } });

test('Priya logs in and sees the task list, then logs out', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.logIn('priya@blueleaf.example', 'demo-password-123');

  await expect(page).toHaveURL('/tasks');
  await expect(page.getByRole('heading', { name: 'Tasks' })).toBeVisible();
  await expect(page.getByTestId('task-item').first()).toBeVisible();

  // Log out here, not in a test that uses the saved login: logging out ends that session on the server.
  await page.getByRole('button', { name: 'Log out' }).click();
  await expect(page).toHaveURL('/login');
  await expect(page.getByRole('heading', { name: 'Log in' })).toBeVisible();
});

test('a wrong password shows an error', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.logIn('priya@blueleaf.example', 'not-the-password');

  await expect(loginPage.error).toHaveText('wrong email or password');
  await expect(page).toHaveURL('/login');
});

test('the guard sends /tasks to /login when logged out', async ({ page }) => {
  await page.goto('/tasks');
  await expect(page).toHaveURL('/login');
});
