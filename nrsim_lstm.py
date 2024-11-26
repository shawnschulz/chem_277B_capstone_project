# Chem 277B: Machine Learning Algorithms for
#            Molecular Sciences
#
# Date Created: 11/22/2024
# Last revisited: 11/22/2024




# Long Term Short Term Memory Model Class


import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Conv1D, MaxPooling1D, Flatten, TimeDistributed



class NRSIM_LSTM:

    def __init__(self, neurons, activation_func, nTimesteps, nFeatures, npredTimesteps, model_optimizer,
                  model_loss, model_metrics, conv_layer=False, nfilters=64, cact ='relu', cpool=2):
        
        """
        Initialize an LSTM model

        Parameters
        ----------
        neurons : list[int]
            number of desired neurons at each layer
        activation_func: string
            activation function
        nTimesteps : int
            number of timesteps from training data
        nFeatures : int
            number of features from training data
        npredTimesteps : int
            number of predicted timesteps
        model_optimizer : string
            optimizer to run on model
        model_loss : string
            loss function   
        model_metrics : list[str]
            metrics 
        conv_layer : bool
            adds convolutional layer (optional)
        nfilters : int
            number of convolutional filters
        cact : string
            convolutional activation function
        cpool : 
            max pooling pool size
        """
        
        

       # intitializes model
        self.model = Sequential()

        # adds convolutional layer 
        if conv_layer:
            self.model.add(TimeDistributed(Conv1D(filters = nfilters, kernel_size = 3,
                                             activation = cact), input_shape = (None, nTimesteps, nFeatures)))
            self.model.add(TimeDistributed(MaxPooling1D(pool_size=cpool)))
            self.model.add(TimeDistributed(Flatten()))
       
        # adds layers with specified number of neurons in each layer
        for L in range(len(neurons) - 1):
            if L == 0:
                self.model.add(LSTM(neurons[L], activation=activation_func, input_shape = (nTimesteps, nFeatures),  
                                    return_sequences=True))
            else:  
                self.model.add(LSTM(neurons[L], activation=activation_func, return_sequences=True))
        self.model.add(LSTM(neurons[-1], activation=activation_func, return_sequences=False))

        # output layer
        self.model.add(Dense(npredTimesteps))

        # compiling model
        self.model.compile(optimizer=model_optimizer, loss=model_loss, metrics=model_metrics)

    def fit(self, X, y, nEpochs, nBatches):
        '''fits model'''
        
        self.model.fit(X, y, epochs=nEpochs, batch_size=nBatches)

    def predict(self, X):

        '''takes in dataframe or np.array of 
        test data and generates output'''

        return self.model.predict(X)
    
    def get_model(self):
        ''' function to return model after initialization'''
        return self.model
    


    
