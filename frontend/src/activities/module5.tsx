import { useMemo, useState } from 'react';
import { BarChart, PixelGrid } from '@/components/charts';
import { Prose } from '@/components/Prose';
import { Button, Callout, Metric, Reveal, Segmented, Slider } from '@/components/primitives';
import { SaveState } from '@/components/SaveState';
import { useActivityAutosave } from '@/api/useAutosave';
import { useInteractionTracker } from '@/analytics/useInteractionTracker';
import { ActivityShell, LiveResult, PredictGate, type ActivityProps } from './ActivityShell';
import {
  KERNELS,
  addSaltPepper,
  applyWindow,
  attenuationPhantom,
  clahe,
  convolutionDetail,
  convolve,
  edgePhantom,
  equalize,
  histogram,
  imageContrast,
  lowContrastPhantom,
  meanFilter,
  medianFilter,
} from './lib/imaging';
import { fixed, percent } from './lib/math';

// ── Pixel reveal ─────────────────────────────────────────────────────────────

export function PixelReveal(props: ActivityProps) {
  const [showValues, setShowValues] = useState(false);
  const tracker = useInteractionTracker(props.activityKey, props);

  const small = useMemo(() => {
    const image = edgePhantom(12, 8);
    return image;
  }, []);
  const full = useMemo(() => edgePhantom(48, 32), []);

  return (
    <ActivityShell heading="See the numbers" completed={props.completed}>
      <Segmented
        label="View"
        value={showValues ? 'values' : 'image'}
        options={[
          { value: 'image', label: 'As an image' },
          { value: 'values', label: 'As numbers' },
        ]}
        onChange={(value) => {
          const next = value === 'values';
          setShowValues(next);
          tracker.parameter('view', value);
          if (next) {
            tracker.complete({ viewed_values: true });
            props.onComplete();
          }
        }}
      />

      <div className="activity__split" style={{ marginTop: 'var(--sp-4)' }}>
        <div>
          <p className="kicker">At normal scale · 48 × 32</p>
          <PixelGrid title="Simulated image at normal scale" pixels={full.data} gridWidth={full.width} cellSize={9} />
        </div>
        <div>
          <p className="kicker">Magnified · 12 × 8 corner</p>
          <LiveResult>
            <PixelGrid
              title={showValues ? 'The same pixels as numbers' : 'The same pixels magnified'}
              pixels={small.data}
              gridWidth={small.width}
              cellSize={34}
              showValues={showValues}
              caption={
                showValues
                  ? 'Each cell holds one integer from 0 (black) to 255 (white). This is what a model receives — there is no image in the computer.'
                  : 'Switch to "As numbers" to see the values behind each square.'
              }
            />
          </LiveResult>
        </div>
      </div>

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <Metric label="Values in the 48 × 32 image" value={`${full.data.length.toLocaleString()}`} note="one per pixel" />
      </div>
    </ActivityShell>
  );
}

// ── Attenuation phantom ──────────────────────────────────────────────────────

