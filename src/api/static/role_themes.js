// 15 Iconic Cartoon & Disney Movie Card Banner Themes with Matching Color Palettes & Full-Color Pictograms
window.ROLE_THEMES = [
    {
        key: "lion_king",
        title: "The Lion King",
        subtitle: "Pride Rock Sunrise",
        color: "#d97706",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Lion Mane & Simba Face -->
            <circle cx="20" cy="20" r="16" fill="#b45309" stroke="#78350f" stroke-width="1.5"/>
            <circle cx="11" cy="11" r="4.5" fill="#f59e0b" stroke="#b45309" stroke-width="1.2"/>
            <circle cx="29" cy="11" r="4.5" fill="#f59e0b" stroke="#b45309" stroke-width="1.2"/>
            <circle cx="20" cy="21" r="11" fill="#fbbf24"/>
            <!-- Rafiki Red Ceremony Mark -->
            <path d="M16 13 Q20 11 24 13" stroke="#dc2626" stroke-width="2.2" stroke-linecap="round" fill="none"/>
            <!-- Eyes & Nose -->
            <circle cx="16" cy="19" r="1.8" fill="#451a03"/>
            <circle cx="24" cy="19" r="1.8" fill="#451a03"/>
            <polygon points="17.5,23 22.5,23 20,26" fill="#be123c"/>
            <path d="M20 26 L20 28 M17 28 Q20 30 23 28" stroke="#451a03" stroke-width="1.4" fill="none" stroke-linecap="round"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="lk-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#fde68a"/>
                    <stop offset="55%" stop-color="#f59e0b"/>
                    <stop offset="100%" stop-color="#b45309"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#lk-sky)"/>
            <circle cx="315" cy="58" r="42" fill="#fef08a" opacity="0.85"/>
            <circle cx="315" cy="58" r="54" fill="#fde047" opacity="0.3"/>
            <path d="M165 125 L168 88 L152 72 M168 92 L185 76" stroke="#451a03" stroke-width="3.5" fill="none"/>
            <ellipse cx="152" cy="70" rx="26" ry="5.5" fill="#451a03"/>
            <ellipse cx="182" cy="74" rx="22" ry="5" fill="#451a03"/>
            <ellipse cx="168" cy="64" rx="30" ry="6" fill="#451a03"/>
            <path d="M250 140 L285 95 L385 68 L372 102 L405 140 Z" fill="#78350f"/>
            <path d="M0 124 Q140 112 280 125 L420 120 L420 140 L0 140 Z" fill="#451a03"/>
            <path d="M362 69 L365 56 Q370 50 375 54 L377 60 L374 68 Z" fill="#451a03"/>
            <circle cx="372" cy="54" r="5.5" fill="#451a03"/>
        </svg>`
    },
    {
        key: "frozen",
        title: "Frozen",
        subtitle: "Arendelle Ice Palace",
        color: "#0284c7",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Olaf & Arendelle Ice Crystal -->
            <circle cx="20" cy="20" r="16" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5"/>
            <!-- twigs -->
            <path d="M20 9 L20 4 M17 5 L20 8 L23 5" stroke="#78350f" stroke-width="1.5" fill="none" stroke-linecap="round"/>
            <!-- Olaf Head -->
            <ellipse cx="20" cy="21" rx="10" ry="11" fill="#ffffff" stroke="#38bdf8" stroke-width="1.5"/>
            <circle cx="16.5" cy="17" r="1.8" fill="#0f172a"/>
            <circle cx="23.5" cy="17" r="1.8" fill="#0f172a"/>
            <!-- Carrot Nose -->
            <polygon points="19,19.5 30,21.5 19,23.5" fill="#f97316" stroke="#c2410c" stroke-width="0.8"/>
            <!-- Big Happy Smile & Buck Tooth -->
            <path d="M14 24.5 Q20 29.5 26 24.5" stroke="#0f172a" stroke-width="1.6" fill="none" stroke-linecap="round"/>
            <rect x="18.5" y="25.5" width="3" height="2.5" fill="#ffffff" stroke="#0f172a" stroke-width="0.7"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="fr-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#bae6fd"/>
                    <stop offset="50%" stop-color="#38bdf8"/>
                    <stop offset="100%" stop-color="#0369a1"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#fr-sky)"/>
            <path d="M40 28 Q160 5 260 35 T410 18" stroke="#a5f3fc" stroke-width="10" fill="none" opacity="0.45"/>
            <polygon points="180,140 245,55 310,140" fill="#075985" opacity="0.55"/>
            <polygon points="295,140 365,42 430,140" fill="#0c4a6e" opacity="0.7"/>
            <polygon points="315,140 330,38 345,140" fill="#e0f2fe" opacity="0.9"/>
            <polygon points="298,140 310,64 322,140" fill="#bae6fd" opacity="0.85"/>
            <polygon points="338,140 350,60 362,140" fill="#bae6fd" opacity="0.85"/>
            <polygon points="325,22 330,10 335,22 330,42" fill="#ffffff"/>
        </svg>`
    },
    {
        key: "aladdin",
        title: "Aladdin",
        subtitle: "Arabian Nights & Carpet",
        color: "#7c3aed",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Golden Genie Magic Lamp -->
            <circle cx="20" cy="20" r="16" fill="#4c1d95"/>
            <!-- Blue Genie Magic Swirl -->
            <path d="M31 16 Q34 9 27 8 Q22 7 24 12" stroke="#38bdf8" stroke-width="2.5" fill="none" stroke-linecap="round"/>
            <circle cx="25" cy="9" r="1.5" fill="#fde047"/>
            <!-- Golden Lamp -->
            <path d="M9 22 C9 17, 14 17, 14 21 C14 24, 10 24, 9 22 Z" fill="none" stroke="#facc15" stroke-width="2.2"/>
            <path d="M12 21 Q20 15 27 21 L34 16 L32 23 Q23 28 13 25 Z" fill="#facc15" stroke="#b45309" stroke-width="1.2"/>
            <ellipse cx="20" cy="17.5" rx="3.8" ry="1.8" fill="#eab308" stroke="#b45309" stroke-width="1"/>
            <circle cx="20" cy="15.5" r="1.5" fill="#fef08a"/>
            <rect x="16" y="26" width="8" height="3" rx="1.5" fill="#eab308" stroke="#b45309" stroke-width="1"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="al-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#ddd6fe"/>
                    <stop offset="50%" stop-color="#8b5cf6"/>
                    <stop offset="100%" stop-color="#4c1d95"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#al-sky)"/>
            <circle cx="355" cy="42" r="26" fill="#fef08a" opacity="0.9"/>
            <circle cx="345" cy="36" r="22" fill="#6d28d9"/>
            <path d="M210 48 Q232 38 255 46 L248 56 Q228 48 205 56 Z" fill="#facc15"/>
            <path d="M214 50 Q232 42 250 48 L245 54 Q228 47 210 54 Z" fill="#dc2626"/>
            <rect x="275" y="95" width="90" height="45" fill="#2e1065"/>
            <path d="M290 95 C280 68, 320 55, 320 42 C320 55, 360 68, 350 95 Z" fill="#3b0764"/>
            <path d="M0 126 Q180 110 420 128 L420 140 L0 140 Z" fill="#2e1065"/>
        </svg>`
    },
    {
        key: "moana",
        title: "Moana",
        subtitle: "Motunui Ocean Voyage",
        color: "#0d9488",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Glowing Green Heart of Te Fiti Stone -->
            <ellipse cx="20" cy="20" rx="14" ry="15.5" fill="#10b981" stroke="#065f46" stroke-width="1.8"/>
            <ellipse cx="20" cy="20" rx="11" ry="12.5" fill="#34d399"/>
            <path d="M20 20 m0 -1 a2 2 0 1 1 -2 2 a4 4 0 1 1 4 -4 a6.5 6.5 0 1 1 -6.5 6.5 a9 9 0 1 1 9 -9" stroke="#ecfdf5" stroke-width="2" fill="none" stroke-linecap="round"/>
            <!-- Pink Plumeria Flower Corner -->
            <circle cx="30" cy="10" r="4.5" fill="#f472b6" stroke="#be185d" stroke-width="1"/>
            <circle cx="30" cy="10" r="1.8" fill="#fef08a"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="mo-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#99f6e4"/>
                    <stop offset="55%" stop-color="#14b8a6"/>
                    <stop offset="100%" stop-color="#115e59"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#mo-sky)"/>
            <circle cx="245" cy="46" r="24" fill="#bbf7d0" opacity="0.65"/>
            <path d="M245 46 m-12 0 a12 12 0 1 0 24 0 a9 9 0 1 0 -18 0 a5 5 0 1 0 10 0" stroke="#047857" stroke-width="2.5" fill="none"/>
            <path d="M320 108 L335 28 Q375 56 355 108 Z" fill="#fef3c7"/>
            <path d="M326 92 Q342 84 354 92" stroke="#dc2626" stroke-width="3" fill="none"/>
            <circle cx="340" cy="68" r="6" fill="none" stroke="#b45309" stroke-width="2.2"/>
            <path d="M298 110 L375 110 L365 118 L308 118 Z" fill="#78350f"/>
            <path d="M0 116 Q70 98 140 116 T280 116 T420 114 L420 140 L0 140 Z" fill="#0f766e"/>
        </svg>`
    },
    {
        key: "toy_story",
        title: "Toy Story",
        subtitle: "Andy's Cloud Room",
        color: "#2563eb",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Iconic Pixar Luxo Ball (Yellow, Blue Stripe, Red Star) -->
            <circle cx="20" cy="20" r="15.5" fill="#facc15" stroke="#b45309" stroke-width="1.5"/>
            <path d="M5 16.5 H35 V23.5 H5 Z" fill="#2563eb"/>
            <polygon points="20,9 22.6,16.2 30.2,16.2 24,20.6 26.4,28 20,23.5 13.6,28 16,20.6 9.8,16.2 17.4,16.2" fill="#ef4444" stroke="#991b1b" stroke-width="0.9"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="ts-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#bfdbfe"/>
                    <stop offset="55%" stop-color="#3b82f6"/>
                    <stop offset="100%" stop-color="#1d4ed8"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#ts-sky)"/>
            <g fill="#ffffff" opacity="0.88">
                <path d="M165 62 H225 A12 12 0 0 0 218 42 A16 16 0 0 0 188 36 A14 14 0 0 0 165 52 Z"/>
                <path d="M265 98 H335 A14 14 0 0 0 326 74 A20 20 0 0 0 292 66 A15 15 0 0 0 265 86 Z"/>
                <path d="M335 48 H395 A11 11 0 0 0 388 30 A15 15 0 0 0 360 25 A12 12 0 0 0 335 38 Z"/>
            </g>
            <g transform="translate(362, 92)">
                <polygon points="0,-22 6,-7 22,-7 9,3 14,19 0,10 -14,19 -9,3 -22,-7 -6,-7" fill="#facc15" stroke="#b45309" stroke-width="1.5"/>
            </g>
        </svg>`
    },
    {
        key: "beauty_beast",
        title: "Beauty & the Beast",
        subtitle: "The Enchanted Rose",
        color: "#e11d48",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Enchanted Rose in Glass Bell Jar -->
            <path d="M10 33 L10 15 A10 10 0 0 1 30 15 L30 33 Z" fill="#e0f2fe" opacity="0.65" stroke="#38bdf8" stroke-width="1.5"/>
            <circle cx="20" cy="4" r="2" fill="#38bdf8"/>
            <rect x="8" y="33" width="24" height="3.5" rx="1.5" fill="#eab308" stroke="#854d0e" stroke-width="1"/>
            <!-- Stem & Leaves -->
            <path d="M20 18 L20 33" stroke="#15803d" stroke-width="2.2"/>
            <path d="M20 25 Q13 22 15 27 Z" fill="#16a34a"/>
            <path d="M20 27 Q27 24 25 29 Z" fill="#16a34a"/>
            <!-- Crimson Rose Bloom -->
            <circle cx="20" cy="15" r="6" fill="#be123c"/>
            <path d="M16 14 Q20 10 24 14 Q21 18 16 14 Z" fill="#f43f5e"/>
            <circle cx="20" cy="14" r="2.2" fill="#fda4af"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="bb-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#fecdd3"/>
                    <stop offset="55%" stop-color="#f43f5e"/>
                    <stop offset="100%" stop-color="#881337"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#bb-sky)"/>
            <circle cx="335" cy="70" r="56" fill="#fda4af" opacity="0.25" stroke="#fef08a" stroke-width="2"/>
            <path d="M308 122 L308 56 A27 27 0 0 1 362 56 L362 122 Z" fill="#ffffff" opacity="0.28" stroke="#ffffff" stroke-width="2"/>
            <rect x="298" y="122" width="74" height="8" rx="4" fill="#facc15"/>
            <path d="M335 66 L333 118" stroke="#15803d" stroke-width="3"/>
            <circle cx="335" cy="58" r="13" fill="#be123c"/>
            <circle cx="332" cy="55" r="8" fill="#fb7185"/>
        </svg>`
    },
    {
        key: "little_mermaid",
        title: "The Little Mermaid",
        subtitle: "Atlantica Coral Kingdom",
        color: "#059669",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Ariel Seashell & Emerald Mermaid Tail -->
            <circle cx="20" cy="20" r="16" fill="#d1fae5" stroke="#059669" stroke-width="1.5"/>
            <!-- Purple Scallop Seashell -->
            <path d="M12 18 C9 10, 17 7, 20 12 C23 7, 31 10, 28 18 L23 22 L17 22 Z" fill="#a855f7" stroke="#6b21a8" stroke-width="1.2"/>
            <line x1="20" y1="12" x2="20" y2="22" stroke="#e9d5ff" stroke-width="1.2"/>
            <line x1="16" y1="11" x2="18" y2="22" stroke="#e9d5ff" stroke-width="1.2"/>
            <line x1="24" y1="11" x2="22" y2="22" stroke="#e9d5ff" stroke-width="1.2"/>
            <!-- Emerald Tail Fin -->
            <path d="M17 22 Q20 29 20 31 Q13 33 11 28 Q15 27 17 22 Z" fill="#10b981" stroke="#047857" stroke-width="1.2"/>
            <path d="M23 22 Q20 29 20 31 Q27 33 29 28 Q25 27 23 22 Z" fill="#10b981" stroke="#047857" stroke-width="1.2"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="lm-sea" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#a7f3d0"/>
                    <stop offset="55%" stop-color="#10b981"/>
                    <stop offset="100%" stop-color="#065f46"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#lm-sea)"/>
            <polygon points="180,0 220,0 260,140 140,140" fill="#ffffff" opacity="0.18"/>
            <path d="M325 130 L325 58 Q335 32 345 58 L345 130 Z" fill="#fde047" opacity="0.8"/>
            <path d="M302 130 L302 76 Q310 56 318 76 L318 130 Z" fill="#facc15" opacity="0.75"/>
            <path d="M352 130 L352 72 Q360 52 368 72 L368 130 Z" fill="#facc15" opacity="0.75"/>
        </svg>`
    },
    {
        key: "tangled",
        title: "Tangled",
        subtitle: "Floating Lanterns",
        color: "#c026d3",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Glowing Corona Sky Lantern -->
            <circle cx="20" cy="20" r="16" fill="#581c87"/>
            <rect x="11" y="8" width="18" height="24" rx="4" fill="#fde047" stroke="#d97706" stroke-width="1.5"/>
            <rect x="13" y="10" width="14" height="20" rx="2" fill="#fef08a"/>
            <!-- Corona Sun Emblem -->
            <circle cx="20" cy="20" r="4.5" fill="#d97706"/>
            <g stroke="#d97706" stroke-width="1.6" stroke-linecap="round">
                <line x1="20" y1="12.5" x2="20" y2="14.5"/><line x1="20" y1="25.5" x2="20" y2="27.5"/>
                <line x1="12.5" y1="20" x2="14.5" y2="20"/><line x1="25.5" y1="20" x2="27.5" y2="20"/>
                <line x1="15" y1="15" x2="16.5" y2="16.5"/><line x1="25" y1="25" x2="23.5" y2="23.5"/>
                <line x1="25" y1="15" x2="23.5" y2="16.5"/><line x1="15" y1="25" x2="16.5" y2="23.5"/>
            </g>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="tg-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#f5d0fe"/>
                    <stop offset="55%" stop-color="#c026d3"/>
                    <stop offset="100%" stop-color="#581c87"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#tg-sky)"/>
            <circle cx="348" cy="64" r="34" fill="#fde047" opacity="0.25"/>
            <g>
                <rect x="335" y="34" width="22" height="28" rx="4" fill="#fef08a"/>
                <circle cx="346" cy="48" r="6" fill="#f59e0b"/>
                <rect x="282" y="22" width="16" height="21" rx="3" fill="#fde047" opacity="0.9"/>
                <rect x="242" y="54" width="18" height="24" rx="3" fill="#fef08a" opacity="0.9"/>
            </g>
            <path d="M0 122 Q210 112 420 122 L420 140 L0 140 Z" fill="#3b0764"/>
        </svg>`
    },
    {
        key: "up",
        title: "Up",
        subtitle: "Paradise Falls Balloons",
        color: "#ea580c",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Balloon Cluster & Carl's House -->
            <line x1="20" y1="25" x2="13" y2="13" stroke="#94a3b8" stroke-width="1"/>
            <line x1="20" y1="25" x2="20" y2="10" stroke="#94a3b8" stroke-width="1"/>
            <line x1="20" y1="25" x2="27" y2="13" stroke="#94a3b8" stroke-width="1"/>
            <circle cx="13" cy="13" r="5.5" fill="#ef4444" stroke="#b91c1c" stroke-width="1"/>
            <circle cx="27" cy="13" r="5.5" fill="#3b82f6" stroke="#1d4ed8" stroke-width="1"/>
            <circle cx="16.5" cy="9" r="5.5" fill="#22c55e" stroke="#15803d" stroke-width="1"/>
            <circle cx="23.5" cy="9" r="5.5" fill="#a855f7" stroke="#7e22ce" stroke-width="1"/>
            <circle cx="20" cy="13" r="6" fill="#facc15" stroke="#ca8a04" stroke-width="1"/>
            <!-- Little Yellow & Pink House -->
            <polygon points="12,27 20,21 28,27" fill="#9a3412" stroke="#431407" stroke-width="1"/>
            <rect x="14" y="27" width="12" height="9" fill="#fef08a" stroke="#9a3412" stroke-width="1.2"/>
            <rect x="18" y="29.5" width="4" height="4" fill="#38bdf8" stroke="#0284c7" stroke-width="0.8"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="up-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#fed7aa"/>
                    <stop offset="55%" stop-color="#fb923c"/>
                    <stop offset="100%" stop-color="#c2410c"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#up-sky)"/>
            <circle cx="315" cy="44" r="13" fill="#ef4444"/>
            <circle cx="355" cy="44" r="13" fill="#3b82f6"/>
            <circle cx="335" cy="30" r="15" fill="#facc15"/>
            <circle cx="322" cy="28" r="12" fill="#a855f7"/>
            <circle cx="348" cy="28" r="12" fill="#22c55e"/>
            <circle cx="335" cy="44" r="14" fill="#f97316"/>
            <polygon points="320,98 335,84 350,98" fill="#7c2d12"/>
            <rect x="323" y="98" width="24" height="18" fill="#fef08a" stroke="#9a3412" stroke-width="1.5"/>
        </svg>`
    },
    {
        key: "finding_nemo",
        title: "Finding Nemo",
        subtitle: "Great Barrier Reef",
        color: "#f97316",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Nemo Clownfish -->
            <circle cx="20" cy="20" r="16" fill="#0284c7"/>
            <polygon points="29,20 36,13 36,27" fill="#f97316" stroke="#7c2d12" stroke-width="1.2"/>
            <ellipse cx="18" cy="20" rx="13" ry="8.5" fill="#f97316" stroke="#7c2d12" stroke-width="1.4"/>
            <!-- White Stripes with Black Edges -->
            <path d="M13 12 Q15 20 13 28" stroke="#ffffff" stroke-width="3.5" fill="none"/>
            <path d="M22 12.5 Q24 20 22 27.5" stroke="#ffffff" stroke-width="3" fill="none"/>
            <!-- Eye & Smile -->
            <circle cx="9.5" cy="18.5" r="2" fill="#ffffff"/>
            <circle cx="9.2" cy="18.5" r="1.1" fill="#0f172a"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="fn-sea" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#ffedd5"/>
                    <stop offset="50%" stop-color="#fb923c"/>
                    <stop offset="100%" stop-color="#ea580c"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#fn-sea)"/>
            <path d="M0 118 Q110 96 220 118 T420 112 L420 140 L0 140 Z" fill="#9a3412" opacity="0.55"/>
            <g transform="translate(325, 65)">
                <ellipse cx="0" cy="0" rx="28" ry="16" fill="#ea580c" stroke="#7c2d12" stroke-width="2"/>
                <polygon points="24,0 40,-12 40,12" fill="#ea580c" stroke="#7c2d12" stroke-width="2"/>
                <path d="M-12 -14 Q-8 0 -12 14" stroke="#ffffff" stroke-width="6" fill="none"/>
                <path d="M6 -15 Q10 0 6 15" stroke="#ffffff" stroke-width="5" fill="none"/>
            </g>
        </svg>`
    },
    {
        key: "mulan",
        title: "Mulan",
        subtitle: "Cherry Blossom Garden",
        color: "#db2777",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Pink Cherry Blossom & Jade Comb -->
            <circle cx="20" cy="20" r="16" fill="#fce7f3" stroke="#db2777" stroke-width="1.5"/>
            <!-- 5 Pink Petals -->
            <circle cx="20" cy="11" r="5.5" fill="#f472b6" stroke="#be185d" stroke-width="1"/>
            <circle cx="28.5" cy="17" r="5.5" fill="#f472b6" stroke="#be185d" stroke-width="1"/>
            <circle cx="25" cy="27" r="5.5" fill="#f472b6" stroke="#be185d" stroke-width="1"/>
            <circle cx="15" cy="27" r="5.5" fill="#f472b6" stroke="#be185d" stroke-width="1"/>
            <circle cx="11.5" cy="17" r="5.5" fill="#f472b6" stroke="#be185d" stroke-width="1"/>
            <circle cx="20" cy="19.5" r="4.2" fill="#fde047" stroke="#ca8a04" stroke-width="1"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="mu-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#fce7f3"/>
                    <stop offset="55%" stop-color="#ec4899"/>
                    <stop offset="100%" stop-color="#9d174d"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#mu-sky)"/>
            <polygon points="210,140 285,58 360,140" fill="#831843" opacity="0.45"/>
            <path d="M420 22 Q335 38 255 24 M340 31 Q310 52 285 48" stroke="#500724" stroke-width="3.5" fill="none"/>
            <g fill="#fbcfe8">
                <circle cx="255" cy="24" r="7"/><circle cx="285" cy="48" r="6.5"/>
                <circle cx="318" cy="34" r="8"/><circle cx="362" cy="28" r="7.5"/>
            </g>
        </svg>`
    },
    {
        key: "wall_e",
        title: "WALL-E",
        subtitle: "Starlight & Plant Sprout",
        color: "#65a30d",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color WALL-E Binocular Eyes & Green Plant Leaf -->
            <rect x="11" y="25" width="18" height="10" rx="2" fill="#f59e0b" stroke="#78350f" stroke-width="1.3"/>
            <rect x="18" y="19" width="4" height="6" fill="#94a3b8" stroke="#475569" stroke-width="1"/>
            <!-- Left & Right Binocular Eyes -->
            <rect x="5" y="11" width="14" height="10" rx="4" fill="#cbd5e1" stroke="#475569" stroke-width="1.4"/>
            <rect x="21" y="11" width="14" height="10" rx="4" fill="#cbd5e1" stroke="#475569" stroke-width="1.4"/>
            <circle cx="12" cy="16" r="3.2" fill="#0f172a"/>
            <circle cx="11" cy="15" r="1" fill="#ffffff"/>
            <circle cx="28" cy="16" r="3.2" fill="#0f172a"/>
            <circle cx="27" cy="15" r="1" fill="#ffffff"/>
            <!-- Green Sprout Leaf on Top -->
            <path d="M20 11 L20 5" stroke="#15803d" stroke-width="1.8"/>
            <path d="M20 7 Q26 3 25 8 Q22 9 20 7 Z" fill="#22c55e" stroke="#15803d" stroke-width="0.8"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="we-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#ecfccb"/>
                    <stop offset="55%" stop-color="#84cc16"/>
                    <stop offset="100%" stop-color="#3f6212"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#we-sky)"/>
            <circle cx="335" cy="72" r="44" fill="#fef08a" opacity="0.45"/>
            <path d="M322 95 L344 95 L346 118 L314 118 Q310 110 322 106 Z" fill="#78350f"/>
            <path d="M333 95 L333 56" stroke="#15803d" stroke-width="4" fill="none"/>
            <path d="M333 70 Q308 52 315 42 Q330 46 333 68 Z" fill="#22c55e"/>
            <path d="M333 62 Q358 44 352 34 Q336 38 333 60 Z" fill="#16a34a"/>
        </svg>`
    },
    {
        key: "coco",
        title: "Coco",
        subtitle: "Marigold Bridge Fiesta",
        color: "#ca8a04",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Coco White & Gold Acoustic Guitar -->
            <circle cx="20" cy="20" r="16" fill="#7c2d12"/>
            <g transform="translate(20, 21) rotate(-35)">
                <rect x="-2" y="-16" width="4" height="11" fill="#fde047" stroke="#713f12" stroke-width="1"/>
                <circle cx="0" cy="-3" r="6" fill="#ffffff" stroke="#ca8a04" stroke-width="1.4"/>
                <circle cx="0" cy="5" r="8" fill="#ffffff" stroke="#ca8a04" stroke-width="1.4"/>
                <circle cx="0" cy="1" r="2.8" fill="#0f172a" stroke="#f97316" stroke-width="1.2"/>
                <rect x="-3.5" y="7" width="7" height="2" fill="#ca8a04"/>
            </g>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="co-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#fef08a"/>
                    <stop offset="55%" stop-color="#eab308"/>
                    <stop offset="100%" stop-color="#854d0e"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#co-sky)"/>
            <path d="M180 140 Q290 48 410 140" stroke="#f97316" stroke-width="22" fill="none" opacity="0.8"/>
            <path d="M180 140 Q290 48 410 140" stroke="#fde047" stroke-width="10" fill="none" opacity="0.9"/>
            <g transform="translate(340, 58) rotate(-25)">
                <circle cx="-8" cy="0" r="13" fill="#ffffff" stroke="#713f12" stroke-width="2"/>
                <circle cx="6" cy="0" r="10" fill="#ffffff" stroke="#713f12" stroke-width="2"/>
            </g>
        </svg>`
    },
    {
        key: "monsters_inc",
        title: "Monsters, Inc.",
        subtitle: "Monstropolis Laugh Floor",
        color: "#0891b2",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Mike Wazowski Cyclops Monster -->
            <polygon points="10,11 13,5 16,10" fill="#cbd5e1" stroke="#475569" stroke-width="1"/>
            <polygon points="30,11 27,5 24,10" fill="#cbd5e1" stroke="#475569" stroke-width="1"/>
            <circle cx="20" cy="21" r="14" fill="#84cc16" stroke="#3f6212" stroke-width="1.5"/>
            <circle cx="20" cy="18" r="7.5" fill="#ffffff" stroke="#3f6212" stroke-width="1.2"/>
            <circle cx="20" cy="18" r="4.5" fill="#0891b2"/>
            <circle cx="20" cy="18" r="2.2" fill="#0f172a"/>
            <circle cx="18.5" cy="16.5" r="1" fill="#ffffff"/>
            <path d="M14 28 Q20 32 26 28" stroke="#3f6212" stroke-width="1.8" fill="none" stroke-linecap="round"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="mi-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#cffafe"/>
                    <stop offset="55%" stop-color="#06b6d4"/>
                    <stop offset="100%" stop-color="#155e75"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#mi-sky)"/>
            <circle cx="215" cy="38" r="12" fill="#a855f7" opacity="0.45"/>
            <rect x="330" y="28" width="46" height="86" rx="4" fill="#fdf2f8" stroke="#be185d" stroke-width="2.5"/>
            <circle cx="285" cy="68" r="22" fill="#84cc16" stroke="#3f6212" stroke-width="2"/>
            <circle cx="285" cy="66" r="11" fill="#ffffff"/>
            <circle cx="285" cy="66" r="6" fill="#0d9488"/>
        </svg>`
    },
    {
        key: "peter_pan",
        title: "Peter Pan",
        subtitle: "Neverland Second Star",
        color: "#16a34a",
        iconSvg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">
            <!-- Full-color Peter Pan Green Hat with Red Feather & Gold Star -->
            <circle cx="20" cy="20" r="16" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
            <!-- Red Feather -->
            <path d="M25 20 Q32 8 34 11 Q32 19 26 22 Z" fill="#ef4444" stroke="#991b1b" stroke-width="1.1"/>
            <!-- Green Cap -->
            <path d="M8 26 L22 11 L30 24 Z" fill="#16a34a" stroke="#14532d" stroke-width="1.4"/>
            <path d="M6 26 L33 24 L30 29 L9 29 Z" fill="#22c55e" stroke="#14532d" stroke-width="1.3"/>
            <!-- Pixie Gold Star -->
            <polygon points="12,11 13.2,14 16.5,14 13.8,16 14.8,19 12,17 9.2,19 10.2,16 7.5,14 10.8,14" fill="#eab308"/>
        </svg>`,
        svg: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 140" preserveAspectRatio="xMidYMid slice">
            <defs>
                <linearGradient id="pp-sky" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0%" stop-color="#dcfce7"/>
                    <stop offset="55%" stop-color="#22c55e"/>
                    <stop offset="100%" stop-color="#14532d"/>
                </linearGradient>
            </defs>
            <rect width="420" height="140" fill="url(#pp-sky)"/>
            <g transform="translate(355, 36)">
                <polygon points="0,-18 4,-4 18,-4 6,4 10,18 0,9 -10,18 -6,4 -18,-4 -4,-4" fill="#fef08a"/>
            </g>
            <path d="M180 95 Q255 45 355 36" stroke="#fef08a" stroke-width="3" stroke-dasharray="4 5" fill="none"/>
            <polygon points="275,140 288,58 301,140" fill="#052e16"/>
        </svg>`
    }
];

window.getRoleTheme = (themeKey) => {
    return window.ROLE_THEMES.find(t => t.key === themeKey) || window.ROLE_THEMES[1];
};

window.getRoleThemeDataUri = (themeKey) => {
    const theme = window.getRoleTheme(themeKey);
    return `data:image/svg+xml;utf8,${encodeURIComponent(theme.svg)}`;
};

window.hexToRgba = (hex, alpha = 1) => {
    const clean = (hex || "#0284c7").replace("#", "");
    const bigint = parseInt(clean.length === 3 ? clean.split("").map(c => c + c).join("") : clean, 16);
    if (isNaN(bigint)) return `rgba(2, 132, 199, ${alpha})`;
    const r = (bigint >> 16) & 255;
    const g = (bigint >> 8) & 255;
    const b = bigint & 255;
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};
