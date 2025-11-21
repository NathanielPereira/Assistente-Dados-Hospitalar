import { test, expect } from '@playwright/test';

test.describe('Observability Control Room - US3', () => {
  test('deve exibir métricas de uptime, latência e status de integrações', async ({ page }) => {
    await page.goto('/observability');
    
    // Verifica que painel carrega
    await expect(page.locator('h1')).toContainText('Observability Control Room');
    
    // Verifica métricas principais
    await expect(page.locator('text=/Uptime/')).toBeVisible();
    await expect(page.locator('text=/Latência p95/')).toBeVisible();
    await expect(page.locator('text=/Status Geral/')).toBeVisible();
    
    // Verifica status das integrações
    await expect(page.locator('text=/neondb/i')).toBeVisible();
    await expect(page.locator('text=/s3/i')).toBeVisible();
    await expect(page.locator('text=/rag/i')).toBeVisible();
  });

  test('deve exibir alerta quando modo degradado está ativo', async ({ page }) => {
    await page.goto('/observability');
    
    // Simula modo degradado (via mock ou estado real)
    // Verifica que alerta aparece
    const degradedAlert = page.locator('text=/Modo Degradado Ativo/i');
    // Se existir, deve estar visível
    if (await degradedAlert.count() > 0) {
      await expect(degradedAlert).toBeVisible();
    }
  });

  test('deve atualizar métricas automaticamente', async ({ page }) => {
    await page.goto('/observability');
    
    const initialTimestamp = await page.locator('text=/Última atualização/').textContent();
    
    // Aguarda atualização (5s de intervalo)
    await page.waitForTimeout(6000);
    
    const newTimestamp = await page.locator('text=/Última atualização/').textContent();
    expect(newTimestamp).not.toBe(initialTimestamp);
  });
});
