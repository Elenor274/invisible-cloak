# Contributing

Thanks for helping improve the project.

## Development setup

1. Fork and clone the repository.
2. Create a focused branch from `main`.
3. Create a virtual environment.
4. Install dependencies with `pip install -r requirements.txt -r requirements-dev.txt`.
5. Run `python -m pytest -q` before opening a pull request.

Keep pull requests small and add synthetic image tests for reusable image-processing functions. Webcam-dependent behavior should degrade gracefully when a camera is unavailable.

Look for issues labeled `good first issue` if you are new to the project.
