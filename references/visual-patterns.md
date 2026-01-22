# Visual Patterns Library

This document maps visual requirements (screenshots/mockups) to specific component configurations. Use this reference when the user provides a visual description or an image of a desired well-log plot.

## Table of Contents
- [Visual Patterns Library](#visual-patterns-library)
  - [Table of Contents](#table-of-contents)
  - [Patterns](#patterns)
    - [Standard Filled Area](#standard-filled-area)
    - [Inverted Filled Area](#inverted-filled-area)
    - [Dual/Differential Fill Area](#dualdifferential-fill-area)
    - [Differential / Crossover Plot](#differential--crossover-plot)
    - [Dot Plot](#dot-plot)
    - [Line Plot (Solid / Dashed)](#line-plot-solid--dashed)
    - [Step Plot](#step-plot)
    - [Tadpole / Dip Plot](#tadpole--dip-plot)
  - [Track Patterns](#track-patterns)
    - [Standard Graph Track (Grid)](#standard-graph-track-grid)
    - [Graph Track (Piecewise)](#graph-track-piecewise)
    - [Graph Track (Multiple Plots)](#graph-track-multiple-plots)
    - [Graph Track (Single Plot)](#graph-track-single-plot)
    - [Dual Scale Track](#dual-scale-track)
    - [Scale Track](#scale-track)
    - [Stacked Track](#stacked-track)
    - [Distribution Track](#distribution-track)
  - [Viewer Patterns](#viewer-patterns)
    - [Log Viewer (Single Track)](#log-viewer-single-track)
    - [Log Viewer (Multiple Tracks)](#log-viewer-multiple-tracks)
    - [Log Viewer (Dual Scale \& Interpolation)](#log-viewer-dual-scale--interpolation)
    - [Log Viewer (Stacked/Cement/Formation)](#log-viewer-stackedcementformation)
    - [Log Viewer (Flag Track)](#log-viewer-flag-track)
    - [Log Viewer (Horizontal Layout)](#log-viewer-horizontal-layout)
    - [Log Viewer (With Legend)](#log-viewer-with-legend)
  - [Controller Patterns](#controller-patterns)
    - [Standard Log Controller](#standard-log-controller)
    - [Horizontal Log Controller](#horizontal-log-controller)
    - [Log Controller Legend Configuration](#log-controller-legend-configuration)
    - [Log Controller (Multiple Tracks Layout)](#log-controller-multiple-tracks-layout)
    - [Log Controller (Single Track)](#log-controller-single-track)
  - [Composite Layouts](#composite-layouts)
    - [Triple Combo](#triple-combo)

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
  horizontal: false, // Default: Vertical layout
});

// 2. Create an array of tracks (using patterns defined above)
const tracks = [
  new ScaleTrack('scale', { width: 1 }),
  new GraphTrack('graph', { width: 3 }),
  new DistributionTrack('dist', { width: 2 }),
];

// 3. Initialize and mount
controller.init(domElement).setTracks(tracks);

// 4. (Optional) Zoom Control
controller.zoomTo([300, 400], 1000); // Zoom to depth 300-400 over 1s
```

### Horizontal Log Controller
**Visual Description**: A log controller layout rotated 90 degrees. Tracks are stacked vertically, and the depth/time axis runs horizontally (left-to-right). Ideal for time-series data or drilling parameters.
**Key Components**: `LogController` (with `horizontal: true`), `GraphTrack`, `StackedTrack`.
**Configuration Highlights**:
- `horizontal: true`: This single flag on the controller propagates to all tracks.
- **StackedTrack Labels**: Often need rotation (e.g., `labelRotation: -90`) to be readable in narrow vertical bands.
- **Track Order**: In horizontal mode, the track array order determines top-to-bottom stacking.

**Code Snippet**:
```typescript
const controller = new LogController({
  horizontal: true, // <--- Key setting
  showLegend: true,
  showTitles: true,
  });

const tracks = [
  new ScaleTrack('scale', { height: 1 }), // Height weight instead of width
  new GraphTrack('graph', { height: 3 }),
  new StackedTrack('formation', {
    height: 1,
    labelRotation: -90, // Optimize label text for horizontal layout
  })
];

controller.init(domElement).setTracks(tracks);
```

### Log Controller Legend Configuration
**Visual Description**: The header area of the log viewer, displaying track titles, units, and plot keys (e.g., color-coded curve names). Can include interactive elements.
**Key Components**: `LogController`, `TrackOptions.legendConfig`, `LegendHelper`.
**Configuration Highlights**:
- **Global Toggle**: `LogController({ showLegend: true })` must be enabled.
- **Track-Level Config**: Each track uses `legendConfig` to define its header appearance.
- **Helpers**: Use `LegendHelper` for common patterns instead of raw SVG/DOM coding.
    - `scaleLegendConfig`: Standard scale ticks/units.
    - `graphLegendConfig`: Auto-generates keys based on `plots`.
    - `distributionLegendConfig`: Auto-generates keys based on `components`.
    - `LegendHelper.basicVerticalLabel(label, abbr)`: Simple vertical text.

**Custom Legend Configuration**:
If the built-in helpers don't suffice, you can implement the `LegendConfig` interface directly.
```typescript
interface LegendConfig {
  // 'svg' (default) or 'html'
  elementType: string; 
  // Function returning the number of rows this legend needs
  getLegendRows(track: Track): number;
  // Called once when the legend is created
  onInit: (elm: Element, track: Track, updateTrigger: () => void) => void;
  // Called whenever the track updates or resizes
  onUpdate: (elm: Element, bounds: LegendBounds, track: Track) => void;
}
```

**Code Snippet**:
```typescript
import { LegendHelper, scaleLegendConfig, graphLegendConfig } from '@equinor/videx-wellog';

const controller = new LogController({ showLegend: true });

const tracks = [
  // 1. Scale Legend (Standard)
  new ScaleTrack('scale', {
    legendConfig: scaleLegendConfig,
  }),

  // 2. Graph Legend (Auto-generated from plots)
  new GraphTrack('graph', {
    legendConfig: graphLegendConfig,
    plots: [
      { 
        id: 'curve', 
        type: 'line', 
        options: { 
          legendInfo: () => ({ label: 'Gamma Ray', unit: 'API' }) 
        } 
      }
    ]
  }),

  // 3. Simple Vertical Label
  new GraphTrack('simple', {
    legendConfig: LegendHelper.basicVerticalLabel('My Track', 'MT'),
  })
];
```

### Log Controller (Multiple Tracks Layout)
**Visual Description**: A basic layout focusing on the arrangement of multiple tracks, often featuring a scale track alongside one or more data tracks with grids.
**Key Components**: `LogController`, `GraphTrack`, `ScaleTrack`.
**Configuration Highlights**:
- **Width Weights**: `TrackOptions.width` controls the relative width (flex) of tracks.
    - Example: `width: 2` takes twice the space of `width: 1`.
- **Fixed Width**: `TrackOptions.maxWidth` fixes a track's size (common for ScaleTrack).
- **Titles**: Enabled via `new LogController({ showTitles: true })`. Defaults to track ID if no label is set.

**Code Snippet**:
```typescript
const controller = new LogController({ showTitles: true, showLegend: false });

const tracks = [
  // Fixed width Scale Track
  new ScaleTrack('scale', { maxWidth: 60 }),
  
  // Flexible Graph Tracks
  new GraphTrack('graph1', { width: 2 }), // 2/3 of remaining space
  new GraphTrack('graph2', { width: 1 }), // 1/3 of remaining space
];

controller.init(div).setTracks(tracks);
```

### Log Controller (Single Track)
**Visual Description**: A minimal view showing only one track (e.g., just a scale ruler or a single curve) without headers or legends.
**Key Components**: `LogController`, `ScaleTrack` (or any single Track).
**Configuration Highlights**:
- **Minimal Mode**: `new LogController({ showTitles: false, showLegend: false })` disables titles and legends.
- **Single Addition**: Use `addTrack(track)` instead of `setTracks([...])` for simplicity.

**Code Snippet**:
```typescript
// Create a controller with NO titles or legend
const controller = new LogController({ showTitles: false, showLegend: false });

const scaleTrack = new ScaleTrack('scale');

// Add single track and zoom
controller.init(div)
  .addTrack(scaleTrack)
  .zoomTo([500, 600]);
```

## Composite Layouts

### Triple Combo
**Visual Description**: A standard petrophysical display combining Gamma Ray (lithology), Resistivity (fluids), and Porosity (Density/Neutron) tracks.
**Key Components**: `LogViewer`, `GraphTrack`, `ScaleTrack`, `DifferentialPlot`, `AreaPlot`.
**Layout Structure**:
1.  **Track 1 (Lithology)**: Gamma Ray (GR) + Caliper (CALI) + SP. Often with GR fill to left or right.
2.  **Track 2 (Depth)**: Scale Track.
3.  **Track 3 (Resistivity)**: Deep, Medium, Shallow resistivity on a **Logarithmic** scale.
4.  **Track 4 (Porosity)**: Density (RHOB) and Neutron (NPHI) on compatible scales (e.g., -15 to 45 porosity units). Includes "Crossover" shading (Gas effect).

**Code Snippet (Layout Skeleton)**:
```typescript
import { LogViewer, ScaleTrack, GraphTrack, graphLegendConfig } from '@equinor/videx-wellog';

// 0. Prepare Data
// const data = [
//   { DEPTH: 100, GR: 45, NPHI: 0.15, RHOB_POR: 0.2, RES_DEEP: 10, ... },
//   ...
// ];

// 1. Lithology Track (GR/CALI)
const lithoTrack = new GraphTrack('lithology', {
  label: 'Lithology',
  width: 2,
  scale: 'linear',
  domain: [0, 150], // GR usually 0-150 API
  data: data, // <--- Inject data here
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
  scale: 'log', // <--- Key for resistivity
  domain: [0.2, 2000],
  data: data, // <--- Inject data here
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

// 4. Porosity Track (Density/Neutron Crossover)
// Note: Density and Neutron are often plotted on compatible scales to show lithology/gas
// e.g. Neutron: 0.45 to -0.15 (Left to Right)
// e.g. Density: 1.95 to 2.95 (Left to Right)
// Implementing this often requires normalizing data to a shared 0-100 domain or using multiple axes (if supported).
// Here is a simplified single-domain version with Differential Plot.
const poroTrack = new GraphTrack('porosity', {
  label: 'Porosity',
  width: 2,
  scale: 'linear',
  domain: [45, -15], // Inverted scale for porosity
  data: data, // <--- Inject data here
  legendConfig: graphLegendConfig,
  plots: [
    {
      id: 'diff-nphi-rhob',
      type: 'differential',
      options: {
        serie1: { color: 'blue', fill: 'yellow', width: 1 }, // Neutron (NPHI)
        serie2: { color: 'red', fill: 'grey', width: 1 },    // Density (RHOB equivalent porosity)
        // Fill yellow (Gas) when Neutron < Density (in porosity units)
        dataAccessor: d => [d.NPHI, d.RHOB_POR] 
      }
    }
  ]
});

// Use new LogViewer() instead of basic()
const viewer = new LogViewer({ showLegend: true, showTitles: true });
viewer.init(div).setTracks(lithoTrack, depthTrack, resTrack, poroTrack);
```
