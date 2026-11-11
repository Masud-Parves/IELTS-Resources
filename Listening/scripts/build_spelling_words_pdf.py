"""Build Listening/IELTS_Listening_Spelling_Words.pdf.

Every word comes from three official IDP IELTS articles:
  A = IELTS common spelling mistakes (IDP, 18 May 2023)
  B = IELTS Listening difficult words (IDP, 19 Jan 2022)
  C = IELTS Listening test: tips to build your vocabulary (IDP, 2020, updated 10 Jun 2026)

Word markup: letters inside [ ] are the trap letters and print highlighted.
Usage: python build_spelling_words_pdf.py   (HTML -> PDF via headless Edge)
"""
import re, subprocess, pathlib, random, html as h

ROOT = pathlib.Path(__file__).resolve().parent.parent
HTML = ROOT / "scripts" / "_spelling_build.html"
PDF = ROOT / "IELTS_Listening_Spelling_Words.pdf"
EDGE = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

SOURCES = {
    "A": ("IELTS common spelling mistakes", "IDP, 18 May 2023",
          "ielts.idp.com/prepare/article-ielts-common-spelling-mistakes"),
    "B": ("IELTS Listening difficult words", "IDP, 19 Jan 2022",
          "ielts.idp.com/prepare/article-ielts-listening-difficult-words"),
    "C": ("IELTS Listening test: tips to build your vocabulary", "IDP, 2020 · updated 10 Jun 2026",
          "ielts.idp.com/prepare/article-common-vocabulary-ielts-listening"),
}

# ---------------------------------------------------------------- helpers
registry = {}  # plain lower word -> {"m": marked form, "src": set()}


def plain(s):
    return re.sub(r"[\[\]]", "", s)


def mark(s):
    s = h.escape(s, quote=False)
    return re.sub(r"\[([^\]]+)\]", r"<b class='t'>\1</b>", s)


def reg(word, src):
    key = plain(word).lower()
    e = registry.setdefault(key, {"m": word, "src": set()})
    e["src"].add(src)
    if "[" in word and "[" not in e["m"]:
        e["m"] = word
    return word


def grid(words, src, cols=4):
    seen, chips = set(), []
    for w in words:
        if plain(w).lower() in seen:
            continue
        seen.add(plain(w).lower())
        reg(w, src)
        chips.append(f"<div class='w'><span class='box'></span><span>{mark(w)}</span></div>")
    return f"<div class='grid c{cols}'>" + "".join(chips) + "</div>"


def tip(text, label="IDP tip"):
    return f"<div class='tip'><b>{label}:</b> {text}</div>"


def section(num, title, intro, body):
    return (f"<section class='chapter'><h2><span class='num'>{num}</span>{title}</h2>"
            + (f"<p class='intro'>{intro}</p>" if intro else "") + body + "</section>")


def table(head, rows, cls=""):
    th = "".join(f"<th>{x}</th>" for x in head)
    trs = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table class='{cls}'><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table>"


def words_cell(ws, src):
    return " · ".join(mark(reg(w, src)) for w in ws)


def wrong(s):
    return f"<s class='bad'>{h.escape(s)}</s>"


# ---------------------------------------------------------------- 2. the 7 traps (article A, plus B's tables)
traps = ""

traps += "<h3 class='trap'><span class='tag'>Trap 1</span>Single and double consonants</h3>"
traps += "<p>Mistakes happen when single and double consonants are close together in one word.</p>"
traps += table(["Pattern", "Words"], [
    ["Single, then double", words_cell(["a[c]ro[ss]", "pro[c]e[ss]", "re[c]o[mm]end", "ne[c]e[ss]ary"], "A")],
    ["Double, then single", words_cell(["a[pp]a[r]ent", "e[x]a[gg]e[r]ate", "o[cc]a[s]ion", "pa[r]a[ll]el", "i[mm]e[d]iate"], "A")],
    ["Two doubles", words_cell(["a[dd]re[ss]", "a[ss]e[ss]", "a[cc]o[mm]odation", "po[ss]e[ss]", "su[cc]e[ss]", "o[cc]u[rr]ence"], "A")],
], "rules")

