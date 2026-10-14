import { createFileRoute, redirect } from "@tanstack/react-router";
// Legacy product spelling; BCXMET is canonical.
export const Route = createFileRoute("/medaurus")({
  beforeLoad: () => {
    throw redirect({ to: "/bcxmet", statusCode: 301 });
  },
});
