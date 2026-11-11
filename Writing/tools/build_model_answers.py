"""Assemble a model-answer sheet (Markdown) from essays_*.txt files.

Usage (from the Writing folder):
  python tools/model_count.py --source source/02_Technology.md source/model_answers/02_Technology/essays_*.txt
  python tools/build_model_answers.py source/IELTSLiz_Question_Bank.md source/02_Technology_Model_Answers.md \
         source/model_answers/02_Technology --chapter "02 · Technology & Internet" --topic Technology \
         --bangla "TEC-02, TEC-07, TEC-03"
  python tools/build_pdf.py source/02_Technology_Model_Answers.md Output/T2_02_Technology_Model_Answers.pdf

Essay file format (one block per essay):
  @@ CODE
  title: short topic title
  type: essay type
  pos: position
  ideas: Idea Bank Part 3 categories used
  I: introduction
  B1: body paragraph 1 with {P}/{E}/{X}/{L}/{R} sentence tags
  B2: body paragraph 2
  C: conclusion
Sentences wrapped in [[ ]] are reused from the chapter's Idea Bank and are highlighted.
"""
import re, sys, glob, os, argparse
sys.path.insert(0, os.path.dirname(__file__))
from model_count import parse, wc

ap = argparse.ArgumentParser()
ap.add_argument('bank'); ap.add_argument('out'); ap.add_argument('essays_dir')
ap.add_argument('--chapter', default='01 · Education')
ap.add_argument('--topic', default='Education')
ap.add_argument('--bangla', default='EDU-11, EDU-20, EDU-01')
args = ap.parse_args()

bank = {}
for line in open(args.bank, encoding='utf-8'):
    m = re.match(r'- \*\*([A-Z]{3}-\d+)\*\* (.*)', line.strip())
    if m:
        q = re.sub(r'\s*\((Reported|reported|repeated|common|frequent|appears|quite|discipline|as mentioned|similar|\d{4})[^)]*\)', '', m.group(2)).strip()
        bank[m.group(1)] = q

