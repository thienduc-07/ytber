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
    if (method === 'anatomy') {
      this.renderAnatomyVisual(ctx, w, h, scene, localT, globalT);
    } else if (method === 'schematic') {
      this.renderSchematicVisual(ctx, w, h, scene, localT, globalT);
    } else if (method === 'horror') {
      this.renderHorrorVisual(ctx, w, h, scene, localT, globalT);
    } else if (method === 'presenter') {
      this.renderPresenterVisual(ctx, w, h, scene, localT, globalT, isSpeaking);
    } else if (method === 'map') {
      this.renderAnimatedMap(ctx, w, h, scene, localT);
    } else if (method === 'infographic') {
      this.renderAnimatedInfographics(ctx, w, h, scene, localT);
    } else {
      // Default to Stylized Cartoon Characters & Props
      this.renderAnimatedCharactersAndProps(ctx, w, h, scene, localT, globalT, characterRegistry, isSpeaking);
    }

    // 4. Foreground Occlusion & Framing Layer (Fast Parallax 1.35x for 2.5D Depth)
    if (method !== 'anatomy' && method !== 'schematic') {
      this.renderForegroundOcclusion(ctx, w, h, scene, localT, globalT);
    }

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
   * Domain Visual: Anatomical & Biological Internal Organs (Heart 72 BPM & Live ECG Monitor)
   */
  private static renderAnatomyVisual(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    _scene: SceneItem,
    _localT: number,
    globalT: number
  ) {
    ctx.save();

    // 1. Dark Medical Monitor Ground
    ctx.fillStyle = '#06080E';
    ctx.fillRect(0, 0, w, h);

    // Subtle Grid Overlay
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.06)';
    ctx.lineWidth = 1;
    const gridSize = 40;
    for (let x = 0; x < w; x += gridSize) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += gridSize) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    // 2. Pulse Mechanics (72 BPM = 0.833s period, double beat systole/diastole)
    const period = 0.833;
    const cycle = (globalT % period) / period;
    let pulse = 1.0;
    if (cycle < 0.15) {
      pulse += Math.sin((cycle / 0.15) * Math.PI) * 0.10; // First lub
    } else if (cycle >= 0.18 && cycle < 0.32) {
      pulse += Math.sin(((cycle - 0.18) / 0.14) * Math.PI) * 0.06; // Second dub
    }

    const cx = w * 0.5;
    const cy = h * 0.40;

    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(pulse, pulse);

    // Glow under heart
    const glow = ctx.createRadialGradient(0, 0, 40, 0, 0, 220);
    glow.addColorStop(0, 'rgba(239, 68, 68, 0.35)');
    glow.addColorStop(0.6, 'rgba(185, 28, 28, 0.12)');
    glow.addColorStop(1, 'rgba(0, 0, 0, 0)');
    ctx.fillStyle = glow;
    ctx.beginPath();
    ctx.arc(0, 0, 220, 0, Math.PI * 2);
    ctx.fill();

    // Pulmonary Artery (Blue Arch behind)
    ctx.fillStyle = '#0284C7';
    ctx.beginPath();
    ctx.arc(-55, -95, 42, 0, Math.PI * 2);
    ctx.fill();

    // Aortic Arch (Crimson Tube)
    ctx.strokeStyle = '#DC2626';
    ctx.lineWidth = 36;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.arc(-8, -115, 60, Math.PI * 0.85, Math.PI * 0.15, true);
    ctx.stroke();

    // Branching Carotid Arteries
    ctx.lineWidth = 14;
    ctx.beginPath();
    ctx.moveTo(-40, -170);
    ctx.lineTo(-45, -205);
    ctx.moveTo(-10, -175);
    ctx.lineTo(-10, -212);
    ctx.moveTo(22, -170);
    ctx.lineTo(28, -205);
    ctx.stroke();

    // Main Heart Muscle (Ventricles & Atria)
    const heartGrad = ctx.createRadialGradient(-30, -30, 20, 0, 20, 150);
    heartGrad.addColorStop(0, '#EF4444');
    heartGrad.addColorStop(0.65, '#B91C1C');
    heartGrad.addColorStop(1, '#5B0D0D');

    ctx.fillStyle = heartGrad;
    ctx.beginPath();
    ctx.moveTo(0, 140);
    // Left ventricle curve
    ctx.bezierCurveTo(-150, 60, -160, -80, -65, -80);
    // Center notch
    ctx.bezierCurveTo(-15, -80, 0, -40, 0, -30);
    // Right ventricle curve
    ctx.bezierCurveTo(0, -40, 15, -80, 65, -80);
    ctx.bezierCurveTo(160, -80, 150, 60, 0, 140);
    ctx.closePath();
    ctx.fill();

    // Specular Highlight (3D Volume Depth)
    ctx.fillStyle = 'rgba(255, 255, 255, 0.22)';
    ctx.beginPath();
    ctx.ellipse(-50, -20, 40, 65, -Math.PI / 6, 0, Math.PI * 2);
    ctx.fill();

    // Anterior Interventricular Artery (Coronary Groove Line)
    ctx.strokeStyle = '#FACC15';
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.moveTo(-18, -40);
    ctx.quadraticCurveTo(-10, 40, -5, 125);
    ctx.stroke();

    // Oxygenated blood flow particles
    for (let p = 0; p < 8; p++) {
      const pOffset = (globalT * 2.0 + p * 0.4) % 1.0;
      const angle = Math.PI * 0.85 - pOffset * (Math.PI * 0.7);
      const px = -8 + Math.cos(angle) * 60;
      const py = -115 + Math.sin(angle) * 60;
      ctx.fillStyle = '#FEE2E2';
      ctx.beginPath();
      ctx.arc(px, py, 4, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.restore(); // Heart transform

    // 3. Technical Leader Line Callouts
    // Callout 1: Aorta
    const callout1X = w * 0.72;
    const callout1Y = h * 0.22;
    ctx.strokeStyle = '#38BDF8';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(cx - 10, cy - 130);
    ctx.lineTo(callout1X - 10, callout1Y + 20);
    ctx.stroke();
    ctx.setLineDash([]);

    // Callout 1 Box
    ctx.fillStyle = 'rgba(14, 23, 42, 0.92)';
    ctx.strokeStyle = '#38BDF8';
    ctx.lineWidth = 1.8;
    ctx.fillRect(callout1X - 10, callout1Y - 10, 220, 56);
    ctx.strokeRect(callout1X - 10, callout1Y - 10, 220, 56);
    ctx.fillStyle = '#38BDF8';
    ctx.font = 'bold 12px "Space Grotesk", monospace';
    ctx.fillText('ĐỘNG MẠCH CHỦ (AORTA)', callout1X, callout1Y + 12);
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '900 14px "Montserrat", sans-serif';
    ctx.fillText('ÁP LỰC: 120 mmHg', callout1X, callout1Y + 34);

    // Callout 2: Left Ventricle
    const callout2X = w * 0.72;
    const callout2Y = h * 0.48;
    ctx.strokeStyle = '#38BDF8';
    ctx.lineWidth = 2;
    ctx.setLineDash([6, 4]);
    ctx.beginPath();
    ctx.moveTo(cx - 15, cy + 30);
    ctx.lineTo(callout2X - 10, callout2Y + 20);
    ctx.stroke();
    ctx.setLineDash([]);

    ctx.fillStyle = 'rgba(14, 23, 42, 0.92)';
    ctx.fillRect(callout2X - 10, callout2Y - 10, 220, 56);
    ctx.strokeRect(callout2X - 10, callout2Y - 10, 220, 56);
    ctx.fillStyle = '#38BDF8';
    ctx.font = 'bold 12px "Space Grotesk", monospace';
    ctx.fillText('TÂM THẤT TRÁI', callout2X, callout2Y + 12);
    ctx.fillStyle = '#FFFFFF';
    ctx.font = '900 14px "Montserrat", sans-serif';
    ctx.fillText('CÔNG SUẤT: 5.2 L/P', callout2X, callout2Y + 34);

    // Top Telemetry Badge
    ctx.fillStyle = 'rgba(14, 23, 42, 0.85)';
    ctx.strokeStyle = '#22C55E';
    ctx.lineWidth = 1.5;
    ctx.fillRect(25, h * 0.22 - 10, 210, 56);
    ctx.strokeRect(25, h * 0.22 - 10, 210, 56);
    ctx.fillStyle = '#22C55E';
    ctx.font = 'bold 11px "Space Grotesk", monospace';
    ctx.fillText('NHỊP TIM SINH HỌC', 38, h * 0.22 + 12);
    ctx.font = '900 18px "Montserrat", sans-serif';
    ctx.fillText('72 BPM', 38, h * 0.22 + 34);

    // 4. Live ECG Telemetry Monitor (Lower third above subtitles)
    const ecgY = h * 0.68;
    const ecgH = 80;
    const ecgW = w - 50;

    ctx.fillStyle = 'rgba(8, 14, 28, 0.85)';
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
    ctx.lineWidth = 1.5;
    ctx.fillRect(25, ecgY, ecgW, ecgH);
    ctx.strokeRect(25, ecgY, ecgW, ecgH);

    ctx.fillStyle = '#22C55E';
    ctx.font = 'bold 11px "Space Grotesk", monospace';
    ctx.fillText('ECG TELEMETRY [LEAD II]', 38, ecgY + 20);

    // ECG Waveform Path
    ctx.strokeStyle = '#22C55E';
    ctx.lineWidth = 2.5;
    ctx.shadowColor = '#22C55E';
    ctx.shadowBlur = 10;
    ctx.beginPath();

    const baselineY = ecgY + 50;
    const waveProgress = ((globalT * 120) % (ecgW - 40));

    ctx.moveTo(35, baselineY);
    for (let x = 35; x < 35 + waveProgress; x += 3) {
      const rel = (x - 35) % 180;
      let yOffset = 0;
      if (rel > 60 && rel < 75) yOffset = -5; // P wave
      else if (rel >= 75 && rel < 82) yOffset = 4; // Q
      else if (rel >= 82 && rel < 92) yOffset = -36; // R spike
      else if (rel >= 92 && rel < 100) yOffset = 10; // S
      else if (rel >= 115 && rel < 135) yOffset = -9; // T wave
      ctx.lineTo(x, baselineY + yOffset);
    }
    ctx.stroke();

    ctx.restore();
  }

  /**
   * Domain Visual: Scientific & Technical Schematic (Holographic Radar & Physics Blueprint)
   */
  private static renderSchematicVisual(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    _scene: SceneItem,
    _localT: number,
    globalT: number
  ) {
    ctx.save();

    // 1. Blueprint Deep Navy Ground
    ctx.fillStyle = '#070C1A';
    ctx.fillRect(0, 0, w, h);

    // Blueprint Cyan Grid
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.08)';
    ctx.lineWidth = 1;
    for (let x = 0; x < w; x += 36) {
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, h);
      ctx.stroke();
    }
    for (let y = 0; y < h; y += 36) {
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(w, y);
      ctx.stroke();
    }

    const cx = w * 0.5;
    const cy = h * 0.42;

    // Holographic Circular Target System
    const radius = Math.min(w, h) * 0.28;
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.35)';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.arc(cx, cy, radius, 0, Math.PI * 2);
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(cx, cy, radius * 0.65, 0, Math.PI * 2);
    ctx.stroke();

    ctx.beginPath();
    ctx.arc(cx, cy, radius * 0.3, 0, Math.PI * 2);
    ctx.stroke();

    // Rotating Sweep Laser Beam
    const sweepAngle = (globalT * 1.6) % (Math.PI * 2);
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(sweepAngle);

    const sweepGrad = ctx.createRadialGradient(0, 0, 10, 0, 0, radius);
    sweepGrad.addColorStop(0, 'rgba(56, 189, 248, 0.6)');
    sweepGrad.addColorStop(0.8, 'rgba(56, 189, 248, 0.15)');
    sweepGrad.addColorStop(1, 'rgba(56, 189, 248, 0)');
    ctx.fillStyle = sweepGrad;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.arc(0, 0, radius, 0, Math.PI * 0.25);
    ctx.closePath();
    ctx.fill();

    // Laser Edge Line
    ctx.strokeStyle = '#38BDF8';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(radius, 0);
    ctx.stroke();

    ctx.restore();

    // Crosshairs
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.5)';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(cx - radius - 20, cy);
    ctx.lineTo(cx + radius + 20, cy);
    ctx.moveTo(cx, cy - radius - 20);
    ctx.lineTo(cx, cy + radius + 20);
    ctx.stroke();

    // Oscilloscope Waveform at Mid-Bottom
    const oscY = h * 0.66;
    ctx.strokeStyle = '#FACC15';
    ctx.lineWidth = 3;
    ctx.shadowColor = '#FACC15';
    ctx.shadowBlur = 12;
    ctx.beginPath();
    for (let x = 40; x < w - 40; x += 4) {
      const freq = 0.04;
      const amp = Math.sin((x * freq) - (globalT * 6)) * 28;
      if (x === 40) ctx.moveTo(x, oscY + amp);
      else ctx.lineTo(x, oscY + amp);
    }
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Technical Labels
    ctx.fillStyle = '#38BDF8';
    ctx.font = 'bold 12px "Space Grotesk", monospace';
    ctx.fillText('SƠ ĐỒ NGUYÊN LÝ KHOA HỌC // HỆ THỐNG RADAR & SÓNG', 40, h * 0.16);
    ctx.fillStyle = '#FACC15';
    ctx.fillText('DAO ĐỘNG CỘNG HƯỞNG: 4.8 Hz // BẬT', 40, oscY - 35);

    ctx.restore();
  }

  /**
   * Domain Visual: Atmospheric Horror (Dynamic Multi-Scene Code-First Engine - Phương Án 2)
   * Intelligently renders distinct, cinematic 2.5D visual compositions tailored to the exact
   * narrative beat, props, characters, lighting, and camera angle of each scene.
   */
  private static renderHorrorVisual(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    scene: SceneItem,
    localT: number,
    globalT: number
  ) {
    ctx.save();

    const text = (scene.narration_text || '').toLowerCase();
    const desc = (scene.visual_description || '').toLowerCase();
    const order = scene.scene_order || 1;

    // Detect scene context
    const isAerial = order === 1 || text.includes('flycam') || desc.includes('flycam') || text.includes('ngôi làng') || desc.includes('ngôi làng');
    const isSwing = order === 2 || text.includes('xích đu') || desc.includes('xích đu') || text.includes('lãng quên') || desc.includes('mục nát');
    const isClockAltar = order === 3 || text.includes('đồng hồ') || desc.includes('đồng hồ') || text.includes('ngọn đèn') || text.includes('bàn thờ');
    const isFootprints = order === 4 || text.includes('bước chân') || desc.includes('dấu chân') || text.includes('dấu chân');
    const isMinhFlashlight = order === 5 || text.includes('người khách') || desc.includes('đèn pin') && text.includes('máy quay');
    const isDoorOpen = order === 6 || text.includes('cánh cửa tự mở') || desc.includes('cửa từ từ mở');
    const isFamilyPhoto = order === 7 || text.includes('bức ảnh kỳ lạ') || desc.includes('cào xước') || text.includes('cào nát');
    const isWhisperShadow = order === 8 || text.includes('thì thầm') || desc.includes('sau gáy') || text.includes('sau lưng');
    const isLockedDoor = order === 9 || text.includes('khóa kín') || desc.includes('gầm cầu thang') || text.includes('vết cào sâu');
    const isDiary = order === 10 || text.includes('nhật ký') || desc.includes('nhật ký') || text.includes('ngày 17 tháng 10');
    const isFlashback = order === 11 || text.includes('chôn giấu') || desc.includes('flashback') || text.includes('bi kịch');
    const isWhiteWoman = order === 12 || text.includes('người đàn bà') || desc.includes('áo trắng') || text.includes('tóc dài');
    const isChase = order === 13 || text.includes('ngoảnh đầu') || desc.includes('chạy dọc') || text.includes('lao về phía');
    const isMirror = order === 14 || text.includes('trong gương') || desc.includes('chiếc gương') || text.includes('bầm tím');
    const isTwist = order === 15 || text.includes('cú twist') || desc.includes('con gái yêu') || text.includes('chính là minh');
    const isMorning = order === 16 || text.includes('tiếp theo') || text.includes('sáng hôm sau') || desc.includes('sáng hôm sau');

    if (isAerial) {
      // SCENE 1: Cinematic Aerial Push-In over Vietnamese Village in Night Mist
      const sky = ctx.createLinearGradient(0, 0, 0, h);
      sky.addColorStop(0, '#020308');
      sky.addColorStop(0.5, '#070A18');
      sky.addColorStop(1, '#03050B');
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, w, h);

      // Distant cold moon
      const mx = w * 0.76;
      const my = h * 0.18;
      const mGlow = ctx.createRadialGradient(mx, my, 10, mx, my, 160);
      mGlow.addColorStop(0, 'rgba(254, 243, 199, 0.6)');
      mGlow.addColorStop(0.4, 'rgba(254, 243, 199, 0.15)');
      mGlow.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = mGlow;
      ctx.beginPath();
      ctx.arc(mx, my, 160, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#FEF3C7';
      ctx.beginPath();
      ctx.arc(mx, my, 38, 0, Math.PI * 2);
      ctx.fill();

      // Distant mountain ridge
      ctx.fillStyle = '#050711';
      ctx.beginPath();
      ctx.moveTo(0, h * 0.45);
      ctx.bezierCurveTo(w * 0.3, h * 0.38, w * 0.7, h * 0.48, w, h * 0.42);
      ctx.lineTo(w, h);
      ctx.lineTo(0, h);
      ctx.closePath();
      ctx.fill();

      // Village roofs in mist (aerial bird-eye angle)
      ctx.fillStyle = '#080C1A';
      for (let r = 0; r < 5; r++) {
        const rx = w * (0.12 + r * 0.18);
        const ry = h * (0.55 + (r % 2) * 0.08);
        ctx.beginPath();
        ctx.moveTo(rx - 45, ry + 25);
        ctx.lineTo(rx, ry - 20);
        ctx.lineTo(rx + 45, ry + 25);
        ctx.closePath();
        ctx.fill();
        ctx.strokeStyle = '#1E293B';
        ctx.lineWidth = 2;
        ctx.stroke();
      }

      // Winding dirt path
      ctx.strokeStyle = '#0F172A';
      ctx.lineWidth = 28;
      ctx.beginPath();
      ctx.moveTo(w * 0.1, h);
      ctx.bezierCurveTo(w * 0.35, h * 0.82, w * 0.45, h * 0.72, w * 0.52, h * 0.62);
      ctx.stroke();

      // Solitary Grand Wooden House at the end of the road
      const hx = w * 0.52;
      const hy = h * 0.60;
      ctx.fillStyle = '#04060C';
      ctx.fillRect(hx - 60, hy - 30, 120, 65);
      ctx.beginPath();
      ctx.moveTo(hx - 80, hy - 25);
      ctx.lineTo(hx, hy - 75);
      ctx.lineTo(hx + 80, hy - 25);
      ctx.closePath();
      ctx.fill();

      // Volumetric drifting fog
      ctx.fillStyle = 'rgba(148, 163, 184, 0.15)';
      for (let i = 0; i < 3; i++) {
        const fy = h * (0.5 + i * 0.16);
        const fOffset = (globalT * (20 + i * 15)) % w;
        ctx.beginPath();
        ctx.ellipse((w * 0.5 + fOffset) % (w + 200) - 100, fy, 260, 45, 0, 0, Math.PI * 2);
        ctx.fill();
      }

    } else if (isSwing) {
      // SCENE 2: The Abandoned Wooden House & Autonomous Creaking Porch Swing
      ctx.fillStyle = '#050711';
      ctx.fillRect(0, 0, w, h);

      // Decaying wooden porch beam
      ctx.fillStyle = '#0D111E';
      ctx.fillRect(w * 0.08, h * 0.22, w * 0.84, 30);
      ctx.fillRect(w * 0.15, h * 0.22, 28, h * 0.55);
      ctx.fillRect(w * 0.82, h * 0.22, 28, h * 0.55);

      // Autonomous swinging swing
      const swingAngle = Math.sin(globalT * 2.4) * 0.22;
      const pivotX = w * 0.5;
      const pivotY = h * 0.25;
      const ropeLen = h * 0.38;

      ctx.save();
      ctx.translate(pivotX, pivotY);
      ctx.rotate(swingAngle);

      // Rusty chains
      ctx.strokeStyle = '#64748B';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(-35, 0);
      ctx.lineTo(-35, ropeLen);
      ctx.moveTo(35, 0);
      ctx.lineTo(35, ropeLen);
      ctx.stroke();

      // Wooden swing seat
      ctx.fillStyle = '#334155';
      ctx.fillRect(-50, ropeLen, 100, 14);
      ctx.restore();

      // Overgrown dead tree vines
      ctx.strokeStyle = '#090D18';
      ctx.lineWidth = 8;
      ctx.beginPath();
      ctx.moveTo(0, h * 0.15);
      ctx.bezierCurveTo(w * 0.18, h * 0.35, w * 0.05, h * 0.55, w * 0.2, h * 0.7);
      ctx.stroke();

      // Rotted porch floorboards with ground mist
      ctx.fillStyle = '#070A14';
      ctx.fillRect(0, h * 0.75, w, h * 0.25);

      ctx.fillStyle = 'rgba(203, 213, 225, 0.10)';
      ctx.beginPath();
      ctx.ellipse(w * 0.5, h * 0.85, w * 0.65, 55, 0, 0, Math.PI * 2);
      ctx.fill();

    } else if (isClockAltar) {
      // SCENE 3: Grandfather Clock Striking 00:00 & Ancestral Altar Oil Lamp Bursting into Flame
      ctx.fillStyle = '#030408';
      ctx.fillRect(0, 0, w, h);

      // 1. Antique Grandfather Pendulum Clock on Left
      const clockX = w * 0.25;
      const clockY = h * 0.28;
      ctx.fillStyle = '#1C1917';
      ctx.fillRect(clockX - 55, clockY, 110, h * 0.52);
      ctx.strokeStyle = '#78350F';
      ctx.lineWidth = 5;
      ctx.strokeRect(clockX - 55, clockY, 110, h * 0.52);

      // Clock face
      ctx.fillStyle = '#FEF3C7';
      ctx.beginPath();
      ctx.arc(clockX, clockY + 60, 42, 0, Math.PI * 2);
      ctx.fill();
      ctx.strokeStyle = '#1C1917';
      ctx.lineWidth = 3;
      // Hands exactly pointing to 12:00
      ctx.beginPath();
      ctx.moveTo(clockX, clockY + 60);
      ctx.lineTo(clockX, clockY + 28);
      ctx.moveTo(clockX, clockY + 60);
      ctx.lineTo(clockX, clockY + 34);
      ctx.stroke();

      // Pendulum swinging
      const pendAngle = Math.sin(globalT * 3.6) * 0.25;
      ctx.save();
      ctx.translate(clockX, clockY + 110);
      ctx.rotate(pendAngle);
      ctx.strokeStyle = '#D97706';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.moveTo(0, 0);
      ctx.lineTo(0, 110);
      ctx.stroke();
      ctx.fillStyle = '#F59E0B';
      ctx.beginPath();
      ctx.arc(0, 110, 18, 0, Math.PI * 2);
      ctx.fill();
      ctx.restore();

      // 2. Ancestral Altar on Right
      const altarX = w * 0.72;
      const altarY = h * 0.50;
      ctx.fillStyle = '#450A0A'; // Deep antique mahogany red
      ctx.fillRect(altarX - 110, altarY, 220, 24);
      ctx.fillRect(altarX - 95, altarY + 24, 190, 80);

      // Brass candlesticks
      ctx.fillStyle = '#B45309';
      ctx.fillRect(altarX - 85, altarY - 50, 14, 50);
      ctx.fillRect(altarX + 71, altarY - 50, 14, 50);

      // Oil Lamp (Đèn Dầu) in Center of Altar
      const lampX = altarX;
      const lampY = altarY - 25;
      ctx.fillStyle = '#D97706';
      ctx.beginPath();
      ctx.arc(lampX, lampY, 18, 0, Math.PI * 2);
      ctx.fill();

      // Violent Burst of Flame & Radiant Glow (00:00 trigger)
      const flameFlicker = 1.0 + Math.sin(globalT * 15) * 0.25;
      const flameGrad = ctx.createRadialGradient(lampX, lampY - 45, 5, lampX, lampY - 45, 120 * flameFlicker);
      flameGrad.addColorStop(0, 'rgba(255, 87, 34, 0.95)');
      flameGrad.addColorStop(0.3, 'rgba(251, 191, 36, 0.7)');
      flameGrad.addColorStop(0.7, 'rgba(234, 88, 12, 0.25)');
      flameGrad.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = flameGrad;
      ctx.beginPath();
      ctx.arc(lampX, lampY - 45, 120 * flameFlicker, 0, Math.PI * 2);
      ctx.fill();

      // Teardrop flame shape
      ctx.fillStyle = '#FFFBEB';
      ctx.beginPath();
      ctx.moveTo(lampX, lampY - 70 * flameFlicker);
      ctx.bezierCurveTo(lampX - 22, lampY - 30, lampX - 15, lampY - 5, lampX, lampY - 5);
      ctx.bezierCurveTo(lampX + 15, lampY - 5, lampX + 22, lampY - 30, lampX, lampY - 70 * flameFlicker);
      ctx.fill();

    } else if (isFootprints) {
      // SCENE 4: Low-Angle Tracking Shot along Wooden Floorboards & Glowing Wet Footprints
      ctx.fillStyle = '#060813';
      ctx.fillRect(0, 0, w, h);

      // Perspective floorboards converging into hallway distance
      const vanishingX = w * 0.5;
      const vanishingY = h * 0.25;
      ctx.strokeStyle = '#1E293B';
      ctx.lineWidth = 3;
      for (let f = -5; f <= 5; f++) {
        ctx.beginPath();
        ctx.moveTo(vanishingX, vanishingY);
        ctx.lineTo(w * 0.5 + f * (w * 0.22), h);
        ctx.stroke();
      }

      // Horizontal plank joints
      for (let j = 1; j <= 8; j++) {
        const py = vanishingY + Math.pow(j / 8, 2.2) * (h - vanishingY);
        ctx.beginPath();
        ctx.moveTo(0, py);
        ctx.lineTo(w, py);
        ctx.stroke();
      }

      // Wet footprint sequence stepping closer over time
      const footCount = 6;
      for (let fp = 0; fp < footCount; fp++) {
        const fpProg = fp / footCount;
        const fy = vanishingY + Math.pow(fpProg, 1.8) * (h * 0.65);
        const fx = vanishingX + (fp % 2 === 0 ? -1 : 1) * (30 + fpProg * 75);
        const scale = 0.4 + fpProg * 1.1;

        // Footprint opacity based on sequence
        const alpha = Math.min(0.85, Math.max(0.08, 1.0 - (globalT * 0.8 - fp * 0.5) % 2.5));
        ctx.fillStyle = `rgba(56, 189, 248, ${alpha * 0.65})`;
        ctx.save();
        ctx.translate(fx, fy);
        ctx.scale(scale, scale);
        // Sole
        ctx.beginPath();
        ctx.ellipse(0, 0, 16, 28, 0, 0, Math.PI * 2);
        ctx.fill();
        // Heel
        ctx.beginPath();
        ctx.ellipse(0, 26, 12, 14, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }

      // Ominous silhouette in background
      ctx.fillStyle = '#020306';
      ctx.fillRect(vanishingX - 22, vanishingY - 70, 44, 75);
      ctx.beginPath();
      ctx.arc(vanishingX, vanishingY - 80, 16, 0, Math.PI * 2);
      ctx.fill();

    } else if (isMinhFlashlight) {
      // SCENE 5: Minh Holding Flashlight in Dense Fog & Camcorder [REC] HUD
      ctx.fillStyle = '#03050C';
      ctx.fillRect(0, 0, w, h);

      // Character Minh from behind
      const charX = w * 0.32;
      const charY = h * 0.72;
      ctx.fillStyle = '#1E293B'; // Jacket
      ctx.beginPath();
      ctx.ellipse(charX, charY, 70, 110, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#0F172A'; // Head
      ctx.beginPath();
      ctx.arc(charX, charY - 110, 42, 0, Math.PI * 2);
      ctx.fill();

      // Hand holding flashlight
      const flashX = charX + 65;
      const flashY = charY - 25;
      ctx.fillStyle = '#020617';
      ctx.fillRect(flashX - 15, flashY - 8, 30, 16);

      // Volumetric Flashlight Beam cutting through fog
      const beamGrad = ctx.createRadialGradient(flashX, flashY, 5, flashX + 300, flashY, 650);
      beamGrad.addColorStop(0, 'rgba(254, 240, 138, 0.95)');
      beamGrad.addColorStop(0.25, 'rgba(250, 204, 21, 0.45)');
      beamGrad.addColorStop(0.7, 'rgba(56, 189, 248, 0.15)');
      beamGrad.addColorStop(1, 'rgba(0,0,0,0)');

      ctx.fillStyle = beamGrad;
      ctx.beginPath();
      ctx.moveTo(flashX, flashY);
      ctx.lineTo(w + 100, flashY - 260);
      ctx.lineTo(w + 100, flashY + 320);
      ctx.closePath();
      ctx.fill();

      // Camcorder HUD Overlay [REC]
      ctx.fillStyle = '#EF4444';
      ctx.beginPath();
      ctx.arc(45, 45, 10, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = '#FFFFFF';
      ctx.font = 'bold 16px monospace';
      ctx.fillText('REC ● 00:04:12', 65, 50);
      ctx.fillText('BAT: 85% [■■■□]', w - 160, 50);

      // Rule of thirds grid lines
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.12)';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(w * 0.33, 0); ctx.lineTo(w * 0.33, h);
      ctx.moveTo(w * 0.66, 0); ctx.lineTo(w * 0.66, h);
      ctx.moveTo(0, h * 0.33); ctx.lineTo(w, h * 0.33);
      ctx.moveTo(0, h * 0.66); ctx.lineTo(w, h * 0.66);
      ctx.stroke();

    } else if (isDoorOpen) {
      // SCENE 6: Wooden Door Creaking Open & Dusty Room with Tilted Frames
      ctx.fillStyle = '#03050B';
      ctx.fillRect(0, 0, w, h);

      // Doorframe
      const dfX = w * 0.28;
      const dfY = h * 0.20;
      const dfW = w * 0.50;
      const dfH = h * 0.65;
      ctx.strokeStyle = '#334155';
      ctx.lineWidth = 12;
      ctx.strokeRect(dfX, dfY, dfW, dfH);

      // Door open angle
      const doorOpen = Math.min(1.0, localT * 1.6);
      ctx.fillStyle = '#0F172A';
      ctx.beginPath();
      ctx.moveTo(dfX, dfY);
      ctx.lineTo(dfX + dfW * (1.0 - doorOpen * 0.65), dfY + 40 * doorOpen);
      ctx.lineTo(dfX + dfW * (1.0 - doorOpen * 0.65), dfY + dfH - 20 * doorOpen);
      ctx.lineTo(dfX, dfY + dfH);
      ctx.closePath();
      ctx.fill();

      // Interior dark room revealed with tilted picture frame
      ctx.save();
      ctx.translate(dfX + dfW * 0.5, dfY + dfH * 0.35);
      ctx.rotate(-0.16);
      ctx.fillStyle = '#78350F';
      ctx.fillRect(-45, -55, 90, 110);
      ctx.fillStyle = '#FEF3C7';
      ctx.fillRect(-38, -48, 76, 96);
      ctx.restore();

      // Floating illuminated dust motes
      ctx.fillStyle = 'rgba(254, 240, 138, 0.7)';
      for (let m = 0; m < 30; m++) {
        const dx = (m * 47 + globalT * 12) % w;
        const dy = (m * 73 + globalT * 8) % h;
        ctx.beginPath();
        ctx.arc(dx, dy, (m % 3) + 1.2, 0, Math.PI * 2);
        ctx.fill();
      }

    } else if (isFamilyPhoto) {
      // SCENE 7: Extreme Close-Up of Scratched Family Portrait
      ctx.fillStyle = '#050404';
      ctx.fillRect(0, 0, w, h);

      // Oval antique picture frame
      const cx = w * 0.5;
      const cy = h * 0.50;
      const frameR = Math.min(w, h) * 0.38;

      ctx.strokeStyle = '#78350F';
      ctx.lineWidth = 22;
      ctx.beginPath();
      ctx.arc(cx, cy, frameR, 0, Math.PI * 2);
      ctx.stroke();

      // Sepia photograph background
      ctx.fillStyle = '#D6C7A1';
      ctx.beginPath();
      ctx.arc(cx, cy, frameR - 11, 0, Math.PI * 2);
      ctx.fill();

      // Three family silhouettes in photo (Father, Mother, Little Girl)
      ctx.fillStyle = '#3F2D20';
      // Father
      ctx.beginPath();
      ctx.ellipse(cx - 75, cy - 20, 32, 50, 0, 0, Math.PI * 2);
      ctx.fill();
      // Mother
      ctx.beginPath();
      ctx.ellipse(cx + 75, cy - 10, 30, 48, 0, 0, Math.PI * 2);
      ctx.fill();
      // Little Girl in center foreground
      ctx.beginPath();
      ctx.ellipse(cx, cy + 35, 26, 42, 0, 0, Math.PI * 2);
      ctx.fill();

      // VIOLENT CLAW SCRATCH MARKS GOUGING THE GIRL'S FACE
      ctx.strokeStyle = '#180202';
      ctx.lineWidth = 5;
      ctx.beginPath();
      ctx.moveTo(cx - 32, cy + 12);
      ctx.lineTo(cx + 34, cy + 62);
      ctx.moveTo(cx - 24, cy + 6);
      ctx.lineTo(cx + 28, cy + 58);
      ctx.moveTo(cx - 15, cy + 2);
      ctx.lineTo(cx + 38, cy + 50);
      ctx.moveTo(cx + 28, cy + 10);
      ctx.lineTo(cx - 30, cy + 55);
      ctx.stroke();

    } else if (isWhisperShadow) {
      // SCENE 8: Dying Flashlight & Shadows Gathering Behind Minh
      ctx.fillStyle = '#020306';
      ctx.fillRect(0, 0, w, h);

      const cx = w * 0.5;
      const cy = h * 0.65;

      // Flashlight dying stutter
      const strob = Math.random() > 0.35 ? 0.8 : 0.08;
      const dyingBeam = ctx.createRadialGradient(cx, cy - 120, 10, cx, cy - 120, 280);
      dyingBeam.addColorStop(0, `rgba(254, 240, 138, ${strob})`);
      dyingBeam.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = dyingBeam;
      ctx.beginPath();
      ctx.arc(cx, cy - 120, 280, 0, Math.PI * 2);
      ctx.fill();

      // Minh head from behind looking nervous
      ctx.fillStyle = '#090D1A';
      ctx.beginPath();
      ctx.arc(cx, cy - 60, 52, 0, Math.PI * 2);
      ctx.fill();

      // Whisper soundwaves emitting behind his neck
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.4)';
      ctx.lineWidth = 2.5;
      for (let s = 1; s <= 4; s++) {
        const sr = (globalT * 40 + s * 30) % 140;
        ctx.beginPath();
        ctx.arc(cx, cy - 70, sr, Math.PI * 0.7, Math.PI * 1.3);
        ctx.stroke();
      }

    } else if (isLockedDoor) {
      // SCENE 9: Locked Under-Stair Door with Deep Claw Marks from Inside
      ctx.fillStyle = '#05070E';
      ctx.fillRect(0, 0, w, h);

      // Diagonal wooden stairs overhead
      ctx.fillStyle = '#0F172A';
      ctx.beginPath();
      ctx.moveTo(0, h * 0.15);
      ctx.lineTo(w, h * 0.55);
      ctx.lineTo(w, 0);
      ctx.lineTo(0, 0);
      ctx.closePath();
      ctx.fill();

      // Small wooden door under stairs
      const drX = w * 0.22;
      const drY = h * 0.42;
      const drW = w * 0.56;
      const drH = h * 0.48;
      ctx.fillStyle = '#1E293B';
      ctx.fillRect(drX, drY, drW, drH);
      ctx.strokeStyle = '#020617';
      ctx.lineWidth = 6;
      ctx.strokeRect(drX, drY, drW, drH);

      // Deep Claw Marks gouging outward through wood
      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 4.5;
      for (let c = 0; c < 8; c++) {
        const sx = drX + 35 + c * 25;
        const sy = drY + 60 + (c % 3) * 25;
        ctx.beginPath();
        ctx.moveTo(sx, sy);
        ctx.lineTo(sx + 15, sy + 75);
        ctx.stroke();
      }

      // Rusted iron padlock on floor
      ctx.fillStyle = '#78350F';
      ctx.fillRect(drX + drW * 0.45, h * 0.88, 28, 24);
      ctx.strokeStyle = '#451A03';
      ctx.strokeRect(drX + drW * 0.45, h * 0.88, 28, 24);

    } else if (isDiary) {
      // SCENE 10: 50-Year-Old Yellowed Diary with Cursive Handwriting
      ctx.fillStyle = '#070503';
      ctx.fillRect(0, 0, w, h);

      // Wooden desk
      ctx.fillStyle = '#1C1917';
      ctx.fillRect(0, 0, w, h);

      // Open Diary (leather book binding)
      const bW = w * 0.78;
      const bH = h * 0.58;
      const bX = (w - bW) / 2;
      const bY = h * 0.22;

      ctx.fillStyle = '#451A03';
      ctx.fillRect(bX - 10, bY - 8, bW + 20, bH + 16);

      // Yellowed aged pages
      ctx.fillStyle = '#FEF3C7';
      ctx.fillRect(bX, bY, bW, bH);
      ctx.strokeStyle = '#D97706';
      ctx.lineWidth = 2;
      // Center spine seam
      ctx.beginPath();
      ctx.moveTo(bX + bW / 2, bY);
      ctx.lineTo(bX + bW / 2, bY + bH);
      ctx.stroke();

      // Cursive ink handwriting on page
      ctx.fillStyle = '#451A03';
      ctx.font = 'italic 16px "Times New Roman", serif';
      ctx.fillText('Ngày 17 tháng 10...', bX + 25, bY + 50);
      ctx.fillText('Con gái tôi vẫn ở trong phòng.', bX + 25, bY + 85);
      ctx.fillText('Tôi đã khóa cửa lại.', bX + 25, bY + 120);
      ctx.fillText('Đêm nào nó cũng khóc than...', bX + 25, bY + 155);
      ctx.fillStyle = '#B91C1C';
      ctx.fillText('Người chết không phải nó!', bX + 25, bY + 195);

    } else if (isFlashback) {
      // SCENE 11: Dutch Angle Dramatic Flashback Montage
      ctx.save();
      ctx.translate(w * 0.5, h * 0.5);
      ctx.rotate(-0.14); // Dutch angle tilt
      ctx.translate(-w * 0.5, -h * 0.5);

      ctx.fillStyle = '#1A0505'; // Blood red dark tone
      ctx.fillRect(-100, -100, w + 200, h + 200);

      // Shutter lines
      ctx.strokeStyle = 'rgba(0, 0, 0, 0.45)';
      ctx.lineWidth = 4;
      for (let y = 0; y < h; y += 12) {
        ctx.beginPath();
        ctx.moveTo(0, y);
        ctx.lineTo(w, y);
        ctx.stroke();
      }

      // Man slamming door silhouette
      ctx.fillStyle = '#000000';
      ctx.fillRect(w * 0.42, h * 0.3, 140, 280);
      // Weeping mother silhouette on knees
      ctx.beginPath();
      ctx.ellipse(w * 0.25, h * 0.72, 45, 35, 0, 0, Math.PI * 2);
      ctx.fill();

      ctx.restore();

    } else if (isWhiteWoman) {
      // SCENE 12: Woman in White with Long Black Hair at End of Corridor
      ctx.fillStyle = '#02040A';
      ctx.fillRect(0, 0, w, h);

      // Perspective Corridor lines
      const cx = w * 0.5;
      const cy = h * 0.38;
      ctx.strokeStyle = '#1E293B';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(cx, cy); ctx.lineTo(0, 0);
      ctx.moveTo(cx, cy); ctx.lineTo(w, 0);
      ctx.moveTo(cx, cy); ctx.lineTo(0, h);
      ctx.moveTo(cx, cy); ctx.lineTo(w, h);
      ctx.stroke();

      // Apparition of Woman in White Dress
      ctx.fillStyle = '#F8FAFC'; // White flowing gown
      ctx.beginPath();
      ctx.moveTo(cx - 24, cy - 20);
      ctx.lineTo(cx + 24, cy - 20);
      ctx.lineTo(cx + 42, cy + 120);
      ctx.lineTo(cx - 42, cy + 120);
      ctx.closePath();
      ctx.fill();

      // Long Jet-Black Hair completely covering face
      ctx.fillStyle = '#020617';
      ctx.beginPath();
      ctx.ellipse(cx, cy - 45, 22, 35, 0, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillRect(cx - 20, cy - 40, 40, 65); // Hair hangs down past shoulders

      // Spectral cyan glow
      const ghostGlow = ctx.createRadialGradient(cx, cy + 40, 10, cx, cy + 40, 160);
      ghostGlow.addColorStop(0, 'rgba(56, 189, 248, 0.45)');
      ghostGlow.addColorStop(1, 'rgba(0,0,0,0)');
      ctx.fillStyle = ghostGlow;
      ctx.beginPath();
      ctx.arc(cx, cy + 40, 160, 0, Math.PI * 2);
      ctx.fill();

    } else if (isChase) {
      // SCENE 13: Frantic Chase through Endless Slamming Doors
      const shakeX = (Math.sin(globalT * 35) + Math.cos(globalT * 42)) * 6;
      const shakeY = (Math.cos(globalT * 38)) * 4;

      ctx.save();
      ctx.translate(shakeX, shakeY);

      ctx.fillStyle = '#0A0505';
      ctx.fillRect(-20, -20, w + 40, h + 40);

      // Radial speed blur lines
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.28)';
      ctx.lineWidth = 2.5;
      for (let a = 0; a < Math.PI * 2; a += Math.PI / 8) {
        ctx.beginPath();
        ctx.moveTo(w * 0.5, h * 0.5);
        ctx.lineTo(w * 0.5 + Math.cos(a) * w, h * 0.5 + Math.sin(a) * h);
        ctx.stroke();
      }

      // Slamming Door Frames on sides
      ctx.fillStyle = '#1C1917';
      ctx.fillRect(0, h * 0.2, 70, h * 0.65);
      ctx.fillRect(w - 70, h * 0.2, 70, h * 0.65);

      ctx.restore();

    } else if (isMirror) {
      // SCENE 14: Mirror Reflection Reveal with Bruised Little Girl Behind Minh
      ctx.fillStyle = '#030408';
      ctx.fillRect(0, 0, w, h);

      // Ornate oval mirror
      const mx = w * 0.5;
      const my = h * 0.48;
      const mrX = w * 0.36;
      const mrY = h * 0.32;

      ctx.strokeStyle = '#78350F';
      ctx.lineWidth = 18;
      ctx.beginPath();
      ctx.ellipse(mx, my, mrX, mrY, 0, 0, Math.PI * 2);
      ctx.stroke();

      // Mirror surface reflection
      ctx.fillStyle = '#0F172A';
      ctx.beginPath();
      ctx.ellipse(mx, my, mrX - 9, mrY - 9, 0, 0, Math.PI * 2);
      ctx.fill();

      // Minh in mirror reflection (foreground left)
      ctx.fillStyle = '#E2E8F0';
      ctx.beginPath();
      ctx.arc(mx - 45, my + 40, 48, 0, Math.PI * 2);
      ctx.fill();

      // Pale bruised Ghost Girl looming right over his shoulder
      const gx = mx + 38;
      const gy = my - 15;
      ctx.fillStyle = '#94A3B8'; // Pale cyan-grey flesh
      ctx.beginPath();
      ctx.arc(gx, gy, 42, 0, Math.PI * 2);
      ctx.fill();

      // Sunken bruised eyes
      ctx.fillStyle = '#0F172A';
      ctx.beginPath();
      ctx.ellipse(gx - 14, gy, 8, 11, 0, 0, Math.PI * 2);
      ctx.ellipse(gx + 14, gy, 8, 11, 0, 0, Math.PI * 2);
      ctx.fill();

      // Bruise marks
      ctx.fillStyle = 'rgba(88, 28, 135, 0.55)';
      ctx.beginPath();
      ctx.ellipse(gx - 20, gy + 15, 12, 8, 0.4, 0, Math.PI * 2);
      ctx.fill();

    } else if (isTwist) {
      // SCENE 15: The Plot Twist — Photograph Inscription "Con gái yêu - Minh"
      ctx.fillStyle = '#080303';
      ctx.fillRect(0, 0, w, h);

      // Back of vintage photograph card
      const cW = w * 0.82;
      const cH = h * 0.52;
      const cX = (w - cW) / 2;
      const cY = h * 0.24;

      ctx.fillStyle = '#D6C7A1';
      ctx.fillRect(cX, cY, cW, cH);
      ctx.strokeStyle = '#574130';
      ctx.lineWidth = 3;
      ctx.strokeRect(cX, cY, cW, cH);

      // Shockwave ring on reveal
      const ringR = (globalT * 90) % (w * 0.8);
      ctx.strokeStyle = 'rgba(239, 68, 68, 0.5)';
      ctx.lineWidth = 4;
      ctx.beginPath();
      ctx.arc(w * 0.5, h * 0.5, ringR, 0, Math.PI * 2);
      ctx.stroke();

      // Handwritten cursive twist text
      ctx.fillStyle = '#1C1917';
      ctx.font = 'bold 28px "Times New Roman", serif';
      ctx.textAlign = 'center';
      ctx.fillText('“Con gái yêu – Minh”', w * 0.5, cY + cH * 0.45);
      ctx.font = 'italic 18px "Times New Roman", serif';
      ctx.fillText('1974', w * 0.5, cY + cH * 0.62);
      ctx.textAlign = 'left';

    } else if (isMorning) {
      // SCENE 16: Silent Morning After & Smiling Portrait on the Altar
      const skyGrad = ctx.createLinearGradient(0, 0, 0, h);
      skyGrad.addColorStop(0, '#0F172A');
      skyGrad.addColorStop(0.5, '#334155');
      skyGrad.addColorStop(1, '#64748B');
      ctx.fillStyle = skyGrad;
      ctx.fillRect(0, 0, w, h);

      // Cool morning window slats / God rays
      ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
      for (let b = 0; b < 6; b++) {
        ctx.beginPath();
        ctx.moveTo(w * 0.1, 0);
        ctx.lineTo(w * 0.35, 0);
        ctx.lineTo(w * 0.9, h);
        ctx.lineTo(w * 0.65, h);
        ctx.closePath();
        ctx.fill();
      }

      // Wooden Altar with New Framed Portrait
      const ax = w * 0.5;
      const ay = h * 0.55;
      ctx.fillStyle = '#1E1B18';
      ctx.fillRect(ax - 130, ay, 260, 30);
      ctx.fillRect(ax - 110, ay + 30, 220, 90);

      // The new framed photo: Minh smiling beside the girl
      ctx.fillStyle = '#78350F';
      ctx.fillRect(ax - 55, ay - 90, 110, 85);
      ctx.fillStyle = '#F8FAFC';
      ctx.fillRect(ax - 48, ay - 83, 96, 71);

      // Thin spiral of incense smoke
      ctx.strokeStyle = 'rgba(241, 245, 249, 0.45)';
      ctx.lineWidth = 2.5;
      ctx.beginPath();
      ctx.moveTo(ax, ay);
      for (let y = 0; y < 140; y += 10) {
        const sx = ax + Math.sin(globalT * 3 + y * 0.1) * 12;
        ctx.lineTo(sx, ay - y);
      }
      ctx.stroke();

    } else {
      // General Atmospheric Fallback
      const skyGrad = ctx.createLinearGradient(0, 0, 0, h);
      skyGrad.addColorStop(0, '#04040A');
      skyGrad.addColorStop(0.65, '#0B0D18');
      skyGrad.addColorStop(1, '#020306');
      ctx.fillStyle = skyGrad;
      ctx.fillRect(0, 0, w, h);

      // Full Moon with Halo
      const moonX = w * 0.72;
      const moonY = h * 0.20;
      const moonR = Math.min(w, h) * 0.10;

      const halo = ctx.createRadialGradient(moonX, moonY, moonR * 0.8, moonX, moonY, moonR * 2.8);
      halo.addColorStop(0, 'rgba(254, 243, 199, 0.45)');
      halo.addColorStop(0.5, 'rgba(254, 243, 199, 0.12)');
      halo.addColorStop(1, 'rgba(0, 0, 0, 0)');
      ctx.fillStyle = halo;
      ctx.beginPath();
      ctx.arc(moonX, moonY, moonR * 2.8, 0, Math.PI * 2);
      ctx.fill();

      ctx.fillStyle = '#FEF3C7';
      ctx.beginPath();
      ctx.arc(moonX, moonY, moonR, 0, Math.PI * 2);
      ctx.fill();

      // Ancient Wooden House Silhouette
      const houseY = h * 0.52;
      ctx.fillStyle = '#06070D';
      ctx.fillRect(w * 0.15, houseY, w * 0.70, h * 0.28);
      ctx.beginPath();
      ctx.moveTo(w * 0.08, houseY + 15);
      ctx.lineTo(w * 0.50, houseY - 90);
      ctx.lineTo(w * 0.92, houseY + 15);
      ctx.closePath();
      ctx.fill();
    }

    ctx.restore();
  }

  /**
   * Domain Visual: Medical Doctor & Expert Presenter (2D Rigged Lip-Sync & Natural Idle)
   */
  private static renderPresenterVisual(
    ctx: CanvasRenderingContext2D,
    w: number,
    h: number,
    _scene: SceneItem,
    _localT: number,
    globalT: number,
    isSpeaking: boolean
  ) {
    ctx.save();

    // Studio Background Gradient
    const bgGrad = ctx.createLinearGradient(0, 0, 0, h);
    bgGrad.addColorStop(0, '#0F172A');
    bgGrad.addColorStop(1, '#020617');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, w, h);

    const cx = w * 0.5;
    const cy = h * 0.55;

    // Doctor Body Idle Breathing
    const breath = Math.sin(globalT * 2.2) * 4;

    ctx.save();
    ctx.translate(cx, cy + breath);

    // Torso / White Medical Coat
    ctx.fillStyle = '#F8FAFC';
    ctx.beginPath();
    ctx.moveTo(-90, 80);
    ctx.lineTo(90, 80);
    ctx.lineTo(110, 260);
    ctx.lineTo(-110, 260);
    ctx.closePath();
    ctx.fill();

    // Inner Blue Scrubs Collar
    ctx.fillStyle = '#0284C7';
    ctx.beginPath();
    ctx.moveTo(-35, 80);
    ctx.lineTo(0, 140);
    ctx.lineTo(35, 80);
    ctx.closePath();
    ctx.fill();

    // Medical Stethoscope
    ctx.strokeStyle = '#475569';
    ctx.lineWidth = 6;
    ctx.beginPath();
    ctx.moveTo(-45, 90);
    ctx.quadraticCurveTo(-35, 175, 0, 185);
    ctx.quadraticCurveTo(35, 175, 45, 90);
    ctx.stroke();

    // Stethoscope Bell
    ctx.fillStyle = '#94A3B8';
    ctx.beginPath();
    ctx.arc(0, 185, 12, 0, Math.PI * 2);
    ctx.fill();

    // Head with Natural Tilting
    const headTilt = Math.sin(globalT * 1.8) * 0.04;
    ctx.save();
    ctx.translate(0, 25);
    ctx.rotate(headTilt);

    // Face / Head
    ctx.fillStyle = '#FBBF24';
    ctx.beginPath();
    ctx.ellipse(0, 0, 52, 64, 0, 0, Math.PI * 2);
    ctx.fill();

    // Hair
    ctx.fillStyle = '#1E293B';
    ctx.beginPath();
    ctx.arc(0, -18, 54, Math.PI, 0);
    ctx.fill();

    // Eyes with Blinking
    const isBlinking = (globalT % 3.6) < 0.16;
    ctx.fillStyle = '#0F172A';
    if (isBlinking) {
      ctx.lineWidth = 3;
      ctx.strokeStyle = '#0F172A';
      ctx.beginPath();
      ctx.moveTo(-28, 0);
      ctx.lineTo(-12, 0);
      ctx.moveTo(12, 0);
      ctx.lineTo(28, 0);
      ctx.stroke();
    } else {
      ctx.beginPath();
      ctx.arc(-20, 0, 5, 0, Math.PI * 2);
      ctx.arc(20, 0, 5, 0, Math.PI * 2);
      ctx.fill();
    }

    // Glasses
    ctx.strokeStyle = '#0F172A';
    ctx.lineWidth = 3;
    ctx.strokeRect(-32, -10, 24, 20);
    ctx.strokeRect(8, -10, 24, 20);
    ctx.beginPath();
    ctx.moveTo(-8, 0);
    ctx.lineTo(8, 0);
    ctx.stroke();

    // Talking Mouth Lip-Sync
    if (isSpeaking) {
      const mouthOpen = Math.sin(globalT * 18) > 0;
      if (mouthOpen) {
        ctx.fillStyle = '#881337';
        ctx.beginPath();
        ctx.ellipse(0, 32, 10, 8, 0, 0, Math.PI * 2);
        ctx.fill();
      } else {
        ctx.strokeStyle = '#881337';
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.moveTo(-10, 32);
        ctx.lineTo(10, 32);
        ctx.stroke();
      }
    } else {
      ctx.strokeStyle = '#881337';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.arc(0, 28, 12, 0.2, Math.PI - 0.2);
      ctx.stroke();
    }

    ctx.restore(); // Head
    ctx.restore(); // Body

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
