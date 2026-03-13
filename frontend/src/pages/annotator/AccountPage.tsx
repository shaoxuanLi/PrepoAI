export function AnnotatorAccountPage(): JSX.Element {
  return (
    <div className="panel-stack">
      <section className="panel">
        <h2>账号信息</h2>
        <p>角色: Annotator</p>
        <p>累计积分: 2350</p>
      </section>
      <section className="panel">
        <h2>安全设置</h2>
        <button className="ghost-btn">修改密码</button>
        <button className="ghost-btn">启用双因素认证</button>
      </section>
    </div>
  );
}