export function AttenuationPhantom(props: ActivityProps) {
  const [air, setAir] = useState(30);
  const [tissue, setTissue] = useState(105);
  const [bone, setBone] = useState(210);
  const tracker = useInteractionTracker(props.activityKey, props);

  const image = useMemo(() => attenuationPhantom(air, tissue, bone), [air, bone, tissue]);
  const bins = useMemo(() => histogram(image, 32), [image]);
  const separation = Math.min(Math.abs(tissue - air), Math.abs(bone - tissue));

  return (
    <ActivityShell heading="Build an X-ray" completed={props.completed}>
      <div className="activity__split">
        <div className="activity__controls">
          <Slider
            label="Air (lungs)"
            value={air}
            min={0}
            max={120}
            onChange={(value) => {
              setAir(value);
              tracker.parameter('air', value);
            }}
            hint="Air absorbs almost nothing, so more photons reach the detector — darker."
          />
          <Slider
            label="Soft tissue"
            value={tissue}
            min={40}
            max={220}
            onChange={(value) => {
              setTissue(value);
              tracker.parameter('tissue', value);
            }}
          />
          <Slider
            label="Bone"
            value={bone}
            min={80}
            max={255}
            onChange={(value) => {
              setBone(value);
              tracker.parameter('bone', value);
            }}
            hint="Dense material absorbs more, so fewer photons arrive — brighter."
          />
          <LiveResult>
            <Metric
              label="Smallest separation between tissue types"
              value={`${separation}`}
              tone={separation < 20 ? 'danger' : separation < 40 ? 'warning' : 'success'}
              note={separation < 20 ? 'peaks overlap — findings become invisible' : 'distinguishable'}
            />
          </LiveResult>
        </div>

        <div>
          <LiveResult>
            <PixelGrid
              title="Simulated radiograph"
              pixels={image.data}
              gridWidth={image.width}
              cellSize={7}
              description={`Simulated chest radiograph. Air-filled lungs at intensity ${air}, soft tissue at ${tissue}, bony midline at ${bone}, on a 0 to 255 scale.`}
            />
            <div style={{ marginTop: 'var(--sp-4)' }}>
              <BarChart
                title="Pixel intensity histogram"
                xLabel="Intensity (0–255)"
                yLabel="Pixel count"
                height={220}
                bars={bins.map((count, index) => ({
                  label: `${index * 8}`,
                  value: count,
                  color: 'var(--viz-1)',
                }))}
                valueFormat={(value) => value.toFixed(0)}
                caption="Three tissue types produce three peaks. Move the sliders together and watch the peaks merge — that is what a low-contrast finding looks like numerically."
              />
            </div>
          </LiveResult>
        </div>
      </div>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ air, tissue, bone, separation });
            props.onComplete();
          }}
        >
          I have made the peaks merge and separate
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── Window / level ───────────────────────────────────────────────────────────

const PRESETS = [
  { value: 'lung', label: 'Lung', centre: 60, width: 160 },
  { value: 'soft', label: 'Soft tissue', centre: 110, width: 90 },
  { value: 'bone', label: 'Bone', centre: 190, width: 130 },
  { value: 'custom', label: 'Custom', centre: 128, width: 255 },
] as const;

export function WindowLevel(props: ActivityProps) {
  const [centre, setCentre] = useState(128);
  const [width, setWidth] = useState(255);
  const tracker = useInteractionTracker(props.activityKey, props);

  const base = useMemo(() => attenuationPhantom(28, 108, 206), []);
  const windowed = useMemo(() => applyWindow(base, centre, width), [base, centre, width]);

  const visible = useMemo(() => {
    const lo = centre - width / 2;
    const hi = centre + width / 2;
    const inWindow = (value: number) => value >= lo && value <= hi;
    return {
      air: inWindow(28),
      tissue: inWindow(108),
      bone: inWindow(206),
    };
  }, [centre, width]);

  return (
    <ActivityShell heading="Window and level" completed={props.completed}>
      <div className="activity__split">
        <div className="activity__controls">
          <div style={{ display: 'flex', gap: 'var(--sp-2)', flexWrap: 'wrap' }}>
            {PRESETS.map((preset) => (
              <Button
                key={preset.value}
                size="sm"
                variant={centre === preset.centre && width === preset.width ? 'primary' : 'outline'}
                onClick={() => {
                  setCentre(preset.centre);
                  setWidth(preset.width);
                  tracker.parameter('preset', preset.value);
                }}
              >
                {preset.label}
              </Button>
            ))}
          </div>
          <Slider
            label="Window centre (level)"
            value={centre}
            min={0}
            max={255}
            onChange={(value) => {
              setCentre(value);
              tracker.parameter('centre', value);
            }}
            hint="Which intensity sits in the middle of the grey scale."
          />
          <Slider
            label="Window width"
            value={width}
            min={10}
            max={255}
            onChange={(value) => {
              setWidth(value);
              tracker.parameter('width', value);
            }}
            hint="How wide a range of values is spread across black to white. Narrow = high contrast, less range."
          />
          <LiveResult>
            <div className="metric-row">
              <Metric label="Lungs visible" value={visible.air ? 'Yes' : 'Clipped to black'} />
              <Metric label="Soft tissue visible" value={visible.tissue ? 'Yes' : 'Clipped'} />
              <Metric label="Bone visible" value={visible.bone ? 'Yes' : 'Clipped to white'} />
            </div>
          </LiveResult>
        </div>

        <div>
          <LiveResult>
            <PixelGrid
              title="After windowing"
              pixels={windowed.data}
              gridWidth={windowed.width}
              cellSize={7}
              description={`Radiograph displayed with window centre ${centre} and width ${width}. Values outside the window are clipped to pure black or pure white.`}
              caption="The underlying array never changed. Only the mapping from value to displayed grey did — and structures outside the window are simply gone."
            />
          </LiveResult>
        </div>
      </div>

      <Callout tone="info" title="Why this matters for a model">
        <p>
          If your model trained on lung-windowed images and receives bone-windowed ones, its input
          distribution has changed completely — from the same study, on the same scanner, with no
          change to the patient. This is one of the most common causes of "it worked in development".
        </p>
      </Callout>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ centre, width });
            props.onComplete();
          }}
        >
          I have tried each preset
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── Convolution lab ──────────────────────────────────────────────────────────

