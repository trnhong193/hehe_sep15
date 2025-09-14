# emp_planning_system/calculations.py
import numpy as np
import math

R_EARTH = 6371000

def lonlat_to_xy(origin_lon, origin_lat, lon, lat):
    dx = (lon - origin_lon) * math.pi / 180 * R_EARTH * math.cos(origin_lat * math.pi / 180)
    dy = (lat - origin_lat) * math.pi / 180 * R_EARTH
    return dx, dy

def check_line_box_intersection(p1, p2, box_min, box_max):
    direction = p2 - p1
    direction[direction == 0] = 1e-9
    t_near = (box_min - p1) / direction
    t_far = (box_max - p1) / direction
    tmin = np.minimum(t_near, t_far)
    tmax = np.maximum(t_near, t_far)
    t0 = np.max(tmin)
    t1 = np.min(tmax)
    return t0 < t1 and t0 < 1 and t1 > 0

def calculate_emp_field(emps, obstacles, user_altitude, bounds, grid_size=(200, 200)):
    origin_lon = (bounds['lon_min'] + bounds['lon_max']) / 2
    origin_lat = (bounds['lat_min'] + bounds['lat_max']) / 2
    grid_height, grid_width = grid_size
    lat_range = np.linspace(bounds['lat_min'], bounds['lat_max'], grid_height)
    lon_range = np.linspace(bounds['lon_min'], bounds['lon_max'], grid_width)
    result_grid = np.zeros(grid_size)

    obstacles_xy = []
    for obs in obstacles:
        center_x, center_y = lonlat_to_xy(origin_lon, origin_lat, obs.lon, obs.lat)
        half_len, half_wid = obs.length / 2, obs.width / 2
        box_min = np.array([center_x - half_len, center_y - half_wid, 0])
        box_max = np.array([center_x + half_len, center_y + half_wid, obs.height])
        obstacles_xy.append({'min': box_min, 'max': box_max})

    map_min_x, map_min_y = lonlat_to_xy(origin_lon, origin_lat, bounds['lon_min'], bounds['lat_min'])
    map_max_x, map_max_y = lonlat_to_xy(origin_lon, origin_lat, bounds['lon_max'], bounds['lat_max'])
    cell_width_m = (map_max_x - map_min_x) / grid_width if grid_width > 0 else 0
    cell_height_m = (map_max_y - map_min_y) / grid_height if grid_height > 0 else 0

    for emp in emps:
        emp_x, emp_y = lonlat_to_xy(origin_lon, origin_lat, emp.lon, emp.lat)
        emp_pos = np.array([emp_x, emp_y, emp.height])
        if emp.power <= 0: continue
        d_max = math.sqrt(0.3 * emp.power) * 1.1
        radius_in_cells_x = (d_max / cell_width_m) if cell_width_m > 0 else grid_width
        radius_in_cells_y = (d_max / cell_height_m) if cell_height_m > 0 else grid_height
        emp_i = (emp_x - map_min_x) / cell_width_m if cell_width_m > 0 else 0
        emp_j = (emp_y - map_min_y) / cell_height_m if cell_height_m > 0 else 0
        i_min, i_max = max(0, int(emp_i - radius_in_cells_x)), min(grid_width, int(emp_i + radius_in_cells_x) + 1)
        j_min, j_max = max(0, int(emp_j - radius_in_cells_y)), min(grid_height, int(emp_j + radius_in_cells_y) + 1)

        for j in range(j_min, j_max):
            for i in range(i_min, i_max):
                grid_x, grid_y = lonlat_to_xy(origin_lon, origin_lat, lon_range[i], lat_range[j])
                grid_pos = np.array([grid_x, grid_y, user_altitude])
                is_obstructed = any(check_line_box_intersection(emp_pos, grid_pos, obs['min'], obs['max']) for obs in obstacles_xy)
                if not is_obstructed:
                    distance_sq = np.sum((emp_pos - grid_pos)**2)
                    e_field = float('inf') if distance_sq < 1e-6 else math.sqrt(30 * emp.power / distance_sq)
                    result_grid[j, i] = max(result_grid[j, i], e_field)
    return result_grid