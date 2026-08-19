import { useAuth } from "../context/AuthContext";

export function ProfilePage() {
  const { user } = useAuth();
  return (
    <section className="profile-page">
      <p className="kicker">Reader profile</p>
      <h1>{user?.first_name} {user?.last_name}</h1>
      <dl>
        <div><dt>Username</dt><dd>@{user?.username}</dd></div>
        <div><dt>Email</dt><dd>{user?.email}</dd></div>
        <div><dt>Member since</dt><dd>{user ? new Date(user.created_at).toLocaleDateString() : ""}</dd></div>
      </dl>
    </section>
  );
}