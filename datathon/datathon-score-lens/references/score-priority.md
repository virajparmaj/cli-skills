# Score Priority

## Repo anchor

- Code root: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon`
- Context bundle: `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1`
- Current scoring notes:
  - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/math.md`
  - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/1/notes/rules.md`
- Existing scoring code:
  - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/src/local_scoring.py`
  - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/scripts/generate_v07.py`
  - `/Users/veerr_89/Work/projects/AWS-DataBricks-Hackathon/scripts/generate_v08.py`

## Official weighting used in this repo

- `Composite = 0.35 * E_V + 0.25 * E_C + 0.15 * E_B + 0.25 * P_t`
- `alpha = 2`, `beta = 1`
- Lower is better.

## Current v08 decision order

1. Protect intraday call-volume shape first.
2. Protect workload realism second.
3. Improve abandon behavior without creating low-volume noise.
4. Only chase pure CCT gains if they help workload or transfer.

## Segment definitions

- `overnight`: slots `0-11` (`00:00-05:30`)
- `morning`: slots `12-23` (`06:00-11:30`)
- `afternoon`: slots `24-35` (`12:00-17:30`)
- `evening`: slots `36-47` (`18:00-23:30`)

## What strong analysis looks like

- Show where `E_V` is largest by portfolio, date, weekday, and daypart.
- Show where `P_t` is largest, split into underforecast and overforecast.
- Call out whether workload miss is mostly caused by volume, CCT, or both.
- Name the smallest plausible next modeling change.

## Weak analysis to avoid

- "CCT looks bad" without showing workload impact.
- "Abandon is noisy" without showing whether it matters to ranking.
- "Need more features" without identifying the failure slice.
