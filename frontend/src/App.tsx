import { useState } from "react";

import ErrorBoundary from "./components/ErrorBoundary";
import ChatPanel from "./components/chat/ChatPanel";
import ChatToggleButton from "./components/chat/ChatToggleButton";
import Dashboard from "./pages/Dashboard";
import ForecastPage from "./pages/ForecastPage";

export default function App() {
  const [view, setView] = useState<"dashboard" | "forecast">("dashboard");

  return (
    <ErrorBoundary>
      {view === "dashboard" ? (
        <Dashboard currentView={view} onNavigate={setView} />
      ) : (
        <ForecastPage currentView={view} onNavigate={setView} />
      )}
      <ChatPanel />
      <ChatToggleButton />
    </ErrorBoundary>
  );
}
