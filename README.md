# Simple BI Migration Engine (Tableau -> DAX)



## Flow (one file per step, in `app/`)
1. parser.py        read JSON / XML / CSV (also un-wraps the quoted-line files)
2. dependency.py    order calculations so A is translated before B
3. translator.py    rules: aggregations, FIXED LOD, WINDOW_SUM, RUNNING_SUM, RANK, division, IF
4. validator.py     self-check our DAX + explain what is wrong with the existing DAX
5. visual_mapper.py Tableau visual -> Power BI visual (lookup)
6. confidence.py    score 0-1 with reasons; each assumption subtracts 0.10
7. benchmark.py     before vs after accuracy against ground_truth.json
engine.py glues steps 2-6 together.

## Result on the shared files
Before (existing DAX correct): 0 of 3 gradable | After (engine): 3 of 3
calc_3 cannot be graded: its ground truth contains "..." (incomplete).

## Limits
- Regex rules: no nested IFs, no multi-dimension FIXED, no arithmetic inside IF branches.
- Table calcs assume they run along the view's last dimension (an assumption, lowers confidence).
- Grading compares normalized text, not numbers. 
