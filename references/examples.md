# Well-Log Visualization Examples

This file contains code snippets for common `videx-wellog` usage patterns.

## Basic Log Viewer with Single Track

```typescript
import '@equinor/videx-wellog/dist/styles/styles.css'; // Essential!
import { ScaleTrack, LogViewer } from '@equinor/videx-wellog';

const div = document.createElement('div');
div.style.width = '100px';
div.style.height = '500px'; // ⚠️ CRITICAL: Container MUST have an explicit height!

const scaleTrack = new ScaleTrack('scale');
// AVOID LogViewer.basic(false) as it may return a limited instance.
// Use new LogViewer with explicit options instead.
const viewer = new LogViewer({ showLegend: false, showTitles: false });

// Ensure div is attached to DOM before init21→requestAnimationFrame(() => {
22→  viewer.init(div).addTrack(scaleTrack);
23→  // viewer.refresh(); // Optional: setTracks/addTrack handles updates automatically
24→});
});
```

## Log Viewer with Multiple Tracks

```typescript
import '@equinor/videx-wellog/dist/styles/styles.css';
import { ScaleTrack, GraphTrack, LogViewer } from '@equinor/videx-wellog';

const div = document.createElement('div');
div.style.width = '500px';
div.style.height = '500px'; // ⚠️ CRITICAL: Container MUST have an explicit height!

const scaleTrack = new ScaleTrack('scale', { maxWidth: 60 });
const graphTrack1 = new GraphTrack('graph1', { 
  width: 2,
  data: [[100, 10], [200, 20], [300, 15]], // Simple array data
  scale: 'linear',
  domain: [0, 50],
  plots: [
    {
      id: 'myLine',
      type: 'line', // MUST be a string 'line', not new LinePlot()
      options: {
        color: 'red',
        width: 2,
      }
    }
  ]
});
const graphTrack2 = new GraphTrack('graph2', {
  // Data as object requires dataAccessor
  data: {
    datasetA: [[100, 5], [200, 15]],
    datasetB: [[100, 25], [200, 35]]
  },
  scale: 'linear',
  domain: [0, 50],
  plots: [
    {
      id: 'plotA',
      type: 'line',
      options: {
        color: 'blue',
        // dataAccessor receives the entire `data` object/array from the track.
        // It MUST return a coordinate array in the format [[depth, value], ...].
        // ⚠️ IMPORTANT: The order is [Depth, Value], NOT [Value, Depth].
        // Example for columnar data:
        dataAccessor: d => d.datasetA
        // Example for row-oriented data (e.g., [{ depth: 100, GR: 50 }]):
        // dataAccessor: (data) => data.map(row => [row.depth, row.GR])
      }
    }
  ]
});

// Use new LogViewer() instead of basic()
const viewer = new LogViewer({ showLegend: true, showTitles: true });

requestAnimationFrame(() => {
  viewer.init(div).setTracks(
    scaleTrack,
    graphTrack1,
    graphTrack2,
  );
  // viewer.refresh(); // Optional: Use refresh() to force immediate render if needed
});
```

## Stacked Track (e.g., Cement/Lithology)

```typescript
import { LogViewer, ScaleTrack, StackedTrack } from '@equinor/videx-wellog';
import { parseColor } from './my-utils'; // Recommended helper (see Abstractions)

// Mock data example (Boundary points, not intervals)
// The viewer fills from depth 100 to 200 with red, then from 200 onwards with blue
// ⚠️ IMPORTANT: StackedTrack REQUIRES color as {r, g, b} objects! 
// Standard CSS strings like 'red' will result in black if not converted.
const data = [
  { depth: 100, color: { r: 255, g: 0, b: 0 }, label: 'Layer A' },
  { depth: 200, color: parseColor('blue'), label: 'Layer B' }
];

const div = document.createElement('div');
div.style.height = '500px';
div.style.width = '100px';

const viewer = new LogViewer();
const scaleTrack = new ScaleTrack('scale', { maxWidth: 60 });
const stackedTrack = new StackedTrack('id', {
  // MUST be a function returning a Promise!
  data: () => Promise.resolve(data),
});
119→requestAnimationFrame(() => {
120→  viewer.init(div).setTracks([scaleTrack, stackedTrack]);
121→});
});
```

## Horizontal Log Viewer