FIX = {
    'To what extend': 'To what extent', 'Do what extent': 'To what extent',
    'have remained such as reading, writing and maths': 'have remained the same, such as reading, writing and maths',
    'some people think that computer skill be made as a fourth skill to be added to the list': 'some people think that computer skills should be added to the list as a fourth basic skill',
    'given homework everyday': 'given homework every day', 'get homework everyday': 'get homework every day',
    'over enthusiastic': 'over-enthusiastic', 'parents which can': 'parents, which can',
    'advantages and disadvantages of children of having': 'advantages and disadvantages for children of having',
    'spent on teacher.': 'spent on teachers.', 'advantages and disadvantage of this': 'advantages and disadvantages of this',
    'hand writing': 'handwriting', 'ever increasing': 'ever-increasing',
    # Technology / communication / crime / business
    'done in the home by hands': 'done in the home by hand',
    'more free time for women and has enabled': 'more free time for women and have enabled',
    'in most work places': 'in most workplaces',
    'More and more children as accessing': 'More and more children are accessing',
    'break down in family': 'breakdown in family', 'face to face communication': 'face-to-face communication',
    'rather than being face to face': 'rather than face to face',
    'online communication are short and basic': 'online communication is short and basic',
    'enabling people, who would normally never have the chance to meet, to communicate': 'enabling people who would normally never have the chance to meet to communicate',
    'due to advance technology': 'due to advanced technology',
    'for both individuals and companies to shopping online': 'of shopping online for both individuals and companies',
    'tackle this problem ?': 'tackle this problem?',
    # Environment
    'that are more important? Do you agree': 'that are more important. Do you agree',
    'more effective ways do to this': 'more effective ways to do this',
    'ever growing urban centers': 'ever-growing urban centres', 'ever growing population': 'ever-growing population',
    'some urban centers': 'some urban centres', 'and boost economies': 'and boost the economy',
    'Some people says trees': 'Some people say trees', 'while other says housing facilities should be build instead': 'while others say housing should be built instead',
    'Do you agree or disagree ?': 'Do you agree or disagree?',
    # Health
    'amount of time spend on sport': 'amount of time spent on sport',
    'overweight children? Do you think this the best way': 'overweight children. Do you think this is the best way',
    'The heath of a person': 'The health of a person', 'is a the responsibility': 'is the responsibility',
    'could result many problems': 'could result in many problems',
    # Work
    'should be payed more': 'should be paid more', 'get a part time job': 'get a part-time job',
    'in the modern work place': 'in the modern workplace',
    'in rural areas which can have': 'in rural areas, which can have',
    'valued equally while others': 'valued equally, while others',
    'think that when recruiting, companies': 'think that, when recruiting, companies',
    'work independently while others considered they should recruit': 'work independently, while others consider that they should recruit',
    'hungry for money as they will': 'hungry for money, as they will',
    # Government, arts, space, aid
    'spending on defense': 'spending on defence', 'lower the budget on the arts': 'lower the budget for the arts',
    'think that government is wasting money': 'think that the government is wasting money',
    'the problems of public.': 'the problems of the public.',
    'Most societies has its homeless people': 'Most societies have homeless people',
    'help them in their development plans': 'help them with their development plans',
    'financial aid is important but others suggest that practical aid and advice are more important?':
        'financial aid is important, but others suggest that practical aid and advice are more important.',
    'host international sports event,': 'host international sports events,', 'both views & give': 'both views and give',
    'on other planets and messages should be sent': 'on other planets and that messages should be sent',
    'A poor infrastructure hinders': 'Poor infrastructure hinders',
    # Crime
    'as soon as they released': 'as soon as they are released',
    'think that regardless of age, teenagers': 'think that, regardless of age, teenagers',
    'Crime rate, in most countries, is often higher': 'The crime rate in most countries is often higher',
    # Family, society and personality
    'Therefore they should be encouraged': 'Therefore, they should be encouraged',
    'both parents working and as a result children': 'both parents working, and as a result, children',
    "into their 90's": 'into their 90s', 'elderly members or should the government': 'elderly members, or should the government',
    'pervious': 'previous',
    'To what extent do you agree. Note: This question can also be about stress.': 'To what extent do you agree?',
    'predetermined as a result of our genes before we are born and there is': 'predetermined by our genes before we are born, and there is',
    'take our time to know them better': 'take our time to get to know them better',
    # Media, advertising and reading
    'is bad news such as wars': 'is bad news, such as wars',
    'Others say that amount of time': 'Others say that the amount of time',
    'Discuss both views and give own opinion': 'Discuss both views and give your own opinion.',
    'negative affects of consumerism': 'negative effects of consumerism',
    'If the product is good and meets consumer needs than advertising': 'If a product is good and meets consumer needs, then advertising',
    'marketing and promotion and as a result, people': 'marketing and promotion, and as a result, people',
    'Marketing and promotion is the key': 'Marketing and promotion are the key',
    'Nowadays celebrities are more famous': 'Nowadays, celebrities are more famous',
    # Culture, tourism and language
    'is a waste of time? To what extent do you agree or disagree.': 'is a waste of time. To what extent do you agree or disagree?',
    'choose to talk the same global language': 'choose to speak the same global language',
    'modern society is the loss': 'modern society comes the loss', 'In what way are music': 'In what ways are music',
    'travel outside of their own country': 'travel outside their own country',
    'there is an growing demand': 'there is a growing demand', 'What problems does this have on the environment?': 'What problems does this cause for the environment?',
    'travel programs on TV': 'travel programmes on TV', 'costs of traveling abroad': 'costs of travelling abroad',
    'believe that to protect local culture, tourism': 'believe that, to protect local culture, tourism',
    'travels into a different culture': 'travels to a different culture',
    'disagree? (2020': 'disagree?',
}
for k in bank:
    for a, b in FIX.items():
        bank[k] = bank[k].replace(a, b)

