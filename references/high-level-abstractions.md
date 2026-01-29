# High-Level Abstractions & Utilities

This document provides helper classes and functions that simplify the usage of `videx-wellog`, effectively acting as a "Standard Library" or "Plugin System" on top of the core library.

Use these abstractions when you want to reduce boilerplate code for common tasks like Readouts, simplified Track creation, or automatic legends.

## Readout Plugin (Auto-Binding)

A high-level controller that automatically subscribes to mouse events and updates a DOM element with values from multiple tracks. This replaces the manual `viewer.overlay.create` boilerplate.

### Usage

```typescript
import { LogViewer, Track } from '@equinor/videx-wellog';
import { getTrackValueAt } from './my-utils'; // See Track Value Accessor below

// 1. Define the Plugin Class (Copy this into your project utilities)
export class ReadoutPlugin {
  private viewer: LogViewer;
  private target: HTMLElement | null;
  private tracks: Track[];
  private template: (depth: number, values: Record<string, any>) => string;
  private overlayId: string;

  constructor(
    viewer: LogViewer,
    options: {
      target: string | HTMLElement;
      tracks?: Track[];
      template?: (depth: number, values: Record<string, any>) => string;
    }
  ) {
    this.viewer = viewer;
    this.tracks = options.tracks || [];
    this.target = typeof options.target === 'string' 
      ? document.querySelector(options.target) 
      : options.target;
    
    // Default template if none provided
    this.template = options.template || ((depth, values) => {
      const rows = Object.entries(values)
        .map(([key, val]) => `<div><b>${key}:</b> ${typeof val === 'number' ? val.toFixed(2) : val}</div>`)
        .join('');
      return `<div><strong>Depth: ${depth.toFixed(2)}</strong></div>${rows}`;
    });

    this.overlayId = `readout-${Math.random().toString(36).substr(2, 9)}`;
    this.init();
  }

  private init() {
    if (!this.target) {
      console.warn('ReadoutPlugin: Target element not found');
      return;
    }

    this.viewer.overlay.create(this.overlayId, {
      onMouseMove: (event) => {
        const { x, y, caller } = event;
        const scale = caller.scale;
        const isHorizontal = caller.options.horizontal;
        const depth = isHorizontal ? scale.invert(x) : scale.invert(y);

        // Collect values from tracks
        const values: Record<string, any> = {};
        
        this.tracks.forEach(track => {
          const val = getTrackValueAt(track, depth);
          if (val !== null && val !== undefined) {
             values[track.id] = val;
          }
        });

        this.target!.innerHTML = this.template(depth, values);
        this.target!.style.display = 'block';
      },
      onMouseExit: () => {
        if (this.target) this.target.style.display = 'none';
      }
    });
  }
}

// 2. Implementation
const viewer = new LogViewer();
const grTrack = new GraphTrack('gr', { ... });

// Initialize Plugin
const readout = new ReadoutPlugin(viewer, {
  target: '#readout-panel',
  tracks: [grTrack],
  template: (depth, values) => `GR: ${values.gr?.toFixed(1)} API`
});
```

## Simplified Track Factory

A helper function to create `GraphTrack` instances with less nesting.

### Usage

