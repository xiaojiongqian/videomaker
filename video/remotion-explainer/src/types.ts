export type CaptionCue = {
  startMs: number;
  endMs: number;
  text: string;
};

export type ExplainerScene = {
  id: string;
  title: string;
  bullets: string[];
  startMs: number;
  endMs: number;
  assetPublicPath?: string;
  note?: string;
};

export type VideoInputProps = {
  title: string;
  fps: number;
  width: number;
  height: number;
  totalFrames: number;
  videoPublicPath: string;
  videoPanelRatio: number;
  scenes: ExplainerScene[];
  captions: CaptionCue[];
};
