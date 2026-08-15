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

.settings {{
    fill: #57606a;
    font-size: 11px;
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


<text
    class="settings"
    x="{WIDTH - 125}"
    y="28">

Contribution settings

</text>


<path
    d="M {WIDTH - 13} 24 l 5 0 l -2.5 3 z"
    fill="#57606a"/>

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
# FOOTER / LEGEND
# ---------------------------------------------------------

footer_y = TOP + 7 * STEP + 25


svg.append(
    f'''
<text
    class="footer"
    x="55"
    y="{footer_y}">

Learn how we count contributions

</text>


<text
    class="footer"
    x="{WIDTH - 145}"
    y="{footer_y}">

Less

</text>
'''
)


legend_x = WIDTH - 116


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
# MOVING STEALTH JET — INSIDE CONTRIBUTION GRAPH
# ---------------------------------------------------------

# Contribution grid boundaries

graph_left = LEFT
graph_right = LEFT + (WEEKS - 1) * STEP + CELL

graph_top = TOP
graph_bottom = TOP + 6 * STEP + CELL


# ---------------------------------------------------------
# FLIGHT PATH
# ---------------------------------------------------------
# The jet travels through the contribution calendar.
# It does NOT leave the graph.

flight_path = (
    f"M {graph_left + 8} {graph_bottom - 8} "
    f"C {graph_left + 80} {graph_top + 5}, "
    f"{graph_left + 160} {graph_top + 5}, "
    f"{graph_left + 230} {graph_bottom - 8} "

    f"C {graph_left + 310} {graph_bottom - 8}, "
    f"{graph_left + 390} {graph_top + 5}, "
    f"{graph_left + 470} {graph_top + 5} "

    f"C {graph_left + 550} {graph_top + 5}, "
    f"{graph_left + 630} {graph_bottom - 8}, "
    f"{graph_right - 8} {graph_top + 8}"
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
    stroke-width="1.5"
    stroke-opacity="0.20"
    stroke-dasharray="4 6"/>
'''
)


# ---------------------------------------------------------
# STEALTH JET
# ---------------------------------------------------------

svg.append(
    f'''
<g filter="url(#planeGlow)">

    <!-- Jet follows the path.
         rotate="auto" keeps the NOSE aligned
         with the direction of travel. -->

    <g>

        <animateMotion
            dur="12s"
            repeatCount="indefinite"
            rotate="auto"
            path="{flight_path}"
        />


        <!--
        B-2 / flying-wing inspired silhouette

        The jet itself NEVER spins.
        It only turns naturally with the flight path.
        -->

        <g transform="scale(0.95)">

            <!-- Main flying-wing body -->

            <path
                d="
                    M -20 2

                    L -8 -2
                    L -2 -7
                    L 4 -10
                    L 9 -8
                    L 18 -3
                    L 27 0

                    L 18 3
                    L 9 8
                    L 4 10
                    L -2 7
                    L -8 2

                    Z
                "
                fill="#111827"
                stroke="#075985"
                stroke-width="0.9"
            />


            <!-- Left swept wing -->

            <path
                d="
                    M -2 -2
                    L -19 -10
                    L -31 -7
                    L -8 1
                    Z
                "
                fill="#1f2937"
                stroke="#0e7490"
                stroke-width="0.6"
            />


            <!-- Right swept wing -->

            <path
                d="
                    M -2 2
                    L -19 10
                    L -31 7
                    L -8 -1
                    Z
                "
                fill="#1f2937"
                stroke="#0e7490"
                stroke-width="0.6"
            />


            <!-- Central stealth body -->

            <path
                d="
                    M -12 0
                    L 8 -5
                    L 22 0
                    L 8 5
                    Z
                "
                fill="#374151"
            />


            <!-- Cockpit -->

            <path
                d="
                    M 7 -2
                    L 15 0
                    L 7 2
                    L 4 0
                    Z
                "
                fill="#38bdf8"
            />


            <!-- Engine glow -->

            <path
                d="
                    M -23 -2
                    L -31 0
                    L -23 2
                    Z
                "
                fill="#22d3ee"
            />

        </g>

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
