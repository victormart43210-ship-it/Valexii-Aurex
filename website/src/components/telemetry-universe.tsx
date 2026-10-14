import { useEffect, useRef, useState, useId } from "react";
import { select } from "d3-selection";
import { zoom, zoomIdentity, type ZoomBehavior, type ZoomTransform } from "d3-zoom";
import { Plus, Minus, RotateCcw, Move, Orbit } from "lucide-react";
import { Button } from "./ui/button";
import { PresentationOrb } from "./presentation-orb";
import { usePresentationActivity } from "@/hooks/use-presentation-activity";
import type { DemoTelemetry } from "./phone-scenarios";
import type { OrbState } from "./orb-states";
import { universeLevel, universeLevels, universeNodes } from "./telemetry-universe-model";

export function TelemetryUniverse({
  telemetry,
  state,
  motion,
  deliberate,
  eventKey,
}: {
  telemetry: DemoTelemetry;
  state: OrbState;
  motion: boolean;
  deliberate: boolean;
  eventKey: number;
}) {
  const id = useId();
  const { ref, active, reducedMotion } = usePresentationActivity();
  const svgRef = useRef<SVGSVGElement>(null);
  const behavior = useRef<ZoomBehavior<SVGSVGElement, unknown> | null>(null);
  const cameraRef = useRef(zoomIdentity);
  const [camera, setCamera] = useState<ZoomTransform>(zoomIdentity);
  const [gestures, setGestures] = useState(false);
  const [selected, setSelected] = useState<string | null>(null);
  const level = universeLevel(camera.k);
  const nodes = universeNodes(telemetry);
  const revealed = nodes.filter((n) => n.level <= level);
  const current = revealed.filter((n) => n.level === level);
  const selectedNode = nodes.find((n) => n.id === selected);
  useEffect(() => {
    const element = svgRef.current;
    if (!element) return;
    const controller = zoom<SVGSVGElement, unknown>()
      .extent([
        [0, 0],
        [660, 660],
      ])
      .translateExtent([
        [0, 0],
        [660, 660],
      ])
      .scaleExtent([1, 8])
      .filter(
        (event) =>
          gestures &&
          (event.type === "wheel" || !event.target.closest("[data-universe-node]")) &&
          (!event.button || event.type === "wheel"),
      )
      .on("zoom", (event) => {
        cameraRef.current = event.transform;
        setCamera(event.transform);
      });
    behavior.current = controller;
    const surface = select(element);
    surface.call(controller).on("dblclick.zoom", null);
    return () => {
      surface.on(".zoom", null);
      behavior.current = null;
    };
  }, [gestures]);
  const changeZoom = (factor: number) => {
    if (svgRef.current && behavior.current)
      select(svgRef.current).call(behavior.current.scaleBy, factor, [330, 330]);
  };
  const reset = () => {
    if (svgRef.current && behavior.current)
      select(svgRef.current).call(behavior.current.transform, zoomIdentity);
    setSelected(null);
  };
  return (
    <section
      ref={ref}
      className="telemetry-universe"
      data-hue={telemetry.hue}
      data-moving={active && motion}
      data-level={level}
      data-reduced={reducedMotion}
      aria-label="XAELI telemetry universe"
    >
      <p className="instrument-demo-label">SOVEREIGN COMET / XAELI TELEMETRY UNIVERSE</p>
      <p className="instrument-demo-label">DEMO / SIMULATED · NO LIVE DEVICE ACCESS</p>
      <div className="universe-toolbar" role="group" aria-label="Telemetry zoom controls">
        <Button
          variant="outline"
          size="icon"
          aria-label="Zoom out"
          disabled={camera.k <= 1}
          onClick={() => changeZoom(1 / 1.65)}
        >
          <Minus />
        </Button>
        <Button
          variant="outline"
          size="icon"
          aria-label="Zoom in"
          disabled={camera.k >= 8}
          onClick={() => changeZoom(1.65)}
        >
          <Plus />
        </Button>
        <Button variant="outline" size="icon" aria-label="Reset telemetry view" onClick={reset}>
          <RotateCcw />
        </Button>
        <Button
          variant="outline"
          size="icon"
          aria-label="Enable canvas gestures"
          title="Canvas gestures"
          aria-pressed={gestures}
          onClick={() => setGestures(!gestures)}
        >
          <Move />
        </Button>
      </div>
      <p className="universe-level" role="status">
        0{level} / {universeLevels[level]} · {camera.k.toFixed(1)}×
      </p>
      <svg
        ref={svgRef}
        viewBox="0 0 660 660"
        className={`universe-surface ${gestures ? "universe-gestures" : ""}`}
        tabIndex={0}
        role="group"
        aria-label="XAELI abstract nongeographic telemetry canvas"
        aria-describedby={`${id}-keys`}
        onKeyDown={(event) => {
          if (event.target !== event.currentTarget) return;
          if (
            [
              "+",
              "=",
              "-",
              "0",
              "Home",
              "ArrowLeft",
              "ArrowRight",
              "ArrowUp",
              "ArrowDown",
            ].includes(event.key)
          ) {
            event.preventDefault();
            if (event.key === "+" || event.key === "=") changeZoom(1.65);
            else if (event.key === "-") changeZoom(1 / 1.65);
            else if (event.key === "0" || event.key === "Home") reset();
            else if (svgRef.current && behavior.current) {
              const step = 45 / cameraRef.current.k;
              select(svgRef.current).call(
                behavior.current.translateBy,
                event.key === "ArrowLeft" ? step : event.key === "ArrowRight" ? -step : 0,
                event.key === "ArrowUp" ? step : event.key === "ArrowDown" ? -step : 0,
              );
            }
          }
        }}
      >
        <g className="universe-camera" transform={camera.toString()}>
          <foreignObject
            x="0"
            y="0"
            width="660"
            height="660"
            className="universe-orb-layer"
            opacity={level >= 3 ? 0.18 : level === 2 ? 0.35 : 1}
          >
            <PresentationOrb
              state={state}
              telemetry={telemetry}
              motion={motion && active}
              deliberate={deliberate}
              eventKey={eventKey}
            />
          </foreignObject>
          {level >= 1 && (
            <g className="universe-orbits" fill="none" stroke="var(--orb-tone)">
              {[80, 112, 144].map((r, i) => (
                <ellipse
                  key={r}
                  cx="330"
                  cy="330"
                  rx={r}
                  ry={r * 0.72}
                  strokeWidth=".7"
                  strokeDasharray={`${3 + i} ${5 + i}`}
                />
              ))}
            </g>
          )}
          {revealed.map((node, i) => (
            <g key={node.id} data-universe-node={node.id} data-detail-level={node.level}>
              <path
                d={`M330 330 Q${node.x} 330 ${node.x} ${node.y}`}
                fill="none"
                stroke="var(--orb-tone)"
                strokeOpacity=".35"
                strokeWidth={1 / camera.k}
              />
              {node.level >= 2 && (
                <g stroke="var(--gold)" strokeOpacity=".4" fill="none">
                  {[0, 1, 2].map((j) => (
                    <path
                      key={j}
                      d={`M${node.x - 6} ${node.y + 5 + j * 2}q6 ${-2 - (i % 3)} 12 0`}
                      strokeWidth={0.6 / camera.k}
                    />
                  ))}
                </g>
              )}
              <g transform={`translate(${node.x} ${node.y}) scale(${1 / camera.k})`}>
                <circle r="15" fill="var(--background)" stroke="var(--orb-tone)" strokeWidth="2" />
                <circle r="4" fill={node.level === 4 ? "var(--gold)" : "var(--orb-tone)"} />
                {node.level === level && (
                  <text y="-24" textAnchor="middle" fill="var(--foreground)" fontSize="20">
                    {node.label}
                  </text>
                )}
                {node.level === 2 &&
                  level === 2 &&
                  telemetry.observations
                    .filter((observation) => observation.id === node.id)
                    .map((observation) => (
                      <g
                        key={observation.id}
                        aria-label={`${observation.id} synthetic RSSI detail`}
                      >
                        <text y="42" textAnchor="middle" fill="var(--foreground)" fontSize="18">
                          {observation.rssi} dBm · ch {observation.channel}
                        </text>
                        <polyline
                          points={observation.trace
                            .map((rssi, i) => `${-45 + i * 18},${58 + (-rssi - 45) * 0.6}`)
                            .join(" ")}
                          fill="none"
                          stroke="var(--cyan)"
                          strokeWidth="2"
                        />
                      </g>
                    ))}
                {node.level === 3 && level === 3 && (
                  <text y="40" textAnchor="middle" fill="var(--gold)" fontSize="16">
                    AUTHORED / UNVERIFIED
                  </text>
                )}
                {node.level === 4 && level === 4 && (
                  <text y="40" textAnchor="middle" fill="var(--gold)" fontSize="16">
                    {node.id === "trace-3" || node.id === "trace-4" ? "NONE" : "NOT VERIFIED"}
                  </text>
                )}
                <circle
                  r="24"
                  fill="transparent"
                  role="button"
                  tabIndex={node.level === level ? 0 : -1}
                  aria-label={`Inspect ${node.label}`}
                  onClick={() => setSelected(node.id)}
                  onFocus={() => setSelected(node.id)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter" || e.key === " ") {
                      e.preventDefault();
                      setSelected(node.id);
                    }
                  }}
                />
              </g>
            </g>
          ))}
        </g>
      </svg>
      <p id={`${id}-keys`} className="universe-help">
        + / − zoom · arrows pan · 0 reset. Page scroll stays normal unless canvas gestures are
        enabled; disable them to scroll over the canvas.
      </p>
      <p className="universe-mode">
        <Orbit aria-hidden="true" />
        {telemetry.modeLabel}
      </p>
      {level === 2 && !telemetry.observations.length && (
        <p className="spectrum-legend">
          No radio observations selected · UNKNOWN. Scan demo supplies authored signal records only.
        </p>
      )}
      <div className="universe-node-picker" role="group" aria-label="Visible telemetry nodes">
        {current.map((node) => (
          <Button
            key={node.id}
            variant="outline"
            className="whitespace-normal"
            onClick={() => setSelected(node.id)}
            aria-pressed={selected === node.id}
          >
            {node.label}
          </Button>
        ))}
      </div>
      {selectedNode && (
        <div className="universe-evidence" aria-label="Selected telemetry evidence">
          <h4>{selectedNode.label} / DEMO</h4>
          <dl>
            {selectedNode.details.map(([key, value]) => (
              <div key={key}>
                <dt>{key}</dt>
                <dd>{value}</dd>
              </div>
            ))}
          </dl>
        </div>
      )}
      <p className="universe-boundary">
        UNKNOWN ≠ SAFE · ORB MOTION AUTHORITY = NONE.
        <br />
        Signal visualization, not location tracking. RSSI gives neither true bearings nor precise
        distance. Missing / stale ≠ PASS.
      </p>
    </section>
  );
}