EDU_TITLES = {
 'EDU-01': 'International exchange visits', 'EDU-02': 'Computer skills as a fourth basic skill',
 'EDU-03': 'More funding for science subjects', 'EDU-04': 'Discipline: teachers or parents?',
 'EDU-05': 'Homework every day?', 'EDU-06': 'Parental pressure and the role of parents',
 'EDU-07': 'Cutting art and music', 'EDU-08': 'Studying literature in high school',
 'EDU-09': 'Educational activities in free time', 'EDU-10': 'Sending disruptive children out of class',
 'EDU-11': 'Free education at all levels', 'EDU-12': 'Continuous assessment instead of exams',
 'EDU-13': 'Educated people vs experience', 'EDU-14': 'When to start a foreign language',
 'EDU-15': 'Education gap: rich and poor countries', 'EDU-16': 'School uniforms',
 'EDU-17': 'Community work in the curriculum', 'EDU-18': 'Compulsory after-school activities',
 'EDU-19': 'Technology or teachers?', 'EDU-20': 'Parents vs teachers: who influences more?',
 'EDU-21': 'Single-sex schools', 'EDU-22': 'Fewer women in university science',
 'EDU-23': 'Learning in old age', 'EDU-24': 'The role of a teacher',
 'EDU-25': 'Less handwriting in schools',
}
NAMES = {'P': 'Point', 'E': 'Explain', 'X': 'Example', 'L': 'Link', 'R': 'Response',
         'T': 'Topic', 'S': 'Summary', 'N': 'Solution'}

def render(s):
    s = re.sub(r'\[\[(.*?)\]\]', r'<span class="reuse">\1</span>', s)
    return re.sub(r'\{([PEXLRTSN])\}\s*', lambda m: f'<span class="pl pl-{m.group(1)}">{NAMES[m.group(1)]}</span>', s)

def title(d):
    return d.get('title') or EDU_TITLES.get(d['code'], '')

def nreuse(d):
    return sum(len(re.findall(r'\[\[', d[k])) for k in ('I', 'B1', 'B2', 'C'))

essays = parse(sorted(glob.glob(os.path.join(args.essays_dir, 'essays_*.txt'))))
missing = [d['code'] for d in essays if d['code'] not in bank]
assert not missing, f'codes not in bank: {missing}'
total_reuse = sum(nreuse(d) for d in essays)
n_advdis = sum(d.get('format') == 'advdis' for d in essays)
n_agree = sum(d.get('format') == 'agree' for d in essays)
n_discuss = sum(d.get('format') == 'discuss' for d in essays)
n_causesol = sum(d.get('format') == 'causesol' for d in essays)
n_double = sum(d.get('format') == 'double' for d in essays)
n_plain = sum('format' not in d for d in essays)

