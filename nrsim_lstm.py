# Chem 277B: Machine Learning Algorithms for
#            Molecular Sciences
#
# Date Created: 11/22/2024
# Last revisited: 11/22/2024




# Long Term Short Term Memory Model Class


import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, LSTM, Dense, Reshape



class NRSIM_LSTM:

    def __init__(self, neurons, activation_func, nTimesteps, nFeatures, npredTimesteps, model_optimizer, model_loss):
        
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
        """
        
        

        # input layer
        input_layer = Input(shape=(nTimesteps, nFeatures))

        # adds LSTM layers with specified number of neurons in each layer
        x = LSTM(neurons[0], activation=activation_func, return_sequencs=True)(input_layer)
        for L in range(1, len(neurons) - 1):
           x = LSTM(neurons[L], activation=activation_func, return_sequences=True)(x)
        x = LSTM(neurons[-1], activation=activation_func, return_sequences=False)(x)

        # output layer
        x = Dense(npredTimesteps * nFeatures)(x)
        output = Reshape((npredTimesteps, nFeatures))(x)
        
        # model
        self.model = Model(inputs=input_layer, outputs=output)

        # compiling model
        self.model.compile(optimizer=model_optimizer, loss=model_loss)

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
    


    
