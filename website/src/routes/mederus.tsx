import { createFileRoute, redirect } from "@tanstack/react-router";
// Legacy product spelling; BCXMET is canonical.
export const Route = createFileRoute("/mederus")({
  beforeLoad: () => {
    throw redirect({ to: "/bcxmet", statusCode: 301 });
  },
});
