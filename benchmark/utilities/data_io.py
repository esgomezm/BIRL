"""
Useful function for managing Input/Output

Copyright (C) 2017-2018 Jiri Borovec <jiri.borovec@fel.cvut.cz>
"""

import os
import logging

import numpy as np
import pandas as pd
from PIL import Image

LANDMARK_COORDS = ['Y', 'X']


def create_dir(path_dir):
    """ create a folder if it not exists

    :param str path_dir:
    """
    path_dir = os.path.abspath(path_dir)
    if not os.path.isdir(path_dir):
        os.makedirs(path_dir, mode=0o775)
    else:
        logging.warning('Folder already exists: %s', path_dir)
    return path_dir


def load_landmarks(path_file):
    """ load landmarks in csv and txt format

    :param str path_file: path to the input file
    :return: np.array<np_points, dim>

    >>> points = np.array([[1, 2], [3, 4], [5, 6]])
    >>> save_landmarks('./sample_landmarks.csv', points)
    >>> points1 = load_landmarks('./sample_landmarks.csv')
    >>> points2 = load_landmarks('./sample_landmarks.txt')
    >>> np.array_equal(points1, points2)
    True
    >>> os.remove('./sample_landmarks.csv')
    >>> os.remove('./sample_landmarks.txt')
    """
    assert os.path.exists(path_file), 'missing file "%s"' % path_file
    ext = os.path.splitext(path_file)[-1]
    if ext == '.csv':
        return load_landmarks_csv(path_file)
    elif ext == '.txt':
        return load_landmarks_txt(path_file)
    else:
        logging.error('not supported landmarks file: %s',
                      os.path.basename(path_file))


def load_landmarks_txt(path_file):
    """ load file with landmarks in txt format

    :param str path_file: path to the input file
    :return: np.array<np_points, dim>

    >>> points = np.array([[1, 2], [3, 4], [5, 6]])
    >>> save_landmarks_txt('./sample_landmarks.txt', points)
    >>> pts = load_landmarks_txt('./sample_landmarks.txt')
    >>> pts  # doctest: +NORMALIZE_WHITESPACE
    array([[ 1.,  2.],
           [ 3.,  4.],
           [ 5.,  6.]])
    >>> os.remove('./sample_landmarks.txt')
    """
    assert os.path.exists(path_file), 'missing file "%s"' % path_file
    with open(path_file, 'r') as fp:
        data = fp.read()
        lines = data.split('\n')
        # lines = [re.sub("(\\r|)\\n$", '', line) for line in lines]
    if len(lines) < 2:
        logging.warning('invalid format: file has less then 2 lines, "%s"',
                        repr(lines))
        return np.zeros((0, 2))
    nb_points = int(lines[1])
    points = [[float(n) for n in line.split()] for line in lines[2:]]
    assert nb_points == len(points), 'number of declared (%i) and found (%i) ' \
                                     'does not match' % (nb_points, len(points))
    return np.array(points, dtype=np.float)


def load_landmarks_csv(path_file):
    """ load file with landmarks in cdv format

    :param str path_file: path to the input file
    :return: np.array<np_points, dim>

    >>> points = np.array([[1, 2], [3, 4], [5, 6]])
    >>> save_landmarks_csv('./sample_landmarks.csv', points)
    >>> pts = load_landmarks_csv('./sample_landmarks.csv')
    >>> pts  # doctest: +NORMALIZE_WHITESPACE +ELLIPSIS
    array([[1, 2],
           [3, 4],
           [5, 6]]...)
    >>> os.remove('./sample_landmarks.csv')
    """
    assert os.path.exists(path_file), 'missing file "%s"' % path_file
    df = pd.read_csv(path_file, index_col=0)
    points = df[LANDMARK_COORDS].values
    return points


def save_landmarks(path_file, landmarks):
    """ save landmarks into a specific file

    :param str path_file: path to the output file
    :param landmarks: np.array<np_points, dim>
    """
    assert os.path.exists(os.path.dirname(path_file)), \
        'missing folder "%s"' % os.path.dirname(path_file)
    path_file = os.path.splitext(path_file)[0]
    save_landmarks_csv(path_file + '.csv', landmarks)
    save_landmarks_txt(path_file + '.txt', landmarks)


def save_landmarks_txt(path_file, landmarks):
    """ save landmarks into a txt file

    :param str path_file: path to the output file
    :param landmarks: np.array<np_points, dim>
    """
    assert os.path.exists(os.path.dirname(path_file)), \
        'missing folder "%s"' % os.path.dirname(path_file)
    lines = ['point', str(len(landmarks))]
    lines += [' '.join(str(i) for i in point) for point in landmarks]
    with open(path_file, 'w') as fp:
        fp.write('\n'.join(lines))


def save_landmarks_csv(path_file, landmarks):
    """ save landmarks into a csv file

    :param str path_file: path to the output file
    :param landmarks: np.array<np_points, dim>
    """
    assert os.path.exists(os.path.dirname(path_file)), \
        'missing folder "%s"' % os.path.dirname(path_file)
    assert os.path.splitext(path_file)[-1] == '.csv', \
        'wrong file extension "%s"' % os.path.basename(path_file)
    df = pd.DataFrame(landmarks, columns=LANDMARK_COORDS)
    df.to_csv(path_file)


