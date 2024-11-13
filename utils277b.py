# Chem 277B: Machine Learning Algorithms for
#            Molecular Sciences
#
# Date Created: 11/12/2024
# Last revisited: 11/13/2024


''' 
----------------------------------
UTILITY FUNCTIONS FOR 277B PROJECT 
----------------------------------
'''



# Imports
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import  KFold, cross_val_score
from sklearn.decomposition import PCA
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV




def rmse(y_true: np.ndarray , y_pred: np.ndarray):
    # calculates rmse
    return np.sqrt(mean_squared_error(y_true, y_pred))

def cross_validation_accuracy(model, X: pd.DataFrame, y: np.ndarray, nKFold: int):
    '''
    Inputs: 
    model - model used for fitting
    X - DataFrame for training
    y - np.array of training values
    
    Returns:

    avg accuracy over cross validation
    '''
    kf = KFold(n_splits=nKFold, shuffle=True)
    accuracies = cross_val_score(model, X, y, cv=kf)     
    return np.mean(accuracies)

def scale(data: np.ndarray):
    # for scaling
    scaler = MinMaxScaler(feature_range=(0,1))
    return scaler.fit_transform(data)

def plot_correlation_matrix(data: pd.DataFrame, title: str):
    
    ''' 
    Inputs: 
    data - Dataframe or np.array
    title - Correlation Matrix title

    Returns: 
    Corr_Matrix - pd.DataFrame with correlation values
    ax - Matplotlib axes object for plotting
    '''
    
    # converts numpy array to DataFrame
    if type(data) == np.ndarray:
        data = pd.DataFrame(data)
    
    # computes correlation matrix
    Corr_Matrix = data.corr(method="pearson", numeric_only=True)
    ax = sns.heatmap(Corr_Matrix, annot=True, vmin=-0.05, vmax=1)
    ax.set_title(title)

    return Corr_Matrix, ax

def plot_confusion_matrix(y_true: np.ndarray, y_pred: np.ndarray, title: str):
    ''' Inputs: 
    y_true - array of true values
    y_pred - array of predicted values
    title - plot title
    
    Returns: 
    cm - np.ndarray (confusion matrix)
    ax - confusion matrix plot
    '''
    featlabels = np.unique(np.sort(y_true))
    Conf_Matrix = confusion_matrix(y_true, y_pred)
    ax = sns.heatmap(Conf_Matrix, annot = True, fmt = 'd', cmap = 'Blues',\
    xticklabels = featlabels, yticklabels = featlabels)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('True')
    ax.set_title(title)

    return Conf_Matrix, ax

def principal_component_analysis(train_data: pd.DataFrame, test_data: pd.DataFrame):
   
    ''' 
    Inputs: 
    train_data - Dataframe or np.array
    test_data - Dataframe or np.array

    Returns: 
    pca_fit - PCA model
    evecTrain - Eigen Vectors
    evalTrain - Eigen Values
    TTrain - Transformed Training Data
    TTest -  Transformed Testing Data 
    fig - Eigen Value bar plot
    '''

    # converts numpy array to DataFrame
    if type(train_data) == np.ndarray:
        train_data = pd.DataFrame(train_data)
    if type(test_data) == np.ndarray:
        test_data = pd.DataFrame(test_data)
   
    # Runs PCA 
    pca_fit = PCA(n_components = train_data.shape[1]).fit(train_data.values) 
    evecTrain = pca_fit.components_
    evalTrain = pca_fit.explained_variance_
    TTrain = pca_fit.transform(train_data.values)
    TTest = pca_fit.transform(test_data.values)

    # Eigenvalue Logarithmic Plot 
    fig, ax = plt.subplots()
    ax.bar(np.arange(1, train_data.shape[1] + 1), evalTrain, color = (0.8, 0.8, 0.8), edgecolor = "black")
    ax.set_xlabel("dimension")
    ax.set_ylabel("eigenvalue")
    ax.set_yscale("log")
  
    return pca_fit, evecTrain, evalTrain, TTrain, TTest, fig



def best_model(param_grid: dict, model, X: pd.DataFrame, y: np.ndarray, nKFold: int):
     
    ''' 
    Inputs: 
    param_grid - parameter grid (alpha) 
    model - regression type (l1, l2, RandomForest, etc.)
    X - Test Data
    y - Labels
    nKFold - number of Kfold cross validations

    Returns: 
    optimized model from grid search
    '''
    
    grid_search = GridSearchCV(estimator=model, param_grid=param_grid, cv=nKFold)
    grid_search.fit(X, y)
    
    return grid_search.best_estimator_