```typescript
import { LogViewer } from '@equinor/videx-wellog';
import createTracks from './shared/tracks'; // Assume tracks are created elsewhere

const div = document.createElement('div');
div.style.height = '95vh';

const viewer = new LogViewer({
  showLegend: true,
  horizontal: true,
});

const tracks = createTracks(); // Helper function to create tracks

requestAnimationFrame(() => {
  viewer.init(div).setTracks(tracks);
});
```

## Dual Scale Track with Custom Interpolation

```typescript
import { DualScaleTrack, LogViewer, InterpolatedScaleHandler } from '@equinor/videx-wellog';

const div = document.createElement('div');
div.style.width = '500px';
div.style.height = '500px';

const scaleTrack1 = new DualScaleTrack('scale multiplied by 2', {
  maxWidth: 180,
  mode: 1,
});
const scaleTrack2 = new DualScaleTrack('scale divided by 2', {
  maxWidth: 180,
  mode: 0,
});

const viewer = new LogViewer({ showLegend: true, showTitles: true });

// Custom interpolator
const forward = v => v / 2;
const reverse = v => v * 2;
const interpolator = {
  forward,
  reverse,
  forwardInterpolatedDomain: domain => domain.map(v => forward(v)),
  reverseInterpolatedDomain: domain => domain.map(v => reverse(v)),
};

const scaleHandler = new InterpolatedScaleHandler(
  interpolator,
  [-10, 100],
).range([0, 500]);

viewer.scaleHandler = scaleHandler;
184→requestAnimationFrame(() => {
185→  viewer.init(div).setTracks(scaleTrack1, scaleTrack2);
186→});
});
```

## Programmatic Zooming

```typescript
import { LogViewer } from '@equinor/videx-wellog';

const viewer = new LogViewer({ showLegend: true, showTitles: true });

// ... setup viewer ...

requestAnimationFrame(() => {
  viewer.init(document.body);

  // Zoom to a specific range (e.g., 3800 to 4200 meters/feet)
  // IMPORTANT: Must pass a single array argument [min, max]
  viewer.zoomTo([3800, 4200]);
});
```

## Restricting Viewport (Prevent Infinite Pan)

To prevent users from panning outside the data/domain range, you can use the `onResize` callback to dynamically set `translateExtent` on the zoom behavior.

> **⚠️ Important**: `translateExtent` works in **pixel coordinates** (viewport size), NOT in data domain coordinates (e.g., depth).
> Do not pass your depth range (e.g., `[0, 3000]`) directly to this function unless your viewport happens to be exactly 3000px tall.
> The example below locks the view to the **track dimensions**, which prevents panning into empty space beyond the tracks.

```typescript
import { LogViewer } from '@equinor/videx-wellog';

const viewer = new LogViewer({
  // Hook into resize events to update boundaries
  onResize: (event) => {
    const { width, height, trackHeight } = event;
    const isHorizontal = viewer.options.horizontal;
    
    // Define the extent in pixels.
    // Ideally, this matches the track dimensions, effectively locking the view
    // to the initial domain unless zoomed in.
    const extent = isHorizontal
      ? [[0, 0], [trackHeight, height]] // [x0, y0], [x1, y1]
      : [[0, 0], [width, trackHeight]];

    // Apply restriction to the internal D3 zoom behavior
    viewer.zoom.translateExtent(extent);
  },
});

requestAnimationFrame(() => {
  viewer.init(document.body);
});
```

## Dip / Tadpole Plot

This plot type is used to visualize dip angle and azimuth, commonly known as a "Tadpole Plot".

> **Note**: The `DipPlot` is part of `GraphTrack` but requires specific data structure.

```typescript
import { GraphTrack, LogViewer, ScaleTrack, graphLegendConfig } from '@equinor/videx-wellog';

// Data format: [depth, dip, azimuth, metadata]
// metadata object must contain { color, shape }
// shapes: 'circle' | 'square' | 'triangle' | 'diamond' | 'cross' | 'plus' | 'star' ...
const dipData = [
  [100, 10, 45, { color: 'green', shape: 'circle' }],
  [110, 15, 90, { color: 'red', shape: 'square' }],
  [120, 5, 270, { color: 'blue', shape: 'triangle' }],
];

const track = new GraphTrack('dip-track', {
  label: 'Dip',
  scale: 'linear',
  domain: [0, 90], // Dip angle range (usually 0-90)
  data: dipData,
  legendConfig: graphLegendConfig,
  plots: [
    {
      id: 'dip-plot',
      type: 'dip', // <--- Key type
      options: {
        // DipPlot doesn't need much config, mainly legendInfo
        legendInfo: () => ({ label: 'DIP', unit: 'deg' }),
      },
    },
  ],
});

const viewer = new LogViewer({ showLegend: true, showTitles: true }).setTracks(new ScaleTrack('scale'), track);
viewer.init(document.body);
```

