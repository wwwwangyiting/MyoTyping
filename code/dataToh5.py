import h5py

def tu(imageData):
    file = h5py.File('..\\temp\\realtime_h5_data.h5', 'w')
    file.create_dataset('imageData', data=imageData)
    file.close()