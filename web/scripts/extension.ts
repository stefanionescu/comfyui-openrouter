import '#styles/interface.css';
import { message } from '#web/text.ts';
import { app } from '../../scripts/app.js';
import { requestLocal } from '#web/http.ts';
import { dynamicControlInputs } from '#web/nodes.ts';
import { openSettings } from '#web/settings/dialog.ts';
import { findWidget, chainCallback } from '#web/widgets.ts';
import type { Widget, CanvasNode, NodeDefinition, DropdownOption } from '#web/contracts.ts';

const controlRestorers = new WeakMap<CanvasNode, ((restore?: boolean) => void)[]>();
const childLabels = new Map<string, Map<string, string>>();

/**
 * List the display names one dropdown option gives its inputs.
 * @param name - The dropdown's input name.
 * @param option - One option of the dropdown.
 * @returns Pairs of option and widget name, and the display name.
 */
function listOptionLabels(name: string, option: DropdownOption): [string, string][] {
  return Object.entries(option.inputs.required ?? {}).flatMap(([child, [, spec]]) =>
    spec.display_name
      ? [[`${option.key}/${name}.${child}`, spec.display_name] as [string, string]]
      : [],
  );
}

/**
 * Keep the display names of each node's conditional inputs, keyed by option and widget name.
 * Checked on frontend 1.49.6: the host labels a dynamic dropdown's child widgets with their input names.
 * @param definitions - The node definitions from the server, keyed by node class.
 */
function readChildLabels(definitions: Record<string, NodeDefinition>): void {
  for (const [nodeClass, definition] of Object.entries(definitions)) {
    const controls = dynamicControlInputs.get(nodeClass) ?? [];
    const labels = new Map(
      Object.entries(definition.input?.required ?? {})
        .filter(([name]) => controls.includes(name))
        .flatMap(([name, [, spec]]) =>
          (spec.options ?? []).flatMap((option) => listOptionLabels(name, option)),
        ),
    );
    if (labels.size) childLabels.set(nodeClass, labels);
  }
}

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
 * Keep the values of hidden controls in the node's properties, and label each control with its display name.
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
  const labels = childLabels.get(canvasNode.comfyClass ?? '');
  const restoreValues = (restore = false): void => {
    const selected = widget.value as string;
    for (const child of canvasNode.widgets ?? []) {
      if (!child.name.startsWith(`${widget.name}.`) || restoredWidgets.has(child)) continue;
      restoredWidgets.add(child);
      const key = `${selected}/${child.name}`;
      const label = labels?.get(key);
      if (label) child.label = label;
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

/** Watch the conditional values of every node after the graph changes. */
function refreshGraph(): void {
  for (const canvasNode of app.rootGraph.nodes) {
    for (const restoreValues of controlRestorers.get(canvasNode) ?? []) restoreValues();
  }
}

app.registerExtension({
  name: 'openrouter',
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
  addCustomNodeDefs: readChildLabels,
  nodeCreated: addNodeControls,
  afterConfigureGraph: refreshGraph,
  commands: [
    {
      id: 'OpenRouter.OpenSettings',
      label: message('settings.menu'),
      function: openSettings.bind(null, requestLocal),
    },
  ],
  menuCommands: [
    {
      path: ['Extensions', 'OpenRouter'],
      commands: ['OpenRouter.OpenSettings'],
    },
  ],
});
