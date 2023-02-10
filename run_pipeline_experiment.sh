#!/bin/bash

folder_path="/nfs/obelix/raid2/msavasci/pipeline-structure/"
saved_data_path="/nfs/obelix/raid2/msavasci/pipeline-structure/saved-data/"

controller_generator_folder_path="/Users/msavasci/Desktop/Research/Obelix-Pipeline-Structure/"

measurement_program="measurement_program_side.py"
workload_generator="workload_generator_side.py"

model_generator="model_generator.py"
pi_controller="controller_generator.py"
cluster_agent="cluster_agent_server_level.py"

app1="Mediawiki"
app2="SocialNetwork"
selected_app=$app2

selected_app_web_path1="/gw/"
selected_app_web_path2="/wrk2-api/"
selected_app_path=$selected_app_web_path2

log_file_path="/var/log/haproxy.log"
comm_port=8094

initial_power_budget_level=30
increase_in_power_budget_level=2
final_power_budget_level=58
expose_duration_to_power_budget_level=10

initial_number_of_request=20
increase_in_number_of_request=20
final_number_of_request=160
expose_duration_to_request=$(((((final_power_budget_level-initial_power_budget_level)/increase_in_power_budget_level)+1)*expose_duration_to_power_budget_level))

experiment_duration=$(((((final_number_of_request-initial_number_of_request)/increase_in_number_of_request)+1)*expose_duration_to_request))

collected_data="CollectedData-"
workload_output="WorkloadOutput-"
model_parameters="ModelParameters-"
controller_parameters="ControllerParameters-"

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
experiment_number="60-"
extension=".txt"

message_to_measurement_program="sudo python3 ${folder_path}${measurement_program} -H 192.168.245.97 -po ${comm_port} -H1 192.168.245.54 -po1 8099 -ip ${initial_power_budget_level} -i ${increase_in_power_budget_level} -fp ${final_power_budget_level} -pd ${expose_duration_to_power_budget_level} -s 0 -p ${selected_app_path} -lf ${log_file_path} -f ${folder_path}${selected_app}${collected_data}${experiment_number}${tuning_percentage}${extension}"

message_to_workload_generator="python3 ${folder_path}${workload_generator} -H 192.168.245.97 -p 8060 -po ${comm_port} -n ${initial_number_of_request} -i ${increase_in_number_of_request} -l ${final_number_of_request} -rd ${expose_duration_to_request}"

message_to_model_generator="python3 ${folder_path}${model_generator} -n ${initial_number_of_request} -i ${increase_in_number_of_request} -l ${final_number_of_request} -sf ${folder_path}${selected_app}${collected_data}${experiment_number}${tuning_percentage}${extension} -df ${folder_path}${selected_app}${model_parameters}${experiment_number}${tuning_percentage}${extension}"

message_to_controller_generator="python3.7 ${controller_generator_folder_path}${pi_controller} -sf ${controller_generator_folder_path}${selected_app}${model_parameters}${experiment_number}${tuning_percentage}${extension} -df ${controller_generator_folder_path}${selected_app}${controller_parameters}${experiment_number}${tuning_percentage}${extension}"

message_to_cluster_manager="python3 ${folder_path}${cluster_agent} -nl 180 -st 1 -t 0.1 -ri 1.0 -th 5 -p ${selected_app_path} -sf ${folder_path}${controller_parameters} -ap ${saved_data_path}${allocated_power_file}${experiment_number}${tuning_percentage}${extension} -ep ${saved_data_path}${estimated_power_file}${experiment_number}${tuning_percentage}${extension} -rt ${saved_data_path}${response_time_file}${experiment_number}${tuning_percentage}${extension} -lf ${saved_data_path}${log_file}${experiment_number}${tuning_percentage}${extension} -ev ${saved_data_path}${error}${experiment_number}${tuning_percentage}${extension} -dp ${saved_data_path}${drop}${experiment_number}${tuning_percentage}${extension} -er ${saved_data_path}${estimated_request}${experiment_number}${tuning_percentage}${extension} -pt ${saved_data_path}${pterm}${experiment_number}${tuning_percentage}${extension} -it ${saved_data_path}${iterm}${experiment_number}${tuning_percentage}${extension} -op ${saved_data_path}${operation_point}${experiment_number}${tuning_percentage}${extension} -in ${saved_data_path}${integrator}${experiment_number}${tuning_percentage}${extension} -is ${saved_data_path}${integrator_switch}${experiment_number}${tuning_percentage}${extension}"

python3 client_app_52_new.py -d $experiment_duration -s "${folder_path}${selected_app}${model_parameters}${experiment_number}${tuning_percentage}${extension}" -f "${controller_parameters}${experiment_number}${tuning_percentage}${extension}" -mm "${message_to_measurement_program}" -mw "${message_to_workload_generator}" -mg "${message_to_model_generator}" -mp "${message_to_controller_generator}" -mc "${message_to_cluster_manager}"