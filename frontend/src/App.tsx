import {
  Activity,
  BarChart3,
  BriefcaseBusiness,
  CircleDollarSign,
  Database,
  Files,
  LayoutDashboard,
  UserCog,
  UserRound,
  Workflow
} from "lucide-react";
import { JSX } from "react";
import { useTranslation } from "react-i18next";
import { Navigate, Outlet, Route, Routes } from "react-router-dom";

import { AppShell } from "./components/layout/AppShell";
import { AdminAccountManagementPage } from "./pages/admin/AccountManagementPage";
import { CostMonitorPage } from "./pages/admin/CostMonitorPage";
import { DataDistributionPage } from "./pages/admin/DataDistributionPage";
import { ProgressPage } from "./pages/admin/ProgressPage";
import { AnnotatorAccountPage } from "./pages/annotator/AccountPage";
import { EarningsPage } from "./pages/annotator/EarningsPage";
import { TaskSquarePage } from "./pages/annotator/TaskSquarePage";
import { WorkbenchPage } from "./pages/annotator/WorkbenchPage";
import { AuditorReviewPage } from "./pages/auditor/AuditorReviewPage";
import { LoginPage } from "./pages/auth/LoginPage";
import { RegisterPage } from "./pages/auth/RegisterPage";
import { EmployerDashboardPage } from "./pages/employer/EmployerDashboardPage";
import { EmployerImportDataPage } from "./pages/employer/ImportDataPage";
import { EmployerProjectListPage } from "./pages/employer/ProjectListPage";
import { HomePage } from "./pages/shared/HomePage";

function AnnotatorLayout(): JSX.Element {
  const { t } = useTranslation();
  return (
    <AppShell
      title={t("workbench")}
      menu={[
        { to: "/annotator/task-square", label: t("taskSquare"), icon: <LayoutDashboard size={16} /> },
        { to: "/annotator/workbench/101", label: t("workbench"), icon: <Workflow size={16} /> },
        { to: "/annotator/earnings", label: t("earnings"), icon: <CircleDollarSign size={16} /> },
        { to: "/annotator/account", label: t("account"), icon: <UserRound size={16} /> }
      ]}
    >
      <Outlet />
    </AppShell>
  );
}

function AdminLayout(): JSX.Element {
  const { t } = useTranslation();
  return (
    <AppShell
      title={t("dashboard")}
      menu={[
        { to: "/admin/cost-monitor", label: t("costMonitor"), icon: <CircleDollarSign size={16} /> },
        { to: "/admin/data-distribution", label: t("dataDistribution"), icon: <Database size={16} /> },
        { to: "/admin/progress", label: t("progress"), icon: <Activity size={16} /> },
        { to: "/admin/accounts", label: t("account"), icon: <UserCog size={16} /> }
      ]}
    >
      <Outlet />
    </AppShell>
  );
}

function EmployerLayout(): JSX.Element {
  const { t } = useTranslation();
  return (
    <AppShell
      title={t("projects")}
      menu={[
        { to: "/employer/projects", label: t("projects"), icon: <BriefcaseBusiness size={16} /> },
        { to: "/employer/import", label: t("importData"), icon: <Files size={16} /> },
        { to: "/employer/dashboard", label: t("dashboard"), icon: <BarChart3 size={16} /> }
      ]}
    >
      <Outlet />
    </AppShell>
  );
}

function AuditorLayout(): JSX.Element {
  const { t } = useTranslation();
  return (
    <AppShell
      title="Auditor"
      menu={[
        { to: "/auditor/review", label: "仲裁质检", icon: <Activity size={16} /> },
        { to: "/auditor/account", label: t("account"), icon: <UserRound size={16} /> }
      ]}
    >
      <Outlet />
    </AppShell>
  );
}

export default function App(): JSX.Element {
  return (
    <Routes>
      <Route path="/" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/home" element={<HomePage />} />

      <Route path="/annotator" element={<AnnotatorLayout />}>
        <Route index element={<Navigate to="task-square" replace />} />
        <Route path="task-square" element={<TaskSquarePage />} />
        <Route path="workbench/:taskId" element={<WorkbenchPage />} />
        <Route path="earnings" element={<EarningsPage />} />
        <Route path="account" element={<AnnotatorAccountPage />} />
      </Route>

      <Route path="/admin" element={<AdminLayout />}>
        <Route index element={<Navigate to="cost-monitor" replace />} />
        <Route path="cost-monitor" element={<CostMonitorPage />} />
        <Route path="data-distribution" element={<DataDistributionPage />} />
        <Route path="progress" element={<ProgressPage />} />
        <Route path="accounts" element={<AdminAccountManagementPage />} />
      </Route>

      <Route path="/employer" element={<EmployerLayout />}>
        <Route index element={<Navigate to="projects" replace />} />
        <Route path="projects" element={<EmployerProjectListPage />} />
        <Route path="import" element={<EmployerImportDataPage />} />
        <Route path="dashboard" element={<EmployerDashboardPage />} />
      </Route>

      <Route path="/auditor" element={<AuditorLayout />}>
        <Route index element={<Navigate to="review" replace />} />
        <Route path="review" element={<AuditorReviewPage />} />
        <Route path="account" element={<AnnotatorAccountPage />} />
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
