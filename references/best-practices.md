# Best Practices & Troubleshooting

This document contains Standard Operating Procedures (SOPs), common pitfalls, and troubleshooting guides for `videx-wellog`.

## Table of Contents
- [Best Practices \& Troubleshooting](#best-practices--troubleshooting)
  - [Table of Contents](#table-of-contents)
  - [React Integration Patterns](#react-integration-patterns)
    - [Complete React Example (Production Ready)](#complete-react-example-production-ready)
  - [Dynamic Data Updates](#dynamic-data-updates)
    - [0. Unified Update Method (RECOMMENDED)](#0-unified-update-method-recommended)
    - [1. GraphTrack (Line, Area, Dot Plots)](#1-graphtrack-line-area-dot-plots)
    - [2. StackedTrack (Lithology, Formations)](#2-stackedtrack-lithology-formations)
    - [3. Summary of Update Methods](#3-summary-of-update-methods)
  - [Performance Optimization](#performance-optimization)
  - [Error Handling Patterns](#error-handling-patterns)
  - [Testing Strategies](#testing-strategies)
  - [Common Pitfalls](#common-pitfalls)
    - [Debugging \& Integration](#debugging--integration)

## React Integration Patterns

Integrating `videx-wellog` with React requires careful handling of the component lifecycle, `StrictMode`, and DOM references.

### Complete React Example (Production Ready)

This example demonstrates:
1.  **Strict Mode Compatibility**: Prevents double-initialization bugs.
2.  **Responsive Resizing**: Uses `ResizeObserver` to keep the viewer in sync.
3.  **Cleanup Logic**: Properly destroys the viewer to prevent memory leaks.
4.  **Dynamic Updates**: Updates tracks when props change.

```tsx
import React, { useEffect, useRef, useState } from 'react';
import { LogViewer, GraphTrack } from '@equinor/videx-wellog/dist/index.umd.js'; // Use UMD for stability
import '@equinor/videx-wellog/dist/styles/styles.css';

interface WellLogProps {
  tracks: any[]; // Replace 'any' with your TrackConfig type
  domain?: [number, number];
}

export const WellLogComponent: React.FC<WellLogProps> = ({ tracks, domain = [0, 1000] }) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<LogViewer | null>(null);
  const isInitRef = useRef(false); // Guard for StrictMode

  // 1. Initialize Viewer
  useEffect(() => {
    if (!containerRef.current || isInitRef.current) return;

    const viewer = new LogViewer({
      domain: domain,
      // Add other global options here
    });

    // Initialize only when DOM is ready
    requestAnimationFrame(() => {
      if (containerRef.current) {
        viewer.init(containerRef.current);
        viewerRef.current = viewer;
        isInitRef.current = true;
        
        // Initial tracks load
        if (tracks.length > 0) {
          viewer.setTracks(tracks);
        }
      }
    });

    // Cleanup
    return () => {
      // Note: videx-wellog doesn't have a destroy() method, 
      // but we should clear references.
      viewerRef.current = null;
      isInitRef.current = false; 
      if (containerRef.current) {
        containerRef.current.innerHTML = ''; // Clear DOM
      }
    };
  }, []); // Empty dep array: Run once on mount

  // 2. Handle Prop Updates (Tracks)
  useEffect(() => {
    if (viewerRef.current && isInitRef.current) {
      viewerRef.current.setTracks(tracks);
    }
  }, [tracks]);

  // 3. Handle Prop Updates (Domain/Zoom)
  useEffect(() => {
    if (viewerRef.current && isInitRef.current) {
       // zoomTo requires an array [min, max]
       viewerRef.current.zoomTo(domain);
    }
  }, [domain]);

  // 4. Responsive Resize Handling
  useEffect(() => {
    if (!containerRef.current) return;

    const resizeObserver = new ResizeObserver(() => {
      if (viewerRef.current && isInitRef.current) {
        // adjustToSize is the correct method, NOT resize()
        viewerRef.current.adjustToSize();
      }
    });

    resizeObserver.observe(containerRef.current);

    return () => resizeObserver.disconnect();
  }, []);

  return (
    <div 
      ref={containerRef} 
      style={{ height: '800px', width: '100%', position: 'relative' }} 
    />
  );
};
```

## Dynamic Data Updates

Updating data for existing tracks should follow these patterns to ensure consistency across different track types and library versions.

### 0. Unified Update Method (RECOMMENDED)
To avoid dealing with track-specific implementation details (Graph vs Stacked), use the `updateTrackData` abstraction. This handles type detection and refresh automatically.

```typescript
import { updateTrackData } from './high-level-abstractions';

// Works for ANY track type (GraphTrack, StackedTrack, etc.)
await updateTrackData(myTrack, newData, viewer);
```

### 1. GraphTrack (Line, Area, Dot Plots)
`GraphTrack` uses a `data` setter that triggers internal plot updates. 
- **Standard Pattern**: Directly set the `.data` property.
- **Verification**: If the track does not immediately redraw, call `viewer.refresh()`.

```typescript
// Update data for a GraphTrack
const track = viewer.getTrackById('gr-track');
track.data = newDataset; 

// Force a redraw if needed (usually handled automatically by set data)
viewer.refresh();
```

### 2. StackedTrack (Lithology, Formations)
`StackedTrack` often requires its data to be a function returning a `Promise`.
- **Standard Pattern**: Use the `setStackedTrackData` abstraction to handle data merging and refresh.
- **Manual Pattern**: Update your external state and then call `viewer.refresh()` to trigger the re-fetch.

```typescript
import { setStackedTrackData } from './high-level-abstractions';

// Using the abstraction (Simulates .setData())
await setStackedTrackData(stackedTrack, [ { from: 100, to: 200, name: 'Shale' } ], viewer);

// Manual update:
this.currentLithology = updatedData;
viewer.refresh(); // Triggers re-fetch
```

### 3. Summary of Update Methods
| Method               | Purpose           | When to use                                                                                            |
| :------------------- | :---------------- | :----------------------------------------------------------------------------------------------------- |
| `updateTrackData()`  | **Unified API**   | **Recommended.** Automatically handles type detection and refresh for any track.                       |
| `track.data = val`   | Property Setter   | Primary way to update data for `GraphTrack`. See [JSON Templates](json-templates.md) for data schemas. |
| `viewer.refresh()`   | Global Redraw     | Triggers re-fetching for function-based data (like `StackedTrack`) and forces all tracks to repaint.   |
| `viewer.setTracks()` | Re-initialization | Use when adding/removing tracks or completely replacing the track list.                                |

## Performance Optimization

Rendering performance degrades with high-frequency data (>100k points).

1.  **Data Downsampling**: Do not pass raw high-res data (e.g., 1cm sampling) for a 500m view. Use `LTTB` (Largest-Triangle-Three-Buckets) or simple decimation to reduce points to match pixel density.
2.  **Avoid React Re-renders**: Do not wrap `LogViewer` in a component that re-renders on every mouse move. Isolate it with `React.memo` or `useMemo`.
3.  **Columnar Data**: Convert row-based objects (`[{d:1, v:2}, ...]`) to simple arrays (`[[1,2], ...]`) *once* before passing to the viewer. Avoid doing this transformation inside `dataAccessor` (runs on every render).

## Error Handling Patterns

| Error Message                         | Cause                                                                         | Fix                                                                     |
| :------------------------------------ | :---------------------------------------------------------------------------- | :---------------------------------------------------------------------- |
| `undefined is not iterable`           | `zoomTo()` called with separate args, or `GraphTrack` missing top-level data. | Use `zoomTo([min, max])`; Ensure `new GraphTrack(id, { data: ... })`.   |
| `datapoints.filter is not a function` | Invalid data structure passed to track.                                       | Ensure data is an array of `[depth, value]` arrays or object of arrays. |
| `viewer.resize is not a function`     | Calling non-existent method.                                                  | Use `viewer.adjustToSize()`.                                            |

## Testing Strategies

1.  **Unit Test**: Mock `LogViewer` and assert that `setTracks` is called with correct config.
2.  **Integration Test**: Check if container has children (canvas/svg) after `init()`.
3.  **Visual Regression**: Use Playwright/Puppeteer to screenshot the canvas. **Note**: Canvas rendering varies by GPU/Browser; use a high tolerance (5%).

## Common Pitfalls

- **Build Entry Point (Consistency Issue)**:
    - **The Issue**: Directly importing from `dist/index.js` or using the root export might resolve to different build formats (CJS, ESM, UMD) depending on your bundler (Webpack, Vite, Rollup). This can cause features like **Horizontal Mode** (which rely on specific DOM/SVG calculation logic) to break or behave inconsistently.
    - **Recommended**: Always explicitly use the UMD build for maximum stability in browser-based apps.
    - **Code**: `import { LogViewer } from '@equinor/videx-wellog/dist/index.umd.js';`
    - **Symptom**: "Horizontal mode" plots are blank or stretched vertically, while standard vertical mode works fine.
- **Container Height (Invisible Plots)**: The most common cause of "blank" or "invisible" plots is a parent container with zero height.
    - **Requirement**: The DOM element passed to `viewer.init(container)` must have a measurable `clientHeight` > 0.
    - **The Trap**: Using `height: auto` on the container or not setting a height at all in CSS. Since the viewer generates absolute-positioned SVG/Canvas elements, they do not "push" the container height open.
    - **Symptom**: The browser Inspector shows the `div` is 0px tall. No errors in console.
    - **Fix**: Set an explicit height (e.g., `height: 600px` or `height: 80vh`) on the container.
    - **Validation**: Use `validateContainer(el)` from [High-Level Abstractions](references/high-level-abstractions.md) before calling `init()`.
- **Coordinate Order (CRITICAL)**: The library uses a vertical-first orientation common in well-logging. This means the independent variable (Depth) is treated as the primary coordinate.
    - **Requirement**: `dataAccessor` and track data **MUST** use the format `[Depth, Value]`.
    - **The Trap**: Developers often use `[Value, Depth]` (Cartesian `[x, y]`).
    - **Symptom**: The plot looks like "compressed data" or horizontal lines, as the large depth values are being interpreted as plot values, exceeding the track's `domain` and `range`.
    - **Bold Reminder**: Always return **`[Depth, Value]`**.
- **Cold Start Failure (0-dimension init)**:
    - **The Trap**: Initializing the viewer while the container is hidden or has 0 width/height (common in Grid/Flex layouts or Tabs). The internal canvas will fail to set up correctly.
    - **Behavior**: Even after the container expands, the viewer remains blank.
    - **SOP**: Use `ResizeObserver` to detect when the container has a valid size, then call `.init()`.
38→    - **Recovery**: If already initialized, call `viewer.adjustToSize()` and `viewer.refresh()` once the container becomes visible.
- **Manual Update (Redundant)**:
    - **Requirement**: The `LogViewer` automatically redraws when tracks are added or modified via `.addTrack()`, `.setTracks()`, or `.removeTrack()`.
    - **Recommendation**: Avoid searching for a `.update()` method as it does not exist. If you need to force an immediate redraw of all tracks and scales, use `.refresh()`.
- **ScaleTrack ID & Label Decoupling**:
    - **The Issue**: Using unique but cryptic IDs (e.g., `track_depth_01`) often results in ugly header labels if the ID is used directly.
    - **Best Practice**: Always decouple them by passing a explicit `label` or `title` in the options.
    - **Example**: `new ScaleTrack('depth-1', { label: 'DEPTH (m)' })`.
- **ScaleTrack ID and Label Coupling**:
    - **The Trap**: Developers often use the display label as the track `id` (e.g., `new ScaleTrack('DEPTH')`). This can lead to collisions if multiple tracks or viewers share the same ID.
    - **Fix**: Use a unique, stable `id` and provide a readable `label` in the options.
    - **Example**: `new ScaleTrack('well-1-md', { label: 'DEPTH' })`. This ensures internal logic remains robust while the UI remains user-friendly.
- **Resize Method (Common Trap)**: The `LogViewer` does **not** have a `.resize()` method.
    - **Behavior**: It automatically responds to container size changes using an internal `ResizeObserver`.
    - **Persistence Warning**: The internal observer is designed for simple scenarios. In complex layouts (Grid/Flex/Modals), you should implement a **persistent** `ResizeObserver` that calls `viewer.adjustToSize()` to ensure the Canvas/SVG layers stay in sync.
    - **Danger**: Calling `viewer.resize()` will throw a `TypeError: viewer.resize is not a function`.
    - **Manual Trigger**: Use `viewer.refresh()` to force a redraw without changing size, and `viewer.adjustToSize()` to force the viewer to recalculate based on current container dimensions.

### Debugging & Integration
- **Isolated Debugging (CRITICAL)**: When integrating into complex environments (e.g., Low-code platforms like Huozige, PowerApps), **NEVER** debug directly in the platform.
    - **The Risk**: Platform-specific CSS, global variables, or caching mechanisms can obscure root causes.
161→    - **The Solution**: Use the [debug.html](../assets/debug.html) template to verify your logic in a clean environment.
    - **Workflow**:
        1. Copy your track configuration and data to `debug.html`.
        2. Verify if it renders correctly in a standard browser.
        3. If it works in `debug.html` but fails in the platform, the issue is likely **CSS pollution** (check container height) or **JS loading order** (ensure D3 is loaded before wellog).
- **Update Method (CRITICAL)**: The `LogViewer` does **NOT** have an `.update()` method.
    - **Danger**: Calling `viewer.update()` will throw a `TypeError: viewer.update is not a function`.
    - **History**: This was an internal method in older versions or other related components, but is not present in the public `LogViewer` API.
    - **Correct Alternative**:
        - To force a redraw: Use `viewer.refresh()`.
        - After adding/removing tracks: `setTracks()` and `addTrack()` handle updates internally; no manual call is strictly required, though `refresh()` can be used to ensure immediate synchronization.
- **Style Missing**: If tracks look broken or invisible, ensure `styles.css` is imported.
- **Strict Property Names**: The library is strict about property names. Using incorrect names (e.g., `lineWidth` instead of `width` for `LinePlot`) will likely be ignored or cause type errors if using TypeScript.
    - **LinePlot / AreaPlot / DotPlot**: Use `width` for stroke width.
    - **DifferentialPlot**: Use `lineWidth` inside `serie1` / `serie2` options.
    - **GraphTrack**: Use `plots` (array), not `plot` (singular).
- **Invalid Plot Configuration**: Inside `GraphTrack`, the `plots` array MUST contain **configuration objects**, not class instances.
    - **Correct**: `plots: [{ type: 'line', options: { ... } }]`
    - **Incorrect**: `plots: [new LinePlot(...)]` (This will cause "undefined-plot" or similar errors).
- **Track Data vs Plot Data (CRITICAL)**:
    - **Requirement**: `GraphTrack` **MUST** have a top-level `data` property, even if it is an empty array (though actual data is preferred).
    - **The Bug**: If you omit `data` at the track level and only provide `data` inside `plots[].options`, the viewer may render initially but will **CRASH** during rescale/zoom operations (Error: `undefined is not iterable`).
    - **Best Practice**: Always define the data source at the Track level and use `dataAccessor` in Plots to select specific curves.
    ```typescript
    // ❌ CRASH PRONE
    new GraphTrack('bad', {
      plots: [{ type: 'line', options: { data: [[0, 10]] } }] 
    });

    // ✅ ROBUST
    new GraphTrack('good', {
      data: { curve: [[0, 10]] }, // Top-level data
      plots: [{ type: 'line', options: { dataAccessor: d => d.curve } }]
    });
    ```
- **Data Accessor**:
    - If your track `data` is a simple array of `[depth, value]` pairs, you do **not** need a `dataAccessor`.
    - If your track `data` is an object containing multiple datasets (e.g., `{ curveA: [...], curveB: [...] }`), you **must** provide a `dataAccessor` in the plot options (e.g., `dataAccessor: d => d.curveA`).
    - **Row-Oriented Data Warning**: If your `data` is an array of objects (e.g., `[{ depth: 100, gr: 50 }, ...]`) and you pass it directly to `GraphTrack`, you **MUST** provide a `dataAccessor` for **EVERY** plot to extract the specific value and map it to `[depth, value]`.
        - **Incorrect**: `options: { ... }` (Causes `datapoints.filter is not a function`).
        - **Correct**: `options: { dataAccessor: d => d.map(r => [r.depth, r.gr]) }` (Expensive! **Note the [depth, value] order**)
        - **Better**: Transform data to columnar format first (see [Data Preparation](#data-preparation-sop)).
    - **Wide Table Array Warning**: Do NOT use "Wide Tables" (arrays where each row is `[depth, val1, val2, ...]`) directly with `dataAccessor`. The `LinePlot` component may fail to process these correctly, leading to crashes or blank screens.
        - **Risk**: Passing `[[depth, v1, v2], ...]` and using `dataAccessor: d => d.map(r => [r[0], r[1]])` is fragile if the order is confused.
        - **Solution**: Always split wide tables into independent `[depth, value]` arrays BEFORE passing them to the track. See `splitWideData` in High-Level Abstractions.
- **Zooming**: The `viewer.zoomTo()` method expects a **single array argument** `[min, max]`.
    - **Correct**: `viewer.zoomTo([3800, 4200])`
    - **Incorrect**: `viewer.zoomTo(3800, 4200)` (Throws "domain is not iterable").
- **StackedTrack Data**:
    - **Promise Required (CRITICAL)**: The `data` property **MUST** be a function that returns a Promise resolving to the data array.
        - **Incorrect**: `data: myDataArray` (Throws `TypeError: options.data is not a function`).
        - **Correct**: `data: () => Promise.resolve(myDataArray)`
    - **Color Format (CRITICAL)**: `StackedTrack` **REQUIRES** color to be an object `{ r, g, b, a? }`. It does NOT support CSS strings like `'red'` or `'#ff0000'`.
        - **Symptom**: Rendering results in solid black (due to `rgb(undefined,undefined,undefined)`).
        - **Fix**: Use `parseColor` (from High-Level Abstractions) or provide the object manually: `color: { r: 255, g: 0, b: 0 }`.
    - **Data Format**: Expects a sequence of **boundary points**, not intervals. `[{ depth: 100, color: {r:255,g:0,b:0} }, { depth: 200, color: {r:0,g:0,b:255} }]`.
- **ScaleHandler Domain Reset**: When providing a custom `ScaleHandler`, `LogViewer`'s constructor will overwrite the handler's domain with its own `domain` option (default `[0, 1000]`).
