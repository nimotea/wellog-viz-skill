# Data Generation & Templates

This file provides both programmatic mock data generators and standard JSON templates for `videx-wellog` tracks.

## 1. Standard JSON Templates
Use these templates when manually setting data for tracks. They ensure correct coordinate order and object structures.

### GraphTrack (Standard Curve)
**Format**: `[[depth, value], [depth, value], ...]`
```json
[
  [100.0, 45.2],
  [100.1, 46.5],
  [100.2, 44.8],
  [100.3, 47.1],
  [100.4, 45.9]
]
```

### GraphTrack (Columnar / Multiple Datasets)
**Format**: Object containing named arrays.
```json
{
  "GR": [[100, 45], [101, 46]],
  "NPHI": [[100, 0.25], [101, 0.26]],
  "RHOB": [[100, 2.3], [101, 2.4]]
}
```

### StackedTrack (Lithology / Formations)
**CRITICAL**: Colors MUST be `{r, g, b}` objects.
```json
[
  {
    "from": 100.0,
    "to": 150.5,
    "name": "Sandstone",
    "color": { "r": 255, "g": 255, "b": 0 }
  },
  {
    "from": 150.5,
    "to": 200.0,
    "name": "Shale",
    "color": { "r": 128, "g": 128, "b": 128 }
  }
]
```

### DipTrack / Tadpole Plots
**Format**: `[[depth, dip, azimuth, { color, shape }], ...]`
```json
[
  [1000.0, 15, 45, { "color": "red", "shape": "circle" }],
  [1010.0, 20, 180, { "color": "blue", "shape": "triangle" }]
]
```

---

## 2. Programmatic Mock Data Generation
Generating mock data is essential for testing well-log visualizations. Here are some helper patterns.

## Basic Linear Data

```typescript
import { range } from 'd3-array';

const domain = [0, 1500];

// Generate simple [depth, value] pairs
export const generateLinearData = () => 
  range(domain[0], domain[1], 10).map(d => [d, Math.random()]);
```

## Realistic Curve Data (With Noise & Trends)

Use this generator to create curves that mimic real well-logs, featuring underlying trends, layering effects, and configurable noise. This is useful for testing zoom behavior and performance with high-density data.

```typescript
interface CurveOptions {
  startDepth?: number;
  endDepth?: number;
  samplingRate?: number; // Depth increment (e.g., 0.1m)
  noiseLevel?: number;   // Amplitude of random noise (0.0 to 1.0)
  frequency?: number;    // Frequency of the main trend
}

/**
 * Generates a realistic synthetic curve with trends and noise.
 * @param options Configuration object
 */
export const generateRealisticCurve = (options: CurveOptions = {}) => {
  const {
    startDepth = 0,
    endDepth = 1000,
    samplingRate = 0.1,
    noiseLevel = 0.05,
    frequency = 0.02,
  } = options;

  const data = [];
  
  for (let depth = startDepth; depth <= endDepth; depth += samplingRate) {
    // 1. Base Trend: Low frequency sine wave to simulate formation changes
    const trend = Math.sin(depth * frequency) * 0.4 + 0.5;
    
    // 2. Layering Effect: Higher frequency component
    const layering = Math.sin(depth * frequency * 5) * 0.1;

    // 3. Random Noise: High frequency jitter
    const noise = (Math.random() - 0.5) * noiseLevel;

    // Combine components and clamp to [0, 1]
    let value = trend + layering + noise;
    value = Math.max(0, Math.min(1, value));

    data.push([depth, value]);
  }
  
  return data;
};

## Complete Mock Utility (Copy-Paste Ready)

You can copy the entire block below into a file named `mock-utils.ts` to have all data generation capabilities in one place.

```typescript
import { range } from 'd3-array';

// --- Types ---
export interface CurveOptions {
  startDepth?: number;
  endDepth?: number;
  samplingRate?: number;
  noiseLevel?: number;
  frequency?: number;
}

// --- Generators ---

/**
 * Generates simple linear data [depth, value]
 */
export const generateLinearData = (domain = [0, 1500]) => 
  range(domain[0], domain[1], 10).map(d => [d, Math.random()]);

/**
 * Generates realistic synthetic curve with trends and noise
 */
export const generateRealisticCurve = (options: CurveOptions = {}) => {
  const {
    startDepth = 0,
    endDepth = 1000,
    samplingRate = 0.1,
    noiseLevel = 0.05,
    frequency = 0.02,
  } = options;

  const data = [];
  for (let depth = startDepth; depth <= endDepth; depth += samplingRate) {
    const trend = Math.sin(depth * frequency) * 0.4 + 0.5;
    const layering = Math.sin(depth * frequency * 5) * 0.1;
    const noise = (Math.random() - 0.5) * noiseLevel;
    let value = Math.max(0, Math.min(1, trend + layering + noise));
    data.push([depth, value]);
  }
  return data;
};

/**
 * Generates formation/lithology blocks
 */
