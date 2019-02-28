from battery_combinations import battery_combinations

frame_weight_mapping = {
    50: 500,
    70: 1000,
    90: 2000,
    120: 3000,
    150: 4000,
    200: 5000,
    250: 6000
}

min_accepted_fly_time = 5

min_accepted_payload = 0

def estimate_frame_weight(num_edf, edf):
    if edf.size in frame_weight_mapping:
        frame_weight = frame_weight_mapping[edf.size]
    else:
        closest_size = min(frame_weight_mapping.keys(), key=lambda x:abs(x-edf.size))
        frame_weight = frame_weight_mapping[closest_size]
    if num_edf == 3:
        frame_weight *= 0.75
    return frame_weight

def drone_specs(num_edf, edf, esc, battery, additional_weight):
    specs = {}
    specs['edf_name'] = edf.edf_name
    specs['num_edf'] = num_edf
    specs['esc_name'] = esc.esc_name
    specs['battery_name'] = battery.battery_name
    frame_weight = estimate_frame_weight(num_edf, edf)
    specs['total_weight'] = num_edf * edf.weight + num_edf * esc.weight + battery.weight + frame_weight + additional_weight
    specs['total_thrust'] = num_edf * edf.thrust
    specs['max_payload'] = specs['total_thrust'] - specs['total_weight']
    specs['total_power_capacity'] = battery.capacity
    specs['max_current_consumption'] = num_edf * edf.current_consumption
    specs['min_fly_time'] = specs['total_power_capacity'] / specs['max_current_consumption'] * 60
    specs['hover_power'] = specs['total_weight'] / specs['total_thrust']
    specs['hover_time'] = specs['min_fly_time'] / specs['hover_power']
    return specs

def valid_combination(num_edf, edf, esc, battery, specs):
    return (edf.battery_type == battery.cells and
            edf.battery_type >= esc.battery_cells_min and
            edf.battery_type <= esc.battery_cells_max and
            edf.current_consumption <= esc.current and
            num_edf * edf.current_consumption <= battery.max_current and
            specs['max_payload'] >= min_accepted_payload and
            specs['min_fly_time'] >= min_accepted_fly_time)

def combinations(edfs, escs, batteries, additional_weight=1000):
    for edf in edfs:
        for esc in escs:
            for battery in battery_combinations(edf, batteries):
                for num_edf in [3, 4]:
                    specs = drone_specs(num_edf, edf, esc, battery, additional_weight)
                    if valid_combination(num_edf, edf, esc, battery, specs):
                        yield edf, esc, battery, specs

