#!/usr/bin/env python3
import sys
import os
import tomllib
import subprocess
import urllib.request
import tarfile

COMMANDS = {
    "--help": " help - show this message",
    "sp": " spawn - install a package",
    "ds": " disrupt - delete a package",
    "fi": " find - find a package on desktop",
    "rs": " refresh - update system/packages",
}

ROOT_DIR = "/"
RECIPES_DIR = "Gekko-EXO/recipes"

ERROR_ID = 0

def show_help():
    print("EXO - Gekko Linux Package Assembler")
    print("Usement: gpa <command> [argument]")
    print("List of commands:")

    for cmd, desc in COMMANDS.items():
        print(f"  {cmd}\t{desc}")
    sys.exit(1)

def spawn_pkg(pkg_name):
    recipe_path = os.path.join(RECIPES_DIR, f"{pkg_name}.toml")

    if not os.path.exists(RECIPES_DIR, f"{pkg_name}.toml"):
        ERROR_ID = 1
        print(f"Error (ID: {ERROR_ID}): Package {pkg_name} not found.")
        sys.exit(1)
    else:
        print(f"Reading recipe for {pkg_name}...")
        #Reads recipe

        with open(recipe_path, "rb") as f:
            recipe = tomllib.load(f)

        pkg_meta = recipe.get("package_manifest", {})
        build_meta = recipe.get("compile_conf", {})
        url = pkg_meta.get("url")
        version = pkg_meta.get("version")
        archive_name = url.split("/")[-1]

        src_dir = "./Sources"
        os.makedirs(src_dir, exist_ok=True)
        archive_path = os.path.join(src_dir, archive_name)

        if not os.path.exists(archive_path):
            print(f"Installling {pkg_name}...")
            try:
                urllib.request.urlretrieve(url, archive_path)
            except Exception as e:
                print(f"Download failed: Error: {e}")
                sys.exit(1)

        print(f"Extracting {archive_name}...")
        try:
            with tarfile.open(archive_path) as tar:
                tar.extractall(path=src_dir)
                extracted_dirname = tar.getnames()[0].split('/')[0]
        except Exception as e:
            print(f"Extraction failed: Error: {e}")

        work_dir = os.path.join(src_dir, extracted_dirname)
        print(f"Entering working directory: {work_dir}")

        conf_cmd = ['./configure']
        build_flags = build_meta.get("configure_flags", ["--prefix=/usr"])
        conf_cmd.extend(build_flags)

        custom_env = os.environ.copy()
        build_env = build_meta.get("env", {})
        custom_env.update(build_env)

        print(f"Running: {' '.join(conf_cmd)}")

        res = subprocess.run(conf_cmd, cwd=work_dir, env=custom_env)
        if res.returncode != 0:
            ERROR_ID = 2
            print(f"Configure failed! (ID: {ERROR_ID})")
            sys.exit(1)

        print(f"Compiling {pkg_name}...")
        jobs = os.cpu_count() or 2
        res = subprocess.run(["make", f"-j{jobs}"], cwd=work_dir)
        if res.returncode != 0:
            ERROR_ID = 2
            print(f"Compilation failed! (ID: {ERROR_ID})")
            sys.exit(1)

        print(f"Installing {pkg_name} to system...")
        res = subprocess.run(["make", f"DESTDIR={ROOT_DIR}", "install"], cwd=work_dir)
        if res.returncode != 0:
            ERROR_ID = 3
            print(f"Installation failed! (ID: {ERROR_ID})")
            sys.exit(1)
        print(f"=== {pkg_name} is successfully spawned! ===")

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "--help":
        show_help()

    action = sys.argv[1]

    if action == "sp" or action == "spawn":
        if len(sys.argv) < 3:
            print("Error: please specify a package to install.")
            sys.exit(1)
        pkg_name = sys.argv[2]
        spawn_pkg(pkg_name)

if __name__ == '__main__':
    main()

        