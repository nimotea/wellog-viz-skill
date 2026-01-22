# High-Level Abstractions & Utilities

This document provides helper classes and functions that simplify the usage of `videx-wellog`, effectively acting as a "Standard Library" or "Plugin System" on top of the core library.

Use these abstractions when you want to reduce boilerplate code for common tasks like Readouts, simplified Track creation, or automatic legends.

## Readout Plugin (Auto-Binding)

A high-level controller that automatically subscribes to mouse events and updates a DOM element with values from multiple tracks. This replaces the manual `viewer.overlay.create` boilerplate.

### Usage

```typescript
import { LogViewer, Track } from '@equinor/videx-wellog';

// 1. Define the Plugin Class (Copy this into your project utilities)
export class ReadoutPlugin {
  private viewer: LogViewer;
  private target: HTMLElement | null;
  private tracks: Track[];
  private template: (depth: number, values: Record<string, number>) => string;
  private overlayId: string;

  constructor(
    viewer: LogViewer,
    options: {
      target: string | HTMLElement;
      tracks?: Track[];
      template?: (depth: number, values: Record<string, number>) => string;
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
        .map(([key, val]) => `<div><b>${key}:</b> ${val.toFixed(2)}</div>`)
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
        const values: Record<string, number> = {};
        
        this.tracks.forEach(track => {
          // Heuristic: Check if track has a data lookup method or expose raw data
          // Note: This requires tracks to have accessible data. 
          // For GraphTrack, we might need to search the data array.
          // This is a simplified example assuming a findValueAt helper exists or data is accessible.
          const val = this.findValueAt(track, depth);
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

  // Helper to find value in a track (Naive implementation for GraphTrack)
  private findValueAt(track: any, depth: number): number | null {
    if (!track.data) return null;
    
    // Handle GraphTrack (Array of [depth, value])
    if (Array.isArray(track.data)) {
      // Simple binary search or find (Optimized version needed for production)
      // This assumes sorted data
      const item = track.data.find((d: any) => Math.abs(d[0] - depth) < 0.5);
      return item ? item[1] : null;
    }
    
    // Handle Columnar Data (Object of arrays)
    // Needs specific knowledge of which curve to pick. 
    // This example assumes 'data' is the array for simplicity.
    return null;
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
