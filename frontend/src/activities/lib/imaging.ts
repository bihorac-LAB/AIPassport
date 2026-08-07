/**
 * Image operations for the Module 5 activities.
 *
 * All of these are the same operations the legacy notebooks called OpenCV for, reimplemented as pure
 * functions over a flat intensity array so they run instantly in the browser.
 */

import { clamp, rng } from './math';

export type Image = { width: number; height: number; data: number[] };

/** Chest-radiograph phantom: air-filled lungs, soft tissue, a bony midline (legacy 5.1). */
export function attenuationPhantom(
  air: number,
  tissue: number,
  bone: number,
  width = 60,
  height = 30,
): Image {
  const data = new Array<number>(width * height).fill(tissue);
  const lungRadius = height * 0.34;
  const centres = [
    { x: width * 0.3, y: height * 0.5 },
    { x: width * 0.7, y: height * 0.5 },
  ];
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      for (const centre of centres) {
        const dx = (x - centre.x) / lungRadius;
        const dy = (y - centre.y) / lungRadius;
        if (dx * dx + dy * dy <= 1) data[y * width + x] = air;
      }
      // Vertical bony structure through the midline.
      if (Math.abs(x - width / 2) <= width * 0.035 && y > height * 0.12 && y < height * 0.88) {
        data[y * width + x] = bone;
      }
    }
  }
  return { width, height, data };
}

/** Small image with a diagonal edge and a bright blob — good for kernels and denoising. */
export function edgePhantom(width = 24, height = 24): Image {
  const data = new Array<number>(width * height).fill(70);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      if (x > width * 0.45) data[y * width + x] = 165;
      const dx = x - width * 0.72;
      const dy = y - height * 0.3;
      if (dx * dx + dy * dy < 12) data[y * width + x] = 235;
      const bx = x - width * 0.25;
      const by = y - height * 0.7;
      if (bx * bx + by * by < 9) data[y * width + x] = 20;
    }
  }
  return { width, height, data };
}

/** Deliberately low-contrast image for the equalization activity. */
export function lowContrastPhantom(width = 32, height = 24): Image {
  const next = rng(5);
  const data = new Array<number>(width * height).fill(0).map((_, index) => {
    const x = index % width;
    const y = Math.floor(index / width);
    const base = 108 + Math.sin(x / 4) * 6 + Math.cos(y / 5) * 5;
    const lesion =
      (x - width * 0.62) ** 2 / 18 + (y - height * 0.45) ** 2 / 10 < 1 ? 12 : 0;
    return clamp(Math.round(base + lesion + next() * 4), 0, 255);
  });
  return { width, height, data };
}

export function histogram(image: Image, bins = 32): number[] {
  const counts = new Array<number>(bins).fill(0);
  for (const value of image.data) {
    const index = clamp(Math.floor((value / 256) * bins), 0, bins - 1);
    counts[index] = (counts[index] ?? 0) + 1;
  }
  return counts;
}

export const KERNELS: Record<
  string,
  { label: string; kernel: number[]; divisor: number; offset: number; note: string }
> = {
  identity: {
    label: 'Identity',
    kernel: [0, 0, 0, 0, 1, 0, 0, 0, 0],
    divisor: 1,
    offset: 0,
    note: 'Copies the centre pixel. The baseline to compare against.',
  },
  blur: {
    label: 'Box blur',
    kernel: [1, 1, 1, 1, 1, 1, 1, 1, 1],
    divisor: 9,
    offset: 0,
    note: 'Averages the neighbourhood. Weights sum to 9 and are divided by 9, so brightness is preserved.',
  },
  sharpen: {
    label: 'Sharpen',
    kernel: [0, -1, 0, -1, 5, -1, 0, -1, 0],
    divisor: 1,
    offset: 0,
    note: 'Boosts the centre and subtracts its neighbours, exaggerating local differences.',
  },
  sobelX: {
    label: 'Vertical edges',
    kernel: [-1, 0, 1, -2, 0, 2, -1, 0, 1],
    divisor: 1,
    offset: 128,
    note: 'Weights sum to zero, so flat regions output nothing and only left-right changes survive.',
  },
  sobelY: {
    label: 'Horizontal edges',
    kernel: [-1, -2, -1, 0, 0, 0, 1, 2, 1],
    divisor: 1,
    offset: 128,
    note: 'The same detector rotated: responds to top-bottom changes instead.',
  },
};

export function convolve(image: Image, kernel: number[], divisor = 1, offset = 0): Image {
  const { width, height, data } = image;
  const out = new Array<number>(width * height).fill(0);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      let sum = 0;
      for (let ky = -1; ky <= 1; ky += 1) {
        for (let kx = -1; kx <= 1; kx += 1) {
          const sx = clamp(x + kx, 0, width - 1);
          const sy = clamp(y + ky, 0, height - 1);
          sum += (data[sy * width + sx] ?? 0) * (kernel[(ky + 1) * 3 + (kx + 1)] ?? 0);
        }
      }
      out[y * width + x] = clamp(Math.round(sum / divisor + offset), 0, 255);
    }
  }
  return { width, height, data: out };
}

