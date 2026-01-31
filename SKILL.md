---
name: wellog-viz
description: "A tool for generating well-log visualizations using the videx-wellog library. Use this skill when you need to create, configure, or understand well-log plots, tracks, and viewers. Trigger this skill when the user asks about: (1) Creating new well-log visualizations, (2) Adding tracks (Graph, Scale, Stacked) or plots (Area, Line, Dip), (3) Configuring LogViewer or LogController, (4) Debugging visualization issues (blank screen, React StrictMode), (5) Using High-Level Abstractions (Readout, Auto-Legend, Async Init)."
---

# Well-Log Visualization Skill

8→This skill provides guidance, code snippets, and high-level utilities for using the `videx-wellog` library.
9→
10→## ⚡ Quick Troubleshooting Index
11→
12→Use this index to quickly locate solutions based on symptoms or error messages.
13→
14→| Symptom / Error | Possible Cause | Solution |
15→| :--- | :--- | :--- |
16→| **Chart is invisible / blank** | Incorrect Domain Configuration | Set `domain` to match your data range (e.g., `[3000, 3500]`). Default is `[0, 1000]`. |
17→| **Curve is compressed at top** | Data Format Error | Ensure data is `[depth, value]`, NOT `[value, depth]`. |
18→| **"domain is not iterable"** | `zoomTo()` parameter error | Pass an **array**: `viewer.zoomTo([min, max])`, not individual arguments. |
19→| **"track.addPlot is not a function"** | API Version Mismatch | Use configuration object: `new GraphTrack(id, { plots: [...] })`. |
20→| **"viewer.update is not a function"** | Deprecated/Non-existent API | Remove `.update()`. Use `.refresh()` or rely on auto-update. |
| **Invalid Data Format** | JSON structure mismatch | Refer to [JSON Templates](references/json-templates.md) for standard schemas. |
| **Horizontal mode broken** | Build Format Mismatch | Import from `dist/index.umd.js`. |
22→
23→## Core Concepts

The library revolves around a few key components, augmented by our **Skill Utilities**:

1.  **LogViewer**: The main container. **Note**: `LogViewer` does **not** provide a `.resize()` method; it automatically responds to container size changes. **Important**: Tracks are automatically updated when using `.setTracks()` or `.addTrack()`. For manual redraws, use `.refresh()`. **Recommendation**: Use `mountLogViewer` (from Abstractions) for safe async initialization.
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
2.  **Import Library**:
    - **Recommended (Stable)**: `import { LogViewer } from '@equinor/videx-wellog/dist/index.umd.js';` (Best for horizontal mode compatibility).
    - **Alternative**: `import { LogViewer } from '@equinor/videx-wellog';` (Uses `index.cjs.js` by default).
3.  **Instantiate**: `new LogViewer(options)`.
4.  **Lifecycle**: Ensure `init(div)` is called inside `requestAnimationFrame`. Note that `init()` returns the viewer instance for chainable configuration.

## ⚠️ Common Pitfalls

- **Domain Configuration (CRITICAL)**: The default domain is `[0, 1000]`.
    - **Risk**: If your data is in the range `3000-4000`, it will be completely invisible unless you explicitly set `domain: [3000, 4000]` in the `LogViewer` constructor.
    - **Symptom**: Blank viewer, or data disappears after zoom reset.