export function ConvolutionLab(props: ActivityProps) {
  const [kernelKey, setKernelKey] = useState('blur');
  const [position, setPosition] = useState(8);
  const tracker = useInteractionTracker(props.activityKey, props);

  const base = useMemo(() => edgePhantom(24, 18), []);
  const kernel = KERNELS[kernelKey] ?? KERNELS.identity!;
  const output = useMemo(
    () => convolve(base, kernel.kernel, kernel.divisor, kernel.offset),
    [base, kernel],
  );

  const y = Math.floor(base.height / 2);
  const detail = useMemo(
    () => convolutionDetail(base, kernel.kernel, kernel.divisor, kernel.offset, position, y),
    [base, kernel, position, y],
  );

  return (
    <ActivityShell heading="Convolution playground" completed={props.completed}>
      <Segmented
        label="Kernel"
        value={kernelKey}
        options={Object.entries(KERNELS).map(([key, entry]) => ({ value: key, label: entry.label }))}
        onChange={(value) => {
          setKernelKey(value);
          tracker.parameter('kernel', value);
        }}
      />

      <div className="activity__split" style={{ marginTop: 'var(--sp-4)' }}>
        <div>
          <p className="kicker">Input</p>
          <PixelGrid
            title="Input image"
            pixels={base.data}
            gridWidth={base.width}
            cellSize={12}
            highlight={{ x: Math.max(0, position - 1), y: y - 1, size: 3 }}
          />
          <p className="kicker" style={{ marginTop: 'var(--sp-4)' }}>
            Output
          </p>
          <LiveResult>
            <PixelGrid
              title={`Output after ${kernel.label}`}
              pixels={output.data}
              gridWidth={output.width}
              cellSize={12}
              caption={kernel.note}
            />
          </LiveResult>
        </div>

        <div>
          <Slider
            label="Kernel position (x)"
            value={position}
            min={1}
            max={base.width - 2}
            onChange={(value) => {
              setPosition(value);
              tracker.parameter('position', value);
            }}
            hint={`The orange box on the input shows the 3×3 window at x=${position}, y=${y}.`}
          />

          <LiveResult>
            <div className="table-wrap" style={{ marginTop: 'var(--sp-4)' }}>
              <table className="data-table">
                <caption className="sr-only">
                  The nine multiplications producing one output pixel
                </caption>
                <thead>
                  <tr>
                    <th scope="col" className="num">
                      Pixel
                    </th>
                    <th scope="col" className="num">
                      × Weight
                    </th>
                    <th scope="col" className="num">
                      = Product
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {detail.terms.map((term, index) => (
                    <tr key={index}>
                      <td className="num">{term.pixel}</td>
                      <td className="num">{term.weight}</td>
                      <td className="num">{term.product}</td>
                    </tr>
                  ))}
                  <tr style={{ background: 'var(--bg-inset)', fontWeight: 650 }}>
                    <td className="num" colSpan={2}>
                      Sum
                    </td>
                    <td className="num">{detail.raw}</td>
                  </tr>
                  <tr style={{ background: 'var(--accent-soft)', fontWeight: 650 }}>
                    <td className="num" colSpan={2}>
                      ÷ {kernel.divisor} {kernel.offset ? `+ ${kernel.offset}` : ''} → output
                    </td>
                    <td className="num">{detail.output}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            <p className="chart__caption">
              Nine multiplications and one addition, repeated once per pixel. A convolutional network
              does not receive these nine weights — it learns them, in hundreds of kernels across many
              layers.
            </p>
          </LiveResult>
        </div>
      </div>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ kernel: kernelKey, position });
            props.onComplete();
          }}
        >
          I have stepped through the arithmetic
        </Button>
      </div>

      <div style={{ marginTop: 'var(--sp-4)' }}>
        <Reveal label="Why the edge kernels sum to zero" eventContext={props}>
          <Prose
            body={[
              'Add up the nine weights of the vertical-edge kernel: −1 + 0 + 1 − 2 + 0 + 2 − 1 + 0 + 1 = 0.',
              'In a flat region every pixel is roughly equal, so the positive and negative contributions cancel and the output is near zero — which the offset of 128 renders as mid-grey. Only where intensity changes left-to-right does anything survive.',
              'Step the position slider across the vertical edge in the image and watch the sum swing from near zero to a large value and back.',
            ]}
          />
        </Reveal>
      </div>
    </ActivityShell>
  );
}