traps += "<h3 class='trap'><span class='tag'>Trap 2</span>Adding -ed, -ing, -er, -est</h3>"
traps += "<p>Sometimes the last consonant doubles when you add an ending.</p>"
traps += table(["Base word", "With the ending", "Don't write"], [
    ["drop", words_cell(["dro[pp]ed", "dro[pp]ing"], "A"), "—"],
    ["big", words_cell(["bi[gg]er", "bi[gg]est"], "A"), "—"],
    ["run", words_cell(["ru[nn]ing", "ru[nn]er"], "A"), "—"],
    ["begin", words_cell(["begi[nn]ing", "begi[nn]er"], "A") , wrong("begining")],
    ["regret", words_cell(["regre[tt]ed", "regre[tt]ing"], "A"), "—"],
    ["refer", words_cell(["refe[rr]ed"], "B"), wrong("refered")],
], "rules")
reg("begi[nn]ing", "B")
traps += tip("All these words end in <i>one short vowel + one consonant</i> (dr<b>o</b>p, b<b>i</b>g, beg<b>i</b>n). "
             "That last consonant doubles before -ed / -ing / -er / -est.", "Pattern to notice")

traps += "<h3 class='trap'><span class='tag'>Trap 3</span>The word changes form</h3>"
traps += "<p>The spelling can change when a word becomes a noun, adjective or verb.</p>"
traps += table(["Change", "From", "To", "Don't write"], [
    ["adjective → noun", "absent", mark(reg("absen[c]e", "A")), "—"],
    ["adjective → noun", "different", mark(reg("differen[c]e", "A")), "—"],
    ["noun → adjective", "benefit", mark(reg("benefi[c]ial", "A")), wrong("benefitial")],
    ["noun → adjective", "influence", mark(reg("influen[t]ial", "A")), wrong("influencial")],
    ["noun → adjective", "circumstance", mark(reg("circumstan[t]ial", "B")), wrong("circumstancial")],
    ["verb → noun", "maintain", mark(reg("maint[e]nance", "A")), wrong("maintainance")],
    ["verb → noun", "pronounce", mark(reg("pron[u]nciation", "A")), "—"],
    ["noun → verb", "excess", mark(reg("ex[ceed]", "A")), "—"],
    ["noun → verb", "success", mark(reg("su[cceed]", "A")), "—"],
], "rules")
for w in ["benefi[c]ial", "influen[t]ial", "maint[e]nance"]:
    reg(w, "B")

traps += "<h3 class='trap'><span class='tag'>Trap 4</span>Silent letters in consonant groups</h3>"
traps += "<p>You don't hear these letters clearly, so they are easy to leave out.</p>"
traps += table(["Letters", "Words", "Don't write"], [
    ["nm", words_cell(["enviro[n]ment", "gover[n]ment"], "A"), wrong("enviroment")],
    ["mn", words_cell(["autum[n]", "colum[n]"], "A"), "—"],
    ["sc", words_cell(["con[sc]ious", "di[sc]ipline", "[sc]ience"], "A"), wrong("concious")],
    ["xc", words_cell(["e[xc]ited", "e[xc]eption", "e[xc]ite"], "A"), wrong("exite")],
    ["kn", words_cell(["[k]now", "[k]nee", "[k]nob"], "A"), "—"],
    ["th (ordinals)", words_cell(["eigh[th]", "twel[f]th"], "A"), "—"],
    ["g (not j)", words_cell(["privile[g]e"], "B"), wrong("privilje")],
], "rules")
for w in ["enviro[n]ment", "con[sc]ious", "e[xc]ite"]:
    reg(w, "B")

traps += "<h3 class='trap'><span class='tag'>Trap 5</span>Words that sound alike</h3>"
traps += "<p>They sound the same (or nearly the same) but mean different things.</p>"
confused = [
    ("lose / loose", "<b>lose</b> = not win, can't find · <b>loose</b> = not tight"),
    ("affect / effect", "<b>affect</b> = verb (to change something) · <b>effect</b> = noun (the result)"),
    ("complement / compliment", "<b>complement</b> = goes well with · <b>compliment</b> = nice words about someone"),
    ("its / it's", "<b>its</b> = belongs to it · <b>it's</b> = it is"),
    ("passed / past", "<b>passed</b> = verb (she passed the exam) · <b>past</b> = time before / go by (walk past)"),
    ("principal / principle", "<b>principal</b> = head of a school, main · <b>principle</b> = a rule or belief"),
    ("than / then", "<b>than</b> = comparing (bigger than) · <b>then</b> = time (and then)"),
    ("their / there / they're", "<b>their</b> = belongs to them · <b>there</b> = place · <b>they're</b> = they are"),
    ("costume / custom", "<b>costume</b> = special clothes · <b>custom</b> = a tradition"),
]
traps += table(["Words", "How to tell them apart"], [[f"<b>{a}</b>", b] for a, b in confused], "rules")

