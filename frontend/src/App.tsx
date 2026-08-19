import { AppShell } from "./components/AppShell";
import { AppProvider } from "./context/AppContext";
import { AppRoutes } from "./routes/AppRoutes";

export function App() {
  return (
    <AppProvider>
      <AppShell>
        <AppRoutes />
      </AppShell>
    </AppProvider>
  );
}