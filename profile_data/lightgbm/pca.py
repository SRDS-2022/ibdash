from numpy import array
from numpy import mean
from numpy import cov
from numpy.linalg import eig
from numpy import genfromtxt
from numpy import concatenate
from numpy import savetxt
import numpy as np

import json
import random
import time
import io
import time as timer

start=timer.time()
train_data = genfromtxt("Digits_Train.txt")
train_labels = train_data[:,0]

A = train_data[:,1:train_data.shape[1]]


# calculate the mean of each column
MA = mean(A.T, axis=1)


# center columns by subtracting column means
CA = A - MA


# calculate covariance matrix of centered matrix
VA = cov(CA.T)

# eigendecomposition of covariance matrix
values, vectors = eig(VA)

# project data
PA = vectors.T.dot(CA.T)

#np.save("vectors_pca.txt", vectors)

first_n_A = PA.T[:,0:10].real
train_labels =  train_labels.reshape(train_labels.shape[0],1)

first_n_A_label = concatenate((train_labels, first_n_A), axis=1)

#savetxt("Digits_Train_Transform.txt", first_n_A_label, delimiter="\t")
end=timer.time()
print("pca: "+str((end-start)/100))