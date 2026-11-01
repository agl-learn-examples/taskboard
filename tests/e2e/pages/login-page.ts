import { type Locator, type Page } from '@playwright/test';

// A page object: the login page's fields and buttons in one place, so a test reads like what a user does.
// If the page changes, only this file changes.
export class LoginPage {
  readonly email: Locator;
  readonly password: Locator;
  readonly submit: Locator;
  readonly error: Locator;

  constructor(private readonly page: Page) {
    this.email = page.getByLabel('Email');
    this.password = page.getByLabel('Password');
    this.submit = page.getByRole('button', { name: 'Log in' });
    this.error = page.getByTestId('login-error');
  }

  async goto() {
    await this.page.goto('/login');
  }

  async logIn(email: string, password: string) {
    await this.email.fill(email);
    await this.password.fill(password);
    await this.submit.click();
  }
}