advdis_sub = ' (Advantages & Disadvantages essays: 310–360)' if n_advdis else ''
advdis_count = ' Advantages & Disadvantages essay-গুলো আলাদা guide মেনে লেখা: **Intro 40–50 · BP1 120–135 · BP2 120–135 · Conclusion 35–45 = 330–360**; মতামত না চাইলে (Type 1) **Intro 30–40 · Conclusion 25–35 = 310–340**।' if n_advdis else ''
agree_sub = ' (Agree / Disagree essays: 270–345)' if n_agree else ''
agree_count = ' Agree / Disagree essay-গুলো আলাদা guide মেনে লেখা: **Intro 35–50 · BP1 100–120 · BP2 100–120 · Conclusion 35–55 = 270–345**।' if n_agree else ''
discuss_sub = ' (Discuss Both Views essays: 260–299)' if n_discuss else ''
discuss_count = ' Discuss Both Views essay-গুলো আলাদা guide মেনে লেখা: **Intro 35–45 · BP1 90–120 · BP2 90–120 · Conclusion 35–45 = 260–299**।' if n_discuss else ''
causesol_sub = ' (Cause/Problem + Solution essays: 260–300)' if n_causesol else ''
causesol_count = ' Cause/Problem + Solution essay-গুলো আলাদা guide মেনে লেখা: **Intro 30–40 · BP1 90–120 · BP2 90–120 · Conclusion 30–40 = 260–300**।' if n_causesol else ''
double_sub = ' (Double Question essays: 260–300)' if n_double else ''
double_count = ' Double Question essay-গুলো আলাদা guide মেনে লেখা: **Intro 30–40 · BP1 90–120 · BP2 90–120 · Conclusion 30–40 = 260–300**।' if n_double else ''
plain_sub = ' · 260–280 words' if n_plain else ''
plain_count = ' **Intro 30–35+ · BP1 100+ · BP2 100+ · Conclusion 30+ = 260–280**।' if n_plain else ''
# Part 6 Bangla essays are translations of these English models (rewritten 2026-11-03)
bangla_note = ' এই বাংলা essay-গুলো এখানকার English model-এর অনুবাদ হিসেবে লেখা, তাই একই কাঠামো ও একই idea পাবে।'
causesol_rows = '''
| <span class="pl pl-N">Solution</span> | Solution (Cause/Problem + Solution only) | Says who acts and what they do | The most effective solution is for… / In addition, … |''' if n_causesol or n_double else ''
causesol_help = ''
if n_causesol:
    causesol_help = f'''
<div class="tip" markdown="1">

**Cause/Problem + Solution essay ({n_causesol}টি) — নতুন নির্দিষ্ট কাঠামো** (IELTS_Cause_Problem_Solution_Essay_Guide.md অনুযায়ী):

- ⭐ **ধরন চেনো:** শুধু প্রথম প্রশ্নটি দেখো। কেন ঘটছে জানতে চাইলে **Cause essay**, কী ক্ষতি হচ্ছে জানতে চাইলে **Problem essay**। প্রশ্নে "this problem" থাকলেই সেটি Problem essay হয় না।
- 🚫 **মতামত নয়:** প্রশ্ন না চাইলে "I think" বা "In my opinion" লিখবে না। "This essay will…" বাক্যও লিখবে না।
- **Introduction (2টি বাক্য):** paraphrase → 2টি কারণ বা সমস্যা, but + 2টি সমাধান।
- **Body 1 = 2টি কারণ বা সমস্যা:** <span class="pl pl-P">Point</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-X">Example</span> → <span class="pl pl-P">Point</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-L">Link</span>।
- **Body 2 = 2টি সমাধান:** <span class="pl pl-N">Solution</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-X">Example</span> → <span class="pl pl-N">Solution</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-L">Link</span>।
- ⭐ **Mirror rule:** সমাধান 1 ঠিক করে কারণ বা সমস্যা 1, সমাধান 2 ঠিক করে কারণ বা সমস্যা 2। প্রতিটি সমাধানে থাকবে কে করবে, কী করবে, আর তাতে কীভাবে কাজ হবে (WHO + WHAT + HOW)।
- **Conclusion (2টি বাক্য):** কারণ বা সমস্যা নতুন শব্দে → সমাধান নতুন শব্দে + চূড়ান্ত ফল। নতুন কোনো idea নয়।
- **শব্দসংখ্যা:** সহজ হিসাব: 35 + 105 + 105 + 35 = 280।
- **একই পরিবারের অন্য প্রশ্ন (guide Section 14):** শুধু সমাধান, দুই পক্ষের সমাধান, বা শুধু সমস্যা চাইলে প্রতিটি body paragraph-এ একটিই idea: <span class="pl pl-P">Point</span>/<span class="pl pl-N">Solution</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-X">Example</span> → <span class="pl pl-L">Link</span>। মতামত নয়।

</div>
'''
double_help = ''
if n_double:
    double_help = f'''
<div class="tip" markdown="1">

**Double Question essay ({n_double}টি) — নতুন নির্দিষ্ট কাঠামো** (IELTS_Double_Question_Essay_Guide.md অনুযায়ী):

- ⭐ **ভাগ করো:** Q1 যাবে Body 1-এ, Q2 যাবে Body 2-এ, প্রশ্নের ক্রমেই। প্রতিটি প্রশ্ন আলাদা করে পরীক্ষা করো।
- **পক্ষ বেছে নিতে হলে (হ্যাঁ/না, ভালো/খারাপ) = Opinion block:** <span class="pl pl-P">Point</span> (I firmly believe that… because…) → <span class="pl pl-E">Explain</span> → <span class="pl pl-X">Example</span> → <span class="pl pl-R">Response</span> (Although some people argue that…) → <span class="pl pl-L">Link</span> (Therefore…)। Body 2-তে শুরু: As for whether…
- **কেন / কী / কীভাবে জানতে চাইলে = List block (2টি idea):** <span class="pl pl-P">Point</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-X">Example</span> → <span class="pl pl-P">Point</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-L">Link</span> (Consequently… / Together, these measures would…)। সমাধান হলে Point-এর জায়গায় <span class="pl pl-N">Solution</span>। List block-এ "I" লিখবে না।
- ⭐ **"do you think" ফাঁদ:** প্রশ্নের প্রথম শব্দ দেখো। *Why do you think…?* আসলে কারণ চায় (List), মত নয়।
- ⭐ **"other" ফাঁদ:** প্রশ্নে *other* থাকলে প্রশ্নে দেওয়া idea বাদ দিয়ে নতুন idea লেখো।
- **Introduction (2টি বাক্য):** paraphrase → [উত্তর 1], and [উত্তর 2]। মতের কারণ Introduction-এ নয়, Opinion block-এর শুরুতে।
- **Conclusion (2টি বাক্য):** In conclusion, [উত্তর 1 নতুন শব্দে]. [উত্তর 2 নতুন শব্দে]. কোনো প্রশ্নই মত না চাইলে (List + List) কোথাও "I" নয়।
- **শব্দসংখ্যা:** সহজ হিসাব: 35 + 105 + 105 + 35 = 280।

</div>
'''
discuss_help = ''
if n_discuss:
    discuss_help = f'''
<div class="tip" markdown="1">

**Discuss Both Views essay ({n_discuss}টি) — নতুন নির্দিষ্ট কাঠামো** (IELTS_Discuss_Both_Views_Essay_Guide.md অনুযায়ী):

- 🚫 **কখনো আংশিক উত্তর নয়:** একটিই স্পষ্ট মত। "both views are important", "it depends" লিখবে না।
- ⭐ **Order rule:** বিপরীত মত সবসময় আগে, তোমার মত সবসময় শেষে। তাই "the latter view" সবসময় তোমার পক্ষকেই বোঝায়।
- **Introduction:** While some people argue that [বিপরীত মত], others believe that [তোমার মত]. → I completely support the latter view because [মূল কারণ].
- **Body 1 = বিপরীত মত ("I" ছাড়া):** <span class="pl pl-P">Point</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-X">Example</span> → <span class="pl pl-L">Link</span>।
- **Body 1 linker:** On the one hand, people who… argue that… → For example… → For this reason, many people believe that…।
- **Body 2 = তোমার মত:** <span class="pl pl-P">Point</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-X">Example</span> → <span class="pl pl-R">Response</span> → <span class="pl pl-L">Link</span>।
- **Body 2 linker:** On the other hand, I firmly believe that… because… → For instance… → Although some people argue that [Body 1-এর যুক্তি], [তোমার পক্ষ] → Consequently…।
- **Conclusion (2টি বাক্য):** In conclusion, people hold different views on whether… → While [বিপরীত মত], I firmly believe that [তোমার মত] because [কারণ]।
- **শব্দসংখ্যা:** সবসময় 300-এর নিচে। সহজ হিসাব: 40 + 100 + 100 + 40 = 280।

</div>
'''
advdis_rows = '''
| <span class="pl pl-T">Topic</span> | Topic sentence (Adv/Disadv only) | Opens the paragraph with a fixed sentence | There is little doubt that… / On the other hand, it cannot be denied that… |
| <span class="pl pl-S">Summary</span> | Summary (Adv/Disadv only) | Sums up the paragraph in general words | Overall, … / Although these… |''' if n_advdis else ''
advdis_help = ''
if n_advdis:
    advdis_help = f'''
<div class="tip" markdown="1">

**Advantages & Disadvantages essay ({n_advdis}টি) — নতুন নির্দিষ্ট কাঠামো** (IELTS_Advantages_Disadvantages_Essay_Guide.md অনুযায়ী):

- **Introduction:** প্রশ্নের paraphrase → **Although** + যে দিক তুমি সমর্থন করো না (2 point), + যে দিক তুমি সমর্থন করো (2 point), but ছাড়া → মতামত (শুধু প্রশ্ন মতামত চাইলে)।
- **Body 1 = সুবিধা, Body 2 = অসুবিধা — প্রতিটিতে ঠিক 7টি বাক্য:** <span class="pl pl-T">Topic</span> → <span class="pl pl-P">Point</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-X">Example</span> → <span class="pl pl-P">Point</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-S">Summary</span>।
- **Body 1 linker:** There is little doubt that… → To begin with → This is because → For example → In addition → As a result → Overall।
- **Body 2 linker:** On the other hand, it cannot be denied that… → Firstly → "; as a result," → For instance → Secondly → If… consequently → শেষ বাক্য: Type 1 হলে Overall, these…; সুবিধার পক্ষে হলে Although these [problems]…, most…; অসুবিধার পক্ষে হলে Although some [people]…, these [problems] often…।
- **Conclusion:** In conclusion + নতুন paraphrase → **While** + দুই দিক, Although বাক্যের একই ক্রমে → মতামত আবার বলো (শুধু প্রশ্ন মতামত চাইলে)।
- 🚫 **প্রশ্ন মতামত না চাইলে (Type 1):** Introduction ও Conclusion-এ মাত্র **2টি বাক্য**। মতামত লিখবে না, আর "This essay will examine both the benefits and the drawbacks…" ধরনের plan sentence-ও লিখবে না — এটি মুখস্থ করা বাক্য মনে হয় এবং নতুন কোনো idea যোগ করে না। Introduction শেষ হবে Although বাক্যে, essay শেষ হবে While বাক্যে।
- ⭐ **Emphasis rule:** Although/While বাক্যে পাঠক সবসময় **শেষের idea (comma-র পরের অংশ)**-কে তোমার মত হিসেবে ধরে। তাই সুবিধার পক্ষে হলে আগে অসুবিধা, পরে সুবিধা; অসুবিধার পক্ষে হলে আগে সুবিধা, পরে অসুবিধা। Type 1-এ (মতামত নেই) সাধারণত আগে অসুবিধা, পরে সুবিধা।

</div>
'''

