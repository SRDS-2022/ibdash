# ibdash
## Table of contents
[General info](#general-info)
[Setup](#setup)

## General info
This framework is intended to orchestrate applications that can be representd as DAGs on both commerical edge devices as well as personal edge devices such as phones, tablets. The framework aims at reducing the end-to-end latency and probability of failure of the application instances.

## Setup
The code listed in the report ared tested under python 3.7
To run this project, following packages are required:
```
$conda install -c anaconda networkx
$conda install -c anaconda pandas
$conda install -c anaconda numpy
$conda install -c conda-forge lightgbm
```
To profiling a personalized application on other devices, you may need the following packages:
```
$conda install -c conda-forge cpulimit
```
