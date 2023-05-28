import numpy as np


def cutout_pipe(pipe, length=10):
    x, y, z = pipe.vectors.reshape((-1, 3)).T
    if min(z) > (-length):
        mask = z < -100
    else:
        mask = z < (-length)
    start = max(z)
    curr_length = max(z) - min(z)
    if length < curr_length:
        z[mask] = start - length
    else:
        z[mask] = z[mask] - np.abs(length - curr_length)
    cutted = np.vstack([x, y, z]).reshape(3, -1, 3).T
    clutted_pipe = np.zeros((cutted.shape[1], 3, 3))
    for i in range(cutted.shape[1]):
        clutted_pipe[i] = cutted[:, i, :]
    pipe.vectors = clutted_pipe
    return pipe


def center_pipe(pipe, axis="x"):
    axis_mapper = {"x": 0, "y": 1, "z": 2}
    axis_values = pipe.vectors.reshape((-1, 3)).T
    min_value = min(axis_values[axis_mapper[axis]])
    # axis_values[axis_mapper[axis]] += min_value-50
    axis_values[axis_mapper[axis]] += min_value
    cutted = np.vstack(axis_values).reshape(3, -1, 3).T
    centered_pipe = np.zeros((cutted.shape[1], 3, 3))
    for i in range(cutted.shape[1]):
        centered_pipe[i] = cutted[:, i, :]
    pipe.vectors = centered_pipe
    return pipe


def move_pipe(pipe, value, axis="x"):
    axis_mapper = {"x": 0, "y": 1, "z": 2}
    axis_values = pipe.vectors.reshape((-1, 3)).T
    axis_values[axis_mapper[axis]] += value
    cutted = np.vstack(axis_values).reshape(3, -1, 3).T
    centered_pipe = np.zeros((cutted.shape[1], 3, 3))
    for i in range(cutted.shape[1]):
        centered_pipe[i] = cutted[:, i, :]
    pipe.vectors = centered_pipe
    return pipe