- **Build Format Consistency**: Using different entry points (e.g., `dist/index.js` vs `dist/index.umd.js`) may lead to inconsistent behavior, especially for features like **Horizontal Mode**. **CRITICAL**: Always use `index.umd.js` if you encounter rendering anomalies in non-standard environments.
- **Coordinate Order**: Data MUST be in `[Depth, Value]` format. Using `[Value, Depth]` will cause incorrect rendering (compressed data).
- **Lifecycle**: `LogViewer.init()` must be called inside `requestAnimationFrame` after the DOM is ready. **Important**: `init()` returns the instance, but features like `overlay` and `zoomTo` are ONLY available after `init()` has executed.
- **Styles**: Always import `@equinor/videx-wellog/dist/styles/styles.css`.
- **No `.update()` method**: The `LogViewer` does **not** have an `.update()` method. To force a redraw, use `.refresh()`. Note that `setTracks()` and `addTrack()` handle internal updates automatically.
- **Dynamic Data Updates**: For `GraphTrack`, update data via `track.data = newData`. For `StackedTrack` (using function-based data), update your state and call `viewer.refresh()`. See [Best Practices](references/best-practices.md#dynamic-data-updates) for details.
- **No `.resize()` & Responsive Handling**: `LogViewer` does **not** have a `.resize()` method. While it uses `ResizeObserver` internally for simple changes, complex layouts (Grid/Flex/Modals) require manual notification via `viewer.adjustToSize()` if dimensions change after initialization. **Recommendation**: Use `createResponsiveViewer` (Vanilla) or `useResponsiveViewer` (React) from Abstractions to ensure continuous synchronization.
- **Cold Start Rendering Issue**: If the container has `width: 0` or `height: 0` during `viewer.init(dom)`, the internal canvas context will be invalid. The viewer **will not** automatically recover when the container eventually expands. **SOP**: Wait until `clientWidth > 0 && clientHeight > 0` before calling `.init()`, or call `viewer.adjustToSize()` immediately after the container becomes visible.
- **ScaleTrack ID vs Label**: By default, `ScaleTrack` uses its `id` as the header label. If you need a unique ID but a clean label (e.g., ID: `depth-track-01`, Label: `DEPTH`), pass `label` in the options: `new ScaleTrack('depth-track-01', { label: 'DEPTH' })`.

## Available Components

-   **LogViewer**: Interactive container (Zoom/Pan/Overlay).
-   **LogController**: Static renderer (No built-in interaction).
-   **Tracks**: `ScaleTrack`, `GraphTrack`, `StackedTrack`, `DualScaleTrack`.
-   **Plots**: `LinePlot`, `AreaPlot`, `DotPlot`, `DifferentialPlot`, `DipPlot`.

## � API Version Compatibility

Significant changes occurred between v0.x and v1.x (current).

| Feature           | v0.x (Legacy)                        | v1.x (Current)                                         |
| :---------------- | :----------------------------------- | :----------------------------------------------------- |
| **Add Plots**     | `track.addPlot(plot)`                | `new GraphTrack(id, { plots: [...] })` (Config Object) |
| **Scale Options** | `new ScaleTrack(id, { ...options })` | Same, but improved `tickConfig` support.               |
| **Update**        | `viewer.update()` (Internal)         | Removed. Use auto-update or `.refresh()`.              |

## �📚 Knowledge Base

### 🚀 Getting Started
- **Basic Examples**: [EXAMPLES.md](references/examples.md) - Standard boilerplate for Viewers and Tracks.
- **Mock Data**: [MOCK_DATA.md](references/mock-data.md) - Generators for test datasets.
- **Color Palettes**: [PALETTES.md](references/palettes.md) - **NEW**. Geologic standard colors (SY/T 5751).

### 🧩 Patterns & Recipes
-   **Visual Patterns**: [VISUAL_PATTERNS.md](references/visual-patterns.md) - Map visual requirements (screenshots) to code.
-   **JSON Templates**: [JSON_TEMPLATES.md](references/json-templates.md) - **NEW**. Standard JSON data formats for copy-pasting into designers.
-   **Advanced Configs**: [ADVANCED_EXAMPLES.md](references/advanced-examples.md) - Complex layouts (Triple Combo, Horizontal).

### 🛠️ Production Utilities
-   **High-Level Abstractions**: [HIGH_LEVEL_ABSTRACTIONS.md](references/high-level-abstractions.md) - **Recommended**. Helper functions for Readouts, Auto-Legends, and Async Init.
-   **Best Practices**: [BEST_PRACTICES.md](references/best-practices.md) - SOPs, Troubleshooting, and **React Integration**.