traps += "<h3 class='trap'><span class='tag'>Trap 6</span>Words that are just hard to spell</h3>"
traps += grid(["hier[a]rchy", "entrepren[eu]r", "defin[i]tely", "for[ei]gn",
               "gr[a]teful", "persever[a]nce", "rh[y]thm", "maint[e]nance"], "A")

traps += "<h3 class='trap'><span class='tag'>Trap 7</span>British vs American spelling</h3>"
traps += ("<p>Both British and American spellings are accepted. <b>Pick one and use it every time.</b> "
          "IDP's own lists use British forms such as <i>colour, theatre, organisation, licence, neighbour</i>.</p>")

# keep each trap (heading + table) on one page
traps = traps.replace("<h3 class='trap'>", "</div><div class='tb'><h3 class='trap'>").replace("</div>", "", 1) + "</div>"

# ---------------------------------------------------------------- 3. IDP's tricky words test list (article B)
b60 = ["li[br]ary", "enviro[n]ment", "rest[au]rant", "customer", "bel[ie]ve", "modern", "di[ff]i[c]ult",
       "contr[o]versy", "sep[a]rate", "compar[i]son", "sk[ii]ng", "b[u]s[i]ness", "pro[f]e[ss]or", "aven[ue]",
       "[nu]clear", "modern", "basic[all]y", "co[mm]i[t]ment", "con[sc]ious", "di[s]a[pp]ear", "e[xc]iting",
       "boring", "rh[y]thm", "i[mm]ediat[e]ly", "ne[c]e[ss]ary", "orig[i]nal", "r[ea]listic", "rec[ei]ve",
       "Feb[r]uary", "tend[e]ncy", "ob[e]sity", "ma[rr]iage", "sol[a]r", "f[ue]l", "fr[ie]ndly", "unti[l]",
       "b[eau]tiful", "hi[gh]way", "perc[e]ntage", "mi[ll]ion", "th[ou]sand", "hund[re]d", "fluct[u]ate",
       "p[ea]k", "recover", "musi[ci]an", "computer", "software", "video", "murder", "topic", "temp[o]rary",
       "unfortunat[e]ly", "di[s]advantage", "arg[u]ment", "We[d]nesday", "n[eigh]bour", "for[ei]gn",
       "o[pp]ortunity", "bec[au]se"]
b_choose = ["absen[c]e", "ach[ie]ve", "co[ll]ea[gu]e", "delib[e]rate", "a[tt]ack", "lang[ua]ge"]
s3 = grid(b60, "B")
s3 += tip("Say the word, write it, check it, then repeat. Doing this again and again helps you remember the correct spelling.")
s3 += "<h3>Plus IDP's \"choose the correct one\" words</h3>"
s3 += grid(b_choose, "B")
s3 += tip("<b>until</b> has one <b>l</b> (not <i>untill</i>). <b>argument</b> drops the <b>e</b> of argue. "
          "<b>skiing</b> has two <b>i</b>'s.", "Watch out")

# ---------------------------------------------------------------- 4-7. vocabulary by part (article C)
p1 = "<h3>Days of the week</h3>" + grid(
    ["Sunday", "Monday", "Tuesday", "We[d]nesday", "Thursday", "Friday", "Saturday"], "C")
p1 += tip("<b>Wednesday</b> is commonly misspelled.")
p1 += "<h3>Months and seasons</h3>" + grid(
    ["January", "Feb[r]uary", "March", "April", "May", "June", "July", "August", "September", "October",
     "November", "December", "winter", "spring", "autum[n]", "summer"], "C")
p1 += tip("The first <b>r</b> in <b>February</b> is often forgotten. The final <b>n</b> in <b>autumn</b> is often "
          "forgotten because you don't hear it. You can write dates in numbers, e.g. 10th February 2020 = 10/02/2020.")
