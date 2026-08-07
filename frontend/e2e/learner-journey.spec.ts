import { expect, test } from '@playwright/test';

/**
 * The critical learner flow, end to end against the real API and database:
 *
 *   register → open module → run activity → answer question → response saved
 *            → event saved → reload → state and progress restored
 */

const API = process.env.VITE_API_BASE_URL ?? 'http://127.0.0.1:8000';

function uniqueEmail(): string {
  return `e2e-${Date.now()}-${Math.floor(Math.random() * 10000)}@example.edu`;
}

const PASSWORD = 'correct-horse-battery-9';

test.describe('learner journey', () => {
  test('register, learn, answer, reload, and find everything restored', async ({ page }) => {
    const email = uniqueEmail();

    // ── Register ──────────────────────────────────────────────────────────
    await page.goto('/register');
    await page.getByLabel('Your name').fill('E2E Learner');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(PASSWORD);
    await page.getByRole('button', { name: 'Create account' }).click();

    await expect(page.getByRole('heading', { name: /made concrete/i })).toBeVisible();
    await expect(page.getByRole('link', { name: 'E2E Learner' })).toBeVisible();

    // ── Open a module, then its first page ────────────────────────────────
    // The module card links to the module overview; scope the page link to that overview so the
    // card's own summary text (which also names the page) cannot match first.
    await page.locator('a.module-card[href^="/modules/module-1"]').click();
    await expect(page.getByRole('heading', { name: 'Fundamentals', level: 1 })).toBeVisible();
    await page.locator('a[href="/modules/module-1/m1p1"]').click();
    await expect(page.getByRole('heading', { name: 'Demystifying AI', level: 1 })).toBeVisible();
    await expect(page.getByText(/0 of 5 activities done/)).toBeVisible();

    // ── Run an activity ───────────────────────────────────────────────────
    const sorter = page.locator('#m1p1-nesting');
    await expect(sorter.getByRole('heading', { name: /Sort the systems/ })).toBeVisible();
    // Answer all six by choosing the first option in each group, then check.
    const groups = sorter.locator('fieldset.panel');
    const groupCount = await groups.count();
    expect(groupCount).toBe(6);
    for (let i = 0; i < groupCount; i += 1) {
      await groups.nth(i).getByRole('radio').first().check();
    }
    await sorter.getByRole('button', { name: /Check my answers/ }).click();
    await expect(sorter.getByText(/of 6 correct/)).toBeVisible();

    // ── Answer a graded question ──────────────────────────────────────────
    const question = page.locator('#m1p1-q1');
    await question.getByRole('radio', { name: /written by people/i }).check();
    await question.getByRole('button', { name: /Check my answer/ }).click();
    await expect(question.getByText('✓ Correct').first()).toBeVisible();
    await expect(question.getByText(/origin of the rules/i)).toBeVisible();

    // Progress moved as a result of real persistence, not local state alone.
    await expect(page.getByText(/2 of 5 activities done/)).toBeVisible();

    // ── Verify persistence directly against the API ───────────────────────
    const responses = await page.evaluate(async (apiBase) => {
      // The access token is in memory only, so exercise the refresh-cookie path the app uses.
      const refresh = await fetch(`${apiBase}/api/v1/auth/refresh`, {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': document.cookie.match(/aip_csrf=([^;]+)/)?.[1] ?? '',
        },
      });
      const { access_token: token } = await refresh.json();
      const [responsesRes, progressRes] = await Promise.all([
        fetch(`${apiBase}/api/v1/responses/me?page_key=m1p1`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
        fetch(`${apiBase}/api/v1/progress/me`, {
          headers: { Authorization: `Bearer ${token}` },
        }),
      ]);
      return { responses: await responsesRes.json(), progress: await progressRes.json() };
    }, API);

    expect(responses.responses.length).toBeGreaterThanOrEqual(1);
    const saved = responses.responses.find(
      (r: { question_key: string }) => r.question_key === 'm1p1.q1',
    );
    expect(saved).toBeTruthy();
    expect(saved.is_correct).toBe(true);
    expect(saved.answer).toEqual({ value: 'no_rules' });
    expect(saved.attempt_no).toBe(1);

    const pageProgress = responses.progress.pages.find(
      (p: { page_key: string }) => p.page_key === 'm1p1',
    );
    expect(pageProgress).toBeTruthy();
    expect(pageProgress.sections_completed).toContain('m1p1-q1');
    expect(pageProgress.sections_completed).toContain('m1p1-nesting');

    // ── Reload: session survives and state is restored ─────────────────────
    await page.reload();
    await expect(page.getByRole('heading', { name: 'Demystifying AI', level: 1 })).toBeVisible();
    await expect(page.getByRole('link', { name: 'E2E Learner' })).toBeVisible();
    await expect(page.getByText(/2 of 5 activities done/)).toBeVisible();
    // The saved answer is pre-selected from the server, not from local storage.
    await expect(page.locator('#m1p1-q1').getByRole('radio', { name: /written by people/i })).toBeChecked();

    // ── Progress page reflects the same server state ───────────────────────
    await page.getByRole('link', { name: 'My progress' }).click();
    await expect(page.getByRole('heading', { name: 'My progress' })).toBeVisible();
    const row = page.getByRole('row').filter({ hasText: 'Demystifying AI' });
    await expect(row.getByText('In progress')).toBeVisible();
    await expect(row.getByText('2 / 5')).toBeVisible();

    // ── Sign out, sign back in, state still there ─────────────────────────
    await page.getByRole('button', { name: 'Sign out' }).click();
    await expect(page.getByRole('link', { name: 'Sign in' })).toBeVisible();

    await page.goto('/sign-in');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(PASSWORD);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(page.getByRole('link', { name: /Continue where you left off/ })).toBeVisible();
  });

  test('events reach the database for an authenticated learner', async ({ page }) => {
    const email = uniqueEmail();
    await page.goto('/register');
    await page.getByLabel('Your name').fill('Event Learner');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(PASSWORD);
    await page.getByRole('button', { name: 'Create account' }).click();
    await expect(page.getByRole('heading', { name: /made concrete/i })).toBeVisible();

    // Wait for the event batch flush that the app schedules.
    const eventRequest = page.waitForRequest(
      (request) => request.url().endsWith('/api/v1/events') && request.method() === 'POST',
      { timeout: 20_000 },
    );
    await page.goto('/modules/module-1/m1p1');
    await expect(page.getByRole('heading', { name: 'Demystifying AI', level: 1 })).toBeVisible();
    const request = await eventRequest;

    const body = request.postDataJSON() as {
      events: Array<{ event_type: string; page_key?: string }>;
      learning_session_id?: string;
    };
    expect(body.events.length).toBeGreaterThan(0);
    expect(body.events.some((event) => event.event_type === 'page_viewed')).toBe(true);
    expect(body.learning_session_id).toBeTruthy();
    // No client-supplied user id anywhere in the payload.
    expect(JSON.stringify(body)).not.toContain('user_id');

    const response = await request.response();
    expect(response?.status()).toBe(202);
  });

  test('embed mode hides global chrome but keeps the lesson usable', async ({ page }) => {
    const email = uniqueEmail();
    await page.goto('/register');
    await page.getByLabel('Your name').fill('Canvas Learner');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(PASSWORD);
    await page.getByRole('button', { name: 'Create account' }).click();
    await expect(page.getByRole('heading', { name: /made concrete/i })).toBeVisible();

    await page.goto('/modules/module-4/m4p2?embed=1');
    await expect(
      page.getByRole('heading', { name: 'Evaluating and Explaining', level: 1 }),
    ).toBeVisible();

    // Global nav and footer collapse; the learning content and identity remain.
    await expect(page.getByRole('navigation', { name: 'Main' })).toHaveCount(0);
    await expect(page.getByRole('button', { name: 'Sign out' })).toHaveCount(0);
    await expect(page.getByText('Canvas Learner')).toBeVisible();

    // The page fits a narrow Canvas frame without horizontal overflow.
    await page.setViewportSize({ width: 720, height: 900 });
    const overflows = await page.evaluate(
      () => document.documentElement.scrollWidth > document.documentElement.clientWidth + 1,
    );
    expect(overflows).toBe(false);
  });

  test('a question block is fully operable from the keyboard', async ({ page }) => {
    const email = uniqueEmail();
    await page.goto('/register');
    await page.getByLabel('Your name').fill('Keyboard Learner');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(PASSWORD);
    await page.getByRole('button', { name: 'Create account' }).click();
    // Wait for registration to land before navigating, otherwise the in-flight request is
    // cancelled and the learner arrives anonymous (so nothing would save).
    await expect(page.getByRole('heading', { name: /made concrete/i })).toBeVisible();

    await page.goto('/modules/module-1/m1p1');
    const question = page.locator('#m1p1-q1');
    await expect(question).toBeVisible();

    const firstRadio = question.getByRole('radio').first();
    await firstRadio.focus();
    await expect(firstRadio).toBeFocused();
    await page.keyboard.press('Space');
    await expect(firstRadio).toBeChecked();

    // The submit control must be reachable by Tab alone and activatable by Enter.
    const submit = question.getByRole('button', { name: /Check my answer/ });
    let reached = false;
    for (let i = 0; i < 8 && !reached; i += 1) {
      await page.keyboard.press('Tab');
      reached = await submit.evaluate((element) => element === document.activeElement);
    }
    expect(reached, 'submit button is reachable with Tab').toBe(true);
    await page.keyboard.press('Enter');
    await expect(question.getByText('✓ Correct').first()).toBeVisible();
  });
});
