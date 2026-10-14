import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  Outlet,
  createRootRouteWithContext,
  useRouter,
  HeadContent,
  Scripts,
} from "@tanstack/react-router";
import { useEffect, type ReactNode } from "react";

import { ActivationConsent } from "@/components/activation-consent";
import appCss from "../styles.css?url";
import { RouteError, RouteNotFound, RoutePending } from "@/components/route-states";

export const Route = createRootRouteWithContext<{ queryClient: QueryClient }>()({
  head: () => ({
    meta: [
      { charSet: "utf-8" },
      { name: "viewport", content: "width=device-width, initial-scale=1" },
      { name: "theme-color", content: "#070F19" },
      { title: "VALEXII.AI" },
      { name: "description", content: "Governed intelligence under human control." },
      { name: "author", content: "VALEXII.AI" },
      { property: "og:site_name", content: "VALEXII.AI" },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
    links: [
      {
        rel: "stylesheet",
        href: appCss,
      },
      { rel: "icon", href: "/favicon.ico", type: "image/x-icon" },
      { rel: "preconnect", href: "https://fonts.googleapis.com" },
      { rel: "preconnect", href: "https://fonts.gstatic.com", crossOrigin: "anonymous" },
      {
        rel: "stylesheet",
        href: "https://fonts.googleapis.com/css2?family=Cinzel:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&display=swap",
      },
    ],
    scripts: [
      {
        type: "application/ld+json",
        children: JSON.stringify({
          "@context": "https://schema.org",
          "@graph": [
            {
              "@type": "Organization",
              "@id": "https://valexii.com/#organization",
              name: "VALEXII.AI",
              url: "https://valexii.com/",
              email: "developer@valexii.com",
              description:
                "Independent research and development of governed, evidence-aware intelligence.",
            },
            {
              "@type": "WebSite",
              "@id": "https://valexii.com/#website",
              name: "VALEXII.AI",
              url: "https://valexii.com/",
              publisher: { "@id": "https://valexii.com/#organization" },
            },
          ],
        }),
      },
    ],
  }),
  shellComponent: RootShell,
  component: RootComponent,
  notFoundComponent: RouteNotFound,
  errorComponent: RouteError,
  pendingComponent: RoutePending,
});

function RootShell({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        {children}
        <Scripts />
      </body>
    </html>
  );
}

function RootComponent() {
  const { queryClient } = Route.useRouteContext();
  const router = useRouter();
  useEffect(() => {
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () =>
      router.update({ ...router.options, defaultViewTransition: !preference.matches });
    update();
    preference.addEventListener("change", update);
    return () => preference.removeEventListener("change", update);
  }, [router]);

  return (
    <QueryClientProvider client={queryClient}>
      <Outlet />
      <span className="route-transition-orb" aria-hidden="true" />
      <ActivationConsent />
    </QueryClientProvider>
  );
}
