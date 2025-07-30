/**
 * End-to-End Authentication Tests
 * Tests complete user authentication workflows
 */

import { test, expect } from '@playwright/test';

const BASE_URL = process.env.BASE_URL || 'http://localhost:3000';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto(BASE_URL);
  });

  test('should display login page', async ({ page }) => {
    await page.click('text=Sign In');
    
    await expect(page).toHaveURL(`${BASE_URL}/login`);
    await expect(page.locator('h1')).toContainText('Sign In');
    await expect(page.locator('input[type="email"]')).toBeVisible();
    await expect(page.locator('input[type="password"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toContainText('Sign In');
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.click('text=Sign In');
    
    // Fill in login form
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Should redirect to dashboard
    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
    await expect(page.locator('h1')).toContainText('Dashboard');
    
    // Should show user menu
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.click('text=Sign In');
    
    // Fill in invalid credentials
    await page.fill('input[type="email"]', 'invalid@example.com');
    await page.fill('input[type="password"]', 'wrongpassword');
    await page.click('button[type="submit"]');
    
    // Should show error message
    await expect(page.locator('[data-testid="error-message"]')).toContainText('Invalid credentials');
    
    // Should stay on login page
    await expect(page).toHaveURL(`${BASE_URL}/login`);
  });

  test('should logout successfully', async ({ page }) => {
    // Login first
    await page.click('text=Sign In');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Wait for dashboard
    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
    
    // Logout
    await page.click('[data-testid="user-menu"]');
    await page.click('text=Sign Out');
    
    // Should redirect to home page
    await expect(page).toHaveURL(BASE_URL);
    await expect(page.locator('text=Sign In')).toBeVisible();
  });

  test('should register new user', async ({ page }) => {
    await page.click('text=Sign Up');
    
    await expect(page).toHaveURL(`${BASE_URL}/signup`);
    
    // Fill in registration form
    await page.fill('input[name="firstName"]', 'John');
    await page.fill('input[name="lastName"]', 'Doe');
    await page.fill('input[name="email"]', 'john.doe@example.com');
    await page.fill('input[name="password"]', 'password123');
    await page.fill('input[name="confirmPassword"]', 'password123');
    await page.click('button[type="submit"]');
    
    // Should show success message
    await expect(page.locator('[data-testid="success-message"]')).toContainText('Registration successful');
    
    // Should redirect to verification page
    await expect(page).toHaveURL(`${BASE_URL}/verify-email`);
  });

  test('should protect routes when not authenticated', async ({ page }) => {
    // Try to access protected route
    await page.goto(`${BASE_URL}/dashboard`);
    
    // Should redirect to login
    await expect(page).toHaveURL(`${BASE_URL}/login`);
  });

  test('should persist authentication across page refreshes', async ({ page }) => {
    // Login
    await page.click('text=Sign In');
    await page.fill('input[type="email"]', 'test@example.com');
    await page.fill('input[type="password"]', 'password123');
    await page.click('button[type="submit"]');
    
    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
    
    // Refresh page
    await page.reload();
    
    // Should still be authenticated
    await expect(page).toHaveURL(`${BASE_URL}/dashboard`);
    await expect(page.locator('[data-testid="user-menu"]')).toBeVisible();
  });
});