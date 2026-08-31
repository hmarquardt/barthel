#!/usr/bin/env python3
"""Serve dist/ locally for preview and QA. Usage: python3 tools/serve.py [port]"""
import http.server
import socketserver
import sys
from pathlib import Path

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8908
DIST = Path(__file__).absolute().parent.parent / "dist"


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIST), **kwargs)

    def log_message(self, *args):
        pass


socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as httpd:
    print(f"serving dist/ at http://127.0.0.1:{PORT}")
    httpd.serve_forever()
