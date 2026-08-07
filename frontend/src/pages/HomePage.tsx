import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { moduleApi, progressApi } from '@/api/endpoints';
import { useAuth } from '@/auth/AuthProvider';
import { modules } from '@/content';
import { withEmbed } from '@/lib/embed';
import { Badge } from '@/components/primitives';

const ACCENT_VAR: Record<string, string> = {
  blue: 'var(--accent-blue)',
  teal: 'var(--accent-teal)',
  violet: 'var(--accent-violet)',
  amber: 'var(--accent-amber)',
  rose: 'var(--accent-rose)',
  green: 'var(--accent-green)',
  slate: 'var(--accent-slate)',
};

export default function HomePage() {
  const { status } = useAuth();
  const authenticated = status === 'authenticated';

  // The API is the source of truth for progress; content copy comes from the bundle.
  const modulesQuery = useQuery({
    queryKey: ['modules'],
    queryFn: moduleApi.list,
    staleTime: 5 * 60 * 1000,
  });
  const progressQuery = useQuery({
    queryKey: ['progress'],
    queryFn: progressApi.overview,
    enabled: authenticated,
    staleTime: 60 * 1000,
  });

  const completedPages = new Set(
    (progressQuery.data?.pages ?? [])
      .filter((row) => row.status === 'completed')
      .map((row) => row.page_key),
  );
  const resume = progressQuery.data?.resume;

  return (
    <>
      <section className="hero">
        <div className="content-width">
          <p className="kicker">University of Florida · AIPassport</p>
          <h1 className="hero__title">Artificial intelligence, made concrete.</h1>
          <p className="hero__body">
            Seven modules, two focused pages each. You will read short explanations and then do the
            thing — move the threshold, break the model, audit the dataset — because that is what makes
            it stick.
          </p>
          <div className="hero__actions">
            {authenticated ? (
              resume ? (
                <Link
                  className="btn btn--primary btn--lg"
                  to={withEmbed(`/modules/${resume.module_key}/${resume.page_key}`)}
                >
                  Continue where you left off
                </Link>
              ) : (
                <Link className="btn btn--primary btn--lg" to={withEmbed('/modules/module-1/m1p1')}>
                  Start Module 1
                </Link>
              )
            ) : (
              <>
                <Link className="btn btn--primary btn--lg" to="/register">
                  Create an account
                </Link>
                <Link className="btn btn--outline btn--lg" to="/sign-in">
                  Sign in
                </Link>
              </>
            )}
          </div>
          {!authenticated ? (
            <p style={{ marginTop: 'var(--sp-4)', fontSize: 'var(--text-sm)', color: 'var(--text-faint)' }}>
              An account lets your answers, progress, and activity results save as you go.
            </p>
          ) : null}
        </div>
      </section>

      <div className="content-width page">
        <div className="page__header">
          <h2 style={{ fontSize: 'var(--text-2xl)' }}>Modules</h2>
          <p className="page__lede" style={{ marginTop: 'var(--sp-2)' }}>
            Each module has exactly two pages: one to build the concept, one to apply it.
          </p>
        </div>

        {modulesQuery.isError ? (
          <div className="callout callout--warning" role="alert">
            <p className="callout__title">Could not load module progress</p>
            <p>
              The course content below is available, but the server did not respond. Your progress may
              not be up to date.
            </p>
          </div>
        ) : null}

        <div className="module-grid">
          {modules.map((module) => {
            const done = module.pages.filter((page) => completedPages.has(page.key)).length;
            return (
              <Link
                key={module.key}
                className="module-card"
                to={withEmbed(`/modules/${module.key}`)}
                style={{ ['--module-accent' as string]: ACCENT_VAR[module.accent] ?? 'var(--accent)' }}
              >
                <div className="module-card__top">
                  <span className="module-card__number">Module {module.position}</span>
                  {authenticated ? (
                    done === module.pages.length ? (
                      <Badge tone="success">Complete</Badge>
                    ) : done > 0 ? (
                      <Badge tone="accent">{done} of 2</Badge>
                    ) : null
                  ) : null}
                </div>
                <h3 className="module-card__title">{module.title}</h3>
                <p className="module-card__summary">{module.summary}</p>
                <div className="module-card__pages">
                  {module.pages.map((page) => (
                    <span className="module-card__page" key={page.key}>
                      <span aria-hidden="true">
                        {completedPages.has(page.key) ? '✓' : '·'}
                      </span>
                      {page.title}
                      <span style={{ color: 'var(--text-faint)' }}>· {page.estimatedMinutes} min</span>
                    </span>
                  ))}
                </div>
              </Link>
            );
          })}
        </div>

        {!authenticated ? (
          <div className="card" style={{ marginTop: 'var(--sp-8)', maxWidth: '46rem' }}>
            <h3 style={{ fontSize: 'var(--text-lg)', marginBottom: 'var(--sp-2)' }}>
              You can read without an account
            </h3>
            <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)' }}>
              Browsing the modules is open. Signing in is what lets your answers, activity results, and
              progress persist — and lets an instructor see that you completed the work.
            </p>
            <div style={{ marginTop: 'var(--sp-4)' }}>
              <Link className="btn btn--primary" to="/register">
                Create an account
              </Link>
            </div>
          </div>
        ) : null}
      </div>
    </>
  );
}
