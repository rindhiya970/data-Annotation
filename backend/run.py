"""Flask application entry point."""

from app import create_app
import sys

app = create_app()

# Add request logging middleware
@app.before_request
def log_request():
    from flask import request
    print(f"\n{'='*60}", file=sys.stderr, flush=True)
    print(f"[REQUEST] {request.method} {request.path}", file=sys.stderr, flush=True)
    print(f"[REQUEST] Content-Type: {request.content_type}", file=sys.stderr, flush=True)
    print(f"[REQUEST] Content-Length: {request.content_length}", file=sys.stderr, flush=True)
    print(f"{'='*60}\n", file=sys.stderr, flush=True)

if __name__ == "__main__":
    print("Starting Flask server...", file=sys.stderr, flush=True)
    app.run(debug=True)