agree_help = ''
if n_agree:
    agree_help = f'''
<div class="tip" markdown="1">

**Agree / Disagree essay ({n_agree}টি) — নতুন নির্দিষ্ট কাঠামো** (IELTS_Agree_Disagree_Essay_Guide.md অনুযায়ী):

- 🚫 **কখনো আংশিক উত্তর নয়:** শুরু থেকে শেষ পর্যন্ত একটিই পক্ষ। "partly agree", "largely agree", "to some extent" লিখবে না।
- **Introduction (2টি বাক্য):** প্রশ্নের paraphrase → I completely agree/disagree with this view because + Idea 1 + Idea 2।
- **Body 1 = Idea 1:** <span class="pl pl-P">Point</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-X">Example</span> → <span class="pl pl-L">Link</span>।
- **Body 1 linker:** The main reason why I agree/disagree with this idea is that… → This is because… → "; as a result," → For example… → Therefore…।
- **Body 2 = Idea 2:** <span class="pl pl-P">Point</span> → <span class="pl pl-E">Explain</span> → <span class="pl pl-X">Example</span> → <span class="pl pl-R">Response</span> → <span class="pl pl-L">Link</span>।
- **Body 2 linker:** Another important reason for my agreement/disagreement is that… → When… → For instance… → Although some people argue that…, [তোমার পক্ষ] → Consequently…।
- **Conclusion (2টি বাক্য):** In conclusion, I firmly believe that… → Idea 1 ও Idea 2 নতুন শব্দে। নতুন কোনো idea নয়।
- ⭐ **Response বাক্য:** বিপরীত মত থাকবে Although অংশে, আর তোমার পক্ষ থাকবে comma-র পরে, but ছাড়া। তাই উত্তর আংশিক হয় না।

</div>
'''

