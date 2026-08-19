import { BrowserRouter } from "react-router-dom";

import { AppShell } from "./components/AppShell";
import { AppProvider } from "./context/AppContext";
import { AuthProvider } from "./context/AuthContext";
import { AppRoutes } from "./routes/AppRoutes";

export function App() {
  return (
    <BrowserRouter>
      <AppProvider>
        <AuthProvider>
          <AppShell><AppRoutes /></AppShell>
        </AuthProvider>
      </AppProvider>
    </BrowserRouter>
  );
}