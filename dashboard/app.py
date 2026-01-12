#!/usr/bin/env python3
"""
Real-Time Benchmark Dashboard

A Flask-based web dashboard for monitoring benchmark progress in real-time.

Usage:
    python dashboard/app.py
    
Then open http://localhost:8080 in your browser.
"""

import json
import logging
import sqlite3
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

try:
    from flask import Flask, render_template, jsonify, send_from_directory
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("ERROR: Flask is required for the dashboard")
    print("Install with: pip install flask flask-cors")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Paths
DASHBOARD_DIR = Path(__file__).parent
REPO_ROOT = DASHBOARD_DIR.parent
BENCHMARK_DIR = REPO_ROOT / "logs" / "benchmarks"
CHECKPOINT_DIR = REPO_ROOT / "checkpoints"


class BenchmarkDatabase:
    """Simple SQLite database for benchmark results."""
    
    def __init__(self, db_path: Path):
        """Initialize database."""
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        """Create database tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS iterations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    benchmark_name TEXT,
                    iteration INTEGER,
                    phase TEXT,
                    accuracy REAL,
                    latency_ms REAL,
                    throughput_rps REAL,
                    cpu_utilization REAL,
                    timestamp REAL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS benchmarks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    status TEXT,
                    started_at TEXT,
                    completed_at TEXT,
                    total_iterations INTEGER,
                    final_accuracy REAL
                )
            """)
            conn.commit()
    
    def add_iteration(self, data: Dict[str, Any]):
        """Add iteration result to database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO iterations 
                (benchmark_name, iteration, phase, accuracy, latency_ms, throughput_rps, cpu_utilization, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data.get('benchmark_name', 'unknown'),
                data.get('iteration', 0),
                data.get('phase', 'unknown'),
                data.get('accuracy', 0),
                data.get('latency_ms', 0),
                data.get('throughput_rps', 0),
                data.get('cpu_utilization', 0),
                data.get('timestamp', 0)
            ))
            conn.commit()
    
    def get_recent_iterations(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent iterations."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM iterations 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]


# Initialize database
db = BenchmarkDatabase(DASHBOARD_DIR / "benchmark_data.db")


@app.route('/')
def index():
    """Main dashboard page."""
    # Try to load latest benchmark results
    latest_results = get_latest_benchmark()
    
    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Evolving-sun Benchmark Dashboard</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .metric {{
            display: inline-block;
            margin: 20px;
            padding: 20px;
            background: #f9f9f9;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
            margin-top: 5px;
        }}
        .status {{
            padding: 10px 20px;
            background: #4CAF50;
            color: white;
            border-radius: 5px;
            display: inline-block;
            margin: 10px 0;
        }}
        .info {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
            border-left: 4px solid #2196F3;
        }}
        .file-list {{
            margin-top: 20px;
        }}
        .file-item {{
            padding: 10px;
            background: #fafafa;
            margin: 5px 0;
            border-radius: 3px;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 Evolving-sun Benchmark Dashboard</h1>
        
        <div class="status">
            System Status: Ready
        </div>
        
        <h2>Latest Benchmark Results</h2>
        
        {render_benchmark_summary(latest_results)}
        
        <div class="info">
            <strong>ℹ️ Dashboard Information</strong><br>
            This is a simplified dashboard. Full real-time monitoring with WebSockets 
            and charts will be available when all dependencies are installed.
            <br><br>
            <strong>Available Endpoints:</strong>
            <ul>
                <li><code>/api/status</code> - System status</li>
                <li><code>/api/benchmarks</code> - Recent benchmarks</li>
                <li><code>/api/latest</code> - Latest benchmark result</li>
            </ul>
        </div>
        
        <h2>Recent Benchmark Files</h2>
        <div class="file-list">
            {render_file_list()}
        </div>
        
        <p style="margin-top: 40px; text-align: center; color: #666;">
            Auto-refresh every 5 seconds<br>
            <small>Dashboard running on port 8080</small>
        </p>
    </div>
    
    <script>
        // Auto-refresh every 5 seconds
        setTimeout(function() {{
            location.reload();
        }}, 5000);
    </script>
</body>
</html>
"""


def render_benchmark_summary(results: Dict[str, Any]) -> str:
    """Render benchmark summary HTML."""
    if not results:
        return "<p>No benchmark results available yet. Run a benchmark to see results here.</p>"
    
    metrics = results.get('metrics', {})
    accuracy = metrics.get('accuracy', 0)
    iterations = results.get('iterations', 0)
    duration = results.get('duration_seconds', 0)
    
    return f"""
        <div class="metric">
            <div class="metric-label">Accuracy</div>
            <div class="metric-value">{accuracy*100:.2f}%</div>
        </div>
        
        <div class="metric">
            <div class="metric-label">Iterations</div>
            <div class="metric-value">{iterations}</div>
        </div>
        
        <div class="metric">
            <div class="metric-label">Duration</div>
            <div class="metric-value">{duration:.1f}s</div>
        </div>
    """


def render_file_list() -> str:
    """Render list of benchmark files."""
    if not BENCHMARK_DIR.exists():
        return "<p>No benchmark directory found.</p>"
    
    files = sorted(BENCHMARK_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not files:
        return "<p>No benchmark files found.</p>"
    
    html = ""
    for f in files[:10]:  # Show latest 10
        html += f'<div class="file-item">{f.name}</div>\n'
    
    return html


def get_latest_benchmark() -> Dict[str, Any]:
    """Get latest benchmark results."""
    if not BENCHMARK_DIR.exists():
        return {}
    
    json_files = sorted(BENCHMARK_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not json_files:
        return {}
    
    try:
        with open(json_files[0], 'r') as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except Exception as e:
        logger.error(f"Error loading latest benchmark: {e}")
        return {}


@app.route('/api/status')
def api_status():
    """API endpoint for system status."""
    return jsonify({
        'status': 'running',
        'timestamp': datetime.now().isoformat(),
        'benchmark_dir': str(BENCHMARK_DIR),
        'checkpoint_dir': str(CHECKPOINT_DIR)
    })


@app.route('/api/benchmarks')
def api_benchmarks():
    """API endpoint for recent benchmarks."""
    if not BENCHMARK_DIR.exists():
        return jsonify({'error': 'Benchmark directory not found'})
    
    files = sorted(BENCHMARK_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    results = []
    for f in files[:20]:  # Latest 20
        try:
            with open(f, 'r') as fp:
                data = json.load(fp)
                if isinstance(data, dict):
                    results.append({
                        'filename': f.name,
                        'timestamp': data.get('timestamp', ''),
                        'benchmark_name': data.get('benchmark_name', ''),
                        'status': data.get('status', ''),
                        'iterations': data.get('iterations', 0)
                    })
        except Exception as e:
            logger.error(f"Error loading {f}: {e}")
    
    return jsonify({'benchmarks': results})


@app.route('/api/latest')
def api_latest():
    """API endpoint for latest benchmark."""
    return jsonify(get_latest_benchmark())


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Benchmark Dashboard")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    logger.info(f"Starting dashboard on http://{args.host}:{args.port}")
    logger.info(f"Benchmark directory: {BENCHMARK_DIR}")
    
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
