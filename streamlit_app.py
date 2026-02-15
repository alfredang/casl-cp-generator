import re
import tempfile
from pathlib import Path

import streamlit as st

from app.ai_generator import (
    ABOUT_COURSE_PROMPT_TEMPLATE,
    ASSESSMENT_METHOD_PROMPT_TEMPLATE,
    ASSESSMENT_METHODS_LIST,
    BACKGROUND_PART_A_PROMPT_TEMPLATE,
    BACKGROUND_PART_B_PROMPT_TEMPLATE,
    COURSE_TITLE_SUGGESTIONS_PROMPT_TEMPLATE,
    COURSE_TOPICS_PROMPT_TEMPLATE,
    COURSE_VALIDATION_PROMPT_TEMPLATE,
    INSTRUCTION_METHOD_PROMPT_TEMPLATE,
    LEARNING_OUTCOME_PROMPT_TEMPLATE,
    LESSON_PLAN_PROMPT_TEMPLATE,
    INSTRUCTION_METHODS_LIST,
    LU_SEQUENCING_TYPES,
    LU_SEQUENCING_TEMPLATES,
    UNIQUE_SKILL_NAMES_LIST,
    SKILL_DESCRIPTIONS,
    JOB_ROLES_PROMPT_TEMPLATE,
    MINIMUM_ENTRY_REQUIREMENT_PROMPT_TEMPLATE,
    WHAT_YOULL_LEARN_PROMPT_TEMPLATE,
    generate_about_course,
    generate_assessment_method,
    generate_background_part_a,
    generate_background_part_b,
    generate_course_title_suggestions,
    generate_course_topics,
    generate_course_validation,
    generate_instruction_method,
    generate_learning_outcomes,
    generate_lesson_plan_content,
    generate_lu_sequencing_rationale,
    generate_job_roles,
    generate_minimum_entry_requirement,
    generate_what_youll_learn,
)
from app.extractor import extract_data
from app.generator_docx import generate_audit_report
from app.generator_lesson_plan import generate_lesson_plan_table
from app.generator_lesson_plan_pdf import generate_lesson_plan_pdf_table

st.set_page_config(page_title="CASL Course Document Generator", page_icon="📄", layout="wide")

# --- Sidebar Navigation ---
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Course Details"

