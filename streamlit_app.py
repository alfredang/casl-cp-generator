import tempfile
from pathlib import Path

import streamlit as st

from app.ai_generator import (
    ABOUT_COURSE_PROMPT_TEMPLATE,
    ASSESSMENT_METHOD_PROMPT_TEMPLATE,
    ASSESSMENT_METHODS_LIST,
    BACKGROUND_PART_A_PROMPT_TEMPLATE,
    BACKGROUND_PART_B_PROMPT_TEMPLATE,
    INSTRUCTION_METHOD_PROMPT_TEMPLATE,
    INSTRUCTION_METHODS_LIST,
    WHAT_YOULL_LEARN_PROMPT_TEMPLATE,
    generate_about_course,
    generate_assessment_method,
    generate_background_part_a,
    generate_background_part_b,
    generate_instruction_method,
    generate_what_youll_learn,
)
from app.extractor import extract_data
from app.generator_docx import generate_docx
from app.generator_lesson_plan import generate_lesson_plan

st.set_page_config(page_title="CASL Course Document Generator", page_icon="📄", layout="wide")

# --- Sidebar Navigation ---
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Course Details"

with st.sidebar:
    st.title("CASL")

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
    if st.button("Instruction Methods", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Instruction Methods" else "secondary"):
        st.session_state["active_page"] = "Instruction Methods"
        st.rerun()
    if st.button("Assessment Methods", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Assessment Methods" else "secondary"):
        st.session_state["active_page"] = "Assessment Methods"
        st.rerun()

    st.markdown("---")
    st.caption("SUBMIT CP")
    if st.button("Lesson Plan", use_container_width=True,
                 type="primary" if st.session_state["active_page"] == "Lesson Plan" else "secondary"):
        st.session_state["active_page"] = "Lesson Plan"
        st.rerun()

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

    with st.form("course_details_form"):
        course_title = st.text_input(
            "Course Title",
            value=saved_title,
            placeholder="e.g. Sales and Marketing Mastery",
        )
        course_topics = st.text_area(
            "Course Topics",
            value=saved_topics,
            placeholder=(
                "e.g. Strategic marketing principles, Consumer behaviour analysis, "
                "Digital marketing channels, Sales pipeline management, Negotiation techniques"
            ),
            height=150,
        )
        col_dur, col_topics = st.columns(2)
        with col_dur:
            course_duration = st.number_input(
                "Course Duration (hrs)",
                min_value=1,
                value=st.session_state.get("saved_course_duration", 8),
                step=1,
            )
        with col_topics:
            num_topics = st.number_input(
                "# of Topics",
                min_value=1,
                value=st.session_state.get("saved_num_topics", 3),
                step=1,
            )
        col_instr, col_assess = st.columns(2)
        with col_instr:
            instructional_duration = st.number_input(
                "Instructional Duration (hrs)",
                min_value=1,
                value=st.session_state.get("saved_instructional_duration", 7),
                step=1,
            )
        with col_assess:
            assessment_duration = st.number_input(
                "Assessment Duration (hrs)",
                min_value=1,
                value=st.session_state.get("saved_assessment_duration", 1),
                step=1,
            )
        col_num_instr, col_num_assess = st.columns(2)
        with col_num_instr:
            num_instr_methods = st.number_input(
                "# of Instruction Methods",
                min_value=1,
                value=st.session_state.get("saved_num_instr_methods", 3),
                step=1,
            )
        with col_num_assess:
            num_assess_methods = st.number_input(
                "# of Assessment Methods",
                min_value=1,
                value=st.session_state.get("saved_num_assess_methods", 1),
                step=1,
            )
        selected_instr_methods = st.multiselect(
            "Select Instruction Methods",
            options=INSTRUCTION_METHODS_LIST,
            default=st.session_state.get("saved_instr_methods", []),
        )
        selected_assess_methods = st.multiselect(
            "Select Assessment Methods",
            options=ASSESSMENT_METHODS_LIST,
            default=st.session_state.get("saved_assess_methods", []),
        )
        submitted = st.form_submit_button("Save Course Details", type="primary", use_container_width=True)

    if submitted:
        if not course_title or not course_topics:
            st.warning("Please enter both a course title and course topics.")
        elif len(selected_instr_methods) != num_instr_methods:
            st.warning(f"Please select exactly {num_instr_methods} instruction method(s). You selected {len(selected_instr_methods)}.")
        elif len(selected_assess_methods) != num_assess_methods:
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
            st.session_state["saved_assess_methods"] = selected_assess_methods
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
        instr_per_method = saved_instr * 60 / saved_num_instr
        assess_per_method = saved_assess * 60 / saved_num_assess

        st.divider()
        st.markdown(f"## {saved_title}")

        summary_data = {
            "Field": [
                "Course Duration",
                "Number of Topics",
                "Duration per Topic",
                "Instructional Duration",
                "Instructional per Topic",
                "# Instruction Methods",
                "Duration per Instruction Method",
                "Assessment Duration",
                "Assessment per Topic",
                "# Assessment Methods",
                "Duration per Assessment Method",
            ],
            "Value": [
                f"{saved_duration} hrs",
                str(saved_num_topics),
                f"{duration_per_topic:.0f} mins",
                f"{saved_instr} hrs",
                f"{instr_per_topic:.0f} mins",
                str(saved_num_instr),
                f"{instr_per_method:.0f} mins",
                f"{saved_assess} hrs",
                f"{assess_per_topic:.0f} mins",
                str(saved_num_assess),
                f"{assess_per_method:.0f} mins",
            ],
        }
        st.dataframe(summary_data, use_container_width=True, hide_index=True)

        saved_im = st.session_state.get("saved_instr_methods", [])
        saved_am = st.session_state.get("saved_assess_methods", [])
        if saved_im:
            st.markdown(f"**Instruction Methods:** {', '.join(saved_im)}")
        if saved_am:
            st.markdown(f"**Assessment Methods:** {', '.join(saved_am)}")

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
# PAGE: Instruction Methods
# ============================================================
elif active_page == "Instruction Methods":
    st.header("Instruction Methods")

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        saved_im = st.session_state.get("saved_instr_methods", [])
        if not saved_im:
            st.warning("Please select instruction methods on the **Course Details** page first.")
        else:
            st.info(f"**Course:** {saved_title}")
            st.markdown(
                "AI will generate an elaboration on the appropriateness of each "
                "selected instructional method for achieving the course learning outcomes."
            )
            st.markdown(f"**Selected Methods:** {', '.join(saved_im)}")

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

    if not has_course_details:
        st.warning("Please enter course details first on the **Course Details** page.")
    else:
        saved_am = st.session_state.get("saved_assess_methods", [])
        if not saved_am:
            st.warning("Please select assessment methods on the **Course Details** page first.")
        else:
            st.info(f"**Course:** {saved_title}")
            st.markdown(
                "AI will generate an elaboration on the appropriateness of each "
                "selected assessment method for this course."
            )
            st.markdown(f"**Selected Methods:** {', '.join(saved_am)}")

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
# PAGE: Lesson Plan
# ============================================================
elif active_page == "Lesson Plan":
    st.header("Lesson Plan")
    st.markdown("Upload a Course Planning Excel file to generate **Course Document** and **Lesson Plan** documents.")

    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"], help="Select the .xlsx course planning file")

    if uploaded_file is not None:
        st.success(f"**{uploaded_file.name}** uploaded ({uploaded_file.size / 1024:.0f} KB)")

        if st.button("Generate Documents", type="primary", use_container_width=True):
            with st.spinner("Extracting data and generating documents..."):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    tmp_path = Path(tmp_dir) / uploaded_file.name
                    tmp_path.write_bytes(uploaded_file.getvalue())

                    data = extract_data(tmp_path)

                    docx_path = Path(tmp_dir) / "output.docx"
                    generate_docx(data, docx_path)
                    docx_bytes = docx_path.read_bytes()

                    lp_path = Path(tmp_dir) / "lesson_plan.docx"
                    generate_lesson_plan(data, lp_path)
                    lp_bytes = lp_path.read_bytes()

                safe_name = data.particulars.course_title.replace(" ", "_")

                st.session_state["generated"] = True
                st.session_state["docx_bytes"] = docx_bytes
                st.session_state["lp_bytes"] = lp_bytes
                st.session_state["safe_name"] = safe_name
                st.session_state["data"] = data

        # --- Show results if generated ---
        if st.session_state.get("generated"):
            data = st.session_state["data"]
            safe_name = st.session_state["safe_name"]
            docx_bytes = st.session_state["docx_bytes"]
            lp_bytes = st.session_state["lp_bytes"]

            st.divider()
            st.subheader("Downloads")

            col1, col2 = st.columns(2)
            with col1:
                st.download_button(
                    label="Download Course Document (.docx)",
                    data=docx_bytes,
                    file_name=f"{safe_name}.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            with col2:
                st.download_button(
                    label="Download Lesson Plan (.docx)",
                    data=lp_bytes,
                    file_name=f"{safe_name}_Lesson_Plan.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )

            # --- Preview extracted data ---
            st.divider()
            st.subheader("Extracted Data Preview")

            with st.expander("Section 1: Course Particulars", expanded=True):
                st.markdown(f"**Training Provider:** {data.particulars.training_provider}")
                st.markdown(f"**Course Title:** {data.particulars.course_title}")
                st.markdown(f"**Course Type:** {data.particulars.course_type}")
                st.markdown(f"**Unique Skill:** {', '.join(data.particulars.unique_skill_names)}")
                st.markdown("---")
                st.markdown("**About This Course**")
                st.text(data.particulars.about_course[:500] + ("..." if len(data.particulars.about_course) > 500 else ""))
                st.markdown("**What You Will Learn**")
                st.text(data.particulars.what_youll_learn[:500] + ("..." if len(data.particulars.what_youll_learn) > 500 else ""))

            with st.expander("Section 2: Course Background"):
                st.text(data.background.targeted_sectors[:500] + ("..." if len(data.background.targeted_sectors) > 500 else ""))

            with st.expander("Section 3: Instructional Design"):
                st.markdown("**Learning Outcomes**")
                lo_rows = [
                    {
                        "Day": lo.day,
                        "Duration (min)": lo.duration_minutes,
                        "LO#": lo.lo_number,
                        "Learning Outcome": lo.learning_outcome,
                        "Topic": lo.topic,
                    }
                    for lo in data.learning_outcomes
                ]
                st.dataframe(lo_rows, use_container_width=True, hide_index=True)

                st.markdown("**Instruction Methods**")
                meth_rows = [
                    {
                        "Day": im.day,
                        "Method": im.method,
                        "Duration (min)": im.duration_minutes,
                        "Mode": im.mode_of_training,
                    }
                    for im in data.instruction_methods
                ]
                st.dataframe(meth_rows, use_container_width=True, hide_index=True)

            with st.expander("Section 4: Assessment"):
                assess_rows = [
                    {
                        "Day": am.day,
                        "Mode": am.mode,
                        "Duration (min)": am.duration_minutes,
                        "Assessors": am.num_assessors,
                        "Candidates": am.num_candidates,
                    }
                    for am in data.assessment_modes
                ]
                st.dataframe(assess_rows, use_container_width=True, hide_index=True)

            with st.expander("Summary"):
                st.markdown("**Topics covered in this course:**")
                for lo in data.learning_outcomes:
                    st.markdown(f"- {lo.topic}")

                st.markdown("")
                unique_methods = list(dict.fromkeys(im.method for im in data.instruction_methods))
                st.markdown(f"**Instructional methods:** {', '.join(unique_methods)}")

                st.markdown("")
                st.markdown("**Duration for each topic:**")
                dur_rows = [{"Topic": lo.topic, "Duration (min)": lo.duration_minutes} for lo in data.learning_outcomes]
                st.dataframe(dur_rows, use_container_width=True, hide_index=True)

                st.markdown("")
                st.markdown(f"- **Total Course Duration:** {data.summary.total_course_duration}")
                st.markdown(f"- **Total Instructional Duration:** {data.summary.total_instructional_duration}")
                st.markdown(f"- **Total Assessment Duration:** {data.summary.total_assessment_duration}")
                st.markdown(f"- **Mode of Training:** {data.summary.mode_of_training}")
