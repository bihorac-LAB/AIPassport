/** Design-system primitives. Native elements wherever native semantics exist. */

import {
  forwardRef,
  useId,
  useState,
  type ButtonHTMLAttributes,
  type InputHTMLAttributes,
  type ReactNode,
  type SelectHTMLAttributes,
  type TextareaHTMLAttributes,
} from 'react';
import { trackEvent, type EventContext } from '@/analytics/track';

// ── Button ───────────────────────────────────────────────────────────────────

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';

export type ButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  size?: 'sm' | 'md' | 'lg';
  block?: boolean;
  loading?: boolean;
};

const VARIANT_CLASS: Record<ButtonVariant, string> = {
  primary: 'btn--primary',
  secondary: '',
  outline: 'btn--outline',
  ghost: 'btn--ghost',
  danger: 'btn--danger',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = 'secondary', size = 'md', block, loading, className, children, ...rest },
  ref,
) {
  const classes = [
    'btn',
    VARIANT_CLASS[variant],
    size === 'sm' ? 'btn--sm' : size === 'lg' ? 'btn--lg' : '',
    block ? 'btn--block' : '',
    className ?? '',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <button
      ref={ref}
      type="button"
      className={classes}
      aria-busy={loading || undefined}
      disabled={rest.disabled || loading}
      {...rest}
    >
      {loading ? <span className="spinner" aria-hidden="true" /> : null}
      {children}
    </button>
  );
});

// ── Card / Panel / Callout ───────────────────────────────────────────────────

export function Card({
  children,
  className,
  as: As = 'div',
}: {
  children: ReactNode;
  className?: string;
  as?: 'div' | 'section' | 'article' | 'li';
}) {
  return <As className={['card', className ?? ''].filter(Boolean).join(' ')}>{children}</As>;
}

export type CalloutTone = 'info' | 'success' | 'warning' | 'danger' | 'neutral';

export function Callout({
  tone = 'info',
  title,
  children,
}: {
  tone?: CalloutTone;
  title?: string;
  children: ReactNode;
}) {
  return (
    <div className={`callout callout--${tone}`}>
      {title ? <p className="callout__title">{title}</p> : null}
      <div>{children}</div>
    </div>
  );
}

export function Badge({
  children,
  tone,
}: {
  children: ReactNode;
  tone?: 'accent' | 'success' | 'warning';
}) {
  return <span className={`badge${tone ? ` badge--${tone}` : ''}`}>{children}</span>;
}

// ── Fields ───────────────────────────────────────────────────────────────────

type FieldWrapperProps = {
  label: string;
  hint?: string;
  error?: string;
  required?: boolean;
  children: (props: { id: string; describedBy: string | undefined; invalid: boolean }) => ReactNode;
};

