# Animated futuristic airplane
if points:

    first_x, first_y = points[0]

    last_x, last_y = points[-1]

    svg.append(
        f'''
<g>
    <!-- Flight trail -->
    <path
        d="M {first_x} {first_y} L {last_x} {last_y}"
        fill="none"
        stroke="#00e5ff"
        stroke-width="2"
        stroke-opacity="0.18"
        stroke-dasharray="4 8">
        <animate
            attributeName="stroke-dashoffset"
            from="0"
            to="-24"
            dur="1.5s"
            repeatCount="indefinite"/>
    </path>

    <!-- Airplane -->
    <g>
        <animateMotion
            dur="16s"
            repeatCount="indefinite"
            rotate="auto">
            <mpath href="#flightPath"/>
        </animateMotion>

        <g transform="translate(-8,-8)">
            <path
                d="M 0 8 L 16 8 L 11 5 L 8 0 L 6 5 L 0 8 Z"
                fill="#00e5ff"
                stroke="#006064"
                stroke-width="0.8"/>

            <path
                d="M 6 8 L 4 14 L 8 9"
                fill="#00b8d4"/>

            <path
                d="M 10 8 L 13 13 L 9 9"
                fill="#00b8d4"/>
        </g>
    </g>
</g>
'''
    )

    # Invisible flight path used by the airplane
    svg.insert(
        -1,
        f'''
<path
    id="flightPath"
    d="M {first_x},{first_y} L {last_x},{last_y}"
    fill="none"
    stroke="none"/>
'''
    )
