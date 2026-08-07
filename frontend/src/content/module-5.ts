import type { Module } from './types';

/**
 * Module 5 — Images.
 * Consolidates legacy microskills 5.1–5.3 and the surviving content of 5.4/5.6.
 * Legacy 5.5 (bare external iframe) was removed — see docs/legacy-audit.md §6.
 */
export const module5: Module = {
  key: 'module-5',
  position: 5,
  title: 'Images',
  subtitle: 'How a scan becomes numbers, and what happens to those numbers',
  summary:
    'Build the mental model that medical images are arrays of intensities, then run the transformations every imaging AI pipeline applies before a model ever sees a pixel.',
  accent: 'rose',
  contentVersion: 1,
  pages: [
    {
      key: 'm5p1',
      slug: 'images-as-data',
      position: 1,
      kind: 'explore',
      title: 'Images as Data',
      kicker: 'Module 5 · Page 1',
      lede:
        'An X-ray is a grid of numbers. Once you see it that way, contrast, windowing, and every "AI reads the scan" claim become concrete.',
      objectives: [
        'Describe a medical image as an array of intensity values.',
        'Explain X-ray attenuation and read an intensity histogram.',
        "Explain how window and level change a model's input without changing the data.",
      ],
      estimatedMinutes: 20,
      contentVersion: 1,
      requiredSections: ['m5p1-pixels', 'm5p1-q1', 'm5p1-attenuation', 'm5p1-q2', 'm5p1-window', 'm5p1-q3'],
      sections: [
        {
          kind: 'prose',
          id: 'm5p1-intro',
          heading: 'There is no image in the computer',
          body: [
            'A grayscale medical image is a two-dimensional array of integers. Each value is one pixel\'s intensity: 0 is black, 255 is white in an 8-bit image. A 512×512 chest X-ray is 262,144 numbers.',
            'Everything else follows. "Enhancing contrast" is arithmetic on those numbers. A convolutional network "looking at" the scan is multiplying small windows of them. Nothing in the pipeline knows it is a lung.',
          ],
        },
        {
          kind: 'activity',
          id: 'm5p1-pixels',
          activity: 'pixel-reveal',
          heading: 'See the numbers',
          intro:
            'A small image at real scale, then magnified until each pixel shows its value. Toggle between them.',
          summary:
            'Learner toggles between rendered pixels and their numeric values to internalize that an image is an array.',
        },
        {
          kind: 'question',
          id: 'm5p1-q1',
          question: {
            key: 'm5p1.q1',
            version: 1,
            type: 'single_choice',
            prompt: 'How much data is a single 512×512 8-bit grayscale slice?',
            options: [
              {
                value: 'quarter_mb',
                label: 'About 262,000 values — roughly a quarter of a megabyte uncompressed.',
                feedback:
                  'Correct: 512 × 512 = 262,144 bytes at one byte per pixel. A 300-slice CT is therefore ~79 MB before compression, which is why imaging AI is an infrastructure problem as much as a modelling one.',
              },
              {
                value: 'few_kb',
                label: 'A few kilobytes.',
                feedback:
                  'That would be about 3,000 pixels — a 55×55 image. Compressed formats can reach a few hundred KB, but the raw array is much larger.',
              },
              {
                value: 'megabytes',
                label: 'Tens of megabytes.',
                feedback:
                  'That is the scale of a full CT *volume*, not one slice.',
              },
            ],
            correct: 'quarter_mb',
            explanation:
              'Real CT is usually 12–16 bit, so multiply by two. This is why imaging models are trained on GPUs and why moving a study between institutions is non-trivial.',
          },
        },
        {
          kind: 'prose',
          id: 'm5p1-atten-intro',
          heading: 'Where the numbers come from',
          body: [
            'X-rays passing through the body are absorbed at different rates. Dense material — bone, metal — absorbs more, so fewer photons reach the detector and the pixel reads **brighter**. Air absorbs almost nothing, so more photons arrive and the pixel reads **darker**.',
            'That is the whole physics of a radiograph, and it explains every appearance you were taught to recognize: bone white, lung black, soft tissue grey.',
          ],
        },
        {
          kind: 'activity',
          id: 'm5p1-attenuation',
          activity: 'attenuation-phantom',
          heading: 'Build an X-ray',
          intro:
            'Set the density of air, soft tissue, and bone. The phantom and its intensity histogram update together — watch how three tissue types make three peaks.',
          summary:
            'Learner adjusts tissue densities in a simulated radiograph and sees the corresponding peaks move in the intensity histogram.',
        },
        {
          kind: 'question',
          id: 'm5p1-q2',
          question: {
            key: 'm5p1.q2',
            version: 1,
            type: 'single_choice',
            prompt:
              'You bring the soft-tissue density close to the bone density. What happens to the histogram, and why does it matter for AI?',
            options: [
              {
                value: 'merge',
                label: 'The two peaks merge, and a model can no longer separate the tissues by intensity alone.',
                feedback:
                  'Correct. Overlapping intensity distributions are exactly why low-contrast findings are hard for both radiologists and models, and why contrast enhancement exists as a preprocessing step.',
              },
              {
                value: 'brighter',
                label: 'The image gets brighter overall but the peaks stay separate.',
                feedback:
                  'Overall brightness shifts, but the important change is the loss of *separation* between the two peaks.',
              },
              {
                value: 'nothing',
                label: 'Nothing important — the model learns shape, not intensity.',
                feedback:
                  'Convolutional networks learn from local intensity *patterns*. If two tissues have the same intensity, there is no local pattern distinguishing them at the boundary.',
              },
            ],
            correct: 'merge',
            explanation:
              'Separable intensity distributions are the substrate everything else is built on. When they overlap, you need contrast enhancement, a different modality, or a different feature.',
          },
        },
        {
          kind: 'prose',
          id: 'm5p1-window-intro',
          heading: 'Windowing: the same data, a different view',
          body: [
            'Radiologists do not look at raw CT. They pick a **window** — a range of values mapped across the full black-to-white scale. A lung window makes airways legible; a bone window on the same slice makes fractures legible. No data changes; the mapping does.',
            'This matters for AI in a way that catches teams out: if your model was trained on lung-windowed images and you feed it bone-windowed ones, you have changed its input distribution completely, even though the underlying study is identical.',
          ],
        },
        {
          kind: 'activity',
          id: 'm5p1-window',
          activity: 'window-level',
          heading: 'Window and level',
          intro:
            'Move the window centre and width across a simulated CT slice. Watch which structures become visible and which disappear.',
          summary:
            'Learner adjusts window centre and width and observes which structures become visible under each setting.',
        },
        {
          kind: 'question',
          id: 'm5p1-q3',
          question: {
            key: 'm5p1.q3',
            version: 1,
            type: 'multi_choice',
            prompt:
              'A radiology AI trained at one hospital performs poorly at another. Which image-level differences could explain it? Select all that apply.',
            options: [
              {
                value: 'window',
                label: 'Different default window/level presets.',
                feedback: 'Yes — this alone can shift the input distribution beyond what the model saw.',
              },
              {
                value: 'scanner',
                label: 'Different scanner manufacturers and reconstruction kernels.',
                feedback:
                  'Yes. Reconstruction kernels change texture and noise characteristics, which convolutional models are sensitive to.',
              },
              {
                value: 'resolution',
                label: 'Different pixel spacing and slice thickness.',
                feedback:
                  'Yes. A lesion spanning 20 pixels at one site spans 12 at another, so learned size cues stop applying.',
              },
              {
                value: 'labels',
                label: 'Different conventions for what counts as a positive finding.',
                feedback:
                  'Yes — and this is the one that gets missed because it is not visible in the image at all. It is a label-definition mismatch.',
              },
            ],
            correct: ['window', 'scanner', 'resolution', 'labels'],
            explanation:
              'All four. This is why imaging AI needs external validation on genuinely different equipment, and why the paper must state acquisition parameters.',
          },
        },
        {
          kind: 'reveal',
          id: 'm5p1-more',
          label: 'Learn more: choosing a modality',
          body: [
            '**Radiograph** — fast, cheap, low dose, projects 3D onto 2D so structures overlap. **CT** — cross-sectional, excellent for bone, lung, and acute bleeding; ionizing dose. **MRI** — superb soft-tissue contrast and no ionizing radiation; slow, expensive, many sequences. **Ultrasound** — real-time, portable, no radiation; heavily operator-dependent, which makes reproducible AI harder. **Histopathology** — cellular resolution over gigapixel slides; staining variation between labs is the dominant generalization problem.',
            'For AI specifically, the question that decides feasibility is: how consistent is acquisition across sites? Consistency, not resolution, is what determines whether a model transfers.',
          ],
        },
      ],
    },
    {
      key: 'm5p2',
      slug: 'enhancing-images',
      position: 2,
      kind: 'apply',
      title: 'Enhancing and Analyzing',
      kicker: 'Module 5 · Page 2',
      lede:
        'Convolution is a 3×3 window of multiplications. It is also the core operation of every image AI model in use today.',
      objectives: [
        'Compute a convolution by hand and explain why an edge kernel sums to zero.',
        'Match a denoising filter to the type of noise present.',
        'Describe the cost of contrast enhancement as well as its benefit.',
        'Audit an imaging pipeline for reproducibility.',
      ],
      estimatedMinutes: 24,
      contentVersion: 1,
      requiredSections: ['m5p2-kernel', 'm5p2-q1', 'm5p2-noise', 'm5p2-q2', 'm5p2-histogram', 'm5p2-checklist'],
      sections: [
        {
          kind: 'prose',
          id: 'm5p2-intro',
          heading: 'One operation, everything else follows',
          body: [
            'Slide a small grid of numbers — a **kernel** — across the image. At each position, multiply the overlapping pixels by the kernel values and sum them. That sum becomes the output pixel. That is convolution.',
            'Change the nine numbers and the same operation blurs, sharpens, or finds edges. A convolutional neural network does not use a kernel you designed; it *learns* the nine numbers, in hundreds of kernels, arranged in layers. The arithmetic below is the arithmetic in the network.',
          ],
        },
        {
          kind: 'activity',
          id: 'm5p2-kernel',
          activity: 'convolution-lab',
          heading: 'Convolution playground',
          intro:
            'Pick a kernel, then step it across the image position by position and watch the nine multiplications that produce each output pixel.',
          summary:
            'Learner applies identity, blur, sharpen, and edge-detection kernels and steps through the per-position arithmetic.',
        },
        {
          kind: 'question',
          id: 'm5p2-q1',
          question: {
            key: 'm5p2.q1',
            version: 1,
            type: 'single_choice',
            prompt:
              'A vertical edge-detection kernel has negative values on its left column and positive values on its right. Why does it output near zero in a uniform region?',
            options: [
              {
                value: 'cancel',
                label: 'The positive and negative contributions cancel when the neighbourhood is uniform.',
                feedback:
                  'Correct. The kernel measures *difference*, not brightness. Uniform region → no difference → near-zero output. It only responds where intensity changes.',
              },
              {
                value: 'small',
                label: 'Because the kernel values are small.',
                feedback:
                  'The magnitude of the values sets the response strength, not whether it is zero. The cancellation is what produces zero.',
              },
              {
                value: 'normalized',
                label: 'Because the output is normalized to zero.',
                feedback:
                  'No normalization step is involved. The zero arises directly from the arithmetic.',
              },
            ],
            correct: 'cancel',
            explanation:
              'Every edge detector works this way: sum to zero, so flat regions vanish and boundaries survive. This is the first thing a trained network learns in its earliest layer.',
          },
        },
        {
          kind: 'activity',
          id: 'm5p2-noise',
          activity: 'noise-denoise',
          heading: 'Noise and denoising',
          intro:
            'Add salt-and-pepper noise, then try a mean filter and a median filter on it. One works far better here — predict which before you look.',
          summary:
            'Learner compares mean and median filtering on impulse noise and sees why the median preserves edges.',
        },
        {
          kind: 'question',
          id: 'm5p2-q2',
          question: {
            key: 'm5p2.q2',
            version: 1,
            type: 'single_choice',
            prompt: 'Why does a median filter beat a mean filter on salt-and-pepper noise?',
            options: [
              {
                value: 'outlier',
                label: 'A single extreme value cannot move a median, but it does move a mean.',
                feedback:
                  'Correct — the same robustness property you saw with clinical outliers in Module 1. Salt-and-pepper noise is impulse noise: extreme, isolated values. The median discards them; the mean averages them in and smears them across the neighbourhood.',
              },
              {
                value: 'faster',
                label: 'The median filter is faster.',
                feedback:
                  'It is actually slower — it sorts each neighbourhood. It wins on quality, not speed.',
              },
              {
                value: 'larger',
                label: 'The median filter uses a larger window.',
                feedback:
                  'Both use the same window. The difference is the statistic computed inside it.',
              },
            ],
            correct: 'outlier',
            explanation:
              'Match the filter to the noise. Median for impulse noise, Gaussian for additive sensor noise, and anisotropic or non-local methods when edge preservation is critical.',
          },
        },
        {
          kind: 'prose',
          id: 'm5p2-hist-intro',
          heading: 'Contrast enhancement, and its cost',
          body: [
            'Histogram equalization spreads a bunched-up intensity distribution across the full range, making low-contrast structure visible. **CLAHE** does it in local tiles with a clip limit, so one bright region cannot dominate the whole image.',
            'The cost is real and often unstated: equalization amplifies noise along with signal, and can create texture that was not in the original. In a diagnostic pipeline that is a safety question, not just an aesthetic one.',
          ],
        },
        {
          kind: 'activity',
          id: 'm5p2-histogram',
          activity: 'histogram-equalization',
          heading: 'Equalization and CLAHE',
          intro:
            'A deliberately low-contrast image. Compare no enhancement, global equalization, and CLAHE — and watch the histogram beneath each.',
          summary:
            'Learner compares global histogram equalization with CLAHE and observes the amplification of noise alongside signal.',
        },
        {
          kind: 'activity',
          id: 'm5p2-checklist',
          activity: 'imaging-checklist',
          heading: 'Reproducibility checklist',
          intro:
            'Score an imaging pipeline against the practices that make it reproducible. Each item you leave unchecked names a specific way results fail to replicate.',
          summary:
            'Learner audits an imaging pipeline against documentation, preprocessing, labelling, and validation practices and receives a scored result.',
        },
        {
          kind: 'reveal',
          id: 'm5p2-more',
          label: 'Learn more: what belongs in an imaging methods section',
          body: [
            'Acquisition: scanner make and model, sequence or protocol, pixel spacing, slice thickness, and the window/level applied if any.',
            'Preprocessing: every step in order, with parameters — resampling target, intensity normalization method, whether CLAHE was used and with which clip limit and tile size.',
            'Labelling: who annotated, their expertise, whether independently, how disagreements were resolved, and the inter-rater agreement.',
            'Validation: how the split was constructed (patient-level, site-level, or time-based) and whether any external dataset from different equipment was used.',
            'A pipeline missing any of these cannot be reproduced, and its reported performance cannot be interpreted.',
          ],
        },
      ],
    },
  ],
};
