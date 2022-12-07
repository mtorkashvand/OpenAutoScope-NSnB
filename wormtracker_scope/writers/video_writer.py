#! python
#
# Copyright 2022
# Authors: Mahdi Torkashvand

"""
This generates the mp4 movie for a dataset

Usage:
    video_writer.py             [options]

Options:
    -h --help                   Show this help.
    --directory=PATH            Directory of the raw dataset.
                                    [default: .]
    --file=HOST:PORT            Raw dataset filename.
                                    [default: flircamera]
    --fps=HOST:PORT             Frame rate for the generated movie.
                                    [default: 10]
"""

import os
from pathlib import Path

import cv2
import numpy as np
from docopt import docopt
import h5py


def write_video(directory, file, fps):
    data_path = Path(directory)

    file_name = os.path.join(data_path, file + ".h5")
    movie_name = os.path.join(data_path, file + ".mp4")

    f = h5py.File(file_name, "r")
    sample_frame = f["data"][0][:]
    shape_t = len(f["times"][:])

    movie_shape = (sample_frame.shape[1], sample_frame.shape[0])

    fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
    video = cv2.VideoWriter(movie_name,
                            fourcc,
                            float(fps),
                            movie_shape,
                            True)



    for t in range(shape_t):
        frame = f["data"][t][:]
        img = np.stack([frame, frame, frame], axis=-1)
        img = cv2.putText(img, str(t + 1), (35,55), cv2.FONT_HERSHEY_SIMPLEX,
                          1.5, (0, 0, 255), 2, cv2.LINE_AA)
        video.write(img)
    video.release()


def main():
    """This is the video write main function"""
    arguments = docopt(__doc__)

    write_video(directory=arguments["--directory"],
                file=arguments["--file"],
                fps=arguments["--fps"])

if __name__ == "__main__":
    main()

