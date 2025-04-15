# ALHIC1901 Deep Layering Anaysis
*Analysis of ECM and coordinated sampling in ALHIC1901 228_4 and 230_4 ice core samples*

## Summary

## Instructions for use

We assume you have Python and conda conda installed.

To install this repository:
- first you should clone the repository with git (git clone git@github.com:liamkirkpatrick/alhic1901_deeplayering.git)
- Next, create a conda environment (conda env create -f environment.yml -n YOUR_ENV_NAME_HERE)
- Finally, activate the conda environment (conda activate YOUR_ENV_NAME_HERE)

All data for this project is included in the repository. This is because the datasets are quite small << 1 mb, and in simple .csv formats.

## Contents

- **data/**
  - **ECM/**
      - **raw/** - *contains ECM datafiles, with a seperate file for each face*
      - **alligned/** - *same data files as raw, but with the depth adjusted on the l and r faces to allign with the top face (and so correct depth*
  - **angles/** - *Contains layer orientation data*
  - **sampling/**
      - **CFA/** - *Contains Dartmouth CFA datasets, including abakus particle data and liquid conductivity*
      - **water isotopes/** - *Contains water isotope data*
      - **GHG/** - *Contains GHG data, including CO2 and CH4*
      - **coulter_counter/** - *Contains Coulter Counter Dusts datasets*
      - **ic_icpms/** - *Contains IC and ICPMS datasets*
      - **master/** - *contains a master spreadsheet for each set of data, including correct depths and dip-adjusted depths. This should be the go-to for accessing and using this data, as it is in a more proccessed state than above.
      - **metadata.csv** - *.csv file contains basic cut information on each stick, used to calculate the dip-adjustment*
- **scripts/**
  - **base_scripts/**
      - **ECMclass.py** - *olds class for single face and section. Very useful for loading and proccessing ECM data files*
  - **angle_calcs/**
      - **calc_angles.ipynb** - *Compute angle on individual faces, and true dip of both sections, using weighted mean approach*
  - **data proccessing/**
      - **proccess_ecm.ipynb** - *compute dip-adjusted depth for ECM data*
      - **proccess_samples.ipynb** - *prepare master .csv for all files except for the ecm data*
