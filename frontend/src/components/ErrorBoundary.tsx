import { Component, type ErrorInfo, type ReactNode } from 'react';

/** Learners see a friendly recovery path, never a stack trace. */
export class ErrorBoundary extends Component<{ children: ReactNode }, { failed: boolean }> {
  constructor(props: { children: ReactNode }) {
    super(props);
    this.state = { failed: false };
  }

  static getDerivedStateFromError(): { failed: boolean } {
    return { failed: true };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    // Kept in the console for developers; not surfaced to the learner.
    console.error('Unhandled UI error', error, info.componentStack);
  }

  render(): ReactNode {
    if (!this.state.failed) return this.props.children;
    return (
      <div className="content-width page">
        <h1 className="page__title">Something went wrong on this page</h1>
        <p className="page__lede">
          Your saved answers are safe on the server. Reloading usually fixes this.
        </p>
        <div style={{ marginTop: 'var(--sp-5)', display: 'flex', gap: 'var(--sp-3)' }}>
          <button type="button" className="btn btn--primary" onClick={() => window.location.reload()}>
            Reload the page
          </button>
          <a className="btn btn--outline" href="/">
            Back to the modules
          </a>
        </div>
      </div>
    );
  }
}
