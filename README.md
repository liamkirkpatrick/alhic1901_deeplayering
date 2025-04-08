# alhic1901_deeplayering
Analysis of ECM and coordinated sampling in ALHIC1901 228_4 and 230_4 ice core samples

## Summary

## Instructions for use

To install this repository, first you should clone the repository with git (git clone git@github.com:UW-MLGEO/MLGEO2024_liamkp.git)
Next, create a conda environment (conda env create -f environment.yml -n YOUR_ENV_NAME_HERE)
Finally, activate the conda environment (conda activate YOUR_ENV_NAME_HERE)

All data for this project is included in the repository. This is because the datasets are quite small << 1 mb, and in simple .csv formats.

## Contents

- data
  - ECM
  - sampling
      - CFA * Contains Dartmouth CFA datasets, including abakus particle data and liquid conductivity*
      - water isotopes * Contains water isotope data*
      - GHG * Contains GHG data, including CO2 and CH4*
      - coulter Counter *Contains Coulter Counter Dusts datasets *
      - IC / ICMPS * Contains IC and ICPMS datasets *
- scripts
  - base_scripts
  - data proccessing
      - read_CFA.ipynb
      - read_GHG.ipynb
