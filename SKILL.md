---
name: wellog-viz
description: "A tool for generating well-log visualizations using the videx-wellog library. Use this skill when you need to create, configure, or understand well-log plots, tracks, and viewers. Trigger this skill when the user asks about: (1) Creating new well-log visualizations, (2) Adding tracks (Graph, Scale, Stacked) or plots (Area, Line, Dip), (3) Configuring LogViewer or LogController, (4) Debugging visualization issues (blank screen, React StrictMode), (5) Using High-Level Abstractions (Readout, Auto-Legend, Async Init)."
---

# Well-Log Visualization Skill

This skill provides guidance, code snippets, and high-level utilities for using the `videx-wellog` library.

## Core Concepts

The library revolves around a few key components, augmented by our **Skill Utilities**:

1.  **LogViewer**: The main container. **Recommendation**: Use `mountLogViewer` (from Abstractions) for safe async initialization.
2.  **Tracks**: Vertical strips (e.g., `GraphTrack`, `ScaleTrack`). **Recommendation**: Use `createSimpleTrack` for reduced boilerplate.
3.  **Plots**: Visual representations (e.g., `LinePlot`, `AreaPlot`).
4.  **ScaleHandler**: Manages depth scale/zooming.

## Usage Guide

### Recommended Workflow (High-Level)

Instead of manually handling DOM and Events, use the **High-Level Abstractions** to speed up development:

1.  **Init**: Use `initLogViewer` or `mountLogViewer` to handle DOM readiness and React StrictMode safety.
2.  **Config**: Use `createSimpleTrack` to define tracks with auto-generated legends.
3.  **Interact**: Use `ReadoutPlugin` to add mouse-following tooltips without manual DOM coding.

### Basic Setup (Low-Level)

If you need full control:

1.  **Import Styles**: `import '@equinor/videx-wellog/dist/styles/styles.css';`
2.  **Instantiate**: `new LogViewer(options)`.
3.  **Lifecycle**: Ensure `init(div)` is called inside `requestAnimationFrame`.

## Available Components

-   **LogViewer**: Interactive container (Zoom/Pan/Overlay).
-   **LogController**: Static renderer (No built-in interaction).
-   **Tracks**: `ScaleTrack`, `GraphTrack`, `StackedTrack`, `DualScaleTrack`.
-   **Plots**: `LinePlot`, `AreaPlot`, `DotPlot`, `DifferentialPlot`, `DipPlot`.

## 📚 Knowledge Base

### 🚀 Getting Started
-   **Basic Examples**: [EXAMPLES.md](references/examples.md) - Standard boilerplate for Viewers and Tracks.
-   **Mock Data**: [MOCK_DATA.md](references/mock-data.md) - Generators for test datasets.

### 🧩 Patterns & Recipes
-   **Visual Patterns**: [VISUAL_PATTERNS.md](references/visual-patterns.md) - Map visual requirements (screenshots) to code.
-   **Advanced Configs**: [ADVANCED_EXAMPLES.md](references/advanced-examples.md) - Complex layouts (Triple Combo, Horizontal).

### 🛠️ Production Utilities
-   **High-Level Abstractions**: [HIGH_LEVEL_ABSTRACTIONS.md](references/high-level-abstractions.md) - **Recommended**. Helper functions for Readouts, Auto-Legends, and Async Init.
-   **Best Practices**: [BEST_PRACTICES.md](references/best-practices.md) - SOPs, Troubleshooting, and **React Integration**.
