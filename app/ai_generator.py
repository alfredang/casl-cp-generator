import asyncio
import csv
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage

_SKILLS_CSV = Path(__file__).resolve().parent.parent / ".claude" / "skills" / "generate_topics" / "skills_description.csv"


def load_skills_data() -> tuple[list[str], dict[str, str]]:
    """Load skill names and descriptions from the CSV.

    Returns (names_list, descriptions_dict) where descriptions_dict maps
    skill name -> description.
    """
    names: list[str] = []
    descriptions: dict[str, str] = {}
    with open(_SKILLS_CSV, encoding="utf-8", errors="replace") as f:
        reader = csv.reader(f)
        next(reader)  # skip header row 1 (title)
        next(reader)  # skip header row 2 (S/N, Skill, Skills Description)
        for row in reader:
            if len(row) >= 3 and row[1].strip():
                name = row[1].strip()
                desc = row[2].strip()
                names.append(name)
                descriptions[name] = desc
    return names, descriptions

ABOUT_COURSE_PROMPT_TEMPLATE = """\
You are an expert course description writer for professional training and \
continuing education programmes. Write an "About the Course" section for \
the following course.

Course Title: {course_title}

Course Topics:
{course_topics}

Guidelines:
- Write in second person ("you") or third person ("learners", "professionals", \
"participants")
- Provide a clear overview of what the course covers
- Highlight practical benefits: skills gained, competencies developed, and \
professional needs the course addresses
- Explain industry relevance and career impact (employment opportunities, job \
upgrading, professional development)
- The target learner level is generally beginner to intermediate; reflect this \
in the description
- Keep the tone professional, engaging, and encouraging
- Write exactly ONE cohesive paragraph of 80-120 words
- Do NOT use bullet points, numbered lists, or headings
- Do NOT include the course title in the opening words; weave it in naturally \
or refer to "this course"
- Do NOT use markdown formatting
- IMPORTANT: The entire response must NOT exceed 2000 characters

Examples:

Example 1:
• This course is designed for professionals from a wide range of industries who \
want to learn how to apply the principles of design thinking to identify and solve \
complex problems. Whether you're a manager, team leader or individual \
contributor, this course will provide you with the tools and techniques you need \
to approach problems with a fresh perspective and come up with innovative \
solutions.

Example 2:
• Unlock the power of strategic marketing and sales expertise in our Sales and \
Marketing Mastery course. Ideal for marketers and sales professionals, learn \
to apply strategic principles, execute sales techniques, and interpret consumer \
behaviour data. Gain hands-on skills to create effective campaigns, engage \
customers, and drive sales growth.

Example 3:
• Designed for aspiring financial professionals, our finance course empowers you \
to analyse data, evaluate cost strategies, and monitor controls. Develop vital \
skills for making informed decisions that drive organisational success.

Respond with ONLY the paragraph text, nothing else."""


async def _generate_async(prompt_template: str, **format_kwargs: str) -> str:
    """Call Claude via the Agent SDK and return the generated text."""
    prompt = prompt_template.format(**format_kwargs)

    options = ClaudeAgentOptions(
        allowed_tools=[],
        max_turns=1,
    )

    result_text = ""
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    result_text += block.text
        elif isinstance(message, ResultMessage):
            if message.is_error:
                raise RuntimeError(
                    message.result or "Claude Agent SDK returned an error."
                )

    if not result_text.strip():
        raise RuntimeError("No text was generated. Please try again.")

    return result_text.strip()


def generate_about_course(course_title: str, course_topics: str, prompt_template: str | None = None) -> str:
    """Generate an 'About the Course' description using the Claude Agent SDK."""
    template = prompt_template or ABOUT_COURSE_PROMPT_TEMPLATE
    return asyncio.run(_generate_async(template, course_title=course_title, course_topics=course_topics))


WHAT_YOULL_LEARN_PROMPT_TEMPLATE = """\
You are an expert course description writer for professional training and \
continuing education programmes. Write a "What You'll Learn" section for \
the following course.

Course Title: {course_title}

Course Topics:
{course_topics}

Guidelines:
- Write one bullet point per major course topic or learning outcome
- Each bullet should describe a specific skill or knowledge the learner will gain
- Start each bullet with "Participants will" or "Learners will"
- Each bullet should be 40-60 words, written as a single cohesive sentence
- Include action verbs like: apply, analyse, demonstrate, evaluate, design, \
implement, interpret, develop, execute, monitor, assess
- Include keywords relevant to the course to help with search discoverability
- Describe practical, real-world application of the skills where possible
- Keep the tone professional, specific, and outcome-focused
- Write 3-5 bullet points depending on the number of topics
- Use a bullet character (•) at the start of each point
- Do NOT use markdown formatting, numbering, or headings
- Separate each bullet point with a blank line
- IMPORTANT: The entire response must NOT exceed 2000 characters

Examples of good "What You'll Learn" bullet points:

Example 1:
• Participants will be able to conduct user research and usability testing to \
identify user needs and preferences and use this information to design more \
user-friendly products and services.
• Participants will be able to apply the principles of design thinking to identify \
and solve complex problems in their work context.
• Participants will be able to implement agile methodologies to manage projects \
and teams more effectively, resulting in increased productivity and better \
outcomes.

Example 2:
• Learners will demonstrate their ability to apply strategic marketing principles \
by analysing market trends, identifying target segments, and developing \
effective marketing strategies. They will translate theoretical concepts into \
actionable plans that encompass product positioning, pricing, distribution, and \
promotion, showcasing their proficiency in devising comprehensive marketing \
campaigns.
• Learners will showcase their sales acumen by executing a variety of sales \
techniques such as consultative selling and objection handling. Through \
role-play scenarios, they will demonstrate their ability to adapt their approaches \
based on customer needs, effectively communicate product value, and \
navigate the sales process to achieve successful outcomes.
• Learners will interpret consumer behaviour data sourced from multiple \
touchpoints, such as CRM systems and e-commerce platforms. They will \
demonstrate their skills in translating raw data into meaningful insights, \
identifying trends, and presenting findings that guide marketing decisions \
aimed at enhancing customer experiences and driving sales growth.

Example 3:
• Learners will be able to analyse complex financial data, applying various ratios \
and metrics to assess the financial health of organizations. They will distinguish \
between liquidity, efficiency, and profitability ratios, examining how these \
indicators relate to a company's performance. Through real-world scenarios, \
they will critically evaluate financial statements, synthesise information, and \
justify their conclusions, demonstrating their ability to make informed \
assessments.
• Learners will demonstrate the skill to evaluate cost management strategies \
within businesses. They will appraise different cost structures, contrasting \
variable and fixed costs, and weigh the implications of various cost-cutting \
approaches. By examining case studies, they will critically judge the \
effectiveness of cost-saving measures, defend their recommended strategies, \
and provide evidence-based justifications for their choices.
• Learners will learn to monitor internal controls and assess potential risks \
within financial systems. They will facilitate the design and implementation \
of internal control mechanisms to detect and prevent fraud or errors. Through \
scenario analysis, they will detect vulnerabilities in financial processes, \
recommend improvements, and argue for the adoption of risk mitigation \
measures.

Respond with ONLY the bullet points, nothing else."""


