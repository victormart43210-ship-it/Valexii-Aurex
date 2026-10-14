import { createFileRoute, redirect } from "@tanstack/react-router";
export const Route = createFileRoute("/reasoning")({
  beforeLoad: () => {
    throw redirect({ to: "/system", statusCode: 301 });
  },
});
