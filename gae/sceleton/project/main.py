from gae.webapp import run
import os, sys

if __name__ == "__main__":
    project_path = os.path.dirname(__file__)
    if project_path not in sys.path:
        sys.path.insert(0, project_path)
    run(project_path)