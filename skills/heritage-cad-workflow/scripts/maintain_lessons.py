"""Project-local lesson transactions. Dry run by default; never opens CAD files.

Mechanical gates do not authenticate evidence or replace semantic review by Codex.
"""
from __future__ import annotations

import argparse
import ast
from datetime import date
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata

ROUTES = {
    "general": "SKILL.md",
    "lineart": "references/lineart-cleaning.md",
    "geometry": "references/geometry-constraints.md",
    "motif": "references/motif-preservation.md",
    "transfer": "references/dxf-transfer.md",
    "quality": "references/quality-audit.md",
}
INDEX = "references/lesson-index.json"
VERIFIED = "references/lessons-learned.md"
PENDING = "references/pending-lessons.md"
FIELDS = ("date", "task_type", "problem", "cause", "evidence", "solution", "validation")
PRIVATE = re.compile(r"[A-Za-z]:[\\/]|/Users/|/home/[^ /]+/|(?:sk-|ghp_|github_pat_)[A-Za-z0-9_-]{16,}|Bearer\s+\S+|eyJ[A-Za-z0-9_-]{20,}\.")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def normalized(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKC", text).casefold() if c.isalnum())


def fingerprint(p: dict) -> str:
    return digest((p["topic"] + normalized(p["problem"]) + normalized(p["solution"])).encode())


def safe_path(name: str) -> str:
    p = PurePosixPath(name)
    if "\\" in name or p.is_absolute() or ".." in p.parts or ":" in name:
        raise ValueError("Unsafe relative path")
    if name not in ("SKILL.md", "CHANGELOG.md") and not (
        p.parts and p.parts[0] == "references" and p.suffix in (".md", ".json")
    ) and not (p.parts and p.parts[0] in ("scripts", "tests") and p.suffix == ".py"):
        raise ValueError("Path outside automatic maintenance scope: " + name)
    return name


def read_index(root: Path) -> list:
    path = root / INDEX
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else []


def validate_proposal(raw: dict) -> dict:
    p = dict(raw)
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,79}", p.get("id", "")):
        raise ValueError("Invalid lesson id")
    if p.get("topic") not in ROUTES or p.get("status") not in ("VERIFIED", "CANDIDATE", "REJECTED"):
        raise ValueError("Invalid topic/status")
    for field in FIELDS:
        if not isinstance(p.get(field), str) or not p[field].strip() or len(p[field]) > 2400:
            raise ValueError("Missing or oversized field: " + field)
    date.fromisoformat(p["date"])
    if PRIVATE.search("\n".join(p[k] for k in FIELDS)):
        raise ValueError("Private absolute path or probable credential in lesson record")
    if p.get("review") not in ("clear", "conflict"):
        raise ValueError("Explicit semantic conflict review required")
    if p["review"] == "conflict":
        p["status"] = "CANDIDATE"
        p["validation"] += "；与现有约束冲突，等待人工确认，未提升为执行规则。"
    if p["status"] == "VERIFIED" and p.get("validation_passed") is not True:
        raise ValueError("VERIFIED requires actual successful validation")
    patches = p.get("patches", {})
    if patches and p["status"] != "VERIFIED":
        raise ValueError("Unverified/conflicting lesson cannot change rules or code")
    if not isinstance(patches, dict):
        raise ValueError("patches must map relative paths to complete UTF-8 content")
    for name, content in patches.items():
        safe_path(name)
        if name in (INDEX, VERIFIED, PENDING, "CHANGELOG.md") or not isinstance(content, str):
            raise ValueError("Ledgers are managed by the transaction")
    if p["status"] != "VERIFIED" and p.get("rule"):
        raise ValueError("Unverified lesson cannot supply an execution rule")
    if p.get("rule") and (not isinstance(p["rule"], str) or PRIVATE.search(p["rule"])):
        raise ValueError("Invalid rule")
    p["fingerprint"] = fingerprint(p)
    return p


def entry(p: dict, files: list[str]) -> str:
    labels = {"date": "日期", "task_type": "任务类型", "problem": "问题", "cause": "原因", "evidence": "证据", "solution": "方法", "validation": "验证"}
    lines = [f"## {p['id']} · {p['status']}"]
    lines += [f"- {labels[k]}：{p[k]}" for k in FIELDS]
    lines += ["- 更新文件：" + ("、".join(files) or "仅经验记录，无执行规则变更")]
    return "\n".join(lines) + "\n"


def replace_record(text: str, lesson_id: str, new: str = "") -> str:
    pattern = r"\n?## " + re.escape(lesson_id) + r" · [^\n]+\n.*?(?=\n## |\Z)"
    return re.sub(pattern, "", text, flags=re.S).rstrip() + ("\n\n" + new if new else "\n")


