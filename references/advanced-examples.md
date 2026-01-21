# Advanced Well-Log Examples

This file contains more complex examples of track configuration.

## Complex Track Configuration

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