// ── Noise and denoising ──────────────────────────────────────────────────────

export function NoiseDenoise(props: ActivityProps) {
  const [noiseRate, setNoiseRate] = useState(0.12);
  const [filter, setFilter] = useState<'none' | 'mean' | 'median'>('none');
  const [prediction, setPrediction] = useState<string | null>(null);
  const [revealed, setRevealed] = useState(false);
  const tracker = useInteractionTracker(props.activityKey, props);

  const base = useMemo(() => edgePhantom(28, 20), []);
  const noisy = useMemo(() => addSaltPepper(base, noiseRate, 3), [base, noiseRate]);
  const filtered = useMemo(() => {
    if (filter === 'mean') return meanFilter(noisy);
    if (filter === 'median') return medianFilter(noisy);
    return noisy;
  }, [filter, noisy]);

  /** Mean absolute error against the clean original — lower is better. */
  const error = useMemo(() => {
    const total = base.data.reduce(
      (sum, value, index) => sum + Math.abs(value - (filtered.data[index] ?? 0)),
      0,
    );
    return total / base.data.length;
  }, [base.data, filtered.data]);

  return (
    <ActivityShell heading="Noise and denoising" completed={props.completed}>
      <PredictGate
        question="Salt-and-pepper noise sets scattered pixels to pure black or pure white. Which filter will recover the image better?"
        options={[
          { value: 'median', label: 'Median filter — takes the middle value of each neighbourhood.' },
          { value: 'mean', label: 'Mean filter — averages each neighbourhood.' },
          { value: 'same', label: 'They will perform about the same.' },
        ]}
        value={prediction}
        onChange={setPrediction}
        revealed={revealed}
        onReveal={() => {
          setRevealed(true);
          tracker.predict({ predicted: prediction });
        }}
      />

      {revealed ? (
        <>
          <div className="activity__split">
            <div className="activity__controls">
              <Slider
                label="Noise level"
                value={noiseRate}
                min={0}
                max={0.4}
                step={0.02}
                format={(value) => percent(value)}
                onChange={(value) => {
                  setNoiseRate(value);
                  tracker.parameter('noise', value);
                }}
              />
              <Segmented
                label="Filter"
                value={filter}
                options={[
                  { value: 'none', label: 'None' },
                  { value: 'mean', label: 'Mean 3×3' },
                  { value: 'median', label: 'Median 3×3' },
                ]}
                onChange={(value) => {
                  setFilter(value);
                  tracker.parameter('filter', value);
                }}
              />
              <LiveResult>
                <Metric
                  label="Mean absolute error vs. clean original"
                  value={fixed(error, 1)}
                  tone={error < 8 ? 'success' : error < 20 ? 'warning' : 'danger'}
                  note="lower is better"
                />
              </LiveResult>
            </div>

            <div>
              <LiveResult>
                <PixelGrid
                  title={filter === 'none' ? 'Noisy image' : `After ${filter} filter`}
                  pixels={filtered.data}
                  gridWidth={filtered.width}
                  cellSize={11}
                  caption={
                    filter === 'median'
                      ? 'The median discards the extreme values entirely and leaves edges intact.'
                      : filter === 'mean'
                        ? 'The mean averages each black and white speck into its neighbours, smearing the noise across the image and blurring the edges.'
                        : 'Scattered pure-black and pure-white pixels — impulse noise.'
                  }
                />
              </LiveResult>
            </div>
          </div>

          <Callout tone="info" title="The same property you met in Module 1">
            <p>
              A single extreme value cannot move a median but does move a mean. That is why the median
              filter wins here, and it is exactly why the median was the robust summary statistic in
              the clinical outlier lab. One idea, two contexts.
            </p>
          </Callout>

          <div style={{ marginTop: 'var(--sp-5)' }}>
            <Button
              variant="primary"
              onClick={() => {
                tracker.complete({ noiseRate, filter, error: Number(error.toFixed(2)) });
                props.onComplete();
              }}
            >
              I have compared both filters
            </Button>
          </div>
        </>
      ) : null}
    </ActivityShell>
  );
}