## Overlay with Tooltip (Crosshair)

To implement a mouse-following crosshair and tooltip, you can use the `viewer.overlay.create` API. This allows you to hook into mouse events (move, exit) and render custom HTML elements on top of the tracks.

```typescript
import { LogViewer, ScaleTrack, GraphTrack } from '@equinor/videx-wellog';

const viewer = new LogViewer();
const scaleTrack = new ScaleTrack('scale');
// Note: Ensure your data is sorted by depth for efficient binary search
const graphTrack = new GraphTrack('graph', { 
  data: [[0, 10], [100, 20], [200, 15]], 
  domain: [0, 50] 
});

requestAnimationFrame(() => {
  viewer.init(document.body).setTracks([scaleTrack, graphTrack]);

  // Create tooltip element
  const tooltip = document.createElement('div');
  Object.assign(tooltip.style, {
    position: 'absolute',
    background: 'white',
    border: '1px solid black',
    padding: '4px',
    pointerEvents: 'none',
    display: 'none',
  });
  
  // Register overlay
  const overlayElm = viewer.overlay.create('tooltip-overlay', {
    onMouseMove: (event) => {
      const { x, y, caller } = event;
      const isHorizontal = caller.options.horizontal;
      
      // Convert pixel coordinate to depth
      // Note: This uses the current scale (zoomed/panned)
      const scale = caller.scale;
      const depth = isHorizontal ? scale.invert(x) : scale.invert(y);

      // Show and position tooltip
      tooltip.style.display = 'block';
      tooltip.style.left = `${x + 10}px`;
      tooltip.style.top = `${y + 10}px`;
      tooltip.innerText = `Depth: ${depth.toFixed(2)}`;
      
      // OPTIONAL: Lookup data (Manual implementation required as tracks don't have unified getValueAt)
      // const data = graphTrack.data.find(...) 
    },
    onMouseExit: () => {
      tooltip.style.display = 'none';
    },
  });
  
  overlayElm.appendChild(tooltip);
});
```

## Multi-Curve Graph Track (e.g. Geom Track)

```typescript
import { GraphTrack, LogViewer, ScaleTrack } from '@equinor/videx-wellog';

const div = document.createElement('div');
div.style.height = '500px';

// Data object containing multiple curves
const curves = {
  HAZI: [[100, 10], [200, 20], [300, 15]],
  DEVI: [[100, 5], [200, 50], [300, 20]],
};

const track = new GraphTrack('multi-curve', {
  label: 'Geom',
  scale: 'linear',
  domain: [0, 100],
  // Pass the entire object as data
  data: curves, 
  plots: [
    {
      id: 'hazi',
      type: 'line',
      options: {
        color: 'green',
        width: 2,
        // Use dataAccessor to extract specific curve. 
        // Returns [[depth, value], ...]
        dataAccessor: (d) => d.HAZI, 
        // Note: legendInfo might require type augmentation in TS (see SKILL.md)
        legendInfo: () => ({ label: 'HAZI', unit: 'deg' }),
      },
    },
    {
      id: 'devi',
      type: 'line',
      options: {
        color: 'red',
        width: 2,
        // Use dataAccessor to extract specific curve
        dataAccessor: (d) => d.DEVI, 
        legendInfo: () => ({ label: 'DEVI', unit: 'deg' }),
      },
    },
  ],
});

const scaleTrack = new ScaleTrack('scale');
const viewer = new LogViewer({ showLegend: true, showTitles: true }).setTracks(scaleTrack, track);

requestAnimationFrame(() => {
  viewer.init(div);
});
```

## Triple Combo Layout (Standard)

A copy-paste ready example of the standard "Triple Combo" petrophysical layout:
1.  **Lithology**: Gamma Ray (GR), Caliper (CALI), SP.
2.  **Depth**: Scale Track.
3.  **Resistivity**: Deep (HDRS), Medium (HMRS), Shallow (HSRS) on Log Scale.
4.  **Porosity**: Density (RHOB) and Neutron (NPHI) with Gas Crossover effect.

