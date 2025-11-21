import { test, expect } from '@playwright/test';

test.describe('Chat Streaming - US1', () => {
  test('deve streamar resposta e exibir SQL executado', async ({ page }) => {
    await page.goto('/chat');
    await page.fill('[data-testid="chat-input"]', 'Qual taxa de ocupação da UTI pediátrica?');
    await page.click('[data-testid="send-button"]');
    
    // Verifica streaming
    await expect(page.locator('[data-testid="streaming-response"]')).toBeVisible({ timeout: 2000 });
    
    // Verifica SQL exibido
    await expect(page.locator('[data-testid="sql-executed"]')).toContainText('SELECT', { timeout: 8000 });
    
    // Verifica citações de documentos
    await expect(page.locator('[data-testid="document-citations"]')).toBeVisible();
  });
});
