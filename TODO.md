# TODO

## Immediate Next Steps
- [ ] Create and activate a Python 3.11+ virtual environment.
- [ ] Install project dependencies with `pip install -e .[dev]`.
- [ ] Run `pytest` to validate the scaffold and ensure OutputWriter tests pass.

## Sprint 1 Enhancements
- [ ] Flesh out `ProblemGenerator` to read configuration and prepare for deterministic workflows.
- [ ] Add CLI option for custom output directory using loaded settings.
- [ ] Implement integration test hitting the FastAPI placeholder endpoint via TestClient.

## Upcoming Features (Sprint 2+)
- [ ] Integrate OpenAI enhancer stub with configurable prompts.
- [ ] Introduce deterministic RNG-based testcase generator module.
- [ ] Add ZIP exporter utility for generated bundles.