```typescript
import { GraphTrack, graphLegendConfig, StackedTrack } from '@equinor/videx-wellog';
import { rgb } from 'd3-color';

/**
 * Parses a CSS color string (Hex, Name, RGB) into an {r, g, b, a} object.
 * This is REQUIRED for StackedTrack as it does not support string colors.
 */
export function parseColor(colorStr: string) {
  const c = rgb(colorStr);
  return { r: c.r, g: c.g, b: c.b, a: c.opacity };
}

interface SimpleTrackConfig {
  id: string;
  data: any[]; // Array or Columnar object
  plotType?: 'line' | 'area' | 'dot' | 'stacked'; // Added 'stacked'
  color?: string;
  label?: string;
  unit?: string;
  domain?: [number, number];
  scale?: 'linear' | 'log';
}

/**
 * Creates a GraphTrack or StackedTrack with a simplified config.
 */
export function createSimpleTrack(config: SimpleTrackConfig): GraphTrack | StackedTrack {
  const { 
    id, data, plotType = 'line', color = 'black', 
    label, unit, domain, scale = 'linear' 
  } = config;

  if (plotType === 'stacked') {
    return new StackedTrack(id, {
      label: label || id,
      data: async () => {
        const rawData = typeof data === 'function' ? await data() : data;
        // Ensure colors are parsed for StackedTrack
        return rawData.map(d => ({
          ...d,
          color: typeof d.color === 'string' ? parseColor(d.color) : d.color
        }));
      }
    });
  }

  return new GraphTrack(id, {
    label: label || id,
    scale,
    domain: domain || [0, 100], // Default domain
    data,
    legendConfig: graphLegendConfig, // Auto-enable legend config
    plots: [
      {
        id: `${id}-plot`,
        type: plotType as any,
        options: {
          color,
          // Auto-generate legend info if label/unit provided
          legendInfo: (label || unit) 
            ? () => ({ label: label || id, unit: unit || '' }) 
            : undefined
        }
      }
    ]
  });
}

/**
 * Validates if the container element is suitable for LogViewer initialization.
 * Checks for existence, visibility, and non-zero dimensions.
 * 
 * ⚠️ CRITICAL: LogViewer captures size at init(). If initialized at 0px, 
 * it will NOT self-correct later.
 * 
 * @param el The DOM element to check.
 * @returns true if valid, false otherwise.
 */
export function validateContainer(el: HTMLElement | null): boolean {
  if (!el) {
    console.error('[wellog-viz] Container element is null or undefined.');
    return false;
  }

  const rect = el.getBoundingClientRect();
  const hasSize = rect.width > 0 && rect.height > 0;
  const isVisible = window.getComputedStyle(el).display !== 'none';

  if (!hasSize || !isVisible) {
    console.error(
      `[wellog-viz] Invalid container dimensions: ${rect.width}x${rect.height}. ` +
      `Ensure the element is visible and has a defined pixel height/width before calling init().`
    );
    return false;
  }

  return true;
}

/**
 * Enhanced LogViewer initialization that waits for the container to have dimensions.
 * Use this to prevent the "zero-size init" bug.
 */
export async function waitAndInit(viewer: any, container: HTMLElement): Promise<void> {
  return new Promise((resolve) => {
    const check = () => {
      if (validateContainer(container)) {
        viewer.init(container);
        resolve();
        return true;
      }
      return false;
    };

    // Try immediately
    if (check()) return;

    // Wait for size change if initially 0
    const observer = new ResizeObserver(() => {
      if (check()) observer.disconnect();
    });
    observer.observe(container);
  });
}

/**
 * Initializes a LogViewer asynchronously, ensuring the DOM is ready.
...
 * Returns a Promise that resolves to the viewer instance.
 * 
 * @param viewer The LogViewer instance.
 * @param container The DOM element to mount into.
 */
export function initLogViewer(
  viewer: LogViewer, 
  container: HTMLElement | null
): Promise<LogViewer> {
  return new Promise((resolve, reject) => {
    if (!container) {
      reject(new Error('LogViewer Init Error: Container element is null.'));
      return;
    }

    requestAnimationFrame(() => {
      try {
        viewer.init(container);
        resolve(viewer);
      } catch (e) {
        reject(e);
      }
    });
  });
}

// Example
// await initLogViewer(viewer, div);
// viewer.overlay.create(...); // Safe now

/**
 * A generalized mount function that handles RAF and cleanup.
 * Useful for non-React environments or custom framework integrations.
 * 
 * @param container The DOM element.
 * @param options LogViewer options.
 * @returns Object containing the viewer instance and a cleanup function.
 */
export function mountLogViewer(container: HTMLElement, options: any = {}) {
  const viewer = new LogViewer(options);
  let rafId: number;

  const promise = new Promise<LogViewer>((resolve, reject) => {
    rafId = requestAnimationFrame(() => {
      try {
        viewer.init(container);
        resolve(viewer);
      } catch (e) {
        reject(e);
      }
    });
  });

  return {
    viewer,
    ready: promise,
    dispose: () => {
      cancelAnimationFrame(rafId);
      // Clean up DOM if needed, though usually handled by framework
      if (container) container.innerHTML = '';
    }
  };
}

// Example
const track = createSimpleTrack({
  id: 'gr',
  data: [[0, 10], [100, 50]],
  color: 'green',
  label: 'Gamma Ray',
  unit: 'API'
});

/**
 * Helper to create a data accessor for Row-Oriented Data.
 * Extracts a specific key from an array of objects and maps it to [depth, value].
 * ⚠️ IMPORTANT: The order is [Depth, Value], NOT [Value, Depth].
 * 
 * @param key The key in the row object to extract as value.
 * @param depthKey The key in the row object representing depth (default: 'depth').
 */
export function createRowAccessor(key: string, depthKey: string = 'depth') {
  return (data: any[]) => {
    if (!Array.isArray(data)) return [];
    return data
      .map((row) => {
        const d = row[depthKey];
        const v = row[key];
        return (typeof d === 'number' && typeof v === 'number') ? [d, v] : null;
      })
      .filter((p): p is [number, number] => p !== null);
  };
}

// Example:
// const data = [{ depth: 100, gr: 50 }, { depth: 101, gr: 55 }];
// plots: [{ 
//   id: 'gr', 
//   type: 'line', 
//   options: { 
//     dataAccessor: createRowAccessor('gr') 
//   } 
// }]

## Declarative Track Layout (TrackBuilder / LayoutConfig)

For complex well-log layouts with many tracks, manually instantiating each `GraphTrack` or `StackedTrack` can become verbose and error-prone. A declarative approach, where the layout is defined by a simple JSON configuration, can significantly reduce boilerplate and improve maintainability.

This pattern involves:
1.  **Defining a Layout Configuration**: An array of objects, where each object describes a track (its type, data, plots, etc.).
2.  **A Factory Function (`createTrackFromConfig`)**: This function takes a single track configuration object and returns the corresponding `Track` instance (`GraphTrack`, `StackedTrack`, `ScaleTrack`, etc.).

### Example Layout Configuration

```typescript
// layout.ts
export const complexWellLayout = [
  {
    type: 'scale',
    id: 'depth-scale',
    options: { maxWidth: 60 },
  },
  {
    type: 'graph',
    id: 'gamma-ray',
    label: 'GR',
    data: { GR: [[100, 50], [200, 70]] }, // Example columnar data
    plots: [
      {
        id: 'gr-plot',
        type: 'line',
        options: { color: 'green', dataAccessor: d => d.GR, legendInfo: () => ({ label: 'GR', unit: 'API' }) },
      },
    ],
    domain: [0, 150],
    scale: 'linear',
  },
  {
    type: 'stacked',
    id: 'lithology',
    label: 'Lithology',
    data: [ // Example stacked data
      { depth: 100, color: 'red', label: 'Sand' },
      { depth: 200, color: 'blue', label: 'Shale' },
    ],
    options: { showLabels: true },
  },
  // ... more tracks
];
```

### Conceptual `createTrackFromConfig` Function

This is a conceptual example. A full implementation would handle all track types and their specific options.

```typescript
// utils/track-builder.ts
import { GraphTrack, StackedTrack, ScaleTrack, Track } from '@equinor/videx-wellog';

