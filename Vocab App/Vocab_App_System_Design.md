# Vocab App — System Design & Architecture

> Version: 1.0 (2026-11-08)
> Related: [Vocab_App_Project_Plan.md](Vocab_App_Project_Plan.md) (features & content) · Diagram: [Vocab_App_Architecture.png](Vocab_App_Architecture.png)
> Scope: how the app is built — components, data, storage, flows, and how it grows.
> Rules (unlock %, review rules, etc.) are **not** decided here. The design keeps them in one config file so we can set them later.

---

## 1. Requirements

### 1.1 Functional (what the app does)

| ID | Requirement |
|---|---|
| F1 | 5 sections: Listening, Reading, Writing, Speaking, Fluent English |
| F2 | Word cards: word, meaning, IPA (UK/US), UK/US audio, mistakes, collocations, example sentences (fields differ per section) |
| F3 | Listening: 30 days, test on the previous day, result + suggestion |
| F4 | Reading: Passage 1/2/3 → Cambridge 10–20 → Test 1–4 → "read the passage" → Yes/No word flow → summary |
| F5 | Writing: topics → word cards. Speaking: categories → word cards |
| F6 | Fluent: structure decided later — design must allow it |
| F7 | My Words bank in each section (track learned / missed / saved) |
| F8 | Progress, streak, daily reminder, settings (default accent) |
| F9 | Search across all words |

### 1.2 Non-functional (how well it must work)

| ID | Requirement | Target |
|---|---|---|
| N1 | **Works offline** | 100% of learning features without internet |
| N2 | Fast | Screen open < 300 ms, audio starts < 500 ms |
| N3 | Small download | App install < 60 MB (v1) |
| N4 | Never lose progress | Progress saved immediately after every answer |
| N5 | Low cost | ~US$0/month running cost for v1 (only store fees) |
| N6 | Easy content updates | Add/fix words without rewriting code |
| N7 | Privacy | v1 collects no personal data |

### 1.3 Constraints

- **1 developer**, working on **Windows** (no Mac).
- Must ship to **iOS + Android**.
- Content is written by us (Listening/Writing/Speaking folders + Cambridge vocab lists).
- No budget for servers in v1.

### 1.4 Assumptions

- Content size (estimate):

| Section | Approx. words |
|---|---|
| Listening (30 days × ~20) | 600 |
| Reading (11 books × 4 tests × 3 passages × 12) | ~1,600 |
| Writing (~10 topics × ~50) | 500 |
| Speaking (~10 categories × ~50) | 500 |
| Fluent | 3,000–6,000 |
| **Total** | **~6,000–9,000 word entries** |

- Text data for all of this ≈ **3–6 MB** → easily fits inside the app.
- Pre-recorded audio for all (9,000 × 2 accents × ~15 KB) ≈ **270 MB** → too big to bundle. This drives the audio design (section 6).

---

## 2. Architecture overview

### Key decision: **Offline-first, no backend in v1**

All content ships **inside the app**. All user progress is stored **on the phone**. A backend is added only in v2 (accounts, sync, content updates).

### 2.1 v1 — high-level diagram

```
┌──────────────────────────── PHONE (iOS / Android) ────────────────────────────┐
│                                                                                │
│   ┌──────────────────────── UI LAYER (screens) ───────────────────────────┐   │
│   │ Home │ Listening │ Reading │ Writing │ Speaking │ Fluent │ My Words │ … │   │
│   └───────────────────────────────┬───────────────────────────────────────┘   │
│                                   │ uses                                       │
│   ┌──────────────────────── FEATURE / LOGIC LAYER ────────────────────────┐   │
│   │ Challenge engine │ Test engine │ Word-flow engine │ My Words service   │   │
│   │ Progress service │ Rules (config) │ Search │ Streak & reminders        │   │
│   └───────────┬───────────────────┬───────────────────┬───────────────────┘   │
│               │                   │                   │                        │
│   ┌───────────▼─────┐   ┌─────────▼─────────┐   ┌─────▼──────────────┐        │
│   │ Content repo    │   │ User data repo    │   │ Audio service      │        │
│   │ (read-only)     │   │ (read/write)      │   │                    │        │
│   └───────┬─────────┘   └─────────┬─────────┘   └──┬──────────────┬──┘        │
│           │                       │                │              │            │
│   ┌───────▼─────────┐   ┌─────────▼─────────┐  ┌───▼────────┐ ┌───▼────────┐  │
│   │ content.db      │   │ user.db           │  │ Phone TTS  │ │ MP3 files  │  │
│   │ (SQLite, ships  │   │ (SQLite, created  │  │ en-GB/en-US│ │ (later)    │  │
│   │  with the app)  │   │  on first launch) │  └────────────┘ └────────────┘  │
│   └─────────────────┘   └───────────────────┘                                  │
│                                                                                │
│   Local notifications (daily reminder) · Crash reporting (optional)            │
└────────────────────────────────────────────────────────────────────────────────┘
```

