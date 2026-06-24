# SME Operations Maturity Model

A Python-based tool to assess how data-driven a small or medium-sized enterprise (SME) really is — built as part of my M.A. thesis research at SRH Berlin on *"Data-Driven Operations in German SMEs."*

---

## Why I Built This

During my thesis, I kept running into the same problem: there's no lightweight, practical tool for assessing analytics maturity in SMEs specifically. Most frameworks (Gartner, IDC) are designed for large enterprises and assume dedicated data teams, expensive BI platforms, and mature governance structures. A 60-person Mittelstand manufacturer doesn't fit that mould.

So I built one that does.

The model draws on:
- Gartner's Analytics Maturity Model (for the dimension structure)
- VDMA's Industrie 4.0 Readiness Index (for SME-specific calibration)
- Deloitte's Digital Maturity Assessment (for human factors framing)
- My own fieldwork reading through SME digitisation case studies from the Fraunhofer IEM and IfM Bonn

---

## What It Measures

Five dimensions, each scored 1–5 with four questions:

| Dimension | Weight | What it covers |
|---|---|---|
| Data Infrastructure | 20% | Data quality, system integration, update frequency, governance |
| Process Standardisation | 20% | Documentation, consistency, KPI use, adaptability |
| Analytics Capability | 25% | Analysis depth, team capability, BI tool use, decision impact |
| Human Factors | 20% | Management buy-in, data trust, ownership, staff confidence |
| Value Chain Integration | 15% | Internal data flow, supplier visibility, order tracking, partner KPIs |

Analytics Capability gets the highest weight because it's the biggest differentiator I found between companies that *have* data and companies that actually *use* it.

### Maturity Levels

| Score | Level | What it means |
|---|---|---|
| 1.0–1.8 | Level 1 — Initial | Ad hoc, person-dependent |
| 1.8–2.6 | Level 2 — Developing | Reactive data use |
| 2.6–3.4 | Level 3 — Defined | Documented and consistent |
| 3.4–4.2 | Level 4 — Managed | Proactive and KPI-driven |
| 4.2–5.0 | Level 5 — Optimising | Predictive, continuous improvement |

---

## Sample Output

![Radar chart for Mustermann GmbH demo](outputs/mustermann_gmbh_radar.png)

---

## How to Use It

### 1. Install dependencies
```bash
pip install matplotlib numpy
```

### 2. Run in interactive mode (single company)
```bash
python maturity_model.py
```
You'll be prompted to enter scores for each question. Takes about 10 minutes for someone who knows the company well.

### 3. Run with sample data (quick demo)
```bash
python maturity_model.py --sample
```

### 4. Run batch mode (multiple companies from CSV)
```bash
python maturity_model.py --batch data/sample_responses.csv
```
This produces individual radar charts and a side-by-side comparison chart.

---

## Output Files

All outputs go into the `outputs/` folder:
- `<company_name>_radar.png` — radar chart for each company
- `<company_name>_report.json` — machine-readable summary
- `comparison_chart.png` — batch mode comparison (when running with --batch)

---

## Sample Data

`data/sample_responses.csv` contains 10 fictional German SMEs across industries (manufacturing, logistics, IT, food & beverage, etc.) to demonstrate the batch comparison mode. The scores are my rough estimates of realistic sector variation based on the digitisation surveys I read — not real companies.

---

## Limitations

- Self-reported scores mean the tool is only as honest as the person filling it in. Works best when done as a structured interview rather than a self-assessment form.
- The weights (especially the 25% on Analytics Capability) are my judgment call. I'd want to validate them against actual performance outcomes with a larger sample.
- No industry benchmarking yet — that would need real data I don't have access to. It's on my list.

---

## Project Structure

```
sme-maturity-model/
├── maturity_model.py          # main script
├── data/
│   └── sample_responses.csv  # 10 demo companies
├── outputs/                   # generated charts and reports
└── README.md
```

---

## Skills Used
`Python` · `Matplotlib` · `NumPy` · `Data Modelling` · `Framework Design` · `SME Analytics`

---

## Related
This project feeds into my broader thesis on analytical capability maturity in German SMEs. The five-dimension model here is a simplified version of the fuller framework in the thesis.