p1 += "<h3>Shapes</h3>" + grid(["circle", "square", "rectangle", "triangle", "c[y]linder", "oval"], "C")
p1 += tip("Shapes appear in place names (e.g. <i>King George Square</i>), so spell the common ones correctly.")
p1 += "<h3>Transport</h3>" + grid(
    ["automobile", "truck", "tractor", "tram", "subway", "airplane", "train", "bic[y]cle", "car",
     "pedes[t]rian", "pa[ss]enger", "co[mm]uter"], "C")
p1 += tip("<b>commuter</b> is often misspelled because people confuse it with <i>computer</i>.")
p1 += "<h3>Colours</h3>" + grid(
    ["red", "orange", "yellow", "green", "blue", "purple", "white", "black", "brown"], "C")
p1 += tip("<b>colour</b> is British spelling and <b>color</b> is American. Both are correct.")
p1 += "<h3>Verbs</h3>" + grid(
    ["su[gg]est", "develo[p]", "bo[rr]ow", "per[su]ade", "dis[c]u[ss]", "review", "concentrate", "bel[ie]ve",
     "crash"], "C")
p1 += tip("Verbs can change form (tense etc.). Writing the wrong form can make your answer wrong.")
p1 += "<h3>Adjectives</h3>" + grid(
    ["b[eau]tiful", "ne[c]e[ss]ary", "fantastic", "comfortable", "conven[ie]nt", "wonderfu[l]", "te[rr]ible",
     "temp[o]rary", "perman[e]nt", "[k]nowledg[e]able", "e[xc]iting", "boring", "di[ff]i[c]ult", "easy"], "C")
p1 += tip("Look carefully at adjectives with double consonants (ss / mm). It is easy to miss a letter.")
p1 += "<h3>Numbers, times and money</h3>" + table(["You hear", "Write"], [
    ["thirty dollars", "$30"], ["six o'clock", "6:00"], ["ten thousand", "10,000"],
    ["10th February 2020", "10/02/2020"]], "rules small")
p1 += tip("To hear the difference between 13 and 30, listen for the stress: thir-<b>TEEN</b> vs <b>THIR</b>-ty. "
          "Use the same currency symbol as the question. Writing <b>$</b> when it should be <b>£</b> is wrong.")

p2 = "<h3>Rooms in buildings</h3>" + grid(
    ["ki[t]chen", "bathroom", "bedroom", "living room", "dining room", "lo[u]nge", "li[br]ary",
     "g[y]mnasium (gym)", "cafet[e]ria (cafe)", "classroom", "waiting room", "re[c]eption", "ticket desk",
     "storage room", "thea[tre]"], "C")
p2 += "<h3>Place markers (street names)</h3>" + grid(
    ["street", "road", "aven[ue]", "lane", "drive", "court", "place", "te[rr]ace", "way"], "C")
p2 += tip("On a map question, you will hear some of these words but may not need to write them.")
p2 += "<h3>Directions and places</h3>" + grid(
    ["north", "south", "east", "west", "up", "down", "right", "left", "strai[gh]t", "a[c]ro[ss] from",
     "between", "beside", "diagonal", "corner", "o[pp]osite", "a[d]jacent to", "near", "past", "before",
     "after"], "C")
p2 += "<h3>Direction verbs</h3>" + grid(
    ["turn", "move", "continue on", "walk", "cross", "pass", "start", "finish", "end", "stop",
     "go strai[gh]t ahead"], "C")
p2 += "<h3>Places on a map</h3>" + grid(
    ["te[nn]is court", "river", "courtyard", "labor[a]tory", "b[ui]lding", "bri[d]ge", "road", "path",
     "tra[ff]ic lights", "bench", "seat", "table", "basketball court", "ru[nn]ing track", "swi[mm]ing pool",
     "beach", "forest", "garden", "ca[s]tle"], "C")
p2 += tip("Write <b>L</b> and <b>R</b> on the edges of your question paper. If the map has no compass, draw one.")

p3 = "<h3>Study words</h3>" + grid(
    ["presentation", "project", "teamwork", "pairs", "organi[s]ation", "outline", "proofreading", "experiment",
     "refe[r]ence", "lecture", "tutor", "teacher", "atten[da]nce", "specialist", "[k]nowledge", "faculty",
     "bachelor's", "master's", "s[ch]edule", "management", "leadership", "questio[nn]aire", "statistic",
     "perc[e]ntage", "labor[a]tory", "school", "university", "co[ll]ege"], "C")
