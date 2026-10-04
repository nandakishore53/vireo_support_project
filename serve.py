"""
Lightweight Executive Dashboard Server for Vireo Audio Support Analytics.
Zero external dependencies (uses standard library http.server).
Automatically synchronizes dashboard/data.js from outputs/ before serving.
Usage: python serve.py [--port 8501]
"""
import sys
import os
import argparse
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

# Ensure project root is in sys.path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

from src.export_dashboard_data import export_dashboard_data


class DashboardHandler(SimpleHTTPRequestHandler):
    """Serve files directly from dashboard/ directory with no-cache headers."""
    def __init__(self, *args, **kwargs):
        dashboard_dir = str(BASE_DIR / "dashboard")
        super().__init__(*args, directory=dashboard_dir, **kwargs)

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()


def run_server(port: int = 8501):
    print("=" * 60)
    print("Vireo Audio Support Analytics — Executive Dashboard")
    print("=" * 60)
    print("1. Synchronizing data from outputs/...")
    export_dashboard_data()

    print(f"\n2. Starting local server on http://localhost:{port} ...")
    print(f"   Dashboard directory: {BASE_DIR / 'dashboard'}")
    print("   Press Ctrl+C to stop.\n")
    print("=" * 60)

    server_address = ("", port)
    httpd = HTTPServer(server_address, DashboardHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping dashboard server. Goodbye!")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Vireo Audio Support Dashboard")
    parser.add_argument("--port", type=int, default=8501, help="Port to serve on (default: 8501)")
    args = parser.parse_args()
    run_server(args.port)
