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
    - `nrsim_lstm.py` python source code for LSTM class.
    - `lstm_test.ipynb` Notebook to test if LSTM class is functioning.
    - `cnn_lstm_test.ipynb` Notebook to test LSTM class with convolution.
    - `lstm_classification.ipynb` Notebook to train and test the Classification Model, generate confusion matrix and ROC curve.
    - `lstm_forecasting.ipynb` Notebook to run LSTM and forecast parameters of nuclear reactor simulation.

## Usage

First, clone this repository:

```
git clone git@github.com:shawnschulz/chem_277B_capstone_project.git
cd chem_277B_capstone_project
```

### Requirements

The required modules for this repository can be installed using pip:

```
pip install -r requirements.txt
```

Alternatively, you can install the latest version of the required packages individually.

```
pip install numpy tensorflow pandas scikit-learn 
```

### How to Run the Simulation

In the command line type: 'python run_simulation.py'