p3 += tip("North Americans say <b>laboratory</b> in three syllables (LAB-ruh-tory). British speakers say it in "
          "four (la-BOR-a-tory). The spelling is the same.")
p3 += "<h3>School subjects</h3>" + grid(
    ["Mathematics (Maths)", "[Sc]ience", "English", "Physical Education (PE)", "Art", "Music", "Geo[g]raphy",
     "Biology", "[Ch]emistry", "History"], "C")
p3 += tip("A school year is divided into <b>terms</b> or <b>semesters</b>, with holidays between them.")
p3 += "<h3>University subjects</h3>" + grid(
    ["Co[mm]erce", "[Sc]ience", "[Ps]ychology", "Engin[ee]ring", "Marketing", "So[ci]ology", "Medi[c]ine",
     "History", "Geo[g]raphy", "Ar[ch]itecture", "Law", "[Ph]ilosophy", "Economics", "Education"], "C")
p3 += tip("A university year is divided into <b>semesters</b>, with exams at the end of each one. "
          "Study can be <b>part-time</b> or <b>full-time</b>.")
p3 += "<h3>Exams</h3>" + grid(
    ["a[ss]e[ss]ment", "test", "revision", "pass", "fail", "repeat", "supervise", "supervis[o]r", "a[ss]e[ss]",
     "exam", "results", "degree", "certificate"], "C")

p4 = "<h3>Health</h3>" + grid(
    ["vegetarian", "vegan", "healthy", "unhealthy", "l[ei]sure", "di[s]ease", "vitamin", "prot[ei]n",
     "carb[o]hydrates", "e[x]er[c]ise", "treatment", "obese", "overweight", "fit", "doct[o]r", "check up",
     "medi[c]ine", "pandemic", "virus", "cure", "va[cc]ination"], "C")
p4 += "<h3>Animals and habitats</h3>" + grid(
    ["ma[mm]als", "reptile", "primates", "predators", "prey", "mountain", "jungle", "forest", "i[s]land", "pond",
     "river", "stream", "zoo", "pet", "endangered", "spe[c]ies", "o[c]ean", "sea"], "C")
p4 += tip("On 5 Nov you wrote <s class='bad'>mamals</s>. It needs two m's: <b>ma<b class='t'>mm</b>als</b>.",
          "Your own mistake")
p4 += "<h3>Continents and countries</h3>" + grid(
    ["North America", "South America", "Asia", "Africa", "Europe", "Antar[c]tica", "Australia", "Oceania",
     "England", "Canada", "China", "United Kingdom", "Germany", "Mexico", "Swi[tz]erland"], "C")
p4 += "<h3>Environment</h3>" + grid(
    ["global warming", "disaster", "earthquake", "tornado", "bli[zz]ard", "hu[rr]icane", "po[ll]ution",
     "temp[er]ature", "drou[gh]t", "flood", "c[y]clone", "volcanic e[r]uption", "deforestation",
     "desertification", "bush fires"], "C")
p4 += "<h3>Government</h3>" + grid(
    ["politics", "leader", "politi[ci]an", "senator", "mayor", "laws", "regulations", "senate", "president",
     "soc[ie]ty", "individual", "coun[c]il", "rules"], "C")
p4 += tip("<b>society</b> is one of the most commonly misspelled words in the IELTS test.")
p4 += "<h3>Energy</h3>" + grid(
    ["[nu]clear", "oil", "coal", "hydro electrical power", "natural gas", "solar power", "so[ur]ce", "generate",
     "electri[c]ity", "dam", "windmill", "wind turbine", "renewable", "non-renewable"], "C")
p4 += tip("Check <b>nuclear</b> carefully. People often write <s class='bad'>unclear</s> by mistake, and that answer is wrong.")
p4 += "<h3>General</h3>" + grid(
    ["a[pp]ointment", "cooperation", "employment", "gover[n]ment", "e[xh]ibition", "o[cc]upation",
     "alumin[i]um / aluminum", "century", "decade", "mi[ll]e[nn]ium", "individual", "creativity", "g[u]arantee",
     "sa[t]e[ll]ite", "o[pp]ortunity", "licen[c]e", "frequently", "calend[a]r", "di[ff]erent"], "C")
