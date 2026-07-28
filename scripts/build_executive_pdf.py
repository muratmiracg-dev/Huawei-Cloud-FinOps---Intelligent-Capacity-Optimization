#!/usr/bin/env python3
"""Build the 20-page executive FinOps report with reproducible demo evidence."""

from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen.canvas import Canvas

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output/pdf/Huawei_Cloud_FinOps_Executive_Report_EN_TR.pdf"
PAGE_W, PAGE_H = landscape(A4)

INK = HexColor("#111827")
MUTED = HexColor("#5B6472")
RED = HexColor("#C7000B")
RED_LIGHT = HexColor("#FDE8EA")
PANEL = HexColor("#F1F3F5")
PANEL_DARK = HexColor("#E2E8F0")
NAVY = HexColor("#0B1324")
TEAL = HexColor("#19C7B4")
BLUE = HexColor("#3D8DFF")
LINE = HexColor("#CBD5E1")

FONT = "FinOpsSans"
FONT_BOLD = "FinOpsSans-Bold"


def register_fonts() -> None:
    pdfmetrics.registerFont(
        TTFont(FONT, "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")
    )
    pdfmetrics.registerFont(
        TTFont(FONT_BOLD, "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
    )


def wrap_text(text: str, font: str, size: float, width: float) -> list[str]:
    lines: list[str] = []
    for paragraph in text.splitlines() or [""]:
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            candidate = f"{current} {word}"
            if pdfmetrics.stringWidth(candidate, font, size) <= width:
                current = candidate
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_text(
    canvas: Canvas,
    text: str,
    x: float,
    y: float,
    width: float,
    *,
    font: str = FONT,
    size: float = 12,
    color: Any = INK,
    leading: float | None = None,
    max_lines: int | None = None,
) -> float:
    line_height = leading or size * 1.35
    lines = wrap_text(text, font, size, width)
    if max_lines is not None:
        lines = lines[:max_lines]
    canvas.setFont(font, size)
    canvas.setFillColor(color)
    for line in lines:
        canvas.drawString(x, y, line)
        y -= line_height
    return y


def draw_source(canvas: Canvas, source: str) -> None:
    draw_text(
        canvas,
        f"Source: {source}",
        42,
        25,
        PAGE_W - 126,
        size=7.2,
        color=MUTED,
        leading=9,
        max_lines=2,
    )


def draw_header(
    canvas: Canvas,
    page_number: int,
    title: str,
    *,
    kicker: str = "HUAWEI CLOUD FINOPS",
    source: str = "Repository evidence",
) -> None:
    canvas.setFillColor(RED)
    canvas.rect(42, PAGE_H - 58, 6, 19, stroke=0, fill=1)
    canvas.setFont(FONT_BOLD, 9)
    canvas.setFillColor(RED)
    canvas.drawString(58, PAGE_H - 52, kicker)
    canvas.setFont(FONT_BOLD, 26)
    canvas.setFillColor(INK)
    canvas.drawString(42, PAGE_H - 94, title)
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.8)
    canvas.line(42, PAGE_H - 111, PAGE_W - 42, PAGE_H - 111)
    canvas.setFont(FONT, 8)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(PAGE_W - 42, 25, f"{page_number} / 20")
    draw_source(canvas, source)


def metric(
    canvas: Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    value: str,
    label: str,
    *,
    accent: Any = RED,
) -> None:
    canvas.setFillColor(PANEL)
    canvas.roundRect(x, y, width, height, 8, stroke=0, fill=1)
    canvas.setFillColor(accent)
    canvas.rect(x, y + height - 7, width, 7, stroke=0, fill=1)
    canvas.setFont(FONT_BOLD, 24)
    canvas.setFillColor(INK)
    canvas.drawString(x + 18, y + height - 50, value)
    draw_text(
        canvas,
        label,
        x + 18,
        y + height - 76,
        width - 36,
        size=10.5,
        color=MUTED,
    )


def panel(
    canvas: Canvas,
    x: float,
    y: float,
    width: float,
    height: float,
    heading: str,
    body: str,
    *,
    heading_color: Any = RED,
) -> None:
    canvas.setFillColor(PANEL)
    canvas.roundRect(x, y, width, height, 8, stroke=0, fill=1)
    draw_text(
        canvas,
        heading,
        x + 18,
        y + height - 32,
        width - 36,
        font=FONT_BOLD,
        size=12,
        color=heading_color,
    )
    draw_text(
        canvas,
        body,
        x + 18,
        y + height - 59,
        width - 36,
        size=10,
        color=INK,
        leading=14,
    )


