import type { ComfyApp } from '@comfyorg/comfyui-frontend-types';

type HostNode = ComfyApp['rootGraph']['nodes'][number];
type HostWidget = NonNullable<HostNode['widgets']>[number];

/** ComfyUI's widgets, with the removal hook the published types do not describe. */
export type Widget = HostWidget & {
  onRemove?: () => void;
};

export type CanvasNode = {
  widgets?: Widget[];
  properties: HostNode['properties'] & {
    conditionalValues?: Record<string, Widget['value']>;
  };
} & HostNode;
