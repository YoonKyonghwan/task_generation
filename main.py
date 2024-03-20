import os
import json
import math
import random

from taskset_generation import generate_random_periods_discrete, generate_uunifastdiscard, generate_tasksets

def generate_available_period_list(min_period: int, max_period: int, sample_list: list = [1,2,5]) -> list:
    multiplicator = 1
    period_list = []
    
    sample_value = 1
    while(sample_value <= max_period):
        for sample in sample_list:
            sample_value = sample * multiplicator
            if min_period <= sample_value and sample_value <= max_period:
                period_list.append(sample_value)
            
            if sample_value > max_period:
                break
        multiplicator *= 10            
    
    return period_list

def generate_json_file(testset_list: list, dirname: str, filename_prefix): 
    json_object = {}
    index = 0
    task_name_dict = {}
    
    for test_index, testset in enumerate(testset_list):
        num_tasks = len(testset)
        if len(task_name_dict) == 0:
            for index in range(num_tasks):
                task_id = index + 1
                task_name_dict[str(task_id)] = "task" + str(task_id)
        json_object['idNameMap'] = task_name_dict
        
        mapping_core_list = []
        
        mapping_info_dict = {}
        mapping_info_dict['coreID'] = 1
        mapping_info_dict['tasks'] = []
        
        for idx, tuple in enumerate(testset):
            task_info_dict = {}
            exec_time = math.ceil(tuple[0])
            period = tuple[1]
            task_info_dict['id'] = idx + 1
            task_info_dict['startTime'] = 0
            task_info_dict['readTime'] = 0.0
            task_info_dict['bodyTime'] = exec_time
            task_info_dict['writeTime'] = 0.0
            task_info_dict['nice'] = 0
            task_info_dict['period'] = period
            task_info_dict['initialPriority'] = -1
            task_info_dict['index'] = idx
            mapping_info_dict['tasks'].append(task_info_dict)
        mapping_core_list.append(mapping_info_dict)
        json_object['mappingInfo'] = mapping_core_list
        
        with open(os.path.join(dirname, filename_prefix + str(test_index) + ".json"), 'w') as f:
            json.dump(json_object, f, indent=2)
            
            

# num_cores = [1] # not used
generated_files_save_dir="../generated_taskset_new"
num_tasks = [3, 6, 9, 12]
utilizations = [0.2, 0.4, 0.6]
num_sets = 50
min_period = 10000
max_period = 1000000

available_period_list = generate_available_period_list(min_period, max_period)

for num_task in num_tasks:
    for utilization in utilizations:
        period_list = generate_random_periods_discrete(num_periods=num_task, num_sets=num_sets, available_periods=available_period_list)
        utilization_list = generate_uunifastdiscard(nsets=num_sets, u=utilization, n=num_task)
        full_set = generate_tasksets(periods=period_list, utilizations=utilization_list)
        
        save_directory = os.path.join(generated_files_save_dir, "1cores", str(num_task)+"tasks", str(utilization)+"utilization")
        os.makedirs(save_directory, exist_ok=True)
        filename_prefix = "1cores_" + str(num_task)+"tasks_" + str(utilization)+"utilization_"
        generate_json_file(full_set, save_directory, filename_prefix)
        