p4 += tip("<b>government</b> and <b>different</b> are among the most commonly misspelled words in the test. "
          "IDP uses the American spelling <i>aluminum</i>; the British spelling is <i>aluminium</i>. Both are accepted.")

# ---------------------------------------------------------------- 8. practice (article B's quiz + B's wrong forms)
quiz = [("absence", "absense"), ("achieve", "acheeve"), ("colleague", "colleage"), ("deliberate", "deliberete"),
        ("attack", "atack"), ("language", "langauge"), ("beneficial", "benefitial"), ("influential", "influencial"),
        ("circumstantial", "circumstancial"), ("maintenance", "maintainance"), ("referred", "refered"),
        ("beginning", "begining"), ("environment", "enviroment"), ("excite", "exite"), ("privilege", "privilje"),
        ("conscious", "concious")]
rnd = random.Random(7)
rnd.shuffle(quiz)
qrows, key = [], []
for i, (right, bad) in enumerate(quiz, 1):
    opts = [right, bad]
    rnd.shuffle(opts)
    qrows.append(f"<li><span class='opt'>Ⓐ {opts[0]}</span><span class='opt'>Ⓑ {opts[1]}</span></li>")
    key.append(f"{i} {'A' if opts[0] == right else 'B'}")
s8 = "<h3>Test 1 · Choose the correct spelling</h3>"
s8 += "<p>Circle A or B. Every wrong spelling here is one that IDP shows.</p>"
s8 += "<ol class='quiz'>" + "".join(qrows) + "</ol>"
s8 += "<h3>Test 2 · Dictation sheet</h3>"
s8 += ("<p>Choose one section of this book. Someone reads the words aloud (or ask Claude to read them with "
       "text-to-speech) while you write. Then check against the list. Add every word you get wrong to "
       "<b>section 8 of your Spelling Fix List</b> and test it again next week.</p>")
rows = "".join(f"<tr><td class='n'>{i}</td><td></td><td class='ck'></td>"
               f"<td class='n'>{i + 15}</td><td></td><td class='ck'></td></tr>" for i in range(1, 16))
s8 += ("<table class='dict'><thead><tr><th>#</th><th>I wrote</th><th>✓/✗</th>"
       "<th>#</th><th>I wrote</th><th>✓/✗</th></tr></thead><tbody>" + rows + "</tbody></table>")
s8 += "<div class='key'><b>Answers to Test 1:</b> " + " · ".join(key) + "</div>"

# ---------------------------------------------------------------- 1. top priority (built last: needs the registry)
flagged = [
    ("We[d]nesday", "commonly misspelled", "C"),
    ("Feb[r]uary", "the first r is often forgotten", "C"),
    ("autum[n]", "the final n is often forgotten", "C"),
    ("co[mm]uter", "often confused with computer", "C"),
    ("soc[ie]ty", "one of the most commonly misspelled words in IELTS", "C"),
    ("gover[n]ment", "one of the most commonly misspelled words in the test", "C"),
    ("di[ff]erent", "one of the most commonly misspelled words in the test", "C"),
    ("[nu]clear", "often written as unclear", "C"),
]
s1 = "<h3>Words IDP names as common mistakes</h3>"
s1 += table(["Word", "What IDP says"], [[f"<span class='big'>{mark(w)}</span>", why] for w, why, _ in flagged],
            "rules")
flagged_keys = {plain(w).lower() for w, _, _ in flagged}
multi = sorted((k, e) for k, e in registry.items() if len(e["src"]) >= 2 and k not in flagged_keys)
s1 += "<h3>Words that appear in two or three of the IDP articles</h3>"
s1 += "<p>IDP repeats these words across its articles, so learn them first.</p>"
s1 += "<div class='grid c4'>" + "".join(
    f"<div class='w'><span class='box'></span><span>{mark(e['m'])}</span><i class='src'>{''.join(sorted(e['src']))}</i></div>"
    for _, e in multi) + "</div>"

