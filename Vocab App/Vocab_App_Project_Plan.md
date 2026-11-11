# IELTS Vocab App — Project Plan

> Status: idea / planning (started 2026-11-08)
> Platforms: iOS (App Store) + Android (Google Play)
> Working name: *to decide* — a simple name **without** "IELTS" or "Cambridge"

---

## 0. Decisions made (2026-11-08)

| # | Decision |
|---|---|
| 1 | **Reading:** no Cambridge passage text in the app. The app only *suggests* which passage to read, then teaches the vocabulary. |
| 2 | **App name:** simple name, no "IELTS" in it. |
| 3 | **Writing & Speaking:** current content plan is the *initial* version — will be modified later. |
| 4 | **My Words bank in every section:** each section has its own bank so the user can track words learned and words they got wrong. |
| 5 | **Word lists / licences:** check licence before use, or use free lists from other sources — decide later. |

**Current focus:** app structure (sections, screens, flows, data). Content comes after.

---

## 1. The idea in one line

A vocabulary app with **5 sections** (Listening, Reading, Writing, Speaking, Fluent English). Every word has **British + American pronunciation** and teaches the word *in the way that skill needs it*.

| # | Section | What the user learns | Main feature |
|---|---|---|---|
| 1 | IELTS Listening | Topic words + correct spelling | 30-Day Challenge with a test before each new day |
| 2 | IELTS Reading | Hard words from Cambridge 10–20 passages | "Do you know this word?" Yes → next, No → meaning + examples |
| 3 | IELTS Writing | Topic vocabulary + collocations | 2–3 Band 7+ style sentences per word |
| 4 | IELTS Speaking | Topic vocabulary + natural phrases | Pronunciation + 2–3 sentences to build answers |
| 5 | Fluent English | 3000–6000 most common English words | Organized later (ideas in section 6) |

**What every section shares:**
- 🔊 British (UK) and American (US) audio button for each word
- IPA for both accents (e.g. *schedule* UK /ˈʃedjuːl/, US /ˈskedʒuːl/)
- A **My Words bank in each section** (Listening, Reading, Writing, Speaking, Fluent) — tracks words learned and words missed (see section 7)
- Progress saved on the phone (works offline)

---

## 2. Section 1 — IELTS Listening (30-Day Challenge)

### How it works
1. Each day = **one category** of words (e.g. Day 1 = Months).
2. For each word the user sees:
   - the word
   - 🔊 UK and 🔊 US pronunciation
   - **common mistakes** (wrong spellings learners write)
3. **Before Day 2 opens**, the user takes a short test on Day 1.
4. After the test → **analysis** + a suggestion: go to the next day or revise.

### Example word card

```
February                       🔊 UK   🔊 US
UK /ˈfebruəri/   US /ˈfebrueri/
Common mistakes:  ✗ Februry   ✗ Febuary
Tip: two "r"s — Feb-RU-ary
```

### Test format (matches the real exam)
IELTS Listening tests **spelling**, so the test should be **listen-and-type** (dictation):
- App plays the word (UK accent mostly, sometimes US) → user types it.
- 10–15 words per test, taken from the previous day.
- Optional extra question type: pick the correct spelling from 4 options.

### Result rules (suggestion)

| Score | Message | What happens |
|---|---|---|
| 80–100% | "Great — move to Day N+1" | Next day unlocks |
| 50–79% | "Good — next day is open, but review these words" | Next day unlocks, wrong words go to *Listening → My Words* |
| below 50% | "Revise Day N first" | Suggest revising; user may still skip if they want |

> The user should always be able to skip — the app **suggests**, it does not force.

### Draft 30-day category list

