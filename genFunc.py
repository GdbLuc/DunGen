from math import sin

def function(maze_length, maze_actual_weight):
    completion = maze_actual_weight / maze_length
    completion *= 100
    # func
    if completion <= 25:
        target_weight = (completion**2) / 96 + 7
    elif completion <= 50:
        target_weight = -((completion-50)**2 / 96 + 7)
    else:
        target_weight = 51 - 0.5 * completion
    target_interval = -7*sin(completion/5)+10
    return target_weight, target_interval
