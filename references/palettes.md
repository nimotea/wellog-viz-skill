# Geologic Color Palettes (SY/T 5751)

This reference provides standardized geologic colors based on the **SY/T 5751** (Petroleum and Natural Gas Industry Standard of China) for use in well-log visualizations.

## SY/T 5751:2012 Standard Colors

These colors are commonly used for `StackedTrack` intervals (Lithology) and `AreaPlot` fills.

| Code    | Lithology (Description)    | Color (Hex) | Sample |
| :------ | :------------------------- | :---------- | :----- |
| **1.1** | Conglomerate (砾岩)        | `#FFD700`   | 🟨      |
| **2.1** | Sandstone (砂岩)           | `#FFFF00`   | 🟨      |
| **3.1** | Siltstone (粉砂岩)         | `#FFFFE0`   | ⬜      |
| **4.1** | Mudstone/Shale (泥岩/页岩) | `#BEBEBE`   | ⬛      |
| **5.1** | Limestone (灰岩)           | `#0000FF`   | 🟦      |
| **6.1** | Dolomite (白云岩)          | `#A52A2A`   | 🤎      |
| **7.1** | Coal (煤)                  | `#000000`   | ⬛      |
| **8.1** | Gypsum (石膏)              | `#FFC0CB`   | 🌸      |
| **9.1** | Salt (岩盐)                | `#FFFFFF`   | ⬜      |

## Usage in Code

### Constant Library

```typescript
export const SYT5751 = {
  '1.1': '#FFD700', // Conglomerate
  '2.1': '#FFFF00', // Sandstone
  '3.1': '#FFFFE0', // Siltstone
  '4.1': '#BEBEBE', // Mudstone
  '5.1': '#0000FF', // Limestone
  '6.1': '#A52A2A', // Dolomite
  '7.1': '#000000', // Coal
  '8.1': '#FFC0CB', // Gypsum
  '9.1': '#FFFFFF', // Salt
};
```

### Application in StackedTrack

```typescript
const lithologyData = [
  { from: 1000, to: 1050, color: SYT5751['2.1'], label: 'Sandstone' },
  { from: 1050, to: 1100, color: SYT5751['4.1'], label: 'Shale' },
];

const track = new StackedTrack('litho', {
  data: () => Promise.resolve(lithologyData),
});
```

### Application in AreaPlot

```typescript
const plot = {
  id: 'gr-fill',
  type: 'area',
  options: {
    color: 'black',
    fill: SYT5751['2.1'], // Standard yellow for sandstone
    fillOpacity: 0.5,
  }
};
```
