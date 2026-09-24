import '#styles/interface.css';
import { message } from '#web/text.ts';
import { app } from '../../scripts/app.js';
import { requestLocal } from '#web/http.ts';
import { dynamicControlInputs } from '#web/nodes.ts';
import { openModels } from '#web/discovery/dialog.ts';
import { openSettings } from '#web/settings/dialog.ts';
import type { Widget, CanvasNode } from '#web/contracts.ts';
import { findWidget, chainCallback } from '#web/widgets.ts';

const controlRestorers = new WeakMap<CanvasNode, ((restore?: boolean) => void)[]>();

/**
 * Keep a node's conditional values across option changes.
 * @param canvasNode - The node ComfyUI created.
 */
function addNodeControls(canvasNode: CanvasNode): void {
  const restorers: ((restore?: boolean) => void)[] = [];
  for (const name of dynamicControlInputs.get(canvasNode.comfyClass ?? '') ?? []) {
    const widget = findWidget(canvasNode, name);
    if (widget) restorers.push(watchControl(canvasNode, widget));
  }
  controlRestorers.set(canvasNode, restorers);
}

/**
 * Restore a control's hidden values whenever its option changes, and redraw the Parameters panel.
 * @param canvasNode - Owner of the control.
 * @param widget - ComfyUI's dynamic dropdown.
 * @returns The callback that restores this control's branch.
 */
function watchControl(canvasNode: CanvasNode, widget: Widget): (restore?: boolean) => void {
  const restoreValues = preserveControlValues(canvasNode, widget);
  chainCallback(widget, () => {
    restoreValues(true);
    // Checked on frontend 1.49.6: the Parameters panel keeps the previous option's rows until the selection changes.
    const canvas = app.canvas;
    // eslint-disable-next-line @typescript-eslint/no-deprecated -- ComfyUI has no other way to refresh the Parameters panel.
    canvas.onSelectionChange?.(canvas.selected_nodes);
  });
  return restoreValues;
}

/**
 * Keep the values of hidden controls in the node's properties.
 * Checked on frontend 1.49.6: the host resets a child widget to its default when its option returns.
 * @param canvasNode - Owner of the conditional widgets.
 * @param widget - ComfyUI's dynamic dropdown.
 * @returns A callback that restores the current branch's widgets and watches for new ones.
 */
function preserveControlValues(
  canvasNode: CanvasNode,
  widget: Widget,
): (restore?: boolean) => void {
  const restoredWidgets = new WeakSet<Widget>();
  const restoreValues = (restore = false): void => {
    const selected = widget.value as string;
    for (const child of canvasNode.widgets ?? []) {
      if (!child.name.startsWith(`${widget.name}.`) || restoredWidgets.has(child)) continue;
      restoredWidgets.add(child);
      const key = `${selected}/${child.name}`;
      const saved = canvasNode.properties.conditionalValues;
      if (restore && saved && Object.hasOwn(saved, key))
        // eslint-disable-next-line security/detect-object-injection -- The key holds a slash and is checked as an own property.
        child.value = saved[key];
      const removed = child.onRemove;
      child.onRemove = function () {
        if (!app.configuringGraph) {
          canvasNode.properties.conditionalValues ??= {};
          // eslint-disable-next-line security/detect-object-injection -- The key holds a slash, so it is never a prototype property.
          canvasNode.properties.conditionalValues[key] = child.value;
        }
        removed?.call(this);
      };
    }
  };
  restoreValues();
  return restoreValues;
}

/** Read ComfyUI's node definitions again, so every model dropdown shows the saved model list. */
function reloadNodes(): void {
  app.extensionManager.command.execute('Comfy.RefreshNodeDefinitions');
}

/** Watch the conditional values of every node after the graph changes. */
function refreshGraph(): void {
  for (const canvasNode of app.rootGraph.nodes) {
    for (const restoreValues of controlRestorers.get(canvasNode) ?? []) restoreValues();
  }
}

app.registerExtension({
  name: 'comfyui-openrouter',
  setup: () => {
    const stylesheet = document.createElement('link');
    stylesheet.rel = 'stylesheet';
    stylesheet.href = new URL('./extension.css', import.meta.url).href;
    const stylesheets = new Set();
    for (const link of document.querySelectorAll('link[rel=stylesheet]')) {
      stylesheets.add(link.getAttribute('href'));
    }
    if (!stylesheets.has(stylesheet.href)) document.head.append(stylesheet);
  },
  nodeCreated: addNodeControls,
  afterConfigureGraph: refreshGraph,
  commands: [
    {
      id: 'OpenRouter.OpenSettings',
      label: message('settings.menu'),
      function: openSettings.bind(null, requestLocal),
    },
    {
      id: 'OpenRouter.OpenModels',
      label: message('models.menu'),
      function: openModels.bind(null, requestLocal, reloadNodes),
    },
  ],
  menuCommands: [
    {
      path: ['Extensions', 'OpenRouter'],
      commands: ['OpenRouter.OpenSettings', 'OpenRouter.OpenModels'],
    },
  ],
});