interface PlotConfig {
  id: string;
  type: 'line' | 'area' | 'dip' | 'differential';
  options: any;
}

interface TrackConfig {
  type: 'scale' | 'graph' | 'stacked';
  id: string;
  label?: string;
  data?: any; // For GraphTrack or StackedTrack
  plots?: PlotConfig[]; // For GraphTrack
  domain?: [number, number]; // For GraphTrack
  scale?: 'linear' | 'log'; // For GraphTrack
  options?: any; // General options for any track type
}

/**
 * Factory function to create a Track instance from a configuration object.
 * @param config The track configuration object.
 * @returns A Track instance.
 */
export function createTrackFromConfig(config: TrackConfig): Track {
  switch (config.type) {
    case 'scale':
      return new ScaleTrack(config.id, config.options);
    case 'graph':
      return new GraphTrack(config.id, {
        label: config.label || config.id,
        data: config.data,
        plots: config.plots?.map(plot => ({
          id: plot.id,
          type: plot.type,
          options: plot.options,
        })),
        domain: config.domain,
        scale: config.scale,
        ...config.options, // Merge additional options
      });
    case 'stacked':
      // Ensure data is wrapped in a Promise-returning function for StackedTrack
      const stackedData = Array.isArray(config.data) 
        ? () => Promise.resolve(config.data) 
        : config.data;
      return new StackedTrack(config.id, {
        label: config.label || config.id,
        data: stackedData,
        ...config.options, // Merge additional options
      });
    default:
      throw new Error(`Unknown track type: ${config.type}`);
  }
}

