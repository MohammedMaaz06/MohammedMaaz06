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
# MOVING FUTURISTIC JET — INSIDE CONTRIBUTION GRAPH
# ---------------------------------------------------------

# Contribution grid boundaries
graph_left = LEFT + 5
graph_right = LEFT + (WEEKS - 1) * STEP + CELL - 5

graph_top = TOP + 5
graph_bottom = TOP + 6 * STEP + CELL - 5

graph_center_x = (graph_left + graph_right) / 2
graph_center_y = (graph_top + graph_bottom) / 2

orbit_radius_x = (graph_right - graph_left) / 2
orbit_radius_y = (graph_bottom - graph_top) / 2


# ---------------------------------------------------------
# JET FLIGHT PATH
# ---------------------------------------------------------
# The path stays INSIDE the contribution calendar.

flight_path = (
    f"M {graph_center_x + orbit_radius_x},{graph_center_y} "
    f"A {orbit_radius_x},{orbit_radius_y} 0 1 1 "
    f"{graph_center_x - orbit_radius_x},{graph_center_y} "
    f"A {orbit_radius_x},{orbit_radius_y} 0 1 1 "
    f"{graph_center_x + orbit_radius_x},{graph_center_y}"
)


# Subtle flight trail inside the contribution graph

svg.append(
    f'''
<path
    d="{flight_path}"
    fill="none"
    stroke="url(#flightGradient)"
    stroke-width="1"
    stroke-opacity="0.18"
    stroke-dasharray="3 6"/>
'''
)


# ---------------------------------------------------------
# FUTURISTIC JET
# ---------------------------------------------------------

svg.append(
    f'''
<g filter="url(#planeGlow)">

    <!-- Move around the contribution graph -->

    <g>

        <animateMotion
            dur="10s"
            repeatCount="indefinite"
            rotate="auto"
            path="{flight_path}"/>


        <!-- Full 360 degree jet rotation -->

        <g>

            <animateTransform
                attributeName="transform"
                type="rotate"
                from="0"
                to="360"
                dur="2s"
                repeatCount="indefinite"/>


            <!-- JET -->

            <g transform="scale(0.8)">

                <!-- Main fuselage -->

                <path
                    d="
                        M -14 0
                        L 7 0
                        L 16 -4
                        L 21 0
                        L 16 4
                        L 7 0
                        Z
                    "
                    fill="#06b6d4"
                    stroke="#0369a1"
                    stroke-width="1"
                />


                <!-- Top wing -->

                <path
                    d="
                        M 2 0
                        L -7 -10
                        L -1 -9
                        L 8 -1
                        Z
                    "
                    fill="#0284c7"
                />


                <!-- Bottom wing -->

                <path
                    d="
                        M 2 0
                        L -7 10
                        L -1 9
                        L 8 1
                        Z
                    "
                    fill="#0284c7"
                />


                <!-- Tail -->

                <path
                    d="
                        M -8 0
                        L -13 -7
                        L -8 -6
                        L -3 0
                        Z
                    "
                    fill="#075985"
                />


                <!-- Cockpit -->

                <ellipse
                    cx="8"
                    cy="-1"
                    rx="3"
                    ry="1.5"
                    fill="#ffffff"
                />


                <!-- Engine -->

                <circle
                    cx="-10"
                    cy="0"
                    r="2"
                    fill="#22d3ee"
                />


                <!-- Engine trail -->

                <path
                    d="M -12 0 L -24 0"
                    stroke="#22d3ee"
                    stroke-width="2"
                    stroke-linecap="round"
                />

            </g>

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
