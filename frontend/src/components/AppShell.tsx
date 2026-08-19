import { BookOpenText, LogOut } from "lucide-react";
import type { PropsWithChildren } from "react";
import { Link } from "react-router-dom";

import { useAppContext } from "../context/AppContext";
import { useAuth } from "../context/AuthContext";

export function AppShell({ children }: PropsWithChildren) {
  const { appName } = useAppContext();
  const { isAuthenticated, logout } = useAuth();

  return (
    <div className="app-shell">
      <header className="masthead">
        <Link className="brand" to="/" aria-label={`${appName} home`}>
          <BookOpenText aria-hidden="true" size={28} strokeWidth={1.7} />
          <span>{appName}</span>
        </Link>
        <nav className={isAuthenticated ? "authenticated-nav" : ""} aria-label="Account navigation">
          {isAuthenticated ? (
            <>
              <Link to="/discover">Discover</Link>
              <Link to="/library">Library</Link>
              <Link to="/clubs">Clubs</Link>
              <Link to="/calendar">Calendar</Link>
              <Link to="/preferences">Preferences</Link>
              <Link className="logout-link" to="/" title="Log out" aria-label="Log out" onClick={logout}>
                <LogOut aria-hidden="true" size={19} />
              </Link>
            </>
          ) : (
            <><Link to="/login">Log in</Link><Link className="nav-primary" to="/register">Register</Link></>
          )}
        </nav>
      </header>
      <main>{children}</main>
    </div>
  );
}