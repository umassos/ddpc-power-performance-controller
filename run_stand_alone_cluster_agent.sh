#!/bin/bash

folder_path="/workspace/pipeline-structure/"
saved_data_path="/workspace/pipeline-structure/saved-data/"

cluster_agent="cluster_agent_with_multiple_policy_options.py"

app1="Mediawiki"
app2="SocialNetwork"
selected_app=$app1

selected_app_web_path1="/gw/"
selected_app_web_path2="/wrk2-api/"
selected_app_path=$selected_app_web_path1

# controller_parameters="MediawikiControllerParameters-8-t-10.txt"
# controller_parameters="SocialNetworkControllerParameters-overMatlab.txt"
controller_parameters="MediawikiControllerParameters-overMatlab.txt"

log_file="log-"
allocated_power_file="allocatedPower-"
estimated_power_file="estimatedPower-"
response_time_file="responseTimes-"
error="errors-"
drop="dropRate-"
estimated_request="estimatedNumberOfRequest-"
pterm="pTerms-"
iterm="iTerms-"
operation_point="operatingPointValues-"
integrator="integrators-"
integrator_switch="integratorSwitch-"
used_machines="numberOfUsedMachines-"

tuning_percentage="ten-percent-t"
experiment_number="149-"
extension=".txt"

sudo python3 ${folder_path}${cluster_agent} -t 0.1 -nl 360 -st 1 -ri 1.0 -pb 160 -p1 ${selected_app_web_path1} -sf1 ${folder_path}${controller_parameters} -lf ${saved_data_path}${log_file}${experiment_number}${tuning_percentage}${extension} -ap1 ${saved_data_path}${allocated_power_file}${experiment_number}${tuning_percentage}${extension} -ep1 ${saved_data_path}${estimated_power_file}${experiment_number}${tuning_percentage}${extension} -rt1 ${saved_data_path}${response_time_file}${experiment_number}${tuning_percentage}${extension} -ev1 ${saved_data_path}${error}${experiment_number}${tuning_percentage}${extension} -dp1 ${saved_data_path}${drop}${experiment_number}${tuning_percentage}${extension} -er1 ${saved_data_path}${estimated_request}${experiment_number}${tuning_percentage}${extension} -pt1 ${saved_data_path}${pterm}${experiment_number}${tuning_percentage}${extension} -it1 ${saved_data_path}${iterm}${experiment_number}${tuning_percentage}${extension} -op1 ${saved_data_path}${operation_point}${experiment_number}${tuning_percentage}${extension} -in1 ${saved_data_path}${integrator}${experiment_number}${tuning_percentage}${extension} -is1 ${saved_data_path}${integrator_switch}${experiment_number}${tuning_percentage}${extension} -um1 ${saved_data_path}${used_machines}${experiment_number}${tuning_percentage}${extension}