| Day | Category | Day | Category |
|---|---|---|---|
| 1 | Months & days of the week | 16 | Health & body |
| 2 | Numbers, dates & time | 17 | Food & cooking |
| 3 | Alphabet & spelling names | 18 | Animals & wildlife |
| 4 | Addresses & street types (Road, Avenue, Crescent…) | 19 | Nature & environment |
| 5 | Personal information (forms) | 20 | Weather & climate |
| 6 | Transport & travel | 21 | Science & research |
| 7 | Accommodation & housing | 22 | Technology & equipment |
| 8 | Shopping & money | 23 | Media & communication |
| 9 | Jobs & workplace | 24 | Buildings & places in a town |
| 10 | Education & university | 25 | Maps & directions |
| 11 | Course & study words (Part 3) | 26 | Tourism & tours |
| 12 | Sports & leisure | 27 | History & museums |
| 13 | Clubs, events & booking | 28 | Business & marketing |
| 14 | Hotel & restaurant | 29 | Commonly misspelled words (mixed) |
| 15 | Furniture & home items | 30 | Final mixed test (all 29 days) |

Source of words: our own lists — [Listening/](../Listening/) and [Writing/IELTS_Spelling_Fix_List.md](../Writing/IELTS_Spelling_Fix_List.md).

---

## 3. Section 2 — IELTS Reading (Cambridge 10–20)

### Structure
```
Reading
 ├── Passage 1  → Cambridge 10 … Cambridge 20 (each book: Test 1–4)
 ├── Passage 2  → same
 └── Passage 3  → same
```
- Suggested order: finish all Passage 1 (C10–C20) → then Passage 2 → then Passage 3.
- The user can **skip** to any passage level, any book, any test.

### Flow for one passage
1. App says: *"Read Cambridge 15, Test 2, Passage 1 — 'The History of Glass'"* (user reads it in their own book).
2. App shows **10–12 key words** from that passage, one by one.
3. For each word:
   - word + 🔊 UK / US
   - question: **"Do you know the meaning?"**
     - **Yes** → next word (optional quick check: pick the meaning from 3 options, so "Yes" is honest)
     - **No** → show the meaning + 1–2 example sentences → word goes to *Reading → My Words* as "missed"
4. End screen: "You knew 8/12 words" + list of new words.

> ✅ **Decided:** no Cambridge passage text inside the app. We only *suggest* the passage to read, then teach the words with **our own** meanings and **our own** example sentences.

Source: our existing [Cambridge eBooks/By Category/](../Cambridge%20eBooks/By%20Category/) work covers C10–C14. C15–C20 need to be collected.

---

## 4. Section 3 — IELTS Writing

- Organized by **topic**, using our Writing Idea Bank: Education, Technology, Environment, Health, Crime, Work, Government, Media, Globalisation, Transport… (same 10 chapters as our topic PDFs).
- Each topic has:
  - **Vocabulary** (word + meaning + 🔊 UK/US)
  - **Collocations** (e.g. *carbon emissions*, *tackle climate change*, *renewable energy sources*)
  - **2–3 IELTS Writing-standard sentences** per word/collocation

### Example
```
Environment → "tackle"  (verb)  🔊 UK  🔊 US
Meaning: to make a serious effort to deal with a problem
Collocations: tackle pollution · tackle climate change · tackle the root cause
Sentences:
 1. Governments must work together to tackle climate change.
 2. Stricter laws are needed to tackle air pollution in big cities.
```

Source: [Writing/](../Writing/) idea bank + model essays (all already follow our five essay guides).

---

## 5. Section 4 — IELTS Speaking

- Organized by **category** (Person, Place, Object, Event, Activity, … — same as our Speaking category banks).
- Each word/phrase has: 🔊 UK/US pronunciation, meaning, **2–3 spoken-style sentences**.

> 📝 **Note:** the Writing and Speaking sections are the **initial plan**. Their content (and how they differ from each other) will be modified later. The app structure stays the same.

Source: [Speaking/](../Speaking/) category banks + Makkar cue cards.

---

## 6. Section 5 — Fluent English (to organize later)

Goal: the **3000–6000 most common English words**, which research says cover most everyday English.

Ideas for later:
- Split into **frequency bands**: 1–500, 501–1000, … up to 6000.
- Inside each band, group by theme so it doesn't feel like a dictionary.
- Daily goal: e.g. 10 new words + review.
- Use **spaced repetition** (words come back after 1 day, 3 days, 7 days, 21 days).