def generate_what_youll_learn(course_title: str, course_topics: str, prompt_template: str | None = None) -> str:
    """Generate a 'What You'll Learn' section using the Claude Agent SDK."""
    template = prompt_template or WHAT_YOULL_LEARN_PROMPT_TEMPLATE
    return asyncio.run(_generate_async(template, course_title=course_title, course_topics=course_topics))


BACKGROUND_PART_A_PROMPT_TEMPLATE = """\
You are an expert course description writer for professional training and \
continuing education programmes. Write a "Background Part A" section for \
the following course. This section covers the targeted sector(s) background, \
target audience / job role(s), and needs for the training.

Course Title: {course_title}

Course Topics:
{course_topics}

Guidelines:
- Identify the specific industry sectors or domains that the course targets
- Describe the current pressures, trends, or challenges facing these sectors \
that create the need for this training
- Identify the target audience: specific job roles, professionals, or \
practitioners who would benefit
- Explain why there is a skills gap or training need in these sectors
- Write in a professional, factual tone suitable for a course proposal document
- Write 2-3 cohesive paragraphs totalling 100-200 words
- Do NOT use bullet points, numbered lists, or headings
- Do NOT use markdown formatting

Examples:

Example 1:
• This course is targeted at sectors that are significantly impacted by \
decarbonisation, sustainability, and ESG requirements, including but not \
limited to:
Manufacturing and Industrial Services
Energy and Utilities
Built Environment, Construction, and Facilities Management
Logistics, Transportation, and Supply Chain Management
Professional Services and Consulting
Financial Services and Corporate Functions supporting ESG reporting

These sectors face increasing pressure from regulatory requirements, corporate \
sustainability commitments, investor expectations, and customer demand to \
measure, manage, and reduce carbon emissions. As a result, there is a growing \
need for professionals who can support carbon accounting, emissions reduction \
planning, and decarbonisation strategy development.

Respond with ONLY the paragraph text, nothing else."""


def generate_background_part_a(course_title: str, course_topics: str, prompt_template: str | None = None) -> str:
    """Generate a 'Background Part A' section using the Claude Agent SDK."""
    template = prompt_template or BACKGROUND_PART_A_PROMPT_TEMPLATE
    return asyncio.run(_generate_async(template, course_title=course_title, course_topics=course_topics))


BACKGROUND_PART_B_PROMPT_TEMPLATE = """\
You are an expert course description writer for professional training and \
continuing education programmes. Write a "Background Part B" section for \
the following course. This section covers:
1. Performance gaps that the course will address
2. How the performance gaps were identified (e.g., market research, focus \
group discussions, surveys, Skills Frameworks, etc.)
3. How the attributes gained post training would benefit learners

Course Title: {course_title}

Course Topics:
{course_topics}

Guidelines:
- First paragraph: Describe the observable performance gaps in the workforce \
related to the course topics — what skills or competencies are lacking
- Second paragraph: Explain how these gaps were identified — reference \
specific methodologies such as Skills Frameworks (SFw), Singapore \
Jobs-Skills Portal, industry consultations, employer feedback, market \
research, focus groups, or surveys
- Third section: List 3-5 bullet points describing how learners will benefit \
post-training — each bullet should start with a verb phrase and describe \
a specific benefit (closing skills gaps, enhancing career readiness, \
improving performance, strengthening adaptability)
- Write in a professional, factual tone suitable for a course proposal document
- Use a dash (- ) at the start of each benefit bullet point
- Do NOT use markdown formatting or headings

Examples:

Example 1:
• Organisations across multiple sectors have been navigating rapid changes in \
business processes, technology integration, and performance expectations. \
While many professionals are familiar with routine operational tasks, there \
is an observable performance gap in strategic productivity and innovation \
capabilities—including the ability to systematically analyse productivity \
challenges, develop aligned strategies, and evaluate results effectively. \
Workers often lack structured skills in productivity management, innovation \
tools implementation, performance measurement, and continuous improvement \
frameworks, limiting their impact on organisational transformation initiatives.

These performance gaps have been identified through analysis of the Skills \
Frameworks (SFw) developed under the Singapore Jobs-Skills Portal. The \
Skills Frameworks map job roles with essential skills and competencies based \
on industry insights from employers, industry associations, professional \
bodies, and government partners. Analysis of this framework reveals that \
roles involved in operations, business improvement, and strategic leadership \
demand enhanced competencies in productivity strategy, innovation management, \
performance monitoring, and results evaluation to meet emerging job \
requirements and support organisational performance growth. The Skills \
Frameworks are updated regularly to reflect current and future skill needs \
across sectors, enabling training providers and learners to identify gaps \
between existing competencies and those required for career progression and \
business impact.

By attending this course, learners will benefit in several key ways:
- Close the skills gap in productivity strategy and innovation management \
by acquiring structured methodologies and tools that align with \
industry-recognised skills and competencies outlined in the Skills Frameworks.
- Enhance career readiness by gaining capabilities that are increasingly \
valued in roles related to productivity improvement, operations, and business \
transformation, improving prospects for job upgrading and broader career \
opportunities.
- Improve individual and organisational performance by learning how to \
implement frameworks that generate measurable outcomes, enabling learners \
to contribute to strategic decision-making, performance evaluation, and \
continuous improvement practices.
- Strengthen adaptability to workplace change by building confidence in \
applying productivity and innovation concepts to real organisational \
challenges, fostering both professional growth and organisational \
competitiveness.

Respond with ONLY the text, nothing else."""