# sudo python3 ${folder_path}${cluster_agent} -t 0.1 -nl 140 -st 1 -lf ${saved_data_path}${selected_app}${log_file}${experiment_number}${tuning_percentage}${extension} -em ${saved_data_path}${selected_app}${enabled_machines}${experiment_number}${tuning_percentage}${extension} -rp ${saved_data_path}${selected_app}${residual_power}${experiment_number}${tuning_percentage}${extension} -cp ${saved_data_path}${selected_app}${corrected_power}${experiment_number}${tuning_percentage}${extension} -um ${saved_data_path}${selected_app}${used_machines}${experiment_number}${tuning_percentage}${extension} -ap ${saved_data_path}${selected_app}${allocated_power_file}${experiment_number}${tuning_percentage}${extension} -p1 ${selected_app_web_path1} -sf1 ${folder_path}${app1}${controller_parameters}${experiment_no_mediawiki}${tuning_percentage}${extension} -ep1 ${saved_data_path}${app1}${estimated_power_file}${experiment_number}${tuning_percentage}${extension} -rt1 ${saved_data_path}${app1}${response_time_file}${experiment_number}${tuning_percentage}${extension} -ev1 ${saved_data_path}${app1}${error}${experiment_number}${tuning_percentage}${extension} -dp1 ${saved_data_path}${app1}${drop}${experiment_number}${tuning_percentage}${extension} -er1 ${saved_data_path}${app1}${estimated_request}${experiment_number}${tuning_percentage}${extension} -pt1 ${saved_data_path}${app1}${pterm}${experiment_number}${tuning_percentage}${extension} -it1 ${saved_data_path}${app1}${iterm}${experiment_number}${tuning_percentage}${extension} -op1 ${saved_data_path}${app1}${operation_point}${experiment_number}${tuning_percentage}${extension} -in1 ${saved_data_path}${app1}${integrator}${experiment_number}${tuning_percentage}${extension} -is1 ${saved_data_path}${app1}${integrator_switch}${experiment_number}${tuning_percentage}${extension} -um1 ${saved_data_path}${app1}${used_machines}${experiment_number}${tuning_percentage}${extension} -cp1 ${saved_data_path}${app1}${corrected_power}${experiment_number}${tuning_percentage}${extension} -p2 ${selected_app_web_path2} -sf2 ${folder_path}${app2}${controller_parameters}${experiment_no_mediawiki}${tuning_percentage}${extension} -ep2 ${saved_data_path}${app2}${estimated_power_file}${experiment_number}${tuning_percentage}${extension} -rt2 ${saved_data_path}${app2}${response_time_file}${experiment_number}${tuning_percentage}${extension} -ev2 ${saved_data_path}${app2}${error}${experiment_number}${tuning_percentage}${extension} -dp2 ${saved_data_path}${app2}${drop}${experiment_number}${tuning_percentage}${extension} -er2 ${saved_data_path}${app2}${estimated_request}${experiment_number}${tuning_percentage}${extension} -pt2 ${saved_data_path}${app2}${pterm}${experiment_number}${tuning_percentage}${extension} -it2 ${saved_data_path}${app2}${iterm}${experiment_number}${tuning_percentage}${extension} -op2 ${saved_data_path}${app2}${operation_point}${experiment_number}${tuning_percentage}${extension} -in2 ${saved_data_path}${app2}${integrator}${experiment_number}${tuning_percentage}${extension} -is2 ${saved_data_path}${app2}${integrator_switch}${experiment_number}${tuning_percentage}${extension} -um2 ${saved_data_path}${app2}${used_machines}${experiment_number}${tuning_percentage}${extension} -cp2 ${saved_data_path}${app2}${corrected_power}${experiment_number}${tuning_percentage}${extension} -p3 ${selected_app_web_path3} -sf3 ${folder_path}${app3}${controller_parameters}${experiment_no_mediawiki}${tuning_percentage}${extension} -ep3 ${saved_data_path}${app3}${estimated_power_file}${experiment_number}${tuning_percentage}${extension} -rt3 ${saved_data_path}${app3}${response_time_file}${experiment_number}${tuning_percentage}${extension} -ev3 ${saved_data_path}${app3}${error}${experiment_number}${tuning_percentage}${extension} -dp3 ${saved_data_path}${app3}${drop}${experiment_number}${tuning_percentage}${extension} -er3 ${saved_data_path}${app3}${estimated_request}${experiment_number}${tuning_percentage}${extension} -pt3 ${saved_data_path}${app3}${pterm}${experiment_number}${tuning_percentage}${extension} -it3 ${saved_data_path}${app3}${iterm}${experiment_number}${tuning_percentage}${extension} -op3 ${saved_data_path}${app3}${operation_point}${experiment_number}${tuning_percentage}${extension} -in3 ${saved_data_path}${app3}${integrator}${experiment_number}${tuning_percentage}${extension} -is3 ${saved_data_path}${app3}${integrator_switch}${experiment_number}${tuning_percentage}${extension} -um3 ${saved_data_path}${app3}${used_machines}${experiment_number}${tuning_percentage}${extension} -cp3 ${saved_data_path}${app3}${corrected_power}${experiment_number}${tuning_percentage}${extension}