reuse_help = ''
if total_reuse:
    reuse_help = f'''
<div class="tip" markdown="1">

**<span class="reuse">হালকা সবুজ দাগ দেওয়া বাক্য</span> = তোমার {args.topic} Idea Bank থেকে হুবহু বা প্রায় হুবহু নেওয়া।** এই sheet-এ মোট **{total_reuse}টি** এমন বাক্য আছে। এগুলো তুমি আগেই পড়েছ, তাই পড়তে কম সময় লাগবে — আর দেখবে, Idea Bank-এর বাক্যগুলো সরাসরি essay-তে ব্যবহার করা যায়। পরীক্ষায় তুমিও ঠিক এভাবে নিজের মুখস্থ করা বাক্য ব্যবহার করতে পারবে।

</div>
'''

md = [f'''<div class="cover" markdown="1">

# IELTS Writing Task 2 — Model Answers

<p class="sub">Chapter {args.chapter} · {len(essays)} IELTS Liz Questions</p>

<p class="sub">Band 7+ sample essays{plain_sub} · Every essay follows its essay-type guide · PEEL(R) paragraphs · Ideas and sentences from your {args.topic} Idea Bank</p>

</div>

## How to Use This Sheet

<div class="tip" markdown="1">

**এই sheet কীভাবে পড়বে**

1. প্রথমে প্রশ্নটি পড়ো এবং **নিজে 5 মিনিটে একটি পরিকল্পনা করো** (Idea Bank Part 2 পদ্ধতিতে)। তারপর model answer-এর "Plan" box-এর সাথে মিলিয়ে দেখো।
2. Model essay পড়ার সময় রঙিন label-গুলো লক্ষ করো — প্রতিটি body paragraph কীভাবে **Point → Explain → Example → Link** ধাপে এগোয়।
3. **Bold** করা collocation-গুলো তোমার {args.topic} Idea Bank-এর Part 4 থেকে নেওয়া — এগুলো খাতায় লিখে নিজের বাক্যে ব্যবহার করো।
4. প্রতিদিন 2–3টি essay পড়ো। একটি essay বেছে নিয়ে, model না দেখে, নিজের ভাষায় আবার লেখো (40 মিনিট)।
5. প্রতিটি essay-র শব্দসংখ্যা দেওয়া আছে।{plain_count}{advdis_count}{agree_count}{discuss_count}{causesol_count}{double_count}
6. Part 6-এর বাংলা essay ({args.bangla}) অনুবাদ করে থাকলে, এখানকার model-এর সাথে তোমার অনুবাদ মিলিয়ে দেখো।{bangla_note}

</div>
{reuse_help}
### The PEEL(R) paragraph method

| Label | Meaning | What the sentence does | Typical linkers |
|---|---|---|---|
| <span class="pl pl-P">Point</span> | Topic sentence | States the main idea of the paragraph | The main reason… / Firstly… / However, I believe… |
| <span class="pl pl-E">Explain</span> | Explanation | Says **why** or **how** the point is true (often 2–3 sentences) | This is because… / Since… / As a result… |
| <span class="pl pl-X">Example</span> | Example | Gives a specific, realistic example | For example… / For instance… / In Bangladesh… |
| <span class="pl pl-L">Link</span> | Link / result | Connects back to the question or shows the result | Therefore… / As a result… / In this way… |
| <span class="pl pl-R">Response</span> | Response to the other side | Admits the opposite view, then answers it (the **R** in PEELR) | Admittedly… / Although… / However, … |{advdis_rows}{causesol_rows}

<div class="tip" markdown="1">

**PEEL বনাম PEELR:** সাধারণ body paragraph-এ **PEEL** যথেষ্ট। কিন্তু opinion বা discussion essay-তে যখন বিপরীত মতকে মেনে নিয়ে জবাব দিতে হয় ("Admittedly… However…"), তখন **R (Response)** যোগ করো — এতে লেখা আরও পরিণত ও যুক্তিপূর্ণ দেখায়, যা Band 7-এর জন্য গুরুত্বপূর্ণ।

</div>
{advdis_help}{agree_help}{discuss_help}{causesol_help}{double_help}
### Contents

| # | Code | Topic | Essay type |
|---|---|---|---|''']
for i, d in enumerate(essays, 1):
    md.append(f"| {i} | {d['code']} | {title(d)} | {d['type']} |")

