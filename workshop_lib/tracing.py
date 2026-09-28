"""Readable traces plus token and cost accounting, so learners can see the loop working."""
from __future__ import annotations

import json
import re
from collections import defaultdict

from . import config

COLORS = {"orchestrator": "\033[95m", "web-researcher": "\033[94m", "policy-reviewer": "\033[92m"}
RESET, DIM, BOLD = "\033[0m", "\033[2m", "\033[1m"


def approx_tokens(obj) -> int:
    """Rough token estimate (about 4 characters per token). Good enough to compare payload sizes."""
    s = obj if isinstance(obj, str) else json.dumps(obj, default=str, ensure_ascii=False)
    return max(1, len(s) // 4)


class Tracer:
    def __init__(self, verbose: bool = True, width: int = 160):
        self.verbose, self.width = verbose, width
        self.usage = defaultdict(lambda: {"calls": 0, "input": 0, "output": 0, "model": None})
        self.events: list[dict] = []

    # -- printing
    def _p(self, agent: str, depth: int, msg: str):
        if self.verbose:
            c = COLORS.get(agent, "")
            print(f"{'    ' * depth}{c}[{agent}]{RESET} {msg}")

    def _short(self, obj) -> str:
        s = obj if isinstance(obj, str) else json.dumps(obj, default=str, ensure_ascii=False)
        return s if len(s) <= self.width else s[: self.width] + f"{DIM}... (+{len(s) - self.width} chars){RESET}"

    def turn(self, agent, depth, turn, response):
        u = self.usage[agent]
        u["calls"] += 1
        u["model"] = response.model if hasattr(response, "model") else u["model"]
        u["input"] += getattr(response.usage, "input_tokens", 0) or 0
        u["output"] += getattr(response.usage, "output_tokens", 0) or 0
        self.events.append({"agent": agent, "turn": turn, "stop_reason": response.stop_reason})
        self._p(agent, depth, f"{DIM}turn {turn}: stop_reason={BOLD}{response.stop_reason}{RESET}{DIM} "
                              f"(in={response.usage.input_tokens}, out={response.usage.output_tokens}){RESET}")
        for b in response.content:
            if b.type == "text" and b.text.strip():
                self._p(agent, depth, "💬 " + self._short(b.text.strip().replace("\n", " ")))

    def tool_call(self, agent, depth, name, args):
        self._p(agent, depth, f"🔧 {BOLD}{name}{RESET}({self._short(args)})")

    def tool_result(self, agent, depth, name, result, is_error=False):
        tag = "❌" if is_error else "↳"
        self._p(agent, depth, f"   {tag} {self._short(result)}")

    def note(self, agent, depth, msg):
        self._p(agent, depth, f"⚠️  {msg}")

    # -- summary
    def cost_table(self) -> str:
        lines = [f"{'agent':<18}{'model':<30}{'calls':>6}{'in tok':>10}{'out tok':>10}{'USD':>9}"]
        total = 0.0
        for agent, u in self.usage.items():
            model = u["model"] or "?"
            key = re.sub(r"[^a-z0-9]", "", model.lower().split("/")[-1])
            pin, pout = next((v for k, v in config.PRICES.items()
                              if re.sub(r"[^a-z0-9]", "", k.split("/")[-1]) in key), (0, 0))
            usd = u["input"] / 1e6 * pin + u["output"] / 1e6 * pout
            total += usd
            lines.append(f"{agent:<18}{model[:29]:<30}{u['calls']:>6}{u['input']:>10}{u['output']:>10}{usd:>9.4f}")
        lines.append(f"{'TOTAL':<72}{total:>9.4f}")
        return "\n".join(lines)
