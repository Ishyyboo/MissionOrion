"""
Mission Orion: Build the Business Constellation
=================================================
A gamified BDLC (Business Development Life Cycle) booth game for QR-code play.

Deploy:  GitHub  ->  Streamlit Community Cloud  (one permanent URL for the QR code)

Anti-cheat:  every game draws a FRESH, randomized set of questions from large
             pools, and option order is shuffled each time. Two phones almost
             never see the same quiz.

Scoring:     Accuracy (max 700) + Speed (max 300) = out of 1000.
             The final page shows name, team, score and breakdown — screenshot it.
"""

import time
import random
import streamlit as st

# ---------------------------------------------------------------------------
# PAGE CONFIG + THEME
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Mission Orion", page_icon="🌟", layout="centered")

CSS = """
<style>
.stApp {
    background:
        radial-gradient(1200px 600px at 20% 10%, rgba(70,90,160,0.25), transparent 60%),
        radial-gradient(900px 500px at 85% 30%, rgba(150,90,200,0.18), transparent 60%),
        linear-gradient(180deg, #05060f 0%, #0a0d1f 55%, #070914 100%);
    color: #e8ecff;
}
.stApp:before {
    content:""; position:fixed; inset:0; pointer-events:none; z-index:0; opacity:.55;
    background-image:
        radial-gradient(1px 1px at 10% 20%, #fff 99%, transparent),
        radial-gradient(1px 1px at 30% 70%, #cfd8ff 99%, transparent),
        radial-gradient(1px 1px at 55% 35%, #fff 99%, transparent),
        radial-gradient(1px 1px at 75% 80%, #b9c4ff 99%, transparent),
        radial-gradient(1px 1px at 90% 15%, #fff 99%, transparent),
        radial-gradient(1px 1px at 45% 90%, #e8ecff 99%, transparent),
        radial-gradient(1px 1px at 5% 55%, #fff 99%, transparent);
}
.block-container { position:relative; z-index:1; max-width:820px; }
h1,h2,h3,h4,p,label,span,div { color:#e8ecff; }
.orion-card {
    background:linear-gradient(160deg, rgba(20,26,55,.92), rgba(12,16,38,.92));
    border:1px solid rgba(120,140,220,.30); border-radius:18px;
    padding:26px 28px; box-shadow:0 0 40px rgba(80,110,220,.18); margin-bottom:18px;
}
.orion-title { font-size:1.9rem; font-weight:800; letter-spacing:.5px; margin:0; }
.orion-sub { color:#aab4e6; margin:6px 0 0 0; font-size:.98rem; }
.star-badge { display:inline-block; font-size:.78rem; font-weight:700;
    padding:4px 12px; border-radius:999px; margin-bottom:10px;
    border:1px solid rgba(255,255,255,.18); }
.challenge { font-size:1.05rem; font-weight:700; margin:4px 0 14px 0; }
.progress-row { text-align:center; letter-spacing:6px; font-size:1.4rem; margin:4px 0 18px 0; }
.stButton > button {
    background:linear-gradient(135deg,#5b6dff,#8a5bff); color:#fff; border:none;
    border-radius:12px; padding:.6rem 1.2rem; font-weight:700; font-size:1rem;
    box-shadow:0 6px 20px rgba(90,110,255,.35); transition:transform .08s ease, box-shadow .2s ease;
}
.stButton > button:hover { transform:translateY(-1px); box-shadow:0 10px 26px rgba(120,100,255,.5); }
.stTextInput input, .stSelectbox div[data-baseweb="select"] > div {
    background:rgba(15,20,45,.8)!important; color:#e8ecff!important; border-radius:10px!important;
}
.score-hero { font-size:4.2rem; font-weight:900; line-height:1;
    background:linear-gradient(135deg,#ffd86b,#ff8a5b,#b06bff);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent; }
.metric-pill { background:rgba(20,26,55,.8); border:1px solid rgba(120,140,220,.25);
    border-radius:14px; padding:14px 10px; text-align:center; }
.metric-pill .v { font-size:1.5rem; font-weight:800; }
.metric-pill .k { font-size:.78rem; color:#aab4e6; text-transform:uppercase; letter-spacing:1px; }
hr { border-color:rgba(120,140,220,.2); }
.small-note { color:#8b96c8; font-size:.82rem; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# STAR META
# ---------------------------------------------------------------------------
STAR_META = [
    ("BETELGEUSE",  "Discover", "#ff5a52", "Spot the Business Opportunity"),
    ("BELLATRIX",   "Analyze",  "#5aa9ff", "Is It Worth It?"),
    ("ORION'S BELT","Design",   "#ffd86b", "Build the Business Core"),
    ("SAIPH",       "Develop",  "#ffe066", "Create the Action Plan"),
    ("RIGEL",       "Launch",   "#e8f0ff", "Pitch to Launch"),
    ("ORION NEBULA","Improve",  "#b06bff", "Read the Market Signals"),
]

# Per-game item counts (keep total fixed so scores are comparable)
N_DISCOVER, N_ANALYZE, N_IMPROVE = 3, 4, 3
N_DESIGN = 3      # 3 belt picks from 1 scenario
N_DEVELOP = 6     # 6 ordered steps from 1 plan
N_LAUNCH = 4      # 4 good pitch elements
TOTAL_ITEMS = N_DISCOVER + N_ANALYZE + N_DESIGN + N_DEVELOP + N_LAUNCH + N_IMPROVE  # 23

ACC_WEIGHT, SPEED_WEIGHT = 700, 300
MIN_TIME, MAX_TIME = 90, 600   # full speed pts <=90s, zero >=600s

# ===========================================================================
# QUESTION POOLS  (sampled per game -> huge variety, hard to cheat)
# ===========================================================================
DISCOVER_POOL = [
    {"q": "Long lines at coffee shops during rush hour. Strongest opportunity?",
     "answer": "A pre-order & skip-the-line app for nearby cafés",
     "wrong": ["Open more coffee shops everywhere", "Tell customers to wake up earlier",
               "Remove all seating to speed up lines"]},
    {"q": "Students need affordable, filling meals near campus. Best opportunity?",
     "answer": "A budget meal subscription with student bundles",
     "wrong": ["Sell luxury tasting menus to students", "Ask the school to give free food",
               "Open a fine-dining restaurant on campus"]},
    {"q": "Sari-sari stores struggle to manage online orders. Best opportunity?",
     "answer": "A simple order + inventory app for micro-retailers",
     "wrong": ["Tell them to stop selling online", "Build a giant central warehouse",
               "Require each store to hire 10 staff"]},
    {"q": "Drivers waste time circling for parking downtown. Best opportunity?",
     "answer": "A real-time app showing open parking spots nearby",
     "wrong": ["Ban all cars from downtown", "Tell drivers to leave home earlier",
               "Build parking only outside the city"]},
    {"q": "Freelancers struggle to get clients to pay on time. Best opportunity?",
     "answer": "An invoicing tool with automatic payment reminders",
     "wrong": ["Tell freelancers to quit freelancing", "Work for free to avoid the issue",
               "Demand full payment years in advance"]},
    {"q": "New gym-goers get injured using the wrong form. Best opportunity?",
     "answer": "On-demand video form-checks with a certified coach",
     "wrong": ["Remove all equipment from gyms", "Tell beginners to avoid exercise",
               "Only allow pro athletes in gyms"]},
    {"q": "Small farmers get low prices from middlemen. Best opportunity?",
     "answer": "A direct farm-to-buyer marketplace",
     "wrong": ["Tell farmers to grow less", "Add even more middlemen",
               "Sell only to one fixed buyer forever"]},
]

ANALYZE_POOL = [
    {"q": "Before building anything, the FIRST thing to validate is…",
     "answer": "Whether real customers need it and would actually pay",
     "wrong": ["What color the logo should be", "How large the future office will be",
               "Which awards the company will win"]},
    {"q": "You find ZERO competitors in your market. This usually means…",
     "answer": "Investigate carefully — there may be no real demand",
     "wrong": ["You are guaranteed to succeed", "The market is automatically huge",
               "You can skip all research"]},
    {"q": "A reliable way to estimate if people will pay is to…",
     "answer": "Run a small test or pre-sell before fully building",
     "wrong": ["Assume everyone will obviously buy", "Wait until after launch to ask anyone",
               "Only ask your immediate family"]},
    {"q": "Which is a realistic risk worth planning for?",
     "answer": "Customers adopt slower than you hoped",
     "wrong": ["The business becomes too successful instantly", "There are genuinely no risks",
               "Competitors will help you for free"]},
    {"q": "The best early way to learn what customers want is to…",
     "answer": "Talk directly to people in your target market",
     "wrong": ["Guess based only on your own taste", "Study your competitor's logo",
               "Wait for them to email you first"]},
    {"q": "Customers say they'd 'love' a feature but won't pay for it. It is…",
     "answer": "A nice-to-have — validate real willingness to pay",
     "wrong": ["A guaranteed bestseller", "Proof to build it immediately",
               "Completely irrelevant to the business"]},
    {"q": "'All my friends love the idea!' is weak evidence because…",
     "answer": "Friends are biased and may not be real buyers",
     "wrong": ["Friends are the only customers that matter", "It proves the market is huge",
               "Bias never affects feedback"]},
    {"q": "Knowing your cost per unit vs. your price tells you…",
     "answer": "Whether you can actually make a profit",
     "wrong": ["Nothing useful at all", "Only what competitors charge",
               "How big your office should be"]},
]

DESIGN_POOL = [
    {"scenario": "Concept: a **late-night street-food & coffee** spot near a university.",
     "items": [
        {"q": "⭐ Target Customer", "answer": "Night-shift workers & students who study late",
         "wrong": ["Early-morning retirees only", "Corporate breakfast meetings"]},
        {"q": "⭐ Value Proposition", "answer": "Affordable quality coffee & food, open when others are closed",
         "wrong": ["The most expensive coffee in the city", "Exactly the same hours as everyone else"]},
        {"q": "⭐ Revenue Model", "answer": "Combo bundles + a loyalty card for repeat night visits",
         "wrong": ["One-time sale, never see them again", "A yearly fee before anyone tastes it"]},
     ]},
    {"scenario": "Concept: **laundry pickup & delivery** for busy condo dwellers.",
     "items": [
        {"q": "⭐ Target Customer", "answer": "Working professionals in condos with no time to do laundry",
         "wrong": ["People who enjoy hand-washing clothes", "Factories needing industrial washing"]},
        {"q": "⭐ Value Proposition", "answer": "Doorstep pickup & next-day return — no laundromat trips",
         "wrong": ["Slower than doing it yourself", "The same effort as the laundromat"]},
        {"q": "⭐ Revenue Model", "answer": "Per-kilo pricing + weekly subscription plans",
         "wrong": ["A free service with no income", "Charge once and never again"]},
     ]},
    {"scenario": "Concept: a **tutoring marketplace** for senior-high STEM students.",
     "items": [
        {"q": "⭐ Target Customer", "answer": "Senior-high students struggling with math & science",
         "wrong": ["Retirees learning for fun", "Toddlers in daycare"]},
        {"q": "⭐ Value Proposition", "answer": "Vetted tutors matched fast, sessions that fit school schedules",
         "wrong": ["Random unverified strangers", "Only available during class hours"]},
        {"q": "⭐ Revenue Model", "answer": "Commission per booked session + bundle packages",
         "wrong": ["No fees, purely charity", "One huge upfront fee for life"]},
     ]},
    {"scenario": "Concept: **healthy meal-prep delivery** for gym-goers.",
     "items": [
        {"q": "⭐ Target Customer", "answer": "Fitness folks who track macros but can't cook daily",
         "wrong": ["People avoiding all healthy food", "Those who never exercise or eat out"]},
        {"q": "⭐ Value Proposition", "answer": "Macro-counted meals delivered weekly, ready to eat",
         "wrong": ["Random meals with no nutrition info", "Raw ingredients you still must cook"]},
        {"q": "⭐ Revenue Model", "answer": "Weekly meal-plan subscription tiers",
         "wrong": ["Free meals forever", "One payment for unlimited lifetime meals"]},
     ]},
    {"scenario": "Concept: a **pop-up phone-repair kiosk** inside malls.",
     "items": [
        {"q": "⭐ Target Customer", "answer": "Mall shoppers with cracked screens or dying batteries",
         "wrong": ["People who never own phones", "Companies that only sell brand-new phones"]},
        {"q": "⭐ Value Proposition", "answer": "Fast walk-in repairs while you shop",
         "wrong": ["Repairs that take three weeks", "You must mail your phone overseas"]},
        {"q": "⭐ Revenue Model", "answer": "Per-repair fees + accessory upsells",
         "wrong": ["No charge for any repair", "An annual fee before any repair is done"]},
     ]},
]

DEVELOP_POOL = [
    {"label": "a new product",
     "order": ["Research customers", "Build a prototype", "Set pricing",
               "Find suppliers", "Test with real users", "Prepare launch materials"]},
    {"label": "a mobile app",
     "order": ["Define the core problem", "Design the MVP", "Build the MVP",
               "Run a closed beta", "Fix bugs from feedback", "Public launch"]},
    {"label": "a food cart",
     "order": ["Scout the best location", "Design the menu", "Source ingredients",
               "Price the items", "Run a soft-opening trial", "Grand opening"]},
    {"label": "a service business",
     "order": ["Identify your niche", "Package the service offer", "Set your rates",
               "Build a sample portfolio", "Land first paying clients", "Scale your outreach"]},
    {"label": "an online store",
     "order": ["Pick the product", "Validate the demand", "Source the stock",
               "Build the online store", "Soft launch to a small list", "Scale paid ads"]},
]

LAUNCH_POOL = [
    {"good": ["The problem you solve", "Who it's for (target customer)",
              "Your solution in one clear line", "A clear call to action / the ask"],
     "bad":  ["Your full life story since childhood", "Heavy jargon nobody understands",
              "Unrelated personal anecdotes"]},
    {"good": ["The pain point in one sentence", "Your ideal customer",
              "What makes you different", "The specific next step you want"],
     "bad":  ["Your company's entire 10-year timeline", "Buzzwords and acronyms nobody knows",
              "Off-topic jokes and tangents"]},
    {"good": ["The core problem, stated simply", "The exact audience you serve",
              "The benefit the customer gets", "A clear ask or next action"],
     "bad":  ["A long history of every past job", "Dense technical specifications",
              "Random stories unrelated to the product"]},
]

IMPROVE_POOL = [
    {"q": "Signal: Customers love it but say it's too expensive.",
     "answer": "Offer a smaller, lower-priced version or bundle",
     "wrong": ["Raise the price even higher", "Ignore the feedback completely",
               "Stop selling the product"]},
    {"q": "Signal: Sales are strong on weekends but weak on weekdays.",
     "answer": "Run weekday promos or target weekday customers",
     "wrong": ["Close on weekends too", "Change nothing at all", "Raise weekend prices only"]},
    {"q": "Signal: Customers keep asking for delivery.",
     "answer": "Pilot a delivery option and measure demand",
     "wrong": ["Insist they always come in person", "Remove the product entirely",
               "Raise prices to discourage them"]},
    {"q": "Signal: Lots of website visitors, but very few buy.",
     "answer": "Simplify checkout and clarify the offer",
     "wrong": ["Add more steps to checkout", "Hide the prices", "Remove the buy button"]},
    {"q": "Signal: Great first-time reviews but few customers return.",
     "answer": "Add a loyalty program and follow-up",
     "wrong": ["Stop talking to past customers", "Only chase brand-new customers",
               "Make returning harder"]},
    {"q": "Signal: One product sells well; the others barely move.",
     "answer": "Double down on the winner, trim the rest",
     "wrong": ["Push only the weak products harder", "Stop selling the popular one",
               "Keep everything exactly the same"]},
    {"q": "Signal: New users say the product is confusing to use.",
     "answer": "Improve onboarding and clearer instructions",
     "wrong": ["Tell users to figure it out", "Add more complex features",
               "Remove the help section"]},
]

# ---------------------------------------------------------------------------
# QUIZ BUILDER  (materialize one frozen quiz per game)
# ---------------------------------------------------------------------------
def _mcq(item):
    opts = [item["answer"]] + list(item["wrong"])
    random.shuffle(opts)
    return {"q": item["q"], "options": opts, "answer": item["answer"]}

def build_quiz():
    q = {}
    q["discover"] = [_mcq(it) for it in random.sample(DISCOVER_POOL, N_DISCOVER)]
    q["analyze"]  = [_mcq(it) for it in random.sample(ANALYZE_POOL, N_ANALYZE)]

    sc = random.choice(DESIGN_POOL)
    q["design"] = {"scenario": sc["scenario"], "items": [_mcq(it) for it in sc["items"]]}

    plan = random.choice(DEVELOP_POOL)
    display = plan["order"][:]
    random.shuffle(display)
    q["develop"] = {"label": plan["label"], "correct": plan["order"], "display": display}

    s = random.choice(LAUNCH_POOL)
    allopts = s["good"] + s["bad"]
    random.shuffle(allopts)
    q["launch"] = {"good": s["good"], "bad": s["bad"], "all": allopts}

    q["improve"] = [_mcq(it) for it in random.sample(IMPROVE_POOL, N_IMPROVE)]
    return q

# ---------------------------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------------------------
def init_state():
    ss = st.session_state
    ss.setdefault("stage", 0)        # 0 welcome, 1..6 stations, 7 results
    ss.setdefault("name", "")
    ss.setdefault("team", "")
    ss.setdefault("quiz", None)
    ss.setdefault("start_time", None)
    ss.setdefault("finish_time", None)
    ss.setdefault("celebrated", False)

init_state()

def goto(stage):
    st.session_state.stage = stage
    st.rerun()

def progress_dots(active_idx):
    dots = ["🌟" if i < active_idx else ("⭐" if i == active_idx else "✩") for i in range(6)]
    st.markdown(f"<div class='progress-row'>{' '.join(dots)}</div>", unsafe_allow_html=True)

def station_header(idx):
    star, stage, color, challenge = STAR_META[idx]
    st.markdown(
        f"""
        <div class='orion-card'>
          <span class='star-badge' style='color:{color}; border-color:{color}55; background:{color}14;'>
            {star} · BDLC STAGE {idx+1}/6
          </span>
          <p class='orion-title' style='color:{color};'>{stage}</p>
          <p class='challenge'>Challenge: {challenge}</p>
        </div>
        """, unsafe_allow_html=True)

# ===========================================================================
# PAGES
# ===========================================================================
def page_welcome():
    st.markdown(
        """
        <div class='orion-card' style='text-align:center;'>
          <p class='orion-sub' style='letter-spacing:3px;'>MISSION ORION</p>
          <p class='orion-title' style='font-size:2.4rem;'>Build the Business Constellation 🌌</p>
          <p class='orion-sub'>Every successful business is like a constellation. Connect the stars and a
          clear direction appears. Navigate Orion through 6 BDLC stages:
          <b>Discover → Analyze → Design → Develop → Launch → Improve.</b></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("#### 🚀 Register your explorer")
    name = st.text_input("Explorer name", value=st.session_state.name, placeholder="e.g. Ish")
    team = st.text_input("Team / Crew name", value=st.session_state.team, placeholder="e.g. CPT 10")

    st.markdown(
        "<p class='small-note'>🔀 Every game pulls a <b>fresh, randomized</b> set of questions — "
        "no two players get the same quiz. Your score blends <b>accuracy</b> (correct answers) "
        "and <b>speed</b> (the timer starts when you launch).</p>", unsafe_allow_html=True)

    if st.button("Begin Mission ✦", use_container_width=True):
        if not name.strip() or not team.strip():
            st.warning("Enter both your name and team to launch.")
        else:
            ss = st.session_state
            ss.name = name.strip()
            ss.team = team.strip()
            ss.quiz = build_quiz()
            ss.celebrated = False
            ss.finish_time = None
            ss.start_time = time.time()
            goto(1)

