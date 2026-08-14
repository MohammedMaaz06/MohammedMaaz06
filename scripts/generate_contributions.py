import json
import os
import urllib.request
from datetime import datetime

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
}).encode()

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

# ------------------------------------------------------------

# Layout

# ------------------------------------------------------------

CELL = 12
GAP = 4
STEP = CELL + GAP

LEFT = 42
TOP = 42

WIDTH = LEFT + len(weeks) * STEP + 12
HEIGHT = TOP + 7 * STEP + 55

# ------------------------------------------------------------

# Colors

# ------------------------------------------------------------

EMPTY = "#ebedf0"

LEVELS = [
"#ebedf0",
"#90caf9",
"#29b6f6",
"#00c853",
"#00e676",
]

# ------------------------------------------------------------

# SVG helpers

# ------------------------------------------------------------

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

  .snake {
    fill: #00e5ff;
    stroke: #006064;
    stroke-width: 1;
  }

  .snake-eye {
    fill: #ffffff;
  }
</style>

""")

# ------------------------------------------------------------

# Month labels

# ------------------------------------------------------------

for month in months:
first_day = month["firstDay"]

```
week_index = None

for index, week in enumerate(weeks):
    if week["firstDay"] <= first_day:
        week_index = index
    else:
        break

if week_index is not None:
    x = LEFT + week_index * STEP
    svg.append(
        f'<text class="month" x="{x}" y="18">{month["name"][:3]}</text>'
    )
```

# ------------------------------------------------------------

# Weekday labels

# ------------------------------------------------------------

weekday_labels = {
1: "Mon",
3: "Wed",
5: "Fri",
}

for weekday, label in weekday_labels.items():
y = TOP + (weekday - 1) * STEP + 9

```
svg.append(
    f'<text class="label" x="0" y="{y}">{label}</text>'
)
```

# ------------------------------------------------------------

# Contribution cells

# ------------------------------------------------------------

points = []

for week_index, week in enumerate(weeks):

```
days = week["contributionDays"]

for day in days:

    weekday = day["weekday"]
    count = day["contributionCount"]

    x = LEFT + week_index * STEP
    y = TOP + (weekday - 1) * STEP

    if count == 0:
        color = EMPTY
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
            class="cell"
            x="{x}"
            y="{y}"
            width="{CELL}"
            height="{CELL}"
            fill="{color}">
            <title>{day["date"]}: {count} contributions</title>
        </rect>'''
    )

    points.append((x + CELL / 2, y + CELL / 2))
```

# ------------------------------------------------------------

# Animated snake

# ------------------------------------------------------------

if points:

```
path_data = " ".join(
    f"L{x},{y}" for x, y in points
)

first_x, first_y = points[0]

svg.append(
    f'''
```

<path
 id="snakePath"
 d="M{first_x},{first_y} {path_data}"
 fill="none"
 stroke="#00e5ff"
 stroke-width="5"
 stroke-linecap="round"
 stroke-linejoin="round"
 stroke-opacity="0.85"
 stroke-dasharray="8 8"> <animate
     attributeName="stroke-dashoffset"
     from="0"
     to="-32"
     dur="2s"
     repeatCount="indefinite"/> </path>
'''
)

```
svg.append(
    f'''
```

<circle
 r="5"
 class="snake"> <animateMotion
     dur="18s"
     repeatCount="indefinite"
     rotate="auto"> <mpath href="#snakePath"/> </animateMotion> </circle>
'''
)

# ------------------------------------------------------------

# Legend

# ------------------------------------------------------------

legend_y = TOP + 7 * STEP + 18

svg.append(
f'<text class="label" x="{LEFT}" y="{legend_y + 10}">Less</text>'
)

for i, color in enumerate(LEVELS):

```
x = LEFT + 32 + i * STEP

svg.append(
    f'''<rect
        class="cell"
        x="{x}"
        y="{legend_y}"
        width="{CELL}"
        height="{CELL}"
        fill="{color}"/>'''
)
```

svg.append(
f'<text class="label" x="{LEFT + 32 + 6 * STEP}" y="{legend_y + 10}">More</text>'
)

svg.append("</svg>")

os.makedirs("assets", exist_ok=True)

with open("assets/contributions.svg", "w", encoding="utf-8") as file:
file.write("\n".join(svg))

print(
f"Generated contribution calendar for {USERNAME}: "
f"{calendar['totalContributions']} contributions"
)
