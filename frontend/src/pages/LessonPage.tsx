/**
 * A module page: the whole learner-facing experience for one of the two pages per module.
 *
 * Content comes from the typed content files. Progress, responses, and events go to the API.
 */

import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { progressApi, responseApi } from '@/api/endpoints';
import type { ResponseRecord } from '@/api/types';
import { getLearningSessionId, trackEvent } from '@/analytics/track';
import { useAuth } from '@/auth/AuthProvider';
import { AiActivity } from '@/activities/AiActivity';
import { getActivity } from '@/activities/registry';
import { Badge, Callout, Reveal } from '@/components/primitives';
import { Prose } from '@/components/Prose';
import { QuestionBlock } from '@/components/QuestionBlock';
import { Spinner } from '@/components/Spinner';
import { findPage, moduleByKey, nextModule, siblingPage } from '@/content';
import type { Section } from '@/content/types';
import { withEmbed } from '@/lib/embed';

const TIME_TICK_MS = 30_000;

export default function LessonPage() {
  const { moduleKey = '', pageKey = '' } = useParams();
  const { status } = useAuth();
  const authenticated = status === 'authenticated';
  const queryClient = useQueryClient();

  const module = moduleByKey.get(moduleKey);
  const page = findPage(moduleKey, pageKey);

  const [completedSections, setCompletedSections] = useState<Set<string>>(new Set());
  const [activeSection, setActiveSection] = useState<string | null>(null);
  const activeTime = useRef(0);
  const registered = useRef(false);

  const responsesQuery = useQuery({
    queryKey: ['responses', pageKey],
    queryFn: () => responseApi.mine({ page_key: pageKey }),
    enabled: authenticated && Boolean(page),
    staleTime: 30 * 1000,
  });

  const progressMutation = useMutation({
    mutationFn: (input: Parameters<typeof progressApi.update>[1]) =>
      progressApi.update(pageKey, input),
    onSuccess: (row) => {
      setCompletedSections(new Set(row.sections_completed));
      void queryClient.invalidateQueries({ queryKey: ['progress'] });
    },
  });

  const savedByQuestion = useMemo(() => {
    const map = new Map<string, ResponseRecord>();
    for (const record of responsesQuery.data ?? []) map.set(record.question_key, record);
    return map;
  }, [responsesQuery.data]);

  // Register the visit once, then send bounded active-time deltas.
  useEffect(() => {
    if (!authenticated || !page || registered.current) return;
    registered.current = true;
    trackEvent('page_viewed', { moduleKey, pageKey }, { title: page.title });
    trackEvent('module_opened', { moduleKey });
    progressMutation.mutate({
      register_visit: true,
      status: 'in_progress',
      learning_session_id: getLearningSessionId() ?? undefined,
    });
    // progressMutation is stable enough for a once-per-mount effect.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authenticated, moduleKey, page, pageKey]);

  useEffect(() => {
    if (!authenticated) return;
    const tick = window.setInterval(() => {
      if (document.visibilityState !== 'visible') return;
      activeTime.current += TIME_TICK_MS / 1000;
      if (activeTime.current >= 30) {
        const delta = Math.min(120, Math.round(activeTime.current));
        activeTime.current = 0;
        progressMutation.mutate({
          seconds_delta: delta,
          learning_session_id: getLearningSessionId() ?? undefined,
        });
      }
    }, TIME_TICK_MS);
    return () => window.clearInterval(tick);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authenticated, pageKey]);

  // Section rail highlight.
  useEffect(() => {
    if (!page) return;
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries
          .filter((entry) => entry.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
        if (visible?.target.id) setActiveSection(visible.target.id);
      },
      { rootMargin: '-20% 0px -70% 0px' },
    );
    for (const section of page.sections) {
      const element = document.getElementById(section.id);
      if (element) observer.observe(element);
    }
    return () => observer.disconnect();
  }, [page]);

  const completeSection = useCallback(
    (sectionId: string) => {
      setCompletedSections((prev) => {
        if (prev.has(sectionId)) return prev;
        const next = new Set(prev);
        next.add(sectionId);
        return next;
      });
      trackEvent('page_section_completed', { moduleKey, pageKey, sectionId });
      if (authenticated) {
        progressMutation.mutate({
          section_completed: sectionId,
          last_section_id: sectionId,
          learning_session_id: getLearningSessionId() ?? undefined,
        });
      }
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [authenticated, moduleKey, pageKey],
  );

  if (!module || !page) {
    return (
      <div className="content-width page">
        <h1 className="page__title">Page not found</h1>
        <p className="page__lede">
          That module page does not exist. <Link to={withEmbed('/')}>Back to the modules</Link>.
        </p>
      </div>
    );
  }

  const required = page.requiredSections;
  const doneCount = required.filter((id) => completedSections.has(id)).length;
  const pageComplete = doneCount === required.length && required.length > 0;

  const sibling = siblingPage(moduleKey, pageKey);
  const followingModule = nextModule(moduleKey);

  return (
    <div className="content-width page">
      <div className="page__header">
        <p className="kicker">{page.kicker}</p>
        <h1 className="page__title">{page.title}</h1>
        <p className="page__lede">{page.lede}</p>

        <div
          style={{
            display: 'flex',
            gap: 'var(--sp-3)',
            alignItems: 'center',
            marginTop: 'var(--sp-5)',
            flexWrap: 'wrap',
          }}
        >
          <Badge>{page.estimatedMinutes} min</Badge>
          <Badge tone={pageComplete ? 'success' : 'accent'}>
            {doneCount} of {required.length} activities done
          </Badge>
          <div className="meter" style={{ flex: '1 1 8rem', minWidth: '8rem', maxWidth: '18rem' }}>
            <div
              className="meter__fill"
              style={{ width: `${required.length ? (doneCount / required.length) * 100 : 0}%` }}
              role="progressbar"
              aria-valuenow={doneCount}
              aria-valuemin={0}
              aria-valuemax={required.length}
              aria-label="Page progress"
            />
          </div>
        </div>

        {page.objectives.length > 0 ? (
          <div style={{ marginTop: 'var(--sp-5)', maxWidth: '56rem' }}>
            <Reveal label="What you will be able to do after this page" eventContext={{ moduleKey, pageKey }}>
              <ul>
                {page.objectives.map((objective) => (
                  <li key={objective}>{objective}</li>
                ))}
              </ul>
            </Reveal>
          </div>
        ) : null}

        {!authenticated ? (
          <div style={{ marginTop: 'var(--sp-5)' }}>
            <Callout tone="warning" title="You are not signed in">
              <p>
                You can read and use every activity, but nothing will be saved.{' '}
                <Link to="/sign-in">Sign in</Link> or <Link to="/register">create an account</Link> to
                keep your work.
              </p>
            </Callout>
          </div>
        ) : null}
      </div>

      <div className="lesson">
        <div className="lesson__sections">
          {page.sections.map((section) => (
            <section className="section" id={section.id} key={section.id}>
              <SectionView
                section={section}
                moduleKey={moduleKey}
                pageKey={pageKey}
                savedByQuestion={savedByQuestion}
                completed={completedSections.has(section.id)}
                onComplete={() => completeSection(section.id)}
              />
            </section>
          ))}

          {pageComplete ? (
            <Callout tone="success" title="Page complete">
              <p>
                Every activity on this page is done and your responses are saved. You can revisit and
                change any answer — earlier attempts are kept.
              </p>
            </Callout>
          ) : null}

          <nav className="pager" aria-label="Course navigation">
            <Link className="btn btn--outline" to={withEmbed(`/modules/${moduleKey}`)}>
              ← {module.title} overview
            </Link>
            {sibling ? (
              <Link className="btn btn--primary" to={withEmbed(`/modules/${moduleKey}/${sibling.key}`)}>
                {sibling.position === 1 ? '←' : ''} {sibling.title} {sibling.position === 2 ? '→' : ''}
              </Link>
            ) : null}
            {page.position === 2 && followingModule ? (
              <Link
                className="btn btn--primary"
                to={withEmbed(`/modules/${followingModule.key}/${followingModule.pages[0].key}`)}
              >
                Module {followingModule.position}: {followingModule.title} →
              </Link>
            ) : null}
          </nav>
        </div>

        <aside className="lesson__rail" aria-label="On this page">
          <p className="rail__title">On this page</p>
          <ul className="rail__list">
            {page.sections
              .filter((section) => section.kind !== 'reveal')
              .map((section) => {
                const label = sectionLabel(section);
                if (!label) return null;
                return (
                  <li key={section.id}>
                    <a
                      className={`rail__link${activeSection === section.id ? ' rail__link--active' : ''}`}
                      href={`#${section.id}`}
                    >
                      <span>{label}</span>
                      {completedSections.has(section.id) ? (
                        <span className="rail__check" aria-label="completed">
                          ✓
                        </span>
                      ) : null}
                    </a>
                  </li>
                );
              })}
          </ul>
        </aside>
      </div>
    </div>
  );
}

function sectionLabel(section: Section): string | null {
  switch (section.kind) {
    case 'prose':
      return section.heading ?? null;
    case 'callout':
      return section.heading;
    case 'question':
      return section.heading ?? 'Question';
    case 'activity':
    case 'aiActivity':
      return section.heading;
    default:
      return null;
  }
}

function SectionView({
  section,
  moduleKey,
  pageKey,
  savedByQuestion,
  completed,
  onComplete,
}: {
  section: Section;
  moduleKey: string;
  pageKey: string;
  savedByQuestion: Map<string, ResponseRecord>;
  completed: boolean;
  onComplete: () => void;
}) {
  switch (section.kind) {
    case 'prose':
      return (
        <>
          {section.heading ? <h2 className="section__heading">{section.heading}</h2> : null}
          <Prose body={section.body} className="section__body" />
        </>
      );

    case 'callout':
      return (
        <Callout tone={section.tone} title={section.heading}>
          <Prose body={section.body} />
        </Callout>
      );

    case 'reveal':
      return (
        <Reveal label={section.label} eventContext={{ moduleKey, pageKey, sectionId: section.id }}>
          <Prose body={section.body} />
        </Reveal>
      );

    case 'question':
      return (
        <QuestionBlock
          question={section.question}
          moduleKey={moduleKey}
          pageKey={pageKey}
          sectionId={section.id}
          heading={section.heading}
          intro={section.intro}
          saved={savedByQuestion.get(section.question.key)}
          onAnswered={onComplete}
        />
      );

    case 'activity': {
      const Component = getActivity(section.activity);
      if (!Component) {
        return (
          <Callout tone="warning" title={section.heading}>
            <p>This activity is not available.</p>
          </Callout>
        );
      }
      return (
        <>
          <h2 className="section__heading">{section.heading}</h2>
          {section.intro ? (
            <p className="section__body" style={{ marginBottom: 'var(--sp-4)' }}>
              {section.intro}
            </p>
          ) : null}
          <Suspense fallback={<div className="placeholder"><Spinner label="Loading activity" /></div>}>
            <Component
              activityKey={section.activity}
              moduleKey={moduleKey}
              pageKey={pageKey}
              sectionId={section.id}
              completed={completed}
              onComplete={onComplete}
            />
          </Suspense>
        </>
      );
    }

    case 'aiActivity':
      return (
        <>
          <h2 className="section__heading">{section.heading}</h2>
          <AiActivity
            promptKey={section.promptKey}
            heading={section.heading}
            intro={section.intro}
            inputLabel={section.inputLabel}
            placeholder={section.placeholder}
            submitLabel={section.submitLabel}
            render={section.render}
            moduleKey={moduleKey}
            pageKey={pageKey}
            sectionId={section.id}
            completed={completed}
            onComplete={onComplete}
          />
        </>
      );

    default:
      return null;
  }
}
