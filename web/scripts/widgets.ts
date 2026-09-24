import type { CanvasNode, Widget } from '#web/contracts.ts';

/**
 * Find one of a node's widgets by the name its schema gives the input.
 * @param canvasNode - The node to look in.
 * @param name - The input's name, as the schema declares it.
 * @returns The widget, or nothing when the node has no such input.
 */
export function findWidget(canvasNode: CanvasNode, name: string): Widget | undefined {
  return canvasNode.widgets?.find((widget) => widget.name === name);
}

/**
 * Do something more whenever a widget changes, after ComfyUI's own handler has run.
 * @param widget - The widget to watch.
 * @param after - What to do once the change has been handled.
 */
export function chainCallback(widget: Widget, after: () => void): void {
  const previous = widget.callback?.bind(widget);
  widget.callback = function (...args) {
    previous?.apply(this, args);
    after();
  };
}
