import json
import os
import urllib.request

USERNAME = os.environ["GITHUB_USER"]
TOKEN = os.environ["GITHUB_TOKEN"]

QUERY = """
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
    "query": QUERY,
    "variables": {"login": USERNAME}
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
total = calendar["totalContributions"]

CELL = 11
GAP = 3
STEP = CELL + GAP

LEFT = 48
TOP = 52

WIDTH = 760
HEIGHT = 210

svg = []

svg.append(
    f'''<svg xmlns="http://www.w3.org/2000/svg"
viewBox="0 0 {WIDTH} {HEIGHT}"
width="{WIDTH}"
height="{HEIGHT}">

<style>
text {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

.header {{
    fill: #1f2328;
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

.cell {{
    stroke: #ffffff;
    stroke-width: 1;
}}
</style>

<!-- GitHub-style card -->
<rect
    x="1"
    y="1"
    width="{WIDTH - 2}"
    height="{HEIGHT - 2}"
    rx="7"
    fill="#ffffff"
    stroke="#d0d7de"
    stroke-width="1"/>

<!-- Header -->
<text
    class="header"
    x="18"
    y="28">
    {total} contributions in the last year
</text>

<text
    class="settings"
    x="{WIDTH - 118}"
    y="28">
    Contribution settings
</text>

<path
    d="M {WIDTH - 17} 24 l 4 0 l -2 3 z"
    fill="#57606a"/>

'''
)

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

        # Keep labels inside the card
        if x < WIDTH - 25:
            svg.append(
                f'<text class="month" x="{x}" y="47">{month["name"][:3]}</text>'
            )

# Weekday labels
labels = {
    1: "Mon",
    3: "Wed",
    5: "Fri"
}

for weekday, label in labels.items():

    y = TOP + (weekday - 1) * STEP + 8

    svg.append(
        f'<text class="weekday" x="5" y="{y}">{label}</text>'
    )

# Contribution colors
COLORS = [
    "#ebedf0",
    "#9be9a8",
    "#40c463",
    "#30a14e",
    "#216e39"
]

# Contribution cells
for week_index, week in enumerate(weeks):

    for day in week["contributionDays"]:

        weekday = day["weekday"]
        count = day["contributionCount"]

        x = LEFT + week_index * STEP
        y = TOP + (weekday - 1) * STEP

        if count == 0:
            level = 0
        elif count <= 1:
            level = 1
        elif count <= 3:
            level = 2
        elif count <= 6:
            level = 3
        else:
            level = 4

        svg.append(
            f'''<rect
x="{x}"
y="{y}"
width="{CELL}"
height="{CELL}"
rx="2"
ry="2"
class="cell"
fill="{COLORS[level]}">
<title>{day["date"]}: {count} contributions</title>
</rect>
'''
        )

# Footer
footer_y = TOP + 7 * STEP + 24

svg.append(
    f'''
<text
class="footer"
x="48"
y="{footer_y}">
Learn how we count contributions
</text>

<text
class="footer"
x="{WIDTH - 165}"
y="{footer_y}">
Less
</text>
'''
)

# Legend
legend_x = WIDTH - 135

for index, color in enumerate(COLORS):

    x = legend_x + 28 + index * 14

    svg.append(
        f'''<rect
x="{x}"
y="{footer_y - 9}"
width="11"
height="11"
rx="2"
fill="{color}"/>'''
    )

svg.append(
    f'''
<text
class="footer"
x="{legend_x + 105}"
y="{footer_y}">
More
</text>
'''
)

svg.append("</svg>")

os.makedirs("assets", exist_ok=True)

with open(
    "assets/contributions.svg",
    "w",
    encoding="utf-8"
) as file:
    file.write("\n".join(svg))

print(f"Generated {total} contributions for {USERNAME}")
