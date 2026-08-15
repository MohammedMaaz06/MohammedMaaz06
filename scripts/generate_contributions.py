import json
import math
import os
import random
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
# FETCH REAL GITHUB CONTRIBUTIONS
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
# CALENDAR
# =========================================================

CELL = 11
GAP = 3
STEP = CELL + GAP

LEFT = 55
TOP = 58

WEEKS = len(weeks)

WIDTH = LEFT + WEEKS * STEP + 20
HEIGHT = 215


COLORS = [
    "#ebedf0",
    "#9be9a8",
    "#40c463",
    "#30a14e",
    "#216e39",
]


# =========================================================
# RANDOM FLIGHT ROUTE
# =========================================================
#
# The route is generated every time this script runs.
#
# The jet:
#
#   ✈ → ↗ → ↑ → ↖ → ← → ↙ → ↓ → ↘ → →
#
# changes direction naturally.
#
# The path is NOT displayed.
#
# =========================================================

random.seed()


FLIGHT_LEFT = LEFT + 8
FLIGHT_RIGHT = LEFT + (WEEKS - 1) * STEP - 8

FLIGHT_TOP = TOP + 7
FLIGHT_BOTTOM = TOP + 6 * STEP - 5


def clamp(value, minimum, maximum):
    return max(minimum, min(maximum, value))


def create_random_route():
    """
    Creates a long, smooth, random-looking flight route.

    The jet starts somewhere inside the graph and travels
    toward randomly selected points. Points near edges
    force the jet to turn and continue in another direction.
    """

    x = random.uniform(
        FLIGHT_LEFT + 20,
        FLIGHT_RIGHT - 20
    )

    y = random.uniform(
        FLIGHT_TOP + 10,
        FLIGHT_BOTTOM - 10
    )

    angle = random.uniform(
        0,
        math.pi * 2
    )

    points = [(x, y)]

    for _ in range(14):

        # Random change of direction.
        angle += random.uniform(
            -1.05,
            1.05
        )

        # Keep the movement mostly forward.
        if random.random() < 0.25:
            angle += random.choice([
                math.pi / 3,
                -math.pi / 3
            ])

        distance = random.uniform(
            70,
            125
        )

        nx = x + math.cos(angle) * distance
        ny = y + math.sin(angle) * distance

        # Hit the left/right edge.
        if nx <= FLIGHT_LEFT:
            nx = FLIGHT_LEFT + 4
            angle = math.pi - angle

        elif nx >= FLIGHT_RIGHT:
            nx = FLIGHT_RIGHT - 4
            angle = math.pi - angle

        # Hit the top/bottom edge.
        if ny <= FLIGHT_TOP:
            ny = FLIGHT_TOP + 4
            angle = -angle

        elif ny >= FLIGHT_BOTTOM:
            ny = FLIGHT_BOTTOM - 4
            angle = -angle

        nx = clamp(
            nx,
            FLIGHT_LEFT,
            FLIGHT_RIGHT
        )

        ny = clamp(
            ny,
            FLIGHT_TOP,
            FLIGHT_BOTTOM
        )

        x = nx
        y = ny

        points.append((x, y))

    return points


route = create_random_route()


def create_smooth_path(points):
    """
    Converts random points into a smooth cubic Bézier path.
    """

    if len(points) < 2:
        return ""

    path = (
        f"M {points[0][0]:.2f} "
        f"{points[0][1]:.2f}"
    )

    for index in range(1, len(points)):

        x0, y0 = points[index - 1]
        x1, y1 = points[index]

        dx = x1 - x0
        dy = y1 - y0

        length = max(
            math.sqrt(dx * dx + dy * dy),
            1
        )

        ux = dx / length
        uy = dy / length

        control_distance = length * 0.38

        c1x = x0 + ux * control_distance
        c1y = y0 + uy * control_distance

        c2x = x1 - ux * control_distance
        c2y = y1 - uy * control_distance

        path += (
            f" C "
            f"{c1x:.2f} {c1y:.2f}, "
            f"{c2x:.2f} {c2y:.2f}, "
            f"{x1:.2f} {y1:.2f}"
        )

    return path


flight_path = create_smooth_path(route)


# =========================================================
# SVG
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
# REAL CONTRIBUTION CELLS
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
# LEGEND
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
# INVISIBLE RANDOM FLIGHT PATH
# =========================================================
#
# IMPORTANT:
# This path is intentionally NOT rendered.
#
# It is only used by animateMotion.
#
# Every time the Python script runs, a different route
# is generated.
#
# =========================================================


svg.append(
    f'''
<g>

    <animateMotion
        dur="28s"
        repeatCount="indefinite"
        rotate="auto"
        path="{flight_path}"/>


    <!-- =================================================
         STEALTH JET
         ================================================= -->


    <g
        transform="scale(0.65)"
        filter="url(#jetGlow)">


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
# WRITE FILE
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

print(
    "Generated a new random jet flight route."
)