md.append('\n## Model Answers {: .part}\n')
for i, d in enumerate(essays, 1):
    c = [wc(d[k]) for k in ('I', 'B1', 'B2', 'C')]
    struct_row = '| **Structure** | Adv/Disadv guide: Although-intro → BP1 advantages (7 sentences) → BP2 disadvantages (7 sentences) → While-conclusion |\n' if d.get('format') == 'advdis' else ''
    if d.get('format') == 'agree':
        struct_row = '| **Structure** | Agree/Disagree guide: Opinion + 2 ideas → BP1 Idea 1 (P E E X L) → BP2 Idea 2 (P E X R L) → Opinion + 2 ideas in new words |\n'
    if d.get('format') == 'discuss':
        struct_row = '| **Structure** | Discuss Both Views guide: Both views + clean opinion → BP1 the other view (P E E X L) → BP2 my view (P E X R L) → Both themes + opinion in new words |\n'
    if d.get('format') == 'causesol':
        struct_row = '| **Structure** | Cause/Problem + Solution guide: 2 causes or problems + 2 solutions → BP1 (P E X P E L) → BP2, each solution fixing one point (N E X N E L) → Same ideas in new words |\n'
        shape = {'solutions': 'Solution 1 (N E E X L) → BP2 Solution 2 (N E E X L)',
                 'groups': "the first group's solution (N E E X L) → BP2 the second group's solution (N E E X L)",
                 'problems': 'Problem 1 (P E E X L) → BP2 Problem 2 (P E E X L)'}.get(d.get('shape'))
        if shape:
            struct_row = f'| **Structure** | Cause/Problem + Solution guide, Section 14: both answers in one sentence → BP1 {shape} → Same ideas in new words, no opinion |\n'
    if d.get('format') == 'double':
        b1, b2 = [b.strip() for b in d['pattern'].split('+')]
        shapes = {'List': 'List block (P E X P E L)', 'Opinion': 'Opinion block (P E X R L)'}
        struct_row = f"| **Structure** | Double Question guide ({d['pattern']}): Answer 1 + answer 2 → BP1 = Q1, {shapes[b1]} → BP2 = Q2, {shapes[b2]} → Both answers in new words |\n"
    reuse_row = f"| **Reused from Idea Bank** | {nreuse(d)} {'sentence' if nreuse(d) == 1 else 'sentences'} (highlighted) |\n" if total_reuse else ''
    md.append(f'''
<div class="essay-block" markdown="1">

### {i}. {d['code']} — {title(d)}

<div class="question">{bank[d['code']]}</div>

| Plan | |
|---|---|
| **Essay type** | {d['type']} |
| **Position** | {d['pos']} |
| **Ideas from Idea Bank (Part 3)** | {d['ideas']} |
{struct_row}{reuse_row}| **Word count** | Intro {c[0]} · BP1 {c[1]} · BP2 {c[2]} · Conclusion {c[3]} · **Total {sum(c)}** |

</div>

<div class="model" markdown="1">

<p class="plabel">Introduction <span class="wc">· {c[0]} words</span></p>

{render(d['I'])}

<p class="plabel">Body Paragraph 1 <span class="wc">· {c[1]} words</span></p>

{render(d['B1'])}

<p class="plabel">Body Paragraph 2 <span class="wc">· {c[2]} words</span></p>

{render(d['B2'])}

<p class="plabel">Conclusion <span class="wc">· {c[3]} words</span></p>

{render(d['C'])}

</div>
''')

open(args.out, 'w', encoding='utf-8').write('\n'.join(md))
print('written', args.out, len(essays), 'essays,', total_reuse, 'reused sentences')
