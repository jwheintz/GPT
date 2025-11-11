import React, { useEffect, useMemo, useRef, useState } from "react";

/** =========================
 *  Types
 *  ========================= */
type Anchor = {
  id: string;
  title: string;
  tags: string[];
  createdAt: number; // ms epoch
};

type RecallCard = {
  id: string; // anchorId@timestamp
  anchorId: string;
  dueAt: number; // ms epoch
  lastReviewedAt?: number;
  intervalDays: number; // current interval length
  ease: number; // 1.2—2.5 simple ease factor
  bucket: number; // Leitner-ish 1..5
};

type SessionKind = "work" | "shortBreak" | "longBreak";

type PomodoroConfig = {
  workMin: number;
  shortBreakMin: number;
  longBreakMin: number;
  sessionsPerCycle: number; // 4
};

type AppState = {
  anchors: Record<string, Anchor>;
  recalls: Record<string, RecallCard>;
  pomodoro: {
    cycleCount: number; // completed work sessions in current cycle 0..4
    running: boolean;
    kind: SessionKind;
    endsAt?: number;
    remainingSec?: number;
  };
};

/** =========================
 *  Constants
 *  ========================= */
const DEFAULT_CONFIG: PomodoroConfig = {
  workMin: 25,
  shortBreakMin: 5,
  longBreakMin: 15,
  sessionsPerCycle: 4,
};

// For demo/testing, uncomment to shorten timings
// const DEFAULT_CONFIG: PomodoroConfig = {
//   workMin: 1,
//   shortBreakMin: 1,
//   longBreakMin: 2,
//   sessionsPerCycle: 4,
// };

const INITIAL_INTERVALS_DAYS = [1, 3, 7, 21];

/** =========================
 *  Utilities
 *  ========================= */
const now = () => Date.now();
const dayMs = 24 * 60 * 60 * 1000;

function uid(prefix = ""): string {
  return `${prefix}${Math.random().toString(36).slice(2, 10)}${Date.now().toString(36).slice(-4)}`;
}

function useLocalStorageState<T>(key: string, initial: T) {
  const [state, setState] = useState<T>(() => {
    const raw = typeof window !== "undefined" ? window.localStorage.getItem(key) : null;
    if (!raw) return initial;
    try {
      return JSON.parse(raw) as T;
    } catch (error) {
      console.warn(`Failed to parse localStorage key "${key}":`, error);
      return initial;
    }
  });

  useEffect(() => {
    window.localStorage.setItem(key, JSON.stringify(state));
  }, [key, state]);

  return [state, setState] as const;
}

function formatTime(sec: number) {
  const m = Math.floor(sec / 60)
    .toString()
    .padStart(2, "0");
  const s = Math.floor(sec % 60)
    .toString()
    .padStart(2, "0");
  return `${m}:${s}`;
}

function normalizeTag(t: string) {
  return t.trim().toLowerCase().replace(/\s+/g, "-");
}

function sessionLengthSeconds(kind: SessionKind, cfg: PomodoroConfig) {
  switch (kind) {
    case "work":
      return cfg.workMin * 60;
    case "shortBreak":
      return cfg.shortBreakMin * 60;
    case "longBreak":
      return cfg.longBreakMin * 60;
    default:
      return cfg.workMin * 60;
  }
}

/** =========================
 *  Interleaving + Scheduling
 *  ========================= */
// Very small SM-lite: increase ease when “easy”, drop when “hard”. Stretch interval by ease.
function nextIntervalDays(current: number, ease: number, feedback: "hard" | "ok" | "easy") {
  let nextEase = ease;
  if (feedback === "easy") nextEase = Math.min(2.5, ease + 0.1);
  else if (feedback === "hard") nextEase = Math.max(1.2, ease - 0.1);

  // next interval grows by ease multiplier
  const base = Math.max(1, current);
  const next = Math.round(base * nextEase);
  return { nextDays: Math.min(120, next), nextEase };
}

// Interleave due cards by shuffling tags and alternating anchors
function interleaveDue(cards: RecallCard[], anchors: Record<string, Anchor>, max = 12) {
  const byTag: Record<string, RecallCard[]> = {};
  for (const c of cards) {
    const a = anchors[c.anchorId];
    const tags = a?.tags.length ? a.tags : ["_untagged"];
    for (const t of tags) {
      const tag = normalizeTag(t);
      if (!byTag[tag]) byTag[tag] = [];
      byTag[tag].push(c);
    }
  }
  const tagOrder = Object.keys(byTag).sort(() => Math.random() - 0.5);
  const out: RecallCard[] = [];
  let exhausted = false;
  while (!exhausted && out.length < max) {
    exhausted = true;
    for (const t of tagOrder) {
      const q = byTag[t];
      if (q?.length) {
        // pick earliest due among this tag, then rotate
        q.sort((a, b) => a.dueAt - b.dueAt);
        out.push(q.shift()!);
        exhausted = false;
        if (out.length >= max) break;
      }
    }
  }
  // de-duplicate by id
  const seen = new Set<string>();
  return out.filter(c => (seen.has(c.id) ? false : (seen.add(c.id), true)));
}

