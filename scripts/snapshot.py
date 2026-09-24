"""Write the model list that ships with the extension from OpenRouter's public lists."""

import sys
import json
import asyncio
from src.paths import SNAPSHOT_PATH
from src.discovery.choices import build_choices
from src.discovery.sources import read_public_models


def main() -> int:
    """Write the bundled model list, then report every model no node lists."""
    snapshot = asyncio.run(read_public_models())
    SNAPSHOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    SNAPSHOT_PATH.write_text(
        json.dumps(snapshot.model_dump(mode="json"), indent=1, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    sys.stdout.write(f"Wrote {len(snapshot.models)} models from {snapshot.retrieved_at[:10]}.\n")
    # A model no node lists means OpenRouter added a new kind of model that needs a node before the next release.
    served = {model_id for choices in build_choices(snapshot).values() for model_id in choices}
    problems = [
        f"No node lists {record.id}; its outputs are {', '.join(record.output_modalities)}.\n"
        for record in snapshot.models
        if record.id not in served
    ]
    sys.stderr.writelines(problems)
    return int(bool(problems))


if __name__ == "__main__":
    raise SystemExit(main())
