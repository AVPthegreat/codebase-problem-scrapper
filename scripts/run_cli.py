import argparse
import sys
from pathlib import Path

# Ensure src on sys.path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from app.services.orchestrator import ScrapeOrchestrator


def main() -> int:
    p = argparse.ArgumentParser(description="Generate a problem bundle without launching the GUI.")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--prompt", help="Prompt describing the problems to fetch")
    g.add_argument("--prompt-file", type=Path, help="Path to a text file containing the prompt")
    p.add_argument("--out", type=Path, default=None, help="Optional output directory for the ZIP")
    args = p.parse_args()

    if args.prompt_file:
        prompt = args.prompt_file.read_text().strip()
    else:
        prompt = args.prompt.strip()

    orch = ScrapeOrchestrator(base_output=args.out) if args.out else ScrapeOrchestrator()

    print("Starting bundle generation...")
    zip_path = orch.generate_bundle(prompt, log_callback=lambda m: print(m))
    print(f"Bundle ready: {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
