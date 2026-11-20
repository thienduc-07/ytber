"""
EnvironmentBuilder2D — Procedural Illustrated 2D Vector Environments.

Constructs detailed, multi-layered illustrated environments with geometry,
lighting, depth, architectural elements, atmospheric effects, and dynamic props:
1. Horror / Indoor: Old wooden bedroom with perspective floorboards, peeling wallpaper,
   half-open door with door crack shadow, arched window with cold moonlight beam,
   swaying curtains, grandfather clock with swinging pendulum.
2. Horror / Corridor: Claustrophobic hallway, flickering overhead bulb, peeling paint.
3. Historical / Battlefield: Layered misty mountain basin, earthen trenches, sandbag parapets,
   heavy camouflaged artillery cannon, explosive ridge bursts, drifting smoke plumes.
4. Historical / Command Bunker: Subterranean timber ceiling, swaying tungsten lamp,
   field map table, military radio transceiver with glowing indicator dials.
5. Historical / Victory Roof: Shattered bunker roof, barbed wire silhouette, sunrise,
   Vietnamese victory flag waving in mountain wind.
"""

from typing import Dict, Any, List


class EnvironmentBuilder2D:
    """Builder generating multi-layered SVG scene environments with GSAP animation directives."""

    @classmethod
    def render_environment(
        cls,
        env_type: str,
        env_id: str,
        width: int = 1080,
        height: int = 1920
    ) -> Dict[str, Any]:
        """
        Renders complete illustrated vector environment markup with atmosphere and props.
        """
        if env_type == "old_wooden_bedroom":
            return cls._render_old_wooden_bedroom(env_id, width, height)
        elif env_type == "dark_corridor":
            return cls._render_dark_corridor(env_id, width, height)
        elif env_type == "command_bunker":
            return cls._render_command_bunker(env_id, width, height)
        elif env_type == "victory_roof":
            return cls._render_victory_roof(env_id, width, height)
        else: # mountain_battlefield
            return cls._render_mountain_battlefield(env_id, width, height)

    @classmethod
    def _render_old_wooden_bedroom(cls, env_id: str, w: int, h: int) -> Dict[str, Any]:
        """Detailed eerie bedroom at night with moonlight, half-open door, and swaying curtains."""
        e = env_id
        defs = f"""
        <defs>
          <linearGradient id="{e}_moon_grad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stop-color="#38BDF8" stop-opacity="0.55"/>
            <stop offset="40%" stop-color="#0284C7" stop-opacity="0.25"/>
            <stop offset="100%" stop-color="#0F172A" stop-opacity="0.0"/>
          </linearGradient>
          <linearGradient id="{e}_floor_grad" x1="50%" y1="0%" x2="50%" y2="100%">
            <stop offset="0%" stop-color="#1E1610"/>
            <stop offset="100%" stop-color="#0B0806"/>
          </linearGradient>
          <pattern id="{e}_peeling_paper" width="60" height="120" patternUnits="userSpaceOnUse">
            <line x1="0" y1="0" x2="0" y2="120" stroke="#1E293B" stroke-width="1"/>
            <line x1="30" y1="0" x2="30" y2="120" stroke="#161F30" stroke-width="1" stroke-dasharray="8 6"/>
          </pattern>
        </defs>
        """

        svg = f"""
        <g id="{e}_root" class="env-bedroom">
          {defs}
          <!-- Wall Layer with Distressed Wallpaper -->
          <rect x="0" y="0" width="{w}" height="1100" fill="#0C101A"/>
          <rect x="0" y="0" width="{w}" height="1100" fill="url(#{e}_peeling_paper)"/>
          
          <!-- Baseboard Molding -->
          <rect x="0" y="1080" width="{w}" height="35" fill="#1C140E" stroke="#2E2016" stroke-width="3"/>

          <!-- Perspective Wooden Floorboards -->
          <polygon points="0,1115 {w},1115 {w},{h} 0,{h}" fill="url(#{e}_floor_grad)"/>
          <g stroke="#160E08" stroke-width="3">
            <line x1="120" y1="1115" x2="-200" y2="{h}"/>
            <line x1="300" y1="1115" x2="100" y2="{h}"/>
            <line x1="480" y1="1115" x2="400" y2="{h}"/>
            <line x1="660" y1="1115" x2="700" y2="{h}"/>
            <line x1="840" y1="1115" x2="1000" y2="{h}"/>
            <line x1="980" y1="1115" x2="1300" y2="{h}"/>
          </g>

          <!-- Arched Window with Pale Cold Moonlight (Left Side) -->
          <g id="{e}_window" transform="translate(100, 260)">
            <!-- Outer Window Frame -->
            <rect x="0" y="0" width="280" height="480" rx="140" fill="#050811" stroke="#2E3C54" stroke-width="12"/>
            <!-- Night Sky & Distant Dead Trees Silhouette -->
            <rect x="12" y="12" width="256" height="456" rx="128" fill="#020617"/>
            <path d="M 40 400 L 70 310 L 55 250 L 70 180" stroke="#0F172A" stroke-width="6" fill="none"/>
            <path d="M 70 310 L 110 260" stroke="#0F172A" stroke-width="4" fill="none"/>
            <!-- Window Mullions (Grids) -->
            <line x1="140" y1="12" x2="140" y2="468" stroke="#1E293B" stroke-width="8"/>
            <line x1="12" y1="240" x2="268" y2="240" stroke="#1E293B" stroke-width="8"/>
            <line x1="12" y1="360" x2="268" y2="360" stroke="#1E293B" stroke-width="8"/>

            <!-- Curtains swaying -->
            <path id="{e}_curtain_l" d="M 0 0 C 40 120 10 320 20 480 L -30 480 L -30 0 Z" fill="#1E293B" opacity="0.85"/>
            <path id="{e}_curtain_r" d="M 280 0 C 240 120 270 320 260 480 L 310 480 L 310 0 Z" fill="#1E293B" opacity="0.85"/>
          </g>

          <!-- Volumetric Moonlight Beam Spilling Across Room Floor -->
          <polygon id="{e}_moonlight_beam" points="240,480 380,480 {w},1600 350,1600" fill="url(#{e}_moon_grad)"/>

          <!-- Half-Open Weathered Wooden Door (Right Side) -->
          <g id="{e}_doorway" transform="translate(740, 280)">
            <!-- Dark Door Frame -->
            <rect x="0" y="0" width="280" height="800" fill="#000000" stroke="#1A130D" stroke-width="14"/>
            <!-- Pitch Black Door Void Beyond -->
            <rect x="14" y="14" width="252" height="786" fill="#000000"/>

            <!-- Door Leaf Pivoting Open into Darkness -->
            <g id="{e}_door_leaf" transform="matrix(0.85, 0, -0.22, 1, 0, 0)">
              <rect x="14" y="14" width="252" height="786" fill="#2D1C13" stroke="#452C1E" stroke-width="8"/>
              <!-- Door Panels -->
              <rect x="38" y="50" width="90" height="280" fill="#1E130D" stroke="#382417" stroke-width="4"/>
              <rect x="148" y="50" width="90" height="280" fill="#1E130D" stroke="#382417" stroke-width="4"/>
              <rect x="38" y="380" width="90" height="380" fill="#1E130D" stroke="#382417" stroke-width="4"/>
              <rect x="148" y="380" width="90" height="380" fill="#1E130D" stroke="#382417" stroke-width="4"/>
              <!-- Brass Doorknob casting shadow -->
              <circle cx="34" cy="420" r="10" fill="#FACC15" stroke="#78350F" stroke-width="3"/>
            </g>

            <!-- Door Shadow Cast onto Floor -->
            <polygon points="14,800 266,800 480,1180 80,1180" fill="#000000" opacity="0.75"/>
          </g>

          <!-- Antique Grandfather Clock with Swinging Pendulum -->
          <g id="{e}_clock" transform="translate(560, 420)">
            <rect x="0" y="0" width="120" height="520" fill="#1E130D" stroke="#382417" stroke-width="6"/>
            <!-- Clock Face -->
            <circle cx="60" cy="80" r="44" fill="#FEF3C7" stroke="#78350F" stroke-width="4"/>
            <line x1="60" y1="80" x2="60" y2="52" stroke="#1C1917" stroke-width="3.5"/> <!-- Hour hand -->
            <line x1="60" y1="80" x2="84" y2="80" stroke="#1C1917" stroke-width="2.5"/> <!-- Minute hand -->
            <circle cx="60" cy="80" r="4" fill="#78350F"/>
            <!-- Glass Cabinet with Pendulum -->
            <rect x="20" y="160" width="80" height="320" fill="#0A0604" stroke="#452C1E" stroke-width="4"/>
            <g id="{e}_pendulum" transform="translate(60, 160)">
              <line x1="0" y1="0" x2="0" y2="240" stroke="#FACC15" stroke-width="4"/>
              <circle cx="0" cy="240" r="22" fill="#FACC15" stroke="#78350F" stroke-width="3"/>
            </g>
          </g>
        </g>
        """

        tweens = [
            # Grandfather clock pendulum ticking back and forth
            f'tl.to("#{e}_pendulum", {{ rotation: 12, transformOrigin: "0px 0px", yoyo: true, repeat: 19, duration: 0.5, ease: "sine.inOut" }}, 0.0);',
            # Curtains swaying gently in the night draft
            f'tl.to("#{e}_curtain_l, #{e}_curtain_r", {{ scaleX: 1.15, transformOrigin: "top center", yoyo: true, repeat: 9, duration: 1.2, ease: "power1.inOut" }}, 0.1);',
            # Door slowly groaning and opening slightly more
            f'tl.to("#{e}_door_leaf", {{ skewY: -4, duration: 3.5, ease: "power1.inOut" }}, 0.8);'
        ]

        return {"svg": svg, "tweens": tweens}

    @classmethod
    def _render_dark_corridor(cls, env_id: str, w: int, h: int) -> Dict[str, Any]:
        """Claustrophobic hallway with perspective walls and flickering overhead wire bulb."""
        e = env_id
        svg = f"""
        <g id="{e}_root" class="env-corridor">
          <!-- Ceiling -->
          <polygon points="0,0 {w},0 780,550 300,550" fill="#0F172A"/>
          <!-- Floor with vanishing perspective lines -->
          <polygon points="0,{h} {w},{h} 780,1200 300,1200" fill="#0B0E14"/>
          <g stroke="#1E293B" stroke-width="2">
            <line x1="0" y1="{h}" x2="300" y2="1200"/>
            <line x1="360" y1="{h}" x2="460" y2="1200"/>
            <line x1="720" y1="{h}" x2="620" y2="1200"/>
            <line x1="{w}" y1="{h}" x2="780" y2="1200"/>
          </g>

          <!-- Left Wall -->
          <polygon points="0,0 300,550 300,1200 0,{h}" fill="#161F30"/>
          <!-- Closed Door Left 1 -->
          <polygon points="40,280 220,580 220,1100 40,1400" fill="#0E1422" stroke="#25334D" stroke-width="4"/>

          <!-- Right Wall -->
          <polygon points="{w},0 780,550 780,1200 {w},{h}" fill="#161F30"/>
          <!-- Half-Ajar Door Right with mysterious warm light slit -->
          <polygon points="860,580 1040,280 1040,1400 860,1100" fill="#0E1422" stroke="#25334D" stroke-width="4"/>
          <!-- Light slit through cracked door -->
          <polygon points="858,584 866,584 866,1096 858,1096" fill="#FACC15" filter="drop-shadow(0 0 12px #FACC15)"/>

          <!-- Deep End Wall -->
          <rect x="300" y="550" width="480" height="650" fill="#05070B"/>

          <!-- Bare Wire Hanging Bulb in Midst -->
          <g id="{e}_bulb" transform="translate(540, 520)">
            <line x1="0" y1="-520" x2="0" y2="0" stroke="#000000" stroke-width="4"/>
            <circle cx="0" cy="16" r="16" fill="#FEF08A" filter="drop-shadow(0 0 25px #FEF08A)"/>
          </g>
        </g>
        """

        tweens = [
            f'tl.to("#{e}_bulb circle", {{ opacity: 0.1, yoyo: true, repeat: 5, duration: 0.12, ease: "steps(2)" }}, 0.4);',
            f'tl.to("#{e}_bulb", {{ rotation: 3, transformOrigin: "0px -500px", yoyo: true, repeat: 7, duration: 0.9, ease: "sine.inOut" }}, 0.0);'
        ]
        return {"svg": svg, "tweens": tweens}

    @classmethod
    def _render_mountain_battlefield(cls, env_id: str, w: int, h: int) -> Dict[str, Any]:
        """Atmospheric Dien Bien Phu mountain basin with trenches, artillery, and shell bursts."""
        e = env_id
        defs = f"""
        <defs>
          <linearGradient id="{e}_sky_grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stop-color="#0A0F1D"/>
            <stop offset="50%" stop-color="#1E293B"/>
            <stop offset="100%" stop-color="#475569"/>
          </linearGradient>
          <linearGradient id="{e}_burst_grad" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#FFFFFF"/>
            <stop offset="40%" stop-color="#FACC15"/>
            <stop offset="80%" stop-color="#EF4444"/>
            <stop offset="100%" stop-color="#1E1B4B" stop-opacity="0"/>
          </linearGradient>
        </defs>
        """

        svg = f"""
        <g id="{e}_root" class="env-battlefield">
          {defs}
          <!-- Dramatic Overcast Sky -->
          <rect x="0" y="0" width="{w}" height="1000" fill="url(#{e}_sky_grad)"/>

          <!-- Distant Mountain Tier 1 (Highest, Pale Blue Mist) -->
          <polygon points="-100,750 150,420 480,560 850,380 1200,600 1200,1000 -100,1000" fill="#1E293B" opacity="0.6"/>

          <!-- Artillery Shell Burst on Distant Ridge -->
          <g id="{e}_burst" transform="translate(850, 380)">
            <circle r="60" fill="url(#{e}_burst_grad)"/>
            <circle id="{e}_shockwave" r="20" fill="none" stroke="#FACC15" stroke-width="6"/>
          </g>

          <!-- Midground Mountain Tier 2 (Darker, Forest Ridges) -->
          <polygon points="-100,900 200,620 540,740 920,580 1200,780 1200,1200 -100,1200" fill="#0F172A"/>

          <!-- Valley Floor & Earthen Trenches -->
          <rect x="0" y="980" width="{w}" height="940" fill="#1A1813"/>

          <!-- Sandbag Parapets & Trench Wood Shoring -->
          <g id="{e}_trench_front" transform="translate(0, 1380)">
            <!-- Sandbag Rows -->
            <ellipse cx="140" cy="40" rx="90" ry="32" fill="#785938" stroke="#452C1E" stroke-width="4"/>
            <ellipse cx="280" cy="35" rx="85" ry="30" fill="#8C6842" stroke="#452C1E" stroke-width="4"/>
            <ellipse cx="420" cy="45" rx="90" ry="32" fill="#6E4F30" stroke="#452C1E" stroke-width="4"/>
            <ellipse cx="560" cy="38" rx="85" ry="30" fill="#8C6842" stroke="#452C1E" stroke-width="4"/>
            <ellipse cx="700" cy="42" rx="90" ry="32" fill="#785938" stroke="#452C1E" stroke-width="4"/>
            <ellipse cx="840" cy="36" rx="85" ry="30" fill="#8C6842" stroke="#452C1E" stroke-width="4"/>
            <ellipse cx="980" cy="44" rx="90" ry="32" fill="#6E4F30" stroke="#452C1E" stroke-width="4"/>

            <!-- Barbed Wire Fence Lines -->
            <path d="M 0 0 L {w} 20" stroke="#334155" stroke-width="3" stroke-dasharray="14 10"/>
            <path d="M 0 25 L {w} 45" stroke="#334155" stroke-width="3" stroke-dasharray="14 10"/>
            <line x1="200" y1="-20" x2="200" y2="60" stroke="#452C1E" stroke-width="8"/>
            <line x1="600" y1="-20" x2="600" y2="60" stroke="#452C1E" stroke-width="8"/>
            <line x1="900" y1="-20" x2="900" y2="60" stroke="#452C1E" stroke-width="8"/>
          </g>

          <!-- Heavy 105mm Artillery Cannon Emplacement (Center-Left) -->
          <g id="{e}_cannon" transform="translate(340, 1150)">
            <!-- Steel Carriage Wheel with Wooden Spokes -->
            <circle cx="0" cy="0" r="85" fill="#2E3C2B" stroke="#161F15" stroke-width="12"/>
            <circle cx="0" cy="0" r="30" fill="#1C1917"/>
            <line x1="-80" y1="0" x2="80" y2="0" stroke="#161F15" stroke-width="8"/>
            <line x1="0" y1="-80" x2="0" y2="80" stroke="#161F15" stroke-width="8"/>
            <!-- Massive Long Barrel Aimed High at Enemy Stronghold -->
            <polygon points="-40,-15 280,-140 290,-115 -20,10" fill="#3D503A" stroke="#1E2A1C" stroke-width="6"/>
            <!-- Camouflage Netting Foliage on Barrel -->
            <circle cx="120" cy="-65" r="32" fill="#2E4A28" opacity="0.9"/>
            <circle cx="200" cy="-105" r="28" fill="#1C381E" opacity="0.9"/>
          </g>
        </g>
        """

        tweens = [
            # Distant shell burst flash and shockwave expansion
            f'tl.fromTo("#{e}_burst", {{ scale: 0, opacity: 0 }}, {{ scale: 1.4, opacity: 1, duration: 0.35, ease: "power2.out" }}, 0.3);',
            f'tl.to("#{e}_burst", {{ opacity: 0, scale: 2.2, duration: 1.1, ease: "power1.out" }}, 0.65);',
            f'tl.fromTo("#{e}_shockwave", {{ r: 20, opacity: 1 }}, {{ r: 160, opacity: 0, duration: 0.9, ease: "power1.out" }}, 0.35);',
            # Cannon recoil rumble
            f'tl.to("#{e}_cannon", {{ x: "-=18", duration: 0.1, yoyo: true, repeat: 1, ease: "power4.out" }}, 0.3);'
        ]
        return {"svg": svg, "tweens": tweens}

    @classmethod
    def _render_command_bunker(cls, env_id: str, w: int, h: int) -> Dict[str, Any]:
        """Underground tactical command post with timber shoring, maps, and radio station."""
        e = env_id
        svg = f"""
        <g id="{e}_root" class="env-bunker">
          <!-- Dark Subterranean Soil & Timber Shoring -->
          <rect x="0" y="0" width="{w}" height="{h}" fill="#16100B"/>
          <!-- Heavy Timber Beams Support (Vertical Posts) -->
          <rect x="80" y="0" width="80" height="{h}" fill="#2E1C12" stroke="#160D08" stroke-width="6"/>
          <rect x="{w - 160}" y="0" width="80" height="{h}" fill="#2E1C12" stroke="#160D08" stroke-width="6"/>
          <!-- Ceiling Crossbeam -->
          <rect x="0" y="120" width="{w}" height="100" fill="#3D2619" stroke="#160D08" stroke-width="8"/>

          <!-- Swaying Tungsten Light Bulb (Center) -->
          <g id="{e}_lamp" transform="translate(540, 220)">
            <line x1="0" y1="0" x2="0" y2="240" stroke="#1C1917" stroke-width="5"/>
            <polygon points="-35,240 35,240 20,220 -20,220" fill="#475569"/> <!-- Metal shade -->
            <circle cx="0" cy="255" r="18" fill="#FACC15" filter="drop-shadow(0 0 35px #FACC15)"/>
            <!-- Volumetric Warm Light Cone illuminating table below -->
            <polygon points="-25,260 25,260 700,{h} -700,{h}" fill="#FEF08A" opacity="0.12"/>
          </g>

          <!-- Large Wooden Planning Table -->
          <g id="{e}_table" transform="translate(180, 1080)">
            <rect x="0" y="0" width="720" height="420" fill="#2E1C12" stroke="#452C1E" stroke-width="10" rx="8"/>
            <!-- Detailed Battlefield Contour Map on Table -->
            <rect x="60" y="40" width="600" height="340" fill="#FEF3C7" stroke="#78350F" stroke-width="4"/>
            <!-- Contour Map Terrain lines & red arrows -->
            <ellipse cx="360" cy="210" rx="220" ry="110" fill="none" stroke="#D97706" stroke-width="3" stroke-dasharray="8 6"/>
            <ellipse cx="360" cy="210" rx="140" ry="70" fill="none" stroke="#D97706" stroke-width="3"/>
            <path d="M 120 320 Q 240 230 320 210" fill="none" stroke="#EF4444" stroke-width="8" stroke-linecap="round"/>
            <polygon points="320,210 300,195 305,225" fill="#EF4444"/>
          </g>
        </g>
        """

        tweens = [
            f'tl.to("#{e}_lamp", {{ rotation: 4, transformOrigin: "0px 0px", yoyo: true, repeat: 7, duration: 1.4, ease: "sine.inOut" }}, 0.1);',
            f'tl.to("#{e}_lamp circle", {{ opacity: 0.85, yoyo: true, repeat: 9, duration: 0.18, ease: "steps(2)" }}, 0.3);'
        ]
        return {"svg": svg, "tweens": tweens}

    @classmethod
    def _render_victory_roof(cls, env_id: str, w: int, h: int) -> Dict[str, Any]:
        """Triumphant scene: Vietnamese national flag waving on roof of bunker at sunrise."""
        e = env_id
        svg = f"""
        <g id="{e}_root" class="env-victory">
          <!-- Brilliant Golden Triumphant Sunrise -->
          <rect x="0" y="0" width="{w}" height="1100" fill="#B91C1C"/>
          <circle cx="540" cy="700" r="420" fill="#FACC15" opacity="0.85" filter="blur(25px)"/>

          <!-- Bunker Concrete Parapet & Sandbags -->
          <polygon points="0,1250 {w},1250 {w},{h} 0,{h}" fill="#1F2937" stroke="#111827" stroke-width="8"/>
          <rect x="80" y="1220" width="920" height="40" fill="#374151"/>

          <!-- Flagpole on Bunker Roof -->
          <line x1="540" y1="350" x2="540" y2="1240" stroke="#E2E8F0" stroke-width="14"/>

          <!-- Large Waving Vietnamese Flag (Quyết Chiến Quyết Thắng) -->
          <g id="{e}_flag" transform="translate(540, 350)">
            <path id="{e}_flag_cloth" d="M 0 0 C 120 -20 240 20 380 0 L 380 240 C 240 260 120 220 0 240 Z" fill="#DC2626"/>
            <!-- Gold Star Centered in Flag -->
            <polygon id="{e}_flag_star" points="190,75 200,105 230,105 205,122 215,152 190,135 165,152 175,122 150,105 180,105" fill="#FACC15"/>
          </g>
        </g>
        """

        tweens = [
            f'tl.to("#{e}_flag_cloth", {{ d: "M 0 0 C 120 20 240 -20 380 0 L 380 240 C 240 220 120 260 0 240 Z", yoyo: true, repeat: 11, duration: 0.6, ease: "sine.inOut" }}, 0.1);',
            f'tl.to("#{e}_flag_star", {{ y: 10, yoyo: true, repeat: 11, duration: 0.6, ease: "sine.inOut" }}, 0.1);'
        ]
        return {"svg": svg, "tweens": tweens}
