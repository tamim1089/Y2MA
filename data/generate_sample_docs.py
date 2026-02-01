#!/usr/bin/env python3
"""
Y2MA Sample Document Generator
Auto-generates realistic Space42 HR documents for the RAG knowledge base.
"""

import os
import json
from datetime import datetime
from pathlib import Path


# Sample Documents Content
DOCUMENTS = {
    "company_overview.txt": """SPACE42 - COMPANY OVERVIEW

About Space42
Space42 is a leading aerospace and AI technology company headquartered in Abu Dhabi, UAE. Formed through the merger of Bayanat and Yahsat, Space42 combines satellite communications, geospatial analytics, and artificial intelligence to deliver transformative solutions across industries.

Our Mission
To leverage space-based technologies and AI to solve complex global challenges, drive economic growth, and enhance the quality of life for communities worldwide.

Our Vision
To be the world's leading AI-powered space technology company, pioneering innovations that connect, protect, and empower people and organizations globally.

Core Business Areas:
1. Satellite Communications - Global connectivity solutions through our fleet of satellites
2. Earth Observation - High-resolution imagery and geospatial analytics
3. AI & Analytics - Advanced machine learning and data analytics platforms
4. Space Technology - Satellite manufacturing and space mission support

Global Presence:
- Headquarters: Abu Dhabi, UAE
- Satellite Ground Stations: UAE, Europe, Africa, Asia
- Offices: Dubai, Singapore, Houston, London
- Employees: 1,500+ professionals worldwide

Key Achievements:
- Launched 5+ satellites providing coverage across MENA, Africa, Europe, and Asia
- Processed over 10 million km² of satellite imagery annually
- Partnered with 50+ governments and enterprises globally
- Generated AED 2+ billion in annual revenue

Company Values:
- Innovation: We push boundaries and embrace new technologies
- Excellence: We strive for the highest quality in everything we do
- Integrity: We act with honesty and transparency
- Collaboration: We work together across teams and borders
- Sustainability: We are committed to environmental responsibility

For more information, visit www.space42.ai
""",

    "job_description_ai_engineer.txt": """JOB DESCRIPTION: SENIOR AI ENGINEER

Position: Senior AI Engineer
Department: AI & Machine Learning
Location: Abu Dhabi, UAE (Hybrid - 2 days remote)
Employment Type: Full-time, Permanent
Job ID: SP42-AI-2024-001

About the Role:
We are seeking a talented Senior AI Engineer to join our growing AI/ML team. You will design, develop, and deploy machine learning models that power our satellite imagery analysis, natural language processing systems, and predictive analytics platforms.

Key Responsibilities:
• Design and implement production-grade machine learning pipelines
• Develop computer vision models for satellite and aerial imagery analysis
• Build NLP systems for document processing and information extraction
• Collaborate with data engineers to optimize data pipelines
• Mentor junior team members and contribute to technical strategy
• Stay current with AI/ML research and evaluate new technologies
• Ensure model performance, scalability, and reliability in production

Required Qualifications:
• Master's or PhD in Computer Science, Machine Learning, or related field
• 5+ years of experience in machine learning engineering
• Strong proficiency in Python, PyTorch, and TensorFlow
• Experience with computer vision (CNNs, object detection, segmentation)
• Knowledge of NLP techniques (transformers, BERT, LLMs)
• Familiarity with cloud platforms (AWS, GCP, or Azure)
• Experience with MLOps tools (MLflow, Kubeflow, or similar)

Preferred Qualifications:
• Experience with satellite/geospatial imagery analysis
• Knowledge of remote sensing and GIS
• Published research in top ML conferences (NeurIPS, ICML, CVPR)
• Experience leading technical projects

Compensation & Benefits:
• Salary Range: AED 280,000 - 350,000 annually (based on experience)
• Annual Performance Bonus: Up to 20% of base salary
• Comprehensive health insurance (medical, dental, vision)
• 30 days annual leave + public holidays
• Education allowance: AED 5,000/year for training and certifications
• Relocation assistance for international candidates
• Flexible working arrangements

How to Apply:
Submit your resume and cover letter through our careers portal.
For questions, contact careers@space42.ai
""",

    "job_description_devops.txt": """JOB DESCRIPTION: DEVOPS ENGINEER

Position: DevOps Engineer
Department: Platform Engineering
Location: Dubai, UAE (Remote-friendly)
Employment Type: Full-time, Permanent
Job ID: SP42-DE-2024-002

About the Role:
Join our Platform Engineering team to build and maintain the infrastructure that powers Space42's satellite operations and AI platforms. You'll work on cutting-edge cloud architecture serving millions of users.

Key Responsibilities:
• Design and manage Kubernetes clusters across multiple cloud providers
• Implement CI/CD pipelines for ML model deployment
• Automate infrastructure provisioning with Terraform and Ansible
• Monitor system performance and implement reliability improvements
• Manage security, access controls, and compliance requirements
• Collaborate with development teams on deployment strategies
• On-call rotation for production systems

Required Qualifications:
• Bachelor's degree in Computer Science or related field
• 3+ years of DevOps/SRE experience
• Strong experience with Kubernetes (CKA certification preferred)
• Proficiency in cloud platforms (AWS/GCP/Azure)
• Experience with Infrastructure as Code (Terraform, Pulumi)
• Knowledge of CI/CD tools (GitLab CI, GitHub Actions, Jenkins)
• Scripting skills in Python, Bash, or Go

Preferred Qualifications:
• Experience with GPU clusters and ML infrastructure
• Knowledge of service mesh (Istio, Linkerd)
• Security certifications (CKS, AWS Security Specialty)

Compensation & Benefits:
• Salary Range: AED 200,000 - 280,000 annually
• Annual Performance Bonus: Up to 15%
• Comprehensive health insurance
• 30 days annual leave
• Remote work options (up to 3 days/week)
• Professional development budget

Apply at: careers@space42.ai
""",

    "job_description_product_manager.txt": """JOB DESCRIPTION: PRODUCT MANAGER

Position: Product Manager - AI Platform
Department: Product
Location: Abu Dhabi, UAE
Employment Type: Full-time, Permanent
Job ID: SP42-PM-2024-003

About the Role:
Lead the product strategy for our AI platform, working at the intersection of satellite technology, machine learning, and enterprise software. You'll define the roadmap, prioritize features, and work closely with engineering and customers.

Key Responsibilities:
• Define product vision, strategy, and roadmap for AI platform
• Gather and prioritize requirements from stakeholders and customers
• Write detailed product requirements and user stories
• Work with engineering to ensure timely delivery of features
• Analyze market trends and competitive landscape
• Conduct user research and incorporate feedback
• Define and track product metrics and KPIs

Required Qualifications:
• Bachelor's degree in Engineering, Business, or related field
• 4+ years of product management experience in B2B SaaS
• Experience with AI/ML products or data platforms
• Strong analytical and problem-solving skills
• Excellent communication and presentation abilities
• Experience with Agile methodologies

Preferred Qualifications:
• MBA or technical master's degree
• Experience in aerospace, geospatial, or enterprise software
• Domain knowledge in satellite imagery or remote sensing

Compensation & Benefits:
• Salary Range: AED 250,000 - 320,000 annually
• Annual Bonus: Up to 25%
• Stock options / equity participation
• Comprehensive benefits package
• 30 days annual leave
• International travel opportunities

Apply at: careers@space42.ai
""",

    "job_description_data_scientist.txt": """JOB DESCRIPTION: DATA SCIENTIST

Position: Data Scientist
Department: Data & Analytics
Location: Dubai, UAE (Hybrid)
Employment Type: Full-time, Permanent
Job ID: SP42-DS-2024-004

About the Role:
Join our Data Science team to uncover insights from satellite imagery, IoT sensors, and enterprise data. You'll build predictive models, design experiments, and present findings to stakeholders.

Key Responsibilities:
• Analyze large-scale geospatial and time-series datasets
• Build predictive and prescriptive analytics models
• Design and run A/B tests and experiments
• Create dashboards and visualizations for stakeholders
• Collaborate with ML engineers to productionize models
• Present insights and recommendations to leadership
• Mentor junior data scientists and analysts

Required Qualifications:
• Master's degree in Statistics, Mathematics, or related quantitative field
• 3+ years of experience in data science
• Strong proficiency in Python, R, and SQL
• Experience with statistical modeling and hypothesis testing
• Knowledge of machine learning algorithms
• Excellent data visualization skills (Tableau, Power BI, or Matplotlib)
• Strong communication and storytelling abilities

Preferred Qualifications:
• PhD in a quantitative field
• Experience with geospatial analysis
• Knowledge of causal inference methods
• Domain expertise in telecommunications or aerospace

Compensation & Benefits:
• Salary Range: AED 180,000 - 250,000 annually
• Annual Bonus: Up to 15%
• Comprehensive health insurance
• 30 days annual leave
• Learning & development budget
• Flexible working hours

Apply at: careers@space42.ai
""",

    "job_description_backend_engineer.txt": """JOB DESCRIPTION: BACKEND ENGINEER

Position: Senior Backend Engineer
Department: Engineering
Location: Abu Dhabi, UAE
Employment Type: Full-time, Permanent
Job ID: SP42-BE-2024-005

About the Role:
Build the backend systems that power Space42's satellite operations, data processing pipelines, and customer-facing APIs. You'll work with modern technologies to create scalable, reliable services.

Key Responsibilities:
• Design and implement high-performance backend services
• Build RESTful and GraphQL APIs
• Develop data processing pipelines for satellite telemetry
• Optimize database queries and system performance
• Implement security best practices and access controls
• Write comprehensive unit and integration tests
• Participate in code reviews and architectural discussions

Required Qualifications:
• Bachelor's degree in Computer Science or related field
• 4+ years of backend development experience
• Strong proficiency in Python, Go, or Java
• Experience with PostgreSQL, MongoDB, or similar databases
• Knowledge of message queues (Kafka, RabbitMQ)
• Familiarity with microservices architecture
• Experience with containerization (Docker, Kubernetes)

Preferred Qualifications:
• Experience with real-time data processing
• Knowledge of time-series databases (InfluxDB, TimescaleDB)
• Experience with satellite or telemetry data
• Understanding of distributed systems

Compensation & Benefits:
• Salary Range: AED 220,000 - 300,000 annually
• Annual Bonus: Up to 15%
• Comprehensive health insurance
• 30 days annual leave
• Stock options eligibility
• Professional development budget

Apply at: careers@space42.ai
""",

    "interview_process.txt": """SPACE42 INTERVIEW PROCESS

Our interview process is designed to be thorough yet respectful of your time. Here's what to expect:

STEP 1: APPLICATION REVIEW (2-3 business days)
After you submit your application, our talent acquisition team reviews your resume and cover letter. We look for alignment with the role requirements and Space42's values.

What we assess:
• Relevant experience and qualifications
• Technical skills match
• Career trajectory and growth potential
• Cultural fit indicators

STEP 2: PHONE SCREENING (30 minutes)
If your application is shortlisted, a recruiter will contact you for a phone screening.

Topics covered:
• Your background and career goals
• Motivation for joining Space42
• Salary expectations and availability
• Role-specific questions
• Opportunity to ask questions about Space42

STEP 3: TECHNICAL ASSESSMENT (Varies by role)
Engineering roles: Take-home coding assignment (4-6 hours estimated)
Data roles: Data analysis challenge with real datasets
Product roles: Case study presentation
All roles: Assessments are designed to reflect actual work

Timeline: 5-7 days to complete
What we look for: Problem-solving approach, code quality, communication

STEP 4: TEAM INTERVIEWS (2-3 rounds, 1-2 hours each)
You'll meet with potential teammates and cross-functional partners.

Round 1 - Technical Deep Dive:
• Detailed discussion of your assessment
• Technical problem-solving session
• Architecture and design questions
• Code review (for engineering roles)

Round 2 - Hiring Manager:
• Role expectations and responsibilities
• Team dynamics and working style
• Career development opportunities
• Your questions about the role

Round 3 - Cross-functional (if applicable):
• Meet with stakeholders from other teams
• Assess collaboration and communication
• Real-world scenario discussions

STEP 5: FINAL INTERVIEW WITH LEADERSHIP (45-60 minutes)
Meet with a senior leader or department head.

Topics covered:
• Your vision and career aspirations
• How you align with Space42's mission
• Leadership potential and growth mindset
• Cultural fit assessment

STEP 6: OFFER AND NEGOTIATION (1-2 weeks)
If successful, you'll receive a written offer.

Offer includes:
• Base salary and bonus structure
• Benefits package details
• Start date and onboarding information
• Relocation support (if applicable)

We're open to negotiation and want to find a package that works for both parties.

TIMELINE SUMMARY:
• Application to first interview: 1-2 weeks
• Interview process: 2-3 weeks
• Offer decision: 1 week after final interview
• Total process: 4-6 weeks

TIPS FOR SUCCESS:
• Research Space42's products and mission
• Prepare specific examples from your experience
• Ask thoughtful questions about the role and team
• Be authentic - we value genuine conversations
• Follow up with thank-you notes after interviews

CONTACT:
For questions about your application status: careers@space42.ai
For general inquiries: hr@space42.ai
""",

    "onboarding_checklist.txt": """SPACE42 ONBOARDING CHECKLIST

Welcome to Space42! This checklist will guide you through your first 30 days.

═══════════════════════════════════════════════════════════════════
BEFORE YOUR START DATE
═══════════════════════════════════════════════════════════════════

□ Complete pre-employment paperwork
  - Signed offer letter
  - Background check consent
  - Tax forms (for UAE: visa documentation)
  - Emergency contact information
  - Bank details for payroll

□ Provide required documents
  - Passport copy
  - Educational certificates
  - Professional certifications
  - Previous employment letters

□ IT Setup (HR will send login instructions)
  - Corporate email activation
  - VPN access request
  - Laptop preferences form

═══════════════════════════════════════════════════════════════════
WEEK 1: ORIENTATION & SETUP
═══════════════════════════════════════════════════════════════════

Day 1:
□ Arrive at reception by 9:00 AM
□ Collect employee badge and welcome kit
□ Complete HR orientation session (2 hours)
  - Company policies review
  - Benefits enrollment
  - Compliance training
□ IT setup and laptop configuration
□ Meet your manager for welcome lunch
□ Tour of the office and facilities

Day 2-3:
□ Complete mandatory training modules
  - Information security awareness
  - Code of conduct
  - Health and safety
  - Anti-harassment policy
□ Set up development environment (technical roles)
□ Review team documentation and wikis
□ Schedule 1:1 meetings with team members

Day 4-5:
□ Attend department overview presentation
□ Begin role-specific training
□ Access required systems and tools
□ Set up Slack/Teams and join relevant channels
□ Review current projects and roadmap

═══════════════════════════════════════════════════════════════════
WEEK 2: TEAM INTEGRATION
═══════════════════════════════════════════════════════════════════

□ Complete 1:1 meetings with all team members
□ Shadow a team member on current project
□ Attend team standup and planning meetings
□ Review coding standards and best practices (tech roles)
□ Understand team processes and workflows
□ Identify your first assignment with manager
□ Set up development environment fully
□ Join cross-functional team meetings as observer

═══════════════════════════════════════════════════════════════════
WEEK 3: CONTRIBUTION BEGINS
═══════════════════════════════════════════════════════════════════

□ Start working on first assignment
□ Pair with senior team member on complex tasks
□ Attend architecture/design reviews
□ Begin contributing to code reviews (tech roles)
□ Participate in agile ceremonies
□ Complete any remaining training modules
□ Schedule check-in with onboarding buddy
□ Explore internal tools and resources

═══════════════════════════════════════════════════════════════════
WEEK 4: FULL ENGAGEMENT
═══════════════════════════════════════════════════════════════════

□ Complete first project/assignment
□ Present work to team (if applicable)
□ 30-day feedback session with manager
  - Discuss initial impressions
  - Review progress against expectations
  - Identify areas for growth
  - Set 60/90 day goals
□ Join optional interest groups or committees
□ Provide feedback on onboarding experience
□ Schedule regular 1:1s with manager

═══════════════════════════════════════════════════════════════════
KEY CONTACTS
═══════════════════════════════════════════════════════════════════

HR Team: hr@space42.ai
IT Support: it-support@space42.ai
Facilities: facilities@space42.ai
Your HR Business Partner: [Assigned during onboarding]
Your Onboarding Buddy: [Assigned during onboarding]

Welcome to the Space42 family! 🚀
""",

    "benefits_guide.txt": """SPACE42 EMPLOYEE BENEFITS GUIDE

At Space42, we believe in taking care of our team. Here's a comprehensive overview of your benefits.

═══════════════════════════════════════════════════════════════════
HEALTH & WELLNESS
═══════════════════════════════════════════════════════════════════

MEDICAL INSURANCE
• Comprehensive coverage for employee and dependents
• Network: Global coverage with focus on UAE, UK, US
• Inpatient: 100% coverage, private rooms
• Outpatient: 90% coverage, AED 100 deductible per visit
• Prescription drugs: 85% coverage
• Pre-existing conditions: Covered after 6 months

DENTAL INSURANCE
• Preventive care: 100% covered (2 cleanings/year)
• Basic procedures: 80% covered
• Major procedures: 50% covered
• Annual maximum: AED 10,000 per person

VISION INSURANCE
• Eye exam: 100% covered annually
• Frames: AED 500 allowance every 2 years
• Lenses: 100% covered
• Contact lenses: AED 300 allowance annually

MENTAL HEALTH SUPPORT
• Employee Assistance Program (EAP)
• 10 free counseling sessions per year
• 24/7 helpline for crisis support
• Stress management workshops

GYM MEMBERSHIP
• AED 400/month fitness allowance
• Corporate rates at partner gyms
• On-site fitness facilities at Abu Dhabi HQ

═══════════════════════════════════════════════════════════════════
TIME OFF
═══════════════════════════════════════════════════════════════════

ANNUAL LEAVE
• 30 days per year (accrued monthly)
• Carry over: Up to 10 days to next year
• Buy/sell: Can sell up to 5 days back

PUBLIC HOLIDAYS
• All UAE public holidays (10-12 days)
• Eid holidays as per government announcement

SICK LEAVE
• Unlimited sick leave with manager approval
• Doctor's note required after 3 consecutive days
• Extended illness: Full pay for 90 days, then 50% for 90 days

PARENTAL LEAVE
• Maternity leave: 12 weeks full pay + 4 weeks half pay
• Paternity leave: 3 weeks full pay
• Adoption leave: Same as birth parents
• Gradual return: Option for reduced hours first month back

OTHER LEAVE
• Bereavement: 5 days for immediate family
• Marriage: 5 days for your wedding
• Hajj: 30 days unpaid (once during employment)
• Study leave: 10 days for exams/certifications

═══════════════════════════════════════════════════════════════════
FINANCIAL BENEFITS
═══════════════════════════════════════════════════════════════════

SALARY & BONUS
• Competitive base salary (reviewed annually)
• Annual performance bonus: 10-25% of base
• Merit increases: Avg. 5-10% annually based on performance

RETIREMENT SAVINGS
• End of Service Gratuity (as per UAE labor law)
• 21 days salary per year (first 5 years)
• 30 days salary per year (after 5 years)

HOUSING ALLOWANCE
• Available for certain roles/levels
• Abu Dhabi: Up to AED 150,000/year
• Dubai: Up to AED 200,000/year

RELOCATION SUPPORT
• International candidates:
  - Flight tickets for employee and dependents
  - 30-day hotel accommodation
  - Shipping allowance: Up to AED 20,000
  - Visa and documentation support
  - Cultural orientation program

═══════════════════════════════════════════════════════════════════
PROFESSIONAL DEVELOPMENT
═══════════════════════════════════════════════════════════════════

LEARNING BUDGET
• AED 5,000 per year for training and certifications
• Company-sponsored conferences: Case by case
• Internal learning platform with 1000+ courses
• Lunch & learn sessions (weekly)

CAREER GROWTH
• Annual career development conversations
• Internal mobility program
• Leadership development program
• Mentorship opportunities

EDUCATION ASSISTANCE
• Master's degree support: Up to 50% tuition (approval required)
• PhD sponsorship available for research roles
• Professional certifications: Fully covered if role-relevant

═══════════════════════════════════════════════════════════════════
WORK-LIFE BALANCE
═══════════════════════════════════════════════════════════════════

FLEXIBLE WORKING
• Core hours: 9 AM - 3 PM
• Flexible start/end times around core hours
• Remote work: Up to 3 days per week (role dependent)
• Compressed workweek option (4 days, 10 hours)

FAMILY SUPPORT
• Childcare subsidy: AED 2,000/month per child (max 2)
• School fee support: Available at senior levels
• Family health coverage included
• Nursing room available at all offices

═══════════════════════════════════════════════════════════════════
PERKS & EXTRAS
═══════════════════════════════════════════════════════════════════

• Annual flight home: Economy ticket for international employees
• Mobile phone allowance: AED 300/month
• Parking: Free at all offices
• Meals: Subsidized cafeteria at HQ
• Team events: Quarterly team outings
• Annual company retreat
• Employee referral bonus: AED 10,000 - 25,000

For questions about benefits, contact: benefits@space42.ai
""",

    "company_culture.txt": """SPACE42 CULTURE & VALUES

At Space42, our culture is the foundation of everything we do. We're building a company where talented people can do their best work, push boundaries, and make a meaningful impact.

═══════════════════════════════════════════════════════════════════
OUR VALUES
═══════════════════════════════════════════════════════════════════

🚀 INNOVATION
We embrace new ideas and technologies. We're not afraid to experiment, fail fast, and learn. Innovation isn't just about products - it's about how we work, collaborate, and solve problems.

How we live it:
• "Innovation Days" - quarterly hackathons
• 20% time for personal projects
• Patent bonuses for novel inventions
• Open idea submission platform

⭐ EXCELLENCE
We hold ourselves to the highest standards. We believe in doing things right, not just doing things fast. Quality is everyone's responsibility.

How we live it:
• Rigorous code reviews and testing
• Design reviews for all major features
• Continuous improvement mindset
• Recognition for exceptional work

🤝 INTEGRITY
We act with honesty, transparency, and ethical responsibility. We do what's right, even when it's hard. Trust is earned through consistent actions.

How we live it:
• Open book financials (quarterly all-hands)
• Speak-up culture for concerns
• Ethical AI development principles
• Environmental responsibility commitments

🌍 COLLABORATION
We work together across teams, functions, and geographies. We believe the best ideas come from diverse perspectives. No silos.

How we live it:
• Cross-functional project teams
• Open office layouts
• Transparent communication tools
• "No brilliant jerks" policy

📚 CONTINUOUS LEARNING
We're committed to growth - for our company and our people. We invest in learning and development because curious minds drive innovation.

How we live it:
• Generous learning budget
• Internal knowledge sharing
• Mentorship programs
• Conference sponsorships

═══════════════════════════════════════════════════════════════════
OUR WORKING STYLE
═══════════════════════════════════════════════════════════════════

AGILE & ITERATIVE
We work in sprints, ship often, and iterate based on feedback. Perfect is the enemy of good.

DATA-DRIVEN DECISIONS
We make decisions based on evidence, not just opinions. We experiment, measure, and learn.

AUTONOMY WITH ACCOUNTABILITY
We trust our people to do their best work. Freedom comes with responsibility for outcomes.

TRANSPARENT COMMUNICATION
We default to open. Information flows freely unless there's a good reason to restrict it.

CUSTOMER OBSESSED
Everything we do starts with the customer. We solve real problems, not imaginary ones.

═══════════════════════════════════════════════════════════════════
DIVERSITY, EQUITY & INCLUSION
═══════════════════════════════════════════════════════════════════

We believe diverse teams build better products. We're committed to:

• Inclusive hiring practices
• Equal pay for equal work
• Representation at all levels
• Employee resource groups
• Bias training and awareness
• Accessible workplace design

Current demographics (2024):
• 65+ nationalities represented
• 35% women in technical roles (above industry avg)
• 45% women in leadership
• 100% pay equity certification

═══════════════════════════════════════════════════════════════════
TEAM TRADITIONS
═══════════════════════════════════════════════════════════════════

WEEKLY
• Tuesday: All-hands standup (15 min)
• Thursday: Team lunch (on the company)
• Friday: Demo day (show what you built)

MONTHLY
• Town hall with leadership Q&A
• Team celebrations for shipped features
• Learning sessions with external speakers

QUARTERLY
• Innovation Days (48-hour hackathon)
• Team offsites and bonding events
• OKR reviews and planning

ANNUALLY
• Company retreat (destination TBD)
• Annual awards ceremony
• Give-back day (community service)
• Year-end party

═══════════════════════════════════════════════════════════════════
WHAT MAKES US DIFFERENT
═══════════════════════════════════════════════════════════════════

"At Space42, I feel like my work matters. We're literally sending satellites into space and building AI that helps governments respond to disasters. It's not just a job - it's a mission."
- Senior AI Engineer, 3 years at Space42

"The learning culture here is incredible. I've grown more in 2 years than in my previous 5 years elsewhere. And the people are genuinely kind."
- Product Manager, 2 years at Space42

"What I love is the balance. Yes, we work hard on challenging problems, but leadership genuinely cares about work-life balance. No weekend emails, no guilt for taking vacation."
- Software Engineer, 4 years at Space42

═══════════════════════════════════════════════════════════════════

We're building something special at Space42. If this resonates with you, we'd love to meet you.

Explore opportunities: careers.space42.ai
""",

    "faq.txt": """SPACE42 CANDIDATE FAQ

Frequently asked questions from candidates and new hires.

═══════════════════════════════════════════════════════════════════
GENERAL QUESTIONS
═══════════════════════════════════════════════════════════════════

Q: What does Space42 do?
A: Space42 is an AI-powered space technology company. We combine satellite communications, earth observation, and artificial intelligence to provide solutions in connectivity, geospatial analytics, and smart data services. We help governments, enterprises, and organizations make better decisions using space-based data.

Q: Where is Space42 located?
A: Our headquarters is in Abu Dhabi, UAE. We have offices in Dubai (UAE), and international presence in Singapore, Houston, and London. We also operate satellite ground stations across UAE, Europe, Africa, and Asia.

Q: How many employees does Space42 have?
A: We have over 1,500 employees globally, representing 65+ nationalities. Our team includes aerospace engineers, AI researchers, data scientists, software engineers, and business professionals.

Q: Is Space42 a startup?
A: Space42 was formed in 2024 through the merger of Bayanat (AI/analytics) and Yahsat (satellite communications), both established companies. We combine startup agility with the stability of established organizations.

═══════════════════════════════════════════════════════════════════
APPLICATION & HIRING
═══════════════════════════════════════════════════════════════════

Q: How do I apply for a job at Space42?
A: Visit careers.space42.ai to browse open positions. Submit your resume and cover letter through our online portal. You can also reach out to our recruiters on LinkedIn.

Q: How long does the hiring process take?
A: Typically 4-6 weeks from application to offer. This includes resume review (1-2 weeks), interviews (2-3 weeks), and offer stage (1 week).

Q: What should I expect in technical interviews?
A: For engineering roles, expect coding challenges, system design discussions, and behavioral questions. We may give you a take-home assignment (~4-6 hours) before the technical interview rounds.

Q: Do you hire internationally?
A: Yes! We actively hire global talent and provide visa sponsorship and relocation support. About 40% of our workforce relocated to the UAE from abroad.

Q: What languages are required?
A: English is our primary business language. Arabic is helpful but not required for most roles. Some customer-facing roles may require Arabic proficiency.

═══════════════════════════════════════════════════════════════════
COMPENSATION & BENEFITS
═══════════════════════════════════════════════════════════════════

Q: Are salaries in UAE tax-free?
A: Yes, the UAE has no personal income tax. Your salary is yours to keep. However, you may have tax obligations in your home country depending on your citizenship.

Q: What is the salary range for engineers?
A: Ranges vary by role and level. As a rough guide:
- Junior Engineer: AED 120,000 - 180,000/year
- Mid-level Engineer: AED 180,000 - 250,000/year
- Senior Engineer: AED 250,000 - 350,000/year
- Staff/Principal Engineer: AED 350,000 - 500,000/year

Q: What benefits does Space42 offer?
A: Comprehensive benefits including medical/dental/vision insurance, 30 days annual leave, 12 weeks maternity leave, AED 5,000 learning budget, gym membership, remote work options, and relocation support.

Q: Is there a bonus structure?
A: Yes, we offer annual performance bonuses ranging from 10-25% of base salary depending on individual performance and company results.

Q: Do you offer stock options or equity?
A: For certain roles and levels, we offer participation in our equity incentive program. Details are discussed during the offer stage.

═══════════════════════════════════════════════════════════════════
WORK ENVIRONMENT
═══════════════════════════════════════════════════════════════════

Q: What is the work schedule?
A: Our core hours are 9 AM - 3 PM with flexibility around those hours. The UAE workweek is Monday to Friday. We also offer a compressed workweek option (4 days, 10 hours each).

Q: Can I work remotely?
A: We offer hybrid work with up to 3 days remote per week for most roles. Some positions (especially those requiring lab/hardware access) may require more on-site presence.

Q: What is the dress code?
A: Smart casual for most days. Dress up for client meetings or formal events. Our engineering teams lean casual (jeans and t-shirts are fine).

Q: What is the team culture like?
A: Collaborative, innovative, and supportive. We have a flat hierarchy where ideas are valued regardless of seniority. We celebrate wins together and support each other through challenges.

═══════════════════════════════════════════════════════════════════
RELOCATION & VISA
═══════════════════════════════════════════════════════════════════

Q: Does Space42 provide relocation assistance?
A: Yes! We offer comprehensive relocation packages including:
- Flight tickets for you and your family
- 30-day hotel accommodation
- Shipping allowance (up to AED 20,000)
- Visa and documentation support
- Cultural orientation program

Q: How long does the UAE visa process take?
A: Typically 2-4 weeks once you accept the offer. Our HR team handles all documentation and guides you through the process.

Q: Can I bring my family to the UAE?
A: Yes, we sponsor family visas for your spouse and children. We also assist with school finding and provide school fee support at senior levels.

Q: Is living in the UAE safe?
A: The UAE is consistently ranked among the safest countries in the world. It has excellent healthcare, infrastructure, and quality of life.

═══════════════════════════════════════════════════════════════════
CAREER DEVELOPMENT
═══════════════════════════════════════════════════════════════════

Q: What growth opportunities exist at Space42?
A: We offer both technical and management tracks. Engineers can progress from Junior to Staff/Principal Engineer. We also have leadership development programs for those interested in management.

Q: Is there a learning and development budget?
A: Yes, every employee has AED 5,000 per year for training, courses, and certifications. We also sponsor conference attendance case by case.

Q: How often are performance reviews?
A: We conduct formal reviews twice a year (mid-year and year-end), with continuous feedback throughout the year. Salary reviews happen annually.

Q: Can I transfer between teams or locations?
A: Yes, we have an internal mobility program. After 1 year, you can apply for open positions in other teams or offices.

═══════════════════════════════════════════════════════════════════
STILL HAVE QUESTIONS?
═══════════════════════════════════════════════════════════════════

For application support: careers@space42.ai
For general HR questions: hr@space42.ai
For technical questions: Post on our LinkedIn during "Ask Me Anything" events

We're here to help! Don't hesitate to reach out.
""",

    "policies.txt": """SPACE42 HR POLICIES SUMMARY

This document provides an overview of key HR policies. Full policy documents are available on the internal HR portal.

═══════════════════════════════════════════════════════════════════
LEAVE POLICIES
═══════════════════════════════════════════════════════════════════

ANNUAL LEAVE
• Entitlement: 30 working days per year
• Accrual: 2.5 days per month (starts from day 1)
• Minimum booking: Half day (4 hours)
• Advance notice: 1 week for 1-3 days, 2 weeks for 4+ days
• Carry over: Maximum 10 days to next year
• Sell back: Up to 5 days at 100% value if not used
• Manager approval required for all requests

SICK LEAVE
• Entitlement: Unlimited with manager approval
• Documentation: Doctor's note required after 3 consecutive days
• Notification: Inform manager before work start time
• Extended illness:
  - Days 1-90: 100% pay
  - Days 91-180: 50% pay
  - Beyond 180 days: Unpaid, case-by-case review

PARENTAL LEAVE
• Maternity: 12 weeks full pay + 4 weeks half pay
• Paternity: 3 weeks full pay
• Adoption: Same as biological parents
• Notice: 8 weeks before expected start date
• Return: Gradual return option (reduced hours first month)
• Breastfeeding: 2x30-min breaks during first year

OTHER LEAVE TYPES
• Bereavement: 5 days (immediate family)
• Marriage: 5 days (your own wedding)
• Hajj/Umrah: Up to 30 days unpaid (once during employment)
• Study leave: 10 days for approved exams/certifications
• Jury duty: Full pay for required duration
• Voting: 2 hours on election day

═══════════════════════════════════════════════════════════════════
REMOTE WORK POLICY
═══════════════════════════════════════════════════════════════════

ELIGIBILITY
• Available after completing probation (6 months)
• Role must be suitable for remote work
• Manager approval required
• Must maintain required productivity

GUIDELINES
• Maximum: 3 days remote per week
• Core hours: Must be available 9 AM - 3 PM UAE time
• Equipment: Company provides laptop, may provide monitor
• Workspace: Must have suitable home office setup
• Security: VPN required, no public WiFi for sensitive work

INTERNATIONAL REMOTE WORK
• Maximum 30 days per year from outside UAE
• Advance approval required (2 weeks notice)
• Tax implications to be reviewed on case-by-case basis
• Time zone overlap of 4+ hours with UAE required

═══════════════════════════════════════════════════════════════════
EXPENSE REIMBURSEMENT
═══════════════════════════════════════════════════════════════════

BUSINESS TRAVEL
• Flights: Economy class (under 4 hours), Business class (over 4 hours for Sr. Manager+)
• Hotels: Up to AED 800/night (standard cities), AED 1,200/night (premium cities)
• Meals: AED 300/day all-inclusive
• Ground transport: Taxis/rideshare, or rental car with approval

EXPENSE CLAIMS
• Submit within 30 days of expense
• Receipts required for all claims over AED 50
• Manager approval required for amounts > AED 500
• Reimbursement processed within 14 business days

WHAT'S COVERED
• Work-related travel
• Client entertainment (pre-approval required for > AED 500)
• Training and conference registration
• Professional memberships (if job-related)
• Home office equipment (up to AED 2,000 one-time)

WHAT'S NOT COVERED
• Personal travel extensions
• Alcoholic beverages
• Traffic fines
• Personal phone bills (unless on approved plan)

═══════════════════════════════════════════════════════════════════
CODE OF CONDUCT
═══════════════════════════════════════════════════════════════════

PROFESSIONAL BEHAVIOR
• Treat all colleagues with respect and dignity
• Embrace diversity and inclusion
• Communicate openly and honestly
• Meet commitments and deadlines
• Represent Space42 professionally

PROHIBITED CONDUCT
• Harassment or discrimination of any kind
• Bullying or intimidation
• Dishonesty or fraud
• Conflicts of interest (undisclosed)
• Violation of confidentiality
• Substance abuse during work

REPORTING CONCERNS
• Speak with your manager first if comfortable
• Contact HR for sensitive matters
• Use anonymous ethics hotline: ethics@space42.ai
• No retaliation for good-faith reports

═══════════════════════════════════════════════════════════════════
PERFORMANCE MANAGEMENT
═══════════════════════════════════════════════════════════════════

REVIEW CYCLE
• Mid-year review: June-July
• Year-end review: December-January
• Continuous feedback encouraged throughout year

RATINGS
• Exceptional (5): Far exceeds expectations
• Strong (4): Exceeds expectations
• Effective (3): Meets expectations
• Developing (2): Below expectations
• Unsatisfactory (1): Does not meet expectations

COMPENSATION IMPACT
• Base salary increases tied to performance rating
• Bonus multiplier based on individual and company performance
• Promotion eligibility requires Strong (4)+ rating

PROBATION
• Duration: 6 months for all new employees
• Review: Formal assessment at 3 and 6 months
• Extension: May extend by 3 months if needed
• Termination: 1 week notice during probation

═══════════════════════════════════════════════════════════════════
CONFIDENTIALITY & IP
═══════════════════════════════════════════════════════════════════

CONFIDENTIAL INFORMATION
• Project details and roadmaps
• Customer and partner information
• Financial data
• Employee compensation data (except your own)
• Technical architectures and designs

INTELLECTUAL PROPERTY
• All work created during employment belongs to Space42
• Inventions made using company resources belong to Space42
• Personal projects: Review with legal if related to Space42's business
• Patent disclosure: Inventions must be disclosed to IP team

DATA PROTECTION
• Handle personal data per privacy policies
• Report data breaches immediately
• Complete mandatory data protection training
• Don't share login credentials

═══════════════════════════════════════════════════════════════════
POLICY UPDATES
═══════════════════════════════════════════════════════════════════

Policies are reviewed annually and may change. Material updates will be communicated via email and updated on the HR portal.

For full policies, visit: hr-portal.space42.ai/policies
Questions? Contact: hr@space42.ai
""",

    "career_paths.txt": """SPACE42 CAREER PATHS & PROGRESSION

At Space42, we offer clear career paths for growth, whether you prefer deep technical expertise or people leadership.

═══════════════════════════════════════════════════════════════════
ENGINEERING TRACKS
═══════════════════════════════════════════════════════════════════

INDIVIDUAL CONTRIBUTOR (IC) TRACK

Level 1: Junior Engineer (L1)
• Experience: 0-2 years
• Scope: Works on well-defined tasks with guidance
• Skills: Learning core technologies, writes solid code
• Salary Range: AED 120,000 - 180,000

Level 2: Engineer (L2)
• Experience: 2-4 years
• Scope: Owns features end-to-end, works independently
• Skills: Strong in 1-2 areas, designs small systems
• Salary Range: AED 180,000 - 250,000

Level 3: Senior Engineer (L3)
• Experience: 4-7 years
• Scope: Leads technical decisions for projects
• Skills: Expert in domain, mentors juniors, designs systems
• Salary Range: AED 250,000 - 350,000

Level 4: Staff Engineer (L4)
• Experience: 7-10 years
• Scope: Cross-team technical leadership
• Skills: Shapes technical strategy, solves ambiguous problems
• Salary Range: AED 350,000 - 450,000

Level 5: Principal Engineer (L5)
• Experience: 10+ years
• Scope: Organization-wide technical influence
• Skills: Industry recognized expertise, sets technical direction
• Salary Range: AED 450,000 - 600,000

Level 6: Distinguished Engineer (L6)
• Experience: 15+ years
• Scope: Company-wide and industry impact
• Skills: Thought leader, represents Space42 externally
• Salary Range: AED 600,000+

MANAGEMENT TRACK

Engineering Manager (EM)
• People: 5-10 engineers
• Focus: Team execution, people development, hiring
• Requirements: L3+ technical background
• Salary Range: AED 300,000 - 400,000

Senior Engineering Manager (Sr. EM)
• People: 15-30 engineers (multiple teams)
• Focus: Multi-team coordination, strategy execution
• Salary Range: AED 400,000 - 500,000

Director of Engineering
• People: 30-60 engineers
• Focus: Department strategy, cross-functional partnerships
• Salary Range: AED 500,000 - 650,000

VP of Engineering
• People: 60+ engineers
• Focus: Organization strategy, executive leadership
• Salary Range: AED 650,000+

═══════════════════════════════════════════════════════════════════
DATA & AI TRACKS
═══════════════════════════════════════════════════════════════════

DATA SCIENCE TRACK

Junior Data Scientist → Data Scientist → Senior Data Scientist → Staff Data Scientist → Principal Data Scientist

Key progression milestones:
• L2: Delivers end-to-end analysis independently
• L3: Leads complex projects, influences product decisions
• L4: Defines data strategy for product area
• L5: Shapes company-wide data science practices

ML ENGINEERING TRACK

Junior ML Engineer → ML Engineer → Senior ML Engineer → Staff ML Engineer → Principal ML Engineer

Key progression milestones:
• L2: Deploys models to production independently
• L3: Designs ML systems, optimizes for scale
• L4: Leads MLOps infrastructure, cross-team architecture
• L5: Industry-recognized ML expertise

═══════════════════════════════════════════════════════════════════
PRODUCT & DESIGN TRACKS
═══════════════════════════════════════════════════════════════════

PRODUCT MANAGEMENT TRACK

Associate PM → Product Manager → Senior PM → Group PM → Director of Product → VP of Product

Progression focus:
• APM-PM: Feature ownership, user research, execution
• Senior PM: Product strategy, roadmap ownership
• Group PM: Multi-product coordination, mentoring
• Director+: Portfolio strategy, business outcomes

DESIGN TRACK

Junior Designer → Designer → Senior Designer → Staff Designer → Principal Designer

Design specializations:
• UX Design
• Visual/UI Design
• UX Research
• Design Systems

═══════════════════════════════════════════════════════════════════
PROMOTION PROCESS
═══════════════════════════════════════════════════════════════════

TYPICAL TIMELINE
• L1 → L2: 2-3 years
• L2 → L3: 2-4 years
• L3 → L4: 3-5 years
• L4 → L5: 4-6 years
• L5 → L6: Exceptional cases only

PROMOTION CRITERIA
1. Consistently performing at next level for 6+ months
2. Demonstrated scope and impact increase
3. Positive feedback from peers and stakeholders
4. Manager recommendation
5. Calibration committee approval

PROMOTION CYCLE
• Twice per year: June and December
• Self-nomination or manager nomination
• Promotion packet and peer feedback required
• Committee review ensures consistency

═══════════════════════════════════════════════════════════════════
SWITCHING TRACKS
═══════════════════════════════════════════════════════════════════

IC TO MANAGEMENT
• Discuss interest with manager
• Shadow a manager for a quarter
• Complete leadership development program
• Take on acting manager role for 6 months
• If successful, transition to permanent EM role

MANAGEMENT TO IC
• This is welcomed and not seen as a demotion
• Many excellent ICs were former managers
• Discuss with manager, transition plan agreed
• May adjust title level based on IC expectations

CHANGING DISCIPLINES
• Data Scientist → ML Engineer: Common, focus on production skills
• Engineer → PM: Develop product sense, internal transfer
• Any role → Management: Leadership development program

═══════════════════════════════════════════════════════════════════
DEVELOPMENT RESOURCES
═══════════════════════════════════════════════════════════════════

INTERNAL PROGRAMS
• Technical Leadership Program (for L3+ ICs)
• Engineering Management Bootcamp
• Mentorship matching program
• Internal mobility job board

EXTERNAL LEARNING
• AED 5,000 annual learning budget
• Conference sponsorship
• Certification reimbursement
• Part-time degree support

FEEDBACK CHANNELS
• Weekly 1:1s with manager
• Quarterly career conversations
• 360 feedback for senior levels
• Skip-level meetings

═══════════════════════════════════════════════════════════════════

Questions about your career path? 
Discuss with your manager or reach out to: career-dev@space42.ai
"""
}


