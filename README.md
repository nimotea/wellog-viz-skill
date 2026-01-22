# Wellog Visualization Skill 文档

本仓库维护 `wellog-viz` skill 的文档和示例，基于 [videx-wellog](https://github.com/equinor/videx-wellog) 库。

## 项目初始化

首次克隆本仓库后，需要运行以下命令来初始化子模块：

```bash
git submodule update --init --recursive
```

## 项目结构

- `SKILL.md`: skill 描述的主要入口文件。
- `references/`: 详细的示例和数据片段。
- `upstream-src/`: 指向 `videx-wellog` 源代码的 git 子模块。用作参考以确保文档与库保持同步。

## 维护工作流

### ⚠️ 重要提示

本项目**严禁**给依赖的子应用 (`upstream-src`) 推送任何修改。该子模块仅作为参考代码使用。如果需要修改库代码，请直接向原仓库提交 PR，然后通过更新子模块引用的方式同步到本项目。

### 更新源代码引用

要从上游 `videx-wellog` 仓库拉取最新更改：

```bash
git submodule update --remote --merge
```

这将把 `upstream-src` 文件夹更新到上游仓库默认分支的最新提交。然后你可以检查 `upstream-src` 中的代码以验证 API 更改或新功能。

### 更新文档

1. 检查 `upstream-src` 的更改。
2. 相应地更新 `SKILL.md` 或 `references/` 中的文件。
3. 提交你的更改：

```bash
git add .
git commit -m "Update docs based on upstream changes"
```
