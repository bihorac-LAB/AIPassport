/**
 * Hand-built SVG charts.
 *
 * Every chart is theme-aware (tokens, not literals), responsive (viewBox + preserveAspectRatio),
 * described to assistive tech (`role="img"` + generated summary), and pairs with a keyboard-reachable
 * data table so a chart is never the only way to get the numbers. Marks differ by shape and label as
 * well as color, so nothing depends on color perception alone.
 */

import { useId, useMemo, useState, type ReactNode } from 'react';

const VIZ = ['var(--viz-1)', 'var(--viz-2)', 'var(--viz-3)', 'var(--viz-4)', 'var(--viz-5)', 'var(--viz-6)'];
const SHAPES = ['circle', 'square', 'triangle', 'diamond'] as const;

export function vizColor(index: number): string {
  return VIZ[index % VIZ.length] as string;
}

type Padding = { top: number; right: number; bottom: number; left: number };
const DEFAULT_PADDING: Padding = { top: 16, right: 20, bottom: 36, left: 48 };

function niceTicks(min: number, max: number, count = 5): number[] {
  if (max === min) return [min];
  const span = max - min;
  const rawStep = span / (count - 1);
  const magnitude = 10 ** Math.floor(Math.log10(rawStep));
  const normalized = rawStep / magnitude;
  const step =
    (normalized <= 1 ? 1 : normalized <= 2 ? 2 : normalized <= 5 ? 5 : 10) * magnitude;
  const start = Math.floor(min / step) * step;
  const ticks: number[] = [];
  for (let v = start; v <= max + step * 0.5; v += step) ticks.push(Number(v.toFixed(10)));
  return ticks.filter((t) => t >= min - step * 0.001);
}

function fmt(value: number): string {
  if (Number.isInteger(value)) return String(value);
  if (Math.abs(value) >= 100) return value.toFixed(0);
  if (Math.abs(value) >= 1) return value.toFixed(2).replace(/\.0+$/, '');
  return value.toFixed(3).replace(/0+$/, '').replace(/\.$/, '');
}

// ── Shared frame ─────────────────────────────────────────────────────────────

