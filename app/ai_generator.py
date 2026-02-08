import asyncio

from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage

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
    course_title: str, course_topics: str, prompt_template: str | None = None
) -> str:
    """Generate a 'Minimum Entry Requirement' section using the Claude Agent SDK."""
    template = prompt_template or MINIMUM_ENTRY_REQUIREMENT_PROMPT_TEMPLATE
    return asyncio.run(
        _generate_async(template, course_title=course_title, course_topics=course_topics)
    )


COURSE_TOPICS_PROMPT_TEMPLATE = """\
You are an expert curriculum designer for professional training and \
continuing education programmes. Generate a structured list of course \
topics with learning outcomes for the following course.

Course Title: {course_title}
Number of Topics: {num_topics}

Guidelines:
- Generate exactly {num_topics} course topics that are directly relevant \
to the course title
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
    course_title: str, num_topics: int, prompt_template: str | None = None
) -> str:
    """Generate course topics using the Claude Agent SDK."""
    template = prompt_template or COURSE_TOPICS_PROMPT_TEMPLATE
    return asyncio.run(
        _generate_async(template, course_title=course_title, num_topics=str(num_topics))
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


UNIQUE_SKILL_NAMES_LIST = [
    "Accident and Incident Response Management",
    "Agile Coaching",
    "Ambulance Readiness and Maintenance",
    "Analytical Method Validation",
    "Arrestation",
    "Artificial Intelligence Ethics and Governance",
    "Arts Curriculum Design",
    "Attractions Content and Experience Development and Delivery",
    "Attractions Guest Relations Management",
    "Attractions Membership, Admission and Ticketing Management",
    "Audio Programming",
    "Audit Compliance",
    "Audit Frameworks",
    "Auditing and Assurance Standards",
    "Auditor Independence",
    "Ballast System Design",
    "Behavioural Economics in Design",
    "Billing Procedure",
    "Bulk Cargo Operations",
    "Bus Fare Management",
    "Bus Garaging",
    "Business Innovation and Improvement",
    "Business Requirements Mapping",
    "Call Centre Management",
    "Cargo and Receipt Inspection",
    "Cargo Issuance and Dispatch",
    "Case and Care Planning",
    "Casework Evaluation",
    "Category Management",
    "Category Marketing",
    "Channel Management",
    "Civil Structure Maintenance",
    "Client Assessment for Occupational Therapy",
    "Client Assessment for Physiotherapy",
    "Client Assessment for Speech Therapy",
    "Clinical Governance",
    "Clinical Supervision",
    "Commodities Trading Management",
    "Common Data Environment Management",
    "Communication and Navigation System Design",
    "Computer-aided Design",
    "Computerised Systems Validation",
    "Condition Monitoring",
    "Condition-based Monitoring",
    "Conflict Management",
    "Content Acquisition Management",
    "Content Commissioning",
    "Content Development and Strategy",
    "Content Distribution",
    "Contract Administration and Management",
    "Contract and Vendor Management",
    "Contract Development and Management",
    "Counselling Assessment",
    "Creative Entrepreneurship",
    "Credit Assessment",
    "Crew Management",
    "Cultural Sensitivity for Design",
    "Customer Acquisition Management",
    "Customer Service Innovation Management",
    "Customisation and Localisation",
    "Data and Information Visualisation",
    "Data Collection and Analysis",
    "Decarbonisation Consulting",
    "Decarbonisation Project Development",
    "Defect Density Monitoring",
    "Design Concepts Generation",
    "Design for Safety",
    "Design Writing",
    "Document Management for Pharmacy Support",
    "Documentation",
    "Documentation and Administration",
    "Dry Dock Project Management",
    "Electrical Engineering Management",
    "Electrostatic Discharge Control",
    "Empathetic Design",
    "Engineering Contract Management",
    "Engineering Drawing, Interpretation and Management",
    "Engineering Safety and Security Standards",
    "Engineering Safety Standards Interpretation",
    "Engineering Support Management",
    "Enterprise Database System Administration",
    "Environment and Social Governance",
    "Environment Impact Assessment",
    "Environmental Management System Policies, Standards, Procedures and Practices Management",
    "Equipment and Systems Testing",
    "Equipment Drawing",
    "Equipment Maintenance and Housekeeping",
    "Evidence Management",
    "Executive Protection",
    "Financial Crime Laws and Regulations",
    "Fleet Procurement",
    "Food and Beverage Equipment Maintenance",
    "Food and Beverage Production Management",
    "Food Manufacturing Process Design",
    "Gas Network System Management",
    "Hazardous Materials Identification System (HMIS) Administration",
    "Hazards and Risk Identification and Management",
    "Heating, Ventilation and Air Conditioning System Design",
    "Heavy Crane Vehicle Maintenance",
    "High Speed Camera Operations",
    "Hospitality Venue Inspection",
    "House Brand Development",
    "Human Resource Systems Management",
    "Image Processing and Industrial Vision Inspection",
    "Immersive Video Editing",
    "Incident and Accident Investigation",
    "Information Collection",
    "Innovation",
    "Integrated System Design and Application",
    "Intellectual Property Commercialisation and Exploitation",
    "Intellectual Property Enforcement",
    "Intellectual Property in Research and Development",
    "Intellectual Property Licencing",
    "Intellectual Property Management",
    "Intellectual Property Portfolio Management",
    "Internal Controls",
    "Internal Controls in Product Development",
    "IT Asset Management",
    "IT Standards",
    "IT Strategy",
    "Knowledge Management",
    "Labour Relations Management",
    "Landscape Tools, Equipment and Machinery Management",
    "Learning Needs Analysis",
    "Legal Writing",
    "Lighting Operations",
    "Loss and Risk Prevention Management",
    "Maintenance Coordination",
    "Maintenance Scheduling",
    "Manpower Planning and Deployment",
    "Manufacturing Workflow Management",
    "Marine Design Customisation",
    "Marine Engineering Calculations",
    "Marine Incident and Accident Investigations",
    "Marine Insurance Underwriting Profitability and Efficiency Management",
    "Marine Survey Reporting",
    "Maritime Emergency Response Management",
    "Maritime Hazards Identification",
    "Maritime Incident Management",
    "Market Entry Strategy Formulation",
    "Market Risk Management",
    "Marketing Strategy Development",
    "Material Qualification",
    "Materials Qualification",
    "Measurement of Building and Construction Works",
    "Mechanical Engineering Management",
    "Mechanical Maintenance Management",
    "Media Data Management",
    "Media Distribution Platform Management",
    "Media Strategy Development",
    "Medication Dispensing",
    "Merchandise Performance Analysis",
    "Metal Forming",
    "Metrology Management",
    "Mobile Equipment - Heavy Duty Prime Mover and Trailer Operations",
    "Mobile Equipment - Prime Mover Defensive Driving",
    "Multi-function Vehicle Maintenance",
    "Narrative Design",
    "Narrative Design in Product Development",
    "Naval Architecture Calculations",
    "Network Monitoring, Control and Supply Restoration",
    "Network Simulation and Analysis",
    "Network Systems Maintenance",
    "Non-destructive Testing",
    "Non-destructive Testing (Radiographic Inspection)",
    "Novel Food Application",
    "Nursing Research and Statistics",
    "Operational Risk Management",
    "Organisational Analysis Management",
    "Patent Office Action and Infringements",
    "Pest Control Site Assessment and Analysis",
    "Pest Disposal Management",
    "Plastic Injection Moulding",
    "Policy Implementation and Revision",
    "Port Call Planning",
    "Portfolio Management",
    "Power Plant Incident Investigation Management",
    "Pricing Strategy",
    "Process Optimisation",
    "Process Validation",
    "Procurement Coordination and Policy Development",
    "Procurement Performance Monitoring",
    "Product Costing and Pricing",
    "Product Improvement",
    "Product Lifecycle Management",
    "Product Risk Assessment",
    "Product Testing",
    "Product, Content and Experience Performance Management",
    "Production Budget Management",
    "Production Operations",
    "Production Planning and Scheduling",
    "Productivity and Innovation Strategy",
    "Productivity Optimisation for Food and Beverages Operations",
    "Project Cost",
    "Project Timeline",
    "Prompt Engineering",
    "Prop Design",
    "Public Areas Housekeeping Operations Management",
    "Qualitative Research",
    "Quality Control and Assurance",
    "Quality Improvement and Safe Practices",
    "Radioactive Materials and Irradiating Apparatus Management",
    "Regulatory Risk Assessment",
    "Regulatory Submission and Clearance",
    "Research Translation",
    "Risk Advisory",
    "Risk and Compliance Reporting",
    "Risk and Crisis Management",
    "Risk Compliance and Governance",
    "Risk Management and Administration",
    "Room Reservation Operations Management",
    "Security Event Management",
    "Set Design",
    "Sheet Metal Structures Maintenance",
    "Ship Cyber Security",
    "Ship Maintenance and Repair (Dock)",
    "Ship Propulsion Inspections",
    "Ship Safety Management Systems Audit",
    "Shipment Load Planning and Palletisation / Consolidation",
    "Single Stack Medium Forklift Operations",
    "Social Policy Evaluation",
    "Social Service Programme Evaluation",
    "Social Service Programme Implementation",
    "Solid-State Device Engineering",
    "Sound Design and Creation",
    "Sound Editing",
    "Sound Mixing",
    "Staff Continuous Learning",
    "Standard Operating Procedures Development",
    "Store Facilities and Housekeeping",
    "Structural Testing",
    "Supplier Performance",
    "Supplier Performance and Management",
    "Supply Chain Solutioning / Modelling / Planning / Strategising",
    "Sustainability Assurance",
    "Sustainability Management",
    "Sustainable Farming Practice Implementation",
    "Switchboard Operations Management",
    "Tax Advisory",
    "Tax Compliance",
    "Tax Controversy Management",
    "Tax Risk Management",
    "Taxation Laws",
    "Technical Report Writing",
    "Technical Sales Support",
    "Technical Sound Design",
    "Test Planning",
    "Time-Sensitive Cargo Delivery Management",
    "Tools Development",
    "Total Rewards Philosophy Development",
    "Tour and Travel Coordination, Ticketing and Reservations Management",
    "Trade Mark Application",
    "Trainer and Assessor Development Management",
    "Transportation and Handover of Patient",
    "Underwriting Process",
    "Underwriting Profitability and Efficiency Management",
    "Vendor and Partnership Management",
    "Vendor Management",
    "Vision Mixing",
    "Volunteer Retention and Engagement",
    "Waste Material Loading and Unloading Administration",
    "Website Performance Management",
    "Work in Biosafety Level-3 laboratories",
    "Workflow Management",
    "Workplace Optimisation",
    "Workplace Safety and Health Culture Management",
    "Workplace Traffic Safety Management",
    "Writing of Advertising Copy for Broadcast and Interactive Media",
    "Youth Development",
    "Youth Outreach",
]


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
