import { Navigate, Route, Routes } from "react-router-dom";

import { ProtectedRoute } from "../components/ProtectedRoute";
import { useAuth } from "../context/AuthContext";
import { DashboardPage } from "../pages/DashboardPage";
import { BookDetailsPage } from "../pages/BookDetailsPage";
import { ClubDetailsPage } from "../pages/ClubDetailsPage";
import { ClubsPage } from "../pages/ClubsPage";
import { CreateClubPage } from "../pages/CreateClubPage";
import { DiscoverPage } from "../pages/DiscoverPage";
import { HomePage } from "../pages/HomePage";
import { LoginPage } from "../pages/LoginPage";
import { LibraryPage } from "../pages/LibraryPage";
import { PreferencesPage } from "../pages/PreferencesPage";
import { ProfilePage } from "../pages/ProfilePage";
import { RegisterPage } from "../pages/RegisterPage";

export function AppRoutes() {
  const { isAuthenticated } = useAuth();
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <LoginPage />} />
      <Route path="/register" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <RegisterPage />} />
      <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
      <Route path="/discover" element={<ProtectedRoute><DiscoverPage /></ProtectedRoute>} />
      <Route path="/books/:workId" element={<ProtectedRoute><BookDetailsPage /></ProtectedRoute>} />
      <Route path="/clubs" element={<ProtectedRoute><ClubsPage /></ProtectedRoute>} />
      <Route path="/clubs/new" element={<ProtectedRoute><CreateClubPage /></ProtectedRoute>} />
      <Route path="/clubs/:clubId" element={<ProtectedRoute><ClubDetailsPage /></ProtectedRoute>} />
      <Route path="/library" element={<ProtectedRoute><LibraryPage /></ProtectedRoute>} />
      <Route path="/preferences" element={<ProtectedRoute><PreferencesPage /></ProtectedRoute>} />
      <Route path="/profile" element={<ProtectedRoute><ProfilePage /></ProtectedRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}