# ---------------------------------------------------------------- assemble
chapters = [
    ("1", "Learn These First", "Start here. IDP either names these words as common mistakes or repeats them across its articles.", s1),
    ("2", "The 7 Spelling Traps", "From IDP's article <i>IELTS common spelling mistakes</i>, with the wrong spellings from <i>IELTS Listening difficult words</i>.", traps),
    ("3", "IDP's Tricky Words List", "IDP's own list of commonly misspelled Listening words. Tick a box only after you spell the word correctly from memory.", s3),
    ("4", "Part 1 Words", "Everyday conversation: forms, bookings, personal details.", p1),
    ("5", "Part 2 Words", "A talk about a place: buildings, maps and directions.", p2),
    ("6", "Part 3 Words", "Students and tutors talking about study.", p3),
    ("7", "Part 4 Words", "A university lecture on an academic topic.", p4),
    ("8", "Test Yourself", "", s8),
]
body = "".join(section(*c) for c in chapters)
total = len(registry)
toc = "".join(f"<li><span class='tnum'>{n}</span>{t}</li>" for n, t, _, _ in chapters)
srcs = "".join(f"<tr><th>{k}</th><td><b>{t}</b><br><small>{d} · {u}</small></td></tr>"
               for k, (t, d, u) in SOURCES.items())

cover = f"""
<section class='cover'>
  <div class='kicker'>IELTS Listening</div>
  <h1>Spelling Words</h1>
  <div class='sub'>{total} words from three official IDP IELTS articles, sorted so you can learn them</div>
  <div class='rule'>In Listening, a misspelled answer is <b>marked wrong</b>, even if you heard it correctly.</div>
  <table class='profile'>{srcs}</table>
  <div class='two'>
    <div><h3>How to learn (IDP's method)</h3>
      <ol class='steps'><li><b>Say</b> the word</li><li><b>Write</b> it from memory</li>
      <li><b>Check</b> it against the book</li><li><b>Repeat</b> until it is right every time</li></ol>
      <p class='small'>Go back over your hard words <b>every week</b>.</p></div>
    <div><h3>Contents</h3><ol class='toc'>{toc}</ol></div>
  </div>
  <div class='legend'><span><b class='t'>red letters</b> = the trap: look hard at these</span>
    <span><s class='bad'>crossed out</s> = a wrong spelling IDP shows</span>
    <span><i class='src'>AB</i> = the IDP articles that list the word</span></div>
</section>
"""