### 2.2 The two databases (most important idea)

| | `content.db` | `user.db` |
|---|---|---|
| What | All words, days, topics, passages | Progress, My Words, test results, settings |
| Who writes | **Us** (build script) | **The app** (user actions) |
| On phone | Read-only | Read/write |
| On app update | **Replaced** with new version | **Kept** — never deleted |
| Link | `word_id` | `word_id` |

**Why split:** we can fix a typo or add 500 words by shipping a new `content.db`, and the user's progress stays safe. The only rule: **never change or reuse a `word_id`**.

---

## 3. Tech stack

| Part | Choice | Why |
|---|---|---|
| Framework | **React Native + Expo** (TypeScript) | One code for iOS + Android; Expo cloud build makes iOS from Windows |
| Navigation | Expo Router (file-based) | Screen map = folder structure, easy to follow |
| Local DB | `expo-sqlite` | Fast queries, search, works offline |
| App state | Zustand | Small, simple (lighter than Redux) |
| Audio (v1) | `expo-speech` (phone TTS) | Free, offline, zero app size |
| Audio (later) | `expo-audio` + MP3 files | Better, consistent quality |
| Notifications | `expo-notifications` (local) | Daily reminder without a server |
| Build & publish | EAS Build + EAS Submit | Build iOS/Android in the cloud, upload to stores |
| Over-the-air fixes | EAS Update | Push small JS fixes without a new store review |
| Crash reports | Sentry (free tier) | Know when the app crashes |
| Content tooling | Node.js script (on our PC) | Turns our JSON files into `content.db` |
| v2 backend | **Supabase** (Postgres + Auth + Storage) | Free tier, SQL, accounts, file hosting in one place |

---

## 4. App code architecture

### 4.1 Layers (each layer only talks to the one below)

```
UI (screens + components)        ← what the user sees, no database code here
   ↓
Features (logic per section)     ← challenge, test, word-flow, my-words
   ↓
Services (shared logic)          ← progress, audio, search, rules, notifications
   ↓
Repositories (data access)       ← the only code that runs SQL
   ↓
content.db  /  user.db  /  device APIs
```

Why: if we change storage later (e.g. add cloud sync), only the **repository** layer changes — screens stay the same.

### 4.2 Folder structure

```
vocab-app/
├── app/                          # Screens (Expo Router — folder = route)
│   ├── index.tsx                 # Home
│   ├── listening/
│   │   ├── index.tsx             # 30-day list
│   │   ├── [day].tsx             # Day N word cards
│   │   ├── test/[day].tsx        # Test on Day N
│   │   └── result/[testId].tsx   # Result + suggestion
│   ├── reading/
│   │   ├── index.tsx             # Passage 1 / 2 / 3
│   │   ├── [level]/index.tsx     # Books 10–20
│   │   ├── [level]/[book].tsx    # Tests 1–4
│   │   └── flow/[passageId].tsx  # Read first → Yes/No → summary
│   ├── writing/  (index, [topic])
│   ├── speaking/ (index, [category])
│   ├── fluent/   (index, [band])
│   ├── my-words/[section].tsx    # One screen, used by all 5 sections
│   ├── search.tsx
│   └── settings.tsx
│
├── src/
│   ├── components/               # WordCard, AudioButton, ProgressBar, QuizInput …
│   ├── features/
│   │   ├── challenge/            # day list, day status (Listening)
│   │   ├── test/                 # build test, check answer, score
│   │   ├── wordflow/             # Yes/No flow (Reading)
│   │   └── mywords/              # bank logic
│   ├── services/
│   │   ├── audio.ts              # play(wordId, accent) → TTS or MP3
│   │   ├── progress.ts
│   │   ├── search.ts
│   │   ├── notifications.ts
│   │   └── rules.ts              # reads config/rules.json
│   ├── data/
│   │   ├── contentRepo.ts        # read words, days, topics, passages
│   │   ├── userRepo.ts           # read/write progress, my words, results
│   │   └── migrations/           # user.db schema versions
│   ├── store/                    # Zustand stores (settings, session)
│   └── types/                    # Word, Day, Passage, TestResult …
│
├── config/
│   └── rules.json                # ALL rules (unlock %, review counts…) — set later
│
├── assets/
│   ├── db/content.db             # built by the content tool
│   └── audio/                    # empty in v1
│
└── content/                      # SOURCE content (we edit these)
    ├── listening/day-01-months.json …
    ├── reading/c10-t1-p1.json …
    ├── writing/environment.json …
    ├── speaking/person.json …
    ├── fluent/ …
    └── tools/build-content.js    # validates + builds content.db
```

