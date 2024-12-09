# Chem 277B: Machine Learning Algorithms for
#            Molecular Sciences
#
# Date Created: 11/22/2024
# Last revisited: 11/29/2024




# Long Term Short Term Memory Model Class


import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense, Dropout, Reshape, \
Conv1D, MaxPooling1D, Flatten, TimeDistributed



class NRSIM_LSTM:

    def __init__(self, neurons, activation_func, 
                nTimesteps, nFeatures, npredTimesteps, npredFeatures, 
                model_optimizer, model_loss, model_metrics, 
                dropout=0, 
                conv_layer=False, nfilters=64, cact ='relu', cpool=2,
                classify=False):
        
        """
        Initialize an LSTM model

        Parameters
        ----------
        neurons : list[int]
            number of desired neurons at each layer
        activation_func: string
            activation function
        nTimesteps : int
            number of past timesteps
        nFeatures : int
            number of past features
        npredTimesteps : int
            number of predicted timesteps
        npredFeatures : int
            number of predicted features
        model_optimizer : string
            optimizer to run on model
        model_loss : string
            loss function   
        model_metrics : list[str]
            metrics 
        dropout : float
            dropout rate
        conv_layer : bool
            adds convolutional layer (optional)
        nfilters : int
            number of convolutional filters
        cact : string
            convolutional activation function
        cpool : int
            max pooling pool size
        classify: bool
            reactor saftey classification

        """
        
        

       # intitializes model
        self.model = Sequential()

        # adds convolutional layer 
        if conv_layer:

            # input layer
            self.model.add(Input(shape=(None, nTimesteps, nFeatures)))
            
            # convolutional layer
            self.model.add(TimeDistributed(Conv1D(filters = nfilters, kernel_size = 3,
                                             activation = cact)))
            # max pooling layer
            self.model.add(TimeDistributed(MaxPooling1D(pool_size=cpool)))
            self.model.add(TimeDistributed(Flatten()))
       
        else:
            
            # input layer (assuming no convolutional layer)
            self.model.add(Input(shape=(nTimesteps, nFeatures)))

        # adds lstm layers with specified number of neurons in each layer
        for L in range(len(neurons) - 1):
        
            self.model.add(LSTM(neurons[L], activation=activation_func, 
                                return_sequences=True))

            # dropout 
            if dropout > 0:
                self.model.add(Dropout(dropout)) 

        # final LSTM layer
        self.model.add(LSTM(neurons[-1], activation=activation_func, return_sequences=False))
        
        # dropout after final layer
        if dropout > 0:
            self.model.add(Dropout(dropout)) 
        

        if classify: 
            
            model_loss = "binary_crossentropy"
            
            if npredFeatures == 1:
                # output layer
                self.model.add(Dense(1, activation="sigmoid"))
            else:
                self.model.add(Dense(npredTimesteps * npredFeatures, activation="sigmoid"))
                self.model.add(Reshape((npredTimesteps, npredFeatures)))

        else:

            if npredFeatures == 1:
                # output layer
                self.model.add(Dense(npredTimesteps))
            else:
                self.model.add(Dense(npredTimesteps * npredFeatures))
                self.model.add(Reshape((npredTimesteps, npredFeatures)))

        # compiling model
        self.model.compile(optimizer=model_optimizer, loss=model_loss, metrics=model_metrics)

    def fit(self, X, y, nEpochs, nBatches, val_split, verb, shuf):
        '''fits model'''
        
        return self.model.fit(X, y, epochs=nEpochs, batch_size=nBatches, 
                       validation_split=val_split, verbose=verb, shuffle=shuf)

    
    def predict(self, X):

        '''takes in dataframe or np.array of 
        test data and generates output'''

        return self.model.predict(X)
    
    def get_model(self):
        ''' function to return model after initialization'''
        return self.model
    


    
