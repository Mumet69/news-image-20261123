#!/usr/bin/env python3
"""news-image-20261123 entry: copy the pre-rendered image to the output dir.

The image (entry.png, in this repository) sums up the world news of Monday
23 November 2026. Standard library only; deterministic: the same bytes out
on every run.
"""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(HERE, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
