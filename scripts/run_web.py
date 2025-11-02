import os
import sys
from pathlib import Path

# Ensure 'src' is on sys.path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fastapi import FastAPI  # type: ignore
from webapp.main import app  # the FastAPI app instance


def main() -> None:
    import uvicorn  # type: ignore
    port = int(os.environ.get("PORT", "8000"))
    uvicorn.run(app, host="127.0.0.1", port=port, reload=False)


if __name__ == "__main__":
    main()
