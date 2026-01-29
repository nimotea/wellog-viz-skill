# Best Practices & Troubleshooting

This document contains Standard Operating Procedures (SOPs), common pitfalls, and troubleshooting guides for `videx-wellog`.

## Table of Contents
- [Common Pitfalls](#common-pitfalls)
- [TypeScript & Build Configuration](#typescript--build-configuration)
- [Robust Initialization (SOP)](#robust-initialization-sop)
- [Data Preparation (SOP)](#data-preparation-sop)
- [Responsive Layout & Resize Handling](#responsive-layout--resize-handling)

## Common Pitfalls

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
- **Manual Update Requirement (Common Pitfall)**: The `LogViewer` does **not** automatically redraw when tracks are added or modified via `.addTrack()`, `.setTracks()`, or `.removeTrack()`.
    - **Requirement**: You **MUST** call `viewer.update()` after your configuration is complete to render the content.
    - **Symptom**: The viewer is initialized and the container has height, but the tracks do not appear.
    - **Fix**: Add `viewer.update();` at the end of your setup logic.
- **Resize Method (Common Trap)**: The `LogViewer` does **not** have a `.resize()` method.
    - **Behavior**: It automatically responds to container size changes using an internal `ResizeObserver`.
    - **Persistence Warning**: The internal observer is designed for simple scenarios. In complex layouts (Grid/Flex/Modals), you should implement a **persistent** `ResizeObserver` that calls `viewer.adjustToSize()` to ensure the Canvas/SVG layers stay in sync.
    - **Danger**: Calling `viewer.resize()` will throw a `TypeError: viewer.resize is not a function`.
    - **Manual Trigger**: Use `viewer.refresh()` to force a redraw without changing size, and `viewer.adjustToSize()` to force the viewer to recalculate based on current container dimensions.
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
    - **Fix**: Explicitly pass the `domain` in `LogViewer` options to match your handler, or re-apply it after creation.
    ```typescript
    const handler = new BasicScaleHandler([0, 5000]);
    
    // INCORRECT: Domain resets to [0, 1000]
    // const viewer = new LogViewer({ scaleHandler: handler });
    
    // CORRECT: Consistent domain
    const viewer = new LogViewer({ 
      scaleHandler: handler,
      domain: [0, 5000] 
    });
    ```

## Lifecycle & Initialization Order (Strict Requirement)

The `videx-wellog` library has a strict dependency on the DOM and initialization order. Failing to follow this order will result in runtime errors.

**Strict Order:**
1.  **Construct**: `new LogViewer(...)`
2.  **Mount**: Ensure the DOM container exists and has non-zero dimensions.
3.  **Init**: Call `viewer.init(container)`.
    -   **Return Value**: `viewer.init()` returns the `LogViewer` instance itself, allowing for chainable configuration (e.g., `.setTracks(...)`).
    -   *Constraint*: Must be called BEFORE setting tracks, accessing overlay, or using scale-dependent methods.
4.  **Configure**: Call `viewer.setTracks(...)` or `viewer.addTrack(...)`.
5.  **Update**: Call `viewer.update()` to render.
6.  **Interact**: Access `viewer.overlay` or call `viewer.zoomTo(...)`.

**Critical Operations Post-Init:**
The following features are **unavailable** until `init()` is called and the internal SVG/Canvas layers are created:
-   `viewer.overlay` (Undefined or will throw errors)
-   `viewer.zoomTo()` (Will fail as the coordinate scales are not yet initialized)
-   `viewer.scale` (The D3 scale instance is not ready)
-   `viewer.setTracks()` / `viewer.addTrack()` (Will fail to find the DOM node to append tracks to)

**Correct Pattern (using requestAnimationFrame):**

The use of `requestAnimationFrame` (RAF) is recommended because it ensures the code runs after the browser has completed the current layout pass and the DOM is definitely ready for manipulation.

```typescript
// 1. Construct
const viewer = new LogViewer();

// 2. Wait for DOM readiness via requestAnimationFrame
requestAnimationFrame(() => {
  const container = document.getElementById('log-container');
  
  if (!container) return;

  // 3. Init (returns the instance, enabling chainability)
  // 4. Configure (Set Tracks)
  viewer.init(container).setTracks([scaleTrack, graphTrack]);
  
  // 5. Update (Mandatory for rendering)
  viewer.update();
  
  // 6. Interact (Overlay/Zoom) - Only safe AFTER init()
  viewer.overlay.create('my-overlay', { ... });
  viewer.zoomTo([1000, 1500]);
});
```

## TypeScript & Build Configuration

### Missing `legendInfo`
The library's `PlotOptions` interface is missing the `legendInfo` property.

**Robust Fix (Module Augmentation)**: Create a declaration file (e.g., `wellog.d.ts`) in your project root or `src/@types` folder.

```typescript
// wellog.d.ts
import '@equinor/videx-wellog';

declare module '@equinor/videx-wellog' {
  // Augment the base PlotOptions interface
  export interface PlotOptions {
    legendInfo?: (data: any) => { label: string; unit: string };
  }
}
```

### Modern Build Tools (Vite/Esbuild)
**Import Type**: When importing interfaces, ALWAYS use `import type` to avoid "does not provide an export" errors at runtime.
- **Correct**: `import type { PlotOptions } from ...`
- **Incorrect**: `import { PlotOptions } from ...`

### LogViewer Instantiation (Avoid `.basic()`)
**Problem**: `LogViewer.basic()` returns a `LogController` type (or a limited instance) which lacks interaction properties like `overlay`, leading to runtime errors.
**Fix**: ALWAYS use `new LogViewer()` to ensure full functionality (Zoom, Overlay, Pan).

```typescript
// ❌ AVOID
// const viewer = LogViewer.basic(); 

// ✅ CORRECT
const viewer = new LogViewer(); 
// or with options
const viewer = new LogViewer({ showLegend: true, showTitles: true });
```

### Modern Bundler Configuration (Vite/Webpack)
When using modern bundlers like Vite or Webpack, D3 v5's CommonJS/UMD modules, especially `d3-transition`, might not have their side effects correctly loaded, leading to runtime errors like `selection.interrupt is not a function`. This is because D3 v5 expects a global `d3` object to attach transitions to.

**Solution: Alias `d3` to its UMD build**
Configure your bundler to alias `d3` to its UMD distribution file (`d3/dist/d3.js`). This ensures that D3 is loaded as a single, global object, allowing `d3-transition` to correctly attach its side effects.

**Vite Configuration (vite.config.js):**
```javascript
import { defineConfig } from 'vite';
import path from 'path';

export default defineConfig({
  resolve: {
    alias: {
      'd3': path.resolve(__dirname, 'node_modules/d3/dist/d3.js'),
    },
  },
});
```

**Webpack Configuration (webpack.config.js):**
```javascript
const path = require('path');

module.exports = {
  resolve: {
    alias: {
      'd3': path.resolve(__dirname, 'node_modules/d3/dist/d3.js'),
    },
  },
};
```

This ensures that all D3 modules correctly share the same global `d3` instance, resolving issues with `d3-transition` and similar plugins.

## Robust Initialization (SOP)

Use this pattern to avoid blank screens caused by initializing on hidden/zero-height elements or before the DOM is ready.

### Check and Render Template (Recommended)

Since `videx-wellog` captures the container size *only* at initialization and does not self-correct if it starts at 0px, you should use a "Check and Render" strategy.

```typescript
import { LogViewer, Track } from '@equinor/videx-wellog';

/**
 * Ensures the container has dimensions before initializing the viewer.
 * If dimensions are 0, it waits via ResizeObserver.
 */
export function safeRender(container: HTMLElement, viewer: LogViewer, tracks: Track[]) {
  const initIfReady = () => {
    const rect = container.getBoundingClientRect();
    if (rect.width > 0 && rect.height > 0) {
      // 1. Init
      viewer.init(container);
      // 2. Configure
      viewer.setTracks(tracks);
      // 3. Update
      viewer.update();
      return true;
    }
    return false;
  };

  // Try immediately (inside RAF)
  requestAnimationFrame(() => {
    if (initIfReady()) return;

    // If not ready (0 size), wait for size change
    console.warn('[wellog-viz] Container has 0 size. Waiting for dimensions...');
    const observer = new ResizeObserver((entries, obs) => {
      if (initIfReady()) {
        obs.disconnect(); // Stop watching once initialized
      }
    });
    observer.observe(container);
  });
}
```

### Legacy Initialization Pattern

```typescript
import { LogViewer, Track } from '@equinor/videx-wellog';

/**
 * Safely initializes a LogViewer instance.
 * @param container The DOM element to mount the viewer into.
 * @param viewer The LogViewer instance.
 * @param tracks Array of tracks to set.
 */
export function initLogViewerSafe(
  container: HTMLElement | null,
  viewer: LogViewer,
  tracks: Track[]
) {
  if (!container) {
    console.error('LogViewer Init Error: Container element is null.');
    return;
  }

  // Ensure container has dimensions
  const rect = container.getBoundingClientRect();
  if (rect.height === 0 || rect.width === 0) {
    console.warn('LogViewer Init Warning: Container has zero width/height. Viewer may be invisible.');
    // Optional: Set a fallback height
    // container.style.height = '500px';
  }

  // Use requestAnimationFrame to wait for the next paint frame (ensures DOM is settled)
  requestAnimationFrame(() => {
    try {
      viewer.init(container).setTracks(tracks);
      // IMPORTANT: All subsequent viewer interactions MUST be inside this callback
      // viewer.overlay.create(...) 
      // viewer.zoomTo(...)
    } catch (e) {
      console.error('LogViewer Init Failed:', e);
    }
  });
}

// Usage:
// initLogViewerSafe(document.getElementById('root'), viewer, [scaleTrack, graphTrack]);
// ❌ WRONG: viewer.zoomTo(...) // Will fail because init() happens async
```

## Promise-Based Initialization (Async/Await)

To avoid callback hell and timing issues, use the `initLogViewer` helper from [High-Level Abstractions](high-level-abstractions.md).

```typescript
import { initLogViewer } from './utils/wellog-helpers';

async function setup() {
  const viewer = new LogViewer();
  // ... configure tracks ...
  
  // Await the initialization
  await initLogViewer(viewer, document.getElementById('root'));
  
  // Safe to use viewer methods now
  viewer.setTracks(tracks);
  viewer.zoomTo([1000, 1200]);
}
```

## React Integration Patterns

Using `LogViewer` in React requires careful handling of the `useEffect` lifecycle to prevent memory leaks, race conditions, and "blank screen" issues caused by StrictMode double-invocation.

**Key Rules:**
1.  **Cancel RAF**: Always store the `requestAnimationFrame` ID and cancel it in the cleanup function.
2.  **Dispose Viewer**: Although the library doesn't have a formal `dispose` method, you should nullify references and clear HTML content to prevent detached DOM nodes.
3.  **Ref Stability**: Use `useRef` to hold the viewer instance if you need to access it outside the effect.

```tsx
import React, { useEffect, useRef } from 'react';
import { LogViewer, ScaleTrack } from '@equinor/videx-wellog';

export const WellLogComponent = () => {
  const containerRef = useRef<HTMLDivElement>(null);
  const viewerRef = useRef<LogViewer | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    let rafId: number;
    let isActive = true; // Guard for cleanup

    // 1. Create Instance
    const viewer = new LogViewer({ showLegend: true });
    viewerRef.current = viewer;

    // 2. Async Init via RAF
    rafId = requestAnimationFrame(() => {
      if (!isActive || !containerRef.current) return;

      try {
        // 3. Init & Configure INSIDE the callback
        viewer.init(containerRef.current);
        
        // Define tracks
        const scaleTrack = new ScaleTrack('scale');
        viewer.setTracks([scaleTrack]);
        
        // Optional: Interactions
        viewer.zoomTo([0, 100]);
        
      } catch (err) {
        console.error('Viewer Init Error:', err);
      }
    });

    // 4. Cleanup Function
    return () => {
      isActive = false;
      cancelAnimationFrame(rafId);
      
      // Clear DOM to prevent duplicates in StrictMode
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
      viewerRef.current = null;
    };
  }, []); // Empty dependency array for mount-only logic

  return <div ref={containerRef} style={{ height: '500px', width: '100%' }} />;
};
```

## Deep Well Data & Domain Configuration

**The Problem**: `LogViewer` defaults to a domain of `[0, 1000]`. If you visualize data at greater depths (e.g., 3000m - 4000m) without setting the `domain`, interactions will fail. The initial `zoomTo` might show data, but the first mouse scroll will likely snap the view back to the wrong range or corrupt the coordinate system.

**Solution 1: Explicit Configuration (CRITICAL)**
Always set the `domain` in the constructor to encompass your entire well depth. 

> ⚠️ **WARNING**: If you `zoomTo` a range (e.g., `[4000, 4100]`) that is outside the configured `domain` (default `[0, 1000]`), the viewer may render initially, but **any interaction** (scroll/pan) will cause the view to snap back or "fly away" to the default domain. You **MUST** set the domain to cover the full data range.

```typescript
const viewer = new LogViewer({
  domain: [0, 6000], // Covers typical well depth
});
```

**Solution 2: Auto-Calculation Helper**
Use this helper to calculate the domain dynamically from your tracks.

```typescript
import { Track } from '@equinor/videx-wellog';

/**
 * Calculates the min/max depth across all provided tracks.
 * Assumes tracks have a `data` property (GraphTrack) or similar structure.
 * Note: This is a heuristic helper.
 */
export function calculateDomainFromTracks(tracks: Track[]): [number, number] | null {
  let min = Infinity;
  let max = -Infinity;
  let found = false;

  tracks.forEach(track => {
    // Check for standard GraphTrack data array (Row or Columnar)
    // Implementation depends on your data structure.
    // This example assumes a simple array of [depth, value] or object structure.
    
    // ... (Add your specific logic here based on how you store data)
    // For manual configuration, it is often safer to pass the known
    // min/max depth from your API response.
  });

  return found ? [min, max] : null;
}
```

**Recommended**: Since iterating tracks can be complex (lazy loading, promises), it is **best practice** to pass the known wellbore MD (Measured Depth) range from your back-end metadata directly to the `LogViewer` constructor.

```typescript
// Best Practice: Use metadata from API
const wellMetaData = { maxDepth: 4500 }; 
const viewer = new LogViewer({ 
  domain: [0, wellMetaData.maxDepth + 100] 
});
```

## Responsive Layout & Resize Handling

In modern web applications using CSS Grid, Flexbox, or resizable panels, the container size can change frequently. Since `LogViewer` renders to Canvas/SVG, it must be explicitly notified to recalculate its internal scaling and buffer sizes.

### The Responsive Pattern (Persistent Observer)

The most robust way to handle responsive layouts is to maintain a persistent `ResizeObserver` for the lifetime of the viewer.

```typescript
import { LogViewer } from '@equinor/videx-wellog';

/**
 * Attaches a persistent resize observer to keep the viewer in sync with its container.
 * @param container The DOM element.
 * @param viewer The LogViewer instance.
 * @returns A function to disconnect the observer.
 */
export function attachResponsiveHandler(container: HTMLElement, viewer: LogViewer) {
  const observer = new ResizeObserver(() => {
    // ⚠️ CRITICAL: adjustToSize() handles recalculating scales and canvas dimensions
    viewer.adjustToSize();
  });
  
  observer.observe(container);
  return () => observer.disconnect();
}
```

### React Responsive Hook (Recommended)

In React, this should be handled within a `useEffect` to ensure proper cleanup.

```tsx
import { useEffect, useRef } from 'react';
import { LogViewer } from '@equinor/videx-wellog';

export const useResponsiveLogViewer = (
  containerRef: React.RefObject<HTMLElement>,
  viewer: LogViewer | null
) => {
  useEffect(() => {
    const el = containerRef.current;
    if (!el || !viewer) return;

    const observer = new ResizeObserver(() => {
      // Debounce is optional but recommended for high-performance layouts
      viewer.adjustToSize();
    });

    observer.observe(el);
    return () => observer.disconnect();
  }, [containerRef, viewer]);
};
```

### When to use `refresh()` vs `adjustToSize()`

| Method               | Use Case                                                                                                                                   |
| :------------------- | :----------------------------------------------------------------------------------------------------------------------------------------- |
| **`adjustToSize()`** | **Container dimensions changed.** Use this when the window resizes, a sidebar toggles, or CSS Grid layout updates.                         |
| **`refresh()`**      | **Data or Styles changed** but size stayed the same. Use this if you manually modified track colors or data outside of standard API calls. |
| **`update()`**       | **Tracks added/removed.** The standard call after `setTracks()` or `addTrack()`.                                                           |

## Data Preparation (SOP)

Use this utility to transform flat "Row-based" data (common from CSV/APIs) into the "Columnar" format optimized for `GraphTrack`.

```typescript
/**
 * Transforms an array of row objects into a columnar object.
 * 
 * Input:  [{ DEPTH: 100, GR: 50 }, { DEPTH: 101, GR: 55 }]
 * Output: { GR: [[100, 50], [101, 55]] }
 * 
 * @param rows Array of row objects.
 * @param depthKey The key representing depth (e.g., 'MD' or 'DEPTH').
 * @param curveKeys Array of keys to extract as curves.
 */
export function transformRowToColumns(
  rows: Record<string, number>[],
  depthKey: string,
  curveKeys: string[]
): Record<string, [number, number][]> {
  const result: Record<string, [number, number][]> = {};
  
  // Initialize arrays
  curveKeys.forEach(key => {
    result[key] = [];
  });

  rows.forEach(row => {
    const depth = row[depthKey];
    if (typeof depth !== 'number') return; // Skip invalid depth

    curveKeys.forEach(key => {
      const value = row[key];
      // Only add valid numbers (filter nulls/undefined)
      if (typeof value === 'number' && !isNaN(value)) {
        result[key].push([depth, value]);
      }
    });
  });

  return result;
}

// Usage Example:
// const rawData = [{ MD: 100, GR: 45, RES: 2 }, { MD: 101, GR: 48, RES: 2.1 }];
// const trackData = transformRowToColumns(rawData, 'MD', ['GR', 'RES']);
//
// new GraphTrack('track', {
//   data: trackData,
//   plots: [
//      { type: 'line', options: { dataAccessor: d => d.GR } }
//   ]
// });
```

# Visual Patterns to Code Mapping

This section provides a mapping from common well-log visual patterns to the `videx-wellog` component configurations required to achieve them. Use this as a reference when translating visual requirements or mockups into code.

## Patterns

### Standard Filled Area
**Visual Description**: A curve with a solid or semi-transparent fill extending from the curve line down to the minimum value (left side) of the track.
**Key Components**: `GraphTrack`, `AreaPlot`
**Configuration Highlights**:
- `type: 'area'`
- `fill`: Sets the color of the area.
- `color`: Sets the color of the boundary line.
- `useMinAsBase: true` (default).

**Code Snippet**:
```typescript
{
  id: 'standard-area',
  type: 'area',
  options: {
    color: 'blue',       // Line color
    fill: 'lightblue',   // Area fill color
    fillOpacity: 0.8,    // Adjust transparency
    width: 1,            // Line width
  }
}
```

### Inverted Filled Area
**Visual Description**: A curve with a fill extending from the curve line *up* to the maximum value (right side) of the track. Often used for density logs or inverted scales.
**Key Components**: `GraphTrack`, `AreaPlot`
**Configuration Highlights**:
- `useMinAsBase: false`: Reverses the fill direction (fills to max instead of min).

**Code Snippet**:
```typescript
{
  id: 'inverted-area',
  type: 'area',
  options: {
    color: 'grey',
    fill: 'darkgrey',
    useMinAsBase: false, // <--- Key property
    fillOpacity: 0.7,
  }
}
```

### Dual/Differential Fill Area
**Visual Description**: A curve where the area *below* the line is one color, and the area *above* the line is a different color. The entire track width is filled.
**Key Components**: `GraphTrack`, `AreaPlot`
**Configuration Highlights**:
- `fill`: Colors the area from min to value.
- `inverseColor`: Colors the area from value to max.

**Code Snippet**:
```typescript
{
  id: 'dual-fill',
  type: 'area',
  options: {
    color: 'grey',       // Line color
    fill: 'red',         // Color below curve (min to value)
    inverseColor: 'grey',// Color above curve (value to max)
    fillOpacity: 0.8,
  }
}
```

### Differential / Crossover Plot
**Visual Description**: Two overlapping curves where the area between them is filled based on which curve has the higher value (crossover effect). Common for comparing neutron/density logs.
**Key Components**: `GraphTrack`, `DifferentialPlot`
**Configuration Highlights**:
- `type: 'differential'`
- `serie1`: Configures the first curve and the fill color when `serie1 > serie2`.
- `serie2`: Configures the second curve and the fill color when `serie2 > serie1`.
- **Data Requirement**: The `dataAccessor` (or track data) must return an array of two datasets: `[ [ [d, v], ... ], [ [d, v], ... ] ]`.

**Code Snippet**:
```typescript
{
  id: 'diff-plot',
  type: 'differential',
  options: {
    // Shared options
    fillOpacity: 0.5,
    
    // Curve 1 (e.g., Neutron)
    serie1: {
      color: 'blue',      // Line color
      fill: 'green',      // Fill when Curve 1 > Curve 2
      width: 1,
    },
    
    // Curve 2 (e.g., Density)
    serie2: {
      color: 'red',       // Line color
      fill: 'yellow',     // Fill when Curve 2 > Curve 1
      width: 1,
    },
    
    // Extract two datasets from the data object
    dataAccessor: (d) => [d.neutronCurve, d.densityCurve] 
  }
}
```

### Dot Plot
**Visual Description**: Discrete circular points. Used for sparse data or discrete sampling events.
**Key Components**: `GraphTrack`, `DotPlot`
**Configuration Highlights**:
- `type: 'dot'`
- `radius`: Sets the size of the dots (in pixels).
- `color`: Sets the fill color.

**Code Snippet**:
```typescript
{
  id: 'dot-plot',
  type: 'dot',
  options: {
    color: 'green',
    radius: 4,      // Dot size
  }
}
```

### Line Plot (Solid / Dashed)
**Visual Description**: A continuous curve connecting data points. Can be solid, dashed, or dotted.
**Key Components**: `GraphTrack`, `LinePlot`
**Configuration Highlights**:
- `type: 'line'`
- `width`: Line thickness.
- `dash`: Array defining dash pattern `[lineLength, gapLength]`.

**Code Snippet**:
```typescript
{
  id: 'line-plot',
  type: 'line',
  options: {
    color: 'black',
    width: 2,
    dash: [5, 5], // 5px line, 5px gap (dashed)
    // dash: [2, 2], // Dotted appearance
    // dash: [],     // Solid line (default)
  }
}
```

### Step Plot
**Visual Description**: A line that changes value in discrete steps (staircase effect). Useful for zoned data or digital logs.
**Key Components**: `GraphTrack`, `LineStepPlot` (Note: In `GraphTrack` config, often referred to as `type: 'line-step'` or imported class).
**Configuration Highlights**:
- `type: 'line-step'` (Check specific factory string if using factory, otherwise instantiate class).
- `width`: Line thickness.
- `dash`: Supports dash patterns like standard lines.

**Code Snippet**:
```typescript
{
  id: 'step-plot',
  type: 'line-step', // Ensure this matches your factory mapping
  options: {
    color: 'purple',
    width: 3,
    dash: [],
  }
}
```

### Tadpole / Dip Plot
**Visual Description**: Discrete symbols (tadpoles) positioned at a specific depth and dip angle, with a tail pointing in the azimuth direction. Used for structural geology.
**Key Components**: `GraphTrack`, `DipPlot`
**Configuration Highlights**:
- `type: 'dip'`
- **Data Requirement**: `[depth, dip, azimuth, { color, shape }]`.
- `domain`: Typically `[0, 90]` for dip angle.

**Code Snippet**:
```typescript
{
  id: 'dip-plot',
  type: 'dip',
  options: {
    legendInfo: () => ({ label: 'DIP', unit: 'deg' }),
  }
}
```

## Track Patterns

### Standard Graph Track (Grid)
**Visual Description**: A container track with a visible background grid (vertical and horizontal lines). Used as the canvas for plotting data curves.
**Key Components**: `GraphTrack`
**Configuration Highlights**:
- `type: 'graph'`
- `scale`: Defines grid distribution ('linear' or 'log').
- **Grid Styling**:
    - Major Lines: Hardcoded to `#ccc` (Grey).
    - Minor Lines: Hardcoded to `#ddd` (Light Grey).
    - *Note: Grid styling is currently internal and not configurable via options.*

**Code Snippet**:
```typescript
{
  id: 'track-1',
  type: 'graph',
  options: {
    scale: 'linear',  // or 'log'
    domain: [0, 100], // Range of the horizontal axis
    // majorTicksOnly: true, // Optional: Simplify grid
  },
  plots: [
    // ... plots go here ...
  ]
}
```

### Graph Track (Piecewise)
**Visual Description**: A track where the horizontal grid spacing is non-uniform or segmented (e.g., compressed in some ranges, expanded in others). Used for focusing on specific data ranges.
**Key Components**: `GraphTrack`
**Configuration Highlights**:
- `domain`: An array with **more than 2 values** (e.g., `[0, 20, 50, 100]`). This triggers the piecewise scaling logic.
- `scale`: Typically 'linear'.

**Code Snippet**:
```typescript
{
  id: 'piecewise-track',
  type: 'graph',
  options: {
    scale: 'linear',
    domain: [0, 20, 50, 100], // Defines 3 segments: 0-20, 20-50, 50-100
  },
}
```

### Graph Track (Multiple Plots)
**Visual Description**: A single track containing multiple superimposed data visualizations (e.g., a line curve overlaid on an area fill).
**Key Components**: `GraphTrack`, `plots` array
**Configuration Highlights**:
- `plots`: An array of plot configuration objects.
- **Order Matters**: Plots are rendered in array order. Put background elements (like filled areas) first, and foreground elements (like lines) last.

**Code Snippet**:
```typescript
{
  id: 'multi-plot-track',
  type: 'graph',
  options: {
    domain: [0, 100],
  },
  plots: [
    // Background: Green Area
    {
      id: 'bg-area',
      type: 'area',
      options: { color: 'green', fillOpacity: 0.3 }
    },
    // Foreground: Purple Line
    {
      id: 'fg-line',
      type: 'line',
      options: { color: 'purple', width: 2 }
    }
  ]
}
```

### Graph Track (Single Plot)
**Visual Description**: A simplified graph track containing only one curve.
**Key Components**: `GraphTrack`
**Configuration Highlights**:
- `plots`: Array with a single plot object.

**Code Snippet**:
```typescript
{
  id: 'single-plot-track',
  type: 'graph',
  options: {
    domain: [0, 100],
    scale: 'linear',
  },
  plots: [
    {
      id: 'curve',
      type: 'line',
      options: { color: 'blue', width: 2 }
    }
  ]
}
```

### Dual Scale Track
**Visual Description**: A scale track (ruler) designed to switch between two measurement units (e.g., Meters vs. Feet) or modes.
**Key Components**: `DualScaleTrack`
**Configuration Highlights**:
- `type: 'scale'` (Note: Often shares the same type string as ScaleTrack, but instantiated differently or via specific factory).
- `mode`: `0` (Master) or `1` (Slave). Used with `InterpolatedScaleHandler` to toggle domains.
- `units`: Label for the units (e.g., 'm' or 'ft').

**Code Snippet**:
```typescript
{
  id: 'dual-scale-track',
  type: 'scale', // Check factory mapping if strictly typed
  options: {
    maxWidth: 60,
    units: 'm',
    mode: 0, // 0 = Master, 1 = Slave
  }
}
```

### Scale Track
**Visual Description**: A standard ruler track showing numerical ticks (e.g., depth).
**Key Components**: `ScaleTrack`
**Configuration Highlights**:
- `type: 'scale'`
- `units`: String label for the measurement unit (e.g., 'm').
- `maxWidth`: Limit the width to prevent it from taking too much space.

**Code Snippet**:
```typescript
{
  id: 'scale-track',
  type: 'scale',
  options: {
    maxWidth: 60,
    units: 'm',
  }
}
```

### Stacked Track
**Visual Description**: A track filled with colored blocks representing intervals (e.g., geological formations, lithology). Blocks can have labels.
**Key Components**: `StackedTrack`
**Configuration Highlights**:
- `type: 'stacked'`
- **Data Requirement**: Array of boundary points (NOT intervals): `[{ depth, color, label }, ...]`.
    - Note: The library infers intervals between consecutive points.
- `data`: Function returning a Promise (Critical!).
- `showLabels`: `true` to display text labels.

**Code Snippet**:
```typescript
{
  id: 'stacked-track',
  type: 'stacked',
  options: {
    // MUST be a function returning a Promise
    data: () => Promise.resolve([
      { depth: 0, color: 'green', label: 'Layer A' },
      { depth: 100, color: 'yellow', label: 'Layer B' },
      { depth: 250, color: 'brown', label: 'Layer C' },
    ]),
    showLabels: true,
  }
}
```

### Distribution Track
**Visual Description**: A filled track showing the percentage composition of multiple components at each depth (e.g., Lithology mix of Sand, Shale, Clay). The cumulative width is typically 100%.
**Key Components**: `DistributionTrack`
**Configuration Highlights**:
- `type: 'distribution'` (or class instantiation).
- `components`: Dictionary defining color for each data key.
- `data`: Array of objects `{ depth, composition: [{ key, value }, ...] }`.
- `interpolationType`: `0` (Linear/Smooth), `1` (Nearest), `2` (Discrete/Stepped).

**Code Snippet**:
```typescript
{
  id: 'dist-track',
  type: 'distribution', // Check factory mapping
  options: {
    // Define colors for keys
    components: {
      sand: { color: 'gold' },
      shale: { color: 'grey' },
      clay: { color: 'brown' },
    },
    // Data format is specific:
    data: [
      { 
        depth: 100, 
        composition: [
          { key: 'sand', value: 80 }, 
          { key: 'shale', value: 20 }
        ]
      },
      // ...
    ],
  }
}
```

## Viewer Patterns

### Log Viewer (Single Track)
**Visual Description**: A stripped-down viewer displaying a single track (often a ScaleTrack) without any headers or legends. Used for embedding simple visuals.
**Key Components**: `LogViewer`, `ScaleTrack`.
**Configuration Highlights**:
- **Initialization**: Use `new LogViewer({ showLegend: false, showTitles: false })` instead of `LogViewer.basic(false)`.
- **Add Track**: Use `addTrack()` for a single component.

**Code Snippet**:
```typescript
// Create a viewer without titles/legend
const viewer = new LogViewer({ showLegend: false, showTitles: false });
const scaleTrack = new ScaleTrack('scale');

// Mount and initialize
viewer.addTrack(scaleTrack);
viewer.init(domElement);
```

### Log Viewer (Multiple Tracks)
**Visual Description**: A simplified layout showing multiple tracks side-by-side (e.g., a ScaleTrack + GraphTracks), suitable for compact data views.
**Key Components**: `LogViewer`, `ScaleTrack`, `GraphTrack`.
**Configuration Highlights**:
- **Initialization**: Use `new LogViewer()` (defaults to titles/legend enabled).
- **Track Layout**: Use `setTracks([...])` to arrange tracks. Supports width weights (flex layout).

**Code Snippet**:
```typescript
const viewer = new LogViewer(); // Titles enabled, Legend enabled

const tracks = [
  new ScaleTrack('scale', { maxWidth: 60 }),
  new GraphTrack('graph1', { width: 2 }),
  new GraphTrack('graph2', { width: 1 }),
];

viewer.init(div).setTracks(tracks);
```

### Log Viewer (Dual Scale & Interpolation)
**Visual Description**: Two scale tracks side-by-side displaying different units (e.g., Meters vs. Feet) or transformations. Often includes a mechanism to switch the "Master" scale.
**Key Components**: `LogViewer`, `DualScaleTrack`, `InterpolatedScaleHandler`.
**Configuration Highlights**:
- **DualScaleTrack**: Use `mode: 0` (Master) and `mode: 1` (Slave).
- **InterpolatedScaleHandler**: Replaces the default scale handler to manage domain transformations (e.g., * 2 or / 2).
- **Custom Logic**: Requires defining `forward` and `reverse` functions for the interpolator.

**Code Snippet**:
```typescript
import { DualScaleTrack, InterpolatedScaleHandler } from '@equinor/videx-wellog';

const viewer = new LogViewer();

// Define tracks for two modes
const track1 = new DualScaleTrack('scale * 2', { mode: 1 });
const track2 = new DualScaleTrack('scale / 2', { mode: 0 });

// Define transformation logic
const interpolator = {
  forward: v => v / 2,
  reverse: v => v * 2,
  forwardInterpolatedDomain: d => d.map(v => v / 2),
  reverseInterpolatedDomain: d => d.map(v => v * 2),
};

// Override default scale handler
const scaleHandler = new InterpolatedScaleHandler(interpolator, [0, 100]);
viewer.scaleHandler = scaleHandler;

viewer.init(div).setTracks(track1, track2);
```

### Log Viewer (Stacked/Cement/Formation)
**Visual Description**: A viewer featuring a StackedTrack to visualize categorical data like cement, formations, or lithology. The track displays colored blocks with optional labels.
**Key Components**: `LogViewer`, `StackedTrack`.
**Configuration Highlights**:
- **Data Source**: The `StackedTrack` requires a `data` function that returns a Promise resolving to an array of objects `{ from, to, color, name }`.
- **Labels**: `showLabels: true` (default) displays the `name` property.
- **Lines**: `showLines: true` (default) draws separators between blocks.

**Code Snippet**:
```typescript
const viewer = new LogViewer();
const scaleTrack = new ScaleTrack('scale', { maxWidth: 60 });

const formationTrack = new StackedTrack('formation', {
  // Data must be a Promise-returning function
  data: async () => [
    { from: 0, to: 100, color: 'blue', name: 'Formation A' },
    { from: 100, to: 250, color: 'green', name: 'Formation B' }
  ],
  showLabels: true,
});

viewer.init(div).setTracks([scaleTrack, formationTrack]);
```

### Log Viewer (Flag Track)
**Visual Description**: A specialized use of the StackedTrack to show boolean flags or events. Typically has no text labels and uses transparency for "off" states.
**Key Components**: `LogViewer`, `StackedTrack`.
**Configuration Highlights**:
- **Clean Look**: `showLabels: false` and `showLines: false`.
- **Transparency**: Use RGBA colors with `a: 0` for invisible segments (gaps).

**Code Snippet**:
```typescript
const flagTrack = new StackedTrack('flags', {
  data: async () => [
    // Visible flag (Pink)
    { from: 10, to: 20, color: { r: 255, g: 0, b: 255, a: 1 } },
    // Invisible gap (Transparent)
    { from: 20, to: 50, color: { r: 0, g: 0, b: 0, a: 0 } },
    // Visible flag
    { from: 50, to: 60, color: { r: 255, g: 0, b: 255, a: 1 } },
  ],
  showLabels: false, // Hide text
  showLines: false,  // Hide separators
});

viewer.init(div).setTracks([new ScaleTrack('scale'), flagTrack]);
```

### Log Viewer (Horizontal Layout)
**Visual Description**: A viewer displaying tracks horizontally (depth axis runs left-to-right).
**Key Components**: `LogViewer`, `GraphTrack`, `StackedTrack`.
**Configuration Highlights**:
- **Orientation**: Set `horizontal: true` in `LogViewer` constructor.
- **Labels**: Rotate labels for stacked tracks (`labelRotation: -90`) to fit vertical bands.

**Code Snippet**:
```typescript
const viewer = new LogViewer({
  horizontal: true, // <--- Key setting
  showLegend: true,
});

const tracks = [
  new ScaleTrack('scale', { height: 1 }),
  new GraphTrack('graph', { height: 2 }),
  // ... other tracks
];

viewer.init(div).setTracks(tracks);
```

### Log Viewer (With Legend)
**Visual Description**: A standard vertical viewer that includes a header/legend area for track titles and keys.
**Key Components**: `LogViewer`.
**Configuration Highlights**:
- **Enable Legend**: `showLegend: true` (Default in `new LogViewer()`, but disabled in `LogViewer.basic(false)`).
- **Track Config**: Ensure tracks have `legendConfig` defined if they need custom headers.

**Code Snippet**:
```typescript
const viewer = new LogViewer({
  showLegend: true, // Enable header area
  // horizontal: false (default)
});

const tracks = createTracks(); // Assume tracks have legendConfig set
viewer.init(div).setTracks(tracks);
```

## Controller Patterns

### Standard Log Controller
**Visual Description**: A full layout orchestrator that manages multiple tracks side-by-side (or stacked vertically if horizontal), handling synchronized zooming, scrolling, titles, and legends.
**Key Components**: `LogController`, `ScaleTrack`, `GraphTrack`, etc.
**Configuration Highlights**:
- **Role**: It acts as the "Parent" container.
- `setTracks(tracks)`: Accepts an array of Track instances.
- **Layout Options**:
    - `horizontal`: `false` (Vertical log, tracks side-by-side) or `true` (Horizontal log, tracks stacked).
    - `showTitles`: Toggle track headers.
    - `showLegend`: Toggle legends.

**Code Snippet**:
```typescript
// 1. Create the controller
const controller = new LogController({
  showLegend: true,
  showTitles: true,

