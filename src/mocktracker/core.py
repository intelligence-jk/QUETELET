"""Track topic accuracy across mock tests and find the weakest topics.

Input is your own table, one row per topic per mock: mock,topic,correct,attempted
Mocks are ordered by their number (1, 2, 3 ...).
"""
from __future__ import annotations

import csv
import io
from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Result:
    mock: int
    topic: str
    correct: int
    attempted: int


@dataclass(frozen=True)
class TopicReport:
    topic: str
    correct: int
    attempted: int
    accuracy: Fraction  # total correct / total attempted
    trend: Fraction | None  # change in accuracy per mock (least squares), None if under 2 mocks
    mocks: int


def read_results(text: str) -> list[Result]:
    reader = csv.DictReader(io.StringIO(text))
    need = {"mock", "topic", "correct", "attempted"}
    if not reader.fieldnames or not need <= {f.strip() for f in reader.fieldnames}:
        raise ValueError("the file needs a header row: mock,topic,correct,attempted")
    out = []
    for n, r in enumerate(reader, 2):
        r = {k.strip(): (v or "").strip() for k, v in r.items() if k}
        try:
            mock, c, a = int(r["mock"]), int(r["correct"]), int(r["attempted"])
        except ValueError:
            raise ValueError(f"line {n}: mock, correct and attempted must be whole numbers")
        if not r["topic"]:
            raise ValueError(f"line {n}: topic is empty")
        if a <= 0 or c < 0 or c > a:
            raise ValueError(f"line {n}: need 0 <= correct <= attempted and attempted > 0")
        out.append(Result(mock, r["topic"].lower(), c, a))
    if not out:
        raise ValueError("no rows found")
    return out


def slope(points: list[tuple[int, Fraction]]) -> Fraction:
    """Least-squares slope of y against x, exact. Needs two different x values."""
    n = len(points)
    mx = Fraction(sum(x for x, _ in points), n)
    my = sum(y for _, y in points) / n
    sxx = sum((x - mx) ** 2 for x, _ in points)
    if sxx == 0:
        raise ValueError("need at least two different x values")
    return sum((x - mx) * (y - my) for x, y in points) / sxx


def topic_report(results: list[Result], min_attempted: int = 1) -> list[TopicReport]:
    """Weakest first. Topics with fewer than min_attempted questions in total are left out."""
    reps = []
    for topic in sorted({r.topic for r in results}):
        mine = [r for r in results if r.topic == topic]
        c, a = sum(r.correct for r in mine), sum(r.attempted for r in mine)
        if a < min_attempted:
            continue
        per_mock: dict[int, list[int]] = {}
        for r in mine:
            cur = per_mock.setdefault(r.mock, [0, 0])
            cur[0] += r.correct
            cur[1] += r.attempted
        pts = [(m, Fraction(v[0], v[1])) for m, v in sorted(per_mock.items())]
        trend = slope(pts) if len(pts) >= 2 else None
        reps.append(TopicReport(topic, c, a, Fraction(c, a), trend, len(pts)))
    reps.sort(key=lambda t: (t.accuracy, t.topic))
    return reps