// Usage:
// import { complexWellLayout } from './layout';
// import { createTrackFromConfig } from './utils/track-builder';
//
// const tracks = complexWellLayout.map(createTrackFromConfig);
// viewer.setTracks(...tracks);
```

## Auto-Legend Helper

A utility to automatically inject `legendInfo` into plot options based on the plot ID or data keys.

### Usage

```typescript
import { PlotOptions } from '@equinor/videx-wellog';

/**
 * Wraps plot options to automatically add legendInfo.
 */
export function withAutoLegend(
  id: string, 
  unit: string, 
  options: any
): any {
  return {
    ...options,
    legendInfo: () => ({ label: id.toUpperCase(), unit })
  };
}

// Example inside GraphTrack
const track = new GraphTrack('track', {
  plots: [
    {
      id: 'cali',
      type: 'line',
      options: withAutoLegend('cali', 'in', { color: 'black', dash: [5, 5] })
    }
  ]
});
```

## Track Value Accessor

A robust utility to retrieve the data value at a specific depth for various track types (`GraphTrack`, `StackedTrack`, `DistributionTrack`). This normalizes the differences in data structures.

### Usage

```typescript
import { Track } from '@equinor/videx-wellog';

/**
 * Retrieves the value/label at a specific depth for a given track.
 * Supports:
 * - GraphTrack: Interpolated or nearest value from array data.
 * - StackedTrack: Label or Name of the interval.
 * - DistributionTrack: Composition object at depth.
 * 
 * @param track The track instance.
 * @param depth The depth to query.
 * @param threshold The maximum depth distance to consider a match (for point data).
 */
export function getTrackValueAt(track: any, depth: number, threshold: number = 0.5): any {
  if (!track || !track.data) return null;
  const data = track.data;

  // 1. Handle StackedTrack (Intervals: { from, to, label/name })
  if (track.type === 'stacked' || (Array.isArray(data) && data[0] && 'from' in data[0])) {
    const interval = data.find((d: any) => depth >= d.from && depth <= d.to);
    return interval ? (interval.label || interval.name) : null;
  }

  // 2. Handle DistributionTrack (Points: { depth, composition })
  if (track.type === 'distribution' || (Array.isArray(data) && data[0] && 'composition' in data[0])) {
    // Find nearest
    const item = data.find((d: any) => Math.abs(d.depth - depth) < threshold);
    return item ? item.composition : null;
  }

  // 3. Handle GraphTrack (Array of [depth, value])
  // Note: This assumes standard array format. Custom dataAccessors might require custom logic.
  if (Array.isArray(data)) {
    // Check for standard [depth, value] pair
    if (Array.isArray(data[0]) && data[0].length === 2) {
       const item = data.find((d: any) => Math.abs(d[0] - depth) < threshold);
       return item ? item[1] : null;
    }
    // Check for object { depth, value }
    if (data[0] && 'depth' in data[0]) {
       const item = data.find((d: any) => Math.abs(d.depth - depth) < threshold);
       // Return the first non-depth value found
       if (item) {
         const keys = Object.keys(item).filter(k => k !== 'depth');
         return keys.length === 1 ? item[keys[0]] : item;
       }
    }
  }

  return null;
}
```

## Wide Data Splitter

A utility to split a "Wide Table" array (single array with multiple columns) into multiple independent `[depth, value]` arrays. This is crucial for avoiding crashes in `GraphTrack`.

### Usage

```typescript
/**
 * Splits a wide table array into a columnar object of [depth, value] arrays.
 * 
 * Input:  [[100, 10, 20], [101, 11, 21]] (Assumes [depth, curve1, curve2])
 * Output: { curve1: [[100, 10], [101, 11]], curve2: [[100, 20], [101, 21]] }
 * 
 * @param data The wide array of arrays.
 * @param keys An array of keys corresponding to the columns (skipping depth).
 *             e.g. ['deep', 'shallow'] for columns 1 and 2.
 * @param depthIndex The index of the depth column (default: 0).
 */