css = """
@page { size: A4; margin: 15mm 14mm 17mm 14mm;
  @bottom-center { content: counter(page); font: 9pt 'Segoe UI', sans-serif; color: #8A94A3; }
  @bottom-right { content: 'IELTS Listening · Spelling Words (IDP)'; font: 8pt 'Segoe UI', sans-serif; color: #B0B8C4; } }
@page :first { @bottom-center { content: none; } @bottom-right { content: none; } }
:root { --ink:#16202C; --muted:#5B6675; --accent:#1A3A5C; --accent2:#2F6B9A; --band:#EDF2F7;
        --line:#D5DCE4; --warn:#FFF6E0; --warnline:#E0A526; --good:#E8F5EC; --trap:#C0392B; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { margin: 0; font: 10.5pt/1.45 'Segoe UI', Calibri, sans-serif; color: var(--ink); background: #fff; }
section.chapter { break-before: page; }
h2 { font-size: 19pt; color: var(--accent); margin: 0 0 6px; padding-bottom: 8px;
     border-bottom: 3px solid var(--accent); display: flex; align-items: center; gap: 12px; break-after: avoid; }
h2 .num { background: var(--accent); color: #fff; border-radius: 8px; min-width: 38px; height: 38px;
          display: inline-flex; align-items: center; justify-content: center; font-size: 17pt; }
p.intro { color: var(--muted); margin: 4px 0 10px; }
h3 { font-size: 12pt; color: var(--accent); margin: 10px 0 5px; break-after: avoid; }
h3.trap { background: var(--band); border-left: 5px solid var(--accent2); padding: 4px 10px; border-radius: 4px; margin-top: 12px; }
h3 .tag { background: var(--accent2); color: #fff; font-size: 9pt; padding: 2px 8px; border-radius: 10px;
          margin-right: 8px; vertical-align: 2px; }
p { margin: 5px 0; }
.tb { break-inside: avoid; }
b.t { color: var(--trap); font-weight: 800; text-decoration: underline; text-decoration-thickness: 1.5px;
      text-underline-offset: 2px; }
s.bad { color: #8A94A3; text-decoration-color: var(--trap); text-decoration-thickness: 1.5px; }
.grid { display: grid; gap: 4px; margin: 4px 0 6px; }
.grid.c4 { grid-template-columns: repeat(4, 1fr); }
.w { border: 1px solid var(--line); border-radius: 5px; padding: 2px 8px; font-size: 10.5pt; break-inside: avoid;
     display: flex; align-items: center; gap: 7px; background: #fff; }
.box { width: 10px; height: 10px; border: 1.3px solid #9AA6B5; border-radius: 2px; flex: none; }
i.src { margin-left: auto; font-style: normal; font-size: 7.5pt; color: #fff; background: var(--accent2);
        padding: 0 5px; border-radius: 8px; letter-spacing: 1px; }
table { width: 100%; border-collapse: collapse; margin: 6px 0 8px; font-size: 10pt; }
tr { break-inside: avoid; }
th { background: var(--accent); color: #fff; text-align: left; padding: 4px 8px; font-weight: 600; }
td { padding: 3px 8px; border-bottom: 1px solid var(--line); vertical-align: top; }
tbody tr:nth-child(even) td { background: #F7F9FB; }
table.rules td:first-child { white-space: nowrap; color: var(--muted); }
table.rules td { font-size: 10.5pt; }
table.small { width: 60%; }
.big { font-size: 12.5pt; }
.tip { background: var(--warn); border-left: 4px solid var(--warnline); padding: 4px 10px; border-radius: 4px;
       margin: 4px 0 3px; font-size: 9.8pt; break-inside: avoid; }
ol.quiz { columns: 2; column-gap: 24px; padding-left: 26px; font-size: 11pt; }
ol.quiz li { margin: 0 0 7px; break-inside: avoid; }
.opt { display: inline-block; min-width: 47%; }
table.dict td { height: 7.4mm; padding: 1px 8px; } table.dict td.n { width: 5%; color: var(--muted); text-align: center; }
table.dict td.ck { width: 8%; } table.dict th:nth-child(4) { border-left: 3px solid #fff; }
.key { margin-top: 10px; font-size: 8.5pt; color: var(--muted); border-top: 1px dashed var(--line); padding-top: 6px; }

/* Cover */
section.cover { min-height: 262mm; display: flex; flex-direction: column; justify-content: center; padding: 0 6mm; }
.kicker { font-size: 14pt; letter-spacing: 3px; text-transform: uppercase; color: var(--accent2); font-weight: 600; }
.cover h1 { font-size: 48pt; line-height: 1.05; margin: 6px 0 4px; color: var(--accent); }
.cover .sub { font-size: 14pt; color: var(--muted); margin-bottom: 18px; }
.rule { background: #FDECEA; border-left: 6px solid var(--trap); padding: 12px 14px; font-size: 13pt;
        border-radius: 4px; margin-bottom: 18px; }
table.profile th { width: 8%; background: var(--band); color: var(--accent); text-align: center; font-size: 14pt;
                   border-bottom: 2px solid #fff; vertical-align: middle; }
table.profile td { background: #fff !important; padding: 7px 12px; }
table.profile small { color: var(--muted); }
.two { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-top: 8px; }
ol.steps { padding-left: 20px; } ol.steps li { margin: 3px 0; font-size: 11pt; }
.small { font-size: 9.5pt; color: var(--muted); }
ol.toc { list-style: none; padding: 0; margin: 0; }
ol.toc li { display: flex; gap: 10px; align-items: center; padding: 4px 0; border-bottom: 1px solid var(--line); }
.tnum { background: var(--accent); color: #fff; border-radius: 5px; min-width: 24px; height: 24px; display: inline-flex;
        align-items: center; justify-content: center; font-weight: 700; font-size: 10pt; }
.legend { margin-top: 18px; display: flex; flex-wrap: wrap; gap: 8px 22px; font-size: 9.5pt; color: var(--muted);
          border-top: 1px solid var(--line); padding-top: 10px; }
"""

page = f"""<!doctype html><html lang='en'><head><meta charset='utf-8'>
<title>IELTS Listening Spelling Words</title><style>{css}</style></head>
<body>{cover}{body}</body></html>"""
HTML.write_text(page, encoding="utf-8")

subprocess.run([EDGE, "--headless", "--disable-gpu", "--no-pdf-header-footer", "--print-to-pdf-no-header",
                f"--print-to-pdf={PDF}", HTML.as_uri()], check=True, capture_output=True, timeout=120)
print("wrote", PDF, "·", total, "unique words ·", len(multi), "repeated across articles")
