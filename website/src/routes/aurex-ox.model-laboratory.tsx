import { createFileRoute } from "@tanstack/react-router";
import { PageHero, PageShell } from "@/components/site";

export const Route = createFileRoute("/aurex-ox/model-laboratory")({
  head: () => ({
    meta: [
      { title: "AUREX-OX model laboratory | VALEXII.AI" },
      {
        name: "description",
        content:
          "Offline registry of model candidates. No weights are installed and no live connection is verified.",
      },
      { property: "og:title", content: "AUREX-OX offline model registry" },
      {
        property: "og:description",
        content: "Registered model candidates. None are installed or connected.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary" },
    ],
  }),
  component: ModelLaboratory,
});

const UPGRADE_CANDIDATES = [
  "Qwen3.5-0.8B",
  "Falcon-H1-1.5B-Instruct",
  "Granite-4.0-Micro",
  "Ministral-3-3B-Reasoning-2512-GGUF",
  "PaddleOCR-VL",
  "DeepSeek-OCR-2",
  "EXAONE-4.0-1.2B",
] as const;

const CANDIDATES = [
  ["Qwen", "China", "Foundation model"],
  ["Mistral / Ministral", "France", "Foundation model"],
  ["K2 Horizon", "United Arab Emirates", "Foundation model"],
  ["Falcon-H1", "United Arab Emirates", "Foundation model"],
  ["DeepSeek", "China", "Foundation model"],
  ["Apertus", "Switzerland", "Foundation model"],
  ["EXAONE", "South Korea", "Foundation model"],
  ["Sarvam", "India", "Foundation model"],
  ["SEA-LION", "Singapore", "Foundation model"],
  ["Sakana AI research", "Japan", "Research framework"],
  ["Llama", "United States", "Foundation model"],
] as const;

function ModelLaboratory() {
  return (
    <PageShell>
      <PageHero eyebrow="Model laboratory / offline" title="Registered candidates. None are connected.">
        <p>
          Every row is NOT INSTALLED and NOT EVALUATED on this site. The backend registry is the
          record. This page does not download weights, run training, or accept company records.
        </p>
      </PageHero>
      <section className="section-space">
        <div className="site-grid overflow-x-auto">
          <table className="w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs text-muted-foreground">
                <th className="py-2 pr-4">Family</th>
                <th className="py-2 pr-4">Country</th>
                <th className="py-2 pr-4">Kind</th>
                <th className="py-2">Status</th>
              </tr>
            </thead>
            <tbody>
              {CANDIDATES.map(([family, country, kind]) => (
                <tr key={family} className="border-b border-border">
                  <td className="py-3 pr-4">{family}</td>
                  <td className="py-3 pr-4">{country}</td>
                  <td className="py-3 pr-4">{kind}</td>
                  <td className="py-3 text-amber">NOT EVALUATED</td>
                </tr>
              ))}
            </tbody>
          </table>
          <h2 className="mt-10 text-lg font-display">Named upgrade candidates</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            These names come from the CCLXIV list. Weights were not downloaded here. No score is shown
            because none was measured.
          </p>
          <table className="mt-4 w-full text-left text-sm">
            <thead>
              <tr className="border-b border-border text-xs text-muted-foreground">
                <th className="py-2 pr-4">Candidate</th>
                <th className="py-2 pr-4">Weights</th>
                <th className="py-2">Evaluation</th>
              </tr>
            </thead>
            <tbody>
              {UPGRADE_CANDIDATES.map((name) => (
                <tr key={name} className="border-b border-border">
                  <td className="py-3 pr-4">{name}</td>
                  <td className="py-3 pr-4 text-amber">NOT INSTALLED</td>
                  <td className="py-3 text-amber">NOT EVALUATED</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </PageShell>
  );
}
