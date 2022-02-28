import numpy as np
import h5py

def convert_to_one_hot(Y, C):
    Y = np.eye(C)[Y.reshape(-1)].T
    return Y

def pred(model):
    fileTest = h5py.File('..\\temp\\realtime_h5_data.h5', 'r')
    imageDataTest = fileTest['imageData'][:]
    fileTest.close()
    imageDataTest = np.expand_dims(imageDataTest, axis=0)
    imageDataTest = np.expand_dims(imageDataTest, axis=3)
    pre = model.predict(imageDataTest)
    pred = [np.argmax(one_hot) for one_hot in pre]
    print("The predictive value is:",pred)
    return pred[0]