### 4.3 Rules live in config, not in code

Every rule we will decide later (test pass %, when a missed word becomes learned, what is locked) goes in `config/rules.json`, read by `services/rules.ts`. Example shape only (values TBD):

```json
{
  "listening": { "testSize": null, "suggestNextAt": null, "suggestReviseBelow": null, "allowSkip": true },
  "mywords":   { "missedToLearnedStreak": null },
  "reading":   { "wordsPerPassage": null, "quickCheckOnYes": null }
}
```

Changing a rule = edit one file, no code change.

---

## 5. Data model

### 5.1 `content.db` (read-only, built by us)

```
sections            id ('listening'|'reading'|'writing'|'speaking'|'fluent'), title, order

groups              id, section_id, type, title, order, meta_json
                    -- one table for every "container":
                    -- listening day   (type='day',     e.g. 'lis-day-01', title 'Months')
                    -- reading passage(type='passage', meta: {level:1, book:15, test:2, title:'…'})
                    -- writing topic   (type='topic')
                    -- speaking cat.   (type='category')
                    -- fluent band     (type='band')

words               id (stable, never reused), headword, part_of_speech,
                    meaning, ipa_uk, ipa_us, audio_uk, audio_us (nullable)

group_words         group_id, word_id, order
                    -- the same word can appear in many groups/sections

word_mistakes       word_id, wrong_spelling          -- Listening
word_collocations   word_id, collocation, order      -- Writing
word_examples       word_id, sentence, context ('writing'|'speaking'|'reading'|…), order

words_fts           full-text search index on headword + meaning

meta                content_version, built_at
```

**Why one `groups` table instead of separate days/topics/passages tables:** all sections share the same screens and logic ("open a group → show its words"). Fluent can be added later with no schema change — just a new `type`.

### 5.2 `user.db` (read/write, on the phone)

```
user_words          word_id, section_id, status ('new'|'learned'|'missed'),
                    saved (0/1), correct_streak, wrong_count,
                    first_seen, last_seen, updated_at
                    PRIMARY KEY (word_id, section_id)     -- one bank per section

group_progress      group_id, status ('locked'|'open'|'in_progress'|'done'),
                    words_seen, updated_at

test_attempts       id, group_id, started_at, finished_at, score, total
test_answers        attempt_id, word_id, user_answer, is_correct

daily_activity      date, words_studied, tests_taken     -- streak

settings            key, value      -- default_accent, reminder_time, …

schema_version      version
```

### 5.3 Example — one Listening test, end to end

```
User finishes Day 1 test
 → test engine checks each typed answer vs words.headword (case-insensitive, trimmed)
 → INSERT test_attempts + test_answers
 → for each word: UPSERT user_words (section='listening', status/streak updated)
 → rules.ts decides suggestion (next day / revise)
 → UPDATE group_progress for Day 2
 → UPDATE daily_activity (streak)
 → Result screen reads test_answers → shows analysis
```

---

## 6. Audio design

| Option | Size | Quality | Cost | Offline |
|---|---|---|---|---|
| **A. Phone TTS** (`expo-speech`, en-GB / en-US voice) | 0 MB | OK, differs by phone | Free | ✅ |
| B. MP3 bundled in app | ~270 MB | Good, same everywhere | TTS service / recording | ✅ |
| C. MP3 download packs per section | ~30–60 MB each | Good | Hosting (v2) | ✅ after download |

**Plan:** v1 = **A**. Later = **C** (e.g. "Download Listening audio pack").

The `audio.ts` service hides this:

```
play(wordId, accent):
   if MP3 file exists on phone → play MP3
   else                        → phone TTS with voice en-GB or en-US
```

Screens just call `play()` — switching from A to C needs no screen changes.

Known risk: some Android phones lack an en-GB voice → show a one-time tip to install it, and fall back to the default English voice.

---

## 7. Content pipeline (how words get into the app)