export function splitWideData(
  data: number[][], 
  keys: string[], 
  depthIndex: number = 0
): Record<string, [number, number][]> {
  const result: Record<string, [number, number][]> = {};
  keys.forEach(k => result[k] = []);

  data.forEach(row => {
    const depth = row[depthIndex];
    let colIndex = 0;
    
    // Iterate through the row, skipping depth index
    row.forEach((val, idx) => {
      if (idx === depthIndex) return;
      
      const key = keys[colIndex];
      if (key) {
        result[key].push([depth, val]);
      }
      colIndex++;
    });
  });

  return result;
}

// Example:
// const wideData = [
//   [1000, 10, 50], 
//   [1001, 12, 55]
// ];
// const columns = splitWideData(wideData, ['res_deep', 'res_shallow']);
//
// const track = new GraphTrack('res', {
//   plots: [
//     { 
//       id: 'deep', 
//       type: 'line', 
//       options: { data: columns.res_deep } // Safe!
//     },
//     { 
//       id: 'shallow', 
//       type: 'line', 
//       options: { data: columns.res_shallow } // Safe!
//     }
//   ]
// });
```

## React Hook (useLogViewer)

A custom Hook that encapsulates the complex initialization logic required for React, including `requestAnimationFrame` handling, StrictMode double-invocation protection, and cleanup.

### Usage

```typescript
import { useEffect, useRef, useState } from 'react';
import { LogViewer } from '@equinor/videx-wellog';

/**
 * A React Hook to safely initialize and manage a LogViewer instance.
 * 
 * @param containerRef Ref to the container DOM element.
 * @param options LogViewer constructor options.
 * @returns The initialized LogViewer instance, or null if not yet ready.
 */
export function useLogViewer(
  containerRef: React.RefObject<HTMLElement>,
  options: any = {}
): LogViewer | null {
  const viewerRef = useRef<LogViewer | null>(null);
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    if (!containerRef.current) return;

    // Guard: Prevent double-init in StrictMode
    if (viewerRef.current) return;

    // 1. Instantiate
    const viewer = new LogViewer(options);
    viewerRef.current = viewer;

    let rafId: number;
    let mounted = true;

    // 2. Async Init
    rafId = requestAnimationFrame(() => {
      if (!mounted || !containerRef.current) return;

      try {
        // Height check warning
        if (containerRef.current.clientHeight === 0) {
          console.warn('LogViewer initialized on zero-height element. It may be invisible.');
        }

        viewer.init(containerRef.current);
        setIsReady(true);
      } catch (e) {
        console.error('LogViewer Init Failed:', e);
      }
    });

    // 3. Cleanup
    return () => {
      mounted = false;
      cancelAnimationFrame(rafId);
      
      // Clear DOM
      if (containerRef.current) {
        containerRef.current.innerHTML = '';
      }
      viewerRef.current = null;
      setIsReady(false);
    };
  }, [containerRef]); // Re-run only if container ref changes (rare)

  return isReady ? viewerRef.current : null;
}

/**
 * A React Hook to add responsive resizing capability to an existing LogViewer.
 */
