# GitHub 初始化与维护

GitHub CLI (需要本人已授权 `gh auth login`)：

```bash
cd OpenEQMount-starter
git init -b main
git add .
git commit -m "chore: initialize OpenEQMount engineering repository"
gh repo create Accelerator6666/OpenEQMount --private --source . --remote origin --push
```

> 若 `OpenEQMount` 已存在，改用 Git remote/push。默认先建 **private**，等许可证、安全说明和图纸整理好再公开。

建议用 GitHub Issues 管理硬件和固件任务；Pull Requests 做设计审查；Actions 跑数学单元测试。Release 在**实际制造版本已验证**之后再发布，明确版本与硬件修订对应关系。