def generate_background_part_b(course_title: str, course_topics: str, prompt_template: str | None = None) -> str:
    """Generate a 'Background Part B' section using the Claude Agent SDK."""
    template = prompt_template or BACKGROUND_PART_B_PROMPT_TEMPLATE
    return asyncio.run(_generate_async(template, course_title=course_title, course_topics=course_topics))


INSTRUCTION_METHOD_PROMPT_TEMPLATE = """\
You are an expert instructional designer for professional training and \
continuing education programmes. Write an elaboration on the appropriateness \
of the given instructional method to achieve the learning outcomes for the \
following course.

Course Title: {course_title}

Course Topics:
{course_topics}

Instructional Method: {method_name}

Guidelines:
- Explain why this instructional method is highly suitable for this course
- Describe how the method supports the learning of the specific course topics
- Reference adult learning principles where applicable
- Explain how the method enables learners to contextualise concepts and relate \
them to their own organisational challenges
- Describe how the method supports knowledge retention and practical application
- Explain how the method allows adaptation to different industries and job roles
- Write 4-5 cohesive paragraphs totalling 250-400 words
- Write in a professional, factual tone suitable for a course proposal document
- Do NOT use bullet points, numbered lists, or headings
- Do NOT use markdown formatting

Examples:

Example 1 (Interactive presentation):
• An interactive presentation approach is highly suitable for the Productivity \
and Innovation Strategy course as the subject matter requires learners to not \
only understand conceptual frameworks, but also to actively apply strategic \
thinking, analysis, and problem-solving skills in a workplace context. \
Productivity and innovation concepts are best learned through engagement, \
discussion, and practical reflection, rather than passive content delivery.

This course involves topics such as productivity strategy formulation, \
innovation tools, performance measurement, and continuous improvement systems, \
which benefit from two-way interaction between the trainer and learners. \
Through interactive presentations, learners are encouraged to participate in \
discussions, ask questions, share workplace experiences, and analyse real-world \
scenarios. This enables learners to contextualise abstract concepts and relate \
them directly to their own organisational challenges.

Interactive presentations also support adult learning principles, where working \
professionals bring prior experience and diverse perspectives to the learning \
environment. Activities such as guided discussions, scenario analysis, short \
exercises, and knowledge checks allow learners to validate their understanding, \
clarify misconceptions, and reinforce learning outcomes in real time. This \
approach enhances comprehension of complex productivity and innovation \
frameworks and improves knowledge retention.

In addition, productivity and innovation strategies often vary across industries \
and job roles. An interactive presentation format allows the trainer to adapt \
examples and discussions dynamically based on learners' sectors and roles, \
ensuring relevance and applicability. Learners gain exposure to different \
viewpoints and best practices, which supports cross-functional learning and \
innovation thinking.

Overall, the use of interactive presentation facilitates active engagement, \
practical understanding, and immediate application of productivity and \
innovation concepts, making it an effective and appropriate delivery mode for \
achieving the course learning outcomes and supporting learners' workplace \
performance.

Respond with ONLY the paragraph text, nothing else."""


ASSESSMENT_METHOD_PROMPT_TEMPLATE = """\
You are an expert instructional designer for professional training and \
continuing education programmes. Write an elaboration on the appropriateness \
of the given mode of assessment for the following course.

Course Title: {course_title}

Course Topics:
{course_topics}

Assessment Method: {method_name}

Guidelines:
- Explain why this assessment method is appropriate for evaluating learners' \
understanding and applied knowledge of the course topics
- Describe what the assessment enables learners to demonstrate (comprehension, \
application of frameworks, articulation of concepts)
- Explain why this format is suitable (structured evaluation, objectivity, \
consistency, fairness)
- Connect the assessment to the knowledge-based learning outcomes of the course
- Write 2-3 cohesive paragraphs totalling 100-200 words
- Write in a professional, factual tone suitable for a course proposal document
- Do NOT use bullet points, numbered lists, or headings
- Do NOT use markdown formatting

Examples:

Example 1 (Written Examination):
• The Written Examination is an appropriate assessment method for evaluating \
learners' theoretical understanding and applied knowledge of key productivity \
and innovation concepts covered in the Productivity and Innovation Strategy \
course. This assessment method enables learners to demonstrate their \
comprehension of productivity principles, innovation strategies, productivity \
management frameworks, continuous improvement concepts, and performance \
measurement systems, which are essential for effective decision-making and \
implementation in organisational contexts.

A written format is particularly suitable as it allows for structured and \
objective evaluation of learners' ability to explain concepts, apply recognised \
productivity and innovation frameworks, and articulate reasoned responses in a \
professional and systematic manner. This aligns with the knowledge-based \
learning outcomes of the course and ensures consistency and fairness in \
assessment across all learners.

Respond with ONLY the paragraph text, nothing else."""


