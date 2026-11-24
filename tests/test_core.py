from fractions import Fraction as F

import pytest

from mocktracker import read_results, slope, topic_report
from mocktracker.__main__ import main

DATA = """mock,topic,correct,attempted
1,algebra,2,5
1,geometry,4,5
2,algebra,3,5
2,geometry,3,5
3,algebra,4,5
3,geometry,2,5
"""


def test_accuracy_exact_and_weakest_first():
    reps = topic_report(read_results(DATA))
    assert [r.topic for r in reps] == ["algebra", "geometry"]  # equal accuracy: by name
    d = {r.topic: r for r in reps}
    assert d["algebra"].accuracy == F(9, 15) == F(3, 5)
    assert d["geometry"].accuracy == F(3, 5)


def test_slope_known_values():
    assert slope([(1, F(0)), (2, F(1)), (3, F(2))]) == 1
    assert slope([(1, F(1, 2)), (2, F(1, 2))]) == 0
    assert slope([(1, F(2, 5)), (2, F(3, 5)), (3, F(4, 5))]) == F(1, 5)
    assert slope([(1, F(4, 5)), (2, F(3, 5)), (3, F(2, 5))]) == F(-1, 5)


def test_trend_up_and_down():
    d = {r.topic: r for r in topic_report(read_results(DATA))}
    assert d["algebra"].trend == F(1, 5) and d["geometry"].trend == F(-1, 5)


def test_slope_matches_two_point_formula():
    assert slope([(2, F(1, 4)), (7, F(3, 4))]) == (F(3, 4) - F(1, 4)) / 5


def test_weakest_ordering_and_min_attempted():
    rows = read_results("mock,topic,correct,attempted\n1,a,1,10\n1,b,9,10\n1,c,0,2\n")
    assert [r.topic for r in topic_report(rows)] == ["c", "a", "b"]
    assert [r.topic for r in topic_report(rows, min_attempted=5)] == ["a", "b"]


def test_single_mock_has_no_trend():
    r = topic_report(read_results("mock,topic,correct,attempted\n1,a,1,2\n"))[0]
    assert r.trend is None and r.mocks == 1


def test_two_rows_same_mock_combined():
    r = topic_report(read_results("mock,topic,correct,attempted\n1,a,1,2\n1,a,2,2\n2,a,4,4\n"))[0]
    assert (r.correct, r.attempted, r.mocks) == (7, 8, 2)
    assert r.trend == F(1, 1) - F(3, 4)


@pytest.mark.parametrize(
    "bad",
    [
        "mock,topic\n1,a\n",
        "mock,topic,correct,attempted\n1,a,3,2\n",
        "mock,topic,correct,attempted\n1,a,1,0\n",
        "mock,topic,correct,attempted\nx,a,1,2\n",
        "mock,topic,correct,attempted\n",
    ],
)
def test_bad_input(bad):
    with pytest.raises(ValueError):
        read_results(bad)


def test_cli(tmp_path, capsys):
    f = tmp_path / "r.csv"
    f.write_text(DATA)
    assert main([str(f)]) == 0
    out = capsys.readouterr().out
    assert "+20.0 points" in out and "-20.0 points" in out