/** =========================
 *  App
 *  ========================= */
export default function App() {
  const [cfg, setCfg] = useLocalStorageState<PomodoroConfig>("cfg", DEFAULT_CONFIG);
  const [state, setState] = useLocalStorageState<AppState>("lh-loop", {
    anchors: {},
    recalls: {},
    pomodoro: { cycleCount: 0, running: false, kind: "work" },
  });

  // Tick logic
  const rafRef = useRef<number | null>(null);
  useEffect(() => {
    if (!state.pomodoro.running || !state.pomodoro.endsAt) return;
    const loop = () => {
      const remaining = Math.max(0, Math.ceil((state.pomodoro.endsAt! - now()) / 1000));
      setState(s => ({ ...s, pomodoro: { ...s.pomodoro, remainingSec: remaining } }));
      if (remaining <= 0) {
        advancePomodoro();
        return;
      }
      rafRef.current = window.setTimeout(loop, 250) as unknown as number;
    };
    loop();
    return () => {
      if (rafRef.current) window.clearTimeout(rafRef.current);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [state.pomodoro.running, state.pomodoro.endsAt, cfg]);

  function start(kind: SessionKind) {
    const minutes =
      kind === "work"
        ? cfg.workMin
        : kind === "shortBreak"
        ? cfg.shortBreakMin
        : cfg.longBreakMin;
    const endsAt = now() + minutes * 60 * 1000;
    setState(s => ({
      ...s,
      pomodoro: { ...s.pomodoro, running: true, kind, endsAt, remainingSec: minutes * 60 },
    }));
  }

  function stop() {
    setState(s => ({ ...s, pomodoro: { ...s.pomodoro, running: false, endsAt: undefined } }));
  }

  function advancePomodoro() {
    setState(s => {
      const { kind, cycleCount } = s.pomodoro;
      if (kind === "work") {
        const nextCount = cycleCount + 1;
        const isLong = nextCount >= cfg.sessionsPerCycle;
        return {
          ...s,
          pomodoro: {
            running: false,
            endsAt: undefined,
            remainingSec: undefined,
            kind: isLong ? "longBreak" : "shortBreak",
            cycleCount: nextCount % cfg.sessionsPerCycle,
          },
        };
      } else {
        // break finished -> back to work
        return {
          ...s,
          pomodoro: {
            running: false,
            endsAt: undefined,
            remainingSec: undefined,
            kind: "work",
            cycleCount: s.pomodoro.cycleCount,
          },
        };
      }
    });
  }

  /** ============ Anchor CRUD ============ */
  const [anchorTitle, setAnchorTitle] = useState("");
  const [anchorTags, setAnchorTags] = useState("");

  function addAnchor() {
    const t = anchorTitle.trim();
    if (!t) return;
    const id = uid("a_");
    const tags = anchorTags
      .split(",")
      .map(x => x.trim())
      .filter(Boolean);
    const anchor: Anchor = { id, title: t, tags, createdAt: now() };
    // Create initial recall plan
    const recalls: RecallCard[] = INITIAL_INTERVALS_DAYS.map(days => {
      const dueAt = anchor.createdAt + days * dayMs;
      const rc: RecallCard = {
        id: `${id}@${dueAt}`,
        anchorId: id,
        dueAt,
        intervalDays: days,
        ease: 1.4,
        bucket: 1,
      };
      return rc;
    });
    setState(s => ({
      ...s,
      anchors: { ...s.anchors, [id]: anchor },
      recalls: { ...s.recalls, ...Object.fromEntries(recalls.map(r => [r.id, r])) },
    }));
    setAnchorTitle("");
    setAnchorTags("");
  }

  function deleteAnchor(id: string) {
    setState(s => {
      const anchors = { ...s.anchors };
      delete anchors[id];
      const recalls = { ...s.recalls };
      for (const k of Object.keys(recalls)) if (recalls[k].anchorId === id) delete recalls[k];
      return { ...s, anchors, recalls };
    });
  }

  /** ============ Due recalls ============ */
  const due = useMemo(() => {
    const cards = Object.values(state.recalls)
      .filter(c => c.dueAt <= now())
      .sort((a, b) => a.dueAt - b.dueAt);
    return interleaveDue(cards, state.anchors, 12);
  }, [state.recalls, state.anchors]);

  /** ============ Review action ============ */
  function review(card: RecallCard, feedback: "hard" | "ok" | "easy") {
    setState(s => {
      const clone = { ...s.recalls };
      // retire this card id
      delete clone[card.id];

      const { nextDays, nextEase } = nextIntervalDays(card.intervalDays, card.ease, feedback);
      const nextDue = now() + nextDays * dayMs;

      const next: RecallCard = {
        id: `${card.anchorId}@${nextDue}`,
        anchorId: card.anchorId,
        dueAt: nextDue,
        lastReviewedAt: now(),
        intervalDays: nextDays,
        ease: nextEase,
        bucket:
          feedback === "easy"
            ? Math.min(5, card.bucket + 1)
            : feedback === "hard"
            ? Math.max(1, card.bucket - 1)
            : card.bucket,
      };
      clone[next.id] = next;
      return { ...s, recalls: clone };
    });
  }

  /** ============ Derived ============ */
  const anchorsArr = useMemo(
    () => Object.values(state.anchors).sort((a, b) => b.createdAt - a.createdAt),
    [state.anchors]
  );
  const displayRemainingSec = state.pomodoro.remainingSec ?? sessionLengthSeconds(state.pomodoro.kind, cfg);
  const workRemaining = state.pomodoro.kind === "work" ? displayRemainingSec : 0;

  /** ============ UI ============ */
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6">
      <header className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold">LearnHero Loop — Pomodoro x Interleaving x Spaced</h1>
        <ConfigPanel cfg={cfg} setCfg={setCfg} />
      </header>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Pomodoro */}
        <section className="col-span-1 bg-slate-900 rounded-xl p-4 border border-slate-800">
          <PomodoroBlock
            kind={state.pomodoro.kind}
            running={state.pomodoro.running}
            remainingSec={displayRemainingSec}
            onStart={() => start(state.pomodoro.kind)}
            onStop={stop}
            onNext={advancePomodoro}
          />
          <div className="mt-3 text-xs text-slate-400">
            Cycle progress: {state.pomodoro.cycleCount}/{cfg.sessionsPerCycle}
          </div>

          {/* Anchor entry only during WORK block */}
          <div className="mt-6">
            <h3 className="font-semibold mb-2">Anchor during session</h3>
            <input
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 mb-2"
              placeholder="e.g., CIA triad vs. risk appetite"
              value={anchorTitle}
              onChange={e => setAnchorTitle(e.target.value)}
              disabled={state.pomodoro.kind !== "work"}
            />
            <input
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 mb-2"
              placeholder="tags, comma-separated (e.g., cissp,security,governance)"
              value={anchorTags}
              onChange={e => setAnchorTags(e.target.value)}
              disabled={state.pomodoro.kind !== "work"}
            />
            <button
              className="bg-blue-600 hover:bg-blue-500 px-3 py-2 rounded disabled:opacity-40"
              onClick={addAnchor}
              disabled={state.pomodoro.kind !== "work" || !anchorTitle.trim()}
            >
              Save Anchor
            </button>

            <p className="text-xs text-slate-400 mt-2">
              Anchors created during work blocks auto-schedule recalls at +1d, +3d, +7d, +21d.
            </p>
          </div>
        </section>

        {/* Due recalls */}
        <section className="col-span-2 bg-slate-900 rounded-xl p-4 border border-slate-800">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold">Due now (interleaved)</h3>
            <span className="text-xs text-slate-400">{due.length} shown</span>
          </div>
          {due.length === 0 ? (
            <p className="text-slate-400 mt-4">No recalls due. Use the work block to add anchors.</p>
          ) : (
            <ul className="mt-4 grid md:grid-cols-2 gap-3">
              {due.map(card => {
                const a = state.anchors[card.anchorId];
                if (!a) return null;
                return (
                  <li key={card.id} className="bg-slate-800 rounded-lg p-3 border border-slate-700">
                    <div className="font-semibold">{a.title}</div>
                    <div className="text-xs text-slate-400 mt-1">
                      tags: {a.tags.length ? a.tags.join(", ") : "none"} | bucket {card.bucket} | interval {card.intervalDays}d
                    </div>
                    <div className="flex gap-2 mt-3">
                      <button
                        className="bg-rose-600 hover:bg-rose-500 px-3 py-1 rounded"
                        onClick={() => review(card, "hard")}
                      >
                        Hard
                      </button>
                      <button
                        className="bg-yellow-600 hover:bg-yellow-500 px-3 py-1 rounded"
                        onClick={() => review(card, "ok")}
                      >
                        OK
                      </button>
                      <button
                        className="bg-green-600 hover:bg-green-500 px-3 py-1 rounded"
                        onClick={() => review(card, "easy")}
                      >
                        Easy
                      </button>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}

          {/* Anchors list */}
          <div className="mt-6">
            <h3 className="font-semibold mb-2">Recent anchors</h3>
            {anchorsArr.length === 0 ? (
              <p className="text-slate-400">No anchors yet.</p>
            ) : (
              <ul className="space-y-2">
                {anchorsArr.slice(0, 8).map(a => (
                  <li
                    key={a.id}
                    className="flex items-center justify-between bg-slate-800 border border-slate-700 rounded px-3 py-2"
                  >
                    <div>
                      <div className="font-medium">{a.title}</div>
                      <div className="text-xs text-slate-400">
                        {new Date(a.createdAt).toLocaleString()} — {a.tags.join(", ")}
                      </div>
                    </div>
                    <button
                      className="text-rose-400 hover:text-rose-300 text-sm"
                      onClick={() => deleteAnchor(a.id)}
                    >
                      delete
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </section>
      </div>

      {/* Footer quick-export */}
      <footer className="mt-8 flex items-center gap-3 text-xs text-slate-400">
        <ExportButton state={state} />
        <span>Data lives in localStorage. Export JSON to move devices.</span>
      </footer>
    </div>
  );
}

/** =========================
 *  Components
 *  ========================= */
function PomodoroBlock(props: {
  kind: SessionKind;
  running: boolean;
  remainingSec: number;
  onStart: () => void;
  onStop: () => void;
  onNext: () => void;
}) {
  const { kind, running, remainingSec, onStart, onStop, onNext } = props;
  const label = kind === "work" ? "Work" : kind === "shortBreak" ? "Short Break" : "Long Break";
  return (
    <div>
      <h3 className="font-semibold mb-2">Pomodoro</h3>
      <div className="text-5xl font-mono">{formatTime(remainingSec || 0)}</div>
      <div className="text-slate-400 mt-1">{label}</div>
      <div className="flex gap-2 mt-3">
        {!running ? (
          <button className="bg-blue-600 hover:bg-blue-500 px-3 py-2 rounded" onClick={onStart}>
            Start
          </button>
        ) : (
          <button className="bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded" onClick={onStop}>
            Stop
          </button>
        )}
        <button className="bg-slate-700 hover:bg-slate-600 px-3 py-2 rounded" onClick={onNext}>
          Next
        </button>
      </div>
      <p className="text-xs text-slate-400 mt-2">Work → Short Break ×3 → Long Break (4-session increment).</p>
    </div>
  );
}

function ConfigPanel(props: { cfg: PomodoroConfig; setCfg: (v: PomodoroConfig) => void }) {
  const { cfg, setCfg } = props;
  const [open, setOpen] = useState(false);
  return (
    <div className="relative">
      <button
        className="text-sm bg-slate-800 border border-slate-700 px-3 py-1 rounded"
        onClick={() => setOpen(v => !v)}
      >
        Settings
      </button>
      {open && (
        <div className="absolute right-0 mt-2 bg-slate-900 border border-slate-800 rounded p-4 w-80 shadow-xl">
          <h4 className="font-semibold mb-3">Pomodoro Config</h4>
          <NumberRow label="Work (min)" value={cfg.workMin} onChange={v => setCfg({ ...cfg, workMin: v })} />
          <NumberRow
            label="Short Break (min)"
            value={cfg.shortBreakMin}
            onChange={v => setCfg({ ...cfg, shortBreakMin: v })}
          />
          <NumberRow
            label="Long Break (min)"
            value={cfg.longBreakMin}
            onChange={v => setCfg({ ...cfg, longBreakMin: v })}
          />
          <NumberRow
            label="Sessions per Cycle"
            value={cfg.sessionsPerCycle}
            onChange={v => setCfg({ ...cfg, sessionsPerCycle: v })}
          />
          <p className="text-xs text-slate-400 mt-2">
            Use short durations while testing. Defaults match standard Pomodoro with 4-session increments.
          </p>
        </div>
      )}
    </div>
  );
}

function NumberRow(props: { label: string; value: number; onChange: (v: number) => void }) {
  return (
    <label className="flex items-center justify-between gap-3 mb-2">
      <span className="text-sm">{props.label}</span>
      <input
        type="number"
        className="w-24 bg-slate-800 border border-slate-700 rounded px-2 py-1"
        value={props.value}
        min={1}
        onChange={e => props.onChange(parseInt(e.target.value || "0", 10))}
      />
    </label>
  );
}

function ExportButton(props: { state: AppState }) {
  function exportJSON() {
    const blob = new Blob([JSON.stringify(props.state, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `learnhero-loop-${new Date().toISOString().slice(0, 10)}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
  return (
    <button
      onClick={exportJSON}
      className="bg-slate-800 border border-slate-700 px-3 py-1 rounded hover:bg-slate-700"
    >
      Export JSON
    </button>
  );
}
