#!/usr/bin/env python3
"""
mtop - htop-like monitor for local LLM inference.

Provides real-time monitoring of GPU usage, memory, token generation speed, etc.
for locally running LLMs.
"""

import argparse
import sys
import time
import curses
from typing import Optional


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Monitor local LLM inference with GPU and token rate metrics."
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=1.0,
        help="Update interval in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--gpu-id",
        type=int,
        default=0,
        help="GPU device ID to monitor (default: 0)",
    )
    parser.add_argument(
        "--llm-endpoint",
        type=str,
        default="http://localhost:8080",
        help="Endpoint for LLM server metrics (default: http://localhost:8080)",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable colored output",
    )
    return parser.parse_args()


def get_gpu_stats(gpu_id: int) -> dict:
    """
    Get GPU statistics using nvidia-smi.

    Executes: nvidia-smi --query-gpu=memory.total,memory.used,utilization.gpu --format=csv,noheader
    For a specific GPU ID, use --id=<gpu_id> flag.

    Returns:
        dict: Contains keys 'gpu_id', 'utilization' (%), 'memory_used' (MB), 'memory_total' (MB).
        Temperature is not included in the specified query; set to 0 as placeholder.
        On error, returns default zero values.
    """
    import subprocess
    try:
        # Run nvidia-smi command for specified GPU
        cmd = [
            "nvidia-smi",
            f"--id={gpu_id}",
            "--query-gpu=memory.total,memory.used,utilization.gpu",
            "--format=csv,noheader"
        ]
        output = subprocess.check_output(cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        # Example output: " 8192 MiB, 2048 MiB, 45 %"
        parts = output.strip().split(', ')
        if len(parts) != 3:
            raise ValueError("Unexpected output format from nvidia-smi")

        memory_total_str, memory_used_str, utilization_str = parts
        # Extract numerical values (remove units)
        memory_total = int(memory_total_str.split()[0])
        memory_used = int(memory_used_str.split()[0])
        utilization = int(utilization_str.split()[0])  # removes the '%' sign

        return {
            "gpu_id": gpu_id,
            "utilization": float(utilization),  # keep as float for consistency with original
            "memory_used": memory_used,
            "memory_total": memory_total,
            "temperature": 0  # placeholder; not queried in the specified command
        }
    except Exception as e:
        # Log error to stderr but don't crash the monitor
        print(f"Error getting GPU stats: {e}", file=sys.stderr)
        return {
            "gpu_id": gpu_id,
            "utilization": 0.0,
            "memory_used": 0,
            "memory_total": 0,
            "temperature": 0
        }


def get_token_rate(endpoint: str) -> dict:
    """
    Placeholder for token rate monitoring from LLM endpoint.
    Returns a dictionary with token metrics.
    """
    # TODO: Implement actual token rate fetching from LLM server (e.g., llama-server metrics)
    return {
        "tokens_per_second": 0.0,
        "prompt_tokens": 0,
        "generation_tokens": 0,
        "total_tokens": 0,
    }


def format_number(num: float) -> str:
    """Format a number for display."""
    if num >= 1e6:
        return f"{num/1e6:.1f}M"
    elif num >= 1e3:
        return f"{num/1e3:.1f}K"
    else:
        return f"{num:.1f}"


def draw_ui(stdscr, gpu_stats, token_stats, interval):
    """Draw the user interface using curses."""
    # Clear screen
    stdscr.clear()

    # Get terminal dimensions
    height, width = stdscr.getmaxyx()

    # Title
    title = "mtop - Local LLM Monitor"
    stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)

    # Separator
    stdscr.addstr(1, 0, "=" * width)

    # Info line
    info = f"Update interval: {interval}s | GPU ID: {gpu_stats['gpu_id']} | LLM Endpoint: {token_stats.get('endpoint', 'N/A')}"
    if len(info) > width - 1:
        info = info[:width-1]
    stdscr.addstr(2, 0, info)

    # Separator
    stdscr.addstr(3, 0, "-" * width)

    # GPU Usage
    gpu_start = 5
    stdscr.addstr(gpu_start, 0, "GPU Usage:", curses.A_BOLD)
    util_text = f"  Utilization: {gpu_stats['utilization']:.1f}%"
    mem_text = f"  Memory: {gpu_stats['memory_used']} MB / {gpu_stats['memory_total']} MB"
    temp_text = f"  Temperature: {gpu_stats['temperature']}°C"
    stdscr.addstr(gpu_start + 1, 0, util_text)
    stdscr.addstr(gpu_start + 2, 0, mem_text)
    stdscr.addstr(gpu_start + 3, 0, temp_text)

    # Token Rate
    token_start = gpu_start + 5
    stdscr.addstr(token_start, 0, "Token Rate:", curses.A_BOLD)
    tps_text = f"  Tokens/s: {token_stats['tokens_per_second']:.1f}"
    prompt_text = f"  Prompt tokens: {token_stats['prompt_tokens']}"
    gen_text = f"  Generation tokens: {token_stats['generation_tokens']}"
    total_text = f"  Total tokens: {token_stats['total_tokens']}"
    stdscr.addstr(token_start + 1, 0, tps_text)
    stdscr.addstr(token_start + 2, 0, prompt_text)
    stdscr.addstr(token_start + 3, 0, gen_text)
    stdscr.addstr(token_start + 4, 0, total_text)

    # Instructions
    instr = "Press 'q' or Ctrl+C to exit"
    if height > 0 and width > 0:
        stdscr.addstr(height - 1, 0, instr[:width-1])

    # Refresh the screen
    stdscr.refresh()


def main() -> None:
    """Main entry point."""
    args = parse_args()

    try:
        # Initialize curses
        stdscr = curses.initscr()
        curses.cbreak()
        curses.noecho()
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(True)  # Non-blocking getch
        # Set timeout based on interval (in milliseconds)
        stdscr.timeout(int(args.interval * 1000))

        while True:
            # Get metrics
            gpu_stats = get_gpu_stats(args.gpu_id)
            token_stats = get_token_rate(args.llm_endpoint)

            # Draw UI
            draw_ui(stdscr, gpu_stats, token_stats, args.interval)

            # Check for key press
            key = stdscr.getch()
            if key == ord('q') or key == 3:  # 'q' or Ctrl+C
                break

            # Small sleep to prevent excessive CPU usage when timeout is 0
            if args.interval <= 0:
                time.sleep(0.01)

    except KeyboardInterrupt:
        pass
    finally:
        # Clean up curses
        curses.nocbreak()
        curses.echo()
        curses.curs_set(1)
        curses.endwin()
        print("\nExiting mtop.")


if __name__ == "__main__":
    main()