def generate_documents():
    """Generate all sample documents"""
    # Determine output directory
    script_dir = Path(__file__).parent
    output_dir = script_dir / "raw"
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("🚀 Generating Space42 sample documents...")
    print(f"   Output directory: {output_dir}")
    print()
    
    generated_files = []
    total_chars = 0
    
    for filename, content in DOCUMENTS.items():
        filepath = output_dir / filename
        
        # Write content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        
        char_count = len(content)
        total_chars += char_count
        generated_files.append({
            "filename": filename,
            "type": categorize_document(filename),
            "char_count": char_count,
            "generated_at": datetime.now().isoformat()
        })
        
        print(f"   ✅ {filename} ({char_count:,} chars)")
    
    # Estimate token count (rough approximation: 1 token ≈ 4 chars)
    estimated_tokens = total_chars // 4
    
    # Write metadata
    metadata = {
        "generated_at": datetime.now().isoformat(),
        "document_count": len(generated_files),
        "total_characters": total_chars,
        "estimated_tokens": estimated_tokens,
        "documents": generated_files
    }
    
    metadata_path = output_dir / "metadata.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    print()
    print("=" * 60)
    print(f"✅ Generated {len(generated_files)} documents")
    print(f"   Total characters: {total_chars:,}")
    print(f"   Estimated tokens: ~{estimated_tokens:,}")
    print(f"   Metadata saved to: {metadata_path}")
    print("=" * 60)


def categorize_document(filename):
    """Categorize document by its filename"""
    if "job_description" in filename:
        return "job_description"
    elif "overview" in filename:
        return "overview"
    elif "interview" in filename:
        return "process"
    elif "onboarding" in filename:
        return "onboarding"
    elif "benefits" in filename:
        return "benefits"
    elif "culture" in filename:
        return "culture"
    elif "faq" in filename:
        return "faq"
    elif "policies" in filename:
        return "policies"
    elif "career" in filename:
        return "career"
    else:
        return "general"


if __name__ == "__main__":
    generate_documents()