```typescript
import { LogViewer, ScaleTrack, GraphTrack, graphLegendConfig } from '@equinor/videx-wellog';

const div = document.createElement('div');
div.style.height = '800px';

// 1. Lithology Track
const lithoTrack = new GraphTrack('lithology', {
  label: 'Lithology',
  width: 2,
  scale: 'linear',
  domain: [0, 150],
  legendConfig: graphLegendConfig,
  plots: [
    {
      id: 'GR',
      type: 'area',
      options: {
        color: 'green',
        fill: 'green',
        fillOpacity: 0.3,
        useMinAsBase: true,
        legendInfo: () => ({ label: 'GR', unit: 'API' }),
      }
    },
    {
      id: 'CALI',
      type: 'line',
      options: {
        color: 'black',
        dash: [5, 5],
        legendInfo: () => ({ label: 'CALI', unit: 'in' }),
      }
    }
  ]
});

// 2. Depth Track
const depthTrack = new ScaleTrack('depth', { maxWidth: 60 });

// 3. Resistivity Track (Log Scale)
const resTrack = new GraphTrack('resistivity', {
  label: 'Resistivity',
  width: 3,
  scale: 'log',
  domain: [0.2, 2000],
  legendConfig: graphLegendConfig,
  plots: [
    {
      id: 'RES_DEEP',
      type: 'line',
      options: { color: 'red', width: 2, legendInfo: () => ({ label: 'HDRS', unit: 'ohm.m' }) }
    },
    {
      id: 'RES_MED',
      type: 'line',
      options: { color: 'blue', width: 1, legendInfo: () => ({ label: 'HMRS', unit: 'ohm.m' }) }
    }
  ]
});

// 4. Porosity Track (Differential Crossover)
const poroTrack = new GraphTrack('porosity', {
  label: 'Porosity',
  width: 2,
  scale: 'linear',
  domain: [45, -15], // Inverted Porosity Scale
  legendConfig: graphLegendConfig,
  plots: [
    {
      id: 'diff-nphi-rhob',
      type: 'differential',
      options: {
        serie1: { color: 'blue', fill: 'yellow', width: 1 }, // Neutron
        serie2: { color: 'red', fill: 'grey', width: 1 },    // Density
        // Fill yellow (Gas) when Neutron < Density (in porosity units)
        // dataAccessor must return [ [depth, NPHI], [depth, RHOB_POR] ]
        dataAccessor: d => [d.NPHI, d.RHOB_POR] 
      }
    }
  ]
});

// Initialize
// Use new LogViewer() to ensure full functionality (Zoom/Overlay)
// IMPORTANT: Set 'domain' to cover the full data range (e.g., 0-3000m).
// Default is [0, 1000], which breaks interaction for deep data.
const viewer = new LogViewer({ 
  showLegend: true, 
  showTitles: true,
  domain: [0, 3000], 
});
494→requestAnimationFrame(() => {
495→  viewer.init(div).setTracks(lithoTrack, depthTrack, resTrack, poroTrack);
496→});
});
```

## Readout Helper Component

A helper class to manage a DOM-based readout (tooltip) that follows the mouse and displays depth/values. This abstracts away the manual DOM manipulation.

```typescript
import { LogViewer } from '@equinor/videx-wellog';

/**
 * A helper class to manage a floating readout/tooltip for the LogViewer.
 */
export class ReadoutController {
  private element: HTMLElement;
  private viewer: LogViewer;
  private overlayId: string;

  constructor(viewer: LogViewer, className = 'wellog-readout') {
    this.viewer = viewer;
    this.overlayId = `readout-${Math.random().toString(36).substr(2, 9)}`;
    
    // Create the DOM element
    this.element = document.createElement('div');
    this.element.className = className;
    Object.assign(this.element.style, {
      position: 'absolute',
      display: 'none',
      pointerEvents: 'none',
      zIndex: '1000',
      background: 'rgba(255, 255, 255, 0.9)',
      border: '1px solid #ccc',
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '12px',
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
    });
  }

  /**
   * Attaches the readout to the viewer's overlay system.
   * @param contentProvider Function to generate HTML content based on depth.
   */
  attach(contentProvider: (depth: number) => string) {
    const overlayElm = this.viewer.overlay.create(this.overlayId, {
      onMouseMove: (event) => {
        const { x, y, caller } = event;
        const isHorizontal = caller.options.horizontal;
        const scale = caller.scale;
        
        // Convert pixel to depth
        const depth = isHorizontal ? scale.invert(x) : scale.invert(y);
        
        // Update Content
        this.element.innerHTML = contentProvider(depth);
        
        // Update Position
        this.element.style.display = 'block';
        this.element.style.left = `${x + 15}px`;
        this.element.style.top = `${y}px`;
      },
      onMouseExit: () => {
        this.element.style.display = 'none';
      }
    });

    overlayElm.appendChild(this.element);
    return this;
  }

  /**
   * Detaches and removes the readout.
   */
  detach() {
    // Note: Library doesn't explicitly support 'removeOverlay', 
    // but we can remove the child element.
    if (this.element.parentElement) {
      this.element.parentElement.removeChild(this.element);
    }
  }
}

// Usage:
// const readout = new ReadoutController(viewer);
// readout.attach((depth) => `<b>Depth:</b> ${depth.toFixed(2)} m`);
```

