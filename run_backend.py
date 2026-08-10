#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

backend_path = os.path.join(os.path.dirname(__file__), "backend")
sys.path.insert(0, backend_path)

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info",
    )
