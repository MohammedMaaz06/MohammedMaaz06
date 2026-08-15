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


# ---------------------------------------------------------
# FETCH REAL GITHUB CONTRIBUTION DATA
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# CALENDAR CONFIGURATION
# ---------------------------------------------------------

CELL = 11
GAP = 3
STEP = CELL + GAP

LEFT = 55
TOP = 58

WEEKS = len(weeks)

WIDTH = LEFT + WEEKS * STEP + 20
HEIGHT = 215


# ---------------------------------------------------------
# CONTRIBUTION COLORS
# ---------------------------------------------------------

COLORS = [
    "#ebedf0",
    "#9be9a8",
    "#40c463",
    "#30a14e",
    "#216e39",
]


# ---------------------------------------------------------
# SVG START
# ---------------------------------------------------------

svg = []

svg.append(
    f'''<svg
xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {WIDTH} {HEIGHT}"
width="{WIDTH}"
height="{HEIGHT}">

<defs>

    <linearGradient
        id="flightGradient"
        x1="0%"
        y1="0%"
        x2="100%"
        y2="0%">

        <stop
            offset="0%"
            stop-color="#2563eb"/>

        <stop
            offset="45%"
            stop-color="#06b6d4"/>

        <stop
            offset="75%"
            stop-color="#10b981"/>

        <stop
            offset="100%"
            stop-color="#22c55e"/>

    </linearGradient>

    <filter
        id="planeGlow"
        x="-100%"
        y="-100%"
        width="300%"
        height="300%">

        <feGaussianBlur
            stdDeviation="2"
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


<!-- CARD -->

<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="7"
    fill="#ffffff"
    stroke="#d0d7de"/>


<!-- HEADER -->

<text
    class="header"
    x="18"
    y="28">

{total} contributions in the last year

</text>

'''
)


# ---------------------------------------------------------
# MONTH LABELS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# WEEKDAY LABELS
# ---------------------------------------------------------

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


# ---------------------------------------------------------
# REAL CONTRIBUTION CELLS
# ---------------------------------------------------------

for week_index, week in enumerate(weeks):

    for day in week["contributionDays"]:

        weekday = day["weekday"]
        count = day["contributionCount"]

        x = LEFT + week_index * STEP
        y = TOP + weekday * STEP


        # Contribution intensity

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


# ---------------------------------------------------------
# LEGEND ONLY
# ---------------------------------------------------------
# Removed:
# - "Learn how we count contributions"
# - "Contribution settings"
#
# The legend remains because it represents the real
# contribution intensity levels.

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


# ---------------------------------------------------------
# MOVING STEALTH JET
# ---------------------------------------------------------
# The jet travels INSIDE the actual contribution calendar.
#
# The contribution cells above are NOT changed.
# They continue to represent real GitHub contribution data.
#
# rotate="auto" makes the jet nose follow the flight path.
# There is NO 360-degree rotation.

graph_left = LEFT
graph_right = LEFT + (WEEKS - 1) * STEP

graph_top = TOP
graph_bottom = TOP + 6 * STEP


# ---------------------------------------------------------
# FLIGHT PATH
# ---------------------------------------------------------

graph_left = LEFT + 8
graph_right = LEFT + (WEEKS - 1) * STEP - 8

# Keep the jet centered inside the contribution grid.
jet_y = TOP + 3 * STEP + 5

# Simple straight flight.
# No visible path.
# No random movement.
# No rotation.
flight_path = (
    f"M {graph_left} {jet_y} "
    f"L {graph_right} {jet_y}"
)


# ---------------------------------------------------------
# SUBTLE FLIGHT TRAIL
# ---------------------------------------------------------

svg.append(
    f'''
<path
    d="{flight_path}"
    fill="none"
    stroke="url(#flightGradient)"
    stroke-width="1"
    stroke-opacity="0.12"
    stroke-dasharray="3 6"/>
'''
)


# ---------------------------------------------------------
# STEALTH JET
# ---------------------------------------------------------

svg.append(
    f'''
<g
    filter="url(#planeGlow)">

    <animateMotion
        dur="14s"
        repeatCount="indefinite"
        rotate="auto"
        path="{flight_path}"/>


    <!--
        Stealth flying-wing jet.

        The nose points toward the right.
        animateMotion + rotate="auto"
        makes the nose follow the flight path.
    -->

    <g transform="scale(0.65)">

        <!-- Main stealth body -->

        <path
            d="
                M 24 0
                L 8 -4
                L -8 -13
                L -34 -9
                L -15 -2
                L -38 0
                L -15 2
                L -34 9
                L -8 13
                L 8 4
                Z
            "
            fill="#1f2937"
            stroke="#111827"
            stroke-width="1"/>


        <!-- Upper wing -->

        <path
            d="
                M 8 -2
                L -18 -18
                L -38 -17
                L -14 -1
                Z
            "
            fill="#374151"
            stroke="#111827"
            stroke-width="1"/>


        <!-- Lower wing -->

        <path
            d="
                M 8 2
                L -18 18
                L -38 17
                L -14 1
                Z
            "
            fill="#374151"
            stroke="#111827"
            stroke-width="1"/>


        <!-- Cockpit -->

        <path
            d="
                M 8 -3
                L 19 0
                L 8 3
                L 3 0
                Z
            "
            fill="#38bdf8"/>


        <!-- Engine glow -->

        <path
            d="
                M -25 -2
                L -39 0
                L -25 2
                Z
            "
            fill="#22d3ee"/>

    </g>

</g>
'''
)


# ---------------------------------------------------------
# CLOSE SVG
# ---------------------------------------------------------

svg.append(
    '''
</svg>
'''
)


# ---------------------------------------------------------
# WRITE FILE
# ---------------------------------------------------------

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
