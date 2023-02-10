## This repo includes server and cluster level implementation of DDPC

### Application Profiler: This is one of the most complicated component of proposed system. It is responsible of initializing workload generator and measuring application response time. We designed application profiler in a way such that it can do both these tasks simultaneously considering order of execution.

### Model Generator: This Python script receives application profiling data as an input and gives ARX model parameters of different workload levels as an output for controller generator to be used to compute PI controller parameters.

### DDPC Controller Generator: The controller generator is implemented using Python3 and Matlab. The main implementation is on the Python side but the Python script call Matlab script to compute controller parameters. The controller generation is at the heart of the system because computing parameter values appropriately plays a significant role in performance of the cluster power manager. As soon as controller parameters are computed, this is reported to the power-performance monitor directly.

### Application Performance Monitor: The monitor locates at the top of load-balancer server. It periodically interacts with the load-balancer log file to keep track and analyze of application response time. It works in real-time and reports average application response time to cluster power manager. It is also capable of tracking and logging drop rate of requests coming to application.

### Cluster Power Manager: This is the main component that implements the power allocation logic considering application target response time. The manager has designed as a modular. This can give anyone an advantage to use different types of managers by replacing the our manager with the one that has another policy. It waits without doing anything if there is no update from performance monitor. Once it receives an update from monitor, it estimates required power and inform local managers to cap this power on their servers. The communication between global power-performance cluster agent and local agent is established over sockets.

### Local Manager: Local managers are small hidden heroes of our system. Although they have less than 80 Python LOCs, they have quite important role. They receive allocated power data information from cluster power manager via socket connection and apply this using RAPL interface.

### In profiling, measurement program and workload generator are used. These scripts are measurement_program_side.py and workload_generator_side.py

### Model parameters are generated using model_generator.py.

### Controller parameters are generated using controller_generator.py. This script uses pi_controller_generator.m.

### DDPC Pipeline is started using run_pipeline_experiment.sh.

### Retraining process is happening using run_retraining_process.sh

### server_app_*_new.py scripts are responsible for starting related program. For example, server_app_73_new.py is responsible for starting workload generator.

[![DOI](https://zenodo.org/badge/600198295.svg)](https://zenodo.org/badge/latestdoi/600198295)