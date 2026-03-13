import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { UserRole } from "../../types/domain";

export function LoginPage(): JSX.Element {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [role, setRole] = useState<UserRole>("annotator");

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    localStorage.setItem("propoai_user", JSON.stringify({ username, role }));

    if (role === "admin") {
      navigate("/admin/cost-monitor");
      return;
    }
    if (role === "employer") {
      navigate("/employer/projects");
      return;
    }
    if (role === "auditor") {
      navigate("/auditor/review");
      return;
    }
    navigate("/annotator/task-square");
  };

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={onSubmit}>
        <h1>PropoAI</h1>
        <p>Sign in to continue annotation workflow</p>

        <label>
          Username
          <input value={username} onChange={(event) => setUsername(event.target.value)} required />
        </label>

        <label>
          Role
          <select value={role} onChange={(event) => setRole(event.target.value as UserRole)}>
            <option value="annotator">Annotator</option>
            <option value="auditor">Auditor</option>
            <option value="employer">Employer</option>
            <option value="admin">Admin</option>
          </select>
        </label>

        <button type="submit" className="primary-btn">Log In</button>
        <span>
          No account? <Link to="/register">Register</Link>
        </span>
      </form>
    </div>
  );
}