## Advanced / Mixed Track Layouts

This example demonstrates how to configure multiple tracks with different plot types, including GraphTrack, ScaleTrack, StackedTrack, DistributionTrack, and ColorStripTrack.

```typescript
import {
  ScaleTrack,
  GraphTrack,
  StackedTrack,
  DistributionTrack,
  ColorStripTrack,
  graphLegendConfig,
  LegendHelper,
  scaleLegendConfig,
  distributionLegendConfig,
} from '@equinor/videx-wellog';

// Define distribution components colors
const distributionComponents = {
  carbonate: { color: 'FireBrick', textColor: '#8E1B1B' },
  sand: { color: 'SandyBrown', textColor: '#9C693E' },
  shale: { color: 'SlateGrey', textColor: '#5A6673' },
};

// Create a set of tracks
export const createAdvancedTracks = (data) => {
  return [
    // 1. Scale Track (Depth)
    new ScaleTrack(0, {
      maxWidth: 50,
      width: 2,
      label: 'MD',
      abbr: 'MD',
      units: 'mtr',
      legendConfig: scaleLegendConfig,
    }),

    // 2. Graph Track (Log Scale)
    new GraphTrack(1, {
      legendConfig: LegendHelper.basicVerticalLabel('Some label', 'Abbr'),
      scale: 'log',
      domain: [0.1, 1000],
      label: 'Track A',
      width: 2,
      data: [], // Add data here
    }),

    // 3. Graph Track with Dot Plot
    new GraphTrack(2, {
      label: 'Pointy',
      abbr: 'Pt',
      data: data.ex1,
      scale: 'linear',
      domain: [0, 1],
      legendConfig: graphLegendConfig,
      plots: [
        {
          id: 'dots',
          type: 'dot',
          options: {
            color: 'orange',
            legendInfo: () => ({ label: 'DOT', unit: 'bar' }),
          },
        },
      ],
    }),

    // 4. Graph Track with Dip Plot
    new GraphTrack(3, {
      label: 'Dip',
      abbr: 'Dip',
      data: data.dipData,
      scale: 'linear',
      domain: [0, 90],
      legendConfig: graphLegendConfig,
      plots: [
        {
          id: 'dip',
          type: 'dip',
          options: {
            legendInfo: () => ({ label: 'DIP', unit: 'deg' }),
          },
        },
      ],
    }),

    // 5. Graph Track with Multiple Plots (Line & LineStep)
    new GraphTrack(4, {
      label: 'Noise & Power',
      abbr: 'noise',
      data: data.ex2,
      legendConfig: graphLegendConfig,
      plots: [
        {
          id: 'noise',
          type: 'line',
          options: {
            color: 'blue',
            dataAccessor: d => d.noise,
            legendInfo: () => ({ label: 'Noise', unit: 'mm' }),
          },
        },
        {
          id: 'power',
          type: 'linestep',
          options: {
            scale: 'linear',
            domain: [0, 40],
            color: 'black',
            offset: 0.5,
            dataAccessor: d => d.noise2,
            legendInfo: () => ({ label: 'Power', unit: 'Pwr' }),
          },
        },
      ],
    }),

    // 6. Stacked Track (Formation)
    new StackedTrack(6, {
      label: 'Formation',
      showLines: false,
      labelRotation: -90,
      data: data.formationData,
    }),

    // 7. Distribution Track
    new DistributionTrack(7, {
      label: 'Distribution',
      abbr: 'Dst',
      data: data.distributionData,
      legendConfig: distributionLegendConfig,
      components: distributionComponents,
      interpolate: true,
    }),
  ];
};
```

// See references/best-practices.md for Robust Initialization Template and Data Preparation Utility