```
 Our materials                Source files              Build tool                 App
(Listening/, Writing/,  →   content/*.json      →   build-content.js     →   assets/db/content.db
 Speaking/, Cambridge         (we edit these)        1. validate               (ships with app)
 vocab lists)                                        2. check IDs unique
                                                     3. check required fields
                                                     4. write SQLite + search
                                                     5. set content_version
```

Validation catches mistakes **before** they reach users:
- every word has meaning, IPA UK + US
- every `word_id` unique and **never removed** from an old version (otherwise user progress breaks)
- Listening words have at least one common mistake
- Reading groups have book/test/passage metadata

Why JSON as the source (not editing the DB directly): easy to read and edit, easy to see changes, and we can generate it from our existing MD files.

---

## 8. v2 — adding a backend (later)

Only when we need **accounts, sync between devices, or content updates without a store release**.

### 8.1 v2 diagram

```
┌──────────── PHONE ────────────┐                 ┌────────────── SUPABASE ──────────────┐
│ UI → Features → Services      │                 │                                      │
│        ↓                      │                 │  Auth (email / Google / Apple login) │
│ Repositories                  │   HTTPS (JSON)  │                                      │
│   ├─ contentRepo ─────────────┼───────────────▶ │  Storage (CDN)                       │
│   │   (checks for new         │  GET manifest   │   ├─ content/manifest.json           │
│   │    content.db)            │  GET content.db │   ├─ content/content-v12.db          │
│   │                           │  GET audio pack │   └─ audio/listening-uk.zip …        │
│   └─ userRepo ── Sync queue ──┼───────────────▶ │                                      │
│        (offline changes saved │  push / pull    │  Postgres                            │
│         and sent when online) │  user_words …   │   ├─ profiles                        │
│                               │                 │   ├─ user_words                      │
└───────────────────────────────┘                 │   ├─ group_progress                  │
                                                  │   └─ test_attempts                   │
                                                  │  (Row Level Security: user sees      │
                                                  │   only their own rows)               │
                                                  └──────────────────────────────────────┘
```

### 8.2 API contracts (v2)

Content (public, read-only, cached on CDN):

```
GET /storage/content/manifest.json
→ { "contentVersion": 12, "minAppVersion": "1.3.0",
    "db": { "url": ".../content-v12.db", "sha256": "…", "sizeBytes": 4200000 },
    "audioPacks": [ { "id": "listening-uk", "url": "…", "sizeBytes": 31000000, "sha256": "…" } ] }
```

User sync (Supabase REST, logged-in user only):

```
GET  /rest/v1/user_words?updated_at=gt.{lastSyncAt}     → changes from other devices
POST /rest/v1/user_words   (upsert, on conflict word_id+section_id)
     [ { "word_id": "lis-d01-february", "section_id": "listening",
         "status": "learned", "saved": false, "correct_streak": 2,
         "updated_at": "2026-12-01T10:00:00Z" } ]
```
Same pattern for `group_progress` and `test_attempts` (attempts are insert-only).

### 8.3 Sync rules

- Phone is the **main copy**; the app always works offline.
- Every local change → also written to a `sync_queue` table.
- When online: push queue → pull changes since `lastSyncAt`.
- Conflict (same word changed on 2 phones): **latest `updated_at` wins**. Test attempts never conflict (insert only).
- Failed request → retry later with growing wait (1 min, 5 min, 30 min…). Nothing is lost because the queue stays on the phone.

### 8.4 Content update flow

```
App start (online) → GET manifest
  if contentVersion > local and app version ≥ minAppVersion:
      download content-vN.db in background → check sha256
      → swap on next app start (user.db untouched)
  if anything fails → keep using the old content.db
```

---

## 9. Error handling

| Situation | What the app does |
|---|---|
| No internet | Nothing changes in v1 (everything is local). v2: sync waits in queue |
| TTS voice missing | Fall back to default English voice + one-time tip |
| App closed in the middle of a test | Attempt saved per answer → "Continue test?" on return |
| user.db schema change in new version | Run migrations in order (`schema_version`), never drop user data |
| Word removed from content by mistake | Build tool blocks it; app also hides orphan rows instead of crashing |
| Corrupt content download (v2) | sha256 check fails → keep old content |
| Crash | Sentry report (no personal data) |

---

## 10. Scale, performance & monitoring

**Load (v1):** no server → no server load. Each phone handles only one user's data (a few thousand rows) — SQLite handles this easily.

