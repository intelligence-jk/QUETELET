# ATLAS: Assessment Tracker for Learning And Scores

Formerly `mock-tracker`.

Track topic accuracy across mock tests, see which way each topic is moving, and find the weakest topics first.

## What it solves
After several mock tests you have scores in lots of places. Keep one plain table (mock number, topic, questions correct, questions attempted) and this gives each topic's overall accuracy, how that accuracy is changing from one mock to the next, and a list with the weakest topic first. It works from your own table only; the example rows below are invented. Pure Python 3.10+, standard library only, exact fractions.

## Example
`results.csv`:
```
mock,topic,correct,attempted
1,algebra,2,5
1,geometry,4,5
2,algebra,3,5
2,geometry,3,5
3,algebra,4,5
3,geometry,2,5
```
```bash
python -m mocktracker results.csv
```
```
topic                    score  accuracy  change per mock
algebra                 9/15       60.0%     +20.0 points
geometry                9/15       60.0%     -20.0 points
```
Both topics sit at 60 percent overall, but algebra is rising and geometry is falling, which the overall figure alone would hide. Add `--min-attempted 10` to leave out topics with too few questions to say much.

## The maths behind it
Overall accuracy is total correct divided by total attempted (not an average of the per-mock percentages, which would give a short mock the same weight as a long one), held as an exact `Fraction`. The change per mock is the least-squares slope of the per-mock accuracy `y` against the mock number `x`:

```
slope = sum((x - mean_x)(y - mean_y)) / sum((x - mean_x)^2)
```

For algebra the accuracies are 2/5, 3/5, 4/5 at mocks 1, 2, 3, so the slope is exactly 1/5, shown as +20 points per mock. A topic seen in only one mock has no slope and shows n/a. With only a few mocks, a slope is a description of what happened, not a forecast, so read it next to the number of questions behind it.

## Install and run
```bash
python -m pip install -e .
python -m mocktracker results.csv
python -m pytest
```

## Licence
MIT. Made by Math & Myth (mathandmyth.ae): one to one maths mentoring, online, across the UAE.
