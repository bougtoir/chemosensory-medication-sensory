# Environment specification

- Python 3.10.12 (CPython)
- OS: Linux 6.8.0-1061-aws x86_64
- Network: not required (pipeline is fully offline; snapshots hash-guarded)
- PYTHONHASHSEED=0, MPLBACKEND=Agg

| Package | Version |
|---|---|
| numpy | 2.2.6 |
| pandas | 2.3.3 |
| scipy | 1.15.3 |
| statsmodels | 0.15.0 |
| scikit-learn | 1.7.2 |
| matplotlib | 3.10.9 |
| PyYAML | 5.4.1 |
| pytest | 9.1.1 |
| openpyxl | 3.1.5 |

Install: `pip install -r offline_pipeline/requirements.txt`.
