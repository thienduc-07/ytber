import type { SceneItem, CharacterProfile } from '../types/database';

/**
 * Reusable Temporal Animation Engine.
 * Implements 100% animated visuals with zero photographic dependencies:
 * - Dynamic Multi-Plane Parallax (Sky, Midground, Ground, Particles)
 * - Stylized Vector Character Rigs with Walk, Pull, Cheer, Point, and Mouth-Flap cycles
 * - Persistent Character Consistency (Costumes, Proportions, Color Schemes)
 * - Animated Motion Graphics (Growing charts, animated counters, spline curves)
 * - Animated Tactical Vector Maps (Dynamic route tracing, pulsing radar pins)
 * - Environmental Particle Systems (Smoke embers, mist, dust, data streams, stars)
 */

export class AnimationEngine {
  /**
   * Smootherstep interpolation curve for cinematic camera motion
   */
  public static smootherstep(t: number): number {
    const clamped = Math.max(0, Math.min(1, t));
    return clamped * clamped * clamped * (clamped * (clamped * 6 - 15) + 10);
  }

  /**
   * Main Scene Visual Renderer: Orchestrates all temporal animation layers
   */
  public static renderScene(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    scene: SceneItem,
    localT: number,
    globalT: number,
    characterRegistry?: Record<string, CharacterProfile>,
    isSpeaking: boolean = false,
    illustrationBmp?: ImageBitmap | null
  ) {
    ctx.save();

    // 1. Camera Transformation (Pan & Smootherstep Zoom)
    const zoomRatio = scene.animation_instructions?.zoom_ratio || 1.10;
    const smoothT = this.smootherstep(localT);
    const currentZoom = 1.0 + smoothT * (zoomRatio - 1.0);

    let panX = 0;
    let panY = 0;
    const camMovement = scene.camera_movement || scene.camera_direction || 'slow_push_in';

    if (camMovement.includes('pan_right')) {
      panX = (localT - 0.5) * (w * 0.08);
    } else if (camMovement.includes('tilt_up')) {
      panY = (0.5 - localT) * (h * 0.06);
    } else if (camMovement.includes('tracking')) {
      panX = Math.sin(localT * Math.PI) * (w * 0.04);
    }

    ctx.translate(w / 2, h / 2);
    ctx.scale(currentZoom, currentZoom);
    ctx.translate(-w / 2 + panX, -h / 2 + panY);

    // 2. Render Layered Environment with Multi-plane Parallax
    this.renderEnvironment(ctx, w, h, scene, localT, globalT, illustrationBmp);

    // 3. Render Domain-Specific Visual Modalities
    const method = scene.visual_method || 'toon';
    if (method === 'map') {
      this.renderAnimatedMap(ctx, w, h, scene, localT);
    } else if (method === 'infographic') {
      this.renderAnimatedInfographics(ctx, w, h, scene, localT);
    } else {
      // Default to Stylized Cartoon Characters & Props
      this.renderAnimatedCharactersAndProps(ctx, w, h, scene, localT, globalT, characterRegistry, isSpeaking);
    }

    // 4. Foreground Occlusion & Framing Layer (Fast Parallax 1.35x for 2.5D Depth)
    this.renderForegroundOcclusion(ctx, w, h, scene, localT, globalT);

    // 5. Render Environmental Particle Overlay (Spores, Fireflies, Embers, Stars)
    this.renderParticles(ctx, w, h, scene, localT, globalT);

    // 6. Volumetric Sunlight Shafts (God Rays)
    this.renderVolumetricLight(ctx, w, h, scene, localT);

    // 7. Cinematic Vignette
    this.renderCinematicVignette(ctx, w, h);

    ctx.restore();
  }

