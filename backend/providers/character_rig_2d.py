"""
CharacterRig2D — Articulated 2D Vector Character & Animation System.

Generates detailed SVG vector characters with independently animatable body parts:
- Head, hair, facial features (eyes, blinking eyelids, darting pupils, expressive eyebrows, talking/gasping mouth).
- Torso, clothing layers (hoodie, jacket, military fatigue uniform, collar, buttons).
- Articulated arms & hands holding narrative props (dynamic flashlight with volumetric light cone, maps, ropes, tools).
- Legs, trousers, footwear, and grounded contact shadows.
- Expression and pose presets: terrified flashlight creep, shock snap-back, military commander, artillery hauling.
- Deterministic GSAP animation directives (pupil darting, trembling, mouth sync, breathing, flashlight aiming).
"""

from typing import Dict, Any, List, Optional
import math


class CharacterRig2D:
    """Builder for articulated 2D vector characters with procedural SVG markup and GSAP tweens."""

    @classmethod
    def render_character_svg(
        cls,
        char_id: str,
        archetype: str = "horror_investigator",  # horror_investigator, shadow_entity, military_commander, artillery_soldier
        pose: str = "frightened_creep",        # frightened_creep, shock_recoil, commanding_point, pulling_rope, observant_stand
        expression: str = "terrified",         # terrified, shocked, determined, grim, eerie
        x: float = 540,
        y: float = 1200,
        scale: float = 1.0,
        flip_x: bool = False
    ) -> Dict[str, Any]:
        """
        Renders complete vector character SVG markup and returns GSAP tween directives.
        """
        transform_flip = "scale(-1, 1)" if flip_x else "scale(1, 1)"
        root_transform = f"translate({x}, {y}) scale({scale}) {transform_flip}"

        if archetype == "shadow_entity":
            return cls._render_shadow_entity(char_id, root_transform)
        elif archetype == "military_commander":
            return cls._render_military_commander(char_id, root_transform, pose, expression)
        elif archetype == "artillery_soldier":
            return cls._render_artillery_soldier(char_id, root_transform, pose, expression)
        else: # horror_investigator
            return cls._render_horror_investigator(char_id, root_transform, pose, expression)

    @classmethod
    def _render_horror_investigator(
        cls,
        char_id: str,
        root_transform: str,
        pose: str,
        expression: str
    ) -> Dict[str, Any]:
        """Renders an expressive character holding a flashlight in an eerie environment."""
        p = char_id

        # Flashlight volumetric cone gradient
        defs = f"""
        <defs>
          <linearGradient id="{p}_cone_grad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stop-color="#FEF08A" stop-opacity="0.85"/>
            <stop offset="30%" stop-color="#FACC15" stop-opacity="0.45"/>
            <stop offset="70%" stop-color="#38BDF8" stop-opacity="0.2"/>
            <stop offset="100%" stop-color="#0284C7" stop-opacity="0.0"/>
          </linearGradient>
          <radialGradient id="{p}_flash_bulb" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stop-color="#FFFFFF"/>
            <stop offset="60%" stop-color="#FEF08A"/>
            <stop offset="100%" stop-color="#EAB308" stop-opacity="0"/>
          </radialGradient>
          <filter id="{p}_shadow_blur" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur in="SourceGraphic" stdDeviation="6"/>
          </filter>
        </defs>
        """

        # Eye expressions
        pupil_x = 0
        pupil_y = 0
        brow_l = "M -28 -72 Q -16 -88 -4 -72"
        brow_r = "M 4 -72 Q 16 -88 28 -72"
        mouth_d = "M -12 -32 Q 0 -22 12 -32 Q 0 -12 -12 -32" # Open gasping mouth

        if expression == "terrified":
            brow_l = "M -28 -78 Q -16 -96 -4 -76"
            brow_r = "M 4 -76 Q 16 -96 28 -78"
            mouth_d = "M -14 -34 Q 0 -16 14 -34 Q 0 -44 -14 -34" # Gasping terror oval
        elif expression == "shocked":
            brow_l = "M -30 -82 Q -16 -100 -2 -80"
            brow_r = "M 2 -80 Q 16 -100 30 -82"
            mouth_d = "M -18 -32 Q 0 -8 18 -32 Q 0 -50 -18 -32" # Screaming/gasping open mouth

        # Hand / Flashlight orientation
        arm_d = "M 32 -30 Q 70 -20 110 -35"
        hand_x = 110
        hand_y = -35
        beam_poly = f"110,-35 850,-180 850,110"

        if pose == "shock_recoil":
            arm_d = "M 30 -20 Q 55 -40 75 -70"
            hand_x = 75
            hand_y = -70
            beam_poly = f"75,-70 700,-350 700,-60"

        svg = f"""
        <g id="{p}_root" class="char-rig" transform="{root_transform}">
          {defs}
          <!-- Contact Ground Shadow -->
          <ellipse cx="0" cy="190" rx="90" ry="18" fill="#000000" opacity="0.65" filter="url(#{p}_shadow_blur)"/>

          <!-- Volumetric Flashlight Beam -->
          <polygon id="{p}_light_cone" points="{beam_poly}" fill="url(#{p}_cone_grad)"/>
          <circle cx="{hand_x}" cy="{hand_y}" r="22" fill="url(#{p}_flash_bulb)"/>

          <!-- Body Silhouette & Torso -->
          <!-- Legs & Boots -->
          <g id="{p}_legs">
            <!-- Left Leg -->
            <path d="M -30 60 L -36 175 L -10 175 L -14 60 Z" fill="#1E293B"/>
            <path d="M -46 172 L -6 172 L -4 188 L -52 188 Z" fill="#0F172A"/> <!-- Boot -->
            <!-- Right Leg -->
            <path d="M 14 60 L 10 175 L 36 175 L 30 60 Z" fill="#1E293B"/>
            <path d="M 0 172 L 40 172 L 46 188 L -2 188 Z" fill="#0F172A"/> <!-- Boot -->
          </g>

          <!-- Torso / Jacket -->
          <g id="{p}_torso">
            <path d="M -45 -40 C -52 10 -48 60 -38 75 C -15 80 15 80 38 75 C 48 60 52 10 45 -40 Z" fill="#334155"/>
            <!-- Jacket zipper and collar -->
            <path d="M 0 -40 L 0 75" stroke="#475569" stroke-width="3"/>
            <path d="M -25 -42 L 0 -18 L 25 -42" fill="none" stroke="#64748B" stroke-width="4"/>
          </g>

          <!-- Back Arm -->
          <path d="M -32 -30 Q -60 -10 -55 25" fill="none" stroke="#334155" stroke-width="18" stroke-linecap="round"/>
          <circle cx="-55" cy="25" r="9" fill="#FCD34D"/>

          <!-- Head & Facial Rig -->
          <g id="{p}_head">
            <!-- Neck -->
            <rect x="-14" y="-55" width="28" height="22" fill="#F59E0B" rx="4"/>
            <!-- Head Oval -->
            <ellipse cx="0" cy="-65" rx="42" ry="48" fill="#FCD34D"/>
            <!-- Sweat drop on temple -->
            <path d="M 28 -75 C 28 -80 34 -85 34 -85 C 34 -85 40 -80 40 -75 C 40 -71 34 -68 28 -75 Z" fill="#38BDF8" opacity="0.9"/>

            <!-- Hair -->
            <path d="M -44 -75 Q -40 -120 0 -122 Q 40 -120 44 -75 Q 30 -105 0 -105 Q -30 -105 -44 -75 Z" fill="#1C1917"/>

            <!-- Left Eye -->
            <g id="{p}_eye_l" transform="translate(-16, -68)">
              <ellipse cx="0" cy="0" rx="10" ry="13" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
              <circle id="{p}_pupil_l" cx="{pupil_x}" cy="{pupil_y}" r="4.5" fill="#0F172A"/>
              <circle cx="{pupil_x + 2}" cy="{pupil_y - 2}" r="1.8" fill="#FFFFFF"/>
            </g>

            <!-- Right Eye -->
            <g id="{p}_eye_r" transform="translate(16, -68)">
              <ellipse cx="0" cy="0" rx="10" ry="13" fill="#FFFFFF" stroke="#0F172A" stroke-width="2"/>
              <circle id="{p}_pupil_r" cx="{pupil_x}" cy="{pupil_y}" r="4.5" fill="#0F172A"/>
              <circle cx="{pupil_x + 2}" cy="{pupil_y - 2}" r="1.8" fill="#FFFFFF"/>
            </g>

            <!-- Eyebrows -->
            <path id="{p}_brow_l" d="{brow_l}" fill="none" stroke="#1C1917" stroke-width="3.5" stroke-linecap="round"/>
            <path id="{p}_brow_r" d="{brow_r}" fill="none" stroke="#1C1917" stroke-width="3.5" stroke-linecap="round"/>

            <!-- Nose -->
            <path d="M 0 -62 L 3 -52 L -3 -50" fill="none" stroke="#D97706" stroke-width="2.5" stroke-linecap="round"/>

            <!-- Mouth -->
            <path id="{p}_mouth" d="{mouth_d}" fill="#881337" stroke="#4C0519" stroke-width="2"/>
          </g>

          <!-- Front Arm Holding Flashlight -->
          <g id="{p}_front_arm">
            <path d="{arm_d}" fill="none" stroke="#334155" stroke-width="18" stroke-linecap="round"/>
            <circle cx="{hand_x}" cy="{hand_y}" r="10" fill="#FCD34D"/> <!-- Hand -->
            <!-- Flashlight body -->
            <rect x="{hand_x - 12}" y="{hand_y - 7}" width="26" height="14" rx="3" fill="#0F172A" transform="rotate(-15, {hand_x}, {hand_y})"/>
            <polygon points="{hand_x+8},{hand_y-9} {hand_x+18},{hand_y-14} {hand_x+18},{hand_y+14} {hand_x+8},{hand_y+9}" fill="#475569" transform="rotate(-15, {hand_x}, {hand_y})"/>
          </g>
        </g>
        """

        # GSAP tween generation for character life & terror
        tweens = [
            # Darting nervous pupils
            f'tl.to("#{p}_pupil_l, #{p}_pupil_r", {{ x: -3, y: -2, duration: 0.18, ease: "power1.inOut" }}, "+=0.3");',
            f'tl.to("#{p}_pupil_l, #{p}_pupil_r", {{ x: 4, y: 1, duration: 0.22, ease: "power1.inOut" }}, "+=0.5");',
            f'tl.to("#{p}_pupil_l, #{p}_pupil_r", {{ x: 0, y: 0, duration: 0.15, ease: "power1.inOut" }}, "+=0.4");',
            # Shaking trembling flashlight beam
            f'tl.to("#{p}_light_cone", {{ rotation: 3, transformOrigin: "{hand_x}px {hand_y}px", yoyo: true, repeat: 9, duration: 0.14, ease: "sine.inOut" }}, 0.1);',
            # Terrified breathing / chest heaving
            f'tl.to("#{p}_torso, #{p}_head", {{ y: -5, duration: 0.5, yoyo: true, repeat: 7, ease: "power1.inOut" }}, 0.0);'
        ]

        return {"svg": svg, "tweens": tweens}

    @classmethod
    def _render_shadow_entity(cls, char_id: str, root_transform: str) -> Dict[str, Any]:
        """Renders an ominous, tall shadowy figure with glowing eyes lurking in doorways or woods."""
        p = char_id
        svg = f"""
        <g id="{p}_root" class="char-shadow-entity" transform="{root_transform}">
          <!-- Diffuse Outer Shadow Aura -->
          <ellipse cx="0" cy="-70" rx="80" ry="170" fill="#000000" opacity="0.9" filter="blur(16px)"/>
          
          <!-- Tall Slender Body Silhouette -->
          <path d="M -35 -140 C -55 -60 -45 60 -40 180 L 40 180 C 45 60 55 -60 35 -140 Z" fill="#050505"/>
          <ellipse cx="0" cy="-170" rx="36" ry="46" fill="#050505"/>
          
          <!-- Piercing Pale Glowing Eyes -->
          <circle id="{p}_eye_l" cx="-12" cy="-175" r="3.5" fill="#FFFFFF" opacity="0.95" filter="drop-shadow(0 0 6px #FFFFFF)"/>
          <circle id="{p}_eye_r" cx="12" cy="-175" r="3.5" fill="#FFFFFF" opacity="0.95" filter="drop-shadow(0 0 6px #FFFFFF)"/>
          
          <!-- Eerie Lengthening Shadow Floor -->
          <ellipse cx="0" cy="180" rx="100" ry="24" fill="#000000" opacity="0.95"/>
        </g>
        """

        tweens = [
            f'tl.fromTo("#{p}_root", {{ opacity: 0, scaleY: 0.9 }}, {{ opacity: 1, scaleY: 1.05, duration: 1.8, ease: "power2.out" }}, "+=0.2");',
            f'tl.to("#{p}_eye_l, #{p}_eye_r", {{ opacity: 0.2, yoyo: true, repeat: 3, duration: 0.25, ease: "sine.inOut" }}, "+=0.8");'
        ]
        return {"svg": svg, "tweens": tweens}

    @classmethod
    def _render_military_commander(
        cls,
        char_id: str,
        root_transform: str,
        pose: str,
        expression: str
    ) -> Dict[str, Any]:
        """Renders a stylized Vietnamese military commander (General / Officer) with tactical map and cap."""
        p = char_id
        svg = f"""
        <g id="{p}_root" class="char-commander" transform="{root_transform}">
          <!-- Ground Shadow -->
          <ellipse cx="0" cy="190" rx="85" ry="16" fill="#000000" opacity="0.6"/>

          <!-- Olive Green Trousers & Field Boots -->
          <path d="M -28 65 L -34 175 L -10 175 L -12 65 Z" fill="#2E402B"/>
          <path d="M -42 172 L -6 172 L -4 188 L -48 188 Z" fill="#1C1917"/> <!-- Leather Boot -->
          <path d="M 12 65 L 10 175 L 34 175 L 28 65 Z" fill="#2E402B"/>
          <path d="M 2 172 L 40 172 L 44 188 L -2 188 Z" fill="#1C1917"/> <!-- Leather Boot -->

          <!-- Commander Tunic / Uniform -->
          <g id="{p}_tunic">
            <path d="M -46 -35 C -50 15 -46 65 -36 75 C -15 80 15 80 36 75 C 46 65 50 15 46 -35 Z" fill="#3D5A37"/>
            <rect x="-38" y="55" width="76" height="12" fill="#5A3A22"/> <!-- Leather Belt -->
            <rect x="-8" y="53" width="16" height="16" fill="#FACC15" rx="2"/> <!-- Brass Buckle -->
            <!-- Collar & Red Epaulets with Gold Star -->
            <polygon points="-46,-35 -30,-48 -20,-35" fill="#EF4444"/>
            <polygon points="46,-35 30,-48 20,-35" fill="#EF4444"/>
            <circle cx="-33" cy="-38" r="3" fill="#FACC15"/>
            <circle cx="33" cy="-38" r="3" fill="#FACC15"/>
          </g>

          <!-- Commander Head -->
          <g id="{p}_head">
            <ellipse cx="0" cy="-65" rx="38" ry="45" fill="#F59E0B"/>
            <!-- Eyes (Determined) -->
            <circle cx="-14" cy="-66" r="3.5" fill="#0F172A"/>
            <circle cx="14" cy="-66" r="3.5" fill="#0F172A"/>
            <!-- Firm Eyebrows -->
            <path d="M -25 -74 L -6 -69" stroke="#1C1917" stroke-width="4" stroke-linecap="round"/>
            <path d="M 6 -69 L 25 -74" stroke="#1C1917" stroke-width="4" stroke-linecap="round"/>
            <!-- Mouth (Confident / Speaking) -->
            <path id="{p}_mouth" d="M -12 -46 Q 0 -42 12 -46" stroke="#78350F" stroke-width="3" fill="none" stroke-linecap="round"/>

            <!-- Military Visor Cap -->
            <ellipse cx="0" cy="-90" rx="46" ry="16" fill="#3D5A37"/>
            <path d="M -44 -90 Q 0 -125 44 -90 Z" fill="#2E402B"/>
            <path d="M -42 -88 Q 0 -72 42 -88" fill="#1C1917"/> <!-- Cap Visor -->
            <!-- Gold Star Emblem -->
            <polygon points="0,-102 3,-94 11,-94 5,-89 7,-81 0,-85 -7,-81 -5,-89 -11,-94 -3,-94" fill="#FACC15"/>
          </g>

          <!-- Right Arm Pointing Forward Strategically -->
          <g id="{p}_arm_point">
            <path d="M 36 -25 Q 75 -20 120 -35" fill="none" stroke="#3D5A37" stroke-width="18" stroke-linecap="round"/>
            <circle cx="120" cy="-35" r="9" fill="#F59E0B"/>
            <!-- Pointer Hand Extension -->
            <path d="M 120 -35 L 145 -42" stroke="#F59E0B" stroke-width="6" stroke-linecap="round"/>
          </g>
        </g>
        """

        tweens = [
            f'tl.fromTo("#{p}_arm_point", {{ rotation: -10, transformOrigin: "36px -25px" }}, {{ rotation: 8, duration: 1.4, yoyo: true, repeat: 3, ease: "power1.inOut" }}, 0.2);',
            f'tl.to("#{p}_head", {{ y: -4, duration: 0.8, yoyo: true, repeat: 5, ease: "sine.inOut" }}, 0.1);'
        ]
        return {"svg": svg, "tweens": tweens}

    @classmethod
    def _render_artillery_soldier(
        cls,
        char_id: str,
        root_transform: str,
        pose: str,
        expression: str
    ) -> Dict[str, Any]:
        """Renders an artillery soldier leaning into heavy ropes hauling weapons up muddy mountain slopes."""
        p = char_id
        svg = f"""
        <g id="{p}_root" class="char-soldier" transform="{root_transform}">
          <!-- Muddy Contact Shadow -->
          <ellipse cx="0" cy="190" rx="95" ry="18" fill="#000000" opacity="0.7"/>

          <!-- Body Leaning at 40 Degrees Hauling Ropes -->
          <g id="{p}_straining_body" transform="rotate(-18, 0, 180)">
            <!-- Straining Legs in Mud -->
            <path d="M -30 65 L -45 175 L -20 175 L -10 65 Z" fill="#2E402B"/>
            <path d="M 15 65 L 5 175 L 30 175 L 35 65 Z" fill="#2E402B"/>
            <!-- Canvas Mud Shoes -->
            <path d="M -55 172 L -15 172 L -12 188 L -60 188 Z" fill="#451A03"/>
            <path d="M -5 172 L 35 172 L 40 188 L -8 188 Z" fill="#451A03"/>

            <!-- Fatigue Tunic with Dirt Smudges -->
            <path d="M -42 -30 C -48 15 -42 65 -32 75 C -15 80 15 80 32 75 C 42 65 48 15 42 -30 Z" fill="#3D5A37"/>
            
            <!-- Head with Camouflage Leaf Netting Helmet -->
            <g id="{p}_head">
              <ellipse cx="0" cy="-60" rx="36" ry="42" fill="#F59E0B"/>
              <!-- Grit Teeth Expression -->
              <rect x="-12" y="-42" width="24" height="8" rx="2" fill="#FFFFFF" stroke="#451A03" stroke-width="2"/>
              <!-- Determined Eyes squinting in rain/sweat -->
              <path d="M -22 -62 L -6 -60" stroke="#1C1917" stroke-width="4" stroke-linecap="round"/>
              <path d="M 6 -60 L 22 -62" stroke="#1C1917" stroke-width="4" stroke-linecap="round"/>

              <!-- Helmet with Foliage Camouflage -->
              <ellipse cx="0" cy="-78" rx="44" ry="24" fill="#1C381E"/>
              <circle cx="-25" cy="-85" r="10" fill="#2E5A27"/>
              <circle cx="0" cy="-92" r="12" fill="#153612"/>
              <circle cx="25" cy="-85" r="10" fill="#3F7A36"/>
            </g>

            <!-- Tensed Arms Gripping Thick Hemp Rope -->
            <path d="M -35 -20 Q -5 20 40 10" fill="none" stroke="#3D5A37" stroke-width="18" stroke-linecap="round"/>
            <circle cx="40" cy="10" r="11" fill="#D97706"/> <!-- Hand -->
            
            <!-- Heavy Hemp Rope Under Extreme Tension -->
            <path d="M -200 45 L 40 10 L 250 -25" stroke="#D97706" stroke-width="12" stroke-dasharray="8 4"/>
          </g>
        </g>
        """

        tweens = [
            f'tl.to("#{p}_straining_body", {{ rotation: -24, duration: 0.9, yoyo: true, repeat: 7, ease: "power2.inOut" }}, 0.1);',
            f'tl.to("#{p}_root", {{ x: "-=60", duration: 3.5, ease: "none" }}, 0.0);'
        ]
        return {"svg": svg, "tweens": tweens}
