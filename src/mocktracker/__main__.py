"""python -m mocktracker results.csv [--min-attempted 4]"""
import argparse
import sys

from .core import read_results, topic_report


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="python -m mocktracker")
    p.add_argument("file")
    p.add_argument("--min-attempted", type=int, default=1)
    a = p.parse_args(argv)
    try:
        reps = topic_report(read_results(open(a.file).read()), a.min_attempted)
    except (ValueError, OSError) as e:
        print(f"Cannot read results: {e}", file=sys.stderr)
        return 1
    print(f"{'topic':20s} {'score':>9s} {'accuracy':>9s} {'change per mock':>16s}")
    for t in reps:
        tr = "n/a" if t.trend is None else f"{float(t.trend) * 100:+.1f} points"
        print(f"{t.topic:20s} {t.correct:>4d}/{t.attempted:<4d} {float(t.accuracy) * 100:8.1f}% {tr:>16s}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