def build(root: Path, raw: dict) -> tuple[dict[str, bytes], dict]:
    p = validate_proposal(raw)
    records = read_index(root)
    same = next((r for r in records if r["id"] == p["id"]), None)
    duplicate = next((r for r in records if r["fingerprint"] == p["fingerprint"]), None)
    if duplicate and duplicate["id"] != p["id"]:
        return {}, {"status": "UNCHANGED", "reason": "duplicate", "existing_id": duplicate["id"]}
    if same:
        if same["status"] == p["status"] and same["fingerprint"] == p["fingerprint"]:
            return {}, {"status": "UNCHANGED", "reason": "already recorded"}
        if same["status"] == "VERIFIED" or same["fingerprint"] != p["fingerprint"]:
            raise ValueError("Existing lesson conflicts; review a new revision explicitly")
    changes = {name: content.encode("utf-8") for name, content in p.get("patches", {}).items()}
    route = ROUTES[p["topic"]]
    if p["status"] == "VERIFIED":
        if p.get("rule"):
            current = changes.get(route, (root / route).read_bytes()).decode("utf-8")
            marker = f"<!-- lesson:{p['id']} -->"
            if marker in current:
                raise ValueError("Duplicate managed rule marker")
            changes[route] = (current.rstrip() + "\n\n" + marker + "\n" + p["rule"].strip() + "\n").encode("utf-8")
        elif not p.get("rule_refs"):
            raise ValueError("Verified lesson must link existing rule_refs or supply a new rule")
        for ref in p.get("rule_refs", []):
            safe_path(ref)
            if not (root / ref).is_file() and ref not in changes:
                raise ValueError("Missing existing rule reference: " + ref)
    modified = sorted(set(changes) | set(p.get("rule_refs", [])))
    destination = VERIFIED if p["status"] == "VERIFIED" else PENDING
    for ledger in (VERIFIED, PENDING):
        original = (root / ledger).read_text(encoding="utf-8")
        updated = replace_record(original, p["id"], entry(p, modified) if ledger == destination else "")
        if updated != original:
            changes[ledger] = updated.encode("utf-8")
    records = [r for r in records if r["id"] != p["id"]]
    records.append({"id": p["id"], "status": p["status"], "topic": p["topic"], "fingerprint": p["fingerprint"], "rule_files": modified})
    changes[INDEX] = (json.dumps(records, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    log = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    changes["CHANGELOG.md"] = (log.rstrip() + f"\n\n- {p['date']} · {p['id']} · {p['status']} · {p['task_type']}\n").encode("utf-8")
    return changes, {"status": p["status"], "id": p["id"], "files": sorted(changes)}


def validate_tree(root: Path, validator: Path | None = None, run_tests: bool = False) -> None:
    for path in root.rglob("*"):
        if path.is_symlink():
            raise ValueError("Symlink not supported inside maintenance tree")
        if path.suffix == ".py" and path.is_file():
            ast.parse(path.read_text(encoding="utf-8-sig"), filename=str(path))
        if path.suffix == ".md" and path.is_file():
            content = path.read_text(encoding="utf-8-sig")
            for target in re.findall(r"\]\(([^)]+)\)", content):
                target = target.strip("<>").split("#")[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (path.parent / target).resolve()
                if not resolved.is_relative_to(root.resolve()) or not resolved.exists():
                    raise ValueError(f"Broken or out-of-skill reference in {path.name}: {target}")
    records = read_index(root)
    for key in ("id", "fingerprint"):
        values = [r[key] for r in records]
        if len(values) != len(set(values)):
            raise ValueError("Duplicate lesson " + key)
    for r in records:
        ledger = VERIFIED if r["status"] == "VERIFIED" else PENDING
        if f"## {r['id']} · {r['status']}" not in (root / ledger).read_text(encoding="utf-8"):
            raise ValueError("Index/ledger mismatch")
    if validator:
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", str(validator), str(root)], capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        if result.returncode:
            raise ValueError("skill-creator validation failed: " + result.stdout + result.stderr)
    if run_tests:
        if not (root / "tests").is_dir():
            raise ValueError("Code update requires related tests")
        result = subprocess.run([sys.executable, "-X", "utf8", "-B", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=root, capture_output=True, text=True, encoding="utf-8", env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        if result.returncode or "Ran 0 tests" in result.stderr:
            raise ValueError("Related tests failed or no tests ran: " + result.stdout + result.stderr)


def transact(root: Path, changes: dict[str, bytes], validator: Path | None = None, commit: bool = False, expected: dict | None = None) -> None:
    root = root.resolve()
    if root.name != "heritage-cad-workflow" or root.is_symlink():
        raise ValueError("Expected project heritage-cad-workflow directory")
    for name in changes:
        safe_path(name)
        if not (root / name).resolve().is_relative_to(root):
            raise ValueError("Path escaped skill")
    original = {n: (root / n).read_bytes() if (root / n).exists() else None for n in changes}
    if expected is not None and any(original[n] != expected.get(n) for n in changes):
        raise ValueError("Concurrent edit since proposal build")
    if any(p.is_symlink() for p in root.rglob("*")):
        raise ValueError("Symlinks are outside maintenance scope")
    with tempfile.TemporaryDirectory(prefix="heritage-lesson-check-") as tmp:
        staged = Path(tmp) / root.name
        shutil.copytree(root, staged, ignore=shutil.ignore_patterns("__pycache__", ".maintenance.lock"))
        for n, data in changes.items():
            (staged / n).parent.mkdir(parents=True, exist_ok=True)
            (staged / n).write_bytes(data)
        validate_tree(staged, validator, any(n.endswith(".py") for n in changes))
    if not commit:
        return
    lock = root / ".maintenance.lock"
    fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    written = []
    try:
        os.write(fd, str(os.getpid()).encode())
        for n, old in original.items():
            current = (root / n).read_bytes() if (root / n).exists() else None
            if current != old:
                raise ValueError("Concurrent edit detected: " + n)
        for n, data in changes.items():
            dest = root / n
            dest.parent.mkdir(parents=True, exist_ok=True)
            # Temp file in destination folder makes each replacement atomic.
            with tempfile.NamedTemporaryFile(dir=dest.parent, delete=False) as f:
                temporary = Path(f.name)
                f.write(data)
            try:
                os.replace(temporary, dest)
            finally:
                temporary.unlink(missing_ok=True)
            written.append(n)
        validate_tree(root, validator)
    except Exception:
        for n in reversed(written):
            if (root / n).read_bytes() != changes[n]:
                raise RuntimeError("Rollback stopped because of external edit: " + n)
            if original[n] is None:
                (root / n).unlink()
            else:
                (root / n).write_bytes(original[n])
        raise
    finally:
        os.close(fd)
        lock.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--proposal", type=Path)
    parser.add_argument("--commit", action="store_true", help="Apply validated lesson; otherwise dry-run")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--skill-validator", type=Path)
    args = parser.parse_args()
    default_validator = Path.home() / ".codex/skills/.system/skill-creator/scripts/quick_validate.py"
    validator = args.skill_validator or (default_validator if default_validator.is_file() else None)
    raw = None
    try:
        if args.check:
            validate_tree(args.skill_root, validator)
            print(json.dumps({"status": "PASS", "skill_creator": validator is not None}))
            return 0
        if not args.proposal:
            parser.error("--proposal or --check is required")
        raw = json.loads(args.proposal.read_text(encoding="utf-8-sig"))
        before = {p.relative_to(args.skill_root).as_posix(): p.read_bytes() for p in args.skill_root.rglob("*") if p.is_file() and not p.is_symlink()}
        changes, result = build(args.skill_root, raw)
        if changes:
            transact(args.skill_root, changes, validator, args.commit, before)
        result["committed"] = bool(changes and args.commit)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        # One bounded attempt to record a sanitized failure; no recursive retry.
        logged = False
        if args.commit and raw and isinstance(raw, dict):
            try:
                identity = raw.get("id", "unknown")
                if not re.fullmatch(r"[a-z0-9-]{3,79}", identity):
                    identity = "unknown"
                failure = {
                    "id": identity[:58] + "-validation-failed", "date": date.today().isoformat(),
                    "topic": "quality", "status": "CANDIDATE", "review": "clear",
                    "task_type": "Skill 更新失败记录", "problem": identity + " 更新校验或事务失败",
                    "cause": "失败类别 " + type(exc).__name__ + "；详细原因须局部复核，未保存输入原文。",
                    "evidence": "维护入口返回失败；正式变更在写入前拒绝或已执行回滚。",
                    "solution": "保持原执行规则，查明原因并通过测试后另行提交。",
                    "validation": "未通过；该记录不构成执行规则。",
                }
                log_changes, _ = build(args.skill_root, failure)
                if log_changes:
                    transact(args.skill_root, log_changes, validator, True)
                logged = True
            except Exception:
                pass
        print(json.dumps({"status": "FAILED", "reason": type(exc).__name__, "failure_recorded": logged, "detail": "Review locally; if unlogged, Codex must record a sanitized cause without retry loops."}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