  /**
   * Layer 1 & 2: Multi-Plane Parallax Environment
   */
  private static renderEnvironment(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    scene: SceneItem,
    localT: number,
    _globalT: number,
    illustrationBmp?: ImageBitmap | null
  ) {
    if (illustrationBmp) {
      // Draw verified illustration asset with subtle parallax offset
      ctx.save();
      const parallaxOffset = (localT - 0.5) * 40;
      const aspect = illustrationBmp.width / illustrationBmp.height;
      const targetAspect = w / h;
      let dW = w, dH = h;
      if (aspect > targetAspect) {
        dH = h;
        dW = dH * aspect;
      } else {
        dW = w;
        dH = dW / aspect;
      }
      ctx.globalAlpha = 0.85;
      ctx.drawImage(illustrationBmp, (w - dW) / 2 + parallaxOffset, (h - dH) / 2, dW, dH);
      ctx.restore();
      return;
    }

    const env = scene.environment;
    const timeOfDay = env?.time_of_day || 'sunset_golden';

    // Sky / Atmosphere Gradient
    const skyGrad = ctx.createLinearGradient(0, 0, 0, h);
    if (timeOfDay === 'night_moonlight') {
      skyGrad.addColorStop(0, '#050714');
      skyGrad.addColorStop(0.6, '#0f172a');
      skyGrad.addColorStop(1, '#1e1b4b');
    } else if (timeOfDay === 'sunset_golden') {
      skyGrad.addColorStop(0, '#451a03');
      skyGrad.addColorStop(0.35, '#9a3412');
      skyGrad.addColorStop(0.7, '#ea580c');
      skyGrad.addColorStop(1, '#fde047');
    } else if (timeOfDay === 'day') {
      skyGrad.addColorStop(0, '#0284c7');
      skyGrad.addColorStop(0.6, '#38bdf8');
      skyGrad.addColorStop(1, '#bae6fd');
    } else {
      // Futuristic / Cyber / Lab
      skyGrad.addColorStop(0, '#090d16');
      skyGrad.addColorStop(0.5, '#0f172a');
      skyGrad.addColorStop(1, '#1e293b');
    }
    ctx.fillStyle = skyGrad;
    ctx.fillRect(0, 0, w, h);

    // Sun / Moon / Distant Celestial Glow
    const celestialY = h * 0.22;
    const celestialX = w * 0.72;
    const glowGrad = ctx.createRadialGradient(celestialX, celestialY, 10, celestialX, celestialY, w * 0.45);
    if (timeOfDay === 'night_moonlight') {
      glowGrad.addColorStop(0, 'rgba(255, 255, 255, 0.95)');
      glowGrad.addColorStop(0.15, 'rgba(224, 231, 255, 0.4)');
      glowGrad.addColorStop(1, 'rgba(15, 23, 42, 0)');
      ctx.fillStyle = glowGrad;
      ctx.beginPath();
      ctx.arc(celestialX, celestialY, 65, 0, Math.PI * 2);
      ctx.fill();
    } else if (timeOfDay === 'sunset_golden') {
      glowGrad.addColorStop(0, 'rgba(254, 240, 138, 0.95)');
      glowGrad.addColorStop(0.25, 'rgba(249, 115, 22, 0.5)');
      glowGrad.addColorStop(1, 'rgba(69, 26, 3, 0)');
      ctx.fillStyle = glowGrad;
      ctx.beginPath();
      ctx.arc(celestialX, celestialY, 85, 0, Math.PI * 2);
      ctx.fill();
    }

    const desc = ((scene.visual_description || '') + ' ' + (scene.narration_text || '')).toLowerCase();
    const isForest = desc.includes('rừng') || desc.includes('forest') || desc.includes('cây') || desc.includes('lá');

    // Midground Parallax Layer 1: Distant Mountain / Forest Ridge Silhouettes (Speed 0.2x)
    const bgParallax = (localT - 0.5) * (w * 0.05);
    ctx.fillStyle = isForest
      ? (timeOfDay === 'night_moonlight' ? '#09150c' : '#14301a')
      : (timeOfDay === 'night_moonlight' ? '#090d16' : '#271911');
    ctx.beginPath();
    ctx.moveTo(0, h * 0.65);
    const bgPoints = 12;
    for (let i = 0; i <= bgPoints; i++) {
      const px = (i * w) / bgPoints + bgParallax;
      const py = h * 0.52 + Math.sin(i * 1.3) * 60 + Math.cos(i * 2.1) * 35;
      ctx.lineTo(px, py);
    }
    ctx.lineTo(w + 100, h);
    ctx.lineTo(-100, h);
    ctx.closePath();
    ctx.fill();

    // Midground Parallax Layer 2: Closer Ridges / Fortifications / Jungle Trees (Speed 0.5x)
    const midParallax = (localT - 0.5) * (w * 0.12);
    ctx.fillStyle = isForest
      ? (timeOfDay === 'night_moonlight' ? '#0e2314' : '#1b3b20')
      : (timeOfDay === 'night_moonlight' ? '#0f172a' : '#382216');
    ctx.beginPath();
    ctx.moveTo(0, h * 0.75);
    const midPoints = 14;
    for (let i = 0; i <= midPoints; i++) {
      const px = (i * w) / midPoints + midParallax;
      const py = h * 0.64 + Math.sin(i * 1.8 + 1.2) * 80 + Math.cos(i * 0.9) * 40;
      ctx.lineTo(px, py);
    }
    ctx.lineTo(w + 100, h);
    ctx.lineTo(-100, h);
    ctx.closePath();
    ctx.fill();

    // Foreground Action Stage / Ground Hill (Speed 1.0x)
    const fgParallax = (localT - 0.5) * (w * 0.2);
    ctx.fillStyle = isForest
      ? (timeOfDay === 'night_moonlight' ? '#122c19' : '#213818')
      : (timeOfDay === 'night_moonlight' ? '#1e293b' : '#22150c');
    ctx.beginPath();
    ctx.moveTo(0, h * 0.82);
    ctx.quadraticCurveTo(w * 0.45 + fgParallax, h * 0.75, w, h * 0.84);
    ctx.lineTo(w, h);
    ctx.lineTo(0, h);
    ctx.closePath();
    ctx.fill();

    // Stylized Bamboo / Forest Trunks for Dense Tropical Forest atmosphere
    if (isForest) {
      ctx.fillStyle = timeOfDay === 'night_moonlight' ? 'rgba(10, 25, 14, 0.75)' : 'rgba(20, 45, 24, 0.75)';
      const trunkPositions = [w * 0.12, w * 0.85, w * 0.92];
      for (const tx of trunkPositions) {
        ctx.fillRect(tx + fgParallax * 0.8, h * 0.35, 18, h * 0.65);
      }
    }
  }