def page_station(idx):
    quiz = st.session_state.quiz
    if quiz is None:           # safety: session lost mid-game
        goto(0)
    progress_dots(idx)
    station_header(idx)

    if idx == 0:               # Discover
        for i, it in enumerate(quiz["discover"]):
            st.radio(it["q"], it["options"], index=None, key=f"discover_{i}")
            st.markdown("")
    elif idx == 1:             # Analyze
        for i, it in enumerate(quiz["analyze"]):
            st.radio(it["q"], it["options"], index=None, key=f"analyze_{i}")
            st.markdown("")
    elif idx == 2:             # Design
        st.markdown(quiz["design"]["scenario"])
        st.markdown("Pick the strongest piece for each of the three Belt stars:")
        for i, it in enumerate(quiz["design"]["items"]):
            st.radio(it["q"], it["options"], index=None, key=f"design_{i}")
            st.markdown("")
    elif idx == 3:             # Develop (ordering)
        st.markdown(f"**Put the steps for launching {quiz['develop']['label']} in the right order.**")
        st.multiselect(
            "Click the steps in sequence (selection order = your answer):",
            options=quiz["develop"]["display"], key="develop_order",
            placeholder="Pick step 1, then 2, then 3 …")
        st.markdown("<p class='small-note'>Pick all 6. The order you click is the order we grade.</p>",
                    unsafe_allow_html=True)
    elif idx == 4:             # Launch
        st.markdown("**Assemble the strongest 15-second launch pitch. Choose only what belongs.**")
        st.multiselect("Pitch elements:", options=quiz["launch"]["all"], key="launch_sel",
                       placeholder="Select the elements of a tight pitch …")
        st.text_area("(Optional) Type your real 15-second pitch for fun — not scored:",
                     key="launch_pitch",
                     placeholder="We help ___ who struggle with ___ by ___. Try us today!")
    elif idx == 5:             # Improve
        for i, it in enumerate(quiz["improve"]):
            st.radio(it["q"], it["options"], index=None, key=f"improve_{i}")
            st.markdown("")

    col1, col2 = st.columns(2)
    with col1:
        if idx > 0 and st.button("← Back", use_container_width=True):
            goto(idx)                       # current stage is idx+1; back is idx
    with col2:
        last = idx == 5
        label = "Reveal My Score ✦" if last else "Continue →"
        if st.button(label, use_container_width=True):
            if last:
                st.session_state.finish_time = time.time()
                goto(7)
            else:
                goto(idx + 2)               # current stage idx+1 -> next idx+2