def bullet_list(
    canvas: Canvas,
    items: list[str],
    x: float,
    y: float,
    width: float,
    *,
    size: float = 11,
    color: Any = INK,
    bullet_color: Any = RED,
    gap: float = 14,
) -> float:
    for item in items:
        canvas.setFillColor(bullet_color)
        canvas.circle(x + 4, y + 4, 2.4, stroke=0, fill=1)
        y = draw_text(
            canvas,
            item,
            x + 16,
            y + 8,
            width - 16,
            size=size,
            color=color,
            leading=size * 1.35,
        )
        y -= gap
    return y


def horizontal_bars(
    canvas: Canvas,
    labels: list[str],
    values: list[float],
    x: float,
    y: float,
    width: float,
    *,
    max_value: float | None = None,
    color: Any = RED,
    value_prefix: str = "$",
) -> None:
    maximum = max_value or max(values)
    bar_height = 22
    row_gap = 18
    label_width = 110
    for index, (label, value) in enumerate(zip(labels, values, strict=True)):
        row_y = y - index * (bar_height + row_gap)
        canvas.setFont(FONT, 9.5)
        canvas.setFillColor(INK)
        canvas.drawRightString(x + label_width - 10, row_y + 6, label)
        track_x = x + label_width
        track_width = width - label_width - 60
        canvas.setFillColor(PANEL_DARK)
        canvas.roundRect(track_x, row_y, track_width, bar_height, 4, stroke=0, fill=1)
        canvas.setFillColor(color)
        canvas.roundRect(
            track_x,
            row_y,
            track_width * value / maximum,
            bar_height,
            4,
            stroke=0,
            fill=1,
        )
        canvas.setFont(FONT_BOLD, 9.5)
        canvas.setFillColor(INK)
        canvas.drawRightString(x + width, row_y + 6, f"{value_prefix}{value:,.0f}")


