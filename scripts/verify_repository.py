#!/usr/bin/env python3
"""Verify repository structure, data contracts, and published demo invariants."""

from __future__ import annotations

import json
import math
import re
import zipfile
from pathlib import Path

import yaml

from finops.adapters import CsvRepository
from finops.engine import FinOpsEngine
from finops.models import model_to_dict

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_PATHS = (
    "README.md",
    "README_TR.md",
    "SECURITY.md",
    "Dockerfile",
    "compose.yaml",
    "pyproject.toml",
    ".github/workflows/ci.yml",
    ".github/workflows/codeql.yml",
    ".github/workflows/security.yml",
    "deploy/kubernetes/base/deployment.yaml",
    "deploy/kubernetes/overlays/production/kustomization.yaml",
    "deploy/helm/finops-optimizer/Chart.yaml",
    "infra/terraform/main.tf",
    "observability/grafana/finops-dashboard.json",
    "policies/finops/kubernetes.rego",
    "docs/architecture.md",
    "docs/security-threat-model.md",
    "docs/portfolio/PROJECT_DESCRIPTION_TR.md",
    "docs/portfolio/PROJECT_DESCRIPTION_EN.md",
    "output/pdf/Huawei_Cloud_FinOps_Executive_Report_EN_TR.pdf",
    "presentation/Huawei_Cloud_FinOps_Executive_Deck_EN.pptx",
    "reports/demo-analysis.json",
)

YAML_ROOTS = (
    ".github",
    "deploy/kubernetes",
    "observability",
    "policies",
)

SECRET_PATTERNS = {
    "AWS access key": re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    "GitHub token": re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]{20,}\b"),
    "private key": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    "Huawei AK/SK assignment": re.compile(
        r"(?im)^\s*HW_(?:ACCESS|SECRET)_KEY\s*=\s*[\"']?[A-Za-z0-9/+]{16,}"
    ),
}


def fail(message: str) -> None:
    print(f"[FAIL] {message}")
    raise SystemExit(1)


def verify_required_files() -> None:
    missing = [path for path in REQUIRED_PATHS if not (ROOT / path).is_file()]
    if missing:
        fail(f"missing required files: {', '.join(missing)}")


def verify_json() -> int:
    checked = 0
    for path in ROOT.rglob("*.json"):
        if {"tmp", ".venv", "__pycache__", ".pytest_cache"}.intersection(path.parts):
            continue
        if any(part.startswith(".") and part not in {".github"} for part in path.parts):
            continue
        with path.open(encoding="utf-8") as stream:
            json.load(stream)
        checked += 1
    return checked


def verify_yaml() -> int:
    checked = 0
    for relative_root in YAML_ROOTS:
        for pattern in ("*.yaml", "*.yml"):
            for path in (ROOT / relative_root).rglob(pattern):
                with path.open(encoding="utf-8") as stream:
                    list(yaml.safe_load_all(stream))
                checked += 1

    for path in (
        ROOT / "compose.yaml",
        ROOT / "deploy/helm/finops-optimizer/Chart.yaml",
        ROOT / "deploy/helm/finops-optimizer/values.yaml",
    ):
        with path.open(encoding="utf-8") as stream:
            list(yaml.safe_load_all(stream))
        checked += 1
    return checked


