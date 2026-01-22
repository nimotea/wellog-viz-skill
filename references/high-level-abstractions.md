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
import { GraphTrack, graphLegendConfig } from '@equinor/videx-wellog';

interface SimpleTrackConfig {
  id: string;
  data: any[]; // Array or Columnar object
  plotType?: 'line' | 'area' | 'dot'; // Default 'line'
  color?: string;
  label?: string;
  unit?: string;
  domain?: [number, number];
  scale?: 'linear' | 'log';
}

/**
 * Creates a GraphTrack with a single plot using a simplified config.
 */
export function createSimpleTrack(config: SimpleTrackConfig): GraphTrack {
  const { 
    id, data, plotType = 'line', color = 'black', 
    label, unit, domain, scale = 'linear' 
  } = config;

  return new GraphTrack(id, {
    label: label || id,
    scale,
    domain: domain || [0, 100], // Default domain
    data,
    legendConfig: graphLegendConfig, // Auto-enable legend config
    plots: [
      {
        id: `${id}-plot`,
        type: plotType,
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
 * Initializes a LogViewer asynchronously, ensuring the DOM is ready.
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