  /**
   * Layer 3: Stylized Vector Character Rigs & Animated Props
   */
  private static renderAnimatedCharactersAndProps(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    scene: SceneItem,
    localT: number,
    globalT: number,
    characterRegistry?: Record<string, CharacterProfile>,
    isSpeaking: boolean = false
  ) {
    const anim = scene.animation_instructions;
    const action = anim?.character_action || 'march';
    const groundY = h * 0.78;

    // Pick main character from registry or fallback to iconic protagonist
    const charList = characterRegistry ? Object.values(characterRegistry) : [];
    const charProfile = charList[0] || {
      character_id: 'default_char',
      name: 'Chiến sĩ',
      role: 'protagonist',
      body_proportions: 'stylized_cartoon',
      costume_description: 'Quân phục xanh',
      color_scheme: ['#36522D', '#EBB991', '#8A5C36', '#FFD700', '#DC281E'],
      facial_features: 'Mắt biểu cảm',
      distinguishing_props: ['cờ']
    };

    // Calculate Character Position & Entrance
    let charX = w * 0.5;
    let charScale = w * 0.0016;

    if (action === 'march') {
      // Walking progression across frame
      charX = w * 0.35 + (localT * w * 0.3);
    } else if (action === 'pull_cannon') {
      charX = w * 0.58;
      // Draw Artillery Cannon being pulled behind
      this.drawArtilleryCannon(ctx, charX - 260 * charScale, groundY + 10 * charScale, charScale * 1.1, localT);
      // Draw taut rope connecting character to cannon
      ctx.strokeStyle = '#8A5C36';
      ctx.lineWidth = 10 * charScale;
      ctx.beginPath();
      ctx.moveTo(charX - 20 * charScale, groundY - 20 * charScale);
      ctx.lineTo(charX - 220 * charScale, groundY + 5 * charScale);
      ctx.stroke();
    } else if (action === 'cheer') {
      charX = w * 0.5;
      // Draw waving flag of victory
      this.drawWavingFlag(ctx, charX + 50 * charScale, groundY - 140 * charScale, charScale * 1.3, globalT);
    }

    // Draw Character Rig
    this.drawCharacterRig(ctx, charX, groundY, charScale, action, localT, globalT, charProfile, isSpeaking);

    // If second character in registry, draw supporting ally
    if (charList.length > 1 && action === 'march') {
      const secondChar = charList[1];
      const allyX = charX - 180 * charScale;
      this.drawCharacterRig(ctx, allyX, groundY + 15 * charScale, charScale * 0.9, action, (localT + 0.5) % 1.0, globalT, secondChar, false);
    }
  }

