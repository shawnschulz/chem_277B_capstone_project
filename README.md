# Chem 277B Capstone Project

## Simulation and State Prediction of Nuclear Reactor Water Chemistry Using LSTM Neural Networks

### Contents

This repository contains the following files:

- A README in markdown format contains documentation of the repositiory.
- The following folders:
    - `Archive` contains previous iterations of past work.
    - `Plots` contains several plots of LSTM predictions versus individual casualties.
    - `Simulation Data` contains CSV files used for training models.
    - `Randomized Search` contains Jupyter notebooks used for Randomized Search hyperparameter tuning
- The following files:
    - `NR_simulation.py` python source code for generating an artificial dataset, simulating a nuclear reactor.
    - `run_simulation.py` python source for running the simulation.
    - `lstm_classification.ipynb` Notebook to run the Classification Model, generate confusion matrix and ROC curve
    - And a bunch of other files where we performed LSTM modelling and evaluation.

### How to Run the Simulation

In the command line type: 'python run_simulation.py'

