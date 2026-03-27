import {Composition} from 'remotion';
import {SplitExplainer} from './SplitExplainer';
import type {VideoInputProps} from './types';

const defaultProps: VideoInputProps = {
  title: 'Split Explainer',
  fps: 30,
  width: 1920,
  height: 1080,
  totalFrames: 900,
  videoPublicPath: '',
  videoPanelRatio: 0.58,
  scenes: [],
  captions: [],
};

export const RemotionRoot = () => {
  return (
    <Composition
      id="SplitExplainer"
      component={SplitExplainer}
      defaultProps={defaultProps}
      durationInFrames={defaultProps.totalFrames}
      fps={defaultProps.fps}
      width={defaultProps.width}
      height={defaultProps.height}
      calculateMetadata={({props}) => {
        return {
          durationInFrames: props.totalFrames,
          fps: props.fps,
          width: props.width,
          height: props.height,
        };
      }}
    />
  );
};
