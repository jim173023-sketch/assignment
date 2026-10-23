# BA3073 作业实施说明（DeepSeek 版本）

## 项目位置与本地启动

本次工作目录是 `C:\Codex\AI_Learning_Assistant-main\AI_Learning_Assistant-main`，
不是外层同名文件夹。后端已有编译好的 `backend/static/` 网页文件。

在项目根目录用 PowerShell 运行：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1
# 修改 Python 源码后需要重新构建：
powershell -ExecutionPolicy Bypass -File scripts/start-local.ps1 -Rebuild
```

浏览器地址为 `http://127.0.0.1:14242/ui/`。用自己的 BNBU 邮箱注册/登录。
已有账户的模型设置不会因环境变量改变而自动覆盖；如显示 Qwen，
请在应用设置中改为以下配置并保存：

| 设置 | 值 |
| --- | --- |
| Provider | `openai_compatible` |
| 名称 | `DeepSeek Flash` |
| Base URL | `https://api.deepseek.com` |
| Model | `deepseek-flash` |
| Context window | `1000000` |

共享密钥仅保存在 `data/model-secrets.env` 的 `MODEL_API_KEY=...` 行，
不放入文档、截图或 Git。项目根目录 `.env` 只配置非秘密选项，且已被忽略。
本地端口绑定 `127.0.0.1`，数据挂载到 `data/` 和 `workspace/`。

模型及接口在 2026-10-14 对照官方文档与账户 `/models` 返回值核实：
https://api-docs.deepseek.com/ 和 https://api-docs.deepseek.com/quick_start/pricing/ 。
这是对原作业示例 Qwen 的替代配置；最终报告应如实注明 DeepSeek。

如果 Docker Hub 无法连接，本次验证可用的官方镜像副本路径为：

```powershell
docker pull public.ecr.aws/docker/library/python:3.12-slim-bookworm
docker tag public.ecr.aws/docker/library/python:3.12-slim-bookworm python:3.12-slim-bookworm
```

## Task 1 证据

在项目目录用 Git Bash 执行老师提供的检查脚本：

```bash
bash scripts/check-local-ui.sh
```

输出为根目录 `local-ui-check.txt`，单独提交。HTTP 检查不能替代网页截图。
登录后截取完整浏览器窗口，保留地址栏，并展示实际工作台或生成结果。

报告指令已在 `backend/pipelines/essay_html.py` 增加 BA3073 专用指导：
本地和 ECS 部署结构、提示词改进说明、真实证据、风险与成本、20 页上限。
页数要求属于提示词约束，最终 PDF 仍须实际检查页数。

## 2026-10-22 范围更新与实际状态

根据学生确认的教师要求，取消域名、HTTPS 及反向代理认证要求。
保留 Task 1、Task 2 和原有提交材料；不推测分数如何重新分配。
原始 README 保留不改，范围说明见 `docs/ASSIGNMENT_SCOPE.md`。

2026-10-14 的证据记录：
- 本地 `/ui/` 返回 HTTP 200；日志已保存。
- Linux amd64 镜像经 ACR 推送并被广州 Ubuntu ECS 拉取，标签 `ba3073-v1`。
- ECS 容器为 healthy，端口 14242 已发布，本机 `/health` 返回 `{"status":"ok"}`。
- ECS 回访自身公网 IP 超时，curl 28、HTTP 000；必须保留原日志，原因尚未确定。
- 学生另提供浏览器公网访问及生成成功截图；最终报告需要附上原图。

继续采用仅允许本人公网 IP/32 访问 TCP 14242 的教学测试方式，提交前核对
实际安全组规则。不要为了让 ECS 自回访通过而放开所有来源。
不购买香港服务器或域名。HTTPS 等仅作为未来改进讨论，不能写成已完成。
本次提示词修订尚未部署到 ECS 的旧镜像中；如需更新运行时，应重新构建部署。

## 最终报告与提交

完成云端部署后，将不含秘密的真实日志、配置说明、截图和 URL 提供给本项目助手，
选择 Essay/Report 生成 HTML/PDF。可使用以下任务说明：

> Write the BA3073 "From AI Agent to Cloud Service" assignment report in English.
> Use only the deployment evidence I provide. Follow the BA3073 guidance in the
> essay pipeline, cover Tasks 1-2 and the prompt improvements, and keep the entire
> report within 20 pages. Mark missing evidence and incomplete tasks honestly.
> The actual model provider is DeepSeek. Do not include secrets.
> The instructor has waived domain, HTTPS and reverse-proxy authentication.
> Mark Task 3 NOT REQUIRED under the revised scope, not INCOMPLETE.

只有截图、证据、学生资料和仓库地址齐全并检查过的报告才能作为最终提交。
生成后核对页数、截图、技术解释和所有成功声明。最终提交：

- 最多 20 页的报告；
- 自己的 GitHub 完整项目仓库链接；
- `local-ui-check.txt`；
- `ecs-docker-check.txt`。

`.env*`、`data/`、`workspace/`、依赖目录和密钥不进入源码提交。
老师原仓库作为 upstream 参考，最终需要你自己的 GitHub 仓库。
