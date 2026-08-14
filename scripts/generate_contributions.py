python
import json
import os
import urllib.request

USERNAME = os.environ["GITHUB_USER"]
TOKEN = os.environ["GITHUB_TOKEN"]

GRAPHQL = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          firstDay
          contributionDays {
            date
            weekday
            contributionCount
          }
        }
        months {
          name
          firstDay
          totalWeeks
        }
      }
    }
  }
}
"""

payload = json.dumps({
    "query": GRAPHQL,
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
        "User-Agent": "github-contribution-calendar"
    }
)

with urllib.request.urlopen(request) as response:
    data = json.loads(response.read())

if "errors" in data:
    raise RuntimeError(json.dumps(data["errors"], indent=2))

calendar = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]

weeks = calendar["weeks"]
months = calendar["months"]

CELL = 11
GAP = 3
STEP = CELL + GAP

LEFT = 42
TOP = 40

WIDTH = LEFT + len(weeks) * STEP + 12
HEIGHT = TOP + 7 * STEP + 48

EMPTY = "#161b22"

LEVELS = [
    "#161b22",
    "#1565c0",
    "#00b8d4",
    "#00c853",
    "#00ff88",
]

svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {WIDTH} {HEIGHT}"
width="{WIDTH}"
height="{HEIGHT}">
'''
)

svg.append("""
<style>
text {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}

.label {
  fill: #57606a;
  font-size: 10px;
}

.month {
  fill: #57606a;
  font-size: 11px;
}

.cell {
  rx: 2;
  ry: 2;
}
</style>
""")

# Month labels
for month in months:
    first_day = month["firstDay"]
    week_index = None

    for index, week in enumerate(weeks):
        if week["firstDay"] <= first_day:
            week_index = index
        else:
            break

    if week_index is not None:
        x = LEFT + week_index * STEP

        svg.append(
            f'<text class="month" x="{x}" y="16">{month["name"][:3]}</text>'
        )

# Weekday labels
weekday_labels = {
    1: "Mon",
    3: "Wed",
    5: "Fri",
}

for weekday, label in weekday_labels.items():
    y = TOP + (weekday - 1) * STEP + 9

    svg.append(
        f'<text class="label" x="0" y="{y}">{label}</text>'
    )

# Contribution cells
points = []

for week_index, week in enumerate(weeks):

    for day in week["contributionDays"]:

        weekday = day["weekday"]
        count = day["contributionCount"]

        x = LEFT + week_index * STEP
        y = TOP + (weekday - 1) * STEP

        if count == 0:
            color = LEVELS[0]
        elif count <= 1:
            color = LEVELS[1]
        elif count <= 3:
            color = LEVELS[2]
        elif count <= 6:
            color = LEVELS[3]
        else:
            color = LEVELS[4]

        svg.append(
            f'''<rect
x="{x}"
y="{y}"
width="{CELL}"
height="{CELL}"
rx="2"
ry="2"
fill="{color}">
<title>{day["date"]}: {count} contributions</title>
</rect>'''
        )

        points.append(
            (x + CELL / 2, y + CELL / 2)
        )

# Animated snake
if points:

    path_parts = []

    first_x, first_y = points[0]

    path_parts.append(
        f"M {first_x} {first_y}"
    )

    for x, y in points[1:]:
        path_parts.append(
            f"L {x} {y}"
        )

    path_data = " ".join(path_parts)

    svg.append(
        f'''
<path
id="snakePath"
d="{path_data}"
fill="none"
stroke="#00e5ff"
stroke-width="4"
stroke-linecap="round"
stroke-linejoin="round"
stroke-opacity="0.85"
stroke-dasharray="8 8">
<animate
attributeName="stroke-dashoffset"
from="0"
to="-32"
dur="2s"
repeatCount="indefinite"/>
</path>
'''
    )

    svg.append(
        '''
<circle
r="5"
fill="#00e5ff"
stroke="#006064"
stroke-width="1">
<animateMotion
dur="18s"
repeatCount="indefinite"
rotate="auto">
<mpath href="#snakePath"/>
</animateMotion>
</circle>
'''
    )

# Legend
legend_y = TOP + 7 * STEP + 14

svg.append(
    f'<text class="label" x="{LEFT}" y="{legend_y + 9}">Less</text>'
)

for index, color in enumerate(LEVELS):

    x = LEFT + 30 + index * STEP

    svg.append(
        f'''<rect
x="{x}"
y="{legend_y}"
width="{CELL}"
height="{CELL}"
rx="2"
ry="2"
fill="{color}"/>'''
    )

svg.append(
    f'<text class="label" x="{LEFT + 30 + 6 * STEP}" y="{legend_y + 9}">More</text>'
)

svg.append("</svg>")

os.makedirs("assets", exist_ok=True)

with open(
    "assets/contributions.svg",
    "w",
    encoding="utf-8"
) as file:
    file.write("\n".join(svg))

print(
    f"Generated contribution calendar for {USERNAME}: "
    f"{calendar['totalContributions']} contributions"
)
