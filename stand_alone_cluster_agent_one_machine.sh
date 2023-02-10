#!/bin/bash

folder_path="/nfs/obelix/raid2/msavasci/pipeline-structure/"
saved_data_path="/nfs/obelix/raid2/msavasci/pipeline-structure/saved-data/"

cluster_agent="cluster_agent_server_level.py"

app1="Mediawiki"
app2="SocialNetwork"
selected_app=$app2

selected_app_web_path1="/gw/"
selected_app_web_path2="/wrk2-api/"
selected_app_path=$selected_app_web_path2

controller_parameters="SocialNetworkModelParameters-60-ten-percent-t.txt"

allocated_power_file="allocatedPower-"
estimated_power_file="estimatedPower-"
response_time_file="responseTimes-"
log_file="log-"
error="errors-"
drop="dropRate-"
estimated_request="estimatedNumberOfRequest-"
pterm="pTerms-"
iterm="iTerms-"
operation_point="operatingPointValues-"
integrator="integrators-"
integrator_switch="integratorSwitch-"
residual_power="residualPower-"
corrected_power="correctedPower-"

tuning_percentage="ten-percent-t"
experiment_number="466-"
extension=".txt"


sudo python3 ${folder_path}${cluster_agent} -nl 180 -st 1 -t 0.1 -ri 0.35 -th 5 -p ${selected_app_path} -sf ${folder_path}${controller_parameters} -ap ${saved_data_path}${allocated_power_file}${experiment_number}${tuning_percentage}${extension} -ep ${saved_data_path}${estimated_power_file}${experiment_number}${tuning_percentage}${extension} -rt ${saved_data_path}${response_time_file}${experiment_number}${tuning_percentage}${extension} -lf ${saved_data_path}${log_file}${experiment_number}${tuning_percentage}${extension} -ev ${saved_data_path}${error}${experiment_number}${tuning_percentage}${extension} -dp ${saved_data_path}${drop}${experiment_number}${tuning_percentage}${extension} -er ${saved_data_path}${estimated_request}${experiment_number}${tuning_percentage}${extension} -pt ${saved_data_path}${pterm}${experiment_number}${tuning_percentage}${extension} -it ${saved_data_path}${iterm}${experiment_number}${tuning_percentage}${extension} -op ${saved_data_path}${operation_point}${experiment_number}${tuning_percentage}${extension} -in ${saved_data_path}${integrator}${experiment_number}${tuning_percentage}${extension} -is ${saved_data_path}${integrator_switch}${experiment_number}${tuning_percentage}${extension}


# sudo python3 ${folder_path}${cluster_agent} -nl 180 -st 1 -t 0.1 -p ${selected_app_path} -sf ${folder_path}${controller_parameters} -ri 1.0 -ap ${saved_data_path}${allocated_power_file}${experiment_number}${tuning_percentage}${extension} -ep ${saved_data_path}${estimated_power_file}${experiment_number}${tuning_percentage}${extension} -rt ${saved_data_path}${response_time_file}${experiment_number}${tuning_percentage}${extension} -lf ${saved_data_path}${log_file}${experiment_number}${tuning_percentage}${extension} -ev ${saved_data_path}${error}${experiment_number}${tuning_percentage}${extension} -dp ${saved_data_path}${drop}${experiment_number}${tuning_percentage}${extension} -er ${saved_data_path}${estimated_request}${experiment_number}${tuning_percentage}${extension} -pt ${saved_data_path}${pterm}${experiment_number}${tuning_percentage}${extension} -it ${saved_data_path}${iterm}${experiment_number}${tuning_percentage}${extension} -op ${saved_data_path}${operation_point}${experiment_number}${tuning_percentage}${extension} -in ${saved_data_path}${integrator}${experiment_number}${tuning_percentage}${extension} -is ${saved_data_path}${integrator_switch}${experiment_number}${tuning_percentage}${extension}