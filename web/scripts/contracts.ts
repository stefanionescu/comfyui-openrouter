import type { ComfyApp } from '@comfyorg/comfyui-frontend-types';

type HostNode = ComfyApp['rootGraph']['nodes'][number];
type HostWidget = NonNullable<HostNode['widgets']>[number];

/**
 * ComfyUI's dynamic widgets.
 * Checked on frontend 1.49.6: `inputSpec` carries the schema a widget was built from. The published types
 * do not describe it, so it is declared here.
 */
export type Widget = HostWidget & {
  inputSpec?: { options?: string[]; multiselect?: boolean; default?: unknown };
  onRemove?: () => void;
};

export type CanvasNode = {
  widgets?: Widget[];
  properties: HostNode['properties'] & {
    conditionalValues?: Record<string, Widget['value']>;
  };
} & HostNode;
