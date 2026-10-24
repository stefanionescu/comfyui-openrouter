"""Run the schema export with ComfyUI on the CPU.

The export runs no model, so ComfyUI may load on the CPU, as its --cpu flag asks. The CI runner has no graphics card
and needs that. ComfyUI reads the flag when its device code loads, and the nodes of the extension and of ComfyUI both
load it, so this script sets the flag first.
"""

import runpy
from pathlib import Path

from comfy.cli_args import args as host_args

host_args.cpu = True
runpy.run_path(str(Path(__file__).with_name('schema.py')), run_name='__main__')
