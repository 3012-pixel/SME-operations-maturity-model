"""
SME Operations Maturity Model
------------------------------
Author: Kumar Aditya
Purpose: Assess operational analytics maturity of German SMEs across
         five dimensions. Built as part of my M.A. thesis research at
         SRH Berlin on data-driven operations in German SMEs.

Usage:
    python maturity_model.py                  # interactive mode
    python maturity_model.py --sample         # run with sample data
    python maturity_model.py --batch data/sample_responses.csv

Notes:
    I based the five dimensions on the Gartner Analytics Maturity Model
    and the VDMA Industrie 4.0 readiness framework, then adapted them
    specifically for SME contexts (under 250 employees) after reading
    through about a dozen case studies on German Mittelstand digitisation.
    The weights feel right to me but I'd revisit them with more data.
"""

import sys
import csv
import json
import argparse
import os
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# ── Dimension definitions ─────────────────────────────────────────────────────
# Each dimension has 4 questions, each scored 1–5.
# I went with 4 questions per dimension after testing with 6 — too long
# for a typical SME operations manager to sit through in one meeting.

DIMENSIONS = {
    "Data Infrastructure": {
        "weight": 0.20,
        "questions": [
            "How would you rate the quality and completeness of your operational data? (1=scattered/manual, 5=centralised/automated)",
            "To what extent are your operational systems integrated (ERP, WMS, CRM)? (1=siloed, 5=fully integrated)",
            "How often is your operational data updated? (1=monthly/annual, 5=real-time or daily)",
            "Do you have a data governance policy in place? (1=none, 5=documented and enforced)",
        ]
    },
    "Process Standardisation": {
        "weight": 0.20,
        "questions": [
            "How well-documented are your core operational processes? (1=undocumented, 5=fully documented with SOPs)",
            "To what degree are processes followed consistently across teams? (1=ad hoc, 5=audited and enforced)",
            "How mature is your use of KPIs to track operations? (1=no KPIs, 5=KPIs reviewed in regular management cycles)",
            "How quickly can your team adapt processes when something breaks? (1=weeks, 5=same-day with a backup procedure)",
        ]
    },
    "Analytics Capability": {
        "weight": 0.25,
        "questions": [
            "What level of analytics does your team routinely perform? (1=descriptive/reporting only, 5=predictive or prescriptive)",
            "How capable is your team at interpreting data outputs independently? (1=relies on IT, 5=business users run their own analyses)",
            "Do you use dashboards or BI tools in day-to-day decisions? (1=no, 5=yes, with automated alerts)",
            "How often are analytical insights actually acted upon? (1=rarely, 5=systematically feeds into decisions)",
        ]
    },
    "Human Factors": {
        "weight": 0.20,
        "questions": [
            "How would you rate management's support for data-driven decisions? (1=sceptical, 5=actively championed)",
            "How much does your team trust the data they work with? (1=low trust/many workarounds, 5=high trust, used as single source)",
            "Is there a dedicated person or team responsible for data/analytics? (1=no, 5=yes, with clear mandate)",
            "How comfortable are non-technical staff with using data tools? (1=resistant or unable, 5=confident and self-sufficient)",
        ]
    },
    "Value Chain Integration": {
        "weight": 0.15,
        "questions": [
            "How well does data flow between your internal departments (e.g. procurement to production to delivery)? (1=manual handoffs, 5=automated and visible end-to-end)",
            "Do you share data or have visibility into supplier/partner performance? (1=no, 5=yes, with integrated systems)",
            "Can you track a customer order from placement to delivery in real time? (1=no, 5=yes, with customer-facing visibility too)",
            "How well do you use operational data to improve supplier or partner relationships? (1=not at all, 5=structured reviews and shared KPIs)",
        ]
    }
}

# Maturity level labels — based loosely on the CMM model
MATURITY_LEVELS = {
    (1.0, 1.8): ("Level 1 — Initial",    "#e74c3c", "Processes are ad hoc and depend on individual effort. Limited data use."),
    (1.8, 2.6): ("Level 2 — Developing", "#e67e22", "Some processes defined but inconsistently applied. Data use is reactive."),
    (2.6, 3.4): ("Level 3 — Defined",    "#f1c40f", "Processes are documented and data is regularly collected. Insights starting to drive decisions."),
    (3.4, 4.2): ("Level 4 — Managed",    "#2ecc71", "Data-driven decisions are standard. KPIs tracked proactively and linked to strategy."),
    (4.2, 5.1): ("Level 5 — Optimising", "#27ae60", "Continuous improvement culture. Predictive analytics embedded in operations."),
}


def get_maturity_label(score):
    for (low, high), (label, color, description) in MATURITY_LEVELS.items():
        if low <= score < high:
            return label, color, description
    return "Level 5 — Optimising", "#27ae60", "Continuous improvement culture."


