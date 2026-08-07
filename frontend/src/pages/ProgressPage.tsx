import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { progressApi } from '@/api/endpoints';
import { modules } from '@/content';
import { withEmbed } from '@/lib/embed';
import { Badge, Metric } from '@/components/primitives';
import { Spinner } from '@/components/Spinner';

function formatMinutes(seconds: number): string {
  const minutes = Math.round(seconds / 60);
  if (minutes < 60) return `${minutes} min`;
  return `${Math.floor(minutes / 60)}h ${minutes % 60}m`;
}

export default function ProgressPage() {
  const query = useQuery({ queryKey: ['progress'], queryFn: progressApi.overview });

  if (query.isLoading) {
    return (
      <div className="content-width page">
        <Spinner label="Loading your progress" />
      </div>
    );
  }

  const rows = new Map((query.data?.pages ?? []).map((row) => [row.page_key, row]));
  const completedPages = (query.data?.pages ?? []).filter((row) => row.status === 'completed').length;
  const totalPages = modules.reduce((sum, module) => sum + module.pages.length, 0);
  const resume = query.data?.resume;

  return (
    <div className="content-width page">
      <div className="page__header">
        <h1 className="page__title">My progress</h1>
        <p className="page__lede">
          Everything here is saved on the server, so it follows you between devices.
        </p>
      </div>

      <div className="metric-row" style={{ maxWidth: '48rem', marginBottom: 'var(--sp-8)' }}>
        <Metric label="Pages completed" value={`${completedPages} / ${totalPages}`} />
        <Metric
          label="Modules completed"
          value={`${query.data?.modules_completed.length ?? 0} / ${modules.length}`}
        />
        <Metric label="Time on task" value={formatMinutes(query.data?.total_seconds ?? 0)} />
      </div>

      {resume ? (
        <p style={{ marginBottom: 'var(--sp-6)' }}>
          <Link
            className="btn btn--primary"
            to={withEmbed(`/modules/${resume.module_key}/${resume.page_key}`)}
          >
            Continue where you left off
          </Link>
        </p>
      ) : null}

      <div className="table-wrap">
        <table className="data-table">
          <caption className="sr-only">Progress by page</caption>
          <thead>
            <tr>
              <th scope="col">Module</th>
              <th scope="col">Page</th>
              <th scope="col">Status</th>
              <th scope="col" className="num">
                Activities
              </th>
              <th scope="col" className="num">
                Time
              </th>
              <th scope="col" className="num">
                Visits
              </th>
            </tr>
          </thead>
          <tbody>
            {modules.flatMap((module) =>
              module.pages.map((page) => {
                const row = rows.get(page.key);
                return (
                  <tr key={page.key}>
                    <td>{module.title}</td>
                    <td>
                      <Link to={withEmbed(`/modules/${module.key}/${page.key}`)}>{page.title}</Link>
                    </td>
                    <td>
                      {row?.status === 'completed' ? (
                        <Badge tone="success">Complete</Badge>
                      ) : row ? (
                        <Badge tone="accent">In progress</Badge>
                      ) : (
                        <Badge>Not started</Badge>
                      )}
                    </td>
                    <td className="num">
                      {row?.sections_completed.length ?? 0} / {page.requiredSections.length}
                    </td>
                    <td className="num">{formatMinutes(row?.seconds_spent ?? 0)}</td>
                    <td className="num">{row?.visit_count ?? 0}</td>
                  </tr>
                );
              }),
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
