#!/usr/bin/env python3
"""
fastfish-format CLI 入口。

供 OpenClaw Skills 通过 system.run 调用。支持公众号/小红书格式化、Markdown 渲染等。
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from fastfish_format.cli import main

if __name__ == "__main__":
    sys.exit(main())
