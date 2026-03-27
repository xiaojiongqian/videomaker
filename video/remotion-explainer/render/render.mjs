import {mkdir, readdir, readFile, rm, writeFile, copyFile} from 'node:fs/promises';
import {existsSync} from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
import {bundle} from '@remotion/bundler';
import {renderMedia, selectComposition} from '@remotion/renderer';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '..');
const publicRoot = path.join(projectRoot, 'public');
const defaultPlaywrightChrome =
  '/Users/vik.qian/Library/Caches/ms-playwright/chromium_headless_shell-1200/chrome-headless-shell-mac-arm64/chrome-headless-shell';

const usage = `Usage:
  node render/render.mjs \\
    --video /abs/path/input.mp4 \\
    --srt /abs/path/input.srt \\
    --script /abs/path/script.md \\
    --out /abs/path/output.mp4 \\
    [--images-dir /abs/path/doc/images] \\
    [--fps 30] [--width 1920] [--height 1080] [--video-panel-ratio 0.58]

Optional script.md annotations:
  ## Scene Title
  @range 00:01:05-00:01:30
  - bullet 1
  - bullet 2
  ![diagram](./doc/images/figure.svg)
`;

const parseArgs = (argv) => {
  const result = {};
  for (let i = 0; i < argv.length; i += 1) {
    const arg = argv[i];
    if (!arg.startsWith('--')) {
      continue;
    }
    const key = arg.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith('--')) {
      result[key] = 'true';
      continue;
    }
    result[key] = next;
    i += 1;
  }
  return result;
};

const fail = (message) => {
  console.error(message);
  process.exit(1);
};

const resolveBrowserExecutable = () => {
  if (process.env.REMOTION_BROWSER_EXECUTABLE) {
    return process.env.REMOTION_BROWSER_EXECUTABLE;
  }
  if (existsSync(defaultPlaywrightChrome)) {
    return defaultPlaywrightChrome;
  }
  return null;
};

const ensureFile = (filePath, label) => {
  if (!filePath) {
    fail(`Missing required argument: ${label}\n\n${usage}`);
  }
};

const parseClock = (value) => {
  const match = value.trim().match(/^(?:(\d+):)?(\d{1,2}):(\d{2})(?:[,.](\d{1,3}))?$/);
  if (!match) {
    throw new Error(`Invalid time: ${value}`);
  }
  const [, hhRaw, mmRaw, ssRaw, msRaw] = match;
  const hh = Number(hhRaw ?? 0);
  const mm = Number(mmRaw);
  const ss = Number(ssRaw);
  const ms = Number((msRaw ?? '0').padEnd(3, '0'));
  return ((hh * 60 + mm) * 60 + ss) * 1000 + ms;
};

const formatId = (title, index) => {
  const slug = title
    .toLowerCase()
    .replace(/[^a-z0-9\u4e00-\u9fa5]+/g, '-')
    .replace(/^-+|-+$/g, '');
  return slug || `scene-${index + 1}`;
};

const parseSrt = (content) => {
  const normalized = content.replace(/\r/g, '');
  const blocks = normalized.split('\n\n').map((block) => block.trim()).filter(Boolean);
  return blocks
    .map((block) => {
      const lines = block.split('\n');
      const timeLine = lines.find((line) => line.includes('-->'));
      if (!timeLine) {
        return null;
      }
      const [start, end] = timeLine.split('-->').map((part) => part.trim());
      const textLines = lines.slice(lines.indexOf(timeLine) + 1).filter(Boolean);
      return {
        startMs: parseClock(start),
        endMs: parseClock(end),
        text: textLines.join(' ').trim(),
      };
    })
    .filter(Boolean);
};

const splitBullets = (text) => {
  return text
    .split(/[；。]/)
    .map((item) => item.trim())
    .filter(Boolean)
    .slice(0, 4);
};

