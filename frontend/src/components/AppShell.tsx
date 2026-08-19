import { BookOpenText } from "lucide-react";
import type { PropsWithChildren } from "react";

import { useAppContext } from "../context/AppContext";

export function AppShell({ children }: PropsWithChildren) {
  const { appName } = useAppContext();

  return (
    <div className="app-shell">
      <header className="masthead">
        <a className="brand" href="/" aria-label={`${appName} home`}>
          <BookOpenText aria-hidden="true" size={28} strokeWidth={1.7} />
          <span>{appName}</span>
        </a>
        <span className="edition">First edition</span>
      </header>
      <main>{children}</main>
    </div>
  );
}