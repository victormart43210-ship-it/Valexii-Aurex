import { useServerFn } from "@tanstack/react-start";
import { runIndustrialDemo } from "../lib/industrial.functions";
import { IndustrialAudit } from "./industrial-audit";
export function IndustrialAuditOwner() {
  const invoke = useServerFn(runIndustrialDemo);
  return <IndustrialAudit run={(fixture) => invoke({ data: { fixture } })} />;
}
