import type { TopicFaq, TopicSource } from "@/components/topic-guide";

export const androidSecurityFaqs: TopicFaq[] = [
  {
    question: "How can I tell if a text or call is a phishing attempt?",
    answer:
      "Common signs include urgency or threats, requests for codes, passwords or payment, unexpected links, and a sender who cannot be verified through a channel you already trust. Contact the organization using a number or app you found yourself, not one supplied in the message.",
  },
  {
    question: "Which Android app permissions deserve a closer look?",
    answer:
      "Permissions that reach sensitive data or control—SMS, call logs, contacts, location, microphone, camera, accessibility services and device administration—deserve review when they do not match what the app obviously does. A permission alone is not proof of harm; it is a reason to ask why.",
  },
  {
    question: "How do I review or remove an app's permissions on Android?",
    answer:
      "Android lets you view and change permissions per app in Settings, and Google Play Protect can check installed apps. Exact menus vary by device and Android version; the linked Android Help pages describe current steps.",
  },
  {
    question: "Does BCXMET protect my phone today?",
    answer:
      "No. BCXMET is an Android security product in development. The demonstrations on this site are simulated and do not block calls, scan apps or read data from your device. Keep using your phone's built-in protections.",
  },
  {
    question: "What does 'evidence-first' mean for mobile security?",
    answer:
      "It means showing what was checked, what was not checked, how fresh the information is, and what remains unknown—so 'unknown' is never presented as 'safe' and a person decides on consequential actions.",
  },
];
export const androidSecuritySources: TopicSource[] = [
  {
    label: "CISA — Recognize and Report Phishing",
    href: "https://www.cisa.gov/secure-our-world/recognize-and-report-phishing",
  },
  {
    label: "Android Help — Change app permissions on your Android phone",
    href: "https://support.google.com/android/answer/9431959",
  },
  {
    label: "Google Play Help — Use Google Play Protect",
    href: "https://support.google.com/googleplay/answer/2812853",
  },
  {
    label: "Android Developers — Permissions on Android",
    href: "https://developer.android.com/guide/topics/permissions/overview",
  },
];

export const voynichFaqs: TopicFaq[] = [
  {
    question: "What is the Voynich Manuscript?",
    answer:
      "An illustrated codex written in an unidentified script, held at Yale University's Beinecke Rare Book & Manuscript Library as MS 408. Radiocarbon testing of its vellum points to the early fifteenth century. Its sections are commonly described as herbal, astronomical, biological, cosmological and pharmaceutical.",
  },
  {
    question: "Has the Voynich Manuscript been deciphered?",
    answer:
      "No decipherment has been accepted by the scholarly community. Many proposed solutions have been published; none has produced readings that independent researchers can reproduce across the text.",
  },
  {
    question: "Can I see the manuscript myself?",
    answer:
      "Yes. The Beinecke Library provides full digital images of the manuscript, linked below.",
  },
  {
    question: "What is VALEXII researching?",
    answer:
      "Computational structure: transcription control, segmentation, line position and comparison against matched null models. These are working hypotheses with evidence attachment required—not a translation. Research in progress — not a claimed decipherment.",
  },
];
export const voynichSources: TopicSource[] = [
  {
    label: "Beinecke Rare Book & Manuscript Library — The Voynich Manuscript",
    href: "https://beinecke.library.yale.edu/beinecke/collections/beinecke-cipher-voynich-manuscript",
  },
  {
    label: "Voynich manuscript — encyclopedia overview with scholarship references",
    href: "https://en.wikipedia.org/wiki/Voynich_manuscript",
  },
];

export const rongorongoFaqs: TopicFaq[] = [
  {
    question: "What is Rongorongo?",
    answer:
      "A system of glyphs carved on wooden objects from Rapa Nui (Easter Island). About two dozen inscribed objects survive in collections worldwide. The lines are written in reverse boustrophedon: the reader turns the object at the end of each line.",
  },
  {
    question: "Has Rongorongo been deciphered?",
    answer:
      "No. Whether it encodes language as true writing or serves as another kind of record is still debated. The most widely discussed partial result is a sequence on the Mamari tablet that several scholars interpret as a lunar calendar, but even that reading is not universally accepted. A 2024 radiocarbon study (Ferrara et al., Scientific Reports) dated the wood of one tablet held in Rome to before European contact, which bears on whether the script was invented independently.",
  },
  {
    question: "Why is it so difficult?",
    answer:
      "The corpus is small, many objects are damaged, the tradition of reading was lost in the nineteenth century, and there is no bilingual text. Any proposal therefore needs strict controls against overfitting.",
  },
  {
    question: "What is VALEXII's approach?",
    answer:
      "Original, unverified hypotheses: work from accurate 3D/record-level corpora, test calendar-constrained alignment with frozen values, and check whether patterns transfer to held-out lines. No translation is claimed.",
  },
];
export const rongorongoSources: TopicSource[] = [
  {
    label:
      "Ferrara et al. (2024), \u201cThe invention of writing on Rapa Nui (Easter Island). New radiocarbon dates on the Rongorongo script,\u201d Scientific Reports 14:2794",
    href: "https://doi.org/10.1038/s41598-024-53063-7",
  },
  {
    label:
      "Lastilla, Ravanelli, Valério & Ferrara (2019), 3D modelling of the Mamari tablet, ISPRS Archives XLII-2/W18 (University of Bologna, ERC INSCRIBE)",
    href: "https://isprs-archives.copernicus.org/articles/XLII-2-W18/85/2019/",
  },
  {
    label: "Rongorongo — encyclopedia overview (general background only)",
    href: "https://en.wikipedia.org/wiki/Rongorongo",
  },
];

export const linearAFaqs: TopicFaq[] = [
  {
    question: "What is Linear A?",
    answer:
      "A script used by the Minoan civilization of Bronze Age Crete, roughly in the first half of the second millennium BCE. Most surviving inscriptions are short administrative records on clay tablets, with others on vessels and objects.",
  },
  {
    question: "Has Linear A been deciphered?",
    answer:
      "No. Many signs resemble those of Linear B, which Michael Ventris showed in 1952 records an early form of Greek, so approximate sound values can be borrowed. The underlying Minoan language, however, remains unidentified, and no proposed translation is accepted.",
  },
  {
    question: "Where can researchers access the inscriptions?",
    answer:
      "Scholarly editions and digital databases such as SigLA, linked below, catalogue Linear A signs and documents.",
  },
  {
    question: "What is VALEXII's approach?",
    answer:
      "Corpus control and testable structural questions, such as sign position and administrative formulae, before any linguistic claim. Findings require evidence attachment; no translation is presented.",
  },
];
export const linearASources: TopicSource[] = [
  {
    label: "SigLA — The Signs of Linear A, a palaeographic database",
    href: "https://sigla.phis.me/",
  },
  {
    label: "Linear A — encyclopedia overview with scholarship references",
    href: "https://en.wikipedia.org/wiki/Linear_A",
  },
];

/** BreadcrumbList JSON-LD for research topic pages (Home › Research › Topic). */
export function researchBreadcrumb(name: string, path: string) {
  return {
    type: "application/ld+json",
    children: JSON.stringify({
      "@context": "https://schema.org",
      "@type": "BreadcrumbList",
      itemListElement: [
        { "@type": "ListItem", position: 1, name: "VALEXII.AI", item: "https://valexii.com/" },
        {
          "@type": "ListItem",
          position: 2,
          name: "Research",
          item: "https://valexii.com/research",
        },
        { "@type": "ListItem", position: 3, name, item: `https://valexii.com${path}` },
      ],
    }),
  };
}
