import { Component, type ErrorInfo, type ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error("[ErrorBoundary]", error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="m-6 p-6 bg-red-900/30 border border-red-600 rounded-xl">
          <h2 className="text-lg font-bold text-red-300 mb-2">
            Something went wrong
          </h2>
          <pre className="text-xs text-red-200 whitespace-pre-wrap break-words">
            {this.state.error?.message}
          </pre>
          <button
            className="mt-4 px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded-md text-sm transition"
            onClick={() => this.setState({ hasError: false, error: null })}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}
