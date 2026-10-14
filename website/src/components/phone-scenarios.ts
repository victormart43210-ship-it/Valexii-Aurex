export const phoneViews = ["Home", "Command Center", "XAELI", "Activity", "More"] as const;
export type PhoneView = (typeof phoneViews)[number];
export type DemoPhase = "idle" | "review" | "returning" | "complete";
export type DemoKind = "routine" | "qualified" | "scan" | "review" | "ambiguous";
export type DemoHue = "unknown" | "observed" | "review" | "ambiguous" | "critical";
export const demoModes: Record<DemoKind, { hue: DemoHue; label: string }> = {
  routine: { hue: "observed", label: "Routine call · simulated observation" },
  qualified: { hue: "critical", label: "Critical scenario · NOT a verified threat" },
  scan: { hue: "observed", label: "Scan storyboard · no device scanning" },
  review: { hue: "review", label: "Qualified-review storyboard · evidence NOT VERIFIED" },
  ambiguous: { hue: "ambiguous", label: "Ambiguous cues · review / HOLD" },
};
export type SpectrumObservation = {
  id: string;
  bin: number;
  source: "Wi-Fi" | "BLE";
  rssi: number;
  channel: string;
  frequency: string;
  name: string;
  lastSeen: string;
  qualification: string;
  confidence: string;
  trace: readonly number[];
};
export const spectrumFixture: readonly SpectrumObservation[] = [
  {
    id: "S1",
    bin: 1,
    source: "Wi-Fi",
    rssi: -54,
    channel: "6",
    frequency: "2437 MHz",
    name: "SSID withheld · name unknown",
    lastSeen: "Snapshot B · illustrative",
    qualification: "NOT VERIFIED",
    confidence: "Uncalibrated",
    trace: [-64, -60, -58, -54, -56, -54],
  },
  {
    id: "S2",
    bin: 2,
    source: "Wi-Fi",
    rssi: -76,
    channel: "36",
    frequency: "5180 MHz",
    name: "Fictional network cue",
    lastSeen: "Snapshot A · stale example",
    qualification: "STALE / HOLD",
    confidence: "Uncalibrated",
    trace: [-72, -73, -75, -74, -78, -76],
  },
  {
    id: "S3",
    bin: 3,
    source: "BLE",
    rssi: -67,
    channel: "Advertising 37",
    frequency: "2402 MHz",
    name: "Fictional advertising cue",
    lastSeen: "Snapshot B · illustrative",
    qualification: "NOT VERIFIED",
    confidence: "Uncalibrated",
    trace: [-70, -68, -71, -69, -66, -67],
  },
];
/** Bin angle is an ordinal drawing slot, never a measured bearing. Radius encodes RSSI only. */
export function plotSpectrumObservation(observation: SpectrumObservation) {
  const angle = (observation.bin - 1) * ((Math.PI * 2) / 3) - Math.PI / 2;
  const radius = 42 + Math.min(60, Math.max(0, -observation.rssi - 35));
  return {
    x: 140 + Math.cos(angle) * radius,
    y: 140 + Math.sin(angle) * radius,
    band:
      observation.rssi >= -60
        ? "Stronger signal"
        : observation.rssi >= -70
          ? "Mid signal"
          : "Weaker signal",
    trace: observation.trace
      .map((rssi, i) => `${12 + i * 24},${10 + Math.min(40, Math.max(0, -rssi - 40))}`)
      .join(" "),
  };
}
export const demoPhases = {
  idle: { label: "Awaiting demo", progress: 0, orb: "REST" },
  review: { label: "Synthetic review", progress: 40, orb: "AWARE" },
  returning: { label: "Review held", progress: 80, orb: "RETURN" },
  complete: { label: "Demo complete · HOLD", progress: 100, orb: "REST" },
} as const;

