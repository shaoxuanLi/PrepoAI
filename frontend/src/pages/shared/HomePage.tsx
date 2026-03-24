import { Link } from "react-router-dom";

export function HomePage(): JSX.Element {
  return (
    <div className="landing-page">
      <div className="hero-card">
        <h1>PrepoAI Annotation System</h1>
        <p>High-efficiency platform for SFT and RLHF in Pacman Lab.</p>
        <div className="hero-actions">
          <Link className="primary-btn" to="/annotator/task-square">
            Enter Task Square
          </Link>
          <Link className="ghost-btn" to="/admin/cost-monitor">
            Admin Dashboard
          </Link>
          <Link className="ghost-btn" to="/employer/projects">
            Employer Console
          </Link>
        </div>
      </div>
    </div>
  );
}