export function Field({ label, hint, error, required, children }: FieldWrapperProps) {
  const id = useId();
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  const describedBy = [hintId, errorId].filter(Boolean).join(' ') || undefined;

  return (
    <div className="field">
      <label className="field__label" htmlFor={id}>
        {label}
        {required ? (
          <span aria-hidden="true" style={{ color: 'var(--danger)' }}>
            {' '}
            *
          </span>
        ) : null}
        {required ? <span className="sr-only"> (required)</span> : null}
      </label>
      {children({ id, describedBy, invalid: Boolean(error) })}
      {hint ? (
        <p className="field__hint" id={hintId}>
          {hint}
        </p>
      ) : null}
      {error ? (
        <p className="field__error" id={errorId} role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export type TextInputProps = Omit<InputHTMLAttributes<HTMLInputElement>, 'className'> & {
  label: string;
  hint?: string;
  error?: string;
};

export function TextInput({ label, hint, error, required, ...rest }: TextInputProps) {
  return (
    <Field label={label} hint={hint} error={error} required={required}>
      {({ id, describedBy, invalid }) => (
        <input
          {...rest}
          id={id}
          className="input"
          aria-describedby={describedBy}
          aria-invalid={invalid || undefined}
          required={required}
        />
      )}
    </Field>
  );
}

export type TextAreaProps = Omit<TextareaHTMLAttributes<HTMLTextAreaElement>, 'className'> & {
  label: string;
  hint?: string;
  error?: string;
};

export function TextArea({ label, hint, error, required, ...rest }: TextAreaProps) {
  return (
    <Field label={label} hint={hint} error={error} required={required}>
      {({ id, describedBy, invalid }) => (
        <textarea
          {...rest}
          id={id}
          className="textarea"
          aria-describedby={describedBy}
          aria-invalid={invalid || undefined}
          required={required}
        />
      )}
    </Field>
  );
}

export type SelectProps = Omit<SelectHTMLAttributes<HTMLSelectElement>, 'className'> & {
  label: string;
  hint?: string;
  options: Array<{ value: string; label: string }>;
};

export function Select({ label, hint, options, ...rest }: SelectProps) {
  return (
    <Field label={label} hint={hint}>
      {({ id, describedBy }) => (
        <select {...rest} id={id} className="select" aria-describedby={describedBy}>
          {options.map((option) => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      )}
    </Field>
  );
}

// ── Slider ───────────────────────────────────────────────────────────────────

export function Slider({
  label,
  value,
  min,
  max,
  step = 1,
  unit,
  format,
  onChange,
  hint,
  disabled,
}: {
  label: string;
  value: number;
  min: number;
  max: number;
  step?: number;
  unit?: string;
  format?: (value: number) => string;
  onChange: (value: number) => void;
  hint?: string;
  disabled?: boolean;
}) {
  const id = useId();
  const display = format ? format(value) : `${value}${unit ? ` ${unit}` : ''}`;
  const hintId = hint ? `${id}-hint` : undefined;

  return (
    <div>
      <div className="slider-row">
        <label className="slider-row__label" htmlFor={id}>
          {label}
        </label>
        <output className="slider-row__value" htmlFor={id}>
          {display}
        </output>
      </div>
      <input
        id={id}
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        disabled={disabled}
        aria-describedby={hintId}
        // Screen readers read the formatted value, not the raw number.
        aria-valuetext={display}
        onChange={(event) => onChange(Number(event.target.value))}
      />
      {hint ? (
        <p className="field__hint" id={hintId}>
          {hint}
        </p>
      ) : null}
    </div>
  );
}

// ── Disclosure ("learn more") ────────────────────────────────────────────────

export function Reveal({
  label,
  children,
  eventContext,
  defaultOpen = false,
}: {
  label: string;
  children: ReactNode;
  eventContext?: EventContext;
  defaultOpen?: boolean;
}) {
  const [open, setOpen] = useState(defaultOpen);
  const id = useId();

  return (
    <div className="reveal">
      <button
        type="button"
        className="reveal__summary"
        aria-expanded={open}
        aria-controls={id}
        onClick={() => {
          const next = !open;
          setOpen(next);
          if (next && eventContext) trackEvent('explanation_opened', eventContext, { label });
        }}
      >
        <svg
          className={`reveal__chevron${open ? ' reveal__chevron--open' : ''}`}
          width="12"
          height="12"
          viewBox="0 0 12 12"
          aria-hidden="true"
        >
          <path d="M4 2l5 4-5 4z" fill="currentColor" />
        </svg>
        {label}
      </button>
      {open ? (
        <div className="reveal__body" id={id}>
          {children}
        </div>
      ) : null}
    </div>
  );
}

// ── Metric ───────────────────────────────────────────────────────────────────

export function Metric({
  label,
  value,
  note,
  tone,
}: {
  label: string;
  value: string;
  note?: string;
  tone?: 'success' | 'warning' | 'danger';
}) {
  const color =
    tone === 'success'
      ? 'var(--success)'
      : tone === 'warning'
        ? 'var(--warning)'
        : tone === 'danger'
          ? 'var(--danger)'
          : undefined;
  return (
    <div className="metric">
      <p className="metric__label">{label}</p>
      <p className="metric__value" style={color ? { color } : undefined}>
        {value}
      </p>
      {note ? <p className="metric__note">{note}</p> : null}
    </div>
  );
}

// ── Segmented control ────────────────────────────────────────────────────────

export function Segmented<T extends string>({
  label,
  value,
  options,
  onChange,
}: {
  label: string;
  value: T;
  options: Array<{ value: T; label: string }>;
  onChange: (value: T) => void;
}) {
  return (
    <div role="group" aria-label={label} className="segmented">
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          className="segmented__option"
          aria-pressed={option.value === value}
          onClick={() => onChange(option.value)}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