**Load (v2), rough estimate:** 10,000 users × ~20 sync requests/day ≈ 200,000 requests/day ≈ 2–3 per second on average. Supabase free/low tier is enough. Content downloads go through the CDN.

**Performance tips:**
- Indexes on `group_words(group_id)`, `user_words(section_id, status)`.
- Load one group's words at a time, not the whole database.
- Full-text search table for instant search.

**Monitoring:**
| What | Tool |
|---|---|
| Crashes, errors | Sentry |
| Store ratings, installs | App Store Connect / Play Console |
| (Optional, needs privacy notice) Usage: which days people stop at | Privacy-friendly analytics, e.g. PostHog — only if we decide to collect it |

---

## 11. Security & privacy

- v1: **no account, no personal data, nothing leaves the phone** → simplest privacy policy.
- v2: Supabase Row Level Security so each user can read/write **only their own** rows.
- Apple rule: if we offer Google login on iOS, we must also offer **Sign in with Apple**.
- Account deletion button required by both stores once accounts exist.
- No API secret keys inside the app (only the public Supabase key, protected by RLS).

---

## 12. Trade-offs (decisions and why)

| Decision | Chosen | Alternative | Why chosen | Cost of choice |
|---|---|---|---|---|
| Framework | React Native + Expo | Flutter, native Swift/Kotlin | One code base; iOS build from Windows; huge community | Slightly bigger app than native |
| Backend in v1 | **None** | Firebase/Supabase from day 1 | Ship faster, $0, works offline, no privacy work | No sync between phones in v1 |
| Content storage | Bundled SQLite | JSON loaded in memory | Fast search & queries at 6–9k words | Needs a build step |
| Content vs user data | **2 separate DBs** | One DB | Content updates never touch progress | Join across 2 DBs in code |
| Audio v1 | Phone TTS | Bundled MP3 | 0 MB, free, offline | Quality varies by phone |
| One `groups` table | Generic | Separate tables per section | Fluent/new sections need no schema change | Section-specific fields go in `meta_json` |
| Rules | Config file | Hard-coded | Rules not decided yet; easy to tune | Slight extra code |
| Sync conflicts (v2) | Last write wins | Merge logic | Simple; conflicts are rare (one person, one word) | Rare edge case may lose one change |

---

## 13. What to revisit as the app grows

| When | Revisit |
|---|---|
| Users ask for better audio | Move from TTS to MP3 download packs |
| Users have 2+ devices / ask for login | Add v2 backend + sync |
| We fix content often | Add remote content updates (manifest) |
| Fluent section is designed | Add `band` groups + maybe spaced-repetition scheduling table |
| Free vs paid decided | Add in-app purchases (RevenueCat or store APIs) + entitlement check |
| Many users | Analytics to see where users drop off; tune rules in `rules.json` |
| Writing/Speaking redesigned | Only content + card component change; data model already supports it |

---

## 14. Hosting & cost

**Version 1 needs no hosting** — words and progress live inside the app.

| Item | Cost | Needed when |
|---|---|---|
| Building & testing (Expo, Expo Go app on own phone) | Free | Now |
| Cloud builds (EAS Build free plan, limited builds/month) | Free | Now |
| Privacy policy page (GitHub Pages / Google Sites) | Free | Before publishing |
| Crash reports (Sentry free plan) | Free | Optional |
| **Google Play** developer account | **US$25 once** | Publish on Android |
| **Apple Developer** account | **US$99 / year** | iPhone testing via TestFlight + publish on App Store |
| Supabase free plan (login, sync) | Free to start | v2 only |
| Audio pack hosting (Supabase Storage / Cloudflare R2 free tier) | Free to start | v2 only |
| Domain name (optional) | ~US$10 / year | Optional |

Minimum to publish on both stores: **US$25 once + US$99 / year**. Cheapest path: build and test free → publish Android first ($25) → add iOS when ready ($99/yr).

---

## 15. Build order (architecture side)

1. Set up Expo project, folders, navigation (empty screens).
2. Content tool: JSON → `content.db` with validation (start with Listening Day 1–5).
3. `contentRepo` + WordCard + audio service (TTS).
4. `user.db` + migrations + `userRepo`.
5. Test engine + result screen (rules from `rules.json`).
6. My Words screen (shared by all sections).
7. Reading word flow → Writing/Speaking lists → Settings, reminders, search.
8. Sentry, EAS Build, TestFlight / Play internal testing.
9. (v2) Supabase: auth → sync queue → content manifest → audio packs.