# ---------------------------------------------------------------------------
# SCORING
# ---------------------------------------------------------------------------
def compute_breakdown():
    ss = st.session_state
    quiz = ss.quiz
    rows = []

    c = sum(1 for i, it in enumerate(quiz["discover"]) if ss.get(f"discover_{i}") == it["answer"])
    rows.append(("Discover", c, N_DISCOVER))

    c = sum(1 for i, it in enumerate(quiz["analyze"]) if ss.get(f"analyze_{i}") == it["answer"])
    rows.append(("Analyze", c, N_ANALYZE))

    c = sum(1 for i, it in enumerate(quiz["design"]["items"]) if ss.get(f"design_{i}") == it["answer"])
    rows.append(("Design", c, N_DESIGN))

    order = ss.get("develop_order", []) or []
    correct = quiz["develop"]["correct"]
    c = sum(1 for pos, step in enumerate(order) if pos < len(correct) and step == correct[pos])
    rows.append(("Develop", c, N_DEVELOP))

    sel = ss.get("launch_sel", []) or []
    good = sum(1 for x in sel if x in quiz["launch"]["good"])
    bad = sum(1 for x in sel if x in quiz["launch"]["bad"])
    c = max(0, min(N_LAUNCH, good - bad))
    rows.append(("Launch", c, N_LAUNCH))

    c = sum(1 for i, it in enumerate(quiz["improve"]) if ss.get(f"improve_{i}") == it["answer"])
    rows.append(("Improve", c, N_IMPROVE))

    correct_total = sum(r[1] for r in rows)
    return rows, correct_total

