
import json
import streamlit as st

from src.agents.orchestrator import run_workflow

st.set_page_config(
    page_title="NEXUS | AI Research Lab",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- FUTURISTIC THEME ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

.stApp {
    background:
      radial-gradient(ellipse at 5% 0%, #122448 0%, transparent 38%),
      radial-gradient(ellipse at 95% 15%, #281344 0%, transparent 32%),
      #070b14;
    color: #e8f0ff;
    font-family: 'Space Grotesk', sans-serif;
}
.block-container { padding-top: 2rem; max-width: 1500px; }
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0b1325,#101020);
    border-right: 1px solid #273452;
}
h1, h2, h3 { color: #e8f4ff !important; }
p, label, .stMarkdown { color: #b9c9e6; }

.hero {
    padding: 30px;
    border: 1px solid #29466b;
    border-radius: 22px;
    background: linear-gradient(120deg,#111f38dd,#211333dd);
    box-shadow: 0 0 35px #00d9ff12, inset 0 0 25px #8b5cf608;
    margin-bottom: 22px;
}
.eyebrow {
    font-family: 'JetBrains Mono', monospace;
    color: #5cecff;
    letter-spacing: 3px;
    font-size: 12px;
}
.hero-title {
    font-size: clamp(30px,4vw,49px);
    font-weight: 700;
    letter-spacing: -1.5px;
    margin: 8px 0;
    background: linear-gradient(90deg,#ffffff,#66eaff,#c5a3ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub { color: #9aafd0; font-size: 15px; }
.metric-card {
    border: 1px solid #253a5d;
    border-radius: 16px;
    padding: 20px;
    min-height: 120px;
    background: linear-gradient(145deg,#101b2e,#0b1020);
    transition: all .25s ease;
}
.metric-card:hover {
    transform: translateY(-5px);
    border-color: #51eaff;
    box-shadow: 0 0 24px #16d9ff25;
}
.metric-label {
    font-size: 12px; letter-spacing: 1.5px;
    color: #8da8cb; text-transform: uppercase;
}
.metric-value {
    font-size: 29px; font-weight: 700;
    color: #66edff; margin-top: 9px;
}
.section-tag {
    color: #8e9fbd;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px; letter-spacing: 2px;
    margin-bottom: 5px;
}
.node {
    padding: 14px;
    border-radius: 13px;
    border: 1px solid #2b4265;
    background: #0d1729;
    text-align: center;
    min-height: 90px;
    transition: all .2s ease;
}
.node:hover {
    border-color: #7e77ff;
    background: #17233b;
    box-shadow: 0 0 20px #7e77ff20;
    transform: scale(1.02);
}
.node-title { color: #e4efff; font-weight: 600; }
.node-sub { color: #7f9abb; font-size: 11px; margin-top: 5px; }
div.stButton > button {
    border: 1px solid #334d74;
    border-radius: 11px;
    background: linear-gradient(120deg,#152844,#211a3e);
    color: #eaf8ff;
    transition: all .2s ease;
    min-height: 43px;
}
div.stButton > button:hover {
    border-color: #55eaff;
    color: #ffffff;
    box-shadow: 0 0 18px #00d9ff30;
    transform: translateY(-2px);
}
div.stButton > button[kind="primary"] {
    background: linear-gradient(100deg,#087fbb,#6550c9);
    border: 1px solid #6beaff;
}
.stTextArea textarea, .stTextInput input {
    background: #0b1425 !important;
    color: #eaf4ff !important;
    border: 1px solid #30476a !important;
    border-radius: 10px !important;
}
div[data-testid="stExpander"] {
    border: 1px solid #243a5b;
    border-radius: 12px;
    background: #0c1423;
}
hr { border-color: #243550; }
.footer {
    color: #607797;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    text-align: center;
    padding: 20px;
}
</style>
""", unsafe_allow_html=True)

# ---------- SESSION STATE ----------
if "workflow_result" not in st.session_state:
    st.session_state.workflow_result = None
if "selected_panel" not in st.session_state:
    st.session_state.selected_panel = "Overview"
if "run_count" not in st.session_state:
    st.session_state.run_count = 0

# ---------- HEADER ----------
st.markdown("""
<div class="hero">
  <div class="eyebrow">NEXUS / AUTONOMOUS RESEARCH SYSTEM</div>
  <div class="hero-title">Scientific Discovery Command Center</div>
  <div class="hero-sub">
    Monitor agent outputs · Explore research evidence · Inspect experiments
  </div>
</div>
""", unsafe_allow_html=True)

# ---------- SIDEBAR ----------
with st.sidebar:
    st.markdown("## ◈ NEXUS LAB")
    st.caption("RESEARCH OPERATIONS / V1.0")
    st.divider()

    st.markdown("### Initialize experiment")
    research_query = st.text_area(
        "Research objective",
        placeholder="e.g. Machine learning for disease prediction",
        height=100,
    )
    paper_text = st.text_area(
        "Paper text / notes",
        placeholder="Paste research notes here (optional)",
        height=110,
    )
    python_code = st.text_area(
        "Python experiment (optional)",
        placeholder="print('Experiment started')",
        height=130,
    )

    run_button = st.button(
        "▶  EXECUTE WORKFLOW",
        type="primary",
        use_container_width=True,
    )

    st.divider()
    st.markdown("#### SYSTEM INFORMATION")
    st.caption("Pipeline: existing orchestrator")
    st.caption("Execution: local Python environment")
    st.caption("Cost telemetry: not instrumented")

# ---------- RUN PIPELINE ----------
if run_button:
    if not research_query.strip() and not paper_text.strip() and not python_code.strip():
        st.warning("Enter a research objective, paper text, or Python code first.")
    else:
        try:
            with st.spinner("◈ Agents are processing your research..."):
                result = run_workflow(
                    papers=[paper_text] if paper_text.strip() else [],
                    research_query=research_query.strip() or None,
                    python_code=python_code.strip() or None,
                )
            st.session_state.workflow_result = result
            st.session_state.run_count += 1
            st.session_state.selected_panel = "Overview"
            st.success("Workflow returned successfully. Explore the panels below.")
        except Exception as exc:
            st.error(f"Workflow error: {type(exc).__name__}: {exc}")

result = st.session_state.workflow_result

# ---------- METRICS ----------
if result is None:
    st.markdown('<div class="section-tag">01 / SYSTEM OVERVIEW</div>', unsafe_allow_html=True)
    st.info("System ready. Add a research objective in the sidebar and execute the workflow.")
    metric_data = [
        ("SYSTEM", "READY"),
        ("RUNS THIS SESSION", str(st.session_state.run_count)),
        ("RESEARCH OUTPUT", "WAITING"),
        ("EXECUTION COST", "N/A"),
    ]
else:
    retrieved = result.get("retrieved_papers") or []
    hypotheses = result.get("hypotheses")
    metric_data = [
        ("WORKFLOW", "RETURNED"),
        ("RUNS THIS SESSION", str(st.session_state.run_count)),
        ("RETRIEVED PAPERS", str(len(retrieved)) if isinstance(retrieved, list) else "Available"),
        ("EXECUTION COST", "N/A"),
    ]

cols = st.columns(4)
for col, (label, value) in zip(cols, metric_data):
    col.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div></div>',
        unsafe_allow_html=True,
    )

st.write("")
st.markdown('<div class="section-tag">02 / INTERACTIVE CONTROL DECK</div>', unsafe_allow_html=True)

# Clickable navigation cards
nav_items = [
    ("Overview", "◈", "System snapshot"),
    ("Literature", "⌕", "Papers & evidence"),
    ("Hypotheses", "✳", "Generated ideas"),
    ("Code Lab", "⌘", "Validation & execution"),
    ("Critic", "◎", "Statistical review"),
    ("Memory", "▤", "Research context"),
]
nav_cols = st.columns(3)
for i, (name, symbol, subtitle) in enumerate(nav_items):
    with nav_cols[i % 3]:
        if st.button(
            f"{symbol}  {name}\n{subtitle}",
            key=f"nav_{name}",
            use_container_width=True,
        ):
            st.session_state.selected_panel = name

st.write("")
selected = st.session_state.selected_panel
st.markdown(f'<div class="section-tag">03 / ACTIVE PANEL — {selected.upper()}</div>', unsafe_allow_html=True)

if result is None:
    st.markdown("""
    <div class="hero">
      <div class="eyebrow">AWAITING INPUT</div>
      <h3>Research console is ready</h3>
      <p>Run a workflow to populate the interactive panels with real agent outputs.</p>
    </div>
    """, unsafe_allow_html=True)

else:
    panels = {
        "Overview": [
            ("Literature Retrieval", "retrieved_papers"),
            ("Paper Review", "reviewed_papers"),
            ("Hypothesis Generation", "hypotheses"),
            ("Code Validation", "code_validation"),
            ("Execution Result", "execution_result"),
            ("Statistical Critic", "critic_report"),
            ("Research Context", "research_context"),
            ("Saved Memory ID", "saved_memory_id"),
        ],
        "Literature": [
            ("Retrieved Papers and Citations", "retrieved_papers"),
            ("Reviewed Papers", "reviewed_papers"),
        ],
        "Hypotheses": [
            ("Generated Hypotheses", "hypotheses"),
        ],
        "Code Lab": [
            ("Code Validation", "code_validation"),
            ("Execution Result", "execution_result"),
        ],
        "Critic": [
            ("Statistical Critic Report", "critic_report"),
        ],
        "Memory": [
            ("Research Context", "research_context"),
            ("Retrieved Memories", "found_memories"),
            ("Saved Memory ID", "saved_memory_id"),
        ],
    }

    active_panels = panels.get(selected, panels["Overview"])

    if selected == "Overview":
        st.markdown("#### ◈ Agent workflow trace")
        stages = [
            ("01", "Retrieve", "retrieved_papers"),
            ("02", "Review", "reviewed_papers"),
            ("03", "Hypotheses", "hypotheses"),
            ("04", "Code", "code_validation"),
            ("05", "Critic", "critic_report"),
        ]
        stage_cols = st.columns(5)
        for col, (number, label, key) in zip(stage_cols, stages):
            value = result.get(key)
            status = "OUTPUT RECEIVED" if value is not None else "NO OUTPUT"
            col.markdown(
                f'<div class="node"><div class="eyebrow">{number}</div>'
                f'<div class="node-title">{label}</div>'
                f'<div class="node-sub">{status}</div></div>',
                unsafe_allow_html=True,
            )
        st.caption(
            "These indicators show returned outputs, not a guarantee that every "
            "agent ran. Optional steps may be skipped."
        )

    for title, key in active_panels:
        value = result.get(key)
        with st.expander(title, expanded=(selected != "Overview")):
            if value is None:
                st.caption("No output returned for this step.")
            else:
                if isinstance(value, (dict, list, tuple)):
                    st.json(value)
                else:
                    st.write(value)

    st.divider()
    st.markdown("#### ◈ Execution telemetry")
    c1, c2 = st.columns(2)
    c1.metric("Workflow returned", "Yes")
    c2.metric("Actual model/API cost", "Not available")
    st.caption(
        "The current orchestrator does not return token usage, per-agent "
        "timings, or billing data. These values are intentionally not fabricated."
    )

    st.download_button(
        "⬇ Export complete workflow JSON",
        data=json.dumps(result, indent=2, default=str),
        file_name="nexus_research_results.json",
        mime="application/json",
    )

st.markdown("""
<div class="footer">
NEXUS RESEARCH LAB · HUMAN-SUPERVISED AI · RESULTS ARE BASED ON RETURNED PIPELINE OUTPUTS
</div>
""", unsafe_allow_html=True)
