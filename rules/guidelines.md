# Wellog Visualization Skill Guidelines

This document combines product maintenance (PM) and development application (Apply) rules for the `wellog-viz` skill.

## 🛠 Core Principles

1.  **Non-Invasive**: Avoid modifying the `upstream-src` (videx-wellog) source code. Changes should focus on the Skill's documentation, abstractions, and configurations.
2.  **Quality First**: Perform technical and logic audits before accepting changes. Do not blindly follow user requests if they violate library principles.
3.  **Audit & Refactor**: Classify tasks as "Requirement/Scenario" or "Technical/Operational". Use appropriate workflows for each.

---

## 📋 Maintenance Workflow (PM)

### Phase 1: Classification & Audit
- **Requirement/Scenario**: Collect logs if applicable. Verify if the issue is real.
- **Technical/Operational**: Direct refactoring or documentation updates.

### Phase 2: Refactoring Standards
- Follow the standard Skill structure: `SKILL.md`, `references/`, `assets/`, `scripts/`.
- Ensure modularity and clarity in high-level abstractions.

### 🤖 Output Format (Maintenance)
- 【输入类别】
- 【日志审计】
- 【审计结论】
- 【整改方案】
- 【执行结果】
- 【改进建议】

---

## 📋 Development Feedback (Apply)

As an AI developing with this skill, you must audit the skill's completeness and usability.

### 1. Gap Detection
Record if there are:
- **Missing Info**: Missing APIs or constraints.
- **Misleading Guidance**: Documentation inconsistent with implementation.
- **Blurry Boundaries**: Unclear performance limits or unsupported scenarios.

### 2. Tooling Enhancements
Suggest improvements for:
- **Engineering Support**: Better logs, mock data, or validation rules.
- **Atomic Capabilities**: High-frequency manual logic that should be built-in.
- **Defensive Warnings**: New "Common Pitfalls" based on your experience.

### 🤖 Mandatory Feedback Module (End of Task)
【wellog-viz 技能优化建议】
- [问题/建议类型]: (缺陷修复 / 易用性改进 / 功能增强 / 风险警示 / 无)
- [场景还原]:
- [现状痛点]:
- [改进建议]: (文档/逻辑优化)