export function useResponsiveViewer(
  containerRef: React.RefObject<HTMLElement>,
  viewer: LogViewer | null
) {
  useEffect(() => {
    const el = containerRef.current;
    if (!el || !viewer) return;

    const observer = new ResizeObserver(() => {
      viewer.adjustToSize();
    });

    observer.observe(el);
    return () => observer.disconnect();
  }, [containerRef, viewer]);
}

/**
 * Attaches a persistent resize observer for Vanilla JS environments.
 * @returns A cleanup function to stop observing.
 */
export function createResponsiveViewer(
  container: HTMLElement,
  viewer: LogViewer
): () => void {
  const observer = new ResizeObserver(() => {
    viewer.adjustToSize();
  });
  observer.observe(container);
  return () => observer.disconnect();
}

// Example Component
// const MyLog = () => {
//   const ref = useRef(null);
//   const viewer = useLogViewer(ref, { showLegend: true });
//
//   useEffect(() => {
//     if (viewer) {
//       viewer.setTracks([...]); // Safe to use
//     }
//   }, [viewer]);
//
//   return <div ref={ref} style={{ height: '500px' }} />;
// };
```

## Safe Zoom Helper

A wrapper for `zoomTo` that checks if the requested range is within the configured domain, preventing "flying view" issues.

### Usage

```typescript
import { LogViewer } from '@equinor/videx-wellog';

/**
 * Safely zooms the viewer to a range, warning if out of bounds.
 * 
 * @param viewer The LogViewer instance.
 * @param range The [min, max] depth range to zoom to.
 */
export function safeZoomTo(viewer: LogViewer, range: [number, number]): void {
  const domain = viewer.options.domain || [0, 1000];
  const [min, max] = domain;
  const [zMin, zMax] = range;

  if (zMin < min || zMax > max) {
    console.warn(
      `Zoom range [${zMin}, ${zMax}] is outside the configured domain [${min}, ${max}]. ` +
      `Interaction may be unstable. Update the domain in the LogViewer constructor.`
    );
  }

  viewer.zoomTo(range);
}
```

## StackedTrack Helper (Auto-Promise)

A factory to create `StackedTrack` instances that automatically wraps the data array in a Promise, preventing the common "data is not a function" error.

### Usage

```typescript
import { StackedTrack } from '@equinor/videx-wellog';

/**
 * Creates a StackedTrack where data can be a static array OR a promise.
 */
export function createStackedTrack(
  id: string,
  options: any
): StackedTrack {
  const { data, ...rest } = options;

  // Auto-wrap array in a Promise-returning function
  const safeData = Array.isArray(data) 
    ? () => Promise.resolve(data) 
    : data;

  return new StackedTrack(id, {
    ...rest,
    data: safeData
  });
}

// Example:
// const track = createStackedTrack('formation', {
//   data: [ // Just pass the array!
//     { from: 0, to: 100, color: 'red', name: 'A' }
//   ],
//   showLabels: true
// });
```

## Data Integrity & Validation Helpers

### Coordinate Order Validator

A utility to detect if your data is likely in the wrong order (`[Value, Depth]` instead of `[Depth, Value]`). This is the most common cause of "compressed" or broken plots.

```typescript
/**
 * Validates the coordinate order of a dataset.
 * Heuristic: If the first value (Depth) varies much less than the second (Value), 
 * or if the first value range is much smaller than the domain while the second is large,
 * it warns the developer.
 * 
 * @param data Array of [d, v] pairs.
 * @param trackId For logging purposes.
 */
