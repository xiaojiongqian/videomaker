import React from 'react';
import {
  AbsoluteFill,
  OffthreadVideo,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import type {CaptionCue, ExplainerScene, VideoInputProps} from './types';

const containerStyle: React.CSSProperties = {
  background:
    'radial-gradient(circle at top left, rgba(46,88,255,0.22), transparent 28%), linear-gradient(135deg, #08101d 0%, #11192a 42%, #1b2234 100%)',
  color: '#f5f7fb',
  fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
};

const cardStyle: React.CSSProperties = {
  borderRadius: 28,
  overflow: 'hidden',
  boxShadow: '0 22px 60px rgba(0, 0, 0, 0.28)',
};

const findCurrentCaption = (captions: CaptionCue[], currentMs: number) => {
  return captions.find((cue) => currentMs >= cue.startMs && currentMs < cue.endMs) ?? null;
};

const currentSceneIndex = (scenes: ExplainerScene[], currentMs: number) => {
  return scenes.findIndex((scene) => currentMs >= scene.startMs && currentMs < scene.endMs);
};

const msToStartFrame = (ms: number, fps: number) => {
  return Math.max(0, Math.round((ms / 1000) * fps));
};

const msToDurationInFrames = (startMs: number, endMs: number, fps: number) => {
  return Math.max(1, Math.round(((endMs - startMs) / 1000) * fps));
};

const shorten = (value: string) => {
  const compact = value.replace(/\s+/g, ' ').trim();
  return compact.length > 18 ? `${compact.slice(0, 18)}...` : compact;
};

const AnimatedDiagram: React.FC<{scene: ExplainerScene}> = ({scene}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const nodes = scene.bullets.slice(0, 3);
  const centerX = 220;
  const centerY = 170;
  const positions = [
    {x: 78, y: 70},
    {x: 420, y: 70},
    {x: 420, y: 270},
  ];

  return (
    <div
      style={{
        ...cardStyle,
        position: 'relative',
        minHeight: 340,
        padding: 22,
        border: '1px solid rgba(255, 255, 255, 0.1)',
        background:
          'linear-gradient(180deg, rgba(255,255,255,0.06), rgba(255,255,255,0.02)), rgba(7, 13, 24, 0.88)',
      }}
    >
      <svg viewBox="0 0 520 320" style={{width: '100%', height: 320, display: 'block'}}>
        <defs>
          <linearGradient id="accentLine" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#8fe0d1" />
            <stop offset="100%" stopColor="#6db8ff" />
          </linearGradient>
          <linearGradient id="panelFill" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#1d4ed8" stopOpacity="0.32" />
            <stop offset="100%" stopColor="#0f172a" stopOpacity="0.92" />
          </linearGradient>
        </defs>

        <rect x="0" y="0" width="520" height="320" rx="24" fill="url(#panelFill)" />
        <circle cx={centerX} cy={centerY} r="84" fill="rgba(109, 184, 255, 0.10)" />
        <rect
          x={centerX - 88}
          y={centerY - 42}
          width="176"
          height="84"
          rx="22"
          fill="rgba(8, 16, 29, 0.92)"
          stroke="rgba(109, 184, 255, 0.28)"
        />
        <text
          x={centerX}
          y={centerY - 4}
          textAnchor="middle"
          fill="#f5f7fb"
          fontSize="20"
          fontWeight="700"
          fontFamily="Arial, sans-serif"
        >
          {shorten(scene.title)}
        </text>
        <text
          x={centerX}
          y={centerY + 22}
          textAnchor="middle"
          fill="rgba(152, 199, 255, 0.9)"
          fontSize="13"
          fontFamily="Arial, sans-serif"
        >
          Sync Explainer
        </text>

        {positions.map((pos, index) => {
          const reveal = spring({
            frame: Math.max(0, frame - index * 6),
            fps,
            config: {damping: 18, stiffness: 110},
          });
          const label = nodes[index] ?? `要点 ${index + 1}`;
          const isLeft = pos.x < centerX;
          const path = isLeft
            ? `M ${centerX - 88} ${centerY} C 154 ${centerY - 12}, 140 ${pos.y + 34}, ${pos.x + 54} ${pos.y + 34}`
            : `M ${centerX + 88} ${centerY} C 330 ${centerY - 10}, 346 ${pos.y + 34}, ${pos.x - 12} ${pos.y + 34}`;

          return (
            <g
              key={`${scene.id}-node-${index}`}
              opacity={interpolate(reveal, [0, 1], [0, 1])}
              transform={`translate(0 ${interpolate(reveal, [0, 1], [12, 0])})`}
            >
              <path
                d={path}
                fill="none"
                stroke="url(#accentLine)"
                strokeWidth="4"
                strokeLinecap="round"
                strokeDasharray="320"
                strokeDashoffset={interpolate(reveal, [0, 1], [320, 0])}
              />
              <rect
                x={pos.x}
                y={pos.y}
                width="112"
                height="68"
                rx="18"
                fill="rgba(8, 16, 29, 0.94)"
                stroke="rgba(143, 224, 209, 0.30)"
              />
              <circle cx={pos.x + 24} cy={pos.y + 24} r="10" fill="#8fe0d1" />
              <text
                x={pos.x + 44}
                y={pos.y + 30}
                fill="#f5f7fb"
                fontSize="16"
                fontWeight="700"
                fontFamily="Arial, sans-serif"
              >
                {`0${index + 1}`}
              </text>
              <text
                x={pos.x + 16}
                y={pos.y + 54}
                fill="rgba(219, 234, 254, 0.92)"
                fontSize="12"
                fontFamily="Arial, sans-serif"
              >
                {shorten(label)}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
};

const ScenePanel: React.FC<{
  scene: ExplainerScene;
  caption: CaptionCue | null;
}> = ({scene, caption}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const rise = spring({
    frame,
    fps,
    config: {damping: 18, stiffness: 120},
  });
  const fade = interpolate(frame, [0, 12], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <AbsoluteFill
      style={{
        padding: 48,
        gap: 28,
        justifyContent: 'space-between',
        opacity: fade,
        transform: `translateY(${interpolate(rise, [0, 1], [22, 0])}px)`,
      }}
    >
      <div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
        <div
          style={{
            alignSelf: 'flex-start',
            padding: '8px 14px',
            borderRadius: 999,
            backgroundColor: 'rgba(109, 184, 255, 0.16)',
            border: '1px solid rgba(109, 184, 255, 0.25)',
            color: '#98c7ff',
            fontSize: 24,
            letterSpacing: 1.2,
          }}
        >
          SYNC EXPLAINER
        </div>
        <div style={{fontSize: 64, fontWeight: 700, lineHeight: 1.1}}>{scene.title}</div>
        <div style={{display: 'flex', flexDirection: 'column', gap: 14}}>
          {scene.bullets.map((bullet, index) => {
            const itemSpring = spring({
              frame: Math.max(0, frame - index * 6),
              fps,
              config: {damping: 20, stiffness: 100},
            });
            return (
              <div
                key={`${scene.id}-${index}`}
                style={{
                  display: 'flex',
                  gap: 16,
                  alignItems: 'flex-start',
                  opacity: interpolate(itemSpring, [0, 1], [0, 1]),
                  transform: `translateX(${interpolate(itemSpring, [0, 1], [24, 0])}px)`,
                }}
              >
                <div
                  style={{
                    width: 12,
                    height: 12,
                    marginTop: 14,
                    borderRadius: 999,
                    backgroundColor: '#8fe0d1',
                    boxShadow: '0 0 0 8px rgba(143, 224, 209, 0.14)',
                    flexShrink: 0,
                  }}
                />
                <div style={{fontSize: 34, lineHeight: 1.45, color: 'rgba(245, 247, 251, 0.94)'}}>
                  {bullet}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div style={{display: 'flex', flexDirection: 'column', gap: 18}}>
        {scene.assetPublicPath ? (
          <div
            style={{
              ...cardStyle,
              padding: 20,
              background:
                'linear-gradient(180deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.02))',
              border: '1px solid rgba(255, 255, 255, 0.1)',
            }}
          >
            <img
              src={staticFile(scene.assetPublicPath)}
              style={{
                width: '100%',
                maxHeight: 360,
                objectFit: 'contain',
                display: 'block',
                transform: `scale(${interpolate(rise, [0, 1], [0.94, 1])})`,
              }}
            />
          </div>
        ) : (
          <AnimatedDiagram scene={scene} />
        )}

        <div
          style={{
            ...cardStyle,
            padding: 24,
            border: '1px solid rgba(255, 255, 255, 0.1)',
            backgroundColor: 'rgba(7, 13, 24, 0.78)',
          }}
        >
          <div style={{fontSize: 20, color: 'rgba(152, 199, 255, 0.92)', marginBottom: 10}}>
            当前音频
          </div>
          <div style={{fontSize: 28, lineHeight: 1.5, color: '#f5f7fb'}}>
            {caption?.text ?? scene.note ?? '当前段落没有匹配到字幕，建议在 script.md 中显式加 @range。'}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};

export const SplitExplainer: React.FC<VideoInputProps> = ({
  title,
  videoPublicPath,
  videoPanelRatio,
  scenes,
  captions,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const currentMs = (frame / fps) * 1000;
  const activeCaption = findCurrentCaption(captions, currentMs);
  const sceneIndex = currentSceneIndex(scenes, currentMs);

  const safeVideoRatio = Math.min(0.78, Math.max(0.35, videoPanelRatio));
  const activeScene = scenes[Math.max(0, sceneIndex)] ?? null;

  return (
    <AbsoluteFill style={containerStyle}>
      <div
        style={{
          display: 'flex',
          height: '100%',
          gap: 28,
          padding: 28,
        }}
      >
        <div style={{width: `${safeVideoRatio * 100}%`, position: 'relative'}}>
          <div
            style={{
              ...cardStyle,
              width: '100%',
              height: '100%',
              border: '1px solid rgba(255, 255, 255, 0.08)',
              backgroundColor: '#05070c',
            }}
          >
            <OffthreadVideo
              src={staticFile(videoPublicPath)}
              style={{width: '100%', height: '100%', objectFit: 'cover'}}
            />
          </div>
          <div
            style={{
              position: 'absolute',
              top: 20,
              left: 20,
              ...cardStyle,
              padding: '12px 16px',
              backgroundColor: 'rgba(6, 10, 19, 0.7)',
              border: '1px solid rgba(255, 255, 255, 0.12)',
              fontSize: 26,
              fontWeight: 600,
            }}
          >
            {title}
          </div>
        </div>

        <div
          style={{
            width: `${(1 - safeVideoRatio) * 100}%`,
            position: 'relative',
            ...cardStyle,
            border: '1px solid rgba(255, 255, 255, 0.08)',
            background:
              'linear-gradient(180deg, rgba(17, 28, 44, 0.92) 0%, rgba(11, 17, 28, 0.96) 100%)',
          }}
        >
          {scenes.map((scene) => {
            const from = msToStartFrame(scene.startMs, fps);
            const durationInFrames = msToDurationInFrames(scene.startMs, scene.endMs, fps);
            return (
              <Sequence
                key={scene.id}
                from={from}
                durationInFrames={durationInFrames}
              >
                <ScenePanel scene={scene} caption={activeCaption} />
              </Sequence>
            );
          })}
          {!activeScene ? (
            <AbsoluteFill
              style={{
                alignItems: 'center',
                justifyContent: 'center',
                padding: 48,
                textAlign: 'center',
                fontSize: 36,
                color: 'rgba(245, 247, 251, 0.85)',
              }}
            >
              没有可用场景。请确认 script.md 至少包含一段正文或标题。
            </AbsoluteFill>
          ) : null}
        </div>
      </div>
    </AbsoluteFill>
  );
};
