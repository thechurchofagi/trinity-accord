# Reproducibility

## Environment
Ubuntu 22.04 runner; Python 3; pandoc; LibreOffice; python-docx; lxml; numpy; matplotlib.

## Build
1. python3 generate_assets.py
2. python3 build_paper.py
3. libreoffice --headless --convert-to pdf --outdir published published/claim-architecture-transition-v1.1.docx
4. python3 finalize_package.py

The illustrative series is deterministic. Parameters: Z=R=L=K=1, beta=0.35, B=0.40, q=0.70, A on a 500-point logarithmic grid from 0.1 to 1000.

The figures are comparative-statics illustrations, not empirical forecasts or calibration results.
