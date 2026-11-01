import { test as setup } from '@playwright/test';
import { LoginPage } from './pages/login-page';

// Runs once before the tests: logs in as Priya and saves what the browser keeps (the tokens in
// localStorage). Every test in the chromium project starts with this saved state, already logged in.
setup('log in as Priya', async ({ page }) => {
  const loginPage = new LoginPage(page);
  await loginPage.goto();
  await loginPage.logIn('priya@blueleaf.example', 'demo-password-123');
  await page.waitForURL('/tasks');
  await page.context().storageState({ path: 'playwright/.auth/priya.json' });
});