MINIMUM_ENTRY_REQUIREMENT_PROMPT_TEMPLATE = """\
You are an expert course description writer for professional training and \
continuing education programmes. Write a "Minimum Entry Requirement" section \
for the following course.

Course Title: {course_title}

Course Topics:
{course_topics}
{special_requirements}
Guidelines:
- Structure the output into these categories: Knowledge and Skills, Attitude, \
Experience, and Target Age Group
- Under Knowledge and Skills: state educational qualifications (e.g., GCE 'O' \
Levels, diploma, degree) and any language proficiency requirements
- Under Attitude: describe the learning attitude expected of participants
- Under Experience: state the minimum years of working experience required
- Include a target age group (typically 21-65 years old)
- Use bullet points with a bullet character (•) for each requirement
- The target learner level is generally beginner to intermediate
- Write in a professional, factual tone suitable for a course proposal document
- Do NOT use markdown formatting or headings
- IMPORTANT: The entire response must NOT exceed 2000 characters

Examples:

Example 1:
Knowledge and Skills
• Able to operate using computer functions
• Minimum 3 GCE 'O' Levels Passes including English or WPL Level 5 \
(Average of Reading, Listening, Speaking & Writing Scores)
Attitude
• Positive Learning Attitude
• Enthusiastic Learner
Experience
• Minimum of 1 year of working experience

Target age group: 21-65 years old

Respond with ONLY the text, nothing else."""


def generate_minimum_entry_requirement(
    course_title: str,
    course_topics: str,
    prompt_template: str | None = None,
    special_requirements: str = "",
) -> str:
    """Generate a 'Minimum Entry Requirement' section using the Claude Agent SDK."""
    template = prompt_template or MINIMUM_ENTRY_REQUIREMENT_PROMPT_TEMPLATE
    if special_requirements.strip():
        special_req_text = (
            f"\nSpecial Requirements (MUST be reflected in the entry requirements):\n"
            f"{special_requirements.strip()}\n"
        )
    else:
        special_req_text = ""
    return asyncio.run(
        _generate_async(
            template,
            course_title=course_title,
            course_topics=course_topics,
            special_requirements=special_req_text,
        )
    )


LEARNING_OUTCOME_PROMPT_TEMPLATE = """\
You are an expert instructional designer for professional training and \
continuing education programmes. Generate learning outcomes for each \
topic of the following course.

Course Title: {course_title}

Course Topics:
{course_topics}

Guidelines:
- Generate exactly ONE learning outcome for EACH topic
- Each learning outcome MUST summarise the entire topic — it should capture \
the overall knowledge and skills covered in that topic in a single sentence
- Each learning outcome MUST start with an action verb (e.g., Apply, Analyse, \
Demonstrate, Evaluate, Design, Implement, Interpret, Develop, Execute, \
Monitor, Assess, Explain, Describe, Identify, Recognise, Differentiate)
- Each learning outcome MUST be less than 25 words
- Learning outcomes should be specific, measurable, and achievable
- Number topics as T1, T2, T3, etc.
- Number learning outcomes to match: T1 gets LO1, T2 gets LO2, etc.
- Use the exact format shown in the example below

Example:

T1: Business Innovation in the Age of Agentic AI
LO1: Explain core AI-driven business innovation concepts, Agentic AI characteristics, industry applications, and emerging opportunities for transformation.

T2: Agentic Vibe Coding for Business Innovation
LO2: Apply intent-driven coding approaches to design, build, and evaluate agentic solutions using low-code and no-code platforms.

T3: Agentic Workflow Design for Business Processes
LO3: Design agentic workflows by differentiating agent architectures, coordinating multi-agent collaboration, and integrating human-AI models.

T4: Building an Agentic AI Workforce
LO4: Develop an Agentic AI workforce strategy covering role-based design, team scaling, and performance monitoring approaches.

Respond with ONLY the formatted topics and learning outcomes, nothing else."""


def generate_learning_outcomes(
    course_title: str, course_topics: str, prompt_template: str | None = None
) -> str:
    """Generate learning outcomes for each topic using the Claude Agent SDK."""
    template = prompt_template or LEARNING_OUTCOME_PROMPT_TEMPLATE
    return asyncio.run(
        _generate_async(template, course_title=course_title, course_topics=course_topics)
    )


