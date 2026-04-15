import streamlit as st
import json
import os
import datetime
from pathlib import Path

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="HadithSciQA – Scholar Validation",
    page_icon="📜",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Global RTL support for Arabic text */
.arabic-text {
    direction: rtl;
    text-align: right;
    font-family: 'Amiri', 'Traditional Arabic', 'Scheherazade New', 'Noto Naskh Arabic', serif;
    font-size: 1.2rem;
    line-height: 2;
}
.arabic-text-lg {
    direction: rtl;
    text-align: right;
    font-family: 'Amiri', 'Traditional Arabic', 'Scheherazade New', 'Noto Naskh Arabic', serif;
    font-size: 1.35rem;
    line-height: 2.2;
    font-weight: 600;
}
.option-box {
    direction: rtl;
    text-align: right;
    font-family: 'Amiri', 'Traditional Arabic', 'Scheherazade New', 'Noto Naskh Arabic', serif;
    font-size: 1.1rem;
    line-height: 1.9;
    padding: 10px 16px;
    border-radius: 8px;
    margin-bottom: 6px;
    border: 1px solid #ddd;
}
.option-correct {
    background-color: #d4edda;
    border-color: #28a745;
}
.option-wrong {
    background-color: #f8f9fa;
    border-color: #dee2e6;
}
.source-badge {
    display: inline-block;
    background-color: #e9ecef;
    color: #495057;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    margin-top: 4px;
}
.difficulty-easy { color: #28a745; font-weight: 700; }
.difficulty-medium { color: #fd7e14; font-weight: 700; }
.difficulty-hard { color: #dc3545; font-weight: 700; }
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
    border-radius: 12px;
    text-align: center;
}
.metric-card h2 { margin: 0; font-size: 2rem; }
.metric-card p { margin: 0; font-size: 0.9rem; opacity: 0.9; }
.scoring-item {
    direction: rtl;
    text-align: right;
    font-family: 'Amiri', 'Traditional Arabic', 'Scheherazade New', 'Noto Naskh Arabic', serif;
    font-size: 1.05rem;
    line-height: 1.8;
    padding: 6px 12px;
    margin-bottom: 4px;
    background: #f0f4ff;
    border-radius: 6px;
    border-right: 4px solid #667eea;
}
.phrase-highlight {
    direction: rtl;
    text-align: center;
    font-family: 'Amiri', 'Traditional Arabic', 'Scheherazade New', 'Noto Naskh Arabic', serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #764ba2;
    padding: 12px;
    background: #f5f0ff;
    border-radius: 10px;
    margin: 8px 0;
}
.grade-badge {
    display: inline-block;
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 4px 16px;
    border-radius: 20px;
    font-size: 1rem;
    font-weight: 700;
}
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
    padding: 10px 20px;
    border-radius: 8px 8px 0 0;
}
div[data-testid="stSidebarContent"] { padding-top: 1rem; }
</style>
<link href="https://fonts.googleapis.com/css2?family=Amiri:wght@400;700&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)


# ─── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_benchmark():
    """Load benchmark from the bundled data file."""
    data_path = Path(__file__).parent / "data" / "full_benchmark.json"
    if not data_path.exists():
        st.error(f"Benchmark file not found at {data_path}")
        st.stop()
    with open(data_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_validation_path():
    return Path(__file__).parent / "data" / "validation_results.json"


def load_validations():
    path = get_validation_path()
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_validations(validations):
    path = get_validation_path()
    with open(path, "w", encoding="utf-8") as f:
        json.dump(validations, f, ensure_ascii=False, indent=2)


data = load_benchmark()

# Split by task
task1 = [q for q in data if q["task"] == "terminology_mcq"]
task2 = [q for q in data if q["task"] == "narrator_grading"]
task3 = [q for q in data if q["task"] == "isnad_reasoning"]

# Init session state
if "validations" not in st.session_state:
    st.session_state.validations = load_validations()


# ─── Helper Functions ──────────────────────────────────────────────────────────
TASK_LABELS = {
    "terminology_mcq": "📖 Task 1: Terminology MCQ",
    "narrator_grading": "⚖️ Task 2: Narrator Grading",
    "isnad_reasoning": "🔗 Task 3: Isnad Reasoning",
}

DIFFICULTY_MAP = {
    "easy": ("🟢 Easy", "difficulty-easy"),
    "medium": ("🟡 Medium", "difficulty-medium"),
    "hard": ("🔴 Hard", "difficulty-hard"),
}


def render_difficulty(difficulty):
    label, css_class = DIFFICULTY_MAP.get(difficulty, ("Unknown", ""))
    return f'<span class="{css_class}">{label}</span>'


def render_question_header(item):
    """Render the common header for any question."""
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.markdown(f"**ID:** `{item['id']}`")
    with col2:
        st.markdown(f"**Difficulty:** {render_difficulty(item['difficulty'])}", unsafe_allow_html=True)
    with col3:
        st.markdown(f'<span class="source-badge">📚 {item["source"]}</span>', unsafe_allow_html=True)


def render_mcq_question(item):
    """Render a terminology MCQ or narrator grading question."""
    render_question_header(item)

    # Special: narrator grading shows the phrase
    if item["task"] == "narrator_grading":
        st.markdown(f'<div class="phrase-highlight">« {item["ibn_hajar_phrase"]} »</div>', unsafe_allow_html=True)
        st.markdown(
            f'<div style="text-align:center;margin-bottom:8px;"><span class="grade-badge">Grade #{item["grade_number"]}</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown(f'<div class="arabic-text-lg">{item["question_ar"]}</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Options
    correct = item["correct"]
    for key in ["A", "B", "C", "D"]:
        if key in item.get("options", {}):
            css = "option-correct" if key == correct else "option-wrong"
            icon = "✅" if key == correct else "⬜"
            st.markdown(
                f'<div class="option-box {css}">{icon} <strong>({key})</strong> {item["options"][key]}</div>',
                unsafe_allow_html=True,
            )

    # Explanation
    if st.toggle("📝 Show Explanation / الشرح", value=False, key=f"expl_{item['id']}"):
        st.markdown(f'<div class="arabic-text">{item["explanation_ar"]}</div>', unsafe_allow_html=True)


def render_isnad_question(item):
    """Render an isnad reasoning (open-ended) question."""
    render_question_header(item)

    st.markdown(f'<div class="arabic-text-lg">{item["question_ar"]}</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Reference answer
    st.markdown("#### 📝 Reference Answer / الإجابة المرجعية")
    st.markdown(f'<div class="arabic-text">{item["reference_answer_ar"]}</div>', unsafe_allow_html=True)

    # Scoring criteria
    st.markdown("#### 📋 Scoring Criteria / معايير التقييم")
    for i, criterion in enumerate(item["scoring_criteria"], 1):
        st.markdown(f'<div class="scoring-item">✦ {criterion}</div>', unsafe_allow_html=True)


def render_validation_form(item):
    """Render the scholar validation form for a question."""
    qid = item["id"]
    existing = st.session_state.validations.get(qid, {})

    st.markdown("#### 🔍 Scholar Validation")
    col_a, col_b = st.columns(2)

    with col_a:
        verdict = st.radio(
            "Is this question and its answer **correct**?",
            options=["✅ Correct", "⚠️ Needs Revision", "❌ Incorrect"],
            index=["✅ Correct", "⚠️ Needs Revision", "❌ Incorrect"].index(existing.get("verdict", "✅ Correct")),
            key=f"verdict_{qid}",
            horizontal=True,
        )

    with col_b:
        quality = st.select_slider(
            "Question Quality (1 = Poor, 5 = Excellent)",
            options=[1, 2, 3, 4, 5],
            value=existing.get("quality", 5),
            key=f"quality_{qid}",
        )

    comments = st.text_area(
        "Comments / ملاحظات (optional)",
        value=existing.get("comments", ""),
        key=f"comments_{qid}",
        height=80,
        placeholder="Any corrections, suggestions, or notes for the research team…",
    )

    if st.button("💾 Save Validation", key=f"save_{qid}", type="primary"):
        st.session_state.validations[qid] = {
            "verdict": verdict,
            "quality": quality,
            "comments": comments,
            "timestamp": datetime.datetime.now().isoformat(),
        }
        save_validations(st.session_state.validations)
        st.success(f"Validation for **{qid}** saved!")


# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://img.icons8.com/color/96/quill-pen.png", width=60)
    st.title("HadithSciQA")
    st.caption("Benchmark Scholar Validation Tool")
    st.markdown("---")

    # Progress
    total = len(data)
    validated = len(st.session_state.validations)
    pct = validated / total if total else 0
    st.metric("Validated", f"{validated} / {total}")
    st.progress(pct)

    # Per-task progress
    for task_key, task_items in [("terminology_mcq", task1), ("narrator_grading", task2), ("isnad_reasoning", task3)]:
        task_validated = sum(1 for q in task_items if q["id"] in st.session_state.validations)
        task_label = TASK_LABELS[task_key].split(": ")[1]
        st.caption(f"{task_label}: {task_validated}/{len(task_items)}")

    st.markdown("---")

    # Filter controls
    st.subheader("🔧 Filters")
    filter_task = st.selectbox(
        "Task Type",
        ["All Tasks"] + list(TASK_LABELS.values()),
        index=0,
    )
    filter_difficulty = st.multiselect(
        "Difficulty",
        ["easy", "medium", "hard"],
        default=["easy", "medium", "hard"],
    )
    filter_status = st.radio(
        "Validation Status",
        ["All", "Not Validated", "Validated"],
        index=0,
        horizontal=True,
    )

    st.markdown("---")

    # Export
    st.subheader("📥 Export")
    if st.session_state.validations:
        export_data = {
            "metadata": {
                "tool": "HadithSciQA Scholar Validation",
                "exported_at": datetime.datetime.now().isoformat(),
                "total_items": total,
                "validated_items": validated,
            },
            "validations": st.session_state.validations,
        }
        st.download_button(
            "⬇️ Download Validation Report",
            data=json.dumps(export_data, ensure_ascii=False, indent=2),
            file_name=f"hadithsciqa_validation_{datetime.date.today()}.json",
            mime="application/json",
        )
    else:
        st.info("Validate items to enable export.")


# ─── Filter Logic ──────────────────────────────────────────────────────────────
def apply_filters(items):
    filtered = items
    # Task filter
    if filter_task != "All Tasks":
        task_key = [k for k, v in TASK_LABELS.items() if v == filter_task][0]
        filtered = [q for q in filtered if q["task"] == task_key]
    # Difficulty filter
    filtered = [q for q in filtered if q["difficulty"] in filter_difficulty]
    # Status filter
    if filter_status == "Not Validated":
        filtered = [q for q in filtered if q["id"] not in st.session_state.validations]
    elif filter_status == "Validated":
        filtered = [q for q in filtered if q["id"] in st.session_state.validations]
    return filtered


# ─── Main Content ──────────────────────────────────────────────────────────────
st.markdown("# 📜 HadithSciQA — Scholar Validation Portal")
st.markdown(
    "Welcome, respected scholar. This tool presents all **150 benchmark questions** from the "
    "*HadithSciQA* dataset for your expert review and validation. Please review each question, "
    "its answer, and provide your scholarly verdict."
)

# Summary metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.markdown(
        '<div class="metric-card"><h2>150</h2><p>Total Questions</p></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown(
        f'<div class="metric-card"><h2>{len(task1)}</h2><p>Terminology MCQ</p></div>',
        unsafe_allow_html=True,
    )
with col3:
    st.markdown(
        f'<div class="metric-card"><h2>{len(task2)}</h2><p>Narrator Grading</p></div>',
        unsafe_allow_html=True,
    )
with col4:
    st.markdown(
        f'<div class="metric-card"><h2>{len(task3)}</h2><p>Isnad Reasoning</p></div>',
        unsafe_allow_html=True,
    )

st.markdown("")

# ─── Tabbed View ───────────────────────────────────────────────────────────────
tab_overview, tab_task1, tab_task2, tab_task3, tab_report = st.tabs(
    ["📊 Overview", "📖 Task 1: Terminology", "⚖️ Task 2: Narrator Grading", "🔗 Task 3: Isnad Reasoning", "📄 Validation Report"]
)

# ── Overview Tab ───────────────────────────────────────────────────────────────
with tab_overview:
    st.markdown("## Benchmark Overview")
    st.markdown(
        "The **HadithSciQA** benchmark evaluates LLMs on three core competencies in the science of Hadith "
        "(*ʿIlm Muṣṭalaḥ al-Ḥadīth*):"
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("### 📖 Task 1: Terminology MCQ")
        st.markdown(
            "**60 questions** testing knowledge of Hadith terminology definitions — "
            "including types of Hadith, conditions of acceptance, narrator evaluation terms, and more."
        )
        difficulties_t1 = {d: sum(1 for q in task1 if q["difficulty"] == d) for d in ["easy", "medium", "hard"]}
        st.markdown(f"- 🟢 Easy: **{difficulties_t1['easy']}**")
        st.markdown(f"- 🟡 Medium: **{difficulties_t1['medium']}**")
        st.markdown(f"- 🔴 Hard: **{difficulties_t1['hard']}**")

    with col_b:
        st.markdown("### ⚖️ Task 2: Narrator Grading")
        st.markdown(
            "**50 questions** testing understanding of Ibn Ḥajar's narrator evaluation phrases "
            "(*alfāẓ al-jarḥ wa-l-taʿdīl*) and their corresponding ranks."
        )
        difficulties_t2 = {d: sum(1 for q in task2 if q["difficulty"] == d) for d in ["easy", "medium", "hard"]}
        st.markdown(f"- 🟢 Easy: **{difficulties_t2['easy']}**")
        st.markdown(f"- 🟡 Medium: **{difficulties_t2['medium']}**")
        st.markdown(f"- 🔴 Hard: **{difficulties_t2['hard']}**")

    with col_c:
        st.markdown("### 🔗 Task 3: Isnad Reasoning")
        st.markdown(
            "**40 open-ended questions** requiring analytical reasoning about chains of narration — "
            "defects, disconnections, rulings on chains, and complex scenarios."
        )
        difficulties_t3 = {d: sum(1 for q in task3 if q["difficulty"] == d) for d in ["easy", "medium", "hard"]}
        st.markdown(f"- 🟢 Easy: **{difficulties_t3['easy']}**")
        st.markdown(f"- 🟡 Medium: **{difficulties_t3['medium']}**")
        st.markdown(f"- 🔴 Hard: **{difficulties_t3['hard']}**")

    st.markdown("---")
    st.markdown("### 📚 Sources Referenced")
    sources = sorted(set(q["source"] for q in data))
    for src in sources:
        count = sum(1 for q in data if q["source"] == src)
        st.markdown(f"- **{src}** — {count} question(s)")

# ── Task Tabs ──────────────────────────────────────────────────────────────────
def render_task_tab(task_items, task_key):
    """Render a full task tab with filtering and pagination."""
    filtered = apply_filters(task_items)
    st.markdown(f"**Showing {len(filtered)} of {len(task_items)} questions**")

    if not filtered:
        st.info("No questions match the current filters. Adjust filters in the sidebar.")
        return

    # Pagination
    items_per_page = 5
    total_pages = max(1, (len(filtered) + items_per_page - 1) // items_per_page)
    page = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1,
        key=f"page_{task_key}",
    )
    start = (page - 1) * items_per_page
    end = start + items_per_page
    page_items = filtered[start:end]

    st.caption(f"Page {page} of {total_pages}")

    for item in page_items:
        qid = item["id"]
        is_validated = qid in st.session_state.validations
        status_icon = "✅" if is_validated else "⬜"

        with st.expander(f"{status_icon} **{qid}** — {item['question_ar'][:80]}…", expanded=False):
            if task_key == "isnad_reasoning":
                render_isnad_question(item)
            else:
                render_mcq_question(item)

            st.markdown("---")
            render_validation_form(item)


with tab_task1:
    st.markdown("## 📖 Task 1: Terminology MCQ")
    st.markdown("Multiple-choice questions on Hadith science terminology.")
    render_task_tab(task1, "terminology_mcq")

with tab_task2:
    st.markdown("## ⚖️ Task 2: Narrator Grading")
    st.markdown("Questions on Ibn Ḥajar's narrator evaluation phrases and their ranks in *al-Jarḥ wa-l-Taʿdīl*.")
    render_task_tab(task2, "narrator_grading")

with tab_task3:
    st.markdown("## 🔗 Task 3: Isnad Reasoning")
    st.markdown("Open-ended analytical questions on chain of narration analysis.")
    render_task_tab(task3, "isnad_reasoning")

# ── Validation Report Tab ─────────────────────────────────────────────────────
with tab_report:
    st.markdown("## 📄 Validation Report")

    if not st.session_state.validations:
        st.info("No validations recorded yet. Please review questions in the task tabs and submit your verdicts.")
    else:
        vals = st.session_state.validations

        # Summary stats
        verdicts = [v["verdict"] for v in vals.values()]
        c_correct = verdicts.count("✅ Correct")
        c_revision = verdicts.count("⚠️ Needs Revision")
        c_incorrect = verdicts.count("❌ Incorrect")
        avg_quality = sum(v["quality"] for v in vals.values()) / len(vals)

        r_col1, r_col2, r_col3, r_col4, r_col5 = st.columns(5)
        r_col1.metric("Validated", len(vals))
        r_col2.metric("Correct", c_correct)
        r_col3.metric("Needs Revision", c_revision)
        r_col4.metric("Incorrect", c_incorrect)
        r_col5.metric("Avg Quality", f"{avg_quality:.1f}/5")

        st.markdown("---")

        # Detailed table
        st.markdown("### Detailed Results")
        report_rows = []
        for qid, v in sorted(vals.items()):
            report_rows.append({
                "ID": qid,
                "Verdict": v["verdict"],
                "Quality": v["quality"],
                "Comments": v.get("comments", ""),
                "Timestamp": v.get("timestamp", ""),
            })

        st.dataframe(report_rows, use_container_width=True, hide_index=True)

        # Items needing attention
        attention = {qid: v for qid, v in vals.items() if v["verdict"] != "✅ Correct"}
        if attention:
            st.markdown("### ⚠️ Items Needing Attention")
            for qid, v in sorted(attention.items()):
                st.markdown(f"- **{qid}**: {v['verdict']} — {v.get('comments', 'No comment')}")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#888;font-size:0.85rem;">'
    "HadithSciQA Benchmark Validation Tool · Built for ICML 2026 Submission · "
    "All data is stored locally"
    "</div>",
    unsafe_allow_html=True,
)