export const generateFormationData = (formationLength = 10) => {
  const names = ['Sandstone', 'Shale', 'Limestone', 'Granite'];
  const colors = [
    { r: 240, g: 230, b: 140 },
    { r: 128, g: 128, b: 128 },
    { r: 255, g: 248, b: 220 },
    { r: 175, g: 175, b: 175 },
  ];
  const arr = [];
  let currentFrom = 0;
  for (let index = 1; index <= formationLength; index++) {
    const newTo = currentFrom + (Math.random() * 100);
    const formationIndex = Math.floor(Math.random() * names.length);
    arr.push({
      name: names[formationIndex],
      from: currentFrom,
      to: newTo,
      color: colors[formationIndex],
    });
    currentFrom = newTo;
  }
  return arr;
};

/**
 * Generates tadpole/dip data
 */
export const generateDipData = () => {
  const colors = ['#228b22', '#ff4500', '#00bfff'];
  const shapes = ['circle', 'square', 'triangle'];
  return range(0, 1000, 10).map(d => [
    d,
    Math.random() * 90,
    Math.random() * 360,
    {
      color: colors[Math.floor(Math.random() * colors.length)],
      shape: shapes[Math.floor(Math.random() * shapes.length)],
    },
  ]);
};

/**
 * Generates sine wave + correlated noise
 */
export const generateSineWithNoise = (domainStart = 0, domainEnd = 1500, step = 1) => {
  const sin = range(domainStart, domainEnd, step).map(d => [
    d,
    Math.sin((d / 2000) * Math.PI * 2 * 20) * 25 + 50,
  ]);
  const noise = sin.map(v => [v[0], v[1] * Math.random() + 35]);
  return { sin, noise };
};
```

## Sine Wave with Varied Noise (Reference Pattern)

This pattern mimics the `ex3` dataset used in `LogViewer` stories, which is excellent for testing `AreaPlot` and `LinePlot` combinations. It generates a smooth sine wave and a correlated noisy signal.

```typescript
import { range } from 'd3-array';

/**
 * Generates a sine wave and a derived noisy signal.
 * Useful for testing AreaPlots where the noise creates a "filled" effect against the sine wave.
 * @param domainStart Start depth (default 0)
 * @param domainEnd End depth (default 1500)
 * @param step Depth step (default 1)
 */
export const generateSineWithNoise = (domainStart = 0, domainEnd = 1500, step = 1) => {
  // 1. Generate base Sine Wave
  // Frequency tuned to show ~15 cycles over 1500 units
  const sin = range(domainStart, domainEnd, step).map(d => [
    d,
    Math.sin((d / 2000) * Math.PI * 2 * 20) * 25 + 50,
  ]);

  // 2. Generate correlated Noise (e.g. for Area Plot)
  // Multiplicative noise based on the sine wave value
  const noise = sin.map(v => [
    v[0], 
    v[1] * Math.random() + 35
  ]);

  return { sin, noise };
};
```

## Stacked Track Data (e.g., Lithology)

```typescript
export const generateFormationData = (formationLength = 10) => {
  const names = ['Sandstone', 'Shale', 'Limestone', 'Granite'];
  const colors = [
    { r: 240, g: 230, b: 140 }, // Sandstone
    { r: 128, g: 128, b: 128 }, // Shale
    { r: 255, g: 248, b: 220 }, // Limestone
    { r: 175, g: 175, b: 175 }, // Granite
  ];

  const arr = [];
  let currentFrom = 0;
  
  for (let index = 1; index <= formationLength; index++) {
    const newTo = currentFrom + (Math.random() * 100);
    const formationIndex = Math.floor(Math.random() * names.length);
    
    arr.push({
      name: names[formationIndex],
      from: currentFrom,
      to: newTo,
      color: colors[formationIndex],
    });
    
    currentFrom = newTo;
  }
  return arr;
};
```

## Dip Plot Data

```typescript
import { range } from 'd3-array';

export const generateDipData = () => {
  const colors = ['#228b22', '#ff4500', '#00bfff'];
  const shapes = ['circle', 'square', 'triangle'];

  return range(0, 1000, 10).map(d => [
    d,                  // Depth
    Math.random() * 90, // Dip angle
    Math.random() * 360,// Azimuth
    {                   // Metadata
      color: colors[Math.floor(Math.random() * colors.length)],
      shape: shapes[Math.floor(Math.random() * shapes.length)],
    },
  ]);
};
```

## Distribution Data

```typescript
export const generateDistributionData = () => {
  const components = ['carbonate', 'sand', 'shale'];
  const data = [];

  for (let depth = 200; depth <= 1000; depth += 10) {
    let remainingValue = 100;
    const composition = components.map((key, index) => {
      if (index === components.length - 1) {
        return { key, value: remainingValue };
      }
      const value = parseFloat((Math.random() * remainingValue).toFixed(2));
      remainingValue -= value;
      return { key, value };
    });

    data.push({ depth, composition });
  }
  return data;
};
```