COURSE_TOPICS_PROMPT_TEMPLATE = """\
You are an expert curriculum designer for professional training and \
continuing education programmes. Generate a structured list of course \
topics with learning outcomes for the following course.

Course Title: {course_title}
Course Duration: {num_days} day(s)
Maximum Topics: {max_topics} (max 3 per day)
{skill_context}{special_requirements}
Guidelines:
- Generate the appropriate number of topics to comprehensively cover the \
subject matter{skill_guideline}
- You decide how many topics are needed — do NOT exceed {max_topics} topics \
(max 3 per day for {num_days} day(s))
- Each topic should represent a distinct, teachable module or unit
- Topics should follow a logical learning progression (foundational to advanced)
- Use concise, professional topic names (3-8 words each)
- Each topic must include 3-5 specific learning outcomes as bullet points
- Learning outcomes should start with action verbs (Explain, Describe, \
Identify, Recognise, Differentiate, Develop, Apply, Analyse, Evaluate)
- Topics should be suitable for WSQ/CASL course proposals
- Use the exact markdown format shown in the example below
- Use ## for topic headings with numbering (## Topic 1: ...)
- Use - for learning outcome bullet points
- Add two trailing spaces after each bullet point line for line breaks

Example (Course: Business Innovation with Agentic AI, 6 topics):

## Topic 1: Business Innovation in the Age of Agentic AI
- Explain the evolution of business innovation in relation to artificial intelligence
- Describe the key characteristics of Agentic AI
- Identify potential applications of Agentic AI across different industries
- Recognise opportunities for business innovation enabled by Agentic AI

## Topic 2: Agentic Vibe Coding for Business Innovation
- Describe the concept and purpose of Agentic Vibe Coding
- Explain intent-driven approaches to coding and system design
- Identify the roles, goals, and constraints of AI agents in business contexts
- Recognise the use of low-code and no-code platforms for agentic solutions

## Topic 3: Agentic Workflow Design for Business Processes
- Differentiate between single-agent and multi-agent systems
- Explain how agents collaborate and coordinate within workflows
- Identify business processes suitable for agentic workflow implementation
- Describe human-AI collaboration models within agentic systems

## Topic 4: Building an Agentic AI Workforce
- Explain the concept of AI agents as digital workers
- Identify role-based designs for an Agentic AI workforce
- Describe approaches to scaling agentic teams within organisations
- Explain methods for managing and monitoring AI workforce performance

## Topic 5: Governance, Risk, and Ethics in Agentic AI
- Explain governance frameworks applicable to Agentic AI systems
- Identify risks associated with autonomous and semi-autonomous AI systems
- Describe ethical considerations in the deployment of Agentic AI
- Recognise regulatory and compliance considerations relevant to Agentic AI

## Topic 6: Measuring Innovation and Business Impact
- Identify performance indicators for Agentic AI initiatives
- Explain methods for measuring business value and return on investment
- Describe change management considerations for AI adoption
- Develop a roadmap for enterprise-scale deployment of Agentic AI solutions

Respond with ONLY the formatted topics and learning outcomes, nothing else."""


def generate_course_topics(
    course_title: str,
    num_days: int,
    prompt_template: str | None = None,
    skill_description: str = "",
    special_requirements: str = "",
) -> str:
    """Generate course topics using the Claude Agent SDK.

    The AI decides the appropriate number of topics to cover the subject,
    constrained to max 3 topics per day.  When *skill_description* is
    provided (CASL mode), it is injected so topics align with the official
    CASL skill description.  *special_requirements* adds user-specified
    constraints to the prompt.
    """
    template = prompt_template or COURSE_TOPICS_PROMPT_TEMPLATE
    max_topics = num_days * 3
    if skill_description:
        skill_context = (
            f"\nCASL Skill Description (use this as context to generate relevant topics):\n"
            f"{skill_description}\n"
        )
        skill_guideline = " and the CASL skill description above"
    else:
        skill_context = ""
        skill_guideline = ""
    if special_requirements.strip():
        special_req_text = (
            f"\nSpecial Requirements (MUST be addressed in the topics):\n"
            f"{special_requirements.strip()}\n"
        )
    else:
        special_req_text = ""
    return asyncio.run(
        _generate_async(
            template,
            course_title=course_title,
            num_days=str(num_days),
            max_topics=str(max_topics),
            skill_context=skill_context,
            skill_guideline=skill_guideline,
            special_requirements=special_req_text,
        )
    )


JOB_ROLES_PROMPT_TEMPLATE = """\
You are an expert in Singapore's workforce development ecosystem. Generate \
10 relevant job roles for the following course. The job role names must follow \
the naming conventions used on the SSG Skills Framework and MySkillsFuture \
Jobs-Skills Portal.

Course Title: {course_title}

Course Topics:
{course_topics}

Guidelines:
- Generate exactly 10 job roles that are directly relevant to the course content
- Each job role name MUST follow the official naming used on the SSG \
Skills Framework / MySkillsFuture Jobs-Skills Portal
- Use the standard format: Job Title / Designation (e.g., "Marketing Manager", \
"Business Development Executive", "Digital Marketing Specialist")
- List all 10 job roles in a single comma-separated line
- Do NOT include descriptions, explanations, or numbering
- Do NOT use markdown formatting

Respond with ONLY the comma-separated job roles, nothing else."""


def generate_job_roles(
    course_title: str, course_topics: str, prompt_template: str | None = None
) -> str:
    """Generate job roles following SSG Skills Jobs portal naming."""
    template = prompt_template or JOB_ROLES_PROMPT_TEMPLATE
    return asyncio.run(
        _generate_async(template, course_title=course_title, course_topics=course_topics)
    )


