# ibdash
## Table of contents
[General info](#general-info)

[Setup](#setup)

## General info
This framework is intended to orchestrate applications that can be representd as DAGs on both commerical edge devices as well as personal edge devices such as phones, tablets. The framework aims at reducing the end-to-end latency and probability of failure of the application instances.

## Setup
The code listed in the repository are tested under python 3.7
To run this project, following packages are required:
```
$conda install -c anaconda networkx
$conda install -c anaconda pandas
$conda install -c anaconda numpy
$conda install -c conda-forge lightgbm
```
In the profile_data folder, we have included the profiling data for the 4 testing application for AWS devices and a MacBook pro.
To profiling a personalized application on other devices, you may need the following packages:
```
$conda install -c conda-forge cpulimit
$conda install -c conda-forge opencv
```
There are six orchestration frame available (IBDASH + 5 baseline), you can run them seperately by commant out the unwannted scheme in ibdash.py. 
To execute ibdash.py, you will need to specify the application need to be orchestarted with --app identifier, and the profiling data matrix with --mc identifier. Moreover, you can control the probability of failure threshold with --pf (default = 0.25), the replication degreee with --rd (default = 0.3), and the joint optimization parameter with --jp (default = 0.5).
An sample command for execution 
```
$python ibdash.py --app lightgbm --mc ED_mcgbm.xlsx 
```
which runs the orchestration for lightgbm application


