import json
import os
import urllib.request
from datetime import datetime


USERNAME = os.environ["GITHUB_USER"]
TOKEN = os.environ["GITHUB_TOKEN"]


QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
            weekday
          }
        }
      }
    }
  }
}
"""


# =========================================================
# FETCH REAL GITHUB CONTRIBUTION DATA
# =========================================================

payload = json.dumps({
    "query": QUERY,
    "variables": {
        "login": USERNAME
    }
}).encode("utf-8")


request = urllib.request.Request(
    "https://api.github.com/graphql",
    data=payload,
    headers={
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "application/json",
        "User-Agent": "MohammedMaaz06-contribution-calendar"
    }
)


with urllib.request.urlopen(request) as response:
    result = json.loads(response.read())


if "errors" in result:
    raise RuntimeError(
        json.dumps(result["errors"], indent=2)
    )


calendar = (
    result["data"]
    ["user"]
    ["contributionsCollection"]
    ["contributionCalendar"]
)


weeks = calendar["weeks"]
total = calendar["totalContributions"]


# =========================================================
# CALENDAR CONFIGURATION
# =========================================================

CELL = 11
GAP = 3
STEP = CELL + GAP

LEFT = 55
TOP = 58

WEEKS = len(weeks)

WIDTH = LEFT + WEEKS * STEP + 20
HEIGHT = 215


# =========================================================
# GITHUB CONTRIBUTION COLORS
# =========================================================

COLORS = [
    "#ebedf0",
    "#9be9a8",
    "#40c463",
    "#30a14e",
    "#216e39",
]


# =========================================================
# SVG START
# =========================================================

svg = []

svg.append(
    f'''<svg
xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {WIDTH} {HEIGHT}"
width="{WIDTH}"
height="{HEIGHT}">

<defs>

    <filter
        id="jetGlow"
        x="-100%"
        y="-100%"
        width="300%"
        height="300%">

        <feGaussianBlur
            stdDeviation="1.5"
            result="blur"/>

        <feMerge>
            <feMergeNode in="blur"/>
            <feMergeNode in="SourceGraphic"/>
        </feMerge>

    </filter>

</defs>


<style>

text {{
    font-family:
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;
}}

.header {{
    fill: #24292f;
    font-size: 14px;
}}

.month {{
    fill: #57606a;
    font-size: 10px;
}}

.weekday {{
    fill: #57606a;
    font-size: 10px;
}}

.footer {{
    fill: #57606a;
    font-size: 10px;
}}

</style>


<!-- =====================================================
     CARD
     ===================================================== -->

<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="7"
    fill="#ffffff"
    stroke="#d0d7de"/>


<!-- =====================================================
     HEADER
     ===================================================== -->

<text
    class="header"
    x="18"
    y="28">

{total} contributions in the last year

</text>

'''
)


# =========================================================
# MONTH LABELS
# =========================================================

previous_month = None


for week_index, week in enumerate(weeks):

    first_day = week["contributionDays"][0]["date"]

    date = datetime.strptime(
        first_day,
        "%Y-%m-%d"
    )

    month = date.strftime("%b")

    if month != previous_month:

        x = LEFT + week_index * STEP

        svg.append(
            f'''
<text
    class="month"
    x="{x}"
    y="47">

{month}

</text>
'''
        )

        previous_month = month


# =========================================================
# WEEKDAY LABELS
# =========================================================

weekday_labels = {
    1: "Mon",
    3: "Wed",
    5: "Fri",
}


for weekday, label in weekday_labels.items():

    y = TOP + weekday * STEP - 2

    svg.append(
        f'''
<text
    class="weekday"
    x="7"
    y="{y}">

{label}

</text>
'''
    )


# =========================================================
# REAL GITHUB CONTRIBUTION CELLS
# =========================================================

for week_index, week in enumerate(weeks):

    for day in week["contributionDays"]:

        weekday = day["weekday"]
        count = day["contributionCount"]

        x = LEFT + week_index * STEP
        y = TOP + weekday * STEP


        if count == 0:
            level = 0

        elif count <= 2:
            level = 1

        elif count <= 5:
            level = 2

        elif count <= 9:
            level = 3

        else:
            level = 4


        color = COLORS[level]


        svg.append(
            f'''
<rect
    x="{x}"
    y="{y}"
    width="{CELL}"
    height="{CELL}"
    rx="2"
    ry="2"
    fill="{color}"
    stroke="#ffffff"
    stroke-width="1">

    <title>
        {day["date"]}: {count} contributions
    </title>

</rect>
'''
        )


# =========================================================
# CONTRIBUTION LEGEND
# =========================================================

footer_y = TOP + 7 * STEP + 25

legend_x = WIDTH - 116


svg.append(
    f'''
<text
    class="footer"
    x="{legend_x - 30}"
    y="{footer_y}">

Less

</text>
'''
)


for index, color in enumerate(COLORS):

    x = legend_x + index * 14

    svg.append(
        f'''
<rect
    x="{x}"
    y="{footer_y - 9}"
    width="11"
    height="11"
    rx="2"
    fill="{color}"/>
'''
    )


svg.append(
    f'''
<text
    class="footer"
    x="{legend_x + 78}"
    y="{footer_y}">

More

</text>
'''
)


# =========================================================
# SMOOTH JET ANIMATION
# =========================================================
#
# The jet moves directly INSIDE the real contribution grid.
#
# Movement:
#
#       START
#         ✈  -------------------->
#
#                              END
#                               ✈
#
# Then smoothly returns:
#
#                              ✈
#                         <----
#
#         ✈
#
# No flight trail.
# No random movement.
# No 360 degree rotation.
# No animateMotion.
#


jet_start_x = LEFT + 12
jet_end_x = LEFT + (WEEKS - 1) * STEP - 12

jet_y = TOP + 3 * STEP + 5


# =========================================================
# JET
# =========================================================

svg.append(
    f'''
<g
    filter="url(#jetGlow)">

    <!--
        Smooth left -> right -> left animation.

        The jet remains completely stable.
        The jet does NOT rotate.
    -->

    <animateTransform
        attributeName="transform"
        attributeType="XML"
        type="translate"

        values="
            {jet_start_x} {jet_y};
            {jet_end_x} {jet_y};
            {jet_start_x} {jet_y}
        "

        dur="20s"
        repeatCount="indefinite"

        calcMode="spline"

        keyTimes="0;0.5;1"

        keySplines="
            0.42 0 0.58 1;
            0.42 0 0.58 1
        "
    />


    <!-- =================================================
         STEALTH JET
         ================================================= -->

    <g
        transform="scale(0.65)">


        <!-- Main body -->

        <path
            d="
                M 28 0
                L 10 -4
                L -8 -13
                L -38 -9
                L -16 -2
                L -42 0
                L -16 2
                L -38 9
                L -8 13
                L 10 4
                Z
            "
            fill="#1f2937"
            stroke="#111827"
            stroke-width="1.2"/>


        <!-- Upper wing -->

        <path
            d="
                M 10 -2
                L -20 -19
                L -42 -17
                L -15 -1
                Z
            "
            fill="#374151"
            stroke="#111827"
            stroke-width="1"/>


        <!-- Lower wing -->

        <path
            d="
                M 10 2
                L -20 19
                L -42 17
                L -15 1
                Z
            "
            fill="#374151"
            stroke="#111827"
            stroke-width="1"/>


        <!-- Cockpit -->

        <path
            d="
                M 10 -3
                L 22 0
                L 10 3
                L 4 0
                Z
            "
            fill="#38bdf8"/>


        <!-- Engine -->

        <path
            d="
                M -27 -2
                L -43 0
                L -27 2
                Z
            "
            fill="#22d3ee"/>

    </g>

</g>
'''
)


# =========================================================
# CLOSE SVG
# =========================================================

svg.append(
    '''
</svg>
'''
)


# =========================================================
# WRITE GENERATED SVG
# =========================================================

os.makedirs(
    "assets",
    exist_ok=True
)


output_file = "assets/contributions.svg"


with open(
    output_file,
    "w",
    encoding="utf-8"
) as file:

    file.write(
        "".join(svg)
    )


print(
    f"Generated contribution calendar for "
    f"{USERNAME}: {total} contributions"
)