LESSON_PLAN_PROMPT_TEMPLATE = """\
You are an expert instructional designer for professional training and \
continuing education programmes. Generate a detailed day-by-day lesson plan \
for the following course.

Course Title: {course_title}

Course Topics:
{course_topics}

Course Duration: {course_duration} hours ({num_days} day(s))
Instructional Duration: {instructional_duration} hours
Assessment Duration: {assessment_duration} hours
Instructional Methods: {instructional_methods}
Assessment Methods: {assessment_methods}

Guidelines:
- Create a day-by-day lesson plan with time slots from 9:00 AM to 6:00 PM
- Include a 1-hour lunch break (typically 1:00 PM - 2:00 PM)
- Distribute all topics across the available training days
- For each time slot, include:
  - Time range (e.g. 9:00 AM - 10:30 AM)
  - Topic/session name
  - Key learning points (2-3 bullet points)
  - Instructional method used for that session
- Include assessment sessions on the last day (or spread across days \
if assessment duration is significant)
- Use plain text format with clear headers for each day
- Use bullet points (•) for learning points within each session
- Separate each day with a blank line
- Do NOT use markdown formatting (no #, **, etc.)
- IMPORTANT: Ensure all topics from the course are covered

Example format:

Day 1 (9:00 AM - 6:00 PM)

9:00 AM - 10:30 AM | Topic 1: Introduction to Business Innovation
• Explain the evolution of business innovation
• Describe key characteristics and applications
• Identify opportunities for transformation
Instructional Method: Interactive presentation

10:30 AM - 12:30 PM | Topic 2: Agentic Vibe Coding
• Apply intent-driven coding approaches
• Design agentic solutions using low-code platforms
• Evaluate agent performance metrics
Instructional Method: Demonstrations / Modelling

12:30 PM - 1:30 PM | Lunch Break

1:30 PM - 3:30 PM | Topic 3: Workflow Design
• Differentiate between agent architectures
• Coordinate multi-agent collaboration
• Integrate human-AI models
Instructional Method: Case studies

3:30 PM - 5:00 PM | Topic 4: Building AI Workforce
• Explain role-based designs for AI workforce
• Describe approaches to scaling agentic teams
• Monitor AI workforce performance
Instructional Method: Discussions

5:00 PM - 6:00 PM | Assessment
• Written Examination covering Day 1 topics
Assessment Method: Written Exam

Respond with ONLY the lesson plan text, nothing else."""