def line_chart(
    canvas: Canvas,
    categories: list[str],
    series: list[tuple[str, list[float], Any]],
    x: float,
    y: float,
    width: float,
    height: float,
    *,
    minimum: float,
    maximum: float,
) -> None:
    left = x + 58
    bottom = y + 38
    chart_width = width - 82
    chart_height = height - 68
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.6)
    for tick in range(5):
        tick_value = minimum + (maximum - minimum) * tick / 4
        tick_y = bottom + chart_height * tick / 4
        canvas.line(left, tick_y, left + chart_width, tick_y)
        canvas.setFont(FONT, 8)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(left - 8, tick_y - 3, f"${tick_value:,.0f}")
    for index, category in enumerate(categories):
        category_x = left + chart_width * index / max(1, len(categories) - 1)
        canvas.setFont(FONT, 8.5)
        canvas.setFillColor(MUTED)
        canvas.drawCentredString(category_x, bottom - 20, category)
    for name, values, color in series:
        points: list[tuple[float, float]] = []
        for index, value in enumerate(values):
            point_x = left + chart_width * index / max(1, len(values) - 1)
            point_y = bottom + chart_height * (value - minimum) / (maximum - minimum)
            points.append((point_x, point_y))
        canvas.setStrokeColor(color)
        canvas.setLineWidth(2.4)
        path = canvas.beginPath()
        path.moveTo(*points[0])
        for point in points[1:]:
            path.lineTo(*point)
        canvas.drawPath(path, stroke=1, fill=0)
        canvas.setFillColor(color)
        for point_x, point_y in points:
            canvas.circle(point_x, point_y, 3.5, stroke=0, fill=1)
        legend_x = left + series.index((name, values, color)) * 145
        canvas.setFillColor(color)
        canvas.rect(legend_x, y + 6, 14, 4, stroke=0, fill=1)
        canvas.setFont(FONT, 8.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(legend_x + 20, y + 3, name)


def table(
    canvas: Canvas,
    rows: list[list[str]],
    x: float,
    y: float,
    widths: list[float],
    row_height: float,
    *,
    font_size: float = 8.5,
) -> None:
    total_width = sum(widths)
    for row_index, row in enumerate(rows):
        row_y = y - (row_index + 1) * row_height
        canvas.setFillColor(NAVY if row_index == 0 else white)
        canvas.rect(x, row_y, total_width, row_height, stroke=0, fill=1)
        current_x = x
        for _column_index, (value, width) in enumerate(zip(row, widths, strict=True)):
            canvas.setStrokeColor(LINE if row_index else NAVY)
            canvas.rect(current_x, row_y, width, row_height, stroke=1, fill=0)
            draw_text(
                canvas,
                value,
                current_x + 7,
                row_y + row_height - 14,
                width - 14,
                font=FONT_BOLD if row_index == 0 else FONT,
                size=font_size,
                color=white if row_index == 0 else INK,
                leading=font_size * 1.2,
                max_lines=2,
            )
            current_x += width


def load_evidence() -> tuple[dict[str, Any], dict[str, str], dict[str, float]]:
    analysis = json.loads((ROOT / "reports/demo-analysis.json").read_text())
    service_by_resource: dict[str, str] = {}
    with (ROOT / "data/demo/resources.csv").open(
        newline="", encoding="utf-8"
    ) as stream:
        for row in csv.DictReader(stream):
            service_by_resource[row["resource_id"]] = row["service"]
    best_by_resource: dict[str, float] = {}
    for recommendation in analysis["recommendations"]:
        resource_id = recommendation["resource_id"]
        best_by_resource[resource_id] = max(
            best_by_resource.get(resource_id, 0.0),
            recommendation["estimated_monthly_savings"],
        )
    savings_by_service: defaultdict[str, float] = defaultdict(float)
    for resource_id, savings in best_by_resource.items():
        savings_by_service[service_by_resource[resource_id]] += savings
    return analysis, service_by_resource, dict(savings_by_service)


def build_report() -> None:
    register_fonts()
    analysis, _, savings_by_service = load_evidence()
    summary = analysis["summary"]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    canvas = Canvas(str(OUTPUT), pagesize=(PAGE_W, PAGE_H))
    canvas.setTitle("Huawei Cloud FinOps & Intelligent Capacity Optimization")
    canvas.setAuthor("Murat Miraç Gedik")
    canvas.setSubject("Executive FinOps and capacity optimization report")

    # 1 - Cover
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, stroke=0, fill=1)
    canvas.setFillColor(RED)
    canvas.rect(48, PAGE_H - 92, 66, 6, stroke=0, fill=1)
    canvas.setFont(FONT_BOLD, 11)
    canvas.drawString(48, PAGE_H - 72, "HUAWEI CLOUD • FINOPS")
    canvas.setFont(FONT_BOLD, 34)
    canvas.setFillColor(white)
    canvas.drawString(48, PAGE_H - 170, "Intelligent capacity.")
    canvas.drawString(48, PAGE_H - 217, "Defensible cloud economics.")
    draw_text(
        canvas,
        "Executive report for an explainable cost, capacity and governance decision platform.",
        48,
        PAGE_H - 270,
        470,
        size=15,
        color=HexColor("#D7DFEA"),
        leading=22,
    )
    canvas.setFont(FONT, 10)
    canvas.setFillColor(HexColor("#AEB9C8"))
    canvas.drawString(48, 62, "Murat Miraç Gedik • July 2026 • EN with TR summary")
    canvas.setFillColor(TEAL)
    canvas.circle(PAGE_W - 145, 160, 78, stroke=0, fill=1)
    canvas.setFillColor(RED)
    canvas.circle(PAGE_W - 90, 230, 34, stroke=0, fill=1)
    canvas.setFillColor(BLUE)
    canvas.circle(PAGE_W - 200, 275, 23, stroke=0, fill=1)
    canvas.showPage()

    # 2 - Executive scorecard
    draw_header(
        canvas,
        2,
        "Executive scorecard",
        source="reports/demo-analysis.json",
    )
    draw_text(
        canvas,
        "The deterministic demo identifies a material savings pool while preserving explicit capacity and governance controls.",
        42,
        PAGE_H - 145,
        700,
        size=14,
        color=INK,
        leading=20,
    )
    metric(canvas, 42, 290, 175, 120, "$6.13K", "Current monthly cost")
    metric(canvas, 232, 290, 175, 120, "$1.52K", "Estimated monthly savings")
    metric(canvas, 422, 290, 175, 120, "24.79%", "Savings opportunity")
    metric(canvas, 612, 290, 175, 120, "96.4", "FinOps maturity score", accent=TEAL)
    panel(
        canvas,
        42,
        135,
        745,
        105,
        "DECISION IMPLICATION",
        "A read-only pilot can validate the top recommendations, confirm capacity headroom and establish realized-savings evidence before any production change.",
    )
    canvas.showPage()

    # 3 - Decision problem
    draw_header(
        canvas,
        3,
        "The decision problem",
        source="docs/optimization-methodology.md",
    )
    panel(
        canvas,
        42,
        295,
        230,
        165,
        "BILLING IS LATE",
        "Invoices and exports explain spend after consumption. They do not prove whether a workload was appropriately sized.",
    )
    panel(
        canvas,
        302,
        295,
        230,
        165,
        "TELEMETRY IS PARTIAL",
        "Utilization shows load but lacks ownership, price and budget context. A low average can hide a critical peak.",
    )
    panel(
        canvas,
        562,
        295,
        230,
        165,
        "SAVINGS CAN OVERLAP",
        "Multiple actions may target one resource. The platform reports only the highest modeled saving per resource.",
    )
    draw_text(
        canvas,
        "The answer is one canonical decision record:",
        42,
        250,
        500,
        font=FONT_BOLD,
        size=15,
    )
    bullet_list(
        canvas,
        [
            "cost + utilization + ownership + budget evidence",
            "risk and confidence attached to every recommendation",
            "human approval, rollback and post-change validation",
        ],
        42,
        220,
        720,
        size=11,
        gap=9,
    )
    canvas.showPage()

    # 4 - Operating loop
    draw_header(
        canvas,
        4,
        "A governed operating loop",
        source="docs/finops-operating-model.md",
    )
    stages = [
        (
            "1",
            "OBSERVE",
            "Normalize billing, inventory, utilization, tags and budgets.",
        ),
        (
            "2",
            "DECIDE",
            "Forecast, detect anomalies and rank explainable recommendations.",
        ),
        (
            "3",
            "GOVERN",
            "Assign owners, enforce policy, approve change and validate outcomes.",
        ),
    ]
    for index, (number, heading, body) in enumerate(stages):
        x = 42 + index * 260
        canvas.setFillColor(RED if index < 2 else TEAL)
        canvas.circle(x + 26, 375, 20, stroke=0, fill=1)
        canvas.setFillColor(white)
        canvas.setFont(FONT_BOLD, 13)
        canvas.drawCentredString(x + 26, 370, number)
        panel(canvas, x, 205, 220, 135, heading, body)
        if index < 2:
            canvas.setStrokeColor(LINE)
            canvas.setLineWidth(2)
            canvas.line(x + 52, 375, x + 258, 375)
    draw_text(
        canvas,
        "The analytics core is read-only. Execution remains an explicit, auditable operating decision.",
        42,
        165,
        745,
        font=FONT_BOLD,
        size=14,
        color=RED,
    )
    canvas.showPage()

    # 5 - Architecture
    draw_header(
        canvas,
        5,
        "Reference architecture",
        source=(
            "docs/images/architecture.png; Huawei Cost Center: "
            "https://support.huaweicloud.com/intl/en-us/usermanual-cost/costcenter_0000001.html"
        ),
    )
    canvas.drawImage(
        str(ROOT / "docs/images/architecture.png"),
        42,
        90,
        width=745,
        height=360,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )
    canvas.showPage()

    # 6 - Data contracts
    draw_header(
        canvas,
        6,
        "Canonical data contracts",
        source=(
            "docs/data-contracts.md; Huawei Cost Analysis: "
            "https://support.huaweicloud.com/intl/en-us/usermanual-cost/costcenter_000002_09.html"
        ),
    )
    contracts = [
        (
            "RESOURCE",
            "Identity, service, region, owner, cost center, product, price mode and capacity.",
        ),
        (
            "COST",
            "Actual and amortized daily cost, usage quantity, currency and resource link.",
        ),
        (
            "UTILIZATION",
            "CPU, memory, network, disk and Kubernetes request saturation samples.",
        ),
        (
            "BUDGET",
            "Scope, limit, actual threshold, forecast threshold and status.",
        ),
    ]
    for index, (heading, body) in enumerate(contracts):
        x = 42 + (index % 2) * 380
        y = 325 if index < 2 else 145
        panel(canvas, x, y, 355, 140, heading, body)
    canvas.showPage()

    # 7 - Service economics
    draw_header(
        canvas,
        7,
        "Service economics",
        source="reports/demo-analysis.json; data/demo/resources.csv",
    )
    service_costs = analysis["allocation"]["service"]
    labels = ["ECS", "CCE", "RDS", "Other"]
    costs = [
        service_costs["ECS"],
        service_costs["CCE_NODE"],
        service_costs["RDS"],
        sum(
            value
            for service, value in service_costs.items()
            if service not in {"ECS", "CCE_NODE", "RDS"}
        ),
    ]
    horizontal_bars(
        canvas,
        labels,
        costs,
        42,
        420,
        475,
        max_value=2400,
        color=BLUE,
    )
    panel(
        canvas,
        550,
        292,
        237,
        180,
        "INTERPRETATION",
        "ECS, CCE and RDS account for $5.15K of modeled monthly resource run-rate. Those same services contain $1.27K of conservative savings opportunity.",
    )
    metric(canvas, 550, 145, 110, 105, "$5.15K", "Top-3 spend", accent=BLUE)
    metric(canvas, 677, 145, 110, 105, "$1.27K", "Top-3 savings")
    canvas.showPage()

    # 8 - Allocation
    draw_header(
        canvas,
        8,
        "Allocation and ownership",
        source=(
            "reports/demo-analysis.json; Huawei Cost Tags: "
            "https://support.huaweicloud.com/intl/en-us/usermanual-cost/costcenter_000005_01.html"
        ),
    )
    products = analysis["allocation"]["product"]
    horizontal_bars(
        canvas,
        ["Commerce", "Insights", "Shared", "Unallocated"],
        [
            products["Commerce"],
            products["Insights"],
            products["Shared"],
            products["unallocated"],
        ],
        42,
        420,
        475,
        max_value=4000,
        color=RED,
    )
    metric(canvas, 555, 350, 232, 115, "97.43%", "Cost allocation coverage")
    panel(
        canvas,
        555,
        155,
        232,
        150,
        "REMEDIATION",
        "Missing cost-center, owner or product metadata creates tagging recommendations. Kubernetes admission policy prevents new unlabeled workloads.",
    )
    canvas.showPage()

    # 9 - Budgets
    draw_header(
        canvas,
        9,
        "Budget exposure",
        source=(
            "reports/demo-analysis.json; Huawei Budgets: "
            "https://support.huaweicloud.com/intl/en-us/usermanual-cost/costcenter_0000023_1.html"
        ),
    )
    budget_rows = [["SCOPE", "LIMIT", "ACTUAL", "FORECAST", "STATUS"]]
    for item in analysis["budgets"]:
        budget_rows.append(
            [
                item["name"],
                f"${item['monthly_limit']:,.0f}",
                f"{item['utilization_pct']:.2f}%",
                f"{item['forecast_utilization_pct']:.2f}%",
                item["status"].replace("_", " ").upper(),
            ]
        )
    table(canvas, budget_rows, 42, 450, [245, 110, 120, 120, 150], 47, font_size=9)
    panel(
        canvas,
        42,
        130,
        745,
        100,
        "CONTROL RESPONSE",
        "Prioritize non-production scheduling and idle cleanup; review Commerce rightsizing and commitment candidates; preserve the healthy Insights baseline.",
    )
    canvas.showPage()

    # 10 - Forecast
    draw_header(
        canvas,
        10,
        "Three-month cost forecast",
        source="reports/demo-analysis.json; src/finops/services/forecast.py",
    )
    forecast = analysis["forecast"]
    line_chart(
        canvas,
        ["Jul", "Aug", "Sep"],
        [
            (
                "Predicted",
                [item["predicted_cost"] for item in forecast],
                RED,
            ),
            (
                "Upper bound",
                [item["upper_bound"] for item in forecast],
                BLUE,
            ),
        ],
        42,
        120,
        520,
        340,
        minimum=5600,
        maximum=7200,
    )
    metric(canvas, 590, 350, 197, 115, "$6.24K", "July point forecast")
    metric(
        canvas,
        590,
        215,
        197,
        115,
        "$6.95K",
        "September upper band",
        accent=BLUE,
    )
    draw_text(
        canvas,
        "Budget controls should use the uncertainty band, not only the point forecast.",
        590,
        175,
        197,
        font=FONT_BOLD,
        size=10.5,
        color=RED,
    )
    canvas.showPage()

    # 11 - Anomalies
    draw_header(
        canvas,
        11,
        "Cost anomaly review",
        source="reports/demo-analysis.json; docs/runbooks/cost-anomaly.md",
    )
    anomalies = analysis["anomalies"]
    for index, item in enumerate(anomalies):
        x = 42 + index * 380
        title = "CCE production node" if "cce" in item["resource_id"] else "ML workload"
        panel(
            canvas,
            x,
            245,
            355,
            210,
            title.upper(),
            (
                f"Date: {item['anomaly_date']}\n"
                f"Actual: ${item['actual_cost']:.2f}\n"
                f"Expected: ${item['expected_cost']:.2f}\n"
                f"Deviation: +{item['deviation_pct']:.2f}%\n"
                f"Severity: {item['severity'].upper()}"
            ),
        )
    draw_text(
        canvas,
        "An anomaly is an investigation trigger, not a root-cause claim.",
        42,
        195,
        745,
        font=FONT_BOLD,
        size=15,
        color=RED,
    )
    bullet_list(
        canvas,
        [
            "confirm owner, release or workload event",
            "compare usage and capacity telemetry",
            "document resolution and baseline effect",
        ],
        42,
        160,
        700,
        size=10.5,
        gap=6,
    )
    canvas.showPage()

    # 12 - Savings portfolio
    draw_header(
        canvas,
        12,
        "Prioritized savings portfolio",
        source="reports/demo-analysis.json",
    )
    top_recommendations = sorted(
        analysis["recommendations"],
        key=lambda item: item["estimated_monthly_savings"],
        reverse=True,
    )[:8]
    horizontal_bars(
        canvas,
        [
            (
                "CCE prod / requests"
                if item["recommendation_type"] == "request_tuning"
                else {
                    "cce-prod-node-a": "CCE prod / size",
                    "ecs-dev-sandbox-01": "Sandbox / idle",
                    "cce-dev-node-01": "CCE dev",
                    "rds-analytics-prod": "Analytics RDS",
                    "ecs-prod-web-02": "Web 2 / size",
                    "rds-orders-prod": "Orders / commit",
                    "ecs-prod-web-01": "Web 1 / commit",
                }.get(item["resource_id"], item["resource_name"][:16])
            )
            for item in top_recommendations
        ],
        [item["estimated_monthly_savings"] for item in top_recommendations],
        42,
        445,
        520,
        max_value=220,
        color=RED,
    )
    metric(
        canvas,
        590,
        350,
        197,
        115,
        "$18.25K",
        "Annualized opportunity",
    )
    panel(
        canvas,
        590,
        155,
        197,
        155,
        "CONSERVATIVE TOTAL",
        "The executive total selects the single largest modeled saving per resource. This prevents schedule, rightsizing and commitment actions from being added twice.",
    )
    canvas.showPage()

    # 13 - Recommendation logic
    draw_header(
        canvas,
        13,
        "Recommendation logic",
        source="src/finops/services/optimization.py; docs/optimization-methodology.md",
    )
    levers = [
        (
            "RIGHTSIZE",
            "Use P95 CPU, memory and required headroom; avoid mean-only decisions.",
        ),
        (
            "ELIMINATE WASTE",
            "Release idle assets, schedule non-production and lifecycle object storage.",
        ),
        (
            "PRICE BETTER",
            "Consider commitments only for stable, reviewed production demand.",
        ),
        (
            "PROTECT CAPACITY",
            "Flag saturation and tune CCE requests before scaling down.",
        ),
    ]
    for index, (heading, body) in enumerate(levers):
        x = 42 + (index % 2) * 380
        y = 325 if index < 2 else 145
        panel(canvas, x, y, 355, 140, heading, body)
    canvas.showPage()

    # 14 - Capacity guardrails
    draw_header(
        canvas,
        14,
        "Capacity guardrails",
        source=(
            "reports/demo-analysis.json; Huawei CCE node pools: "
            "https://support.huaweicloud.com/intl/en-us/usermanual-cce/cce_10_0081.html"
        ),
    )
    metric(canvas, 42, 335, 225, 125, "P95", "Peak-aware utilization evidence")
    metric(canvas, 292, 335, 225, 125, "25%", "Default capacity headroom")
    metric(canvas, 542, 335, 245, 125, "1 HIGH", "Capacity-risk recommendation")
    panel(
        canvas,
        42,
        145,
        745,
        145,
        "ORDER OF OPERATIONS",
        "1. Protect service health.  2. Validate request and limit efficiency.  3. Confirm autoscaling behavior.  4. Only then evaluate scale-down or commitment changes.",
    )
    canvas.showPage()

    # 15 - Security
    draw_header(
        canvas,
        15,
        "Security and control model",
        source="docs/security-threat-model.md; policies/finops/kubernetes.rego",
    )
    security_rows = [
        ["RISK", "CONTROL", "RESIDUAL DECISION"],
        [
            "Credential leakage",
            "Runtime secret or agency; no secrets in repo",
            "Rotate and audit",
        ],
        [
            "Destructive action",
            "Read-only engine; human approval",
            "Named change owner",
        ],
        ["Runaway scaling", "Requests, limits and HPA ceiling", "Capacity review"],
        [
            "Unallocated cost",
            "Required owner and cost-center labels",
            "Tag remediation",
        ],
        ["Supply chain", "CodeQL, Trivy and dependency updates", "Review findings"],
    ]
    table(canvas, security_rows, 42, 455, [190, 340, 215], 48, font_size=8.7)
    panel(
        canvas,
        42,
        110,
        745,
        75,
        "NON-GOAL",
        "The platform does not delete, resize or purchase cloud resources automatically.",
    )
    canvas.showPage()

    # 16 - Huawei deployment
    draw_header(
        canvas,
        16,
        "Huawei Cloud deployment model",
        source="docs/deployment-huawei-cloud.md; infra/terraform",
    )
    deployments = [
        (
            "COST & DATA",
            "Cost Center export or API adapter\nOBS retention and lifecycle\nCanonical analysis data",
        ),
        (
            "RUNTIME",
            "SWR container image\nCCE deployment, HPA and PDB\nNetwork policy and non-root pod",
        ),
        (
            "OPERATIONS",
            "Prometheus-compatible metrics\nGrafana dashboard and alerts\nSMN notification integration",
        ),
    ]
    for index, (heading, body) in enumerate(deployments):
        panel(canvas, 42 + index * 255, 235, 230, 225, heading, body)
    draw_text(
        canvas,
        "Terraform, Helm and Kustomize provide reproducible deployment paths without embedding credentials.",
        42,
        185,
        745,
        font=FONT_BOLD,
        size=13,
        color=RED,
    )
    canvas.showPage()

    # 17 - Observability
    draw_header(
        canvas,
        17,
        "FinOps observability",
        source="docs/images/dashboard-preview.png; observability/",
    )
    canvas.drawImage(
        str(ROOT / "docs/images/dashboard-preview.png"),
        42,
        145,
        width=520,
        height=320,
        preserveAspectRatio=True,
        anchor="c",
        mask="auto",
    )
    panel(
        canvas,
        590,
        300,
        197,
        165,
        "DECISION SIGNALS",
        "Current cost\nSavings opportunity\nAllocation coverage\nBudget status\nAnomaly count\nCapacity risk",
    )
    panel(
        canvas,
        590,
        145,
        197,
        120,
        "OPERATIONS",
        "Health probes, Prometheus metrics and alert rules keep the FinOps service observable.",
    )
    canvas.showPage()

    # 18 - Engineering validation
    draw_header(
        canvas,
        18,
        "Engineering validation",
        source="docs/validation.md; .github/workflows/",
    )
    validation_rows = [
        ["CONTROL", "SCOPE", "RESULT", "GATE"],
        ["Unit tests", "53 scenarios", "PASS", "required"],
        ["Coverage", "branch-aware", "97.09%", ">= 90%"],
        ["Repository", "JSON/YAML/demo", "PASS", "required"],
        ["API", "health + analysis", "PASS", "required"],
        ["Terraform", "fmt + validate", "CI", "required"],
        ["Container", "build + smoke", "CI", "required"],
        ["Security", "CodeQL + Trivy", "CI", "required"],
    ]
    table(canvas, validation_rows, 42, 455, [220, 235, 135, 155], 35, font_size=8.5)
    panel(
        canvas,
        42,
        100,
        745,
        70,
        "LOCAL EVIDENCE VS CI",
        "Python tests, coverage and repository contracts are verified locally. Terraform, container and security workflows execute after publication.",
    )
    canvas.showPage()

    # 19 - Pilot plan
    draw_header(
        canvas,
        19,
        "30-day read-only pilot",
        source="docs/finops-operating-model.md; ROADMAP.md",
    )
    weeks = ["WEEK 1", "WEEK 2", "WEEK 3", "WEEK 4"]
    week_bodies = [
        "Confirm sources, owners and allocation baseline.",
        "Review top 10 recommendations and capacity evidence.",
        "Approve low-risk quick wins and document rollback.",
        "Measure realized savings and operating impact.",
    ]
    for index, (week, body) in enumerate(zip(weeks, week_bodies, strict=True)):
        panel(canvas, 42 + index * 190, 260, 170, 200, week, body)
    draw_text(
        canvas,
        "Success criteria",
        42,
        220,
        250,
        font=FONT_BOLD,
        size=14,
        color=RED,
    )
    bullet_list(
        canvas,
        [
            "100% of top recommendations have owners",
            "realized savings are separated from modeled savings",
            "no action reduces required service headroom",
            "Finance, Platform and product teams accept the evidence log",
        ],
        42,
        190,
        745,
        size=10.5,
        gap=5,
    )
    canvas.showPage()

    # 20 - Turkish summary and sources
    draw_header(
        canvas,
        20,
        "Türkçe yönetici özeti / Sources & scope",
        kicker="HUAWEI CLOUD FINOPS • BILINGUAL HANDOFF",
        source="Repository documentation and official Huawei Cloud references",
    )
    draw_text(
        canvas,
        "TÜRKÇE ÖZET",
        42,
        445,
        340,
        font=FONT_BOLD,
        size=13,
        color=RED,
    )
    bullet_list(
        canvas,
        [
            "Demo portföy aylık 6.133,36 USD maliyet ve 1.520,70 USD tasarruf fırsatı üretmektedir.",
            "Toplam fırsat oranı %24,79; yıllıklandırılmış potansiyel 18.248,40 USD'dir.",
            "Üç bütçe kapsamı aşılmış, iki maliyet anomalisi ve bir yüksek kapasite riski belirlenmiştir.",
            "Karar motoru salt-okunurdur; değişiklikler sahip, onay, geri dönüş ve doğrulama gerektirir.",
            "Önerilen sonraki adım 30 günlük, üretimde otomatik değişiklik yapmayan pilot çalışmadır.",
        ],
        42,
        415,
        345,
        size=9.5,
        gap=5,
    )
    draw_text(
        canvas,
        "PRIMARY SOURCES",
        430,
        445,
        357,
        font=FONT_BOLD,
        size=13,
        color=RED,
    )
    sources = [
        "support.huaweicloud.com/.../costcenter_0000001.html (Cost Center)",
        "support.huaweicloud.com/.../costcenter_000002_09.html (Cost Analysis)",
        "support.huaweicloud.com/.../costcenter_000005_01.html (Cost Tags)",
        "support.huaweicloud.com/.../costcenter_0000023_1.html (Budgets)",
        "support.huaweicloud.com/.../cce_10_0877.html (CCE Cost Governance)",
        "support.huaweicloud.com/.../cce_10_0081.html (CCE Node Pools)",
        "reports/demo-analysis.json (deterministic project evidence)",
    ]
    bullet_list(canvas, sources, 430, 415, 357, size=8.5, gap=4)
    panel(
        canvas,
        430,
        105,
        357,
        105,
        "SCOPE NOTE",
        "All financial figures are synthetic demo outputs and modeled opportunities. They are not realized customer savings or production performance claims.",
    )
    canvas.showPage()

    canvas.save()
    print(f"Wrote {OUTPUT}")
    print(
        "Executive evidence: "
        f"${summary['current_monthly_cost']:,.2f} monthly cost, "
        f"${summary['estimated_monthly_savings']:,.2f} modeled savings, "
        f"{summary['recommendation_count']} recommendations, "
        f"{sum(savings_by_service.values()):,.2f} non-overlapping service savings"
    )


if __name__ == "__main__":
    build_report()