export function ChartFrame({
  title,
  description,
  width = 640,
  height = 320,
  children,
  caption,
  legend,
  table,
}: {
  title: string;
  description: string;
  width?: number;
  height?: number;
  children: ReactNode;
  caption?: string;
  legend?: Array<{ label: string; color: string }>;
  table?: { columns: string[]; rows: Array<Array<string | number>> };
}) {
  const titleId = useId();
  const descId = useId();
  const [showTable, setShowTable] = useState(false);

  return (
    <figure className="chart" style={{ margin: 0 }}>
      <svg
        className="chart__frame"
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="xMidYMid meet"
        role="img"
        aria-labelledby={`${titleId} ${descId}`}
      >
        <title id={titleId}>{title}</title>
        <desc id={descId}>{description}</desc>
        {children}
      </svg>
      {legend && legend.length > 0 ? (
        <ul className="chart-legend" style={{ listStyle: 'none', padding: 0 }}>
          {legend.map((item) => (
            <li className="chart-legend__item" key={item.label}>
              <span
                className="chart-legend__swatch"
                style={{ background: item.color }}
                aria-hidden="true"
              />
              {item.label}
            </li>
          ))}
        </ul>
      ) : null}
      {caption ? <figcaption className="chart__caption">{caption}</figcaption> : null}
      {table ? (
        <>
          <button
            type="button"
            className="btn btn--ghost btn--sm"
            style={{ marginTop: 'var(--sp-2)' }}
            aria-expanded={showTable}
            onClick={() => setShowTable((v) => !v)}
          >
            {showTable ? 'Hide data table' : 'Show data table'}
          </button>
          {showTable ? (
            <div className="table-wrap" style={{ marginTop: 'var(--sp-2)' }}>
              <table className="data-table">
                <caption className="sr-only">{title}</caption>
                <thead>
                  <tr>
                    {table.columns.map((column) => (
                      <th key={column} scope="col">
                        {column}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {table.rows.map((row, index) => (
                    <tr key={index}>
                      {row.map((cell, cellIndex) => (
                        <td key={cellIndex} className={typeof cell === 'number' ? 'num' : undefined}>
                          {typeof cell === 'number' ? fmt(cell) : cell}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : null}
        </>
      ) : null}
    </figure>
  );
}

function Axes({
  width,
  height,
  padding,
  xTicks,
  yTicks,
  xScale,
  yScale,
  xLabel,
  yLabel,
  xTickFormat = fmt,
  yTickFormat = fmt,
}: {
  width: number;
  height: number;
  padding: Padding;
  xTicks: number[];
  yTicks: number[];
  xScale: (v: number) => number;
  yScale: (v: number) => number;
  xLabel: string;
  yLabel: string;
  xTickFormat?: (v: number) => string;
  yTickFormat?: (v: number) => string;
}) {
  return (
    <g aria-hidden="true">
      {yTicks.map((tick) => (
        <g key={`y${tick}`}>
          <line
            x1={padding.left}
            x2={width - padding.right}
            y1={yScale(tick)}
            y2={yScale(tick)}
            stroke="var(--viz-grid)"
            strokeWidth={1}
          />
          <text
            x={padding.left - 8}
            y={yScale(tick)}
            textAnchor="end"
            dominantBaseline="middle"
            fill="var(--viz-axis)"
            fontSize={11}
          >
            {yTickFormat(tick)}
          </text>
        </g>
      ))}
      {xTicks.map((tick) => (
        <text
          key={`x${tick}`}
          x={xScale(tick)}
          y={height - padding.bottom + 16}
          textAnchor="middle"
          fill="var(--viz-axis)"
          fontSize={11}
        >
          {xTickFormat(tick)}
        </text>
      ))}
      <line
        x1={padding.left}
        x2={width - padding.right}
        y1={height - padding.bottom}
        y2={height - padding.bottom}
        stroke="var(--viz-axis)"
        strokeWidth={1}
      />
      <text
        x={(padding.left + width - padding.right) / 2}
        y={height - 4}
        textAnchor="middle"
        fill="var(--viz-axis)"
        fontSize={11}
        fontWeight={600}
      >
        {xLabel}
      </text>
      <text
        x={12}
        y={(padding.top + height - padding.bottom) / 2}
        textAnchor="middle"
        fill="var(--viz-axis)"
        fontSize={11}
        fontWeight={600}
        transform={`rotate(-90 12 ${(padding.top + height - padding.bottom) / 2})`}
      >
        {yLabel}
      </text>
    </g>
  );
}

// ── Line chart ───────────────────────────────────────────────────────────────

export type Series = {
  label: string;
  points: Array<{ x: number; y: number }>;
  color?: string;
  dashed?: boolean;
};

export function LineChart({
  title,
  series,
  xLabel,
  yLabel,
  yDomain,
  xDomain,
  caption,
  height = 300,
  width = 640,
  markers,
}: {
  title: string;
  series: Series[];
  xLabel: string;
  yLabel: string;
  yDomain?: [number, number];
  xDomain?: [number, number];
  caption?: string;
  height?: number;
  width?: number;
  markers?: Array<{ x: number; label: string }>;
}) {
  const padding = DEFAULT_PADDING;
  const all = series.flatMap((s) => s.points);
  const xs = all.map((p) => p.x);
  const ys = all.map((p) => p.y);
  const [xMin, xMax] = xDomain ?? [Math.min(...xs, 0), Math.max(...xs, 1)];
  const [yMin, yMax] = yDomain ?? [Math.min(...ys, 0), Math.max(...ys, 1)];

  const xScale = (v: number) =>
    padding.left + ((v - xMin) / (xMax - xMin || 1)) * (width - padding.left - padding.right);
  const yScale = (v: number) =>
    height - padding.bottom - ((v - yMin) / (yMax - yMin || 1)) * (height - padding.top - padding.bottom);

  const description = series
    .map((s) => {
      const first = s.points[0];
      const last = s.points[s.points.length - 1];
      if (!first || !last) return `${s.label}: no data.`;
      return `${s.label} runs from ${fmt(first.y)} at ${fmt(first.x)} to ${fmt(last.y)} at ${fmt(last.x)}.`;
    })
    .join(' ');

  const table = {
    columns: [xLabel, ...series.map((s) => s.label)],
    rows: (series[0]?.points ?? []).map((point, index) => [
      point.x,
      ...series.map((s) => s.points[index]?.y ?? ''),
    ]) as Array<Array<string | number>>,
  };

  return (
    <ChartFrame
      title={title}
      description={description}
      width={width}
      height={height}
      caption={caption}
      legend={series.map((s, i) => ({ label: s.label, color: s.color ?? vizColor(i) }))}
      table={table}
    >
      <Axes
        width={width}
        height={height}
        padding={padding}
        xTicks={niceTicks(xMin, xMax, 6)}
        yTicks={niceTicks(yMin, yMax, 5)}
        xScale={xScale}
        yScale={yScale}
        xLabel={xLabel}
        yLabel={yLabel}
      />
      {markers?.map((marker) => (
        <g key={marker.label}>
          <line
            x1={xScale(marker.x)}
            x2={xScale(marker.x)}
            y1={padding.top}
            y2={height - padding.bottom}
            stroke="var(--accent)"
            strokeWidth={1.5}
            strokeDasharray="4 3"
          />
          <text
            x={xScale(marker.x) + 5}
            y={padding.top + 11}
            fill="var(--accent)"
            fontSize={11}
            fontWeight={600}
          >
            {marker.label}
          </text>
        </g>
      ))}
      {series.map((s, i) => {
        const color = s.color ?? vizColor(i);
        const path = s.points
          .map((p, index) => `${index === 0 ? 'M' : 'L'}${xScale(p.x)},${yScale(p.y)}`)
          .join(' ');
        const shape = SHAPES[i % SHAPES.length] as (typeof SHAPES)[number];
        return (
          <g key={s.label}>
            <path
              d={path}
              fill="none"
              stroke={color}
              strokeWidth={2.25}
              strokeDasharray={s.dashed ? '6 4' : undefined}
              strokeLinejoin="round"
              strokeLinecap="round"
            />
            {s.points.length <= 40
              ? s.points.map((p, index) => (
                  <Mark
                    key={index}
                    shape={shape}
                    x={xScale(p.x)}
                    y={yScale(p.y)}
                    color={color}
                    size={3.5}
                  />
                ))
              : null}
          </g>
        );
      })}
    </ChartFrame>
  );
}

function Mark({
  shape,
  x,
  y,
  color,
  size = 4,
}: {
  shape: (typeof SHAPES)[number];
  x: number;
  y: number;
  color: string;
  size?: number;
}) {
  if (shape === 'square') {
    return <rect x={x - size} y={y - size} width={size * 2} height={size * 2} fill={color} />;
  }
  if (shape === 'triangle') {
    return (
      <polygon
        points={`${x},${y - size * 1.2} ${x + size * 1.1},${y + size} ${x - size * 1.1},${y + size}`}
        fill={color}
      />
    );
  }
  if (shape === 'diamond') {
    return (
      <polygon
        points={`${x},${y - size * 1.3} ${x + size * 1.2},${y} ${x},${y + size * 1.3} ${x - size * 1.2},${y}`}
        fill={color}
      />
    );
  }
  return <circle cx={x} cy={y} r={size} fill={color} />;
}

// ── Bar chart ────────────────────────────────────────────────────────────────

export function BarChart({
  title,
  bars,
  yLabel,
  xLabel = '',
  yDomain,
  caption,
  height = 280,
  width = 640,
  referenceLine,
  valueFormat = (v: number) => fmt(v),
}: {
  title: string;
  bars: Array<{ label: string; value: number; color?: string; note?: string }>;
  yLabel: string;
  xLabel?: string;
  yDomain?: [number, number];
  caption?: string;
  height?: number;
  width?: number;
  referenceLine?: { value: number; label: string };
  valueFormat?: (value: number) => string;
}) {
  const padding: Padding = { ...DEFAULT_PADDING, bottom: 48 };
  const values = bars.map((b) => b.value);
  const [yMin, yMax] = yDomain ?? [
    Math.min(0, ...values),
    Math.max(...values, referenceLine?.value ?? 0) * 1.12 || 1,
  ];
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const slot = plotWidth / Math.max(1, bars.length);
  const barWidth = Math.min(72, slot * 0.62);
  const yScale = (v: number) => padding.top + plotHeight - ((v - yMin) / (yMax - yMin || 1)) * plotHeight;

  const description = bars.map((b) => `${b.label}: ${valueFormat(b.value)}`).join('. ');

  return (
    <ChartFrame
      title={title}
      description={description}
      width={width}
      height={height}
      caption={caption}
      table={{
        columns: [xLabel || 'Category', yLabel],
        rows: bars.map((b) => [b.label, valueFormat(b.value)]),
      }}
    >
      <Axes
        width={width}
        height={height}
        padding={padding}
        xTicks={[]}
        yTicks={niceTicks(yMin, yMax, 5)}
        xScale={() => 0}
        yScale={yScale}
        xLabel={xLabel}
        yLabel={yLabel}
      />
      {referenceLine ? (
        <g aria-hidden="true">
          <line
            x1={padding.left}
            x2={width - padding.right}
            y1={yScale(referenceLine.value)}
            y2={yScale(referenceLine.value)}
            stroke="var(--accent)"
            strokeWidth={1.5}
            strokeDasharray="5 4"
          />
          <text
            x={width - padding.right}
            y={yScale(referenceLine.value) - 5}
            textAnchor="end"
            fill="var(--accent)"
            fontSize={11}
            fontWeight={600}
          >
            {referenceLine.label}
          </text>
        </g>
      ) : null}
      {bars.map((bar, index) => {
        const cx = padding.left + slot * index + slot / 2;
        const top = yScale(Math.max(bar.value, yMin));
        const base = yScale(Math.max(0, yMin));
        return (
          <g key={bar.label}>
            <rect
              x={cx - barWidth / 2}
              y={Math.min(top, base)}
              width={barWidth}
              height={Math.max(1, Math.abs(base - top))}
              fill={bar.color ?? vizColor(index)}
              rx={3}
            />
            <text
              x={cx}
              y={Math.min(top, base) - 6}
              textAnchor="middle"
              fill="var(--text)"
              fontSize={11}
              fontWeight={650}
            >
              {valueFormat(bar.value)}
            </text>
            <text
              x={cx}
              y={height - padding.bottom + 16}
              textAnchor="middle"
              fill="var(--viz-axis)"
              fontSize={11}
            >
              {bar.label.length > 16 ? `${bar.label.slice(0, 15)}…` : bar.label}
            </text>
            {bar.note ? (
              <text
                x={cx}
                y={height - padding.bottom + 30}
                textAnchor="middle"
                fill="var(--text-faint)"
                fontSize={10}
              >
                {bar.note}
              </text>
            ) : null}
          </g>
        );
      })}
    </ChartFrame>
  );
}

// ── Histogram (supports two overlaid distributions) ──────────────────────────

export function Histogram({
  title,
  distributions,
  xLabel,
  caption,
  height = 280,
  width = 640,
  binCount = 24,
  domain,
}: {
  title: string;
  distributions: Array<{ label: string; values: number[]; color?: string }>;
  xLabel: string;
  caption?: string;
  height?: number;
  width?: number;
  binCount?: number;
  domain?: [number, number];
}) {
  const padding = DEFAULT_PADDING;
  const all = distributions.flatMap((d) => d.values);
  const [lo, hi] = domain ?? [Math.min(...all), Math.max(...all)];
  const binWidth = (hi - lo) / binCount || 1;

  const binned = distributions.map((d) => {
    const counts = new Array<number>(binCount).fill(0);
    for (const value of d.values) {
      const index = Math.min(binCount - 1, Math.max(0, Math.floor((value - lo) / binWidth)));
      counts[index] = (counts[index] ?? 0) + 1;
    }
    const total = d.values.length || 1;
    return { ...d, density: counts.map((c) => c / total) };
  });

  const maxDensity = Math.max(0.0001, ...binned.flatMap((b) => b.density));
  const plotWidth = width - padding.left - padding.right;
  const plotHeight = height - padding.top - padding.bottom;
  const xScale = (v: number) => padding.left + ((v - lo) / (hi - lo || 1)) * plotWidth;
  const yScale = (v: number) => padding.top + plotHeight - (v / maxDensity) * plotHeight;

  const description = binned
    .map((b) => {
      const mean = b.values.reduce((a, v) => a + v, 0) / (b.values.length || 1);
      return `${b.label} centers near ${fmt(mean)}.`;
    })
    .join(' ');

  return (
    <ChartFrame
      title={title}
      description={description}
      width={width}
      height={height}
      caption={caption}
      legend={binned.map((b, i) => ({ label: b.label, color: b.color ?? vizColor(i) }))}
      table={{
        columns: ['Bin start', ...binned.map((b) => `${b.label} (share)`)],
        rows: Array.from({ length: binCount }, (_, i) => [
          fmt(lo + i * binWidth),
          ...binned.map((b) => (b.density[i] ?? 0).toFixed(3)),
        ]),
      }}
    >
      <Axes
        width={width}
        height={height}
        padding={padding}
        xTicks={niceTicks(lo, hi, 6)}
        yTicks={[]}
        xScale={xScale}
        yScale={yScale}
        xLabel={xLabel}
        yLabel="Share of cases"
      />
      {binned.map((b, seriesIndex) => (
        <g key={b.label}>
          {b.density.map((density, i) => {
            if (density === 0) return null;
            const x = xScale(lo + i * binWidth);
            const w = Math.max(1, plotWidth / binCount - 1);
            const y = yScale(density);
            return (
              <rect
                key={i}
                x={x}
                y={y}
                width={w}
                height={padding.top + plotHeight - y}
                fill={b.color ?? vizColor(seriesIndex)}
                opacity={binned.length > 1 ? 0.55 : 0.85}
              />
            );
          })}
        </g>
      ))}
    </ChartFrame>
  );
}

// ── Scatter ──────────────────────────────────────────────────────────────────

export function ScatterChart({
  title,
  groups,
  xLabel,
  yLabel,
  caption,
  height = 320,
  width = 640,
  hLine,
}: {
  title: string;
  groups: Array<{ label: string; points: Array<{ x: number; y: number }>; color?: string }>;
  xLabel: string;
  yLabel: string;
  caption?: string;
  height?: number;
  width?: number;
  hLine?: { value: number; label: string };
}) {
  const padding = DEFAULT_PADDING;
  const all = groups.flatMap((g) => g.points);
  const xs = all.map((p) => p.x);
  const ys = all.map((p) => p.y);
  const xMin = Math.min(...xs, 0);
  const xMax = Math.max(...xs, 1);
  const yMin = Math.min(...ys, 0);
  const yMax = Math.max(...ys, 1) * 1.05;

  const xScale = (v: number) =>
    padding.left + ((v - xMin) / (xMax - xMin || 1)) * (width - padding.left - padding.right);
  const yScale = (v: number) =>
    height - padding.bottom - ((v - yMin) / (yMax - yMin || 1)) * (height - padding.top - padding.bottom);

  const description = groups
    .map((g) => `${g.label}: ${g.points.length} points.`)
    .join(' ');

  return (
    <ChartFrame
      title={title}
      description={description}
      width={width}
      height={height}
      caption={caption}
      legend={groups.map((g, i) => ({ label: g.label, color: g.color ?? vizColor(i) }))}
    >
      <Axes
        width={width}
        height={height}
        padding={padding}
        xTicks={niceTicks(xMin, xMax, 6)}
        yTicks={niceTicks(yMin, yMax, 5)}
        xScale={xScale}
        yScale={yScale}
        xLabel={xLabel}
        yLabel={yLabel}
      />
      {hLine ? (
        <g aria-hidden="true">
          <line
            x1={padding.left}
            x2={width - padding.right}
            y1={yScale(hLine.value)}
            y2={yScale(hLine.value)}
            stroke="var(--accent)"
            strokeDasharray="5 4"
            strokeWidth={1.5}
          />
          <text
            x={width - padding.right}
            y={yScale(hLine.value) - 5}
            textAnchor="end"
            fill="var(--accent)"
            fontSize={11}
            fontWeight={600}
          >
            {hLine.label}
          </text>
        </g>
      ) : null}
      {groups.map((group, groupIndex) => {
        const color = group.color ?? vizColor(groupIndex);
        const shape = SHAPES[groupIndex % SHAPES.length] as (typeof SHAPES)[number];
        return (
          <g key={group.label} opacity={0.85}>
            {group.points.map((point, index) => (
              <Mark
                key={index}
                shape={shape}
                x={xScale(point.x)}
                y={yScale(point.y)}
                color={color}
                size={3.2}
              />
            ))}
          </g>
        );
      })}
    </ChartFrame>
  );
}

// ── Confusion matrix ─────────────────────────────────────────────────────────

export function ConfusionMatrix({
  tn,
  fp,
  fn,
  tp,
  positiveLabel = 'Disease',
  negativeLabel = 'No disease',
}: {
  tn: number;
  fp: number;
  fn: number;
  tp: number;
  positiveLabel?: string;
  negativeLabel?: string;
}) {
  const cells = [
    { row: 0, col: 0, value: tn, kind: 'True negative', good: true },
    { row: 0, col: 1, value: fp, kind: 'False positive', good: false },
    { row: 1, col: 0, value: fn, kind: 'False negative', good: false },
    { row: 1, col: 1, value: tp, kind: 'True positive', good: true },
  ];

  return (
    <div className="table-wrap">
      <table className="data-table">
        <caption className="sr-only">
          Confusion matrix. True negatives {tn}, false positives {fp}, false negatives {fn}, true
          positives {tp}.
        </caption>
        <thead>
          <tr>
            <th scope="col">
              <span className="sr-only">Actual class</span>
            </th>
            <th scope="col" className="num">
              Predicted no
            </th>
            <th scope="col" className="num">
              Predicted yes
            </th>
          </tr>
        </thead>
        <tbody>
          {[negativeLabel, positiveLabel].map((label, rowIndex) => (
            <tr key={label}>
              <th scope="row" style={{ whiteSpace: 'normal', maxWidth: '11rem' }}>
                Actual: {label}
              </th>
              {cells
                .filter((cell) => cell.row === rowIndex)
                .map((cell) => (
                  <td
                    key={cell.kind}
                    className="num"
                    style={{
                      background: cell.good ? 'var(--success-soft)' : 'var(--danger-soft)',
                      fontWeight: 650,
                      whiteSpace: 'normal',
                    }}
                  >
                    {cell.value}
                    <span
                      style={{
                        display: 'block',
                        fontWeight: 500,
                        fontSize: 'var(--text-xs)',
                        color: 'var(--text-muted)',
                      }}
                    >
                      {cell.kind}
                    </span>
                  </td>
                ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

// ── Pixel grid (imaging activities) ──────────────────────────────────────────

export function PixelGrid({
  title,
  pixels,
  gridWidth,
  showValues = false,
  cellSize,
  description,
  caption,
  highlight,
}: {
  title: string;
  pixels: number[];
  gridWidth: number;
  showValues?: boolean;
  cellSize?: number;
  description?: string;
  caption?: string;
  highlight?: { x: number; y: number; size: number };
}) {
  const rows = Math.ceil(pixels.length / gridWidth);
  const size = cellSize ?? Math.max(4, Math.floor(420 / gridWidth));
  const width = gridWidth * size;
  const height = rows * size;

  const summary = useMemo(() => {
    if (description) return description;
    const min = Math.min(...pixels);
    const max = Math.max(...pixels);
    const mean = pixels.reduce((a, b) => a + b, 0) / (pixels.length || 1);
    return `Grayscale image, ${gridWidth} by ${rows} pixels. Intensity ranges ${min} to ${max}, mean ${mean.toFixed(0)} of 255.`;
  }, [description, gridWidth, pixels, rows]);

  return (
    <ChartFrame
      title={title}
      description={summary}
      width={width}
      height={height}
      caption={caption}
    >
      {pixels.map((value, index) => {
        const x = (index % gridWidth) * size;
        const y = Math.floor(index / gridWidth) * size;
        const clamped = Math.max(0, Math.min(255, Math.round(value)));
        return (
          <g key={index}>
            <rect x={x} y={y} width={size} height={size} fill={`rgb(${clamped},${clamped},${clamped})`} />
            {showValues && size >= 26 ? (
              <text
                x={x + size / 2}
                y={y + size / 2}
                textAnchor="middle"
                dominantBaseline="middle"
                fontSize={Math.min(11, size / 2.4)}
                fill={clamped > 130 ? '#111' : '#f5f5f5'}
                fontFamily="var(--font-mono)"
              >
                {clamped}
              </text>
            ) : null}
          </g>
        );
      })}
      {highlight ? (
        <rect
          x={highlight.x * size}
          y={highlight.y * size}
          width={highlight.size * size}
          height={highlight.size * size}
          fill="none"
          stroke="var(--aip-orange)"
          strokeWidth={2.5}
        />
      ) : null}
    </ChartFrame>
  );
}
