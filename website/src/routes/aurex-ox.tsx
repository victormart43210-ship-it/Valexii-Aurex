import { createFileRoute, Outlet } from "@tanstack/react-router";

export const Route = createFileRoute("/aurex-ox")({
  head: () => ({
    meta: [
      { title: "AUREX-OX — Model laboratory | VALEXII.AI" },
      {
        name: "description",
        content:
          "AUREX-OX is the offline laboratory for model registration, evaluation, and synthetic customization. Production is on hold.",
      },
      { property: "og:title", content: "AUREX-OX model laboratory" },
      {
        property: "og:description",
        content: "Offline model registration and evaluation. No live connection and no production release.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: AurexOxLayout,
});

function AurexOxLayout() {
  return <Outlet />;
}
