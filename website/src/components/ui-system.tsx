import { useId, type ComponentProps, type ReactNode } from "react";
import { CircleHelp, TriangleAlert, LoaderCircle } from "lucide-react";
import { Button, type ButtonProps } from "./ui/button";
import { cn } from "../lib/utils";

/** Retains the shared Button variants; never implies a completed external action. */
export interface ActionButtonProps extends ButtonProps {
  busy?: boolean;
  busyLabel?: string;
}
export function ActionButton({
  busy = false,
  busyLabel = "Working…",
  children,
  disabled,
  asChild = false,
  ...props
}: ActionButtonProps) {
  return (
    <Button {...props} asChild={asChild} disabled={disabled || busy} aria-busy={busy || undefined}>
      {asChild ? (
        children
      ) : busy ? (
        <>
          <LoaderCircle aria-hidden="true" />
          {busyLabel}
        </>
      ) : (
        children
      )}
    </Button>
  );
}

export interface CardProps extends ComponentProps<"article"> {
  padding?: "compact" | "normal" | "roomy";
}
export function Card({ padding = "normal", className, ...props }: CardProps) {
  return <article {...props} className={cn("ui-card", `ui-card--${padding}`, className)} />;
}

export interface SectionHeaderProps {
  eyebrow: string;
  title: string;
  copy?: ReactNode;
  action?: ReactNode;
  id?: string;
  className?: string;
}
export function SectionHeader({ eyebrow, title, copy, action, id, className }: SectionHeaderProps) {
  return (
    <div className={cn("ui-section-header", className)}>
      <div className="min-w-0 max-w-3xl">
        <div className="ui-eyebrow">
          <span aria-hidden="true" />
          {eyebrow}
        </div>
        <h2 id={id} className="font-display text-3xl leading-tight text-balance sm:text-5xl">
          {title}
        </h2>
        {copy && (
          <div className="mt-6 max-w-2xl text-base leading-8 text-muted-foreground">{copy}</div>
        )}
      </div>
      {action && <div className="min-w-0 shrink-0">{action}</div>}
    </div>
  );
}

export interface StatePanelProps {
  title: string;
  children?: ReactNode;
  action?: ReactNode;
  tone?: "neutral" | "review" | "error";
  announce?: "off" | "polite" | "assertive";
  headingLevel?: 1 | 2 | 3;
  className?: string;
}
export function StatePanel({
  title,
  children,
  action,
  tone = "neutral",
  announce = "off",
  headingLevel = 3,
  className,
}: StatePanelProps) {
  const id = useId();
  const Heading = headingLevel === 1 ? "h1" : headingLevel === 2 ? "h2" : "h3";
  const Icon = tone === "neutral" ? CircleHelp : TriangleAlert;
  return (
    <section
      className={cn("ui-state-panel", className)}
      data-tone={tone}
      aria-labelledby={id}
      role={announce === "assertive" ? "alert" : announce === "polite" ? "status" : undefined}
    >
      <div className="ui-state-heading">
        <Heading id={id}>{title}</Heading>
        <Icon aria-hidden="true" />
      </div>
      {children && <div className="ui-state-copy">{children}</div>}
      {action && <div className="ui-state-actions">{action}</div>}
    </section>
  );
}

export function EmptyState(props: Omit<StatePanelProps, "tone">) {
  return <StatePanel {...props} tone="neutral" />;
}
export function ErrorState(props: Omit<StatePanelProps, "tone">) {
  return <StatePanel {...props} tone="error" />;
}

export interface LoadingSkeletonProps {
  label?: string;
  lines?: number;
  className?: string;
}
export function LoadingSkeleton({
  label = "Loading page…",
  lines = 3,
  className,
}: LoadingSkeletonProps) {
  const count = Number.isFinite(lines) ? Math.max(1, Math.min(6, Math.floor(lines))) : 3;
  return (
    <div role="status" aria-busy="true" className={cn("ui-loading", className)}>
      <span className="sr-only">{label}</span>
      <div aria-hidden="true" className="ui-skeleton-lines">
        {Array.from({ length: count }, (_, i) => (
          <span key={i} />
        ))}
      </div>
    </div>
  );
}
