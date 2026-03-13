import { ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { Languages } from "lucide-react";
import { useTranslation } from "react-i18next";

interface MenuItem {
  to: string;
  label: string;
  icon: ReactNode;
}

interface AppShellProps {
  title: string;
  menu: MenuItem[];
  children: ReactNode;
}

export function AppShell({ title, menu, children }: AppShellProps): JSX.Element {
  const { i18n, t } = useTranslation();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">{t("brand")}</div>
        <nav className="nav-list">
          {menu.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}
            >
              {item.icon}
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      </aside>

      <main className="content-area">
        <header className="topbar">
          <div>
            <h1>{title}</h1>
            <p>Pacman Lab Multi-Modal LLM Annotation Platform</p>
          </div>
          <button
            className="lang-switch"
            onClick={() => i18n.changeLanguage(i18n.language === "zh" ? "en" : "zh")}
          >
            <Languages size={16} />
            {t("language")}: {i18n.language.toUpperCase()}
          </button>
        </header>
        <section className="page-body">{children}</section>
      </main>
    </div>
  );
}