def title_for(score):
    if score >= 900: return "Certified Orion Business Navigator ⭐ (Legendary)"
    if score >= 750: return "Star Commander"
    if score >= 600: return "Constellation Builder"
    if score >= 400: return "Rising Explorer"
    return "Cadet — mission restart recommended"

def page_results():
    ss = st.session_state
    rows, correct = compute_breakdown()
    elapsed = (ss.finish_time or time.time()) - (ss.start_time or time.time())

    accuracy = correct / TOTAL_ITEMS
    acc_points = accuracy * ACC_WEIGHT
    if elapsed <= MIN_TIME:
        speed_frac = 1.0
    elif elapsed >= MAX_TIME:
        speed_frac = 0.0
    else:
        speed_frac = (MAX_TIME - elapsed) / (MAX_TIME - MIN_TIME)
    speed_points = speed_frac * SPEED_WEIGHT
    score = round(acc_points + speed_points)

    if not ss.celebrated:
        st.balloons()
        ss.celebrated = True

    mins, secs = divmod(int(elapsed), 60)
    st.markdown(
        f"""
        <div class='orion-card' style='text-align:center;'>
          <p class='orion-sub' style='letter-spacing:3px;'>CONSTELLATION COMPLETE 🌌</p>
          <p class='orion-title' style='font-size:1.6rem;'>{ss.name} ·
            <span style='color:#8a5bff'>{ss.team}</span></p>
          <div class='score-hero'>{score}</div>
          <p class='orion-sub'>out of 1000 — <b>{title_for(score)}</b></p>
        </div>
        """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    for col, k, v in [
        (c1, "Correct", f"{correct}/{TOTAL_ITEMS}"),
        (c2, "Accuracy pts", f"{round(acc_points)}/{ACC_WEIGHT}"),
        (c3, "Speed pts", f"{round(speed_points)}/{SPEED_WEIGHT}"),
    ]:
        col.markdown(f"<div class='metric-pill'><div class='v'>{v}</div><div class='k'>{k}</div></div>",
                     unsafe_allow_html=True)

    st.markdown(f"<p style='text-align:center; margin-top:10px;'>⏱️ Time: <b>{mins}m {secs}s</b></p>",
                unsafe_allow_html=True)

    st.markdown("#### ✦ Star-by-star breakdown")
    for stage, cc, tt in rows:
        st.markdown(f"**{stage}** — {cc}/{tt}  {'🌟'*cc}{'✩'*(tt-cc)}")

    st.markdown("<p class='small-note' style='text-align:center;'>📸 Screenshot this screen to record your score.</p>",
                unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔁 New Explorer (Play Again)", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        init_state()
        st.rerun()

# ===========================================================================
# ROUTER
# ===========================================================================
stage = st.session_state.stage
if stage == 0:
    page_welcome()
elif 1 <= stage <= 6:
    page_station(stage - 1)
else:
    page_results()
