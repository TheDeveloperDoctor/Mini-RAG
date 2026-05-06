"use client";

import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  fallback?: ReactNode;
  children: ReactNode;
}

interface State {
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { error: null };

  static getDerivedStateFromError(error: Error): State {
    return { error };
  }

  componentDidCatch(error: Error, info: ErrorInfo): void {
    console.error("[ErrorBoundary]", error, info.componentStack);
  }

  reset = (): void => this.setState({ error: null });

  render(): ReactNode {
    if (!this.state.error) return this.props.children;
    if (this.props.fallback) return this.props.fallback;

    return (
      <div className="rounded-2xl border border-amber/30 bg-amber/5 p-4 text-sm text-amber">
        <p className="font-medium text-ink-100">Something broke in this panel.</p>
        <p className="mt-1 font-mono text-xs text-amber/80">{this.state.error.message}</p>
        <button
          onClick={this.reset}
          className="mt-3 rounded-full border border-amber/40 px-3 py-1 text-xs hover:bg-amber/10 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }
}
