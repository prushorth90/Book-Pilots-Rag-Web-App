import { createContext, useContext, type PropsWithChildren } from "react";

interface AppContextValue {
  appName: string;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: PropsWithChildren) {
  return <AppContext.Provider value={{ appName: "Book Pilots" }}>{children}</AppContext.Provider>;
}

export function useAppContext(): AppContextValue {
  const context = useContext(AppContext);
  if (!context) throw new Error("useAppContext must be used within AppProvider");
  return context;
}