def update_path(path_file, lim_depth=5, absolute=True):
    """ bubble in the folder tree up intil it found desired file
    otherwise return original one

    :param str path_file: original path
    :param int lim_depth: lax depth of going up
    :param bool absolute: return absolute path
    :return str:

    >>> os.path.exists(update_path('benchmark', absolute=False))
    True
    >>> os.path.exists(update_path('/', absolute=False))
    True
    >>> os.path.exists(update_path('~', absolute=False))
    True
    """
    if path_file.startswith('/'):
        return path_file
    elif path_file.startswith('~'):
        path_file = os.path.expanduser(path_file)

    tmp_path = path_file
    for _ in range(lim_depth):
        if os.path.exists(tmp_path):
            path_file = tmp_path
            break
        tmp_path = os.path.join('..', tmp_path)

    if absolute:
        path_file = os.path.abspath(path_file)
    return path_file


def load_image(path_image):
    """ load the image in value range (0, 1)

    :param str path_image:
    :return: np.array<height, width, ch>

    >>> img = np.random.random((50, 50, 3))
    >>> save_image('./test_image.jpg', img)
    >>> img2 = load_image('./test_image.jpg')
    >>> img2.max() <= 1.
    True
    >>> os.remove('./test_image.jpg')
    """
    assert os.path.exists(path_image), 'missing image "%s"' % path_image
    image = np.array(Image.open(path_image))
    while image.max() > 1.:
        image = (image / 255.)
    return image


def convert_ndarray_2_image(image):
    """ convert ndarray to PIL image if it not already

    :param image: np.ndarray
    :return: Image

    >>> img = np.random.random((50, 50, 3))
    >>> image = convert_ndarray_2_image(img)
    >>> isinstance(image, Image.Image)
    True
    """
    if isinstance(image, np.ndarray):
        if np.max(image) <= 1.:
            image = (image * 255)
        image = Image.fromarray(np.round(image).astype(np.uint8))
    return image


def save_image(path_image, image):
    """ save the image into given path

    :param str path_image: path to the image
    :param image: np.array<height, width, ch>
    """
    image = convert_ndarray_2_image(image)
    path_dir = os.path.dirname(path_image)
    if os.path.exists(path_dir):
        image.save(path_image)
    else:
        logging.error('upper folder does not exists: "%s"', path_dir)


def load_parse_bunwarpj_displacement_axis(fp, size, points):
    """ given pointer in the file aiming to the beginning of displacement
     parse all lines and if in the particular line is a point from list
     get its new position

    :param fp: file pointer
    :param (int, int) size: width, height of the image
    :param points: np.array<nb_points, 2>
    :return list: list of new positions on given axis (x/y) for related points
    """
    width, height = size
    points = np.round(points)
    selected_lines = points[:, 1].tolist()
    pos_new = [0] * len(points)

    # walk thor all lined of this displacement field
    for i in range(height):
        line = fp.readline()
        # if the any point is listed in this line
        if i in selected_lines:
            pos = line.rstrip().split()
            # pos = [float(e) for e in pos if len(e)>0]
            assert len(pos) == width
            # find all points in this line
            for j, point in enumerate(points):
                if point[1] == i:
                    pos_new[j] = float(pos[point[0]])
    return pos_new


def load_parse_bunwarpj_displacements_warp_points(path_file, points):
    """ load and parse displacement field for both X and Y coordinated
    and return new position of selected points

    :param str path_file:
    :param points: np.array<nb_points, 2>
    :return: np.array<nb_points, 2>

    >>> fp = open('./my_transform.txt', 'w')
    >>> _= fp.write('''Width=5
    ... Height=4
    ...
    ... X Trans -----------------------------------
    ... 11 12 13 14 15
    ... 11 12 13 14 15
    ... 11 12 13 14 15
    ... 11 12 13 14 15
    ...
    ... Y Trans -----------------------------------
    ... 20 20 20 20 20
    ... 21 21 21 21 21
    ... 22 22 22 22 22
    ... 23 23 23 23 23''') # py2 has no return, py3 returns nb of characters
    >>> fp.close()
    >>> points = np.array([[1, 1], [4, 0], [2, 3]])
    >>> pts = load_parse_bunwarpj_displacements_warp_points(
    ...                             './my_transform.txt', points)
    >>> pts  # doctest: +NORMALIZE_WHITESPACE
    array([[ 12.,  21.],
           [ 15.,  20.],
           [ 13.,  23.]])
    >>> os.remove('./my_transform.txt')
    """
    assert os.path.isfile(path_file), 'missing file "%s"' % path_file

    fp = open(path_file, 'r')
    # read image sizes
    width = int(fp.readline().split('=')[-1])
    height = int(fp.readline().split('=')[-1])
    logging.debug('loaded image size: %i x %i', width, height)
    size = (width, height)
    assert all(np.max(points, axis=0) <= size), \
        'some points are outside of the image'

    # read inter line
    fp.readline()
    fp.readline()
    # read inter line and Transform notation
    points_x = load_parse_bunwarpj_displacement_axis(fp, size, points)

    # read inter line and Transform notation
    fp.readline(), fp.readline()
    # read Y Trans
    points_y = load_parse_bunwarpj_displacement_axis(fp, size, points)
    fp.close()

    points_new = np.vstack((points_x, points_y)).T
    return points_new