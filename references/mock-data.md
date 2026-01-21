# Mock Data Generation

Generating mock data is essential for testing well-log visualizations. Here are some helper patterns.

## Basic Linear Data

```typescript
import { range } from 'd3-array';

const domain = [0, 1500];

// Generate simple [depth, value] pairs
export const generateLinearData = () => 
  range(domain[0], domain[1], 10).map(d => [d, Math.random()]);
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
