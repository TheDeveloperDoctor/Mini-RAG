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
      <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-4 text-sm text-amber-200">
        <p className="font-medium">Something broke in this panel.</p>
        <p className="mt-1 text-xs text-amber-300/80">{this.state.error.message}</p>
        <button
          onClick={this.reset}
          className="mt-3 rounded-md border border-amber-500/40 px-3 py-1 text-xs hover:bg-amber-500/10"
        >
          Retry
        </button>
      </div>
    );
  }
}