> 📝 **Later:** word list to be chosen later — check the licence first, or use a free list from another source.

---

## 7. Shared features (all sections)

| Feature | Notes |
|---|---|
| UK + US audio | Either phone text-to-speech (free, works offline, quality varies) **or** pre-recorded audio files made with a good TTS service (better quality; check the licence allows use in an app) |
| IPA (UK + US) | Write it ourselves or take it from an open dictionary (e.g. Wiktionary, CC BY-SA) |
| My Words bank | One bank **per section** (see below) |
| Progress | Days done, words learned, test scores |
| Streak & reminder | Daily notification "Your Day 5 test is ready" |
| Offline | All content stored inside the app |
| Search | Find any word across all sections |

### My Words bank (one in each section)

Each section (Listening, Reading, Writing, Speaking, Fluent) has its own bank with 3 tabs:

| Tab | What goes in | How a word gets there |
|---|---|---|
| ✅ **Learned** | Words the user knows | Correct in a test, or "Yes, I know it" |
| ❌ **Missed** | Words the user got wrong / didn't know | Wrong in a test, or "No, I don't know it" |
| ⭐ **Saved** | Words the user wants to keep | User taps the star on any word card |

Rules:
- A missed word moves to **Learned** after the user gets it right **2 times in a row** in review.
- Each bank shows counts: *"Listening: 120 learned · 18 missed"*.
- **Review test** button inside each bank — tests only that section's *Missed* words.
- Home screen shows a small total of all 5 banks.

---

## 8. Technical plan

> Full system design & architecture: [Vocab_App_System_Design.md](Vocab_App_System_Design.md)

### Recommended stack: **React Native + Expo**
Why: one codebase for **iOS and Android**, and Expo's cloud build (**EAS Build**) can make the iOS app **from a Windows PC** — we don't need to buy a Mac to publish on the App Store.

| Part | Choice |
|---|---|
| App framework | React Native + Expo (TypeScript) |
| Content | JSON files bundled inside the app (no server needed at first) |
| Progress storage | On the phone (SQLite / AsyncStorage) |
| Audio | `expo-speech` (phone TTS, en-GB / en-US) for MVP → pre-recorded MP3 later |
| Later (optional) | Small backend (e.g. Firebase/Supabase) for accounts, sync across devices, content updates without a new app release |

### Content data format (draft)

```json
{
  "id": "lis-d01-february",
  "section": "listening",
  "group": "day-01-months",
  "word": "February",
  "partOfSpeech": "noun",
  "ipa": { "uk": "/ˈfebruəri/", "us": "/ˈfebrueri/" },
  "audio": { "uk": "audio/uk/february.mp3", "us": "audio/us/february.mp3" },
  "meaning": "the second month of the year",
  "commonMistakes": ["Februry", "Febuary"],
  "collocations": [],
  "examples": ["The course starts on the 3rd of February."]
}
```
Reading words also get `"source": { "book": 15, "test": 2, "passage": 1 }`.
Writing/Speaking words also get `"topic"` and use `collocations` + `examples`.

Every word saved in a My Words bank is stored as:

```json
{ "wordId": "lis-d01-february", "section": "listening", "status": "missed", "correctStreak": 0, "saved": false, "lastSeen": "2026-11-08" }
```
`status` = `"new"` | `"learned"` | `"missed"`

### App structure (screen map)

