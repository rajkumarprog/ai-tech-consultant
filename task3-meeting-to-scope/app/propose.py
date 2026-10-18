import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "shared"))
from llm import LLMUnavailable, complete   # noqa: E402

AC_SYSTEM = ("Write ONE testable acceptance criterion, a single sentence, for this client "
             "requirement. Do not promise dates or prices. Reply with only the sentence.")


def acceptance(desc):
    try:
        return complete(AC_SYSTEM, desc, task="acceptance", max_tokens=600).strip()
    except LLMUnavailable:
        return "TBD: confirm with client"


def hours(row, key):
    return sum(t[key] for t in row.get("tasks", []))


def next_version(meeting):
    nums = [int(p.stem.rsplit("_v", 1)[1])
            for p in Path("data").glob(f"proposal_{meeting}_v*.md")]
    return max(nums, default=0) + 1


def load(name):
    p = Path(name)
    if not p.exists():
        sys.exit(f"Missing {p}. Run the earlier steps first.")
    return json.loads(p.read_text())


def build(meeting):
    ext = load(f"data/extracted_{meeting}.json")
    feas = {r["id"]: r for r in load(f"data/feasibility_{meeting}.json")}
    est = load(f"data/estimate_{meeting}.json")
    est_by = {r["id"]: r for r in est["requirements"]}
    rate, cur = est["hourly_rate_placeholder"], est["currency"]
    L = [f"# Scope and proposal: {meeting}", "",
         "> STATUS: DRAFT. Not approved. Must not be sent to the client.", "",
         "## 1. Requirements, platform check and estimate", ""]
    for r in ext["requirements"]:
        if r["action"] == "remove":
            continue
        f, e = feas.get(r["id"], {}), est_by.get(r["id"], {})
        L += [f"### {r['id']}: {r['description']}",
              f"- Client said: \"{r['quote']}\" (status: {r['status']})",
              f"- Platform check: {f.get('label', 'not checked')}. {f.get('reason', '')}"]
        for s in f.get("sources", [])[:2]:
            L.append(f"  - source: {s['url']}")
        if e.get("status") == "estimated":
            tag = " (PROVISIONAL)" if e.get("provisional") else ""
            L.append(f"- Estimate{tag}: {hours(e, 'low'):.1f} / {hours(e, 'likely'):.1f} / "
                     f"{hours(e, 'high'):.1f} h (low / likely / high)")
        else:
            L.append("- Estimate: needs a human estimate")
        L += [f"- Acceptance criterion (confirm with client): {acceptance(r['description'])}", ""]
    t, cost = est["totals_hours"], est["totals_cost"]
    L += ["## 2. Totals", "",
          f"- Hours (low / likely / high): {t['low']} / {t['likely']} / {t['high']}",
          f"- Cost at placeholder {rate}/h {cur}: {cost['low']} / {cost['likely']} / "
          f"{cost['high']} (NOT a quote)"]
    b = est.get("client_budget")
    if b:
        L.append(f"- Client budget: {b:.0f} {cur}")
        if cost["likely"] > b:
            L.append("- WARNING: likely cost exceeds the client's stated budget. "
                     "Discuss scope or phasing.")
    prov = [r["id"] for r in est["requirements"] if r.get("provisional")]
    L += ["", "## 3. Constraints stated by the client", ""]
    L += [f"- {ct['type']}: {ct['value']}" for ct in ext["constraints"]]
    L += ["", "## 4. Assumptions and risks", "",
          "- Estimates are provisional where the platform check was inconclusive: "
          + (", ".join(prov) or "none"),
          "- The hourly rate is a placeholder; taxes and currency are not decided.",
          "", "## 5. Open questions", ""]
    L += [f"- {q}" for q in ext["open_questions"]] or ["- none recorded"]
    L += ["", "## 6. Exclusions", "",
          "- Reviewer must list anything the client explicitly excluded before approval."]
    path = Path(f"data/proposal_{meeting}_v{next_version(meeting)}.md")
    path.write_text("\n".join(L) + "\n")
    return path


if __name__ == "__main__":
    print("Wrote", build(sys.argv[1]))
