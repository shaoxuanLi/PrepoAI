import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

export function RegisterPage(): JSX.Element {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");

  const onSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    localStorage.setItem("propoai_user", JSON.stringify({ username, email, role: "annotator" }));
    navigate("/");
  };

  return (
    <div className="auth-page">
      <form className="auth-card" onSubmit={onSubmit}>
        <h1>Create Account</h1>
        <p>Full user system API is reserved and can be connected in backend iteration.</p>

        <label>
          Username
          <input value={username} onChange={(event) => setUsername(event.target.value)} required />
        </label>

        <label>
          Email
          <input type="email" value={email} onChange={(event) => setEmail(event.target.value)} required />
        </label>

        <label>
          Password
          <input type="password" minLength={6} required />
        </label>

        <button type="submit" className="primary-btn">Register</button>
        <span>
          Already have account? <Link to="/">Log In</Link>
        </span>
      </form>
    </div>
  );
}
