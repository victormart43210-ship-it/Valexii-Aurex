import { useEffect, type ReactNode } from "react";
import { Link, useRouter, type ErrorComponentProps } from "@tanstack/react-router";
import { ActionButton, EmptyState, ErrorState, LoadingSkeleton } from "./ui-system";
import { reportLovableError } from "../lib/lovable-error-reporting";

function Frame({ children }: { children: ReactNode }) {
  return (
    <main id="main-content" className="ui-route-state site-grid">
      {children}
    </main>
  );
}
export function RouteNotFound() {
  return (
    <Frame>
      <meta name="robots" content="noindex" />
      <EmptyState
        headingLevel={1}
        title="Page not found"
        action={
          <ActionButton asChild>
            <Link to="/">Go home</Link>
          </ActionButton>
        }
      >
        This VALEXII.AI page does not exist or has moved. No research or device result is implied.
      </EmptyState>
    </Frame>
  );
}
export function RoutePending() {
  return (
    <Frame>
      <LoadingSkeleton label="Loading VALEXII.AI page…" lines={4} />
    </Frame>
  );
}
export function RouteError({ error, reset }: ErrorComponentProps) {
  const router = useRouter();
  useEffect(() => {
    reportLovableError(error, { boundary: "tanstack_root_error_component" });
  }, [error]);
  return (
    <Frame>
      <ErrorState
        headingLevel={1}
        title="This page didn’t load"
        announce="polite"
        action={
          <>
            <ActionButton
              onClick={async () => {
                await router.invalidate();
                reset();
              }}
            >
              Try again
            </ActionButton>
            <ActionButton asChild variant="outline">
              <Link to="/">Go home</Link>
            </ActionButton>
          </>
        }
      >
        The page is unavailable. Missing or failed information is not a verified result.
      </ErrorState>
    </Frame>
  );
}