with st.sidebar:
    st.title("WSQ/CASL CP Generator")
    cp_mode = st.radio("Mode", ["CASL", "WSQ"], horizontal=True, key="cp_mode", label_visibility="collapsed")

    st.markdown("---")
    st.caption("PREPARE CP")
    if st.button("Course Details", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Course Details" else "secondary"):
        st.session_state["active_page"] = "Course Details"
        st.rerun()
    if st.button("About This Course", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "About This Course" else "secondary"):
        st.session_state["active_page"] = "About This Course"
        st.rerun()
    if st.button("What You'll Learn", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "What You'll Learn" else "secondary"):
        st.session_state["active_page"] = "What You'll Learn"
        st.rerun()
    if st.button("Background Part A", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Background Part A" else "secondary"):
        st.session_state["active_page"] = "Background Part A"
        st.rerun()
    if st.button("Background Part B", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Background Part B" else "secondary"):
        st.session_state["active_page"] = "Background Part B"
        st.rerun()
    if st.button("Learning Outcomes", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Learning Outcomes" else "secondary"):
        st.session_state["active_page"] = "Learning Outcomes"
        st.rerun()
    if st.button("Instructional Methods", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Instructional Methods" else "secondary"):
        st.session_state["active_page"] = "Instructional Methods"
        st.rerun()
    if st.button("Assessment Methods", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Assessment Methods" else "secondary"):
        st.session_state["active_page"] = "Assessment Methods"
        st.rerun()
    if st.button("LU Sequencing Rationale", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "LU Sequencing Rationale" else "secondary"):
        st.session_state["active_page"] = "LU Sequencing Rationale"
        st.rerun()
    if st.button("Course Validation", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Course Validation" else "secondary"):
        st.session_state["active_page"] = "Course Validation"
        st.rerun()

    st.markdown("---")
    st.caption("SUBMIT CP")
    if st.button("Course Outline", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Course Outline" else "secondary"):
        st.session_state["active_page"] = "Course Outline"
        st.rerun()
    if st.button("Min Entry Requirements", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Min Entry Requirements" else "secondary"):
        st.session_state["active_page"] = "Min Entry Requirements"
        st.rerun()
    if st.button("Job Roles", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Job Roles" else "secondary"):
        st.session_state["active_page"] = "Job Roles"
        st.rerun()
    if st.button("Lesson Plan", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Lesson Plan" else "secondary"):
        st.session_state["active_page"] = "Lesson Plan"
        st.rerun()
    if st.button("CP Quality Audit", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "CP Quality Audit" else "secondary"):
        st.session_state["active_page"] = "CP Quality Audit"
        st.rerun()

    st.markdown("---")
    st.caption("Powered by Tertiary Infotech Academy Pte Ltd")

active_page = st.session_state["active_page"]

# --- Helper: saved course details from session state ---
saved_title = st.session_state.get("saved_course_title", "")
saved_topics = st.session_state.get("saved_course_topics", "")
has_course_details = bool(saved_title and saved_topics)

# ============================================================
# PAGE: Course Details
# ============================================================
if active_page == "Course Details":
    st.header("Course Details")
    st.markdown("Enter the course title and topics. This information will be used across all Prepare CP pages.")

    # --- Course Title (outside form) ---
    if "cd_course_title" not in st.session_state:
        st.session_state["cd_course_title"] = st.session_state.get("saved_course_title", "")
    course_title = st.text_input(
        "Course Title",
        placeholder="e.g. Sales and Marketing Mastery",
        key="cd_course_title",
    )

    # --- Suggest Course Titles with AI ---
    with st.expander("Suggest Course Titles with AI", expanded=False):
        st.markdown("Enter a course topic to brainstorm 20 appealing, SEO-friendly course titles.")

        ct_prompt_template = st.session_state.get("ct_prompt", COURSE_TITLE_SUGGESTIONS_PROMPT_TEMPLATE)
        if st.checkbox("Show Prompt Template", key="ct_show_prompt"):
            ct_prompt = st.text_area(
                "Edit the prompt template used for generation. "
                "Use `{course}` as a placeholder for the course topic.",
                value=ct_prompt_template,
                height=300,
                key="ct_prompt_input",
            )
            st.session_state["ct_prompt"] = ct_prompt

        if st.button("Suggest Titles", type="primary", use_container_width=True, key="ct_suggest_btn"):
            if not course_title:
                st.warning("Please enter a course topic in the Course Title field first.")
            else:
                with st.spinner("Generating course title suggestions..."):
                    try:
                        result = generate_course_title_suggestions(
                            course_title,
                            prompt_template=st.session_state.get("ct_prompt"),
                        )
                        st.session_state["ct_suggestions"] = result
                    except Exception as e:
                        st.error(f"Failed to generate title suggestions: {e}")

        if st.session_state.get("ct_suggestions"):
            st.divider()
            st.markdown("**Suggested Course Titles:**")
            st.code(st.session_state["ct_suggestions"], language=None, wrap_lines=True)

    # --- CASL-specific fields ---
    if st.session_state.get("cp_mode") == "CASL":
        unique_skill_name = st.selectbox(
            "Unique Skill Name",
            options=UNIQUE_SKILL_NAMES_LIST,
            index=UNIQUE_SKILL_NAMES_LIST.index(st.session_state["saved_unique_skill_name"])
            if st.session_state.get("saved_unique_skill_name") in UNIQUE_SKILL_NAMES_LIST
            else 0,
            key="cd_unique_skill_name",
        )

    # --- WSQ-specific fields ---
    if st.session_state.get("cp_mode") == "WSQ":
        col_tsc_code, col_tsc_title = st.columns(2)
        with col_tsc_code:
            tsc_ref_code = st.text_input(
                "TSC Reference Code",
                value=st.session_state.get("saved_tsc_ref_code", ""),
                placeholder="e.g. TSC-2024-001",
                key="cd_tsc_ref_code",
            )
        with col_tsc_title:
            tsc_title = st.text_input(
                "TSC Title",
                value=st.session_state.get("saved_tsc_title", ""),
                placeholder="e.g. Digital Marketing Strategy",
                key="cd_tsc_title",
            )

    # --- Generate Topics with AI ---
    if "cd_course_topics" not in st.session_state:
        st.session_state["cd_course_topics"] = st.session_state.get("saved_course_topics", "")

    with st.expander("Generate Topics with AI", expanded=False):
        st.markdown("Auto-generate course topics based on the course title. You can edit the results afterwards.")
        # Show skill description context for CASL mode
        if st.session_state.get("cp_mode") == "CASL":
            selected_skill = st.session_state.get("cd_unique_skill_name", "")
            skill_desc_preview = SKILL_DESCRIPTIONS.get(selected_skill, "")
            if skill_desc_preview:
                st.info(f"**Skill:** {selected_skill}\n\n**Description:** {skill_desc_preview[:300]}{'...' if len(skill_desc_preview) > 300 else ''}")
            else:
                st.warning(f"No skill description found for **{selected_skill}**. Topics will be generated based on the course title only.")
        saved_dur = st.session_state.get("saved_course_duration", 16)
        default_days = max(1.0, float(saved_dur // 8))
        num_days_est = st.number_input(
            "No. of Days",
            min_value=0.5,
            value=default_days,
            step=0.5,
            format="%.1f",
            key="gen_num_days",
            help="Typically 2-3 topics per day",
        )
        special_req = st.text_area(
            "Special Requirements (optional)",
            value="",
            height=80,
            key="gen_special_req",
            placeholder="e.g. Must include a topic on safety regulations, focus on hands-on practical skills, etc.",
        )
        max_topics = num_days_est * 3
        st.caption(f"AI will generate **2-3 topics per day** for **{num_days_est} day(s)** (max {max_topics} topics)")
        if st.button("Generate Topics", type="primary", use_container_width=True, key="gen_topics_btn"):
            if not course_title:
                st.warning("Please enter a course title first.")
            else:
                with st.spinner("Generating course topics..."):
                    try:
                        # In CASL mode, look up the skill description for context
                        skill_desc = ""
                        if st.session_state.get("cp_mode") == "CASL":
                            selected_skill = st.session_state.get("cd_unique_skill_name", "")
                            skill_desc = SKILL_DESCRIPTIONS.get(selected_skill, "")
                        result = generate_course_topics(
                            course_title, num_days_est,
                            skill_description=skill_desc,
                            special_requirements=special_req,
                        )
                        st.session_state["cd_course_topics"] = result
                        # Auto-detect actual topic count from generated result
                        generated_count = len(re.findall(r"^##\s*Topic\s*\d+", result, re.MULTILINE))
                        if generated_count > 0:
                            st.session_state["saved_num_topics"] = generated_count
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to generate topics: {e}")

    # --- Course Topics (outside form, editable) ---
    course_topics = st.text_area(
        "Course Topics",
        placeholder=(
            "## Topic 1: Strategic Marketing Principles\n"
            "- Explain core marketing frameworks and models\n"
            "- Identify target market segments and positioning strategies\n\n"
            "## Topic 2: Consumer Behaviour Analysis\n"
            "- Describe consumer decision-making processes\n"
            "- Analyse factors influencing purchasing behaviour"
        ),
        height=400,
        key="cd_course_topics",
    )
    if course_topics:
        with st.expander("Preview", expanded=False):
            st.markdown(course_topics)

    # --- Rest of settings in form ---
    with st.form("course_details_form"):
        col_dur, col_topics = st.columns(2)
        with col_dur:
            course_duration = st.number_input(
                "Course Duration (hrs)",
                min_value=1,
                value=st.session_state.get("saved_course_duration", 16),
                step=1,
            )
        with col_topics:
            num_topics = st.number_input(
                "No. of Topics",
                min_value=1,
                value=st.session_state.get("saved_num_topics", 4),
                step=1,
            )
        is_casl = st.session_state.get("cp_mode") == "CASL"
        col_instr, col_assess = st.columns(2)
        with col_instr:
            instructional_duration = st.number_input(
                "Instructional Duration (hrs)",
                min_value=1,
                value=st.session_state.get("saved_instructional_duration", 14),
                step=1,
            )
        with col_assess:
            assessment_duration = st.number_input(
                "Assessment Duration (hrs)",
                min_value=0 if is_casl else 1,
                value=st.session_state.get("saved_assessment_duration", 0 if is_casl else 2),
                step=1,
            )
        col_num_instr, col_num_assess = st.columns(2)
        with col_num_instr:
            num_instr_methods = st.number_input(
                "No. of Instructional Methods",
                min_value=1,
                value=st.session_state.get("saved_num_instr_methods", 3),
                step=1,
            )
        with col_num_assess:
            num_assess_methods = st.number_input(
                "No. of Assessment Methods",
                min_value=0 if is_casl else 1,
                value=st.session_state.get("saved_num_assess_methods", 0 if is_casl else 2),
                step=1,
            )
        selected_instr_methods = st.multiselect(
            "Select Instructional Methods",
            options=INSTRUCTION_METHODS_LIST,
            default=st.session_state.get("saved_instr_methods", [
                "Interactive presentation", "Discussions", "Case studies",
            ]),
        )
        selected_assess_methods = st.multiselect(
            "Select Assessment Methods",
            options=ASSESSMENT_METHODS_LIST,
            default=st.session_state.get("saved_assess_methods", [
                "Written Exam", "Practical Exam",
            ]),
        )
        submitted = st.form_submit_button("Save Course Details", type="primary", use_container_width=True)

    if submitted:
        if not course_title or not course_topics:
            st.warning("Please enter both a course title and course topics.")
        elif len(selected_instr_methods) != num_instr_methods:
            st.warning(f"Please select exactly {num_instr_methods} instruction method(s). You selected {len(selected_instr_methods)}.")
        elif num_assess_methods > 0 and len(selected_assess_methods) != num_assess_methods:
            st.warning(f"Please select exactly {num_assess_methods} assessment method(s). You selected {len(selected_assess_methods)}.")
        else:
            st.session_state["saved_course_title"] = course_title
            st.session_state["saved_course_topics"] = course_topics
            st.session_state["saved_course_duration"] = course_duration
            st.session_state["saved_num_topics"] = num_topics
            st.session_state["saved_instructional_duration"] = instructional_duration
            st.session_state["saved_assessment_duration"] = assessment_duration
            st.session_state["saved_num_instr_methods"] = num_instr_methods
            st.session_state["saved_num_assess_methods"] = num_assess_methods
            st.session_state["saved_instr_methods"] = selected_instr_methods
            st.session_state["saved_assess_methods"] = selected_assess_methods if num_assess_methods > 0 else []
            if st.session_state.get("cp_mode") == "CASL":
                st.session_state["saved_unique_skill_name"] = unique_skill_name
            if st.session_state.get("cp_mode") == "WSQ":
                st.session_state["saved_tsc_ref_code"] = tsc_ref_code
                st.session_state["saved_tsc_title"] = tsc_title
            st.rerun()

    # --- Show saved details ---
    if has_course_details:
        saved_duration = st.session_state.get("saved_course_duration", 8)
        saved_num_topics = st.session_state.get("saved_num_topics", 3)
        saved_instr = st.session_state.get("saved_instructional_duration", 7)
        saved_assess = st.session_state.get("saved_assessment_duration", 1)
        saved_num_instr = st.session_state.get("saved_num_instr_methods", 3)
        saved_num_assess = st.session_state.get("saved_num_assess_methods", 1)
        duration_per_topic = saved_duration * 60 / saved_num_topics
        instr_per_topic = saved_instr * 60 / saved_num_topics
        assess_per_topic = saved_assess * 60 / saved_num_topics
        import math
        num_days = max(1, saved_duration / 8)
        calendar_days = math.ceil(num_days)
        instr_per_method_per_day = saved_instr * 60 / calendar_days / saved_num_instr
        assess_per_method = saved_assess * 60 / saved_num_assess if saved_num_assess > 0 else 0

        st.divider()
        st.markdown(f"## {saved_title}")

        summary_data = {
            "Field": [
                "Total Course Duration",
                "Number of Topics",
                "Duration per Topic",
                "Instructional Duration",
                "Instructional per Topic",
                "No. of Instructional Methods",
                "Duration per Instructional Method per Day",
                "Assessment Duration",
                "No. of Assessment Methods",
                "Duration per Assessment Method",
            ],
            "Value": [
                f"{saved_duration * 60:.0f} mins",
                str(saved_num_topics),
                f"{duration_per_topic:.0f} mins",
                f"{saved_instr} hrs",
                f"{instr_per_topic:.0f} mins",
                str(saved_num_instr),
                f"{instr_per_method_per_day:.0f} mins",
                f"{saved_assess} hrs" if saved_num_assess > 0 else "N/A",
                str(saved_num_assess),
                f"{assess_per_method:.0f} mins" if saved_num_assess > 0 else "N/A",
            ],
        }
        st.dataframe(summary_data, use_container_width=True, hide_index=True)


# ============================================================
# PAGE: About This Course
# ============================================================
elif active_page == "About This Course":
    st.header("About This Course")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")
    st.markdown(
        "AI will generate a professional \"About the Course\" description "
        "suitable for course listings."
    )

    # --- Editable prompt template ---
    with st.expander("Prompt Template", expanded=False):
        about_prompt = st.text_area(
            "Edit the prompt template used for generation. "
            "Use `{course_title}` and `{course_topics}` as placeholders.",
            value=st.session_state.get("about_prompt", ABOUT_COURSE_PROMPT_TEMPLATE),
            height=300,
            key="about_prompt_input",
        )
        st.session_state["about_prompt"] = about_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        generate_clicked = st.button(
            "Generate",
            type="primary",
            use_container_width=True,
            key="about_gen",
        )
    with col_regen:
        regenerate_clicked = st.button(
            "Regenerate",
            use_container_width=True,
            key="about_regen",
        )

    # --- Generation Logic ---
    if generate_clicked or regenerate_clicked:
        if not has_course_details:
            st.warning("Please enter course details first on the **Course Details** page.")
        else:
            with st.spinner("Generating description..."):
                try:
                    result = generate_about_course(
                        saved_title, saved_topics,
                        prompt_template=st.session_state.get("about_prompt"),
                    )
                    st.session_state["about_course_text"] = result
                except Exception as e:
                    st.error(f"Failed to generate text: {e}")

    # --- Display Result ---
    if st.session_state.get("about_course_text"):
        st.divider()
        st.markdown("**Generated \"About the Course\" Text:**")
        st.code(st.session_state["about_course_text"], language=None, wrap_lines=True)

# ============================================================
# PAGE: What You'll Learn
# ============================================================
elif active_page == "What You'll Learn":
    st.header("What You'll Learn")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")
    st.markdown(
        "AI will generate learning outcomes describing the skills and knowledge "
        "trainees will gain from the course."
    )

    # --- Editable prompt template ---
    with st.expander("Prompt Template", expanded=False):
        wyl_prompt = st.text_area(
            "Edit the prompt template used for generation. "
            "Use `{course_title}` and `{course_topics}` as placeholders.",
            value=st.session_state.get("wyl_prompt", WHAT_YOULL_LEARN_PROMPT_TEMPLATE),
            height=300,
            key="wyl_prompt_input",
        )
        st.session_state["wyl_prompt"] = wyl_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        wyl_generate = st.button(
            "Generate",
            type="primary",
            use_container_width=True,
            key="wyl_gen",
        )
    with col_regen:
        wyl_regenerate = st.button(
            "Regenerate",
            use_container_width=True,
            key="wyl_regen",
        )

    # --- Generation Logic ---
    if wyl_generate or wyl_regenerate:
        if not has_course_details:
            st.warning("Please enter course details first on the **Course Details** page.")
        else:
            with st.spinner("Generating learning outcomes..."):
                try:
                    result = generate_what_youll_learn(
                        saved_title, saved_topics,
                        prompt_template=st.session_state.get("wyl_prompt"),
                    )
                    st.session_state["wyl_text"] = result
                except Exception as e:
                    st.error(f"Failed to generate text: {e}")

    # --- Display Result ---
    if st.session_state.get("wyl_text"):
        st.divider()
        st.markdown("**Generated \"What You'll Learn\" Text:**")
        st.code(st.session_state["wyl_text"], language=None, wrap_lines=True)

# ============================================================
# PAGE: Background Part A
# ============================================================
elif active_page == "Background Part A":
    st.header("Background Part A")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")
    st.markdown(
        "AI will generate a background section covering targeted sector(s), "
        "target audience / job role(s), and needs for the training."
    )

    # --- Editable prompt template ---
    with st.expander("Prompt Template", expanded=False):
        bg_prompt = st.text_area(
            "Edit the prompt template used for generation. "
            "Use `{course_title}` and `{course_topics}` as placeholders.",
            value=st.session_state.get("bg_prompt", BACKGROUND_PART_A_PROMPT_TEMPLATE),
            height=300,
            key="bg_prompt_input",
        )
        st.session_state["bg_prompt"] = bg_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        bg_generate = st.button(
            "Generate",
            type="primary",
            use_container_width=True,
            key="bg_gen",
        )
    with col_regen:
        bg_regenerate = st.button(
            "Regenerate",
            use_container_width=True,
            key="bg_regen",
        )

    # --- Generation Logic ---
    if bg_generate or bg_regenerate:
        if not has_course_details:
            st.warning("Please enter course details first on the **Course Details** page.")
        else:
            with st.spinner("Generating background section..."):
                try:
                    result = generate_background_part_a(
                        saved_title, saved_topics,
                        prompt_template=st.session_state.get("bg_prompt"),
                    )
                    st.session_state["bg_text"] = result
                except Exception as e:
                    st.error(f"Failed to generate text: {e}")

    # --- Display Result ---
    if st.session_state.get("bg_text"):
        st.divider()
        st.markdown("**Generated \"Background Part A\" Text:**")
        st.code(st.session_state["bg_text"], language=None, wrap_lines=True)

# ============================================================
# PAGE: Background Part B
# ============================================================
elif active_page == "Background Part B":
    st.header("Background Part B")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")
    st.markdown(
        "AI will generate a section covering performance gaps the course addresses, "
        "how the gaps were identified, and how learners will benefit post-training."
    )

    # --- Editable prompt template ---
    with st.expander("Prompt Template", expanded=False):
        bgb_prompt = st.text_area(
            "Edit the prompt template used for generation. "
            "Use `{course_title}` and `{course_topics}` as placeholders.",
            value=st.session_state.get("bgb_prompt", BACKGROUND_PART_B_PROMPT_TEMPLATE),
            height=300,
            key="bgb_prompt_input",
        )
        st.session_state["bgb_prompt"] = bgb_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        bgb_generate = st.button(
            "Generate",
            type="primary",
            use_container_width=True,
            key="bgb_gen",
        )
    with col_regen:
        bgb_regenerate = st.button(
            "Regenerate",
            use_container_width=True,
            key="bgb_regen",
        )

    # --- Generation Logic ---
    if bgb_generate or bgb_regenerate:
        if not has_course_details:
            st.warning("Please enter course details first on the **Course Details** page.")
        else:
            with st.spinner("Generating performance gaps section..."):
                try:
                    result = generate_background_part_b(
                        saved_title, saved_topics,
                        prompt_template=st.session_state.get("bgb_prompt"),
                    )
                    st.session_state["bgb_text"] = result
                except Exception as e:
                    st.error(f"Failed to generate text: {e}")

    # --- Display Result ---
    if st.session_state.get("bgb_text"):
        st.divider()
        st.markdown("**Generated \"Background Part B\" Text:**")
        st.code(st.session_state["bgb_text"], language=None, wrap_lines=True)

# ============================================================
# PAGE: Learning Outcomes
# ============================================================
elif active_page == "Learning Outcomes":
    st.header("Learning Outcomes")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")
    st.markdown(
        "AI will generate learning outcomes for each topic. "
        "Each outcome starts with an action verb and is under 25 words."
    )

    # --- Editable prompt template ---
    with st.expander("Prompt Template", expanded=False):
        lo_prompt = st.text_area(
            "Edit the prompt template used for generation. "
            "Use `{course_title}` and `{course_topics}` as placeholders.",
            value=st.session_state.get("lo_prompt", LEARNING_OUTCOME_PROMPT_TEMPLATE),
            height=300,
            key="lo_prompt_input",
        )
        st.session_state["lo_prompt"] = lo_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        lo_generate = st.button(
            "Generate",
            type="primary",
            use_container_width=True,
            key="lo_gen",
        )
    with col_regen:
        lo_regenerate = st.button(
            "Regenerate",
            use_container_width=True,
            key="lo_regen",
        )

    # --- Generation Logic ---
    if lo_generate or lo_regenerate:
        if not has_course_details:
            st.warning("Please enter course details first on the **Course Details** page.")
        else:
            with st.spinner("Generating learning outcomes..."):
                try:
                    result = generate_learning_outcomes(
                        saved_title, saved_topics,
                        prompt_template=st.session_state.get("lo_prompt"),
                    )
                    st.session_state["lo_text"] = result
                except Exception as e:
                    st.error(f"Failed to generate text: {e}")

    # --- Display Result ---
    if st.session_state.get("lo_text"):
        st.divider()
        st.markdown("**Generated Learning Outcomes:**")
        st.code(st.session_state["lo_text"], language=None, wrap_lines=True)

# ============================================================
# PAGE: Instructional Methods
# ============================================================
elif active_page == "Instructional Methods":
    st.header("Instructional Methods")

    saved_im = st.session_state.get("saved_instr_methods", [])
    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    elif not saved_im:
        st.warning("Please select instruction methods on the **Course Details** page first.")
    else:
        st.info(f"**Course:** {saved_title}")
        st.markdown(f"**Selected Methods:** {', '.join(saved_im)}")
    st.markdown(
        "AI will generate an elaboration on the appropriateness of each "
        "selected instructional method for achieving the course learning outcomes."
    )

    # --- Editable prompt template ---
    with st.expander("Prompt Template", expanded=False):
        im_prompt = st.text_area(
            "Edit the prompt template used for generation. "
            "Use `{course_title}`, `{course_topics}`, and `{method_name}` as placeholders.",
            value=st.session_state.get("im_prompt", INSTRUCTION_METHOD_PROMPT_TEMPLATE),
            height=300,
            key="im_prompt_input",
        )
        st.session_state["im_prompt"] = im_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        im_generate = st.button(
            "Generate All",
            type="primary",
            use_container_width=True,
            key="im_gen",
        )
    with col_regen:
        im_regenerate = st.button(
            "Regenerate All",
            use_container_width=True,
            key="im_regen",
        )

    # --- Generation Logic ---
    if im_generate or im_regenerate:
        if not has_course_details or not saved_im:
            st.warning("Please enter course details and select instruction methods first.")
        else:
            results = {}
            for method in saved_im:
                with st.spinner(f"Generating for {method}..."):
                    try:
                        result = generate_instruction_method(
                            saved_title, saved_topics, method,
                            prompt_template=st.session_state.get("im_prompt"),
                        )
                        results[method] = result
                    except Exception as e:
                        results[method] = f"Error: {e}"
            st.session_state["im_results"] = results

    # --- Display Results ---
    if st.session_state.get("im_results"):
        st.divider()
        for method, text in st.session_state["im_results"].items():
            st.markdown(f"### {method}")
            st.code(text, language=None, wrap_lines=True)

# ============================================================
# PAGE: Assessment Methods
# ============================================================
elif active_page == "Assessment Methods":
    st.header("Assessment Methods")

    saved_am = st.session_state.get("saved_assess_methods", [])
    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    elif not saved_am and st.session_state.get("saved_num_assess_methods", 1) == 0:
        st.info("No assessment methods configured for this CASL course.")
    elif not saved_am:
        st.warning("Please select assessment methods on the **Course Details** page first.")
    else:
        st.info(f"**Course:** {saved_title}")
        st.markdown(f"**Selected Methods:** {', '.join(saved_am)}")
    st.markdown(
        "AI will generate an elaboration on the appropriateness of each "
        "selected assessment method for this course."
    )

    # --- Editable prompt template ---
    with st.expander("Prompt Template", expanded=False):
        am_prompt = st.text_area(
            "Edit the prompt template used for generation. "
            "Use `{course_title}`, `{course_topics}`, and `{method_name}` as placeholders.",
            value=st.session_state.get("am_prompt", ASSESSMENT_METHOD_PROMPT_TEMPLATE),
            height=300,
            key="am_prompt_input",
        )
        st.session_state["am_prompt"] = am_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        am_generate = st.button(
            "Generate All",
            type="primary",
            use_container_width=True,
            key="am_gen",
        )
    with col_regen:
        am_regenerate = st.button(
            "Regenerate All",
            use_container_width=True,
            key="am_regen",
        )

    # --- Generation Logic ---
    if am_generate or am_regenerate:
        if not has_course_details or not saved_am:
            st.warning("Please enter course details and select assessment methods first.")
        else:
            results = {}
            for method in saved_am:
                with st.spinner(f"Generating for {method}..."):
                    try:
                        result = generate_assessment_method(
                            saved_title, saved_topics, method,
                            prompt_template=st.session_state.get("am_prompt"),
                        )
                        results[method] = result
                    except Exception as e:
                        results[method] = f"Error: {e}"
            st.session_state["am_results"] = results

    # --- Display Results ---
    if st.session_state.get("am_results"):
        st.divider()
        for method, text in st.session_state["am_results"].items():
            st.markdown(f"### {method}")
            st.code(text, language=None, wrap_lines=True)

# ============================================================
# PAGE: Min Entry Requirements
# ============================================================
elif active_page == "Min Entry Requirements":
    st.header("Min Entry Requirements")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")
    st.markdown(
        "AI will generate minimum entry requirements covering knowledge and skills, "
        "attitude, experience, and target age group."
    )

    mer_special_req = st.text_area(
        "Special Requirements (optional)",
        value="",
        height=80,
        key="mer_special_req",
        placeholder="e.g. Participants must have basic IT skills, minimum diploma in relevant field, etc.",
    )

    # --- Editable prompt template ---
    with st.expander("Prompt Template", expanded=False):
        mer_prompt = st.text_area(
            "Edit the prompt template used for generation. "
            "Use `{course_title}`, `{course_topics}`, and `{special_requirements}` as placeholders.",
            value=st.session_state.get("mer_prompt", MINIMUM_ENTRY_REQUIREMENT_PROMPT_TEMPLATE),
            height=300,
            key="mer_prompt_input",
        )
        st.session_state["mer_prompt"] = mer_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        mer_generate = st.button(
            "Generate",
            type="primary",
            use_container_width=True,
            key="mer_gen",
        )
    with col_regen:
        mer_regenerate = st.button(
            "Regenerate",
            use_container_width=True,
            key="mer_regen",
        )

    # --- Generation Logic ---
    if mer_generate or mer_regenerate:
        if not has_course_details:
            st.warning("Please enter course details first on the **Course Details** page.")
        else:
            with st.spinner("Generating entry requirements..."):
                try:
                    result = generate_minimum_entry_requirement(
                        saved_title, saved_topics,
                        prompt_template=st.session_state.get("mer_prompt"),
                        special_requirements=mer_special_req,
                    )
                    st.session_state["mer_text"] = result
                except Exception as e:
                    st.error(f"Failed to generate text: {e}")

    # --- Display Result ---
    if st.session_state.get("mer_text"):
        st.divider()
        st.markdown("**Generated \"Minimum Entry Requirement\" Text:**")
        st.code(st.session_state["mer_text"], language=None, wrap_lines=True)

# ============================================================
# PAGE: Job Roles
# ============================================================
elif active_page == "Job Roles":
    st.header("Job Roles")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")
    st.markdown(
        "AI will generate 10 relevant job roles for the course in comma-separated format, "
        "following SSG Skills Framework / MySkillsFuture Jobs-Skills Portal naming."
    )

    # --- Editable prompt template ---
    with st.expander("Prompt Template", expanded=False):
        jr_prompt = st.text_area(
            "Edit the prompt template used for generation. "
            "Use `{course_title}` and `{course_topics}` as placeholders.",
            value=JOB_ROLES_PROMPT_TEMPLATE,
            height=300,
            key="jr_prompt_input",
        )
        st.session_state["jr_prompt"] = jr_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        jr_generate = st.button(
            "Generate",
            type="primary",
            use_container_width=True,
            key="jr_gen",
        )
    with col_regen:
        jr_regenerate = st.button(
            "Regenerate",
            use_container_width=True,
            key="jr_regen",
        )

    # --- Generation Logic ---
    if jr_generate or jr_regenerate:
        if not has_course_details:
            st.warning("Please enter course details first on the **Course Details** page.")
        else:
            with st.spinner("Generating job roles..."):
                try:
                    result = generate_job_roles(
                        saved_title, saved_topics,
                        prompt_template=st.session_state.get("jr_prompt"),
                    )
                    st.session_state["jr_text"] = result
                except Exception as e:
                    st.error(f"Failed to generate text: {e}")

    # --- Display Result ---
    if st.session_state.get("jr_text"):
        st.divider()
        st.markdown("**Generated Job Roles:**")
        st.code(st.session_state["jr_text"], language=None, wrap_lines=True)

# ============================================================
# PAGE: Course Outline
# ============================================================
elif active_page == "Course Outline":
    st.header("Course Outline")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")

    if st.button("Generate", type="primary", use_container_width=True, key="co_gen"):
        if not has_course_details:
            st.warning("Please enter course details first on the **Course Details** page.")
        else:
            saved_duration = st.session_state.get("saved_course_duration", 16)
            saved_num_topics = st.session_state.get("saved_num_topics", 4)
            duration_per_topic = saved_duration * 60 / saved_num_topics
            saved_im = st.session_state.get("saved_instr_methods", [])
            main_topics = re.findall(r"^##\s*Topic\s*\d+:\s*(.+)$", saved_topics, re.MULTILINE)

            info_lines = []
            if main_topics:
                info_lines.append("(1) The list of topics covered in this course")
                for i, topic in enumerate(main_topics, 1):
                    info_lines.append(f"T{i}: {topic}")

            if saved_im:
                info_lines.append("")
                info_lines.append("(2) Instructional methods")
                info_lines.append(", ".join(saved_im))

            if main_topics:
                info_lines.append("")
                info_lines.append("(3) Duration for each topic")
                for i, topic in enumerate(main_topics, 1):
                    info_lines.append(f"Topic {i}: {duration_per_topic:.0f}mins")

            st.session_state["co_text"] = "\n".join(info_lines)

    # --- Display Result ---
    if st.session_state.get("co_text"):
        st.divider()
        st.code(st.session_state["co_text"], language=None, wrap_lines=True)

# ============================================================
# PAGE: Lesson Plan
# ============================================================
elif active_page == "Lesson Plan":
    st.header("Lesson Plan")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")
    st.markdown(
        "Generate a lesson plan from your course details. "
        "Downloads are available as Word (.docx) and PDF (.pdf)."
    )

    # --- AI prompt template ---
    with st.expander("AI Prompt Template", expanded=False):
        lp_prompt = st.text_area(
            "Edit the prompt template used for AI generation.",
            value=st.session_state.get("lp_prompt", LESSON_PLAN_PROMPT_TEMPLATE),
            height=300,
            key="lp_prompt_input",
        )
        st.session_state["lp_prompt"] = lp_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        lp_generate = st.button(
            "Generate",
            type="primary",
            use_container_width=True,
            key="lp_gen",
        )
    with col_regen:
        lp_regenerate = st.button(
            "Regenerate",
            use_container_width=True,
            key="lp_regen",
        )

    # --- Build schedule & generate documents ---
    if lp_generate or lp_regenerate:
        if not has_course_details:
            st.warning("Please enter course details first on the **Course Details** page.")
        else:
            # --- Collect course details ---
            lp_duration = st.session_state.get("saved_course_duration", 16)
            lp_instr_hrs = st.session_state.get("saved_instructional_duration", 14)
            lp_assess_hrs = st.session_state.get("saved_assessment_duration", 2)
            lp_num_topics = st.session_state.get("saved_num_topics", 4)
            lp_im = st.session_state.get("saved_instr_methods", [])
            lp_am = st.session_state.get("saved_assess_methods", [])

            main_topics = re.findall(r"^##\s*Topic\s*\d+:\s*(.+)$", saved_topics, re.MULTILINE)
            num_topics = len(main_topics) if main_topics else lp_num_topics
            # --- Build schedule from course details ---
            def _fmt_12h(mins: int) -> str:
                h, m = divmod(mins, 60)
                suffix = "AM" if h < 12 else "PM"
                if h > 12:
                    h -= 12
                elif h == 0:
                    h = 12
                return f"{h}:{m:02d} {suffix}"

            DAY_START = 9 * 60          # 9:00 AM
            DAY_END = 18 * 60           # 6:00 PM
            LUNCH_START = 12 * 60 + 30  # 12:30 PM
            LUNCH_END = 13 * 60 + 15    # 1:15 PM
            LUNCH_MINS = 45
            MIN_SESSION = 15  # min topic session length to avoid tiny splits

            num_days = max(1, lp_duration // 8)
            instr_per_topic = (lp_instr_hrs * 60) // num_topics if num_topics else 0
            assess_total_mins = lp_assess_hrs * 60
            assess_start = DAY_END - assess_total_mins  # e.g. 4:00 PM

            schedule: dict[int, list[dict]] = {}
            topic_idx = 0
            carry = 0  # minutes of current topic already scheduled

            for day in range(1, num_days + 1):
                rows: list[dict] = []
                current = DAY_START
                is_last_day = (day == num_days)
                lunch_done = False

                while topic_idx < num_topics:
                    # --- Handle barriers first ---
                    if not lunch_done and current >= LUNCH_START:
                        rows.append({
                            "timing": f"{_fmt_12h(LUNCH_START)} - {_fmt_12h(LUNCH_END)}",
                            "duration": f"{LUNCH_MINS} mins",
                            "description": "Lunch Break",
                            "methods": "",
                        })
                        current = LUNCH_END
                        lunch_done = True
                        continue
                    if is_last_day and current >= assess_start:
                        break
                    if current >= DAY_END:
                        break

                    # --- Determine next barrier ---
                    if not lunch_done:
                        barrier = LUNCH_START
                    elif is_last_day:
                        barrier = assess_start
                    else:
                        barrier = DAY_END

                    avail = barrier - current
                    topic_remaining = instr_per_topic - carry

                    if avail < MIN_SESSION:
                        if not lunch_done and barrier == LUNCH_START:
                            # Start lunch early to avoid tiny break next to lunch
                            lunch_end = current + LUNCH_MINS
                            rows.append({
                                "timing": f"{_fmt_12h(current)} - {_fmt_12h(lunch_end)}",
                                "duration": f"{LUNCH_MINS} mins",
                                "description": "Lunch Break",
                                "methods": "",
                            })
                            current = lunch_end
                            lunch_done = True
                        else:
                            # Insert break before other barriers (assessment, day-end)
                            if avail > 0:
                                rows.append({
                                    "timing": f"{_fmt_12h(current)} - {_fmt_12h(barrier)}",
                                    "duration": f"{avail} mins",
                                    "description": "Break",
                                    "methods": "",
                                })
                            current = barrier
                        continue

                    topic_name = main_topics[topic_idx] if topic_idx < len(main_topics) else f"Topic {topic_idx + 1}"
                    label = f"T{topic_idx + 1}: {topic_name}"
                    if carry > 0:
                        label += " (Cont'd)"

                    methods_str = ", ".join(lp_im) if lp_im else ""

                    if topic_remaining <= avail:
                        # Topic fits completely before barrier
                        end = current + topic_remaining
                        rows.append({
                            "timing": f"{_fmt_12h(current)} - {_fmt_12h(end)}",
                            "duration": f"{topic_remaining} mins",
                            "description": label,
                            "methods": methods_str,
                        })
                        current = end
                        carry = 0
                        topic_idx += 1
                    else:
                        # Split topic at barrier
                        rows.append({
                            "timing": f"{_fmt_12h(current)} - {_fmt_12h(barrier)}",
                            "duration": f"{avail} mins",
                            "description": label,
                            "methods": methods_str,
                        })
                        carry += avail
                        current = barrier

                # --- Fill remaining day structure after topics ---
                if not lunch_done:
                    if current < LUNCH_START:
                        gap = LUNCH_START - current
                        if gap > 0:
                            rows.append({
                                "timing": f"{_fmt_12h(current)} - {_fmt_12h(LUNCH_START)}",
                                "duration": f"{gap} mins",
                                "description": "Break",
                                "methods": "",
                            })
                        current = LUNCH_START
                    rows.append({
                        "timing": f"{_fmt_12h(LUNCH_START)} - {_fmt_12h(LUNCH_END)}",
                        "duration": f"{LUNCH_MINS} mins",
                        "description": "Lunch Break",
                        "methods": "",
                    })
                    current = LUNCH_END
                    lunch_done = True

                if is_last_day and assess_total_mins > 0:
                    if current < assess_start:
                        gap = assess_start - current
                        rows.append({
                            "timing": f"{_fmt_12h(current)} - {_fmt_12h(assess_start)}",
                            "duration": f"{gap} mins",
                            "description": "Break",
                            "methods": "",
                        })
                    rows.append({
                        "timing": f"{_fmt_12h(assess_start)} - {_fmt_12h(DAY_END)}",
                        "duration": f"{assess_total_mins} mins",
                        "description": f"Assessment: {', '.join(lp_am)}",
                        "methods": "",
                    })

                schedule[day] = rows

            # --- Generate documents ---
            with st.spinner("Generating lesson plan documents..."):
                try:
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        docx_path = Path(tmp_dir) / "lesson_plan.docx"
                        generate_lesson_plan_table(
                            saved_title, lp_duration, lp_instr_hrs, lp_assess_hrs,
                            schedule, docx_path,
                            instructional_methods=lp_im,
                        )
                        st.session_state["lp_docx_bytes"] = docx_path.read_bytes()

                        pdf_path = Path(tmp_dir) / "lesson_plan.pdf"
                        generate_lesson_plan_pdf_table(
                            saved_title, lp_duration, lp_instr_hrs, lp_assess_hrs,
                            schedule, pdf_path,
                            instructional_methods=lp_im,
                        )
                        st.session_state["lp_pdf_bytes"] = pdf_path.read_bytes()

                    st.session_state["lp_generated"] = True
                except Exception as e:
                    st.error(f"Failed to generate documents: {e}")

            # --- AI generation ---
            with st.spinner("Generating lesson plan text with AI..."):
                try:
                    result = generate_lesson_plan_content(
                        course_title=saved_title,
                        course_topics=saved_topics,
                        course_duration=lp_duration,
                        instructional_duration=lp_instr_hrs,
                        assessment_duration=lp_assess_hrs,
                        instructional_methods=lp_im,
                        assessment_methods=lp_am,
                        prompt_template=st.session_state.get("lp_prompt"),
                    )
                    st.session_state["lp_text"] = result
                except Exception as e:
                    st.error(f"Failed to generate AI lesson plan: {e}")

    # --- Downloads ---
    if st.session_state.get("lp_generated"):
        st.divider()
        st.subheader("Downloads")
        safe_name = saved_title.replace(" ", "_") if saved_title else "Lesson_Plan"
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download Lesson Plan (.docx)",
                data=st.session_state["lp_docx_bytes"],
                file_name=f"{safe_name}_Lesson_Plan.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )
        with col2:
            st.download_button(
                label="Download Lesson Plan (.pdf)",
                data=st.session_state["lp_pdf_bytes"],
                file_name=f"{safe_name}_Lesson_Plan.pdf",
                mime="application/pdf",
                use_container_width=True,
            )

    # --- AI-Generated Text ---
    if st.session_state.get("lp_text"):
        st.divider()
        st.markdown("**AI-Generated Lesson Plan:**")
        st.code(st.session_state["lp_text"], language=None, wrap_lines=True)

# ============================================================
# PAGE: CP Quality Audit
# ============================================================
elif active_page == "CP Quality Audit":
    st.header("CP Quality Audit")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")
        st.markdown(
            "Upload the Course Proposal Excel file to check consistency "
            "against your saved course details. Any mismatches will be highlighted."
        )

        uploaded_cp = st.file_uploader(
            "Upload CP Excel file", type=["xlsx"],
            help="Select the .xlsx Course Proposal file to audit",
            key="cp_audit_upload",
        )

        if uploaded_cp is not None:
            st.success(f"**{uploaded_cp.name}** uploaded ({uploaded_cp.size / 1024:.0f} KB)")

            if st.button("Run Audit", type="primary", use_container_width=True, key="cp_audit_btn"):
                with st.spinner("Extracting data and running audit..."):
                    try:
                        with tempfile.TemporaryDirectory() as tmp_dir:
                            tmp_path = Path(tmp_dir) / uploaded_cp.name
                            tmp_path.write_bytes(uploaded_cp.getvalue())
                            data = extract_data(tmp_path)

                        issues = []
                        passes = []

                        # --- 1. Course Title ---
                        if data.particulars.course_title.strip().lower() != saved_title.strip().lower():
                            issues.append({
                                "field": "Course Title",
                                "expected": saved_title,
                                "found": data.particulars.course_title,
                            })
                        else:
                            passes.append("Course Title")

                        # --- 2. Unique Skill Name (CASL mode) ---
                        if st.session_state.get("cp_mode") == "CASL":
                            expected_usn = st.session_state.get("saved_unique_skill_name", "")
                            cp_usn = ", ".join(data.particulars.unique_skill_names)
                            if expected_usn and expected_usn.lower() not in cp_usn.lower():
                                issues.append({
                                    "field": "Unique Skill Name",
                                    "expected": expected_usn,
                                    "found": cp_usn,
                                })
                            else:
                                passes.append("Unique Skill Name")

                        # --- 3. Number of Topics ---
                        expected_num_topics = st.session_state.get("saved_num_topics", 0)
                        cp_num_topics = len(data.learning_outcomes)
                        if expected_num_topics != cp_num_topics:
                            issues.append({
                                "field": "Number of Topics",
                                "expected": str(expected_num_topics),
                                "found": str(cp_num_topics),
                            })
                        else:
                            passes.append("Number of Topics")

                        # --- 4. Topic Names ---
                        main_topics = re.findall(
                            r"^##\s*Topic\s*\d+:\s*(.+)$", saved_topics, re.MULTILINE
                        )
                        cp_topics = [lo.topic for lo in data.learning_outcomes]
                        for i, expected_topic in enumerate(main_topics):
                            expected_clean = expected_topic.strip().lower()
                            found_in_cp = any(
                                expected_clean in ct.lower() for ct in cp_topics
                            )
                            if not found_in_cp:
                                issues.append({
                                    "field": f"Topic {i + 1}",
                                    "expected": expected_topic.strip(),
                                    "found": cp_topics[i] if i < len(cp_topics) else "(missing)",
                                })
                        if not any(item["field"].startswith("Topic ") for item in issues):
                            passes.append("Topic Names")

                        # --- 5. Instructional Methods ---
                        expected_im = set(
                            m.lower() for m in st.session_state.get("saved_instr_methods", [])
                        )
                        cp_im = set(im.method.lower() for im in data.instruction_methods)
                        missing_im = expected_im - cp_im
                        extra_im = cp_im - expected_im
                        if missing_im:
                            issues.append({
                                "field": "Instructional Methods (missing)",
                                "expected": ", ".join(sorted(missing_im)),
                                "found": "(not in CP)",
                            })
                        if extra_im:
                            issues.append({
                                "field": "Instructional Methods (extra in CP)",
                                "expected": "(not selected)",
                                "found": ", ".join(sorted(extra_im)),
                            })
                        if not missing_im and not extra_im:
                            passes.append("Instructional Methods")

                        # --- 6. Assessment Methods ---
                        expected_am = set(
                            m.lower() for m in st.session_state.get("saved_assess_methods", [])
                        )
                        cp_am = set(am.mode.lower() for am in data.assessment_modes)
                        missing_am = expected_am - cp_am
                        extra_am = cp_am - expected_am
                        if missing_am:
                            issues.append({
                                "field": "Assessment Methods (missing)",
                                "expected": ", ".join(sorted(missing_am)),
                                "found": "(not in CP)",
                            })
                        if extra_am:
                            issues.append({
                                "field": "Assessment Methods (extra in CP)",
                                "expected": "(not selected)",
                                "found": ", ".join(sorted(extra_am)),
                            })
                        if not missing_am and not extra_am:
                            passes.append("Assessment Methods")

                        # --- 7. About This Course ---
                        expected_about = st.session_state.get("about_course_text", "")
                        if expected_about:
                            cp_about = data.particulars.about_course.strip()
                            if expected_about.strip()[:200].lower() != cp_about[:200].lower():
                                issues.append({
                                    "field": "About This Course",
                                    "expected": expected_about[:100] + "...",
                                    "found": cp_about[:100] + "..." if cp_about else "(empty)",
                                })
                            else:
                                passes.append("About This Course")

                        # --- 8. What You'll Learn ---
                        expected_wyl = st.session_state.get("wyl_text", "")
                        if expected_wyl:
                            cp_wyl = data.particulars.what_youll_learn.strip()
                            if expected_wyl.strip()[:200].lower() != cp_wyl[:200].lower():
                                issues.append({
                                    "field": "What You'll Learn",
                                    "expected": expected_wyl[:100] + "...",
                                    "found": cp_wyl[:100] + "..." if cp_wyl else "(empty)",
                                })
                            else:
                                passes.append("What You'll Learn")

                        # --- 9. Background Part A ---
                        expected_bg = st.session_state.get("bg_text", "")
                        if expected_bg:
                            cp_bg = data.background.targeted_sectors.strip()
                            if expected_bg.strip()[:200].lower() != cp_bg[:200].lower():
                                issues.append({
                                    "field": "Background Part A",
                                    "expected": expected_bg[:100] + "...",
                                    "found": cp_bg[:100] + "..." if cp_bg else "(empty)",
                                })
                            else:
                                passes.append("Background Part A")

                        # --- 10. Background Part B ---
                        expected_bgb = st.session_state.get("bgb_text", "")
                        if expected_bgb:
                            cp_bgb = data.background.performance_gaps.strip()
                            if expected_bgb.strip()[:200].lower() != cp_bgb[:200].lower():
                                issues.append({
                                    "field": "Background Part B",
                                    "expected": expected_bgb[:100] + "...",
                                    "found": cp_bgb[:100] + "..." if cp_bgb else "(empty)",
                                })
                            else:
                                passes.append("Background Part B")

                        st.session_state["audit_issues"] = issues
                        st.session_state["audit_passes"] = passes
                        st.session_state["audit_extracted_data"] = data

                    except Exception as e:
                        st.error(f"Failed to extract data from Excel: {e}")

        # --- Display Audit Results ---
        if st.session_state.get("audit_issues") is not None:
            issues = st.session_state["audit_issues"]
            passes = st.session_state["audit_passes"]

            st.divider()

            if not issues:
                st.success(f"All {len(passes)} checks passed. No issues found.")
            else:
                st.error(f"{len(issues)} issue(s) found, {len(passes)} check(s) passed.")

            # Show issues
            if issues:
                st.subheader("Issues")
                for item in issues:
                    with st.container(border=True):
                        st.markdown(f"**{item['field']}**")
                        col_exp, col_found = st.columns(2)
                        with col_exp:
                            st.markdown(f"Expected: `{item['expected']}`")
                        with col_found:
                            st.markdown(f"Found in CP: `{item['found']}`")

            # Show passes
            if passes:
                with st.expander(f"Passed Checks ({len(passes)})", expanded=False):
                    for p in passes:
                        st.markdown(f"- {p}")

            # --- Download Audit Report as Word Doc ---
            audit_data = st.session_state.get("audit_extracted_data")
            if audit_data is not None:
                st.divider()
                st.subheader("Download Audit Report")
                st.markdown("Download a Word document with all key information extracted from the CP Excel.")

                if st.button("Generate Audit Report", type="primary", use_container_width=True, key="audit_report_btn"):
                    with st.spinner("Generating audit report..."):
                        try:
                            with tempfile.TemporaryDirectory() as tmp_dir:
                                report_path = Path(tmp_dir) / "CP_Audit_Report.docx"
                                generate_audit_report(
                                    audit_data,
                                    st.session_state.get("cp_mode", "CASL"),
                                    report_path,
                                    min_entry_req=st.session_state.get("mer_text", ""),
                                    job_roles=st.session_state.get("jr_text", ""),
                                    tsc_ref_code=st.session_state.get("saved_tsc_ref_code", ""),
                                    tsc_title=st.session_state.get("saved_tsc_title", ""),
                                    im_descriptions=st.session_state.get("im_results", {}),
                                    am_descriptions=st.session_state.get("am_results", {}),
                                )
                                st.session_state["audit_report_bytes"] = report_path.read_bytes()
                        except Exception as e:
                            st.error(f"Failed to generate audit report: {e}")

                if st.session_state.get("audit_report_bytes"):
                    st.download_button(
                        label="Download CP Audit Report (.docx)",
                        data=st.session_state["audit_report_bytes"],
                        file_name="CP_Audit_Report.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )

# ============================================================
# PAGE: LU Sequencing Rationale
# ============================================================
elif active_page == "LU Sequencing Rationale":
    st.header("Rationale of LU Sequencing")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")
    st.markdown(
        "AI will generate a justification for the rationale of Learning Unit (LU) "
        "sequencing based on your chosen curriculum framework."
    )

    # --- Sequencing Type Selection ---
    sequencing_type = st.selectbox(
        "Sequencing Framework",
        options=LU_SEQUENCING_TYPES,
        index=0,
        key="lu_seq_type",
    )

    # --- Learning Outcomes input ---
    lo_default = st.session_state.get("lo_text", "")
    lu_learning_outcomes = st.text_area(
        "Learning Outcomes",
        value=lo_default,
        height=200,
        key="lu_seq_lo",
        placeholder="Paste your learning outcomes here (e.g. from the Learning Outcomes page).",
    )

    # --- Course Outline input ---
    co_default = st.session_state.get("co_text", "")
    lu_course_outline = st.text_area(
        "Course Outline",
        value=co_default,
        height=200,
        key="lu_seq_co",
        placeholder="Paste your course outline here (e.g. from the Course Outline page).",
    )

    # --- Editable prompt template ---
    current_template = LU_SEQUENCING_TEMPLATES.get(sequencing_type, "")
    with st.expander("Prompt Template", expanded=False):
        lu_prompt = st.text_area(
            "Edit the prompt template used for generation. "
            "Use `{course}`, `{learning_outcomes}`, and `{course_outline}` as placeholders.",
            value=st.session_state.get(f"lu_seq_prompt_{sequencing_type}", current_template),
            height=300,
            key="lu_seq_prompt_input",
        )
        st.session_state[f"lu_seq_prompt_{sequencing_type}"] = lu_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        lu_generate = st.button(
            "Generate",
            type="primary",
            use_container_width=True,
            key="lu_seq_gen",
        )
    with col_regen:
        lu_regenerate = st.button(
            "Regenerate",
            use_container_width=True,
            key="lu_seq_regen",
        )

    # --- Generation Logic ---
    if lu_generate or lu_regenerate:
        if not has_course_details:
            st.warning("Please enter course details first on the **Course Details** page.")
        elif not lu_learning_outcomes.strip():
            st.warning("Please enter the learning outcomes.")
        elif not lu_course_outline.strip():
            st.warning("Please enter the course outline.")
        else:
            with st.spinner(f"Generating {sequencing_type} sequencing rationale..."):
                try:
                    result = generate_lu_sequencing_rationale(
                        course=saved_title,
                        learning_outcomes=lu_learning_outcomes,
                        course_outline=lu_course_outline,
                        sequencing_type=sequencing_type,
                        prompt_template=st.session_state.get(f"lu_seq_prompt_{sequencing_type}"),
                    )
                    st.session_state["lu_seq_text"] = result
                except Exception as e:
                    st.error(f"Failed to generate rationale: {e}")

    # --- Display Result ---
    if st.session_state.get("lu_seq_text"):
        st.divider()
        st.markdown(f"**Generated Rationale ({st.session_state.get('lu_seq_type', 'Step by Step')} Sequencing):**")
        st.code(st.session_state["lu_seq_text"], language=None, wrap_lines=True)

# ============================================================
# PAGE: Course Validation
# ============================================================
elif active_page == "Course Validation":
    st.header("Course Validation")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        st.info(f"**Course:** {saved_title}")
    st.markdown(
        "AI will generate 5 distinct sets of survey responses covering "
        "performance gaps and how this WSQ course addresses training needs "
        "for your chosen industry."
    )

    # --- Industry input ---
    cv_industry = st.text_input(
        "Industry",
        placeholder="e.g. Healthcare, Logistics, Financial Services, Retail",
        key="cv_industry",
    )

    # --- Learning Outcomes input ---
    lo_default = st.session_state.get("lo_text", "")
    cv_learning_outcomes = st.text_area(
        "Learning Outcomes",
        value=lo_default,
        height=200,
        key="cv_lo",
        placeholder="Paste your learning outcomes here (e.g. from the Learning Outcomes page).",
    )

    # --- Editable prompt template ---
    with st.expander("Prompt Template", expanded=False):
        cv_prompt = st.text_area(
            "Edit the prompt template used for generation. "
            "Use `{course}`, `{industry}`, and `{learning_outcomes}` as placeholders.",
            value=st.session_state.get("cv_prompt", COURSE_VALIDATION_PROMPT_TEMPLATE),
            height=300,
            key="cv_prompt_input",
        )
        st.session_state["cv_prompt"] = cv_prompt

    # --- Generate Buttons ---
    col_gen, col_regen = st.columns([1, 1])
    with col_gen:
        cv_generate = st.button(
            "Generate",
            type="primary",
            use_container_width=True,
            key="cv_gen",
        )
    with col_regen:
        cv_regenerate = st.button(
            "Regenerate",
            use_container_width=True,
            key="cv_regen",
        )

    # --- Generation Logic ---
    if cv_generate or cv_regenerate:
        if not has_course_details:
            st.warning("Please enter course details first on the **Course Details** page.")
        elif not cv_industry.strip():
            st.warning("Please enter the industry.")
        elif not cv_learning_outcomes.strip():
            st.warning("Please enter the learning outcomes.")
        else:
            with st.spinner("Generating course validation responses..."):
                try:
                    result = generate_course_validation(
                        course=saved_title,
                        industry=cv_industry,
                        learning_outcomes=cv_learning_outcomes,
                        prompt_template=st.session_state.get("cv_prompt"),
                    )
                    st.session_state["cv_text"] = result
                except Exception as e:
                    st.error(f"Failed to generate validation: {e}")

    # --- Display Result ---
    if st.session_state.get("cv_text"):
        st.divider()
        st.markdown("**Generated Course Validation Responses:**")
        st.code(st.session_state["cv_text"], language=None, wrap_lines=True)