const parseScript = async (scriptPath) => {
  const content = await readFile(scriptPath, 'utf8');
  const lines = content.replace(/\r/g, '').split('\n');
  const sections = [];
  let current = null;

  const pushCurrent = () => {
    if (!current) {
      return;
    }
    const bullets = current.bullets.length > 0
      ? current.bullets
      : splitBullets(current.body.join(' '));
    const title = current.title || bullets[0] || `Scene ${sections.length + 1}`;
    sections.push({
      title,
      bullets: bullets.length > 0 ? bullets : ['补充一段解释文本或项目符号。'],
      note: current.body.join(' ').trim(),
      range: current.range,
      assetHint: current.assetHint,
    });
    current = null;
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line || line === 'plaintext' || line.startsWith('```')) {
      continue;
    }
    if (line.startsWith('# ')) {
      pushCurrent();
      current = {title: line.slice(2).trim(), bullets: [], body: [], range: null, assetHint: null};
      continue;
    }
    if (line.startsWith('## ')) {
      pushCurrent();
      current = {title: line.slice(3).trim(), bullets: [], body: [], range: null, assetHint: null};
      continue;
    }
    if (!current) {
      current = {title: '', bullets: [], body: [], range: null, assetHint: null};
    }
    if (line.startsWith('@range ')) {
      const [startRaw, endRaw] = line.slice(7).split('-').map((part) => part.trim());
      if (startRaw && endRaw) {
        current.range = {startMs: parseClock(startRaw), endMs: parseClock(endRaw)};
      }
      continue;
    }
    if (line.startsWith('- ')) {
      current.bullets.push(line.slice(2).trim());
      continue;
    }
    const imageMatch = line.match(/!\[[^\]]*]\((.+)\)/);
    if (imageMatch) {
      current.assetHint = imageMatch[1].trim();
      continue;
    }
    current.body.push(line);
  }

  pushCurrent();
  return sections;
};

const listImages = async (imagesDir) => {
  if (!imagesDir) {
    return [];
  }
  const entries = await readdir(imagesDir, {withFileTypes: true});
  return entries
    .filter((entry) => entry.isFile())
    .map((entry) => path.join(imagesDir, entry.name))
    .filter((filePath) => /\.(svg|png|jpe?g|webp)$/i.test(filePath))
    .sort();
};

const probeVideo = (videoPath) => {
  const result = spawnSync(
    'ffprobe',
    [
      '-v',
      'error',
      '-show_entries',
      'format=duration',
      '-of',
      'default=noprint_wrappers=1:nokey=1',
      videoPath,
    ],
    {encoding: 'utf8'}
  );

  if (result.status !== 0) {
    fail(`ffprobe failed:\n${result.stderr}`);
  }

  return Number(result.stdout.trim());
};

const stageFile = async (sourcePath, targetPath) => {
  await copyFile(sourcePath, targetPath);
};

const resolveAssetFromHint = (assetHint, scriptPath) => {
  if (!assetHint) {
    return null;
  }
  if (path.isAbsolute(assetHint)) {
    return assetHint;
  }
  return path.resolve(path.dirname(scriptPath), assetHint);
};

const buildScenes = ({sections, images, scriptPath, durationMs}) => {
  if (sections.length === 0) {
    return [
      {
        id: 'scene-1',
        title: 'Split-screen explainer',
        bullets: ['请在 script.md 中添加标题、要点和可选 @range 时间段。'],
        startMs: 0,
        endMs: durationMs,
        note: '当前自动生成了一个默认场景。',
      },
    ];
  }

  const scenes = [];
  const defaultSpan = durationMs / sections.length;
  let lastEndMs = 0;

  sections.forEach((section, index) => {
    const startMs = section.range?.startMs ?? Math.round(index * defaultSpan);
    const endMs = section.range?.endMs ?? Math.round((index + 1) * defaultSpan);
    const resolvedHint = resolveAssetFromHint(section.assetHint, scriptPath);
    scenes.push({
      id: formatId(section.title, index),
      title: section.title,
      bullets: section.bullets.slice(0, 4),
      startMs: Math.max(lastEndMs, startMs),
      endMs: Math.max(lastEndMs + 1000, endMs),
      sourceAssetPath: resolvedHint ?? images[index] ?? null,
      note: section.note,
    });
    lastEndMs = scenes[scenes.length - 1].endMs;
  });

  scenes[0].startMs = 0;
  scenes[scenes.length - 1].endMs = durationMs;
  return scenes;
};