// ── Histogram equalization ───────────────────────────────────────────────────

export function HistogramEqualization(props: ActivityProps) {
  const [method, setMethod] = useState<'none' | 'equalize' | 'clahe'>('none');
  const [clipLimit, setClipLimit] = useState(2.5);
  const tracker = useInteractionTracker(props.activityKey, props);

  const base = useMemo(() => lowContrastPhantom(36, 24), []);
  const processed = useMemo(() => {
    if (method === 'equalize') return equalize(base);
    if (method === 'clahe') return clahe(base, 4, clipLimit);
    return base;
  }, [base, clipLimit, method]);

  const bins = useMemo(() => histogram(processed, 24), [processed]);

  return (
    <ActivityShell heading="Equalization and CLAHE" completed={props.completed}>
      <div className="activity__split">
        <div className="activity__controls">
          <Segmented
            label="Enhancement"
            value={method}
            options={[
              { value: 'none', label: 'None' },
              { value: 'equalize', label: 'Global equalization' },
              { value: 'clahe', label: 'CLAHE' },
            ]}
            onChange={(value) => {
              setMethod(value);
              tracker.parameter('method', value);
            }}
          />
          {method === 'clahe' ? (
            <Slider
              label="Clip limit"
              value={clipLimit}
              min={1}
              max={8}
              step={0.5}
              onChange={(value) => {
                setClipLimit(value);
                tracker.parameter('clip_limit', value);
              }}
              hint="How much any single intensity bin may contribute. Lower means less noise amplification and less enhancement."
            />
          ) : null}
          <LiveResult>
            <Metric
              label="Contrast (range used)"
              value={percent(imageContrast(processed))}
              note={`was ${percent(imageContrast(base))} before`}
              tone={imageContrast(processed) > 0.7 ? 'success' : undefined}
            />
          </LiveResult>
        </div>

        <div>
          <LiveResult>
            <PixelGrid
              title={
                method === 'none'
                  ? 'Original low-contrast image'
                  : method === 'equalize'
                    ? 'After global histogram equalization'
                    : 'After CLAHE'
              }
              pixels={processed.data}
              gridWidth={processed.width}
              cellSize={11}
              description={`Low-contrast image with a subtle lesion at right of centre, ${method === 'none' ? 'unenhanced' : method === 'equalize' ? 'globally equalized' : 'enhanced with CLAHE'}.`}
              caption={
                method === 'none'
                  ? 'The lesion is present in the data but occupies a narrow intensity band, so it is barely visible.'
                  : method === 'equalize'
                    ? 'The lesion is now visible — and so is the sensor noise, amplified by the same amount. Global equalization cannot distinguish them.'
                    : 'CLAHE equalizes in local tiles with a clip limit, so the lesion is enhanced without the noise being amplified as aggressively.'
              }
            />
            <div style={{ marginTop: 'var(--sp-4)' }}>
              <BarChart
                title="Intensity histogram after enhancement"
                xLabel="Intensity"
                yLabel="Pixels"
                height={200}
                bars={bins.map((count, index) => ({
                  label: `${index * 11}`,
                  value: count,
                  color: 'var(--viz-4)',
                }))}
                valueFormat={(value) => value.toFixed(0)}
                caption="Enhancement spreads a bunched-up histogram across the full range. Notice that it does not create information — it redistributes it."
              />
            </div>
          </LiveResult>
        </div>
      </div>

      <Callout tone="warning" title="The cost nobody states in the methods section">
        <p>
          Enhancement amplifies noise along with signal, and can create texture that was not in the
          original acquisition. If a downstream model or reader acts on that texture, the enhancement
          step is a patient-safety decision, not a display preference — so it belongs in the methods
          with its parameters.
        </p>
      </Callout>

      <div style={{ marginTop: 'var(--sp-5)' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ method, clipLimit });
            props.onComplete();
          }}
        >
          I have compared all three
        </Button>
      </div>
    </ActivityShell>
  );
}

