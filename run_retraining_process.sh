#!/bin/bash

folder_path="/nfs/obelix/raid2/msavasci/pipeline-structure/"
saved_data_path="/nfs/obelix/raid2/msavasci/pipeline-structure/saved-data/"

controller_generator_folder_path="/Users/msavasci/Desktop/Research/Obelix-Pipeline-Structure/"

measurement_program="measurement_program_side.py"
workload_generator="workload_generator_side.py"
model_generator="model_generator.py"
pi_controller="controller_generator.py"

app1="Mediawiki"
app2="SocialNetwork"
selected_app=$app2

selected_app_web_path1="/gw/"
selected_app_web_path2="/wrk2-api/"
selected_app_path=$selected_app_web_path2

log_file_path="/var/log/haproxy.log"
comm_port=8098

initial_power_budget_level=30
increase_in_power_budget_level=2
final_power_budget_level=48
expose_duration_to_power_budget_level=10

initial_number_of_request=$1
increase_in_number_of_request=10
final_number_of_request=$((initial_number_of_request+40))
expose_duration_to_request=$(((((final_power_budget_level-initial_power_budget_level)/increase_in_power_budget_level)+1)*expose_duration_to_power_budget_level))

experiment_duration=$(((((final_number_of_request-initial_number_of_request)/increase_in_number_of_request)+1)*expose_duration_to_request))

collected_data="CollectedData-"
workload_output="WorkloadOutput-"
model_parameters="ModelParameters-"
controller_parameters="ControllerParameters-"

tuning_percentage="ten-percent-t"
experiment_number="10-"
extension=".txt"

# To run measurement program
message_to_measurement_program="sudo python3 ${folder_path}${measurement_program} -H 192.168.245.97 -po ${comm_port} -H1 192.168.245.54 -po1 8054 -ip ${initial_power_budget_level} -i ${increase_in_power_budget_level} -fp ${final_power_budget_level} -pd ${expose_duration_to_power_budget_level} -s 0 -p ${selected_app_path} -lf ${log_file_path} -f ${folder_path}${selected_app}${collected_data}${experiment_number}${tuning_percentage}${extension}"

# To run workload generator program
message_to_workload_generator="python3 ${folder_path}${workload_generator} -H 192.168.245.97 -p 8060 -po ${comm_port} -n ${initial_number_of_request} -i ${increase_in_number_of_request} -l ${final_number_of_request} -rd ${expose_duration_to_request}"

# To run model generator program
message_to_model_generator="python3 ${folder_path}${model_generator} -n ${initial_number_of_request} -i ${increase_in_number_of_request} -l ${final_number_of_request} -sf ${folder_path}${selected_app}${collected_data}${experiment_number}${tuning_percentage}${extension} -df ${folder_path}${selected_app}${model_parameters}${experiment_number}${tuning_percentage}${extension}"

# To run controller generator program
message_to_controller_generator="python3.7 ${controller_generator_folder_path}${pi_controller} -sf ${controller_generator_folder_path}${selected_app}${model_parameters}${experiment_number}${tuning_percentage}${extension} -df ${controller_generator_folder_path}${selected_app}${controller_parameters}${experiment_number}${tuning_percentage}${extension}"

# To initialize the pipeline
python3 client_app_retrain_new.py -d $experiment_duration -s "${folder_path}${selected_app}${model_parameters}${experiment_number}${tuning_percentage}${extension}" -f "${controller_parameters}${experiment_number}${tuning_percentage}${extension}" -mm "${message_to_measurement_program}" -mw "${message_to_workload_generator}" -mg "${message_to_model_generator}" -mp "${message_to_controller_generator}" -mc "${message_to_cluster_manager}"