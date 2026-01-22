# Best Practices & Troubleshooting

This document contains Standard Operating Procedures (SOPs), common pitfalls, and troubleshooting guides for `videx-wellog`.

## Table of Contents
- [Common Pitfalls](#common-pitfalls)
- [TypeScript & Build Configuration](#typescript--build-configuration)
- [Robust Initialization (SOP)](#robust-initialization-sop)
- [Data Preparation (SOP)](#data-preparation-sop)

## Common Pitfalls

- **Resize Method**: The `LogViewer` does **not** have a `.resize()` method. Do not attempt to call `viewer.resize()`. The viewer handles resizing automatically or requires re-initialization logic depending on the wrapper.
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
        - **Correct**: `options: { dataAccessor: d => d.map(r => [r.depth, r.gr]) }` (Expensive!)
        - **Better**: Transform data to columnar format first (see [Data Preparation](#data-preparation-sop)).
    - **Wide Table Array Warning**: Do NOT use "Wide Tables" (arrays where each row is `[depth, val1, val2, ...]`) directly with `dataAccessor`. The `LinePlot` component may fail to process these correctly, leading to crashes or blank screens.
        - **Risk**: Passing `[[depth, v1, v2], ...]` and using `dataAccessor: d => d.map(r => [r[0], r[1]])` is fragile.
        - **Solution**: Always split wide tables into independent `[depth, value]` arrays BEFORE passing them to the track. See `splitWideData` in High-Level Abstractions.
- **Zooming**: The `viewer.zoomTo()` method expects a **single array argument** `[min, max]`.
    - **Correct**: `viewer.zoomTo([3800, 4200])`
    - **Incorrect**: `viewer.zoomTo(3800, 4200)` (Throws "domain is not iterable").
- **StackedTrack Data**:
    - **Promise Required (CRITICAL)**: The `data` property **MUST** be a function that returns a Promise resolving to the data array.
        - **Incorrect**: `data: myDataArray` (Throws `TypeError: options.data is not a function`).
        - **Correct**: `data: () => Promise.resolve(myDataArray)`
    - **Data Format**: Expects a sequence of **boundary points**, not intervals. `[{ depth: 100, color: 'red' }, { depth: 200, color: 'blue' }]`.
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
    -   *Constraint*: Must be called BEFORE setting tracks or accessing overlay.
4.  **Configure**: Call `viewer.setTracks(...)` or `viewer.addTrack(...)`.
5.  **Interact**: Access `viewer.overlay` or call `viewer.zoomTo(...)`.

**Common Errors & Causes:**

| Error Message                                                       | Cause                                                                                                |
| :------------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------- |
| `Cannot read properties of null (reading 'node')`                   | Calling `setTracks()` before `init()`. The viewer tries to render tracks to a non-existent DOM node. |
| `TypeError: Cannot read properties of undefined (reading 'create')` | Accessing `viewer.overlay` before `init()`. The overlay system is initialized *inside* `init()`.     |
| `LogViewer Init Error: Container element is null`                   | Passing a null reference to `init()`.                                                                |

**Correct Pattern:**

```typescript
// 1. Construct
const viewer = new LogViewer();

// 2. Wait for DOM (Mount)
requestAnimationFrame(() => {
  const container = document.getElementById('log-container');
  
  // 3. Init
  viewer.init(container);
  
  // 4. Configure (Set Tracks)
  viewer.setTracks([scaleTrack, graphTrack]);
  
  // 5. Interact (Overlay/Zoom)
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

## Robust Initialization (SOP)

Use this pattern to avoid blank screens caused by initializing on hidden/zero-height elements or before the DOM is ready.

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