// ── Imaging reproducibility checklist ────────────────────────────────────────

const CHECKLIST = [
  {
    id: 'scanner',
    label: 'Scanner make, model, and reconstruction kernel recorded',
    failure: 'Another group cannot reproduce your texture statistics, and you cannot explain a performance drop at a new site.',
  },
  {
    id: 'spacing',
    label: 'Pixel spacing and slice thickness recorded, and resampling documented',
    failure: 'Learned size cues do not transfer; a lesion spanning 20 pixels at your site spans 12 elsewhere.',
  },
  {
    id: 'window',
    label: 'Window/level or intensity normalization applied is stated',
    failure: 'The model\'s input distribution is undefined, so nobody can feed it comparable images.',
  },
  {
    id: 'preproc',
    label: 'Every preprocessing step listed in order with its parameters',
    failure: 'The pipeline cannot be rebuilt. This is the single most common reason imaging results fail to replicate.',
  },
  {
    id: 'annotators',
    label: 'Annotator count, expertise, independence, and agreement reported',
    failure: 'Your label quality — and therefore your performance ceiling — is unknown to the reader.',
  },
  {
    id: 'labeldef',
    label: 'The label definition is written down, including borderline rules',
    failure: 'Two sites will label differently and neither will know why the model transfers badly.',
  },
  {
    id: 'split',
    label: 'Split is patient-level (and site- or time-level where relevant)',
    failure: 'Reported performance is inflated by leakage and will not survive prospective use.',
  },
  {
    id: 'external',
    label: 'External validation on different equipment attempted or its absence stated',
    failure: 'Generalization is asserted rather than demonstrated.',
  },
] as const;

export function ImagingChecklist(props: ActivityProps) {
  const [checked, setChecked] = useState<string[]>([]);
  const tracker = useInteractionTracker(props.activityKey, props);
  const { status, save } = useActivityAutosave(props.activityKey, props.moduleKey, props.pageKey);

  const score = checked.length;
  const total = CHECKLIST.length;
  const missing = CHECKLIST.filter((item) => !checked.includes(item.id));

  return (
    <ActivityShell heading="Reproducibility checklist" completed={props.completed}>
      <fieldset className="choice-list">
        <legend className="choice-list__legend">
          Which of these does the pipeline you would build actually document?
        </legend>
        {CHECKLIST.map((item) => (
          <label className="choice" key={item.id}>
            <input
              type="checkbox"
              checked={checked.includes(item.id)}
              onChange={() => {
                const next = checked.includes(item.id)
                  ? checked.filter((id) => id !== item.id)
                  : [...checked, item.id];
                setChecked(next);
                tracker.parameter(item.id, !checked.includes(item.id));
                save({ checked: next, score: next.length, total }, false);
              }}
            />
            <span className="choice__body">{item.label}</span>
          </label>
        ))}
      </fieldset>

      <LiveResult>
        <div className="metric-row" style={{ marginTop: 'var(--sp-4)' }}>
          <Metric
            label="Reproducibility score"
            value={`${score} / ${total}`}
            tone={score === total ? 'success' : score >= 6 ? 'warning' : 'danger'}
          />
        </div>
        {missing.length > 0 ? (
          <Callout tone="warning" title={`${missing.length} gap${missing.length === 1 ? '' : 's'} — each is a specific failure`}>
            <ul>
              {missing.slice(0, 4).map((item) => (
                <li key={item.id} style={{ marginBottom: 'var(--sp-2)' }}>
                  <strong>{item.label}:</strong> {item.failure}
                </li>
              ))}
            </ul>
          </Callout>
        ) : (
          <Callout tone="success" title="Fully documented">
            <p>
              Every item is covered. A reader could rebuild this pipeline, and you could diagnose a
              performance drop at a new site instead of guessing.
            </p>
          </Callout>
        )}
      </LiveResult>

      <div style={{ marginTop: 'var(--sp-5)', display: 'flex', gap: 'var(--sp-3)', alignItems: 'center' }}>
        <Button
          variant="primary"
          onClick={() => {
            tracker.complete({ score, total });
            save({ checked, score, total }, true);
            props.onComplete();
          }}
        >
          Save my audit
        </Button>
        <SaveState status={status} />
      </div>
    </ActivityShell>
  );
}