export function validateDataOrder(data: [number, number][], trackId: string = 'unknown'): void {
  if (!data || data.length < 2) return;

  const firstVals = data.map(p => p[0]);
  const secondVals = data.map(p => p[1]);

  const min1 = Math.min(...firstVals);
  const max1 = Math.max(...firstVals);
  const range1 = max1 - min1;

  const min2 = Math.min(...secondVals);
  const max2 = Math.max(...secondVals);
  const range2 = max2 - min2;

  // Heuristic: In well logs, Depth range (range1) is usually significantly 
  // larger than the data value range (range2), especially for deep wells.
  // If range2 > range1 * 10 AND range1 is very small (e.g., < 100 while depth is 3000+),
  // it's almost certainly swapped.
  if (range2 > range1 * 5 && range1 < 500) {
    console.warn(
      `[wellog-viz] Potential Coordinate Order Swap detected in track "${trackId}". \n` +
      `Expected [Depth, Value], but found first-column range (${range1}) to be much \n` +
      `smaller than second-column range (${range2}). \n` +
      `Ensure your dataAccessor returns [Depth, Value].`
    );
  }
}

/**
 * Validates if the DOM container has non-zero dimensions.
 * SVG/Canvas components will collapse if the parent height is 0.
 * 
 * @param container The DOM element to be used for LogViewer.init()
 */
export function validateContainer(container: HTMLElement | null): boolean {
  if (!container) {
    console.error('[wellog-viz] Validation Error: Container element is null.');
    return false;
  }

  const { clientWidth, clientHeight } = container;
  
  if (clientHeight <= 0) {
    console.warn(
      `[wellog-viz] Runtime Warning: Container height is ${clientHeight}px. \n` +
      `The visualization will be INVISIBLE. Ensure the container has an \n` +
      `explicit CSS height (e.g., style="height: 500px").`
    );
  }

  if (clientWidth <= 0) {
    console.warn(`[wellog-viz] Runtime Warning: Container width is ${clientWidth}px.`);
  }

  return clientHeight > 0 && clientWidth > 0;
}

## Geologic Palette Utilities

### SY/T 5751 Standard Colors

A helper to retrieve standardized geologic colors without hardcoding hex values.

```typescript
export const SYT5751 = {
  'CONG': '#FFD700', // 1.1 Conglomerate
  'SAND': '#FFFF00', // 2.1 Sandstone
  'SILT': '#FFFFE0', // 3.1 Siltstone
  'SHALE': '#BEBEBE',// 4.1 Mudstone
  'LIME': '#0000FF', // 5.1 Limestone
  'DOLO': '#A52A2A', // 6.1 Dolomite
  'COAL': '#000000', // 7.1 Coal
};

/**
 * Helper to get geologic color by standard code or mnemonic.
 * @param key Standard code (e.g., '2.1') or mnemonic (e.g., 'SAND').
 */
export function getGeoColor(key: string): string {
  const palette: Record<string, string> = {
    '1.1': '#FFD700', 'CONG': '#FFD700',
    '2.1': '#FFFF00', 'SAND': '#FFFF00',
    '3.1': '#FFFFE0', 'SILT': '#FFFFE0',
    '4.1': '#BEBEBE', 'SHALE': '#BEBEBE',
    '5.1': '#0000FF', 'LIME': '#0000FF',
    '6.1': '#A52A2A', 'DOLO': '#A52A2A',
    '7.1': '#000000', 'COAL': '#000000',
  };
  return palette[key.toUpperCase()] || '#FFFFFF';
}
```

## Multi-Segment / Lithology Plot Helpers

### Segmented Plot Factory

To avoid creating dozens of `Plot` instances for different rock types, use a factory to pre-process segmented data into a single track with multiple plots, or use a custom data accessor that handles segment filtering.

```typescript
/**
 * Creates a list of AreaPlots for a segmented dataset.
 * Each segment (e.g., Sand, Shale) gets its own plot instance for color/pattern.
 * 
 * @param data Array of segments: { from, to, type, value }
 * @param palette Color mapping object.
 */
export function createSegmentedPlots(
  data: { from: number; to: number; type: string; value: number }[],
  palette: Record<string, string>
) {
  const types = [...new Set(data.map(d => d.type))];
  
  return types.map(type => ({
    id: `litho-${type}`,
    type: 'area',
    options: {
      fill: palette[type] || '#ccc',
      // Filter data for this specific rock type
      data: data
        .filter(d => d.type === type)
        .flatMap(d => [[d.from, d.value], [d.to, d.value]]),
    }
  }));
}
```
```
