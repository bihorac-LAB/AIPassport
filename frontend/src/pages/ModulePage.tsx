import { Link, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { progressApi } from '@/api/endpoints';
import { useAuth } from '@/auth/AuthProvider';
import { moduleByKey } from '@/content';
import { withEmbed } from '@/lib/embed';
import { Badge, Callout } from '@/components/primitives';

export default function ModulePage() {
  const { moduleKey = '' } = useParams();
  const { status } = useAuth();
  const module = moduleByKey.get(moduleKey);

  const progressQuery = useQuery({
    queryKey: ['progress'],
    queryFn: progressApi.overview,
    enabled: status === 'authenticated',
    staleTime: 60 * 1000,
  });

  if (!module) {
    return (
      <div className="content-width page">
        <h1 className="page__title">Module not found</h1>
        <p className="page__lede">
          <Link to={withEmbed('/')}>Back to the modules</Link>
        </p>
      </div>
    );
  }

  const progressByPage = new Map(
    (progressQuery.data?.pages ?? []).map((row) => [row.page_key, row]),
  );

  return (
    <div className="content-width page">
      <div className="page__header">
        <p className="kicker">Module {module.position}</p>
        <h1 className="page__title">{module.title}</h1>
        <p className="page__lede">{module.summary}</p>
      </div>

      <div style={{ display: 'grid', gap: 'var(--sp-4)', maxWidth: '52rem' }}>
        {module.pages.map((page) => {
          const progress = progressByPage.get(page.key);
          const done = progress?.status === 'completed';
          return (
            <Link
              key={page.key}
              className="card card--interactive"
              to={withEmbed(`/modules/${module.key}/${page.key}`)}
              style={{ textDecoration: 'none', color: 'inherit', display: 'block' }}
            >
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'baseline',
                  gap: 'var(--sp-3)',
                  flexWrap: 'wrap',
                }}
              >
                <div>
                  <p className="kicker">
                    Page {page.position} · {page.kind === 'explore' ? 'Learn' : 'Apply'}
                  </p>
                  <h2 style={{ fontSize: 'var(--text-xl)', margin: 'var(--sp-2) 0' }}>{page.title}</h2>
                </div>
                <div style={{ display: 'flex', gap: 'var(--sp-2)' }}>
                  <Badge>{page.estimatedMinutes} min</Badge>
                  {done ? <Badge tone="success">Complete</Badge> : null}
                  {!done && progress ? (
                    <Badge tone="accent">
                      {progress.sections_completed.length} of {page.requiredSections.length}
                    </Badge>
                  ) : null}
                </div>
              </div>

              <p style={{ color: 'var(--text-muted)', fontSize: 'var(--text-sm)', maxWidth: '60ch' }}>
                {page.lede}
              </p>

              <ul
                style={{
                  marginTop: 'var(--sp-4)',
                  fontSize: 'var(--text-sm)',
                  color: 'var(--text-muted)',
                }}
              >
                {page.objectives.slice(0, 3).map((objective) => (
                  <li key={objective}>{objective}</li>
                ))}
              </ul>
            </Link>
          );
        })}
      </div>

      <div style={{ marginTop: 'var(--sp-8)', maxWidth: '52rem' }}>
        <Callout tone="neutral" title="Two pages, by design">
          <p>
            This module is deliberately two experiences rather than a long sequence of short lessons.
            Page 1 builds the concept with visual and interactive explanation; page 2 puts you in the
            practitioner's seat with the same ideas.
          </p>
        </Callout>
      </div>
    </div>
  );
}
