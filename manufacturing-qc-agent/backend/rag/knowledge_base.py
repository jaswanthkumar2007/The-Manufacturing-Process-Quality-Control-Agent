"""
Manufacturing knowledge base documents for the RAG system.
Covers ISO 9001, SPC, FMEA, common defects, and control charts.
"""

KNOWLEDGE_DOCS = [
    {
        "id": "iso9001_overview",
        "title": "ISO 9001:2015 Quality Management System Overview",
        "content": """
ISO 9001:2015 is the international standard for Quality Management Systems (QMS).
It specifies requirements for organizations that want to demonstrate their ability to
consistently provide products and services that meet customer and regulatory requirements.

Key Principles:
1. Customer Focus – Understanding current and future customer needs
2. Leadership – Top management commitment to quality
3. Engagement of People – Competent, empowered, and engaged employees
4. Process Approach – Managing activities as interrelated processes
5. Improvement – Ongoing improvement of organizational performance
6. Evidence-based Decision Making – Data-driven decisions
7. Relationship Management – Mutually beneficial supplier relationships

Core Clauses (ISO 9001:2015):
- Clause 4: Context of the organization
- Clause 5: Leadership
- Clause 6: Planning (risk-based thinking)
- Clause 7: Support (resources, competence, documented information)
- Clause 8: Operation (production processes, control of nonconforming outputs)
- Clause 9: Performance evaluation (monitoring, audit, management review)
- Clause 10: Improvement (corrective action, continual improvement)

In manufacturing, ISO 9001 requires documented procedures for:
- Incoming material inspection
- In-process quality checks
- Final product inspection and testing
- Calibration of measuring equipment
- Control of nonconforming products
- Corrective and preventive actions (CAPA)
""",
        "tags": ["iso9001", "quality", "standard", "certification"],
    },
    {
        "id": "spc_control_charts",
        "title": "Statistical Process Control (SPC) and Control Charts",
        "content": """
Statistical Process Control (SPC) is a method of quality control that uses statistical
methods to monitor and control a manufacturing process.

Control Charts:
1. X-bar (Mean) Chart – monitors the process mean over time
   - UCL = X-double-bar + A2 * R-bar
   - LCL = X-double-bar - A2 * R-bar
   - A2 constant depends on subgroup size (n=5: A2=0.577)

2. R (Range) Chart – monitors process variation
   - UCL_R = D4 * R-bar (n=5: D4=2.114)
   - LCL_R = D3 * R-bar (n=5: D3=0)

3. p-Chart – monitors proportion of defective items
4. c-Chart – monitors count of defects per unit
5. EWMA – Exponentially Weighted Moving Average for detecting small shifts

Nelson's Rules for Control Chart Violations:
Rule 1: One point beyond 3σ (immediate action required)
Rule 2: Nine consecutive points on one side of the mean
Rule 3: Six consecutive points trending up or down
Rule 4: Fourteen consecutive alternating up-down points
Rule 5: Two of three consecutive points beyond 2σ
Rule 6: Four of five consecutive points beyond 1σ
Rule 7: Fifteen consecutive points within 1σ

Process Capability Indices:
- Cp  = (USL - LSL) / (6 * σ) — potential capability
- Cpk = min[(USL - μ) / (3σ), (μ - LSL) / (3σ)] — actual capability
- Cp ≥ 1.33 is generally considered capable
- Cpk ≥ 1.00 indicates process is centred and capable
""",
        "tags": ["spc", "control-charts", "statistics", "xbar", "r-chart"],
    },
    {
        "id": "fmea_methodology",
        "title": "Failure Mode and Effects Analysis (FMEA)",
        "content": """
FMEA is a systematic approach for identifying potential failures in a product or process
before they occur.

Types of FMEA:
1. Design FMEA (dFMEA) – identifies potential failures in product design
2. Process FMEA (pFMEA) – identifies potential failures in manufacturing processes
3. System FMEA – analyses system-level failures

FMEA Process Steps:
1. List all potential failure modes
2. Describe the effect of each failure
3. Determine the cause of each failure
4. Rate Severity (S): 1-10 (1=no effect, 10=safety hazard)
5. Rate Occurrence (O): 1-10 (1=remote, 10=almost certain)
6. Rate Detection (D): 1-10 (1=almost certain to detect, 10=undetectable)
7. Calculate Risk Priority Number: RPN = S × O × D
8. Identify recommended actions for high-RPN items
9. Implement actions and recalculate RPN

Common Manufacturing Failure Modes:
- Dimensional non-conformance (out-of-tolerance)
- Surface finish defects (scratches, burrs, porosity)
- Material property failures (hardness, tensile strength)
- Assembly errors (missing components, wrong orientation)
- Weld defects (porosity, cracking, undercut)
- Heat treatment failures (wrong temperature/time)
- Contamination (chips, coolant residue)

Action Priority (AP) — newer FMEA standard (AIAG-VDA 2019):
- High: Immediate action required
- Medium: Action should be taken
- Low: Action may be required at discretion of team
""",
        "tags": ["fmea", "failure-analysis", "risk", "rpn"],
    },
    {
        "id": "temperature_anomalies",
        "title": "Temperature Anomalies in Manufacturing Processes",
        "content": """
Temperature control is critical in manufacturing. Deviations indicate:

HIGH TEMPERATURE ANOMALIES (above UCL):
- CNC Machining: Tool wear, incorrect coolant flow, spindle bearing failure
  → Action: Stop machine, inspect tooling, check coolant system
- Injection Moulding: Barrel overheating, blocked vent, screw wear
  → Action: Reduce barrel temperature setpoint, check cooling channels
- PCB Reflow: Oven profile deviation, thermocouple failure
  → Action: Verify thermal profile, run test board

LOW TEMPERATURE ANOMALIES (below LCL):
- Coolant system overcooling, heater failure, draft from open doors
  → Action: Check heater operation, seal environment

Typical Thresholds:
- CNC cutting zone: 20°C – 80°C (optimal 40°C – 65°C)
- Injection barrel: 180°C – 280°C (material-dependent)
- PCB reflow peak: 235°C – 260°C (lead-free solder)
- Ambient floor temperature: 18°C – 26°C

Calibration Requirements:
- Thermocouples: Calibrate every 6 months per ISO 10012
- IR sensors: Verify with blackbody reference quarterly
""",
        "tags": ["temperature", "anomaly", "cnc", "injection-moulding", "pcb"],
    },
    {
        "id": "pressure_vibration_anomalies",
        "title": "Pressure and Vibration Anomalies in Manufacturing",
        "content": """
PRESSURE ANOMALIES:
High Pressure (above UCL):
- Injection moulding: Mould blockage, degraded material, worn check ring
  → Action: Purge barrel, inspect mould, reduce injection speed
- Hydraulic system: Filter clogging, relief valve failure
  → Action: Replace filter, test relief valve

Low Pressure (below LCL):
- Pump failure, leak in hydraulic circuit, worn seals
  → Action: Check pump pressure, inspect hydraulic lines

VIBRATION ANOMALIES:
High Vibration (above UCL):
- CNC machine: Unbalanced toolholder, worn spindle bearings, resonance
  → Action: Balance tool assembly, replace bearings, adjust speeds
- Conveyor: Worn belts, misaligned rollers, loose bolts
  → Action: Realign components, re-tension belts

Vibration Analysis Methods:
- FFT (Fast Fourier Transform) for frequency spectrum analysis
- Time waveform analysis for impact identification
- Envelope detection for bearing fault frequencies
  - BPFO (Ball Pass Frequency Outer race) = (N/2)(1 - d/D cos α) × RPM/60
  - BPFI (Ball Pass Frequency Inner race) = (N/2)(1 + d/D cos α) × RPM/60

ISO 10816 Vibration Severity Classes:
- Class A: < 0.71 mm/s RMS — Good
- Class B: 0.71 – 1.8 mm/s RMS — Satisfactory
- Class C: 1.8 – 4.5 mm/s RMS — Unsatisfactory (plan maintenance)
- Class D: > 4.5 mm/s RMS — Unacceptable (immediate action)
""",
        "tags": ["pressure", "vibration", "hydraulics", "bearing", "maintenance"],
    },
    {
        "id": "defect_classification",
        "title": "Manufacturing Defect Classification and Root Cause",
        "content": """
DEFECT CATEGORIES (8D / Ishikawa Classification):

1. Dimensional Defects:
   - Out-of-tolerance dimensions (length, diameter, angle)
   - Root causes: Worn tooling, thermal expansion, machine calibration drift
   - Detection: CMM (Coordinate Measuring Machine), go/no-go gauges

2. Surface Defects:
   - Scratches, dents, porosity, roughness deviation
   - Root causes: Incorrect feed/speed, wrong coolant, contamination
   - Detection: Visual inspection, profilometers, dye penetrant

3. Material Defects:
   - Wrong hardness, tensile strength failure, composition errors
   - Root causes: Material mixing errors, heat treatment deviation
   - Detection: Hardness testers, tensile testing, spectrometry

4. Assembly Defects:
   - Missing components, wrong torque, incorrect orientation
   - Root causes: Poka-yoke failure, operator error, damaged fixtures
   - Detection: Vision systems, torque verification, assembly jigs

5. Cosmetic Defects:
   - Colour variation, burrs, flash, sink marks
   - Root causes: Mould wear, paint viscosity, post-processing errors

Defect Rate Calculation:
- ppm (parts per million) = (Defectives / Total) × 1,000,000
- DPMO = (Defects / (Units × Opportunities per unit)) × 1,000,000
- Six Sigma target: 3.4 DPMO

Acceptable Quality Levels (AQL per ISO 2859):
- AQL 0.065%: Critical components (safety, regulatory)
- AQL 0.65%: Major defects (function impaired)
- AQL 2.5%: Minor defects (appearance only)
""",
        "tags": ["defects", "quality", "inspection", "root-cause", "8d"],
    },
    {
        "id": "spc_reactions",
        "title": "SPC Reaction Plan and Corrective Actions",
        "content": """
REACTION PLAN when a control chart signal is detected:

RULE 1 (Point beyond 3σ):
1. Stop the process immediately
2. Identify the last known good product
3. Segregate all suspect product since last good check
4. Investigate root cause using 5-Why analysis
5. Implement containment action
6. Document in non-conformance report (NCR)
7. Complete 8D or CAPA report within 24 hours

RULE 2 (9 consecutive points same side):
1. Process mean has shifted — investigate process settings
2. Check: raw material lot change, operator change, shift change, tooling change
3. Adjust process toward nominal target
4. Increase sampling frequency temporarily

RULE 3 (6 consecutive trend):
1. Indicates progressive drift — tool wear, thermal drift, consumable depletion
2. Schedule preventive tooling change
3. Verify calibration of measurement equipment

STANDARD CORRECTIVE ACTION FORM (8D):
D1: Team assembled
D2: Problem defined (5W2H)
D3: Interim containment implemented
D4: Root cause verified
D5: Permanent corrective action chosen
D6: Action implemented and validated
D7: Recurrence prevention (systems update)
D8: Team recognition

Key Performance Indicators for QC:
- First Pass Yield (FPY) = Units passing first inspection / Total units
- Overall Equipment Effectiveness (OEE) = Availability × Performance × Quality
- Cost of Poor Quality (COPQ) = Internal failures + External failures + Appraisal + Prevention
""",
        "tags": ["spc", "corrective-action", "8d", "oee", "kpi"],
    },
]


def get_all_documents() -> list[dict]:
    return KNOWLEDGE_DOCS


def get_document_by_id(doc_id: str) -> dict | None:
    return next((d for d in KNOWLEDGE_DOCS if d["id"] == doc_id), None)