def collect_responses_interactive(company_name):
    """Walk through each dimension and question, collect integer scores 1–5."""
    print(f"\n{'='*65}")
    print(f"  SME Operations Maturity Assessment — {company_name}")
    print(f"{'='*65}")
    print("For each question, enter a score from 1 (lowest) to 5 (highest).\n")

    all_scores = {}
    for dim_name, dim_data in DIMENSIONS.items():
        print(f"\n── {dim_name.upper()} ──")
        scores = []
        for i, q in enumerate(dim_data["questions"], 1):
            while True:
                try:
                    val = int(input(f"  Q{i}. {q}\n  Score [1–5]: ").strip())
                    if 1 <= val <= 5:
                        scores.append(val)
                        break
                    else:
                        print("  Please enter a number between 1 and 5.")
                except ValueError:
                    print("  Invalid input — please enter a whole number.")
        all_scores[dim_name] = scores

    return all_scores


def load_csv_responses(filepath):
    """
    Load a batch of company responses from CSV.
    Expected columns: company_name, then one column per question
    (in the same order as DIMENSIONS). The CSV header row is skipped.
    """
    companies = []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("company_name", "Unknown")
            scores_flat = []
            for key, val in row.items():
                if key != "company_name" and key != "industry" and key != "size":
                    try:
                        scores_flat.append(int(val))
                    except ValueError:
                        scores_flat.append(3)  # default to mid if missing

            # reshape flat scores into per-dimension structure
            all_scores = {}
            idx = 0
            for dim_name, dim_data in DIMENSIONS.items():
                n = len(dim_data["questions"])
                all_scores[dim_name] = scores_flat[idx:idx+n]
                idx += n

            industry = row.get("industry", "Unknown")
            size = row.get("size", "Unknown")
            companies.append((name, all_scores, industry, size))

    return companies


def compute_scores(all_scores):
    """Calculate weighted overall score and per-dimension averages."""
    dim_averages = {}
    weighted_total = 0.0
    total_weight = 0.0

    for dim_name, dim_data in DIMENSIONS.items():
        scores = all_scores.get(dim_name, [])
        if scores:
            avg = sum(scores) / len(scores)
        else:
            avg = 0.0
        dim_averages[dim_name] = round(avg, 2)
        weighted_total += avg * dim_data["weight"]
        total_weight += dim_data["weight"]

    overall = round(weighted_total / total_weight, 2) if total_weight else 0
    return dim_averages, overall


def generate_radar_chart(company_name, dim_averages, overall_score, output_dir="outputs"):
    """
    Radar (spider) chart for the five dimensions.
    I spent a while getting the label positioning right — matplotlib's
    polar axes are a bit fiddly when labels overlap at the top.
    """
    os.makedirs(output_dir, exist_ok=True)
    labels = list(dim_averages.keys())
    values = list(dim_averages.values())

    # close the polygon
    values_plot = values + [values[0]]
    N = len(labels)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles_plot = angles + [angles[0]]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#fafafa')

    # background rings at each level
    for level in [1, 2, 3, 4, 5]:
        ring = [level] * (N + 1)
        ax.plot(angles_plot, ring, color='#cccccc', linewidth=0.5, linestyle='--')

    # filled area
    ax.fill(angles_plot, values_plot, color='#2980b9', alpha=0.25)
    ax.plot(angles_plot, values_plot, color='#2980b9', linewidth=2, marker='o', markersize=6)

    ax.set_xticks(angles)
    ax.set_xticklabels(labels, size=10, color='#333333')
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_yticklabels(['1', '2', '3', '4', '5'], size=8, color='#888888')
    ax.set_ylim(0, 5)

    label, color, _ = get_maturity_label(overall_score)
    ax.set_title(
        f"{company_name}\nOverall Maturity: {overall_score}/5.0 — {label}",
        size=13, fontweight='bold', pad=25, color='#222222'
    )

    safe_name = company_name.replace(" ", "_").replace("/", "-").lower()
    filepath = os.path.join(output_dir, f"{safe_name}_radar.png")
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    return filepath


def generate_comparison_chart(results, output_dir="outputs"):
    """
    Bar chart comparing overall scores across multiple companies.
    Only used in batch mode.
    """
    os.makedirs(output_dir, exist_ok=True)
    names = [r["company"] for r in results]
    scores = [r["overall"] for r in results]
    colors = [get_maturity_label(s)[1] for s in scores]

    fig, ax = plt.subplots(figsize=(max(8, len(names) * 1.4), 5))
    fig.patch.set_facecolor('#fafafa')
    ax.set_facecolor('#fafafa')

    bars = ax.bar(names, scores, color=colors, edgecolor='white', linewidth=1.5)
    ax.set_ylim(0, 5.5)
    ax.set_ylabel("Overall Maturity Score (out of 5)", fontsize=11)
    ax.set_title("SME Maturity Score Comparison", fontsize=13, fontweight='bold', pad=15)
    ax.axhline(y=3.0, color='#888888', linestyle='--', linewidth=1, label='Threshold (Level 3)')

    for bar, score in zip(bars, scores):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08,
                f'{score}', ha='center', va='bottom', fontsize=10, fontweight='bold')

    # legend for levels
    legend_items = [
        mpatches.Patch(color='#e74c3c', label='Level 1 — Initial'),
        mpatches.Patch(color='#e67e22', label='Level 2 — Developing'),
        mpatches.Patch(color='#f1c40f', label='Level 3 — Defined'),
        mpatches.Patch(color='#2ecc71', label='Level 4 — Managed'),
        mpatches.Patch(color='#27ae60', label='Level 5 — Optimising'),
    ]
    ax.legend(handles=legend_items, loc='upper right', fontsize=8)
    ax.tick_params(axis='x', rotation=20)

    filepath = os.path.join(output_dir, "comparison_chart.png")
    plt.tight_layout()
    plt.savefig(filepath, dpi=150, bbox_inches='tight')
    plt.close()
    return filepath