def verify_demo_contract() -> None:
    repository = CsvRepository(ROOT / "data/demo")
    if len(repository.resources()) != 15:
        fail("demo contract must contain 15 resources")
    if len(repository.costs()) != 2_715:
        fail("demo contract must contain 2,715 cost records")
    if len(repository.utilization()) != 1_320:
        fail("demo contract must contain 1,320 utilization samples")
    if len(repository.budgets()) != 4:
        fail("demo contract must contain four budgets")

    generated = FinOpsEngine(repository).full_analysis(3)
    expected = json.loads((ROOT / "reports/demo-analysis.json").read_text())
    generated_json = json.loads(
        json.dumps(generated, default=model_to_dict, sort_keys=True)
    )
    if generated_json != expected:
        fail("reports/demo-analysis.json is not reproducible from data/demo")

    summary = expected["summary"]
    invariants = {
        "positive current cost": summary["current_monthly_cost"] > 0,
        "positive savings": summary["estimated_monthly_savings"] > 0,
        "savings below cost": (
            summary["estimated_monthly_savings"] < summary["current_monthly_cost"]
        ),
        "annualized savings": math.isclose(
            summary["annualized_savings"],
            summary["estimated_monthly_savings"] * 12,
            rel_tol=0,
            abs_tol=0.01,
        ),
        "allocation percentage": 0 <= summary["allocation_coverage_pct"] <= 100,
        "budget percentage": 0 <= summary["budget_coverage_pct"] <= 100,
        "maturity score": 0 <= summary["maturity_score"] <= 100,
        "recommendation count": (
            summary["recommendation_count"] == len(expected["recommendations"])
        ),
        "anomaly count": summary["anomaly_count"] == len(expected["anomalies"]),
    }
    failed = [name for name, passed in invariants.items() if not passed]
    if failed:
        fail(f"demo invariants failed: {', '.join(failed)}")


def verify_workload_security() -> None:
    deployment = yaml.safe_load(
        (ROOT / "deploy/kubernetes/base/deployment.yaml").read_text()
    )
    pod = deployment["spec"]["template"]["spec"]
    container = pod["containers"][0]
    labels = deployment["spec"]["template"]["metadata"]["labels"]
    required_labels = {
        "finops.huaweicloud.com/cost-center",
        "finops.huaweicloud.com/owner",
        "finops.huaweicloud.com/environment",
    }
    checks = {
        "service-account token disabled": not pod["automountServiceAccountToken"],
        "pod runs as non-root": pod["securityContext"]["runAsNonRoot"],
        "read-only root filesystem": container["securityContext"][
            "readOnlyRootFilesystem"
        ],
        "resource requests": bool(container["resources"]["requests"]),
        "resource limits": bool(container["resources"]["limits"]),
        "readiness probe": bool(container["readinessProbe"]),
        "liveness probe": bool(container["livenessProbe"]),
        "FinOps labels": required_labels <= labels.keys(),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        fail(f"workload security checks failed: {', '.join(failed)}")


def verify_no_secrets() -> None:
    findings: list[str] = []
    excluded = {".git", ".venv", "tmp", "__pycache__", ".pytest_cache"}
    for path in ROOT.rglob("*"):
        if not path.is_file() or excluded.intersection(path.parts):
            continue
        if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".pdf", ".pptx"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)} ({name})")
    if findings:
        fail(f"potential credentials found: {', '.join(findings)}")


def verify_executive_artifacts() -> None:
    deck = ROOT / "presentation/Huawei_Cloud_FinOps_Executive_Deck_EN.pptx"
    with zipfile.ZipFile(deck) as archive:
        slides = [
            name
            for name in archive.namelist()
            if name.startswith("ppt/slides/slide") and name.endswith(".xml")
        ]
        notes = [
            name
            for name in archive.namelist()
            if name.startswith("ppt/notesSlides/notesSlide") and name.endswith(".xml")
        ]
    if len(slides) != 18:
        fail(f"executive deck must contain 18 slides, found {len(slides)}")
    if len(notes) != 18:
        fail(f"executive deck must contain 18 source-note pages, found {len(notes)}")

    report = (
        ROOT / "output/pdf/Huawei_Cloud_FinOps_Executive_Report_EN_TR.pdf"
    ).read_bytes()
    if not report.startswith(b"%PDF-"):
        fail("executive report does not have a valid PDF header")
    if b"/Count 20" not in report:
        fail("executive report must contain 20 pages")


def main() -> None:
    verify_required_files()
    json_count = verify_json()
    yaml_count = verify_yaml()
    verify_demo_contract()
    verify_workload_security()
    verify_no_secrets()
    verify_executive_artifacts()
    file_count = sum(
        path.is_file()
        for path in ROOT.rglob("*")
        if not {".git", ".venv", "tmp"}.intersection(path.parts)
    )
    print(
        "[PASS] repository contracts verified: "
        f"{file_count} files, {json_count} JSON documents, "
        f"{yaml_count} YAML documents, deterministic demo analysis, "
        "18-slide deck, 20-page report"
    )


if __name__ == "__main__":
    main()
