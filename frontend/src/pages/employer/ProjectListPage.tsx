import { mockProjects } from "../../mocks/data";

export function EmployerProjectListPage(): JSX.Element {
  return (
    <div className="panel-stack">
      <section className="panel">
        <h2>项目列表</h2>
        <button className="primary-btn">创建项目</button>
      </section>
      <section className="panel">
        <table className="data-table">
          <thead>
            <tr>
              <th>项目名称</th>
              <th>甲方</th>
              <th>状态</th>
              <th>完成进度</th>
            </tr>
          </thead>
          <tbody>
            {mockProjects.map((project) => (
              <tr key={project.id}>
                <td>{project.name}</td>
                <td>{project.clientName}</td>
                <td>{project.status}</td>
                <td>{Math.round(project.progress * 100)}%</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </div>
  );
}