const main = async () => {
  const args = parseArgs(process.argv.slice(2));
  if (args.help === 'true') {
    console.log(usage);
    process.exit(0);
  }

  ensureFile(args.video, '--video');
  ensureFile(args.srt, '--srt');
  ensureFile(args.script, '--script');
  ensureFile(args.out, '--out');

  const fps = Number(args.fps ?? 30);
  const width = Number(args.width ?? 1920);
  const height = Number(args.height ?? 1080);
  const videoPanelRatio = Number(args['video-panel-ratio'] ?? 0.58);
  const browserExecutable = resolveBrowserExecutable();

  const durationSeconds = probeVideo(args.video);
  const durationMs = Math.round(durationSeconds * 1000);
  const totalFrames = Math.max(1, Math.round(durationSeconds * fps));
  const captions = parseSrt(await readFile(args.srt, 'utf8'));
  const sections = await parseScript(args.script);
  const images = await listImages(args['images-dir']);
  const scenes = buildScenes({sections, images, scriptPath: args.script, durationMs});

  const jobId = new Date().toISOString().replace(/[:.]/g, '-');
  const jobDir = path.join(publicRoot, 'jobs', jobId);
  await mkdir(jobDir, {recursive: true});

  const stagedVideoPath = path.join(jobDir, path.basename(args.video));
  await stageFile(args.video, stagedVideoPath);

  const stagedAssets = new Map();
  for (const scene of scenes) {
    if (!scene.sourceAssetPath || stagedAssets.has(scene.sourceAssetPath)) {
      continue;
    }
    const target = path.join(jobDir, path.basename(scene.sourceAssetPath));
    await stageFile(scene.sourceAssetPath, target);
    stagedAssets.set(scene.sourceAssetPath, target);
  }

  const inputProps = {
    title: path.basename(args.video, path.extname(args.video)),
    fps,
    width,
    height,
    totalFrames,
    videoPublicPath: path.relative(publicRoot, stagedVideoPath).replace(/\\/g, '/'),
    videoPanelRatio,
    captions,
    scenes: scenes.map((scene) => ({
      id: scene.id,
      title: scene.title,
      bullets: scene.bullets,
      startMs: scene.startMs,
      endMs: scene.endMs,
      note: scene.note,
      assetPublicPath: scene.sourceAssetPath
        ? path.relative(publicRoot, stagedAssets.get(scene.sourceAssetPath)).replace(/\\/g, '/')
        : undefined,
    })),
  };

  await mkdir(path.dirname(args.out), {recursive: true});
  const entryPoint = path.join(projectRoot, 'src', 'index.ts');
  const bundled = await bundle({
    entryPoint,
    webpackOverride: (config) => config,
  });
  const composition = await selectComposition({
    serveUrl: bundled,
    id: 'SplitExplainer',
    inputProps,
    browserExecutable,
  });

  await renderMedia({
    composition,
    serveUrl: bundled,
    codec: 'h264',
    outputLocation: args.out,
    inputProps,
    browserExecutable,
  });

  const manifestPath = path.join(jobDir, 'input-props.json');
  await writeFile(manifestPath, JSON.stringify(inputProps, null, 2), 'utf8');

  console.log(
    JSON.stringify(
      {
        output: args.out,
        manifest: manifestPath,
        scenes: inputProps.scenes.length,
        captions: inputProps.captions.length,
        durationSeconds,
      },
      null,
      2
    )
  );
};

main().catch(async (error) => {
  console.error(error);
  process.exitCode = 1;
  try {
    await rm(path.join(publicRoot, 'jobs', 'tmp'), {recursive: true, force: true});
  } catch {
    // noop
  }
});