def print_report(company_name, dim_averages, overall_score, industry="", size=""):
    """Print a readable summary to the terminal."""
    label, _, description = get_maturity_label(overall_score)
    print(f"\n{'='*65}")
    print(f"  MATURITY ASSESSMENT REPORT")
    print(f"  Company : {company_name}")
    if industry:
        print(f"  Industry: {industry}")
    if size:
        print(f"  Size    : {size}")
    print(f"  Date    : {datetime.now().strftime('%d %b %Y')}")
    print(f"{'='*65}")
    print(f"\n  Overall Score  : {overall_score} / 5.0")
    print(f"  Maturity Level : {label}")
    print(f"  Summary        : {description}")
    print(f"\n  Dimension Breakdown:")
    print(f"  {'Dimension':<30} {'Score':>6}  {'Bar':}")
    print(f"  {'-'*55}")
    for dim, score in dim_averages.items():
        bar = '█' * int(score * 4)
        print(f"  {dim:<30} {score:>5.2f}  {bar}")
    print()


def save_json_report(company_name, dim_averages, overall_score,
                     radar_path, industry="", size="", output_dir="outputs"):
    """Save results as JSON for further analysis or integration."""
    os.makedirs(output_dir, exist_ok=True)
    label, _, description = get_maturity_label(overall_score)
    report = {
        "company": company_name,
        "industry": industry,
        "size": size,
        "date": datetime.now().strftime('%Y-%m-%d'),
        "overall_score": overall_score,
        "maturity_level": label,
        "description": description,
        "dimensions": dim_averages,
        "chart": radar_path
    }
    safe_name = company_name.replace(" ", "_").replace("/", "-").lower()
    filepath = os.path.join(output_dir, f"{safe_name}_report.json")
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description='SME Operations Maturity Model — assess how data-driven an SME really is.'
    )
    parser.add_argument('--sample', action='store_true',
                        help='Run a quick demo with hardcoded sample data')
    parser.add_argument('--batch', metavar='CSV_FILE',
                        help='Assess multiple companies from a CSV file')
    args = parser.parse_args()

    if args.sample:
        # Quick demo so someone can see output without sitting through the questions
        print("\nRunning sample mode with Mustermann GmbH demo data...")
        sample_scores = {
            "Data Infrastructure":      [3, 2, 3, 2],
            "Process Standardisation":  [4, 3, 3, 4],
            "Analytics Capability":     [2, 2, 3, 2],
            "Human Factors":            [3, 3, 2, 3],
            "Value Chain Integration":  [2, 1, 2, 2],
        }
        company = "Mustermann GmbH"
        dim_avgs, overall = compute_scores(sample_scores)
        print_report(company, dim_avgs, overall, industry="Manufacturing", size="120 employees")
        chart = generate_radar_chart(company, dim_avgs, overall)
        json_file = save_json_report(company, dim_avgs, overall, chart,
                                     industry="Manufacturing", size="120 employees")
        print(f"  Radar chart saved : {chart}")
        print(f"  JSON report saved : {json_file}\n")

    elif args.batch:
        companies = load_csv_responses(args.batch)
        results = []
        for name, scores, industry, size in companies:
            dim_avgs, overall = compute_scores(scores)
            print_report(name, dim_avgs, overall, industry, size)
            chart = generate_radar_chart(name, dim_avgs, overall)
            json_file = save_json_report(name, dim_avgs, overall, chart, industry, size)
            results.append({"company": name, "overall": overall, "dimensions": dim_avgs})
            print(f"  Radar chart : {chart}")
            print(f"  JSON report : {json_file}")

        comparison_chart = generate_comparison_chart(results)
        print(f"\n  Comparison chart saved: {comparison_chart}")

    else:
        # Interactive single-company mode
        print("\nSME Operations Maturity Model")
        print("Developed by Kumar Aditya — SRH Berlin, 2025")
        company = input("\nEnter company name (or press Enter for 'My Company'): ").strip()
        if not company:
            company = "My Company"
        industry = input("Industry (optional): ").strip()
        size = input("Company size — employees (optional): ").strip()

        all_scores = collect_responses_interactive(company)
        dim_avgs, overall = compute_scores(all_scores)
        print_report(company, dim_avgs, overall, industry, size)
        chart = generate_radar_chart(company, dim_avgs, overall)
        json_file = save_json_report(company, dim_avgs, overall, chart, industry, size)
        print(f"  Radar chart saved : {chart}")
        print(f"  JSON report saved : {json_file}\n")


if __name__ == "__main__":
    main()