  /**
   * Stylized Character Vector Rig
   */
  private static drawCharacterRig(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    scale: number,
    action: string,
    localT: number,
    globalT: number,
    charProfile: CharacterProfile,
    isSpeaking: boolean
  ) {
    const palette = charProfile.color_scheme || ['#36522D', '#EBB991', '#8A5C36', '#FFD700', '#DC281E'];
    const uniformColor = palette[0] || '#36522D';
    const skinColor = palette[1] || '#EBB991';
    const beltColor = palette[2] || '#8A5C36';
    const starGold = palette[3] || '#FFD700';
    const flagRed = palette[4] || '#DC281E';

    ctx.save();
    ctx.translate(x, y);

    // Cycle math
    const walkCycles = 4;
    const walkPhase = Math.sin(localT * walkCycles * Math.PI * 2);
    const bobbing = Math.abs(walkPhase) * 12 * scale;

    // 0. DYNAMIC CONTACT SHADOW (Grounds the character on terrain, eliminating floating artifacts)
    const legLength = 110 * scale;
    const footY = legLength;
    const shadowScale = 1 - Math.min(0.3, bobbing / (40 * scale));
    const shadowWidth = 52 * scale * shadowScale;
    const shadowHeight = 14 * scale * shadowScale;
    const shadowY = footY + 6 * scale;

    ctx.save();
    const shadowGradient = ctx.createRadialGradient(0, shadowY, 2 * scale, 0, shadowY, shadowWidth);
    shadowGradient.addColorStop(0, 'rgba(0, 0, 0, 0.55)');
    shadowGradient.addColorStop(0.5, 'rgba(0, 0, 0, 0.25)');
    shadowGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = shadowGradient;
    ctx.beginPath();
    ctx.ellipse(0, shadowY, shadowWidth, shadowHeight, 0, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    // 1. LEGS & BOOTS
    ctx.lineWidth = 18 * scale;
    ctx.lineCap = 'round';
    ctx.strokeStyle = uniformColor;

    if (action === 'pull_cannon') {
      // Strained wide pulling stance
      ctx.beginPath();
      ctx.moveTo(-12 * scale, 30 * scale);
      ctx.lineTo(-45 * scale, footY);
      ctx.moveTo(12 * scale, 30 * scale);
      ctx.lineTo(35 * scale, footY - 15 * scale);
      ctx.stroke();

      // Boots
      ctx.fillStyle = '#141414';
      ctx.fillRect(-58 * scale, footY - 6 * scale, 36 * scale, 12 * scale);
      ctx.fillRect(25 * scale, footY - 21 * scale, 36 * scale, 12 * scale);
    } else if (action === 'cheer') {
      // Cheering triumphant jump
      ctx.beginPath();
      ctx.moveTo(-10 * scale, 30 * scale);
      ctx.lineTo(-28 * scale, footY - 10 * scale);
      ctx.moveTo(10 * scale, 30 * scale);
      ctx.lineTo(28 * scale, footY - 10 * scale);
      ctx.stroke();

      ctx.fillStyle = '#141414';
      ctx.fillRect(-42 * scale, footY - 16 * scale, 32 * scale, 12 * scale);
      ctx.fillRect(16 * scale, footY - 16 * scale, 32 * scale, 12 * scale);
    } else {
      // Marching Cycle
      const legOffset1 = walkPhase * 28 * scale;
      const legOffset2 = -legOffset1;

      ctx.beginPath();
      ctx.moveTo(-10 * scale, 30 * scale);
      ctx.lineTo(-10 * scale + legOffset1, footY - bobbing);
      ctx.moveTo(10 * scale, 30 * scale);
      ctx.lineTo(10 * scale + legOffset2, footY - bobbing);
      ctx.stroke();

      ctx.fillStyle = '#141414';
      ctx.fillRect(-10 * scale + legOffset1 - 10 * scale, footY - bobbing - 6 * scale, 30 * scale, 12 * scale);
      ctx.fillRect(10 * scale + legOffset2 - 10 * scale, footY - bobbing - 6 * scale, 30 * scale, 12 * scale);
    }

    // 2. TORSO / TUNIC
    const leanForward = action === 'pull_cannon' ? 22 * scale : 0;
    const bodyW = 54 * scale;
    const bodyH = 75 * scale;
    const bodyX = -bodyW / 2 + leanForward;
    const bodyY = -30 * scale - bobbing;

    ctx.fillStyle = uniformColor;
    ctx.roundRect(bodyX, bodyY, bodyW, bodyH, 12 * scale);
    ctx.fill();

    // Directional 3D Rim Lighting on Torso (Highlights sunward edge)
    ctx.fillStyle = 'rgba(255, 255, 255, 0.16)';
    ctx.beginPath();
    ctx.roundRect(bodyX + 2 * scale, bodyY + 2 * scale, bodyW * 0.32, bodyH - 4 * scale, [10 * scale, 0, 0, 10 * scale]);
    ctx.fill();

    // Leather belt and brass buckle
    ctx.fillStyle = beltColor;
    ctx.fillRect(bodyX, bodyY + bodyH * 0.65, bodyW, 12 * scale);
    ctx.fillStyle = starGold;
    ctx.fillRect(bodyX + bodyW / 2 - 8 * scale, bodyY + bodyH * 0.65, 16 * scale, 12 * scale);

    // 3. HEAD & FACE
    const headRadius = 28 * scale;
    const headX = leanForward;
    const headY = bodyY - headRadius * 0.9;

    ctx.fillStyle = skinColor;
    ctx.beginPath();
    ctx.arc(headX, headY, headRadius, 0, Math.PI * 2);
    ctx.fill();

    // Directional 3D Rim Lighting on Head
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.28)';
    ctx.lineWidth = 3.5 * scale;
    ctx.beginPath();
    ctx.arc(headX, headY, headRadius - 2 * scale, Math.PI * 0.8, Math.PI * 1.4);
    ctx.stroke();

    // Expressive Eyes
    const eyeOffsetX = 9 * scale;
    const eyeOffsetY = -2 * scale;
    ctx.fillStyle = '#141414';
    ctx.beginPath();
    ctx.arc(headX + eyeOffsetX, headY + eyeOffsetY, 4.5 * scale, 0, Math.PI * 2);
    ctx.fill();
    // Catchlight highlight
    ctx.fillStyle = '#FFFFFF';
    ctx.beginPath();
    ctx.arc(headX + eyeOffsetX - 1.5 * scale, headY + eyeOffsetY - 1.5 * scale, 1.8 * scale, 0, Math.PI * 2);
    ctx.fill();

    // Eyebrows (Heroic / Determined angle)
    ctx.strokeStyle = '#271911';
    ctx.lineWidth = 3 * scale;
    ctx.beginPath();
    ctx.moveTo(headX + eyeOffsetX - 9 * scale, headY + eyeOffsetY - 7 * scale);
    ctx.lineTo(headX + eyeOffsetX + 7 * scale, headY + eyeOffsetY - 5 * scale);
    ctx.stroke();

    // Mouth Animation: Flap speaking cycle when reading narration, smile when idle
    const mouthY = headY + 12 * scale;
    if (isSpeaking) {
      const mouthOpen = (Math.sin(globalT * 18) + 1) * 3.5 * scale;
      ctx.fillStyle = '#831843';
      ctx.beginPath();
      ctx.ellipse(headX + eyeOffsetX - 2 * scale, mouthY, 6 * scale, Math.max(2 * scale, mouthOpen), 0, 0, Math.PI * 2);
      ctx.fill();
    } else {
      ctx.strokeStyle = '#271911';
      ctx.lineWidth = 2.5 * scale;
      ctx.beginPath();
      ctx.arc(headX + eyeOffsetX - 2 * scale, mouthY - 2 * scale, 5 * scale, 0.2 * Math.PI, 0.8 * Math.PI);
      ctx.stroke();
    }

    // 4. ICONIC HELMET (Mũ nan ngụy trang có sao vàng hoặc mũ kê-pi)
    const hatY = headY - 12 * scale;
    ctx.fillStyle = uniformColor;
    ctx.beginPath();
    ctx.ellipse(headX, hatY, headRadius * 1.25, 24 * scale, 0, Math.PI, 0, false);
    ctx.fill();
    ctx.beginPath();
    ctx.ellipse(headX, hatY + 4 * scale, headRadius * 1.35, 10 * scale, 0, 0, Math.PI * 2);
    ctx.fill();

    // Gold Star on Red Badge
    const badgeX = headX + 12 * scale;
    const badgeY = hatY - 4 * scale;
    ctx.fillStyle = flagRed;
    ctx.beginPath();
    ctx.arc(badgeX, badgeY, 6.5 * scale, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = starGold;
    ctx.beginPath();
    ctx.arc(badgeX, badgeY, 3 * scale, 0, Math.PI * 2);
    ctx.fill();

    // 5. ARMS & ACTIONS
    ctx.strokeStyle = uniformColor;
    ctx.lineWidth = 16 * scale;
    ctx.lineCap = 'round';

    if (action === 'cheer') {
      // Raised arms cheering
      const armWave = Math.sin(globalT * 8) * 8 * scale;
      ctx.beginPath();
      ctx.moveTo(-18 * scale, bodyY + 16 * scale);
      ctx.lineTo(-40 * scale, bodyY - 45 * scale + armWave);
      ctx.moveTo(18 * scale, bodyY + 16 * scale);
      ctx.lineTo(40 * scale, bodyY - 45 * scale - armWave);
      ctx.stroke();
    } else if (action === 'pull_cannon') {
      // Both arms pulling taut rope
      ctx.beginPath();
      ctx.moveTo(10 * scale, bodyY + 16 * scale);
      ctx.lineTo(-24 * scale, bodyY + 40 * scale);
      ctx.moveTo(-10 * scale, bodyY + 16 * scale);
      ctx.lineTo(-35 * scale, bodyY + 45 * scale);
      ctx.stroke();
    } else if (action === 'point_gesture') {
      // One arm pointing forward, one at hip
      ctx.beginPath();
      ctx.moveTo(-18 * scale, bodyY + 16 * scale);
      ctx.lineTo(-22 * scale, bodyY + 45 * scale);
      ctx.moveTo(18 * scale, bodyY + 16 * scale);
      ctx.lineTo(55 * scale, bodyY - 15 * scale);
      ctx.stroke();
    } else {
      // Marching arm swing
      const armSwing1 = -walkPhase * 24 * scale;
      const armSwing2 = -armSwing1;
      ctx.beginPath();
      ctx.moveTo(-18 * scale, bodyY + 16 * scale);
      ctx.lineTo(-18 * scale + armSwing1, bodyY + 50 * scale);
      ctx.moveTo(18 * scale, bodyY + 16 * scale);
      ctx.lineTo(18 * scale + armSwing2, bodyY + 50 * scale);
      ctx.stroke();
    }

    ctx.restore();
  }

  /**
   * Animated Heavy Artillery Cannon (Pháo binh kéo đèo)
   */
  private static drawArtilleryCannon(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    scale: number,
    localT: number
  ) {
    ctx.save();
    ctx.translate(x, y);

    // Wheels rotation as it rolls
    const wheelRadius = 55 * scale;
    const wheelRotation = localT * 8 * Math.PI;

    // Cannon Barrel (Thép đại bác ngẩng cao)
    ctx.save();
    ctx.rotate(-0.35); // Aiming up
    ctx.fillStyle = '#262626';
    ctx.fillRect(-40 * scale, -22 * scale, 180 * scale, 34 * scale);
    ctx.fillStyle = '#404040';
    ctx.fillRect(130 * scale, -25 * scale, 15 * scale, 40 * scale);
    ctx.restore();

    // Carriage Frame
    ctx.fillStyle = '#1c1917';
    ctx.beginPath();
    ctx.moveTo(-80 * scale, 10 * scale);
    ctx.lineTo(20 * scale, -10 * scale);
    ctx.lineTo(0, 30 * scale);
    ctx.closePath();
    ctx.fill();

    // Big Wooden / Steel Wheel
    ctx.save();
    ctx.translate(0, 0);
    ctx.rotate(wheelRotation);
    ctx.fillStyle = '#57534e';
    ctx.beginPath();
    ctx.arc(0, 0, wheelRadius, 0, Math.PI * 2);
    ctx.fill();
    ctx.fillStyle = '#292524';
    ctx.beginPath();
    ctx.arc(0, 0, wheelRadius * 0.8, 0, Math.PI * 2);
    ctx.fill();

    // Spokes
    ctx.strokeStyle = '#d6d3d1';
    ctx.lineWidth = 4 * scale;
    for (let s = 0; s < 6; s++) {
      ctx.beginPath();
      ctx.moveTo(0, 0);
      const angle = (s * Math.PI) / 3;
      ctx.lineTo(Math.cos(angle) * wheelRadius * 0.8, Math.sin(angle) * wheelRadius * 0.8);
      ctx.stroke();
    }
    ctx.fillStyle = '#1c1917';
    ctx.beginPath();
    ctx.arc(0, 0, 16 * scale, 0, Math.PI * 2);
    ctx.fill();
    ctx.restore();

    ctx.restore();
  }

  /**
   * Animated Waving Flag ("Quyết chiến Quyết thắng")
   */
  private static drawWavingFlag(
    ctx: CanvasRenderingContext2D,
    x: number,
    y: number,
    scale: number,
    globalT: number
  ) {
    ctx.save();
    ctx.translate(x, y);

    // Flagpole
    ctx.strokeStyle = '#d4d4d8';
    ctx.lineWidth = 6 * scale;
    ctx.beginPath();
    ctx.moveTo(0, 140 * scale);
    ctx.lineTo(0, -90 * scale);
    ctx.stroke();

    // Flag Cloth Sine Wave Simulation
    const flagW = 150 * scale;
    const flagH = 95 * scale;
    const waveFreq = 8;
    const waveAmp = 12 * scale;

    ctx.fillStyle = '#dc2626';
    ctx.beginPath();
    ctx.moveTo(0, -85 * scale);

    // Top wavy edge
    for (let px = 0; px <= flagW; px += 10) {
      const py = -85 * scale + Math.sin(globalT * waveFreq + px * 0.05) * waveAmp;
      ctx.lineTo(px, py);
    }
    // Bottom wavy edge
    for (let px = flagW; px >= 0; px -= 10) {
      const py = -85 * scale + flagH + Math.sin(globalT * waveFreq + px * 0.05) * waveAmp;
      ctx.lineTo(px, py);
    }
    ctx.closePath();
    ctx.fill();

    // Centered Gold Star in Flag
    const starX = flagW * 0.42;
    const starY = -85 * scale + flagH * 0.48 + Math.sin(globalT * waveFreq + starX * 0.05) * waveAmp;

    ctx.fillStyle = '#facc15';
    ctx.beginPath();
    ctx.arc(starX, starY, 18 * scale, 0, Math.PI * 2);
    ctx.fill();

    ctx.restore();
  }

  /**
   * Animated Motion Graphics & Infographics (for Economics / Tech / Data)
   */
  private static renderAnimatedInfographics(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    _scene: SceneItem,
    localT: number
  ) {
    const smoothT = this.smootherstep(localT);
    const centerX = w * 0.5;
    const centerY = h * 0.48;

    // Translucent glassmorphic card container
    const cardW = w * 0.86;
    const cardH = h * 0.46;
    ctx.fillStyle = 'rgba(15, 23, 42, 0.85)';
    ctx.strokeStyle = '#38bdf8';
    ctx.lineWidth = 4;
    ctx.roundRect(centerX - cardW / 2, centerY - cardH / 2, cardW, cardH, 28);
    ctx.fill();
    ctx.stroke();

    // Growing Bars (e.g. GDP, Capital, Inflation Growth)
    const barCount = 5;
    const barW = (cardW * 0.65) / barCount;
    const maxBarH = cardH * 0.55;
    const startX = centerX - (cardW * 0.38);
    const groundBarY = centerY + cardH * 0.32;

    const barValues = [0.45, 0.6, 0.72, 0.88, 1.0];
    const barColors = ['#38bdf8', '#0284c7', '#0d9488', '#10b981', '#facc15'];

    for (let i = 0; i < barCount; i++) {
      const currentH = barValues[i] * maxBarH * smoothT;
      const bx = startX + i * (barW + 16);
      const by = groundBarY - currentH;

      ctx.fillStyle = barColors[i];
      ctx.roundRect(bx, by, barW, currentH, 8);
      ctx.fill();

      // Number counter on top of final bar
      if (i === barCount - 1 && smoothT > 0.3) {
        const displayValue = (barValues[i] * 7.09 * smoothT).toFixed(2);
        ctx.fillStyle = '#FFFFFF';
        ctx.font = 'bold 38px "Be Vietnam Pro", sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(`+${displayValue}%`, bx + barW / 2, by - 14);
      }
    }

    // Dynamic Spline Trend Line overlay
    ctx.strokeStyle = '#facc15';
    ctx.lineWidth = 8;
    ctx.beginPath();
    for (let i = 0; i < barCount; i++) {
      const bx = startX + i * (barW + 16) + barW / 2;
      const currentH = barValues[i] * maxBarH * smoothT;
      const by = groundBarY - currentH;
      if (i === 0) ctx.moveTo(bx, by);
      else ctx.lineTo(bx, by);
    }
    ctx.stroke();

    // Card Header Banner
    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 44px "Be Vietnam Pro", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('CHỈ SỐ TĂNG TRƯỞNG & DÒNG VỐN', centerX, centerY - cardH * 0.35);
  }

  /**
   * Animated Tactical Vector Maps (for Geographic / Campaign Routes)
   */
  private static renderAnimatedMap(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    _scene: SceneItem,
    localT: number
  ) {
    const smoothT = this.smootherstep(localT);
    const centerX = w * 0.5;
    const centerY = h * 0.46;

    // Tactical Radar Grid
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.2)';
    ctx.lineWidth = 2;
    for (let r = 80; r < w * 0.48; r += 90) {
      ctx.beginPath();
      ctx.arc(centerX, centerY, r, 0, Math.PI * 2);
      ctx.stroke();
    }

    // Dynamic Marching / Route Vector (Curved arrow drawing across map)
    const startX = centerX - w * 0.32;
    const startY = centerY + h * 0.18;
    const ctrlX = centerX - w * 0.05;
    const ctrlY = centerY - h * 0.15;
    const targetX = centerX + w * 0.28;
    const targetY = centerY - h * 0.12;

    ctx.strokeStyle = '#ef4444';
    ctx.lineWidth = 12;
    ctx.setLineDash([20, 12]);
    ctx.beginPath();
    ctx.moveTo(startX, startY);

    // Compute Bezier point according to progress
    const t = smoothT;
    const currentX = (1 - t) * (1 - t) * startX + 2 * (1 - t) * t * ctrlX + t * t * targetX;
    const currentY = (1 - t) * (1 - t) * startY + 2 * (1 - t) * t * ctrlY + t * t * targetY;
    ctx.quadraticCurveTo(ctrlX, ctrlY, currentX, currentY);
    ctx.stroke();
    ctx.setLineDash([]); // Reset dash

    // Pulsing Destination Pin (Đồi A1 / Sở chỉ huy)
    const pulseRadius = 24 + Math.sin(localT * 12) * 12;
    ctx.fillStyle = 'rgba(239, 68, 68, 0.35)';
    ctx.beginPath();
    ctx.arc(targetX, targetY, pulseRadius, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#ef4444';
    ctx.beginPath();
    ctx.arc(targetX, targetY, 14, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#facc15';
    ctx.beginPath();
    ctx.arc(targetX, targetY, 6, 0, Math.PI * 2);
    ctx.fill();

    // Map Location Badge
    ctx.fillStyle = '#ffffff';
    ctx.font = 'bold 36px "Be Vietnam Pro", sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('ĐỊA BÀN CHIẾN DỊCH & TUYẾN HÀNH QUÂN', centerX, centerY - h * 0.24);
  }

  /**
   * Layer 4: Environmental Particle System (Smoke, Embers, Dust, Stars)
   */
  private static renderParticles(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    scene: SceneItem,
    _localT: number,
    globalT: number
  ) {
    const env = scene.environment;
    const particleType = env?.weather_particles || 'smoke_embers';

    if (particleType === 'smoke_embers') {
      // Rising glowing embers
      const count = 30;
      for (let i = 0; i < count; i++) {
        const seed = i * 137.5;
        const speed = 0.3 + (i % 5) * 0.15;
        const px = ((seed * 11 + globalT * 40 * speed) % w);
        const py = h - (((seed * 7 + globalT * 120 * speed) % h));
        const pSize = 3 + (i % 4) * 2;
        const alpha = 0.4 + Math.sin(globalT * 6 + i) * 0.3;

        ctx.fillStyle = i % 2 === 0 ? `rgba(251, 146, 60, ${alpha})` : `rgba(250, 204, 21, ${alpha})`;
        ctx.beginPath();
        ctx.arc(px, py, pSize, 0, Math.PI * 2);
        ctx.fill();
      }
    } else if (particleType === 'stars') {
      // Twinkling celestial cosmos
      const count = 45;
      for (let i = 0; i < count; i++) {
        const px = (i * 12345) % w;
        const py = (i * 67890) % (h * 0.65);
        const twinkle = 0.3 + Math.sin(globalT * 5 + i * 2) * 0.4;
        ctx.fillStyle = `rgba(255, 255, 255, ${Math.max(0.1, twinkle)})`;
        ctx.beginPath();
        ctx.arc(px, py, 2.5, 0, Math.PI * 2);
        ctx.fill();
      }
    } else if (particleType === 'data_stream') {
      // Falling tech data packets
      const cols = 16;
      for (let c = 0; c < cols; c++) {
        const colX = (c * w) / cols + 20;
        const speed = 250 + (c % 4) * 100;
        const headY = (globalT * speed + c * 80) % h;
        const alpha = 0.5 + Math.sin(globalT * 4 + c) * 0.3;

        ctx.fillStyle = `rgba(56, 189, 248, ${alpha})`;
        ctx.fillRect(colX, headY, 4, 30);
      }
    } else {
      // Default / Forest: Floating luminous fireflies & pollen spores
      const count = 28;
      for (let i = 0; i < count; i++) {
        const seed = i * 233.1;
        const speedX = Math.sin(globalT * 1.5 + i) * 25;
        const speedY = Math.cos(globalT * 1.2 + i * 2) * 15;
        const px = ((seed * 17 + globalT * 12 + speedX) % w + w) % w;
        const py = ((seed * 31 - globalT * 25 + speedY) % h + h) % h;
        const pSize = 3 + (i % 3) * 2;
        const alpha = 0.35 + Math.sin(globalT * 4 + i) * 0.35;

        ctx.fillStyle = `rgba(250, 204, 21, ${alpha})`;
        ctx.beginPath();
        ctx.arc(px, py, pSize, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  /**
   * Layer 4: Foreground Occlusion & Framing (Fast parallax 1.35x for cinematic 2.5D depth)
   */
  private static renderForegroundOcclusion(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    scene: SceneItem,
    localT: number,
    globalT: number
  ) {
    const desc = ((scene.visual_description || '') + ' ' + (scene.narration_text || '')).toLowerCase();
    const fgParallax = (localT - 0.5) * (w * 0.35); // Fast parallax creates foreground depth

    ctx.save();

    if (desc.includes('rừng') || desc.includes('forest') || desc.includes('cây') || desc.includes('nature') || desc.includes('lá')) {
      // Tropical Forest Foreground: Dangling vines and silhouette foliage
      const sway = Math.sin(globalT * 2.2) * 12;

      // Top-Left Overhanging Branch & Liana Vine
      ctx.fillStyle = '#0f1f12';
      ctx.beginPath();
      ctx.moveTo(-40 + fgParallax, 0);
      ctx.quadraticCurveTo(w * 0.25 + fgParallax + sway, h * 0.12, w * 0.35 + fgParallax, 0);
      ctx.lineTo(-40, 0);
      ctx.fill();

      // Dangling vine
      ctx.strokeStyle = '#182b1c';
      ctx.lineWidth = 6;
      ctx.beginPath();
      ctx.moveTo(w * 0.18 + fgParallax, h * 0.08);
      ctx.quadraticCurveTo(w * 0.20 + fgParallax + sway, h * 0.28, w * 0.16 + fgParallax + sway * 1.5, h * 0.45);
      ctx.stroke();

      // Top-Right Palm Frond Silhouette
      ctx.fillStyle = '#0a170d';
      ctx.beginPath();
      ctx.moveTo(w + 50 + fgParallax, 0);
      ctx.quadraticCurveTo(w * 0.75 + fgParallax - sway, h * 0.18, w * 0.65 + fgParallax, 0);
      ctx.lineTo(w + 50, 0);
      ctx.fill();

      // Bottom-Left and Bottom-Right Bush Silhouette
      ctx.fillStyle = '#0c1a10';
      ctx.beginPath();
      ctx.arc(-20 + fgParallax, h + 30, 110, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.arc(w + 30 + fgParallax, h + 40, 130, 0, Math.PI * 2);
      ctx.fill();
    } else {
      // Architectural / Framing Pillar Silhouette
      ctx.fillStyle = 'rgba(10, 8, 16, 0.45)';
      ctx.beginPath();
      ctx.moveTo(-30 + fgParallax, 0);
      ctx.lineTo(w * 0.08 + fgParallax, 0);
      ctx.lineTo(w * 0.04 + fgParallax, h);
      ctx.lineTo(-30, h);
      ctx.closePath();
      ctx.fill();
    }

    ctx.restore();
  }

  /**
   * Layer 6: Volumetric Light Rays (Cinematic God Rays)
   */
  private static renderVolumetricLight(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    scene: SceneItem,
    _localT: number
  ) {
    const desc = ((scene.visual_description || '') + ' ' + (scene.narration_text || '')).toLowerCase();
    const env = scene.environment;
    const timeOfDay = env?.time_of_day || 'sunset_golden';

    if (timeOfDay === 'night_moonlight') return; // No golden rays at night

    ctx.save();
    ctx.globalCompositeOperation = 'screen';

    const rayAngle = 0.45; // Radians angled down
    const rayOriginX = w * 0.75;
    const rayOriginY = h * 0.15;

    // Draw 3 soft volumetric light beams
    for (let r = 0; r < 3; r++) {
      const beamOffset = r * (w * 0.14) - (w * 0.10);
      const beamW = w * 0.16;

      const grad = ctx.createLinearGradient(rayOriginX, rayOriginY, rayOriginX - h * Math.sin(rayAngle), h);
      const isWarm = desc.includes('rừng') || timeOfDay === 'sunset_golden';
      grad.addColorStop(0, isWarm ? 'rgba(254, 240, 138, 0.14)' : 'rgba(224, 242, 254, 0.10)');
      grad.addColorStop(0.7, isWarm ? 'rgba(251, 146, 60, 0.04)' : 'rgba(186, 230, 253, 0.03)');
      grad.addColorStop(1, 'rgba(0, 0, 0, 0)');

      ctx.fillStyle = grad;
      ctx.beginPath();
      ctx.moveTo(rayOriginX + beamOffset, rayOriginY);
      ctx.lineTo(rayOriginX + beamOffset + beamW, rayOriginY);
      ctx.lineTo(rayOriginX + beamOffset + beamW - h * Math.sin(rayAngle) * 0.6, h);
      ctx.lineTo(rayOriginX + beamOffset - h * Math.sin(rayAngle) * 0.6, h);
      ctx.closePath();
      ctx.fill();
    }

    ctx.restore();
  }

  /**
   * Cinematic Vignette
   */
  private static renderCinematicVignette(ctx: CanvasRenderingContext2D, w: number, h: number) {
    const vigGrad = ctx.createRadialGradient(w / 2, h / 2, Math.min(w, h) * 0.45, w / 2, h / 2, Math.max(w, h) * 0.8);
    vigGrad.addColorStop(0, 'rgba(0, 0, 0, 0)');
    vigGrad.addColorStop(1, 'rgba(0, 0, 0, 0.45)');
    ctx.fillStyle = vigGrad;
    ctx.fillRect(0, 0, w, h);
  }
}
