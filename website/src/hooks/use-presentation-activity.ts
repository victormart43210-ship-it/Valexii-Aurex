import { useEffect, useRef, useState } from "react";

/** Presentation lifecycle only; this hook never supplies security authority. */
export function usePresentationActivity() {
  const ref = useRef<HTMLElement>(null);
  const [active, setActive] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(true);
  useEffect(() => {
    const element = ref.current;
    if (!element) return;
    // Unsupported observers receive the existing static SVG, never a failed render.
    if (typeof IntersectionObserver === "undefined") return;
    let visible = false;
    const preference = window.matchMedia("(prefers-reduced-motion: reduce)");
    const update = () => {
      setReducedMotion(preference.matches);
      setActive(visible && !document.hidden && !preference.matches);
    };
    const observer = new IntersectionObserver(
      ([entry]) => {
        visible = Boolean(entry?.isIntersecting);
        update();
      },
      { threshold: 0.1 },
    );
    observer.observe(element);
    update();
    preference.addEventListener("change", update);
    document.addEventListener("visibilitychange", update);
    return () => {
      observer.disconnect();
      preference.removeEventListener("change", update);
      document.removeEventListener("visibilitychange", update);
    };
  }, []);
  return { ref, active, reducedMotion };
}