```
App
├── Home
│   ├── 5 section tiles (each shows % done)
│   ├── Continue where you left off
│   ├── Streak 🔥
│   └── My Words total (all sections)
│
├── 1. Listening
│   ├── 30-Day list (locked / open / done)
│   │   └── Day N
│   │       ├── Test on Day N-1   (from Day 2 onward)
│   │       │   └── Result + suggestion (next day / revise)
│   │       └── Word cards (word · UK/US audio · IPA · common mistakes)
│   └── My Words (Learned · Missed · Saved · Review test)
│
├── 2. Reading
│   ├── Passage 1 / Passage 2 / Passage 3
│   │   └── Cambridge 10 … 20
│   │       └── Test 1–4
│   │           ├── "Read this passage first" screen
│   │           ├── Word flow (Do you know it? Yes / No → meaning + examples)
│   │           └── Summary (knew X / 12)
│   └── My Words
│
├── 3. Writing
│   ├── Topic list (Education, Technology, Environment …)
│   │   └── Topic
│   │       └── Word cards (meaning · collocations · 2–3 sentences)
│   └── My Words
│
├── 4. Speaking
│   ├── Category list (Person, Place, Object, Event …)
│   │   └── Category
│   │       └── Word cards (audio · meaning · 2–3 sentences)
│   └── My Words
│
├── 5. Fluent English
│   ├── Bands (structure decided later)
│   └── My Words
│
└── Settings
    ├── Default accent (UK / US)
    ├── Daily reminder time
    ├── Reset progress
    └── About / Privacy policy
```

### Main user flows

**A. Listening day**
`Open Day N` → *(if N > 1)* `Test on Day N-1` → `Result` → `Next day` **or** `Revise Day N-1` → `Word cards` → `Day N done`

**B. Reading passage**
`Pick passage level` → `Pick book + test` → `"Read the passage"` → `Word 1…12 (Yes / No)` → `Summary` → `Next test`

**C. Writing / Speaking topic**
`Pick topic` → `Word cards` → `Mark ⭐ / quick check` → `Topic done`

**D. My Words review (any section)**
`Section → My Words` → `Missed tab` → `Review test` → right ×2 → moves to `Learned`

### Unlock rules

| Section | Rule |
|---|---|
| Listening | Day 1 open. Day N opens after Day N-1 test (suggested, user can skip) |
| Reading | All open — suggested order Passage 1 → 2 → 3, user can skip |
| Writing | All topics open |
| Speaking | All categories open |
| Fluent | Decide later |

---

## 9. Before App Store — checklist

| Item | Status |
|---|---|
| No Cambridge passage text — only suggest the passage | ✅ Decided |
| Simple app name, no "IELTS" | ✅ Decided |
| Word lists / dictionary data — licence checked or free source | ⏳ Later |
| TTS audio — licence allows use in an app | ⏳ Later |
| Privacy policy page (both stores require one) | ⏳ Before publishing |

### Store costs
- Apple Developer Program: **US$99 / year**
- Google Play Console: **US$25 one time**

---

## 10. Build phases

| Phase | Scope | Done when |
|---|---|---|
| **0. Content** | Write Day 1–5 Listening words in the JSON format | 5 days of words with IPA + mistakes ready |
| **1. MVP** | Home + **Listening 30-Day Challenge only** (cards, audio, test, result, progress) | Works on our own phone |
| **2. Test** | Give to 5–10 IELTS learners, fix problems | Feedback collected |
| **3. Reading** | Passage 1/2/3 flow for C10–C14 first | C10–C14 word lists done |
| **4. Writing + Speaking** | From our idea bank + speaking banks | 10 Writing topics + main Speaking categories |
| **5. Publish v1** | Store listing, screenshots, privacy policy | Live on App Store + Play Store |
| **6. Fluent English** | Choose licensed list, organize bands | — |
| **7. Extras** | Accounts/sync, "Say it" recording, premium plan | — |

> Start with Listening because it's the most original part (daily challenge + test gate) and needs the least content to launch.

---

## 11. Open questions (decide later)

- [ ] App name (simple, no "IELTS")
- [ ] Free or paid? (idea: Listening Day 1–7 free, rest premium; or one-time unlock)
- [ ] Phone TTS or pre-recorded audio for v1?
- [ ] Default accent for tests: UK only, or mixed UK/US (real exam is mostly UK, some others)?
- [ ] Should Reading "Yes, I know it" have a quick check question?
- [ ] Bangla meanings as an option? (useful for our learners)
- [ ] Fluent English: which word list (licence)?
- [ ] Writing & Speaking: final content style
- [ ] More Listening ideas (user will add)
