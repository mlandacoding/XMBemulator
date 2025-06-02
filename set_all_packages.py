import os
import subprocess
import sys
import importlib.util


def load_requirements(file_path="requirements.txt"):
    if not os.path.exists(file_path):
        print(f"{file_path} not found.")
        return []

    requirements = []
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                if " as " in line:
                    package, import_name = line.split(" as ")
                    requirements.append((package.strip(), import_name.strip()))
                else:
                    requirements.append((line, line))  # package name and import name are the same
    return requirements


def is_stdlib(module_name):
    try:
        spec = importlib.util.find_spec(module_name)
        return spec.origin == "built-in" or "python" in spec.origin and "site-packages" not in spec.origin
    except Exception:
        return False


def install_and_import(package, import_name=None, global_scope=None):
    if import_name is None:
        import_name = package

    if is_stdlib(import_name):
        print(f"{import_name} is a built-in module. Skipping install.")
    else:
        try:
            importlib.import_module(import_name)
        except ImportError:
            print(f"{package} not found. Installing...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            except subprocess.CalledProcessError as e:
                print(f"Error installing {package}: {e}")
                return None

    # Inject into caller's scope
    module = importlib.import_module(import_name)
    if global_scope is not None:
        global_scope[import_name] = module
    return module


def set_all_packages(global_scope):
    requirements = load_requirements()
    for package, import_name in requirements:
        install_and_import(package, import_name, global_scope)
