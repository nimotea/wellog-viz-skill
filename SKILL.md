---
name: wellog-viz
description: A tool for generating well-log visualizations using the videx-wellog library. Use this skill when you need to create, configure, or understand well-log plots, tracks, and viewers.
---

# Well-Log Visualization Skill

This skill provides guidance and code snippets for using the `videx-wellog` library to create well-log visualizations.

## When to use this skill

Use this skill when:
- You need to create a new well-log visualization.
- You want to add specific tracks (Graph, Scale, Stacked, etc.) to a log viewer.
- You need to configure plot types (Area, Line, Dot, etc.).
- You are debugging or modifying existing well-log code.

## Core Concepts

The library revolves around a few key components:
1.  **LogViewer**: The main container that holds tracks.
2.  **Tracks**: Vertical strips that display data (e.g., `GraphTrack`, `ScaleTrack`, `StackedTrack`).
3.  **Plots**: Visual representations of data within a track (e.g., `LinePlot`, `AreaPlot`).
4.  **ScaleHandler**: Manages the depth scale and zooming.

## Usage Guide

### Basic Setup

To create a basic log viewer:

1.  **Import Styles**: You MUST import the CSS styles for the viewer to render correctly.
    ```typescript
    import '@equinor/videx-wellog/dist/styles/styles.css';
    ```
2.  Instantiate `LogViewer`.
3.  Create Tracks.
4.  Add Tracks to the Viewer.
5.  Initialize the Viewer with a DOM element.

### Common Pitfalls

-   **Resize Method**: The `LogViewer` does **not** have a `.resize()` method. Do not attempt to call `viewer.resize()`. The viewer handles resizing automatically or requires re-initialization logic depending on the wrapper.
-   **Style Missing**: If tracks look broken or invisible, ensure `styles.css` is imported.
-   **Strict Property Names**: The library is strict about property names. Using incorrect names (e.g., `lineWidth` instead of `width` for `LinePlot`) will likely be ignored or cause type errors if using TypeScript.
    -   **LinePlot / AreaPlot / DotPlot**: Use `width` for stroke width.
    -   **DifferentialPlot**: Use `lineWidth` inside `serie1` / `serie2` options.
    -   **GraphTrack**: Use `plots` (array), not `plot` (singular).
-   **Invalid Plot Configuration**: Inside `GraphTrack`, the `plots` array MUST contain **configuration objects**, not class instances.
    -   **Correct**: `plots: [{ type: 'line', options: { ... } }]`
    -   **Incorrect**: `plots: [new LinePlot(...)]` (This will cause "undefined-plot" or similar errors).
-   **Data Accessor**:
    -   If your track `data` is a simple array of `[depth, value]` pairs, you do **not** need a `dataAccessor`.
    -   If your track `data` is an object containing multiple datasets (e.g., `{ curveA: [...], curveB: [...] }`), you **must** provide a `dataAccessor` in the plot options (e.g., `dataAccessor: d => d.curveA`).
-   **Zooming**: The `viewer.zoomTo()` method expects a **single array argument** `[min, max]`.
    -   **Correct**: `viewer.zoomTo([3800, 4200])`
    -   **Incorrect**: `viewer.zoomTo(3800, 4200)` (Throws "domain is not iterable").
-   **StackedTrack Data**:
    -   **Promise Required**: The `data` property MUST be a function that returns a Promise resolving to the data array. Passing the array directly will cause "options.data(...).then is not a function" errors.
    -   **Data Format**: Expects a sequence of **boundary points**, not intervals. `[{ depth: 100, color: 'red' }, { depth: 200, color: 'blue' }]`.
-   **Initialization**: While the `LogViewer` constructor accepts a container, it is more robust to use `viewer.init(element)` wrapped in `requestAnimationFrame`.
    -   This ensures the DOM is fully ready before the viewer attempts to measure dimensions.

See [EXAMPLES.md](references/examples.md) for concrete code snippets.

### Available Components

-   **LogViewer**: `LogViewer.basic()` or `new LogViewer(options)`
-   **Tracks**:
    -   `ScaleTrack`: Displays depth scale.
    -   `GraphTrack`: Displays line/area graphs.
    -   `StackedTrack`: Displays stacked data (e.g., lithology).
    -   `DualScaleTrack`: Scale track with dual units.
-   **Plots**:
    -   `LinePlot`
    -   `AreaPlot`
    -   `DotPlot`
    -   `DifferentialPlot`

### Reference Material

-   **Examples & Snippets**: See [EXAMPLES.md](references/examples.md) for basic usage.
-   **Advanced Configurations**: See [ADVANCED_EXAMPLES.md](references/advanced-examples.md) for complex track setups.
-   **Mock Data**: See [MOCK_DATA.md](references/mock-data.md) for data generation helpers.
-   **API Details**: (Refer to source code in `src/` or generated docs in `docs/` if needed).