/** Authored storyboard progress, never measured scan coverage or device observations. */
export function getDemoTelemetry(phase: DemoPhase, kind: DemoKind | null) {
  const step = demoPhases[phase];
  const active = phase === "review" && kind !== null;
  const hue: DemoHue = active
    ? demoModes[kind].hue
    : phase === "returning"
      ? "ambiguous"
      : "unknown";
  return {
    hue,
    modeLabel: active ? demoModes[kind].label : "Unknown current state · no security verdict",
    scanActive: active && kind === "scan",
    observations: kind === "scan" && phase !== "idle" ? spectrumFixture : [],
    fields: ["Device", "Communications", "Network", "Spectrum", "Identity-Privacy"].map((name) => {
      const observed =
        active &&
        ((name === "Spectrum" && kind === "scan") ||
          (name === "Communications" && kind === "routine") ||
          (name === "Device" && kind !== "scan" && kind !== "routine"));
      return {
        name,
        status: observed ? "DEMO observation / NOT VERIFIED" : "UNKNOWN",
        hue: observed ? hue : "unknown",
      };
    }),
    phase: step.label,
    progress: step.progress,
    orb:
      active && kind === "qualified"
        ? ("DEFEND" as const)
        : active && kind === "ambiguous"
          ? ("WATCH" as const)
          : step.orb,
    current: "UNKNOWN",
    verification: "NOT VERIFIED",
    historical: "CLEAR not established",
    lastCheck: "Unknown · no device check",
    freshness: "Unverified",
    authority: "NONE",
    evidence:
      kind === "routine"
        ? "Authored call cues · no call received or blocked"
        : kind === "qualified"
          ? "Authored permission A → B · no attack established"
          : "Authored permission A → B · no live device data",
    evidenceTopic: kind === "routine" ? phoneTopics["Command Center"][0] : phoneTopics.Home[0],
  };
}
export type DemoTelemetry = ReturnType<typeof getDemoTelemetry>;
type Topic = { title: string; summary: string; fields: [string, string][] };
const boundaries: [string, string][] = [
  [
    "Qualification",
    "SIMULATED / NOT ESTABLISHED. No independent witness or device observations are attached. Missing, stale or unresolved evidence never counts as PASS.",
  ],
  [
    "Authority",
    "Historical review is not current permission. Any effect would require fresh evidence and current human authorization. This demo performs no consequential action.",
  ],
];
const scenario = (
  title: string,
  summary: string,
  checked: string,
  missing: string,
  evidence: string,
  next: string,
): Topic => ({
  title,
  summary,
  fields: [
    ["Checked in this example", checked],
    ["Not checked / limitations", missing],
    ["Example evidence", evidence],
    ["Next review", next],
    ...boundaries,
  ],
});
export const phoneTopics: Record<PhoneView, Topic[]> = {
  Home: [
    {
      title: "NOW",
      summary: "Review needed · Unknown ≠ Safe",
      fields: [
        [
          "Evidence quality",
          "A synthetic permission comparison is available; source binding, completeness and independent corroboration are absent. This is not a device-health score.",
        ],
        [
          "Freshness",
          "Illustrative snapshot A → B, not a live feed. The demo does not know the device's current state.",
        ],
        ...boundaries,
      ],
    },
    {
      title: "CHANGED",
      summary: "An example app requests a new permission",
      fields: [
        [
          "Observation",
          "Fictional app Example Maps requests location access in snapshot B; snapshot A did not contain that request.",
        ],
        [
          "Alternative",
          "An expected update or a changed feature could explain it. A permission request alone is not proof of harm.",
        ],
        [
          "Scope",
          "Only this synthetic permission difference is described; installed apps, package signatures and network behavior are not inspected.",
        ],
      ],
    },
    {
      title: "NEXT",
      summary: "Review before granting access",
      fields: [
        [
          "User review",
          "Open the real Android permission settings yourself, compare the requested access with the app's purpose, and consult an independently verified source.",
        ],
        ["Boundary", "No permission is granted, denied, revoked or changed here."],
      ],
    },
    {
      title: "WHY",
      summary: "Separate observation from interpretation",
      fields: [
        [
          "Reasoning summary",
          "New permission → possible change in access → review request. There is no supported inference that an attack occurred.",
        ],
        [
          "Independent challenge",
          "Check the update explanation against an independent source. The system may never be its own sole witness.",
        ],
      ],
    },
    {
      title: "PROOF",
      summary: "Inspect source, scope and freshness",
      fields: [
        [
          "Provenance",
          "Source: authored synthetic fixture, not device telemetry. Snapshot identifiers: A and B. No cryptographic or independent proof is attached.",
        ],
        [
          "Truth architecture",
          "Evidence → Qualification → Reality → Authority → Effect. This example stops at unresolved qualification; no effect is authorized.",
        ],
        [
          "Freshness rule",
          "A timestamp alone cannot establish freshness. Revalidate source identity and the applicable state at effect time.",
        ],
      ],
    },
  ],
  "Command Center": [
    {
      title: "Spam & Scam Call Blocker",
      summary: "#1 · Preview: review a simulated bank-impersonation call",
      fields: [
        [
          "What it can do · design intent",
          "Help review suspicious call cues and a proposed blocking choice. No calls are received or blocked by this website.",
        ],
        [
          "How it works · concept",
          "Compare the claimed caller identity, requested urgency and independent corroboration. Caller ID alone is not proof; legitimate calls can be misclassified.",
        ],
        [
          "Permissions required · proposed",
          "An Android call-screening role and user approval would be needed for actual blocking. Availability depends on OS/device restrictions; no phone or call-log permission is requested here.",
        ],
        [
          "Supported / under development",
          "Working website interaction: simulated scenario and evidence drill-down. Android call screening, blocking and efficacy are UNDER DEVELOPMENT / NOT VERIFIED.",
        ],
        [
          "Example evidence",
          "Authored fixture call-A: a fictional caller claims to be a bank and requests a recovery code. No phone number, recording or real call metadata is used. Source identity remains unknown.",
        ],
        [
          "Next review",
          "Do not disclose codes. End the real conversation yourself and contact the bank through an independently verified channel. This preview performs no blocking.",
        ],
        ...boundaries,
      ],
    },
    {
      title: "Malware & Suspicious App Detection",
      summary: "#2 · Preview: review a suspicious app-permission example",
      fields: [
        [
          "What it can do · design intent",
          "Explain suspicious app signals and their limits. A permission difference is not proof of malware; no installed app is scanned here.",
        ],
        [
          "How it works · concept",
          "Review source identity, permission changes and independently checked evidence. An expected update is a competing interpretation.",
        ],
        [
          "Permissions required · proposed",
          "App visibility and any optional usage/accessibility access require scope review and explicit consent. Broad privileges are not assumed or requested. Android restrictions may limit available observations.",
        ],
        [
          "Supported / under development",
          "Working website interaction: authored app fixture and evidence review. Malware detection, app inspection and security efficacy are UNDER DEVELOPMENT / NOT VERIFIED.",
        ],
        [
          "Example evidence",
          "Authored fixture app-B requests an unexpected permission. No app inventory, executable, package hash or live reputation source is attached; qualification stays unresolved.",
        ],
        [
          "Next review",
          "Inspect actual Android settings and independently verified app information. Use Android's existing security tools; no uninstall, quarantine or protection action runs here.",
        ],
        ...boundaries,
      ],
    },
    scenario(
      "Scams & Phishing",
      "Example: a delivery message asks for a fee",
      "Compare the example sender text, destination hostname and requested urgency.",
      "No URL is visited; no sender ownership, payload, reputation or malware check occurs.",
      "Synthetic message: ‘Delivery fee required’; destination example.invalid. A mismatched sender is a review cue, not proof of a scam.",
      "Use a separately verified courier contact; avoid following the message's link.",
    ),
    scenario(
      "Transactions",
      "Example: an unfamiliar payment request",
      "Compare fictional payee, amount and user intent.",
      "No bank connection, transaction signing, balance check or payment interception.",
      "Synthetic request: Example Merchant, 49 units; currency and recipient identity are unverified.",
      "Review through the bank's independently opened app. Never authorize solely on this example.",
    ),
    scenario(
      "Privacy",
      "Example: location permission added",
      "Compare the synthetic before/after permission list.",
      "No installed app inspection, signature verification or access-history collection.",
      "Fixture A: no location request. Fixture B: location request. Source identity and freshness remain unknown.",
      "Review real Android settings and the app's independently verified purpose before choosing access.",
    ),
    scenario(
      "Network & Travel",
      "Example: unfamiliar public Wi-Fi",
      "Compare a fictional network label and expected venue information.",
      "No packet inspection, encryption test, captive-portal validation or live network protection.",
      "Synthetic network name: Guest Example. A familiar name does not establish a trustworthy operator.",
      "Confirm the network with venue staff through a trusted channel; review device connection settings.",
    ),
    scenario(
      "Identity",
      "Example: unexpected account recovery notice",
      "Compare the example recovery request with user intent.",
      "No account access, breach search, identity validation or recovery operation.",
      "Synthetic notice: recovery requested for Example Account. Sender and request authenticity are unverified.",
      "Open the service independently and review recovery activity; never share recovery codes with this demo.",
    ),
  ],
  XAELI: [
    {
      title: "Explain it",
      summary: "A permission change is an observation, not a verdict",
      fields: [
        [
          "Context",
          "Example Maps requests location after a fictional update. XAELI separates the visible difference from possible explanations.",
        ],
        [
          "Uncertainty",
          "An expected feature change may explain it; malicious intent is not established. No live scan or protective action runs.",
        ],
        [
          "Assistant provenance",
          "This explanation is authored demo text, not a live AI response. XAELI is represented by the abstract luminous Orb in this app concept. Orb motion authority is NONE; presentation never supplies security authority.",
        ],
      ],
    },
    {
      title: "Show proof",
      summary: "Trace every claim back to its source",
      fields: [
        [
          "Source record",
          "Authored fixture permission-A / permission-B. No real package hash, signed artifact or independent device observation is supplied.",
        ],
        [
          "Quality / freshness",
          "Synthetic, illustrative and incomplete. No claim of current evidence or independently verified implementation.",
        ],
        [
          "Challenge",
          "Compare any real update explanation with an independent witness; XAELI cannot validate itself merely by repeating its own summary.",
        ],
      ],
    },
    {
      title: "Help me review it",
      summary: "People retain the decision",
      fields: [
        [
          "Review checklist",
          "Confirm the app's identity; inspect real settings; compare the requested permission with intended use; seek independent corroboration; leave unresolved questions open.",
        ],
        [
          "Authority",
          "Recommendations do not become authorization. No setting, permission or device state changes here.",
        ],
        [
          "Next step",
          "If evidence is missing or contradictory, HOLD for human review. Unknown ≠ Safe.",
        ],
      ],
    },
  ],
  Activity: [
    {
      title: "Permission comparison",
      summary: "Illustrative 09:00 UTC · scenario day, not a real date",
      fields: [
        [
          "Event detail",
          "Snapshot B differs from A by a location-permission request. This is a fictional event, not a recent device notification.",
        ],
        ["Source", "Authored fixture permission-B; no device or publisher identity binding."],
        [
          "Qualification",
          "UNRESOLVED: incomplete scope, no freshness verification, no independent corroboration.",
        ],
        [
          "Historical authority",
          "The example review was recorded; it did not authorize permission changes.",
        ],
        [
          "Current authority",
          "NONE. No current device state is known and no action is authorized. Revocation would not erase the historical record.",
        ],
      ],
    },
    {
      title: "Alternative explanation",
      summary: "Illustrative 09:05 UTC · same fictional scenario day",
      fields: [
        [
          "Challenge",
          "An expected update could explain the request. This alternative is not a verified fact.",
        ],
        ["Source", "Authored challenge fixture; no publisher release notes are attached."],
        ["Qualification", "NOT ESTABLISHED. An independent source is required."],
        ...boundaries,
      ],
    },
    {
      title: "Review held",
      summary: "Illustrative 09:10 UTC · no real elapsed-time claim",
      fields: [
        ["Decision", "HOLD: missing source identity and current evidence prevent an effect."],
        [
          "Provenance",
          "Synthetic evidence trail retained; no real audit log or telemetry integration.",
        ],
        ...boundaries,
      ],
    },
  ],
  More: [
    {
      title: "Privacy",
      summary: "No device data is collected by this simulator",
      fields: [
        [
          "Demo scope",
          "This phone receives no Android permissions, messages, accounts or network traffic. Selections are local presentation state and are not saved as security records.",
        ],
        [
          "Website policy",
          "The site's Privacy page remains the applicable draft notice; this example does not establish production privacy approval.",
        ],
      ],
    },
    {
      title: "Accessibility",
      summary: "Keyboard, readable labels and reduced motion",
      fields: [
        [
          "Presentation",
          "Use the motion checkbox to disable decorative motion. Operating-system reduced-motion preference and offscreen lifecycle also pause the Orb.",
        ],
        [
          "Navigation",
          "All screen and topic controls have text labels. The detail panel uses normal page scrolling; no swipe-only or focus-trapping interface.",
        ],
      ],
    },
    {
      title: "Permissions",
      summary: "Review concepts, not Android controls",
      fields: [
        [
          "Access boundary",
          "No permission is requested or changed. Real permission review must happen in Android settings.",
        ],
        [
          "Authority",
          "Every consequential effect requires current authorization. A past approval cannot silently authorize a new action.",
        ],
      ],
    },
    {
      title: "Disclaimers",
      summary: "Concept / simulation / verification stay separate",
      fields: [
        [
          "Implemented here",
          "Editable website tabs, explanatory drill-downs and decorative Orb presentation. These are presentation functions, not independently qualified device-security features.",
        ],
        [
          "Developmental",
          "BCXMET product workflows are design intent. No scanner, live protection, efficacy result or released-build claim is implied.",
        ],
        [
          "Invariants",
          "Evidence → Qualification → Reality → Authority → Effect. Unknown ≠ Safe. The system may never be its own sole witness. ORB MOTION AUTHORITY = NONE.",
        ],
      ],
    },
  ],
};
