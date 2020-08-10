#!/usr/bin/env python
# coding: utf-8
from argparse import ArgumentParser
from subprocess import PIPE, run
from pydub import AudioSegment
import os
import shutil
import json

#import mirex

DEFAULT_ANNOTATIONS_PATH = "/content/AugmentedGiantSteps/fixed_small/annotations/"
DEFAULT_DATA_PATH = "/content/AugmentedGiantSteps/fixed_small/"
DEFAULT_SPLIT_DATA_PATH = "/content/AugmentedGiantSteps/fixed_small/split/"

# Run the KeyRecognition CNN script to get the predicted key
def predict_cnn(key_path, data_path, file):
    #command = ['python3', key_path, 'single', data_path + file]
    command = [key_path, 'single',  data_path + file]
    result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True).stdout.rstrip()
    return result

# Run the TempoDetection script to get the average tempo for all given files
def get_tempos(tempo_path, data_path, files):
    # TODO: Getting tempo with TempoDetector takes too long, need to figure out better approach
    # files_arg = ""
    # for file in files[:1]:
    #     files_arg += data_path + file + " "
    # files_arg = files_arg[:-1]
    # temp_dir = "tempo"
    # if os.path.isdir(temp_dir):
    #     shutil.rmtree(temp_dir)
    # os.mkdir(temp_dir)
    # command = ['python.exe', tempo_path, 'batch', '-o', temp_dir, files_arg]
    # result = run(command, stdout=PIPE, stderr=PIPE, universal_newlines=True).stderr.rstrip()
    # print(result)
    return ""

# Used for sorting json object
def extract_time(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return float(json['start'])
    except KeyError:
        return 0

def main():
    parser = ArgumentParser()
    parser.add_argument('--ann', type=str, default=DEFAULT_ANNOTATIONS_PATH,
                        help="Input path to find annotations in. Default: {}".format(DEFAULT_ANNOTATIONS_PATH))
    parser.add_argument('--data', type=str, default=DEFAULT_DATA_PATH,
                        help="Input path to find testing dataset in. Default: {}".format(DEFAULT_DATA_PATH))
    parser.add_argument('--split_data', type=str, default=DEFAULT_SPLIT_DATA_PATH,
                        help="Input path to store testing dataset in. Default: {}".format(DEFAULT_SPLIT_DATA_PATH))
    # eg. C:\ProgramData\Anaconda3\Scripts\KeyRecognition
    parser.add_argument('--key', type=str, required=True,
                        help="Path to the KeyDetector program.")
    # eg. C:\ProgramData\Anaconda3\Scripts\TempoDetector
    parser.add_argument('--tempo', type=str, required=True,
                        help="Path to the TempoDetector program.")

    args = parser.parse_args()

    ann_path = args.ann
    data_path = args.data
    split_data_path = args.split_data

    # Step 1: Provide path to KeyDetector and TempoDetector executables
    # eg. "python.exe .\KeyRecognition single .\10089-0.LOFI.mp3"
    key_path = args.key
    tempo_path = args.tempo

    data_files = os.listdir(data_path)
    # Step 2: For each file, find the average tempo with TempoDetector
    # get_tempos(tempo_path, data_path, data_files)
    # TODO: hardcoding tempo to 100 for now, fix later
    tempo = 100

    scores = []

    # Step 3: Get list of data files in Dataset/ directory (or restrict to smaller set)
    for file in data_files:
        # Step 4: Find the corresponding annotation for the current file and parse the list of ground truth modulations
        split_path = os.path.splitext(file)
        if (split_path[-1] == '.mp3'):
          ann_file = ann_path + split_path[0] + ".json"
          ann_data = json.load(open(ann_file))
          ann_data.sort(key=extract_time)
          print(ann_data)

          # Step 5: Run the sliding window algorithm
          sound = AudioSegment.from_mp3(data_path + file)
          
          # Window is 10 seconds (in milliseconds)
          window = 10 * 1000
          divisions = (len(sound) // window) + 1

          # TODO split up the file into multiple files
          for i in range(divisions):
            split_file = split_path[0] + '-{}'.format(i) + split_path[1]
            sound[i*window:(i+1)*window].export(split_data_path + split_file, format="mp3")

            # Run keydetection on each file
            print(predict_cnn(key_path, split_data_path, split_file))
          

          # Step 6: Calculate the running MIREX score

if __name__ == '__main__':
    main()
