#! /usr/bin/env python3

import os
import argparse
import configparser
import subprocess
from pathlib import Path

# initialize directories
example_dir = Path(__file__).parent
project_dir = ( example_dir ).resolve()
bin_dir = project_dir / "build" / example_dir.relative_to(project_dir)

def init():
    args = []
    args += [ example_dir / "init.py" ]
    subprocess.run(args, check=True, cwd=example_dir)

def solve( config_path: Path ):
    solver_path = bin_dir / f"damBreak3D_WCSPH-DBC_benchmark"

    args = []
    args += [
        solver_path,
        "--config", config_path,
    ]

    # run the process and print its output as it is being executed
    with subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          bufsize=1, cwd=example_dir, text=True) as p:
        for line in p.stdout:
            print(line, end="")
    if p.returncode != 0:
        raise subprocess.CalledProcessError(p.returncode, p.args)

if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Dam break equation example")
    argparser.add_argument("--init", default=False,
            help="generate initial configuration of the case, including particles")
    argparser.add_argument("--config", default="sources/config.ini",
            help="path to the config file (relative to the path of this script)")

    # parse the command line arguments
    args = argparser.parse_args()

    if args.init  or  not os.path.exists( example_dir / "sources" ):
        init()

    config_path = example_dir / args.config

    # run the simulation
    solve( config_path )