def generate_lesson_plan_content(
    course_title: str,
    course_topics: str,
    course_duration: int,
    instructional_duration: int,
    assessment_duration: int,
    instructional_methods: list[str],
    assessment_methods: list[str],
    prompt_template: str | None = None,
) -> str:
    """Generate a lesson plan using the Claude Agent SDK."""
    template = prompt_template or LESSON_PLAN_PROMPT_TEMPLATE
    num_days = max(1, course_duration // 8)
    return asyncio.run(
        _generate_async(
            template,
            course_title=course_title,
            course_topics=course_topics,
            course_duration=str(course_duration),
            num_days=str(num_days),
            instructional_duration=str(instructional_duration),
            assessment_duration=str(assessment_duration),
            instructional_methods=", ".join(instructional_methods),
            assessment_methods=", ".join(assessment_methods),
        )
    )


COURSE_TITLE_SUGGESTIONS_PROMPT_TEMPLATE = """\
You are an expert course naming strategist for professional training and \
continuing education programmes. Brainstorm 20 course titles for the \
following course topic.

Course Topic: {course}

Guidelines:
- Generate exactly 20 course titles
- Titles should be appealing and engaging for potential learners
- Titles should be optimized for search engine visibility (SEO-friendly)
- Include relevant keywords that learners would search for
- Mix different title styles: descriptive, action-oriented, outcome-focused, \
and benefit-driven
- Titles should be concise (3-10 words each)
- Titles should sound professional and suitable for WSQ/CASL course listings
- Number each title from 1 to 20
- Do NOT use markdown formatting
- Do NOT include descriptions or explanations — titles only

Example (Course Topic: Digital Marketing):

1. Digital Marketing Essentials
2. Mastering Digital Marketing Strategies
3. Digital Marketing for Business Growth
4. Strategic Digital Marketing and Analytics
5. Digital Marketing Campaign Management
6. Online Marketing and Social Media Mastery
7. Data-Driven Digital Marketing
8. Digital Marketing in the Age of AI
9. Fundamentals of Digital Marketing
10. Digital Marketing and Brand Strategy
11. Advanced Digital Marketing Techniques
12. Digital Marketing for Professionals
13. Effective Digital Marketing Campaigns
14. Digital Marketing and Customer Engagement
15. Modern Digital Marketing Practices
16. Digital Marketing Strategy and Execution
17. Applied Digital Marketing Skills
18. Digital Marketing and E-Commerce
19. Digital Marketing for Career Advancement
20. Integrated Digital Marketing Solutions

Respond with ONLY the numbered list of titles, nothing else."""


def generate_course_title_suggestions(
    course: str, prompt_template: str | None = None
) -> str:
    """Generate 20 course title suggestions using the Claude Agent SDK."""
    template = prompt_template or COURSE_TITLE_SUGGESTIONS_PROMPT_TEMPLATE
    return asyncio.run(_generate_async(template, course=course))


LU_SEQUENCING_TYPES = [
    "Step by Step",
    "Simple to Complex",
    "Part to Part to Part",
    "Part to Whole",
    "Spiral",
]

LU_SEQUENCING_STEP_BY_STEP_TEMPLATE = """\
Ignore all the previous instructions and start from beginning.
You are an experienced course developer and instructional designer.

Course Title: {course}

Learning Outcomes:
{learning_outcomes}

Course Outline:
{course_outline}

TASK:
You will need to justify the rationale of sequencing using step-by-step \
curriculum framework for this course - {course}
Your justification based on the course outline and learning outcomes.

OUTPUT FORMAT:
Output your response in the following format with reference to the \
learning outcomes and course outline. For example:

For this course, the step-by-step sequencing is employed to scaffold \
the learners' comprehension and application of video marketing strategies \
using AI tools. The methodology is crucial as it systematically breaks \
down the intricate facets of video marketing, inbound marketing strategies, \
and AI tools into digestible units. This aids in gradually building the \
learners' knowledge and skills from fundamental to more complex concepts, \
ensuring a solid foundation before advancing to the next topic. The \
progression is designed to foster a deeper understanding and the ability \
to effectively apply the learned concepts in real-world marketing scenarios.

LU1: Translating Strategy into Action and Fostering a Customer-Centric Culture
LU1 lays the foundational knowledge by introducing learners to the \
organization's inbound marketing strategies and how they align with the \
overall marketing strategy. The facilitator will guide learners through \
translating these strategies into actionable plans and understanding the \
customer decision journey. This unit sets the stage for fostering a \
customer-centric culture with a particular focus on adhering to \
organizational policies and guidelines. The integration of AI tools in \
these processes is introduced, giving learners a glimpse into the \
technological aspects they will delve deeper into in subsequent units.

LU2: Improving Inbound Marketing Strategies and Content Management
Building on the foundational knowledge, LU2 dives into the practical \
aspects of content creation and curation and how AI tools can be utilized \
for strategy improvement. Learners will be led through exercises to \
recommend improvements and manage content across various platforms. The \
hands-on activities in this unit are designed to enhance learners' ability \
to manage and optimize video content, crucial skills in video marketing \
with AI tools.

LU3: Leading Customer Decision Processes and Monitoring Inbound Marketing \
Effectiveness
LU3 escalates to a higher level of complexity where learners delve into \
lead conversion processes, leading customers through decision processes, \
and evaluating marketing strategy effectiveness. Under the guidance of the \
facilitator, learners will engage in monitoring and reviewing inbound \
marketing strategies, thereby aligning theoretical knowledge with practical \
skills in a real-world context. The synthesis of previous knowledge with \
advanced concepts in this unit culminates in a comprehensive understanding \
of video marketing with AI tools, equipping learners with the requisite \
skills to excel in the modern marketing landscape.

Respond with ONLY the rationale text, nothing else."""

LU_SEQUENCING_SIMPLE_TO_COMPLEX_TEMPLATE = """\
Ignore all the previous instructions and start from beginning.
You are an experienced course developer and instructional designer.

Course Title: {course}

Learning Outcomes:
{learning_outcomes}

Course Outline:
{course_outline}

TASK:
You will need to justify the rationale of sequencing using simple-to-complex \
curriculum framework for this course - {course}
Your justification based on the course outline and learning outcomes.

OUTPUT FORMAT:
Output your response in the following format with reference to the \
learning outcomes and course outline. Start with an introductory paragraph \
explaining why simple-to-complex sequencing is appropriate for this course, \
then provide a justification for each Learning Unit (LU) showing how it \
progresses from simpler to more complex concepts.

Respond with ONLY the rationale text, nothing else."""

LU_SEQUENCING_PART_TO_PART_TEMPLATE = """\
Ignore all the previous instructions and start from beginning.
You are an experienced course developer and instructional designer.

Course Title: {course}

Learning Outcomes:
{learning_outcomes}

Course Outline:
{course_outline}

TASK:
You will need to justify the rationale of sequencing using part-to-part-to-part \
curriculum framework for this course - {course}
Your justification based on the course outline and learning outcomes.

OUTPUT FORMAT:
Output your response in the following format with reference to the \
learning outcomes and course outline. Start with an introductory paragraph \
explaining why part-to-part-to-part sequencing is appropriate for this \
course, then provide a justification for each Learning Unit (LU) showing \
how each part builds upon and connects to the other parts as distinct but \
interrelated components.

Respond with ONLY the rationale text, nothing else."""

LU_SEQUENCING_PART_TO_WHOLE_TEMPLATE = """\
Ignore all the previous instructions and start from beginning.
You are an experienced course developer and instructional designer.

Course Title: {course}

Learning Outcomes:
{learning_outcomes}

Course Outline:
{course_outline}

TASK:
You will need to justify the rationale of sequencing using part-to-whole \
framework for this course - {course}
Your justification based on the course outline and learning outcomes.

OUTPUT FORMAT:
Output your response in the following format with reference to the \
learning outcomes and course outline. For example:

For this course, the part-to-whole sequencing is employed to scaffold \
the learners' comprehension and application of video marketing strategies \
using AI tools. The methodology is crucial as it systematically breaks \
down the intricate facets of video marketing, inbound marketing strategies, \
and AI tools into digestible units. This aids in gradually building the \
learners' knowledge and skills from fundamental to more complex concepts, \
ensuring a solid foundation before advancing to the next topic. The \
progression is designed to foster a deeper understanding and the ability \
to effectively apply the learned concepts in real-world marketing scenarios.

LU1: Translating Strategy into Action and Fostering a Customer-Centric Culture
LU1 lays the foundational knowledge by introducing learners to the \
organization's inbound marketing strategies and how they align with the \
overall marketing strategy. The facilitator will guide learners through \
translating these strategies into actionable plans and understanding the \
customer decision journey. This unit sets the stage for fostering a \
customer-centric culture with a particular focus on adhering to \
organizational policies and guidelines. The integration of AI tools in \
these processes is introduced, giving learners a glimpse into the \
technological aspects they will delve deeper into in subsequent units.

LU2: Improving Inbound Marketing Strategies and Content Management
Building on the foundational knowledge, LU2 dives into the practical \
aspects of content creation and curation and how AI tools can be utilized \
for strategy improvement. Learners will be led through exercises to \
recommend improvements and manage content across various platforms. The \
hands-on activities in this unit are designed to enhance learners' ability \
to manage and optimize video content, crucial skills in video marketing \
with AI tools.

LU3: Leading Customer Decision Processes and Monitoring Inbound Marketing \
Effectiveness
LU3 escalates to a higher level of complexity where learners delve into \
lead conversion processes, leading customers through decision processes, \
and evaluating marketing strategy effectiveness. Under the guidance of the \
facilitator, learners will engage in monitoring and reviewing inbound \
marketing strategies, thereby aligning theoretical knowledge with practical \
skills in a real-world context. The synthesis of previous knowledge with \
advanced concepts in this unit culminates in a comprehensive understanding \
of video marketing with AI tools, equipping learners with the requisite \
skills to excel in the modern marketing landscape.

Respond with ONLY the rationale text, nothing else."""

LU_SEQUENCING_SPIRAL_TEMPLATE = """\
Ignore all the previous instructions and start from beginning.
You are an experienced course developer and instructional designer.

Course Title: {course}

Learning Outcomes:
{learning_outcomes}

Course Outline:
{course_outline}

TASK:
You will need to justify the rationale of sequencing using spiral \
curriculum framework for this course - {course}
Your justification based on the course outline and learning outcomes.

OUTPUT FORMAT:
Output your response in the following format with reference to the \
learning outcomes and course outline. Start with an introductory paragraph \
explaining why spiral sequencing is appropriate for this course, then \
provide a justification for each Learning Unit (LU) showing how key \
concepts are revisited at increasing levels of depth and complexity \
throughout the course.

Respond with ONLY the rationale text, nothing else."""

LU_SEQUENCING_TEMPLATES = {
    "Step by Step": LU_SEQUENCING_STEP_BY_STEP_TEMPLATE,
    "Simple to Complex": LU_SEQUENCING_SIMPLE_TO_COMPLEX_TEMPLATE,
    "Part to Part to Part": LU_SEQUENCING_PART_TO_PART_TEMPLATE,
    "Part to Whole": LU_SEQUENCING_PART_TO_WHOLE_TEMPLATE,
    "Spiral": LU_SEQUENCING_SPIRAL_TEMPLATE,
}


def generate_lu_sequencing_rationale(
    course: str,
    learning_outcomes: str,
    course_outline: str,
    sequencing_type: str,
    prompt_template: str | None = None,
) -> str:
    """Generate a rationale for LU sequencing using the Claude Agent SDK."""
    template = prompt_template or LU_SEQUENCING_TEMPLATES.get(
        sequencing_type, LU_SEQUENCING_STEP_BY_STEP_TEMPLATE
    )
    return asyncio.run(
        _generate_async(
            template,
            course=course,
            learning_outcomes=learning_outcomes,
            course_outline=course_outline,
        )
    )


COURSE_VALIDATION_PROMPT_TEMPLATE = """\
As a director in a company, your role is to assist users in determining \
the relevance and potential impact of various courses for specific industries.

Course Title: {course}
Industry: {industry}
Learning Outcomes:
{learning_outcomes}

TASKS:
You will generate FIVE distinct responses to two survey questions:
1. What are the performance gaps in the industry (1-2 paragraphs are sufficed)
2. Why you think this WSQ course will address the training needs for the \
industry (1-2 paragraphs are sufficed)

RULES:
1. Do not mention learning outcomes in the response.
2. Do not mention you are the director
3. Do not mention the specific industry by name
4. 1 or 2 paragraphs answers for each question in the survey
5. Each paragraph is less than 120 words
6. Only consider 1 or 2 of the learning outcomes for your response.
7. The response need to related to the course, industry and learning outcomes
8. For each set of response, you will generate the responses use different \
learning outcomes and different style.

OUTPUT FORMAT:
For each set, use the following format:

Set 1:
1. What are the performance gaps in the industry (1-2 paragraphs are sufficed)

(Enter your answer here)

2. Why you think this WSQ course will address the training needs for the \
industry (1-2 paragraphs are sufficed)

(Enter your answer here)

Set 2:
...

You will generate FIVE distinct sets of responses for the survey above.

Respond with ONLY the five sets of responses, nothing else."""


def generate_course_validation(
    course: str,
    industry: str,
    learning_outcomes: str,
    prompt_template: str | None = None,
) -> str:
    """Generate course validation survey responses using the Claude Agent SDK."""
    template = prompt_template or COURSE_VALIDATION_PROMPT_TEMPLATE
    return asyncio.run(
        _generate_async(
            template,
            course=course,
            industry=industry,
            learning_outcomes=learning_outcomes,
        )
    )


UNIQUE_SKILL_NAMES_LIST, SKILL_DESCRIPTIONS = load_skills_data()



INSTRUCTION_METHODS_LIST = [
    "Brainstorming",
    "Case studies",
    "Concept formation",
    "Debates",
    "Demonstrations / Modelling",
    "Didactic questions",
    "Discussions",
    "Drill and Practice",
    "Experiments",
    "Explicit teaching (Lecture) & Homework",
    "Field trips",
    "Games",
    "Independent reading",
    "Interactive presentation",
    "Peer teaching / Peer practice",
    "Problem solving",
    "Reflection",
    "Role-play",
    "Simulations",
]

ASSESSMENT_METHODS_LIST = [
    "Written Exam",
    "Online Test",
    "Project",
    "Assignments",
    "Oral Interview",
    "Demonstration",
    "Practical Exam",
    "Role Play",
    "Oral Questioning",
    "Others: Case Studies",
    "Others: Reflection",
]


def generate_instruction_method(
    course_title: str, course_topics: str, method_name: str, prompt_template: str | None = None
) -> str:
    """Generate an appropriateness elaboration for an instructional method."""
    template = prompt_template or INSTRUCTION_METHOD_PROMPT_TEMPLATE
    return asyncio.run(
        _generate_async(template, course_title=course_title, course_topics=course_topics, method_name=method_name)
    )


def generate_assessment_method(
    course_title: str, course_topics: str, method_name: str, prompt_template: str | None = None
) -> str:
    """Generate an appropriateness elaboration for an assessment method."""
    template = prompt_template or ASSESSMENT_METHOD_PROMPT_TEMPLATE
    return asyncio.run(
        _generate_async(template, course_title=course_title, course_topics=course_topics, method_name=method_name)
    )
