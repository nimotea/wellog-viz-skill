# Well-Log Visualization Examples

This file contains code snippets for common `videx-wellog` usage patterns.

## Basic Log Viewer with Single Track

```typescript
import '@equinor/videx-wellog/dist/styles/styles.css'; // Essential!
import { ScaleTrack, LogViewer } from '@equinor/videx-wellog';

const div = document.createElement('div');
div.style.width = '100px';
div.style.height = '500px';

const scaleTrack = new ScaleTrack('scale');
const viewer = LogViewer.basic(false).addTrack(scaleTrack);

// Ensure div is attached to DOM before init
requestAnimationFrame(() => {
  viewer.init(div);
});
```

## Log Viewer with Multiple Tracks

```typescript
import '@equinor/videx-wellog/dist/styles/styles.css';
import { ScaleTrack, GraphTrack, LogViewer } from '@equinor/videx-wellog';

const div = document.createElement('div');
div.style.width = '500px';
div.style.height = '500px';

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
        dataAccessor: d => d.datasetA
      }
    }
  ]
});

const viewer = LogViewer.basic().setTracks(
  scaleTrack,
  graphTrack1,
  graphTrack2,
);

requestAnimationFrame(() => {
  viewer.init(div);
});
```

## Stacked Track (e.g., Cement/Lithology)

```typescript
import { LogViewer, ScaleTrack, StackedTrack } from '@equinor/videx-wellog';

// Mock data example (Boundary points, not intervals)
// The viewer fills from depth 100 to 200 with red, then from 200 onwards with blue
const data = [
  { depth: 100, color: 'red', label: 'Layer A' },
  { depth: 200, color: 'blue', label: 'Layer B' }
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

requestAnimationFrame(() => {
  viewer.init(div).setTracks([scaleTrack, stackedTrack]);
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

const viewer = LogViewer.basic().setTracks(scaleTrack1, scaleTrack2);

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

requestAnimationFrame(() => {
  viewer.init(div);
});
```

## Programmatic Zooming

```typescript
import { LogViewer } from '@equinor/videx-wellog';

const viewer = LogViewer.basic();

// ... setup viewer ...

requestAnimationFrame(() => {
  viewer.init(document.body);

  // Zoom to a specific range (e.g., 3800 to 4200 meters/feet)
  // IMPORTANT: Must pass a single array argument [min, max]
  viewer.zoomTo([3800, 4200]);
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
        // Use dataAccessor to extract specific curve
        dataAccessor: (d) => d.HAZI, 
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
const viewer = LogViewer.basic().setTracks(scaleTrack, track);

requestAnimationFrame(() => {
  viewer.init(div);
});
```
