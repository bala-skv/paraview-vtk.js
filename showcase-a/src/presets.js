// Transfer-function presets. Control points are on a 0..1 scale and are mapped
// to the dataset's scalar range when applied (see viewer.applyPreset).
export const PRESETS = {
  Grayscale: {
    color: [[0, 0, 0, 0], [1, 1, 1, 1]],
    opacity: [[0, 0], [0.15, 0], [1, 0.8]],
  },
  Bone: {
    color: [[0, 0, 0, 0], [0.3, 0.55, 0.25, 0.15], [0.6, 0.9, 0.85, 0.75], [1, 1, 1, 0.95]],
    opacity: [[0, 0], [0.25, 0], [0.4, 0.15], [0.7, 0.5], [1, 0.9]],
  },
  'Soft tissue': {
    color: [[0, 0, 0, 0], [0.2, 0.55, 0.25, 0.15], [0.45, 0.9, 0.7, 0.6], [1, 1, 1, 0.95]],
    opacity: [[0, 0], [0.1, 0], [0.3, 0.25], [0.6, 0.35], [1, 0.6]],
  },
  Vessel: {
    color: [[0, 0, 0, 0], [0.3, 0.6, 0, 0], [0.6, 1, 0.4, 0.1], [1, 1, 1, 0.8]],
    opacity: [[0, 0], [0.35, 0], [0.5, 0.5], [1, 1]],
  },
};

export const PRESET_NAMES = Object.keys(PRESETS);
