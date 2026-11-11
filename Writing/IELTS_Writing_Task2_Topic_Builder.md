# IELTS Writing Task 2 — Topic Idea Bank Builder (Master Instructions)

> This file controls how every Writing Task 2 topic PDF is made.
> The learner gives a one-word command such as **`technology`**, **`environment`** or **`globalization`**.
> The AI then reads this file and builds one complete chapter PDF for that topic, following every rule below.

---

## 1. Mission

Build a series of large-font study PDFs, one for each of the most common IELTS Writing Task 2 topics. Each PDF must help the learner do three things:

1. **Generate ideas fast in the exam hall.** The learner should be able to find 2 strong ideas in 3–5 minutes for any question on that topic.
2. **Learn topic vocabulary with collocations.** The words should be natural and band-7 level, not rare or "showy".
3. **Practise expressing ideas in good English sentences.** The PDF includes 2–3 model essays written **only in Bangla**. The learner translates them into English to train sentence structure (simple, compound, complex and compound-complex), grammar and vocabulary use.
4. **Write independently.** Every PDF ends with **3–4 homework essay questions** that the learner writes alone, without a model answer.

**Question source:** the Bangla essays and the homework essays use real past-style questions from **IELTS Liz — 100 IELTS Essay Questions** (https://ieltsliz.com/100-ielts-essay-questions/). A cleaned local copy with question codes is in `Writing/source/IELTSLiz_Question_Bank.md` (Section 6.0).

### Learner profile (read before writing anything)

| Item | Detail |
|---|---|
| Target | IELTS Writing Band 7+ |
| Essay word plan | Intro **30–35+**, BP1 **100–120+**, BP2 **100–120+**, Conclusion **30–35+** → total **260+ words** (applies to every essay, plan and homework) |
| First language | Bangla |
| Main weakness 1 | Has ideas in mind but cannot express them clearly in English |
| Main weakness 2 | The Bangla thinking itself is not well organised, so the English becomes messy |
| Main weakness 3 | Needs a mix of long simple, compound and complex sentences in each paragraph |
| Vocabulary preference | **Clear, common academic words.** No rare, extraordinary or literary vocabulary |
| Reading comfort | Big font: body text **15–16 pt** |
| Reference style | The learner's own sample `Writing/Technology .pdf` (category-wise free writing) |

---

## 2. Command → action

| Learner types | AI builds |
|---|---|
| `education` | Chapter 01 |
| `technology` | Chapter 02 |
| `environment` | Chapter 03 |
| `health` | Chapter 04 |
| `government` / `government spending` | Chapter 05 |
| `work` / `employment` | Chapter 06 |
| `crime` | Chapter 07 |
| `family` / `society` | Chapter 08 |
| `media` / `advertising` | Chapter 09 |
| `culture` / `globalization` | Chapter 10 |
| `economy` / `business` | Extra Chapter 11 |
| `cities` / `transport` / `housing` | Extra Chapter 12 |
| `science` / `space` / `research` | Extra Chapter 13 |

Rules:

- Build **one chapter per command**. Do not build several chapters unless the learner asks for them.
- If a chapter already exists in `Writing/Output/`, tell the learner, then ask whether to rebuild it or make a "Part 2" with new essays and categories.
- After finishing, update the **Progress Log** (Section 13) and suggest the next topic.

---

## 3. Folder layout

```
Writing/
├── IELTS_Writing_Task2_Topic_Builder.md   ← this file (master instructions)
├── Technology .pdf                        ← learner's reference sample (style model)
├── writing common topic.pdf               ← learner's list of the 10 most repeated topics
├── tools/
│   ├── build_pdf.py                       ← Markdown → HTML → Chrome → PDF
│   └── style.css                          ← fonts, sizes, colours (body 15.5pt, Bangla 16pt)
├── source/
│   ├── IELTSLiz_Question_Bank.md          ← 258 IELTS Liz questions with codes (EDU-01, TEC-07 …)
│   └── NN_Topic.md                        ← the full chapter content (editable source)
└── Output/
    └── T2_NN_Topic_Idea_Bank.pdf          ← final PDF for the learner
```

Naming examples:

- `source/02_Technology.md` → `Output/T2_02_Technology_Idea_Bank.pdf`
- `source/10_Culture_Globalization.md` → `Output/T2_10_Culture_Globalization_Idea_Bank.pdf`

Build command (run from the `Writing` folder):

```
python tools/build_pdf.py source/02_Technology.md Output/T2_02_Technology_Idea_Bank.pdf
```

Why this pipeline: ReportLab and similar libraries break Bangla letters (যুক্তাক্ষর and vowel signs come out wrong). Headless Chrome shapes Bangla correctly, so it is always used. Dependencies: Python 3, `pip install markdown`, and Google Chrome or Microsoft Edge.

---

## 4. Chapter blueprint (every PDF follows this exact order)

| Part | Title in PDF | Purpose | Size target |
|---|---|---|---|
| 0 | Cover + How to Use This Chapter | Topic name, chapter number, a 6-step study routine | 1 page |
| 1 | Idea Generation Flow | The topic → sub-category chain, as in the learner's sample | ½–1 page |
| 2 | Exam-Hall Brainstorming System | How to find ideas in 3–5 minutes under pressure | 4–6 pages |
| 3 | Category-Wise Free Writing | Long English passages, one per sub-category (the core of the PDF) | 9–12 categories × 450–600 words |
| 4 | Vocabulary & Collocation Bank | Topic words with Bangla meaning, collocations and examples | 45–60 items |
| 5 | Sentence Structure Toolkit | Ready sentence patterns using this topic | 12–15 patterns |
| 6 | Bangla → English Translation Essays | 3 model essays in Bangla only, on IELTS Liz questions | 3 essays |
| 7 | Question Bank | Practice questions for this topic | 12–15 questions |
| 8 | Self-Check Checklist | Checklist for the learner's own English translation | ½ page |
| 9 | Homework Essays | 3–4 IELTS Liz questions the learner writes alone (no model answer) | 2–4 pages |

Part 9 is always the **last part** of the PDF.

Total length is normally **55–70 pages** at 15.5 pt (Chapter 02 Technology = 65 pages). Enough content matters more than page count: every category passage must be complete and full-length.

---

## 5. Part-by-part rules

### Part 0 — Cover + How to Use This Chapter

- Cover: `IELTS Writing Task 2 — Topic Idea Bank`, chapter number, topic name, one-line subtitle.
- "How to use" box (short, in Bangla with English key terms), for example:
  1. Read Part 1 and 2 once. Memorise the idea flow chain.
  2. Read 2 category passages per day. Underline collocations.
  3. Learn 10 vocabulary items per day from Part 4.
  4. Copy 3 sentence patterns from Part 5 into your notebook with your own examples.
  5. Translate one Bangla essay from Part 6 into English in 40 minutes, without looking at a dictionary first.
  6. Check your English with the Part 8 checklist, then improve it.

### Part 1 — Idea Generation Flow

Copy the format of the learner's sample exactly:

```
Technology → Education → Business/Economy → Communication → Healthcare → Environment →
Employment → Society → Culture → Government → Privacy/Security → Lifestyle
```

- Use the topic-specific chain from Section 6.
- Under the chain, add a short explanation: "When you see any [topic] question, run through this chain in your head and stop at the 2 links that fit the question best."

### Part 2 — Exam-Hall Brainstorming System

This part must be practical and fast to use. Include all of the following.

**2A. The 5-minute plan (timeline)**

| Minute | Action |
|---|---|
| 0–1 | **Decode the question.** Underline the topic words and the task words. Identify the essay type: Opinion / Discussion / Advantages–Disadvantages / Problem–Solution / Two-part (direct questions). |
| 1–3 | **WHO + WHAT grid.** Who is affected? What is the effect? Write 4–6 one-line notes. |
| 3–4 | **Pick the 2 strongest ideas.** For each idea, add *one reason* and *one real example*. |
| 4–5 | **Decide your position and outline.** Thesis + BP1 + BP2 + conclusion in 4 short lines. |

**2B. WHO is affected?** Topic-specific list (e.g. for Technology: students, workers, businesses, governments, consumers, elderly people, society).

**2C. WHAT is the effect?** Economic / Educational / Social / Environmental / Cultural / Health / Psychological / Safety. Add one topic example for each.

**2D. Quick Idea Bank table**: one row per sub-category.

| Sub-category | Positive ideas / arguments FOR | Negative ideas / arguments AGAINST | Ready example |
|---|---|---|---|

Each cell has 2–3 short bullet ideas. The "Ready example" column gives a realistic, general example (e.g. "a student in a rural village joining an online course"). **Never invent statistics, studies or named reports.** Use general, believable examples instead.

**2E. The idea-expansion chain (PEEL)**: Point → Explain (why?) → Example → Link/Result. Show it once in Bangla and once in English with a topic idea, so the learner sees how 1 idea becomes 5–6 sentences.

**2F. Worked brainstorm demo**: take one real question from the Question Bank and show what the 5-minute notes would look like (short English notes), then a 1–2 line Bangla explanation of why those ideas were chosen.

**2G. Essay-type paragraph plans**: a compact table showing what goes in the Introduction, BP1, BP2 and Conclusion for each of the 5 essay types. The column headers show the word plan: Introduction (30–35), BP1 (100–120), BP2 (100–120), Conclusion (30–35). Below it, add a **"260-word plan"** box in Bangla explaining how many sentences go in each paragraph.

### Part 3 — Category-Wise Free Writing (the core)

This copies the style of the learner's `Technology .pdf`. Each sub-category from the idea flow gets its own section.

Rules for every passage:

- **Heading**: `[Topic] and [Sub-category]`, e.g. "Technology and Healthcare".
- **Length**: 450–600 words. Never shorter than 450.
- **Structure inside each passage** (as in the sample):
  1. Opening paragraph: how the topic has changed this area (past vs present).
  2. 2–3 paragraphs of **benefits/positive effects**, each with explanation and a general example.
  3. 2–3 paragraphs of **problems/negative effects**, each with explanation and a general example.
  4. 1 paragraph of **solutions or a balanced view**: what governments, schools, companies or individuals should do.
  5. Closing paragraph: a balanced judgement the learner can reuse as an essay position.
- **Bold 6–10 key collocations** in each passage (`**narrow educational inequalities**`) so they stand out when the learner revises.
- Each passage must work as an **idea store**: after reading it, the learner should have 4–6 ideas they could use in an essay.
- Cover the common questions in Section 6 across the categories, so every listed question has ideas somewhere in Part 3.
- Use the language rules in Section 7.

### Part 4 — Vocabulary & Collocation Bank

- 45–60 items, **grouped by sub-category** (small heading per group).
- Table format:

| Word / Phrase | বাংলা অর্থ | Useful collocations | Example sentence (topic-based) |
|---|---|---|---|
| access (n/v) | প্রবেশাধিকার, পাওয়ার সুযোগ | **gain access to**, **easy access to**, **widen access to** | Online courses have **widened access to** higher education. |

- Include word families where useful: *access, accessible, accessibility*.
- Include 8–10 **topic phrases for "positive" and "negative" ideas**, e.g. *a double-edged sword*, *bring tangible benefits*, *pose a serious threat*.
- Vocabulary level: see Section 7.

### Part 5 — Sentence Structure Toolkit

12–15 patterns. For each pattern give: the pattern name, a formula, a short Bangla explanation (one line), and **2 topic examples**.

Must include:

1. Long simple sentence (with a rich noun phrase): *The rapid growth of online learning platforms has changed the way students study.*
2. Compound with *and / but / so / yet*
3. Compound with semicolon + linker: *…; however, … / …; therefore, …*
4. Complex: *Although / Even though …,*
5. Complex: *Because / Since / As …,*
6. Complex: *If / Unless / Provided that …,*
7. Relative clause: *which / who / where / whose*
8. Compound-complex: *Although …, X …, and Y …*
9. Participle phrase: *Having …, / Living in …,*
10. *Not only … but also …*
11. *The more …, the more …*
12. Cleft / emphasis: *It is … that …* / *What … is …*
13. Passive for objectivity: *It is widely believed that …*
14. Contrast of views: *While some people argue that …, others believe that …*
15. Result / consequence: *…, which means that … / As a result, …*

After the patterns, add a **"Paragraph mix formula"** box: every body paragraph should contain ~1 long simple, 1–2 compound, 2–3 complex and 1 compound-complex sentence.

### Part 6 — Bangla → English Translation Essays (most important practice part)

The PDF contains **3 essays** (minimum 2 if a topic is very narrow). They must cover **3 different essay types** chosen from: Opinion (agree/disagree), Discussion (both views + opinion), Advantages–Disadvantages, Problem–Solution / Cause–Solution, Two-part question.

**Choosing the essay questions:**

- Take all 3 questions from `source/IELTSLiz_Question_Bank.md`, using the IELTS Liz sections mapped to this chapter (Section 6.0).
- Prefer questions that also match a ★ common question from the learner's list (Section 6), and those marked "common", "frequent", "repeated most years" or with recent years.
- Copy the question text exactly, fixing only obvious typos (e.g. "To what extend" → "To what extent"). Do not copy the site's notes in brackets, such as "(Reported 2017)".
- Show the question code under the question, e.g. *Source: IELTS Liz · EDU-11*.
- Never reuse a question code already used in an earlier chapter (check the Progress Log).
- The Bangla essay ideas must be written fresh by the AI, using the ideas from Part 3. Do not copy any model answer from IELTS Liz or another website.

For each essay, show these blocks in this order:

1. **Question** — a full IELTS-style question in English (in a grey box).
2. **Essay type + Position** — one line in English, one line in Bangla.
3. **পরিকল্পনা (Plan)** — 4 short Bangla lines: Intro idea, BP1 idea + example, BP2 idea + example, Conclusion.
4. **Word Bank for this essay** — 10–12 English words/collocations from Part 4 that fit this essay. These are the words the learner should try to use when translating.
5. **The Bangla essay** — in the orange Bangla box, with **exactly these four headings**:
   - **Introduction**
   - **Body Paragraph 1**
   - **Body Paragraph 2**
   - **Conclusion**

Rules for the Bangla essay text:

- **Bangla only.** Do **not** give an English version of the essay anywhere in the PDF (the learner will translate it). An English model answer is only added if the learner asks for it later.
- Use standard **চলিত ভাষা** (modern standard Bangla), clear and natural, not literary or সাধু ভাষা.
- **One Bangla sentence = one target English sentence.** Write each Bangla sentence so that its correct English translation becomes a good IELTS sentence. Use Bangla connectors that point to the right structure:
  - যদিও … তবুও → *Although …*
  - কারণ / যেহেতু → *because / since*
  - যদি … তাহলে → *If …*
  - যা / যে / যেখানে / যার → *which / who / where / whose*
  - ফলে / এর ফলে → *As a result, / …, which leads to …*
  - শুধু … নয়, … ও → *not only … but also …*
  - অন্যদিকে / তবে → *On the other hand, / However,*
  - উদাহরণস্বরূপ → *For example, / For instance,*
- After each Bangla sentence, add a small **structure tag** showing the target sentence type: `<span class="tag">Simple</span>`, `Compound`, `Complex` or `Compound-Complex`. This trains the learner to see sentence variety.
- Key technical terms that are awkward in Bangla may be given in brackets in English, e.g. "দূরশিক্ষণ (online learning)". Maximum 1 bracket per sentence, 6–10 per essay.
- **Length — the learner's fixed word plan (minimum 260 words in English):**

  | Paragraph | English words (when translated) | Bangla sentences | Content |
  |---|---|---|---|
  | Introduction | **at least 30–35** | 2–3 | paraphrase of the question + clear thesis/position |
  | Body Paragraph 1 | **at least 100–120** | 5–6 | topic sentence → explanation → example → result |
  | Body Paragraph 2 | **at least 100–120** | 5–6 | same pattern |
  | Conclusion | **at least 30–35** | 2 | summary + final opinion/recommendation |
  | **Total** | **260–310** | 14–17 | |

  - Show the target in every Bangla heading: `#### Introduction (30–35 words)`, `#### Body Paragraph 1 (100–120 words)`, `#### Body Paragraph 2 (100–120 words)`, `#### Conclusion (30–35 words)`.
  - Each Bangla sentence must carry enough detail (reason, example, result) that its natural English translation is about 18–25 words in the body paragraphs.
  - **Word-count check (mandatory):** before building, the AI writes a private English draft of each essay in the scratchpad (never in the PDF) and counts the words per paragraph. If any paragraph is below its target, add detail to the Bangla text and check again.
- Sentence mix across the essay: at least 3 Simple, 3 Compound, 5 Complex, 2 Compound-Complex.
- The ideas in the essays must come from Part 3, so the learner sees how the idea bank turns into an essay.
- The position must be clear and consistent from Introduction to Conclusion.

Before the first essay, add a one-page **"How to translate these essays" guide (in Bangla)**:

1. Read the whole Bangla paragraph first. Understand the idea, not each word.
2. Look at the tag. Decide the English structure before you write.
3. Choose the linker (Although / Because / which / As a result …).
4. Use words from the essay's Word Bank.
5. Check the verb tense, subject–verb agreement and articles (a/an/the).
6. Do not translate word for word; translate meaning into natural English.
7. Time yourself: 40 minutes per essay.

### Part 7 — Question Bank

- 12–15 IELTS-style questions on the topic, grouped by essay type.
- Include all the learner's common questions for this topic (Section 6), written as full questions.
- Fill the rest with IELTS Liz questions from the mapped sections (show the code). Do not repeat the questions used in Part 6 or Part 9.
- After each question, add a short "Use ideas from: [category names]" hint pointing to Part 3.

### Part 8 — Self-Check Checklist

A table or checklist the learner uses after translating each essay:

- Did I answer every part of the question?
- Is my position clear in the introduction and the conclusion?
- Does each body paragraph have one main idea, an explanation and an example?
- Did I use at least 5 complex and 2 compound-complex sentences?
- Did I use 8+ words from the Word Bank correctly?
- Articles (a/an/the), plurals, subject–verb agreement, tense checked?
- Did I avoid repeating the same word more than 3 times?
- Is the word count 260+, with Intro 30–35+, BP1 100–120+, BP2 100–120+, Conclusion 30–35+?

### Part 9 — Homework Essays (always the last part)

3–4 essays the learner plans and writes **alone in English**, under exam conditions. No model answer, no Bangla essay, and no English answer are given.

Choosing the questions:

- Take them from `source/IELTSLiz_Question_Bank.md` (mapped sections in Section 6.0).
- They must be **different from** the Part 6 essays and the Part 7 question bank.
- Cover **different essay types**, preferably the types not used in Part 6, so that by the end of the chapter the learner has met all 5 types.
- At least 1 question should match a ★ common question.

For each homework essay, show (each essay on its own page, using `<div class="essay-block" markdown="1">`):

1. **Homework N** heading + the question in the grey question box + *Source: IELTS Liz · CODE*.
2. **Essay type** (English) and **time limit**: 40 minutes, 260+ words.
   **Word plan:** Intro 30–35 · BP1 100–120 · BP2 100–120 · Conclusion 30–35.
3. **Use ideas from:** the 2–3 Part 3 categories that help with this question.
4. **ভাবনার প্রশ্ন (Thinking prompts):** 4 short guiding questions in Bangla only. They point the learner in a direction but do not give the answer, for example:
   - তোমার মত কী: পুরোপুরি একমত, আংশিক একমত, নাকি একমত নও?
   - Body Paragraph 1-এ কোন যুক্তি দেবে? এর একটি বাস্তব উদাহরণ কী হতে পারে?
   - Body Paragraph 2-এ বিপরীত দিক বা সমাধান কী লিখবে?
   - উপসংহারে কোন সুপারিশ করবে?
5. **Try to use:** 6–8 collocations from Part 4 that suit the question.
6. **Sentence target:** a reminder line, e.g. "Use at least 5 complex and 2 compound-complex sentences."
7. A short note: "After writing, check your essay with the Part 8 checklist. If you want feedback, send your essay to the AI."

Close Part 9 with a small **homework tracker table** the learner can fill in by hand:

| Homework | Date written | Time taken | Word count | Self-check score (/8) |
|---|---|---|---|---|
| 1 | | | | |

---

## 6. Topic map: sub-categories (idea flow) and common questions

The "common questions" marked ★ come from the learner's file `writing common topic.pdf`. They guide the categories and the question bank. The essays (Part 6) and homework (Part 9) use IELTS Liz questions, chosen to match the ★ themes where possible.

### 6.0 IELTS Liz section → chapter mapping

All codes refer to `source/IELTSLiz_Question_Bank.md`. "Main" sections are used first; "Also" sections are used when they contain a question that clearly fits the chapter. A question code may be used in **only one** chapter.

| Chapter | Main IELTS Liz sections | Also |
|---|---|---|
| 01 Education | Education (EDU) | Reading (REA), Language (LAN-03, LAN-06), Work (WRK-03, WRK-11, WRK-12) |
| 02 Technology & Internet | Technology (TEC) | Communication & Personality (COM-10 to COM-15), Crime (CRI-01, CRI-15), Business (BUS-02, BUS-08) |
| 03 Environment | Environment (ENV) | Transport (TRA-03, TRA-05), Tourism (TOU-02, TOU-09, TOU-10), Housing (HOU-02, HOU-08) |
| 04 Health & Lifestyle | Health (HEA), Food & Diet (FOO) | Sport & Exercise (SPO), Government (GOV-01, GOV-03) |
| 05 Government & Public Spending | Government (GOV), Art (ART-01, ART-06) | Space Exploration (SPA), Sport (SPO-05), Society (SOC-04), Transport (TRA-08) |
| 06 Work & Employment | Work (WRK) | Business & Money (BUS-01, BUS-11, BUS-13, BUS-15, BUS-16), Leisure (LEI-02), Sport (SPO-06) |
| 07 Crime & Punishment | Crime & Punishment (CRI) | Media (MED-02) |
| 08 Family & Society | Family & Children (FAM), Society (SOC) | Communication & Personality (COM-01 to COM-09, COM-16 to COM-20) |
| 09 Media & Advertising | Media & Advertising (MED) | Business (BUS-05, BUS-06, BUS-09, BUS-18), Reading (REA-01, REA-04), Sport (SPO-08) |
| 10 Culture & Globalization | Tourism & Travel (TOU), Language (LAN) | Society (SOC-05, SOC-07, SOC-08, SOC-09, SOC-13), Art (ART-02 to ART-05), Business (BUS-07) |
| 11 Economy & Business (extra) | Business & Money (BUS) | Society (SOC-01, SOC-03), Leisure (LEI-01) |
| 12 Cities, Housing & Transport (extra) | Housing (HOU), Transport (TRA) | Society (SOC-06, SOC-10, SOC-11), Work (WRK-02, WRK-10), Family (FAM-02) |
| 13 Science, Space & Research (extra) | Space Exploration (SPA) | Food (FOO-01, FOO-06), Education (EDU-22) |

If a chapter's sections run short of unused questions, write a new IELTS-style question on the same theme and label it *Source: practice question*.

### Chapter 01 — Education
**Idea flow:** Education → Cost & Free Education → Online vs Classroom Learning → Exams & Assessment → Teachers vs Parents → Academic vs Practical Skills → Technology in Schools → University & Employment → Studying Abroad → Arts, Sports & Physical Education → Discipline & Behaviour → Lifelong Learning
**Common questions:** ★ Should education be free for everyone? ★ Online education vs traditional classroom ★ Exams vs continuous assessment ★ Teachers' responsibility vs parents' responsibility; extra: university for everyone or only for the best students; practical skills vs academic subjects; studying abroad; compulsory physical education.

### Chapter 02 — Technology & Internet
**Idea flow:** Technology → Education → Business/Economy → Communication → Healthcare → Environment → Employment (AI & Automation) → Society & Social Media → Culture → Government → Privacy/Security → Lifestyle → Children & Screen Time
**Common questions:** ★ Technology reduces face-to-face communication ★ AI & automation replacing jobs ★ Social media's impact on young people ★ Advantages and disadvantages of the internet; extra: children using smartphones, online shopping vs local shops, dependence on technology.
**Note:** The learner's `Technology .pdf` is the style model. Do not copy it word for word. Write new passages, and add the categories it does not have (Society & Social Media, Children & Screen Time, AI).

### Chapter 03 — Environment
**Idea flow:** Environment → Climate Change & Responsibility (Government vs Individuals) → Plastic & Waste → Wildlife & Biodiversity → Renewable Energy → Air Pollution, Cities & Transport → Water & Farming → Deforestation → Economic Growth vs Environment → Consumerism → International Cooperation → Environmental Education
**Common questions:** ★ Climate change: whose responsibility (government vs individuals)? ★ Plastic pollution ★ Protecting wildlife ★ Renewable energy; extra: economic growth vs protecting the environment; rich vs poor countries' responsibility; banning private cars in city centres.

### Chapter 04 — Health & Lifestyle
**Idea flow:** Health → Fast Food & Diet → Exercise & Sedentary Lifestyle → Mental Health & Stress → Government Spending (Prevention vs Treatment) → Technology & Health → Ageing Population → Sugar/Tobacco Taxes & Laws → Children's Health & Sport → Work Stress → Food Advertising & Labelling
**Common questions:** ★ Fast food & unhealthy habits ★ Mental health issues ★ Government spending on healthcare ★ Exercise & modern lifestyle; extra: individual vs government responsibility for health; taxing unhealthy food; free healthcare.

### Chapter 05 — Government & Public Spending
**Idea flow:** Government → Education vs Defence → Public Transport vs Roads → Arts vs Science Funding → Healthcare → Space Exploration → Sports Facilities & Big Events → Welfare & Poverty → Foreign Aid → Taxation → Rural Development → Museums & Heritage
**Common questions:** ★ Government should spend more on education than on defence ★ Public transport vs road development ★ Arts vs science funding; extra: space research vs problems on Earth; hosting international sports events; helping poor countries; should governments pay for museums and theatres.

### Chapter 06 — Work & Employment
**Idea flow:** Work → Job Satisfaction vs High Salary → Work–Life Balance → Working from Home → Job Security vs Career Change → Automation & AI → Youth Unemployment & Skills → Gender Equality at Work → Retirement Age → Self-Employment & Entrepreneurship → Teamwork vs Working Alone → Working Abroad & Brain Drain
**Common questions:** ★ Job satisfaction vs high salary ★ Work–life balance ★ Working from home ★ Job security vs career change; extra: a four-day working week; young people starting their own business; equal pay.

### Chapter 07 — Crime & Punishment
**Idea flow:** Crime → Causes of Crime (Poverty, Education, Family) → Prison vs Rehabilitation → Capital Punishment → Youth Crime → Media & Violence → Police, Technology & Surveillance → Cybercrime → Community Service → Education as Prevention → Repeat Offending → Drugs & Crime
**Common questions:** ★ Causes of crime ★ Prison vs rehabilitation ★ Capital punishment ★ Youth crime; extra: longer prison sentences; parents' responsibility for children's crimes; CCTV and privacy.

### Chapter 08 — Family & Society
**Idea flow:** Family → Nuclear vs Joint Family → Care for Elderly People → Generation Gap → Children's Upbringing & Parenting → Working Parents & Childcare → Technology & Family Time → Changing Gender Roles → Children's Independence & Discipline → Urban Life & Community → Housing & Living Alone
**Common questions:** ★ Nuclear family vs joint family ★ Care for elderly people ★ Generation gap ★ Children's upbringing; extra: should parents or schools teach values; young adults living with parents; family meals.

### Chapter 09 — Media & Advertising
**Idea flow:** Media → Advertising & Children → Fake News & Misinformation → Media Responsibility → Too Much Advertising & Consumerism → Celebrities & Influencers → Social Media vs Traditional News → Privacy of Famous People → Violence in Media → Government Control & Freedom of the Press → Public Service Advertising
**Common questions:** ★ Advertising's influence on children ★ Fake news ★ Media responsibility ★ Too much advertising; extra: should advertising to children be banned; online news vs newspapers; celebrities as role models.

### Chapter 10 — Culture & Globalization
**Idea flow:** Globalization → Traditional Culture Disappearing → Western Influence → Globalization: Benefits or Harm → International Tourism → Language & English as a Global Language → Multinational Companies vs Local Business → Food, Fashion & Lifestyle → Migration & Multicultural Societies → Museums & Heritage → Global Economy & Inequality → International Cooperation
**Common questions:** ★ Traditional culture is disappearing ★ Western influence ★ Does globalization benefit or harm culture? ★ International tourism; extra: minority languages dying out; local vs international products; learning about other cultures.

### Extra Chapter 11 — Economy & Business
**Idea flow:** Economy → Economic Growth vs Well-being → Small Business vs Big Companies → Online Shopping → Consumerism → Wealth Gap & Poverty → Tax & Government Role → International Trade → Tourism Economy → Rural vs Urban Economy → Money & Happiness

### Extra Chapter 12 — Cities, Housing & Transport
**Idea flow:** Cities → Urbanisation → Traffic & Public Transport → Housing Costs → Rural–Urban Migration → Pollution & Green Spaces → Planning & Infrastructure → Crime & Safety in Cities → Old Buildings vs New Development → Remote Work & Small Towns

### Extra Chapter 13 — Science, Space & Research
**Idea flow:** Science → Space Exploration → Medical Research → Animal Testing → Government vs Private Funding → Science Education → Genetic Engineering & Food → Ethics of Research → Science for Developing Countries

---

## 7. Language rules (all English text in the PDF)

### Vocabulary level

Use **clear, natural, band-7 academic vocabulary** of the kind found in the learner's `Technology .pdf`. Good examples:

> significant, considerably, access, accessible, affordable, efficient, sustainable, vulnerable, widen inequalities, reduce costs, improve productivity, rely heavily on, take responsibility for, play a vital role in, have a negative impact on, raise awareness, strike a balance, in the long term

**Do not use** rare, literary or "showy" words that examiners do not reward and that the learner cannot use naturally. Avoid words like:

> ubiquitous, panacea, quintessential, plethora, myriad (as a noun), juxtapose, ameliorate, deleterious, exacerbate (use *worsen*), proliferation (use *rapid growth*), paradigm shift, inexorable, salient, multifarious, burgeoning

Rule of thumb: if a word would sound strange in a BBC news report, do not use it.

### Sentence structure

- Every paragraph mixes sentence types (long simple, compound, complex, compound-complex).
- Average sentence length 18–28 words; vary it.
- Use natural linkers. Do not overuse *Moreover / Furthermore* (max 2 per passage each). Also use *In addition, Similarly, As a result, Consequently, For instance, However, Nevertheless, On the other hand, In contrast, Therefore, This means that, Ultimately*.
- Prefer clear general examples ("a student living in a rural area…") to invented data.

### Accuracy and honesty

- No invented statistics, percentages, named studies, named reports or fake quotes.
- Facts must be general and widely accepted.
- Spelling: one consistent style (British English is preferred for IELTS: *behaviour, organise, labour*).

### Bangla text

- Standard চলিত ভাষা, clear sentences, correct spelling.
- No mixing in random English words except the bracketed key terms allowed in Part 6.

---

## 8. Source file conventions (`source/NN_Topic.md`)

The source is Markdown, plus a few HTML blocks for special boxes. Use these exact patterns:

**Cover**

```html
<div class="cover" markdown="1">
# IELTS Writing Task 2 — Topic Idea Bank
<p class="sub">Chapter 02 · Technology & Internet</p>
<p class="sub">Ideas · Vocabulary · Sentence Structure · Bangla Translation Essays</p>
</div>
```

**A new part on a new page:** `## Part 3 — Category-Wise Free Writing {: .part}`

**Idea-flow chain:** `<div class="flow">Technology → Education → … → Lifestyle</div>`

**Tip / strategy box:**

```html
<div class="tip" markdown="1">
**Exam tip:** …
</div>
```

**Essay question:** `<div class="question">Some people believe that … To what extent do you agree or disagree?</div>`

**Each essay starts on a new page:** `<div class="essay-block" markdown="1"> … </div>` wraps the essay title, question, plan and word bank.

**Bangla essay block:**

```html
<div class="bn" markdown="1">
#### Introduction
বাক্য ১ … । <span class="tag">Complex</span> বাক্য ২ … । <span class="tag">Simple</span>

#### Body Paragraph 1
…

#### Body Paragraph 2
…

#### Conclusion
…
</div>
```

**Collocations in passages:** bold with `**…**`.

Font sizes are set in `tools/style.css` (English body 15.5 pt, Bangla 16 pt, tables 14 pt). Do not reduce them below 15 pt for body text.

---

## 9. Build workflow (follow in order)

1. **Read this file** completely, then open `Writing/Technology .pdf` (style model) and `Writing/writing common topic.pdf` (question list) if not read in this session.
2. **Check Output/** for an existing PDF of the requested topic (see Section 2 rules).
3. **Open `source/IELTSLiz_Question_Bank.md`** and list the unused questions in the sections mapped to this chapter (Section 6.0; used codes are in the Progress Log). If the bank file is missing, download it again from https://ieltsliz.com/100-ielts-essay-questions/ (one page per topic).
4. **Plan**: pick the 9–12 sub-categories (Section 6), the 3 Part 6 essay questions (3 different essay types), the 3–4 Part 9 homework questions (other types), and the 12–15 question-bank items. Make sure Part 3 contains ideas for every chosen question.
5. **Write `source/NN_Topic.md`** part by part, in the order of Section 4. Long topics can be written in several passes (Parts 0–2, then Part 3, then Parts 4–9).
6. **Build** with `python tools/build_pdf.py source/NN_Topic.md Output/T2_NN_Topic_Idea_Bank.pdf`.
7. **Verify** (Section 10).
8. **Update the Progress Log** (Section 13), including every IELTS Liz code used.
9. **Report** to the learner: file path, page count, categories covered, the 3 essay questions, the homework questions, and the suggested next topic.

---

## 10. Verification checklist (before reporting)

Content:

- [ ] All 10 parts (Part 0 – Part 9) present, in order, with Homework Essays last.
- [ ] Part 6 essays and Part 9 homework use IELTS Liz questions (code shown), with no repeats inside the chapter or from earlier chapters.
- [ ] 3–4 homework essays, each with essay type, idea pointers, Bangla thinking prompts, collocations and a sentence target, and **no model answer**.
- [ ] 9–12 category passages, each **450+ words** (count them with a script).
- [ ] Every ★ common question is covered by ideas in Part 3 and appears in Part 7.
- [ ] 45–60 vocabulary items, each with Bangla meaning, collocations and an example.
- [ ] 12–15 sentence patterns with 2 topic examples each.
- [ ] 3 Bangla essays, each with the 4 headings (Introduction / Body Paragraph 1 / Body Paragraph 2 / Conclusion), structure tags, a plan and a word bank.
- [ ] **No English version** of the Bangla essays.
- [ ] Private English drafts counted: every essay meets Intro 30–35+, BP1 100–120+, BP2 100–120+, Conclusion 30–35+, total 260+.
- [ ] Bangla headings show the word targets; homework shows the word plan.
- [ ] Sentence tags match the real grammar of the English draft (e.g. "The reason is *that*…" = Complex, not Simple; "…, who…" = Complex).
- [ ] No stray Hindi (Devanagari) letters in the Bangla text: search for `[ऀ-ॣ०-ॿ]` (the danda । U+0964 is allowed).
- [ ] No rare/"showy" vocabulary from the Section 7 avoid list.
- [ ] No invented statistics or named studies.

Layout (render 3–4 pages to PNG and look at them):

- [ ] Bangla letters render correctly (যুক্তাক্ষর, কার signs in the right place).
- [ ] Body text is 15–16 pt and easy to read.
- [ ] Tables do not overflow the page.
- [ ] Each Part and each essay starts on a new page.
- [ ] Page numbers appear at the bottom.

Quick word-count check (example):

```
python -c "import re,sys;t=open('source/02_Technology.md',encoding='utf-8').read();[print(s[:40].strip(),len(re.findall(r'[A-Za-z]+',s))) for s in t.split('\n### ')[1:]]"
```

---

## 11. Quality bar — what "good" looks like

- A learner who reads only Part 2 + the Idea Bank table can plan any question on the topic in 5 minutes.
- A learner who reads Part 3 has at least 40 usable ideas with examples.
- Each Bangla essay, translated well, produces a **band 7+ essay of 260–310 words** (Intro 30–35+, BP1 100–120+, BP2 100–120+, Conclusion 30–35+) with a clear position, two developed body paragraphs and varied sentence structures.
- Vocabulary feels natural and usable, not memorised and forced.

---

## 12. Recommended study order (for the learner)

Based on how often topics appear: **Education → Technology → Environment → Health → Work → Government Spending → Crime → Family → Media → Culture & Globalization**, then the extra chapters (Economy, Cities, Science) if time allows.

Suggested routine per chapter (about 8 days):

| Day | Task |
|---|---|
| 1 | Parts 1–2 (idea flow + brainstorming), 3 category passages |
| 2 | 3–4 category passages, 15 vocabulary items |
| 3 | Remaining passages, 15 vocabulary items, Part 5 patterns |
| 4 | Translate Essay 1, self-check |
| 5 | Translate Essay 2, self-check |
| 6 | Translate Essay 3, self-check |
| 7 | Homework Essays 1–2 (40 minutes each, no help), self-check |
| 8 | Homework Essays 3–4, self-check, then send one essay to the AI for feedback |

---

## 13. Progress Log

Update this table after every build.

Record every IELTS Liz code used (Part 6 essays, Part 7 bank, Part 9 homework) so no question is repeated in a later chapter.

| # | Topic | Output PDF | Pages | Part 6 essays (code, type) | Part 9 homework (codes) | Part 7 Liz codes | Date | Status |
|---|---|---|---|---|---|---|---|---|
| 01 | Education | Output/T2_01_Education_Idea_Bank.pdf | 59 | EDU-11 (Opinion), EDU-20 (Discussion), EDU-01 (Adv–Disadv) — English drafts 327 / 302 / 289 words | EDU-12, EDU-06, EDU-15, EDU-19 | EDU-02, EDU-03, EDU-07, WRK-12, EDU-23, EDU-04, EDU-05, EDU-14, EDU-24, EDU-16, EDU-21, EDU-10, EDU-13, EDU-17 (+1 practice) | 2026-10-23 | Done |
| 02 | Technology & Internet | Output/T2_02_Technology_Idea_Bank.pdf | 65 | TEC-02 (Opinion), TEC-07 (Discussion), TEC-03 (Two-part) | TEC-08, COM-11, TEC-04, TEC-09 | COM-10, TEC-10, COM-14, COM-15, CRI-01, TEC-01, BUS-02, BUS-08, COM-13, CRI-15, TEC-06, TEC-05 (+3 practice) | 2026-10-23 | Done |
| 03 | Environment | Output/T2_03_Environment_Idea_Bank.pdf | 64 | ENV-13 (Discussion), ENV-10 (Cause–Solution), ENV-11 (Opinion) — English drafts 293 / 301 / 305 words | ENV-09, TOU-09, ENV-05, ENV-14 | ENV-02, ENV-03, ENV-06, ENV-08, ENV-15, ENV-17, TOU-10, HOU-02, ENV-01, ENV-04, ENV-07, ENV-12, ENV-16 (+2 practice) | 2026-10-23 | Done |
| 04 | Health & Lifestyle | Output/T2_04_Health_Idea_Bank.pdf | 63 | HEA-01 (Opinion), FOO-10 (Adv–Disadv), HEA-02 (Cause–Solution) — English drafts 288 / 314 / 307 words | HEA-07, HEA-09, FOO-07, HEA-05 | HEA-04, HEA-06, HEA-08, FOO-02, FOO-04, FOO-11, SPO-04, SPO-06, SPO-07, GOV-01, FOO-05, HEA-03, FOO-08, FOO-13 (+1 practice) | 2026-10-24 | Done |
| 05 | Government & Public Spending | Output/T2_05_Government_Idea_Bank.pdf | 64 | ART-01 (Opinion), SPA-03 (Discussion), Practice ★ public transport vs roads (Adv–Disadv) — English drafts 327 / 289 / 296 words | Practice ★ defence vs education (Two-part), GOV-06, SPO-05, TRA-08 | GOV-02, GOV-04, GOV-05, ART-06, SPA-02, SOC-03, GOV-03, SPA-01, SOC-04 (+5 practice) | 2026-10-24 | Done |
| 06 | Work & Employment | Output/T2_06_Work_Idea_Bank.pdf | 63 | WRK-13 (Adv–Disadv), WRK-19 (Two-part), WRK-06 (Cause–Solution) — English drafts 288 / 304 / 302 words | WRK-08, WRK-03, WRK-01, WRK-14 | WRK-04, WRK-15, WRK-17, WRK-18, BUS-15, BUS-01, BUS-13, LEI-02, WRK-07, WRK-09, WRK-02, WRK-05, WRK-16, BUS-16 (+1 practice) | 2026-10-24 | Done |
| 07 | Crime & Punishment | Output/T2_07_Crime_Idea_Bank.pdf | 62 | CRI-12 (Opinion), CRI-02 (Cause–Solution), CRI-09 (Adv–Disadv) — English drafts 304 / 287 / 299 words | CRI-11, CRI-10, CRI-03, CRI-13 | CRI-04, CRI-05, CRI-06, CRI-08, CRI-14, CRI-16, MED-02, CRI-07 (+4 practice) | 2026-10-25 | Done |
| 08 | Family & Society | Output/T2_08_Family_Idea_Bank.pdf | 63 | FAM-11 (Opinion), FAM-06 (Discussion), FAM-04 (Two-part) — English drafts 289 / 301 / 307 words | Practice ★ nuclear vs joint (Adv–Disadv), FAM-07, FAM-12, FAM-09 | FAM-05, FAM-13, SOC-02, COM-05, COM-17, COM-06, COM-16, COM-20, FAM-02, FAM-08, FAM-10, FAM-01, FAM-03 (+1 practice) | 2026-10-25 | Done |
| 09 | Media & Advertising | Output/T2_09_Media_Idea_Bank.pdf | 61 | MED-11 (Opinion), MED-10 (Adv–Disadv), MED-05 (Two-part) — English drafts 294 / 296 / 288 words | Practice ★ fake news (Problem–Solution), MED-06, MED-04, MED-03 | MED-07, MED-09, MED-14, MED-16, BUS-05, BUS-09, REA-01, SPO-08, COM-07, COM-08, MED-01, MED-08, REA-04, MED-15, BUS-06 | 2026-10-25 | Done |
| 10 | Culture & Globalization | Output/T2_10_Culture_Globalization_Idea_Bank.pdf | 63 | SOC-05 (Adv–Disadv), MED-13 (Opinion), SOC-07 (Two-part) — English drafts 282 / 293 / 283 words | TOU-05, TOU-03, LAN-02, MED-12 | TOU-04, TOU-07, SOC-13, LAN-01, LAN-04, LAN-05, ART-02, ART-05, BUS-07, TOU-08, LAN-06, TOU-01, TOU-06, SOC-08, SOC-09 | 2026-10-25 | Done |
| 11 | Economy & Business (extra) | — | — | — | — | — | — | Not started |
| 12 | Cities, Housing & Transport (extra) | — | — | — | — | — | — | Not started |
| 13 | Science, Space & Research (extra) | — | — | — | — | — | — | Not started |

---

## 13A. Extra chapters (11–13) — on hold

The learner decided on 2026-10-26 **not** to build the extra chapters (Economy, Cities, Science) for now, because the 10 core chapters already cover enough topics for the available study time. Do not build them unless the learner asks again.

## 13B. Model Answer Sheets (companion to each chapter)

When the learner asks for model answers for a topic (e.g. "model answers for education"), build a **Model Answer Sheet** containing **every IELTS Liz question used in that chapter**: the topic's main Liz section plus the related Liz questions the chapter already used in Part 6, Part 7 and Part 9 (skip near-duplicates and say so). Each question gets a band 7+ English essay. These sheets are separate from the chapter PDFs: here English answers **are** wanted.

Rules:

- **Length:** every essay **260–280 words** — Intro 30–35+, BP1 100+, BP2 100+, Conclusion 30+. Check with `tools/model_count.py` (it flags any essay outside these limits).
- **PEEL(R) structure:** every body paragraph follows Point → Explain → Example → Link, plus **R (Response)** when conceding and answering the other side ("Admittedly… However…"). Each sentence in the source starts with a tag: `{P}` `{E}` `{X}` `{L}` `{R}`; the PDF shows them as coloured labels.
- **Use the chapter's Idea Bank:** take ideas, examples and collocations from that topic's Part 3 and Part 4, and **bold** the collocations. Each essay's `ideas:` field names the Part 3 categories used.
- **Reuse Idea Bank sentences (learner's request, 2026-10-26):** wherever a sentence from the chapter's Part 3 passages or Part 5 patterns fits the essay, copy it **word for word** (or with only tiny changes, such as dropping "also" or a linker) instead of writing a new one. This cuts reading time and builds confidence, because the learner recognises sentences already studied. Aim for **3–8 reused sentences per essay**. Wrap each reused sentence or phrase in `[[ ]]`; the PDF highlights it in light green, and the plan table shows the count. Do **not** mark a sentence as reused if it only follows a pattern loosely.
- **Verify reuse:** run `model_count.py --source source/NN_Topic.md …`; it reports any `[[ ]]` sentence that is not an exact phrase in the chapter and has a similarity below 0.75. Fix or unmark every reported sentence. When a question belongs to another chapter's theme (e.g. rural teachers in the Work section), reuse that chapter's sentences too and pass both files: `--source source/06_Work.md,source/01_Education.md`; name the other chapter in the essay's `ideas:` field.
- **Advantages & disadvantages essays (learner's request, 2026-10-28):** these follow `IELTS_Advantages_Disadvantages_Essay_Guide.md` instead of the 260–280 rule. Add `format: advdis` to the essay block. Shape: 3-sentence intro with an **Although** sentence (no "but") → BP1 advantages and BP2 disadvantages, each exactly 7 sentences tagged `{T}{P}{E}{X}{P}{E}{S}` (T = Topic, S = Summary) with the guide's fixed linkers → 3-sentence conclusion with a **While** sentence. Limits: Intro 40–50 · each body 120–135 · Conclusion 35–45 · total 330–360. **Type 1 (no opinion asked):** the introduction ends on the Although sentence and the conclusion on the While sentence. There is no opinion sentence and no plan sentence ("This essay will examine…"), because the learner says it reads as memorised. Limits: Intro 30–40 · Conclusion 25–35 · total 310–340. `model_count.py` checks the tags, linker chain, Although/While and word ranges for every `advdis` essay. **Emphasis rule (guide Section 2):** the side the essay supports always goes after the comma in both the Although and While sentences. Type 1 puts the disadvantages first by default. An essay that supports the disadvantages gets `side: disadvantages`, uses the guide's disadvantages-side formulas, and ends BP2 with "Although some [people] …, these [problems] often …". The checker tests the opinion sentences for each type and the BP2 summary opener; check the order inside Although/While by eye. Essays labelled Opinion (e.g. "What do you think of this trend?") keep the normal PEEL(R) format.
- **Agree / disagree essays (learner's request, 2026-11-01):** these follow `IELTS_Agree_Disagree_Essay_Guide.md` instead of the 260–280 rule. Add `format: agree` and `type: Agree / Disagree` to the essay block. Always one clear side, never a partial answer. Shape: 2-sentence intro ending "I completely agree/disagree with this view because [Idea 1] and [Idea 2]." → BP1 tagged `{P}{E}{E}{X}{L}` (The main reason why I agree/disagree with this idea is that… / This is because… / "; as a result," / For example… / Therefore…) → BP2 tagged `{P}{E}{X}{R}{L}` (Another important reason for my agreement/disagreement is that… / When… / For instance… / Although some people argue that…, [my side] / Consequently…) → 2-sentence conclusion starting "In conclusion, I firmly believe that". Limits: Intro 35–50 · each body 100–120 · Conclusion 35–55 · total 270–345. `model_count.py` checks the tags, openers, word ranges and banned partial phrases. This covers questions asking "do you agree?" or "to what extent?" and those with one claim followed by "What is your opinion?". Questions giving two views ("some think X, others think Y") follow the Discuss Both Views rule below, including HOU-02, even though it ends with "Do you agree or disagree?".
- **Discuss both views essays (learner's request, 2026-11-01):** these follow `IELTS_Discuss_Both_Views_Essay_Guide.md` instead of the 260–280 rule. Add `format: discuss` and `type: Discussion (both views + opinion)` to the essay block. One clean opinion, never partial, and the other view always comes first. Shape: intro of 2 sentences (or 3 with a general statement) with "While some people argue that [other view], others believe that [my view]. I completely support the latter view because [reason]." → BP1 (the other view, no "I") tagged `{P}{E}{E}{X}{L}` (On the one hand, people who… argue that… / For example… / For this reason, many people believe that…) → BP2 (my view) tagged `{P}{E}{X}{R}{L}` (On the other hand, I firmly believe that… because… / For instance… / Although some people argue that [BP1's point], [my side] / Consequently…) → 2-sentence conclusion ("In conclusion, people hold different views on whether…" / "While…, I firmly believe that… because…"). Limits: Intro 35–45 · each body 90–120 · Conclusion 35–45 · total 260–299. `model_count.py` checks the tags, openers, word ranges and banned partial phrases. Check by eye that the example shows the Explain sentence before it, and that the other view comes first even when the question states the writer's side first. This covers any question with two views or two options, including those ending "What is your opinion?". Part 6 Bangla essays on these questions are translations of the sheet's English model.
- **Cause/Problem + Solution essays (learner's request, 2026-11-01):** these follow `IELTS_Cause_Problem_Solution_Essay_Guide.md` instead of the 260–280 rule. Add `format: causesol` and `type: Cause and Solution`, `Problem and Solution` or `Consequence and Solution` to the essay block. The first question alone decides the type. No opinion and no plan sentence unless the question asks for an opinion. Shape: 2-sentence intro (paraphrase, then 2 causes or problems + ", but" + 2 solutions) → BP1 tagged `{P}{E}{X}{P}{E}{L}` (For example… / Consequently…) → BP2 tagged `{N}{E}{X}{N}{E}{L}`, where N = Solution (For instance… / In addition… / Together, these measures would…) → 2-sentence conclusion starting "In conclusion". Each solution fixes one cause or problem where that is natural, and each has WHO + WHAT + HOW. Limits: Intro 30–40 · each body 90–120 · Conclusion 30–40 · total 260–300. `model_count.py` checks the shape and limits, but read each E and X together by eye, as under the Example rule. **Relatives (guide Section 14):** questions asking only for solutions, solutions by two groups, or only problems add `shape: solutions`, `shape: groups` or `shape: problems`; each body has one idea tagged `{N}{E}{E}{X}{L}` (`{P}` for problems), the intro has no ", but", and there is still no opinion.
- **Double Question essays (learner's guide, confirmed 2026-11-03):** these follow `IELTS_Double_Question_Essay_Guide.md`. Add `format: double`, `pattern: List + Opinion`, `Opinion + List` or `List + List`, and `type: Double Question — [pattern] (…)`. Q1 = BP1, Q2 = BP2. List block tagged `{P}{E}{X}{P}{E}{L}` (`{N}` for solutions), no "I", Link "Consequently," / "As a result," / "Together, these measures would…". Opinion block tagged `{P}{E}{X}{R}{L}`, P with "I firmly believe that" ("As for whether …" in BP2), R "Although some people argue that…", Link "Therefore,". "For example" in BP1, "For instance" in BP2. 2-sentence intro ("[Answer 1], and [answer 2].") and conclusion ("In conclusion, …"); "I firmly believe that" in both only when there is an Opinion block. Limits: Intro 30–40 · each body 90–120 · Conclusion 30–40 · total 260–300. Questions shaped "What are the advantages? Do the disadvantages outweigh them?" (TEC-05) go to the Advantages/Disadvantages guide.
- **No partial positions anywhere:** Type 3 advantages essays end "Overall, I believe this is a positive/negative development." without "largely" (changed 2026-11-03 in the guide and in FAM-12, LAN-02, WRK-01 and TEC-01).
- **Example rule for agree and advantages essays (learner's request, 2026-11-01):** in `format: agree` and `format: advdis` essays, the example `{X}` must show the situation in the Explain sentence directly before it, not just the general topic. In BP1 of `format: agree`, that means the second `{E}`. The Link `{L}` must return to that paragraph's idea with no new idea, and R is the only sentence that may come from outside the chain. `model_count.py` cannot check meaning, so read each E and X together by eye when writing or reviewing an essay.
- **Body paragraph rules (learner's request, 2026-11-01):** `IELTS_Body_Paragraph_Rules.md` holds the general PEEL/PEERL rules for every essay type. Follow it when writing or reviewing body paragraphs. The rules are flexible guides: never make a paragraph robotic to tick a rule. Word limits in the essay-type guides and `model_count.py` are unchanged.
- Plain band-7 vocabulary (Section 7 rules), no invented statistics, general Bangladeshi examples where natural.
- Clear position in the introduction, repeated in the conclusion.

Files and build:

```
source/model_answers/NN_Topic/essays_*.txt     ← one block per essay (@@ CODE, title, type, pos, ideas, I, B1, B2, C)
python tools/model_count.py --source source/NN_Topic.md source/model_answers/NN_Topic/essays_*.txt
python tools/build_model_answers.py source/IELTSLiz_Question_Bank.md source/NN_Topic_Model_Answers.md \
       source/model_answers/NN_Topic --chapter "NN · Topic Name" --topic "Topic" --bangla "CODE-1, CODE-2, CODE-3"
python tools/build_pdf.py source/NN_Topic_Model_Answers.md Output/T2_NN_Topic_Model_Answers.pdf
```

**All-in-one phone PDF (learner's request, 2026-11-03):** `python tools/build_all_answers.py Output/T2_All_Model_Answers_Mobile.pdf` merges all 10 sheets into one 90 × 160 mm PDF for reading on the road: each Liz question and its sample answer only (no plan box, labels, word counts or highlights), grouped by topic with a chapter outline. Rebuild it after any sheet change.

Essays appear in the order of the source files (essays_a, essays_b, …). If a Liz question has typos, add a correction to the `FIX` dictionary in `build_model_answers.py`.

| # | Topic | Output PDF | Questions | Reused sentences | Pages | Date |
|---|---|---|---|---|---|---|
| 01 | Education | Output/T2_01_Education_Model_Answers.pdf | EDU-01 – EDU-25 (all 25), 265–279 words each; adv/disadv essays EDU-01, EDU-16, EDU-21, EDU-25 rewritten to the guide format on 2026-10-28 (Type 1 essays have 2-sentence intros and conclusions, 333–337 words; opinion essays 354–359) | — (rule added later; the 4 rewritten essays reuse 9) | 68 | 2026-10-26 |
| 02 | Technology & Internet | Output/T2_02_Technology_Model_Answers.pdf | TEC-01 – TEC-10, COM-10, COM-11, COM-13, COM-14, COM-15, CRI-01, CRI-15, BUS-02, BUS-08 (19; COM-12 skipped as a near-duplicate of TEC-08), 266–279 words each; adv/disadv essays TEC-01, COM-11, COM-13, BUS-02, BUS-08 rewritten to the guide format on 2026-10-28 (Type 1 essays have 2-sentence intros and conclusions, 335–337 words; TEC-01 356) | 107 (all verified) | 51 | 2026-10-26 |
| 03 | Environment | Output/T2_03_Environment_Model_Answers.pdf | ENV-01 – ENV-17 (all 17), TOU-09, TOU-10, HOU-02 (20), 267–280 words each | 135 (all verified) | 52 | 2026-10-26 |
| 04 | Health & Lifestyle | Output/T2_04_Health_Model_Answers.pdf | HEA-01 – HEA-09, FOO-01 – FOO-13, SPO-04, SPO-06, SPO-07, GOV-01 (26), 266–280 words each; adv/disadv essays FOO-03, FOO-06 (Type 1, 336–338 words), FOO-10, FOO-12 (disadvantages side, 351–358) rewritten to the guide format on 2026-10-28 | 156 (all verified; FOO-01, FOO-03, FOO-06 have none, as GM and local food are not in the Idea Bank) | 67 | 2026-10-27 |
| 05 | Government & Public Spending | Output/T2_05_Government_Model_Answers.pdf | GOV-01 – GOV-03, GOV-05, GOV-06, ART-01, ART-06, SPA-01 – SPA-03, SOC-03, SOC-04, SPO-05, TRA-08 (14; GOV-04 skipped as a near-duplicate of ART-06), 272–279 words each | 95 (all verified; GOV-03 also reuses Ch. 04 Health sentences) | 38 | 2026-10-27 |
| 06 | Work & Employment | Output/T2_06_Work_Model_Answers.pdf | WRK-01 – WRK-19 (all 19), BUS-01, BUS-13, BUS-15, BUS-16, LEI-02 (24), 267–279 words each; adv/disadv essays WRK-07, WRK-09, WRK-13 (Type 1, 335–337 words) and WRK-01 (Type 3, disadvantages side, 358) rewritten to the guide format on 2026-10-29 | 126 (all verified; WRK-03, WRK-11 and WRK-12 also reuse Ch. 01 Education sentences) | 67 | 2026-10-27 |
| 07 | Crime & Punishment | Output/T2_07_Crime_Model_Answers.pdf | CRI-01 – CRI-16 (all 16), MED-02 (17), 268–280 words each | 134 (all verified; CRI-06 also reuses Ch. 06 Work sentences; CRI-01 and CRI-15 are second answers, the Technology sheet has the first) | 42 | 2026-10-27 |
| 08 | Family & Society | Output/T2_08_Family_Model_Answers.pdf | FAM-01 – FAM-13 (all 13), SOC-02, COM-05, COM-06, COM-16, COM-17, COM-20 (19), 269–280 words each; adv/disadv essays FAM-02, FAM-10 (Type 1, 331–335 words), FAM-08 (Type 2, 357) and FAM-12 (Type 3 positive/negative, 354) rewritten to the guide format on 2026-10-29 | 116 (all verified; COM-05 and COM-06 also reuse Ch. 04 Health sentences, COM-20 reuses Ch. 06 Work sentences) | 51 | 2026-10-28 |
| 09 | Media & Advertising | Output/T2_09_Media_Model_Answers.pdf | MED-01 – MED-11, MED-14 – MED-16, BUS-05, BUS-06, BUS-09, COM-07, REA-01, REA-04, SPO-08 (21; COM-08 skipped as a near-duplicate of MED-06; MED-12 and MED-13 belong to the Culture sheet, where MED-13 is a Bangla essay), 266–279 words each | 160 (all verified; MED-02 is a second answer, the Crime sheet has the first; BUS-06 also reuses Ch. 10 Culture and Ch. 06 Work sentences) | 53 | 2026-10-28 |
| 10 | Culture & Globalization | Output/T2_10_Culture_Model_Answers.pdf | TOU-01 – TOU-07, LAN-01, LAN-02, LAN-04 – LAN-06, SOC-05, SOC-07, SOC-08, SOC-09, SOC-13, ART-02, ART-05, BUS-07, MED-12, MED-13 (22; TOU-08 is answered by LAN-02, LAN-03 by EDU-25 in the Education sheet, TOU-09 and TOU-10 in the Environment sheet), 270–280 words each; adv/disadv essays LAN-06 (Type 1, 333 words), SOC-05 (discuss + opinion as Type 2, 358) and LAN-02 (Type 3 negative, 359) rewritten to the guide format on 2026-10-29 | 161 (all verified; TOU-02 reuses Ch. 03 Environment sentences) | 61 | 2026-10-28 |

**Update 2026-11-01:** 84 agree/disagree essays across all 10 sheets were rewritten to the guide format and all 10 PDFs rebuilt (Education 6, Technology 7, Environment 9, Health 14, Government 7, Work 6, Crime 9, Family 5, Media 11, Culture 10). The question, reuse and page figures in the table above were recorded before this update. Bangla essays for EDU-11, TEC-02, ENV-11, HEA-01, ART-01, MED-11 and MED-13 in the Idea Bank chapters were not changed, so their position may differ from the model answer; each sheet's "How to Use" box says so. Later the same day, 43 body paragraphs in these two essay types (38 agree, 5 advantages) were corrected under the Example rule in §13B and the PDFs rebuilt. Other essay types were not reviewed under that rule.

**Update 2026-11-01 (Cause/Problem + Solution):** 15 essays were rewritten to the guide format and 8 PDFs rebuilt: EDU-22, TEC-08, ENV-10, HEA-02, HEA-09, FOO-08, FOO-13, WRK-02, WRK-06, WRK-11, CRI-02, CRI-13, BUS-06, TOU-02 and TOU-03 (260–300 words each). HEA-09 and TOU-02 match the guide's model essays. The Bangla essays for HEA-02, ENV-10, WRK-06 and CRI-02 in the Idea Bank chapters were not changed; each affected sheet's "How to Use" box says so. Related questions were not converted: causes + problems (WRK-10, WRK-14, FAM-07), solutions only (EDU-15, CRI-15, TOU-06, ENV-12, ENV-16) and problems only (TEC-06, FAM-03).

**Update 2026-11-01 (Discuss Both Views):** 43 essays were rewritten to the guide format across all 10 sheets (Education 8, Technology 2, Environment 5, Health 3, Government 7, Work 5, Crime 2, Family 5, Media 5, Culture 1), including the 10 that were labelled "Opinion (two views)" or "Opinion (two options)". Seven Part 6 Bangla essays were rewritten as translations of these models (EDU-20, TEC-07, ENV-13, SPA-03, CRI-12, FAM-06, FAM-11). The Part 9 briefs for these question types (EDU-19, TEC-04, ENV-05, HEA-07, GOV-06, SPO-05, WRK-03, CRI-10, MED-04, TOU-05) and the Part 2G Discussion row were updated. All 20 PDFs were rebuilt.

**Update 2026-11-03 (all essays now follow the five guides):** the 41 sheet essays that followed no guide were rewritten: 28 Double Question (`format: double`; WRK-10, HEA-03 and FAM-04 match the guide's Model Essays C, B and A), 4 Advantages/Disadvantages (TEC-05, TOU-09 Type 2; CRI-09, MED-10 Type 1), 8 Cause/Problem + Solution relatives (`shape:`; EDU-15, CRI-15 ×2, TOU-06, ENV-16 solutions; ENV-12 groups; TEC-06, FAM-03 problems) and EDU-12 (Agree, "What do you think of this trend?"). All 207 essays pass `model_count.py` (759 reused sentences verified). In the Idea Banks, all 30 Part 6 Bangla essays are now sentence-by-sentence translations of the sheet's English models with guide headings, word targets, fixed openers and new word banks; the Government practice essay (public transport vs roads) is Type 1 adv/disadv with its English draft kept only in the scratchpad. The Part 2F worked demos, the Part 2G table (one row per guide, plus the Bangla word-plan box) and all 30 non-discussion Part 9 briefs were rewritten to the guides, removing every "partly / largely / mostly" position. All 20 PDFs rebuilt (Idea Banks 73–84 pages, sheets 43–83 pages). Later the same day, the rest of each chapter was aligned too: the Part 0 "How to Use" word plan and Part 8 checklist item 8 now point to the guides' word plans, the Part 2A examples name the guide, and the Part 7 Question Bank is regrouped under the five guides (Agree / Disagree, Discuss Both Views, Advantages – Disadvantages, Cause/Problem + Solution, Double Question) with a **Guide:** line on every question; practice questions without a sheet answer were classified by the guides' 5-second test.

## 14. Final operating checklist (short version)

1. Command received → map it to a chapter (Section 2).
2. Read this file + reference PDFs + `source/IELTSLiz_Question_Bank.md`.
3. Plan categories, 3 essays and 3–4 homework questions (unused IELTS Liz codes), plus the question bank.
4. Write `source/NN_Topic.md` (Parts 0–9, homework last).
5. Build PDF with Chrome pipeline.
6. Verify content + layout.
7. Update Progress Log with all codes used.
8. Report and suggest the next topic.
