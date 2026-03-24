# PrepoAI 初版框架

面向 Pacman 实验室多模态 LLM 训练（SFT + RLHF）的数据标注与管理系统初版。

本仓库已完成前后端分离的可运行骨架，核心目标是先打通：
- 多角色用户系统入口（Admin / Employer / Annotator / Auditor）
- 抢单式任务广场 -> 标注工作台 -> 提交结果 的主流程
- PostgreSQL + MongoDB 混合存储链路
- 质量管理（Human F1 / Golden / Arbitration）接口占位
- Docker 一体化部署基础设施

## 1. 当前项目结构

```text
PrepoAI/
	backend/
		app/
			api/
			core/
			schemas/
			services/
			integrations/
			main.py
			celery_app.py
		backend_db/
			db.py
			db_models.py
			mongo.py
			db_interface.py
		requirements.txt
		Dockerfile
		celery_worker.py

	frontend/
		src/
			api/
			components/
			hooks/
			locales/
			pages/
			types/
			mocks/
			App.tsx
			main.tsx
			i18n.ts
			styles.css
		package.json
		Dockerfile

	docker-compose.yml
	.env.example
	README.md
```

## 2. 后端能力（FastAPI + Celery）

### 2.1 已实现 API 骨架

- `GET /api/v1/health` 健康检查
- `POST /api/v1/auth/register` 用户注册
- `POST /api/v1/auth/login` 用户登录
- `POST /api/v1/projects` 创建项目
- `GET /api/v1/projects` 项目列表
- `POST /api/v1/projects/{project_id}/import-data` 导入任务内容（Mongo + PG 分配）
- `GET /api/v1/tasks/square` 任务广场列表
- `POST /api/v1/tasks/{task_id}/claim` 抢单
- `POST /api/v1/tasks/{task_id}/submit` 提交标注结果
- `POST /api/v1/tasks/{task_id}/under-review` 转质检
- `POST /api/v1/tasks/{task_id}/finalize` 终审完成
- `POST /api/v1/quality/metric` 记录质量指标
- `GET /api/v1/quality/overview` 质量概览
- `GET /api/v1/dashboard/admin` 管理员看板
- `GET /api/v1/dashboard/annotator/{annotator_id}` 标注员看板
- `GET /api/v1/dashboard/data-distribution` 数据分布概览

### 2.2 `backend_db/` 模块说明

按需求生成了以下四个核心模块：

- `backend_db/db.py`
	- PostgreSQL async engine / session
	- SQLAlchemy Base
	- 初始化建表
- `backend_db/db_models.py`
	- 用户、项目、任务分配、质量指标表
	- 状态机与角色枚举
- `backend_db/mongo.py`
	- MongoDB client / database dependency
- `backend_db/db_interface.py`
	- 混合数据库统一接口：
		- 创建项目
		- 导入任务内容（Task_Content -> Mongo）
		- 生成任务分配（Task_Assignment -> PostgreSQL）
		- 抢单与状态流转
		- 提交标注（Annotation_Result -> Mongo）并回写 `result_doc_id`
		- 记录质量指标（Quality_Metric -> PostgreSQL）

## 3. 数据流（已按需求对齐）

系统工作流程：

1. 任务内容写入 `MongoDB.task_content`
2. 任务分配写入 `PostgreSQL.task_assignments`
3. 标注完成后写入 `MongoDB.annotation_result`
4. Mongo 返回 `document_id`
5. PostgreSQL `task_assignments.result_doc_id` 回写该 `document_id`
6. 质检结果写入 `PostgreSQL.quality_metrics`

## 4. 前端能力（React + TypeScript）

### 4.1 已实现页面框架

- 登录 / 注册
- 标注员端：
	- 任务广场（抢单）
	- 标注工作台（文本主流程）
	- 收益监控
	- 账号管理
- 管理员端：
	- 成本监控
	- 数据分布
	- 标注进度
	- 账号管理
- Employer 端：
	- 项目管理
	- 数据导入
	- 项目看板

### 4.2 标注工作台关键交互

- 快捷键支持：
	- `1~5`：评分
	- `W/S`：上下切样本
	- `Space`：提交
	- `Esc`：任务进行中禁止退出提示
	- `Enter`：聚焦输入框
	- `←/→`：接受 AI 建议 / 基于 AI 编辑
- 布局：左样本导航、中间标注区、右属性面板、底部状态栏
- 文本支持 Markdown 预览切换
- 图像/音频/视频页面提供了明确占位与后续扩展接口位置

### 4.3 多语言

- 已接入中英文 i18n
- 语言包位于 `frontend/src/locales/{zh,en}/common.json`

## 5. 容器化部署

已提供 `docker-compose.yml`，包含：
- `frontend`
- `backend`
- `celery-worker`
- `postgres`
- `mongodb`
- `redis`
- `minio`
- `etcd`
- `milvus`

## 6. 快速启动

### 6.1 Docker 启动（推荐）

```bash
cp .env.example .env
docker compose up --build
```

访问：
- Frontend: `http://localhost:5173`
- Backend API docs: `http://localhost:8000/docs`

### 6.2 本地启动

后端：

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

前端：

```bash
cd frontend
npm install
npm run dev
```

## 7. 下一步建议

1. 接入真实鉴权（JWT 校验、RBAC、接口鉴权依赖）。
2. 完成抢单锁定策略（服务端强制禁止中途退出/回收机制）。
3. 接入图像/音频/视频标注组件与预标注模型 API。
4. 补充看板图表组件（饼图、箱线图、折线、热力图）并连通真实统计接口。
5. 增加金标准混入、自动共识计算、仲裁工作流闭环。
6. 加入测试（后端 pytest + 前端 vitest）和 CI。