/** The nine multiplications behind one output pixel, for the step-through view. */
export function convolutionDetail(
  image: Image,
  kernel: number[],
  divisor: number,
  offset: number,
  x: number,
  y: number,
) {
  const terms: Array<{ pixel: number; weight: number; product: number }> = [];
  for (let ky = -1; ky <= 1; ky += 1) {
    for (let kx = -1; kx <= 1; kx += 1) {
      const sx = clamp(x + kx, 0, image.width - 1);
      const sy = clamp(y + ky, 0, image.height - 1);
      const pixel = image.data[sy * image.width + sx] ?? 0;
      const weight = kernel[(ky + 1) * 3 + (kx + 1)] ?? 0;
      terms.push({ pixel, weight, product: pixel * weight });
    }
  }
  const raw = terms.reduce((a, t) => a + t.product, 0);
  return { terms, raw, output: clamp(Math.round(raw / divisor + offset), 0, 255) };
}

export function addSaltPepper(image: Image, rate: number, seed = 3): Image {
  const next = rng(seed);
  const data = image.data.map((value) => {
    if (next() < rate / 2) return 0;
    if (next() < rate / 2) return 255;
    return value;
  });
  return { ...image, data };
}

export function medianFilter(image: Image, radius = 1): Image {
  const { width, height, data } = image;
  const out = new Array<number>(width * height).fill(0);
  for (let y = 0; y < height; y += 1) {
    for (let x = 0; x < width; x += 1) {
      const window: number[] = [];
      for (let dy = -radius; dy <= radius; dy += 1) {
        for (let dx = -radius; dx <= radius; dx += 1) {
          const sx = clamp(x + dx, 0, width - 1);
          const sy = clamp(y + dy, 0, height - 1);
          window.push(data[sy * width + sx] ?? 0);
        }
      }
      window.sort((a, b) => a - b);
      out[y * width + x] = window[Math.floor(window.length / 2)] ?? 0;
    }
  }
  return { width, height, data: out };
}

export function meanFilter(image: Image, radius = 1): Image {
  const size = radius * 2 + 1;
  return convolve(image, new Array<number>(size * size).fill(1).slice(0, 9), 9, 0);
}

export function applyWindow(image: Image, centre: number, width: number): Image {
  const lo = centre - width / 2;
  const hi = centre + width / 2;
  const span = hi - lo || 1;
  return {
    ...image,
    data: image.data.map((value) => clamp(Math.round(((value - lo) / span) * 255), 0, 255)),
  };
}

export function equalize(image: Image): Image {
  const counts = new Array<number>(256).fill(0);
  for (const value of image.data) {
    const index = clamp(Math.round(value), 0, 255);
    counts[index] = (counts[index] ?? 0) + 1;
  }
  const total = image.data.length || 1;
  const cdf: number[] = [];
  let running = 0;
  for (let i = 0; i < 256; i += 1) {
    running += counts[i] ?? 0;
    cdf.push(running / total);
  }
  return {
    ...image,
    data: image.data.map((value) =>
      clamp(Math.round((cdf[clamp(Math.round(value), 0, 255)] ?? 0) * 255), 0, 255),
    ),
  };
}

/** Contrast-limited adaptive equalization over tiles. */
export function clahe(image: Image, tiles = 4, clipLimit = 2.5): Image {
  const { width, height } = image;
  const out = [...image.data];
  const tileW = Math.ceil(width / tiles);
  const tileH = Math.ceil(height / tiles);

  for (let ty = 0; ty < tiles; ty += 1) {
    for (let tx = 0; tx < tiles; tx += 1) {
      const x0 = tx * tileW;
      const y0 = ty * tileH;
      const x1 = Math.min(width, x0 + tileW);
      const y1 = Math.min(height, y0 + tileH);
      const values: number[] = [];
      for (let y = y0; y < y1; y += 1) {
        for (let x = x0; x < x1; x += 1) values.push(image.data[y * width + x] ?? 0);
      }
      if (values.length === 0) continue;

      const counts = new Array<number>(256).fill(0);
      for (const value of values) {
        const bin = clamp(Math.round(value), 0, 255);
        counts[bin] = (counts[bin] ?? 0) + 1;
      }

      // Clip tall bins and redistribute — this is the "contrast-limited" part.
      const limit = Math.max(1, (clipLimit * values.length) / 256);
      let excess = 0;
      for (let i = 0; i < 256; i += 1) {
        const count = counts[i] ?? 0;
        if (count > limit) {
          excess += count - limit;
          counts[i] = limit;
        }
      }
      const share = excess / 256;
      for (let i = 0; i < 256; i += 1) counts[i] = (counts[i] ?? 0) + share;

      const cdf: number[] = [];
      let running = 0;
      for (let i = 0; i < 256; i += 1) {
        running += counts[i] ?? 0;
        cdf.push(running / values.length);
      }
      for (let y = y0; y < y1; y += 1) {
        for (let x = x0; x < x1; x += 1) {
          const value = clamp(Math.round(image.data[y * width + x] ?? 0), 0, 255);
          out[y * width + x] = clamp(Math.round((cdf[value] ?? 0) * 255), 0, 255);
        }
      }
    }
  }
  return { width, height, data: out };
}

export function imageContrast(image: Image): number {
  const min = Math.min(...image.data);
  const max = Math.max(...image.data);
  return (max - min) / 255;
}
