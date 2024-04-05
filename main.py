import os
import json
import math
import argparse

from taskset_generation import generate_random_periods_discrete, generate_uunifastdiscard, generate_tasksets

def generate_available_period_list(min_period: int, max_period: int, sample_list: list = [1,2,3,5]) -> list:
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

def get_min_period(testset: list) -> int:
    min_period = max_period
    for tuple in testset:
        period = tuple[1]
        if(period < min_period):
            min_period = period
    return min_period

def set_nice_value_by_deadline(period: int, min_period: int):
    nice_value = -19
    period_inc = min_period
    while(period_inc < period and nice_value < 19):
        period_inc = (period_inc * 5) / 4
        nice_value += 1
    return nice_value

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
        min_period_in_testset = get_min_period(testset)
        
        for idx, tuple in enumerate(testset):
            task_info_dict = {}
            exec_time = math.ceil(tuple[0])
            period = tuple[1]
            task_info_dict['id'] = idx + 1
            task_info_dict['startTime'] = 0
            task_info_dict['readTime'] = 0.0
            task_info_dict['bodyTime'] = exec_time
            task_info_dict['writeTime'] = 0.0
            task_info_dict['nice'] = set_nice_value_by_deadline(period=period, min_period=min_period_in_testset)
            #task_info_dict['nice'] = 0
            task_info_dict['period'] = period
            task_info_dict['initialPriority'] = -1
            task_info_dict['index'] = idx
            mapping_info_dict['tasks'].append(task_info_dict)
        mapping_core_list.append(mapping_info_dict)
        json_object['mappingInfo'] = mapping_core_list
        
        with open(os.path.join(dirname, filename_prefix + str(test_index) + ".json"), 'w') as f:
            json.dump(json_object, f, indent=2)
            
            
            
if __name__ == "__main__":
    # num_cores = [1] # not used
    parser = argparse.ArgumentParser()
    parser.add_argument("-g", "--generated_files_save_dir", type=str, default="generated_tasksets", help="Directory to save generated tasksets")
    parser.add_argument("-n", "--num_tasksets", type=int, default=3, help="Number of tasks in a taskset")
    parser.add_argument("--min_period", type=int, default=30000, help="Minimum period of tasks(us)")
    parser.add_argument("--max_period", type=int, default=1000000, help="Maximum period of tasks(us)")
    args = parser.parse_args()
    generated_files_save_dir= args.generated_files_save_dir
    num_sets = args.num_tasksets
    min_period = args.min_period
    max_period = args.max_period
    num_tasks = [3, 6, 9, 12]
    utilizations = [0.4, 0.6, 0.8]

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
            
