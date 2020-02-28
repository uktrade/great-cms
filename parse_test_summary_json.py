#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import os
import sys


def parse_summary_json(summary_path: str):
    if not os.path.exists(summary_path):
        print(f"Could not find test summary file: {summary_path}")
        return

    with open(summary_path, "r") as json_file:
        report = json.loads(json_file.read())
        stats = report["statistic"]

    message = (
        f"Test Summary: Total={stats['total']}💪 Passed={stats['passed']}😁 "
        f"Failed={stats['failed']}😭 Skipped={stats['skipped']}😴 "
        f"Broken={stats['broken']}🤕 Unknown={stats['unknown']}😵"
    )
    print(message)


if __name__ == "__main__":
    parse_summary_json(sys.argv[1])
