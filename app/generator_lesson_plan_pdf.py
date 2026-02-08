from pathlib import Path

from fpdf import FPDF

from app.models import ExtractedData

HEADING_COLOR = (68, 114, 196)  # Steel blue matching DOCX template
DAY_START_MINUTES = 9 * 60
LUNCH_DURATION = 60
DAY_TOTAL_MINUTES = 480


def _fmt_time(minutes_from_midnight: int) -> str:
    h = minutes_from_midnight // 60
    m = minutes_from_midnight % 60
    if h > 12:
        h -= 12
    elif h == 0:
        h = 12
    return f"{h}:{m:02d}"


def _build_schedule(data: ExtractedData) -> dict[int, list[dict]]:
    topics_by_day: dict[int, list] = {}
    for lo in data.learning_outcomes:
        topics_by_day.setdefault(lo.day, []).append(lo)

    assess_by_day: dict[int, int] = {}
    for am in data.assessment_modes:
        assess_by_day[am.day] = assess_by_day.get(am.day, 0) + am.duration_minutes

    num_days = max(topics_by_day.keys()) if topics_by_day else 1
    schedule: dict[int, list[dict]] = {}

    for day in range(1, num_days + 1):
        slots: list[dict] = []
        topics = topics_by_day.get(day, [])
        assess_min = assess_by_day.get(day, 0)

        instruction_min = DAY_TOTAL_MINUTES - assess_min
        num_topics = len(topics)
        per_topic = instruction_min // num_topics if num_topics else 0

        current = DAY_START_MINUTES
        lunch_inserted = False

        for topic in topics:
            if not lunch_inserted and current >= 13 * 60 - 10:
                lunch_end = current + LUNCH_DURATION
                slots.append({
                    "start": _fmt_time(current),
                    "end": _fmt_time(lunch_end),
                    "label": "Lunch Break",
                })
                current = lunch_end
                lunch_inserted = True

            end = current + per_topic
            slots.append({
                "start": _fmt_time(current),
                "end": _fmt_time(end),
                "label": topic.topic,
            })
            current = end

        if not lunch_inserted and assess_min > 0:
            lunch_end = current + LUNCH_DURATION
            slots.append({
                "start": _fmt_time(current),
                "end": _fmt_time(lunch_end),
                "label": "Lunch Break",
            })
            current = lunch_end

        if assess_min > 0:
            end = current + assess_min
            slots.append({
                "start": _fmt_time(current),
                "end": _fmt_time(end),
                "label": "Assessment",
            })

        schedule[day] = slots

    return schedule


def _extract_overview(data: ExtractedData) -> str:
    text = data.particulars.about_course
    for para in text.split("\n"):
        stripped = para.strip()
        if not stripped:
            continue
        if len(stripped) < 80:
            continue
        if stripped.startswith("- "):
            continue
        return stripped
    return text[:500]


def generate_lesson_plan_pdf(data: ExtractedData, output_path: Path) -> Path:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    # --- Title ---
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"Lesson Plan: {data.particulars.course_title}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    # --- Metadata ---
    num_days = max(lo.day for lo in data.learning_outcomes) if data.learning_outcomes else 1
    unique_methods = list(dict.fromkeys(im.method for im in data.instruction_methods))

    training_hours = data.summary.total_instructional_duration
    assessment_hours = data.summary.total_assessment_duration

    pdf.set_font("Helvetica", "", 10)
    metadata_lines = [
        f"Course Duration: {num_days} Days (9:00 AM \u2013 6:00 PM daily)",
        f"Total Training Hours: {training_hours} (excluding lunch breaks)",
        f"Total Assessment Hours: {assessment_hours}",
        f"Instructional Methods: {', '.join(m.lower() for m in unique_methods)}",
    ]
    for line in metadata_lines:
        pdf.cell(0, 6, line, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # --- Course Overview ---
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(*HEADING_COLOR)
    pdf.cell(0, 8, "Course Overview", new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    overview_text = _extract_overview(data)
    pdf.multi_cell(0, 5, overview_text)
    pdf.ln(4)

    # --- Day schedules ---
    schedule = _build_schedule(data)

    for day_num in sorted(schedule.keys()):
        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(*HEADING_COLOR)
        pdf.cell(0, 8, f"Day {day_num}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(2)

        pdf.set_font("Helvetica", "", 10)
        for slot in schedule[day_num]:
            slot_text = f"{slot['start']} \u2013 {slot['end']}  |  {slot['label']}"
            pdf.cell(0, 6, slot_text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

    pdf.output(str(output_path))
    return output_path
