---
name: wellog-viz
description: A tool for generating well-log visualizations using the videx-wellog library. Use this skill when you need to create, configure, or understand well-log plots, tracks, and viewers. Trigger this skill when the user asks about: (1) Creating new well-log visualizations, (2) Adding tracks (Graph, Scale, Stacked) or plots (Area, Line, Dip), (3) Configuring LogViewer or LogController, (4) Debugging visualization issues or "blank screen" errors, (5) Mocking well-log data.
---

# Well-Log Visualization Skill

This skill provides guidance and code snippets for using the `videx-wellog` library to create well-log visualizations.

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

### Best Practices & Troubleshooting

For detailed SOPs, common pitfalls, and robust initialization patterns, see **[BEST_PRACTICES.md](references/best-practices.md)**. This includes:
-   **Common Pitfalls**: Resize issues, style missing, invalid plot config.
-   **TypeScript Errors**: Fixing missing `legendInfo`.
-   **Robust Initialization**: Preventing blank screens.
-   **Data Preparation**: Transforming row data to columnar format.

## Available Components

-   **LogViewer**: The primary component for interactive visualization.
    -   **MUST be used** if you need built-in zooming, panning, or overlay interactions.
    -   Usage: `new LogViewer(options)`. **Avoid `LogViewer.basic()`**.
-   **LogController**: The base class for rendering tracks without interaction.
    -   **Use only** for static exports (e.g., PDF generation) or if you are building a completely custom interaction layer.
    -   **Does NOT support** zoom/pan out of the box.
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

## Reference Material

-   **Examples & Snippets**: See [EXAMPLES.md](references/examples.md) for basic usage.
-   **Best Practices**: See [BEST_PRACTICES.md](references/best-practices.md) for SOPs and troubleshooting.
-   **Visual Patterns**: See [VISUAL_PATTERNS.md](references/visual-patterns.md) for mapping visual styles to code configurations.
-   **Advanced Configurations**: See [ADVANCED_EXAMPLES.md](references/advanced-examples.md) for complex track setups.
-   **Mock Data**: See [MOCK_DATA.md](references/mock-data.md) for data generation helpers.
-   **API Details**: (Refer to source code in `src/` or generated docs in `docs/` if needed).
