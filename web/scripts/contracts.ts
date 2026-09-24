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

/** One option of a dynamic dropdown, with the inputs it shows. */
export type DropdownOption = { key: string; inputs: { required?: Record<string, InputSpec> } };

/** An input as ComfyUI's node definition lists it: its type, then its options. */
type InputSpec = [string, { display_name?: string; options?: DropdownOption[] }];

/** The part of ComfyUI's node definition that names a node's inputs and their dropdown options. */
export type NodeDefinition = {
  input?: { required?: Record<string, InputSpec> };
};
