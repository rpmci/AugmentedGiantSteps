#!/usr/bin/env python
# coding: utf-8
from argparse import ArgumentParser
from subprocess import PIPE, run
from pydub import AudioSegment
import os
import shutil
import json
import csv

#import mirex

DEFAULT_ANNOTATIONS_PATH = "/content/AugmentedGiantSteps/data_200/annotations/"
DEFAULT_DATA_PATH = "/content/AugmentedGiantSteps/data_200/"
DEFAULT_CSV_OUT_PATH = "/content/AugmentedGiantSteps/data_200/csv_out/"

v2k = [
  'C major', 'Db major', 'D major', 'Eb major', 'E major', 'F major', 'Gb major', 'G major', 'Ab major', 'A major', 'Bb major', 'B major',
  'C minor', 'Db minor', 'D minor', 'Eb minor', 'E minor', 'F minor', 'Gb minor', 'G minor', 'Ab minor', 'A minor', 'Bb minor', 'B minor'
]

k2v = { k: i for i, k in enumerate(v2k) }

k_desc = [
  'C', 'D', 'E', 'F', 'G', 'A', 'B', 'C'
]

def enharmonic_equiv(k):
  # If k has a sharp, return the enharmonic equivalent (as a flat)
  if '#' in k:
    k = k_desc[k_desc.index(k[0]) + 1] + 'b' + k[2:]
  return k

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
    # eg. C:\ProgramData\Anaconda3\Scripts\KeyRecognition
    parser.add_argument('--key', type=str, required=True,
                        help="Path to the KeyDetector program.")
    # eg. C:\ProgramData\Anaconda3\Scripts\TempoDetector
    parser.add_argument('--tempo', type=str, required=True,
                        help="Path to the TempoDetector program.")

    args = parser.parse_args()

    ann_path = args.ann
    data_path = args.data

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

    new_path = data_path + 'csv_out/'
    try:
        os.mkdir(new_path)
    except OSError:
        print ("Creation of the directory %s failed" % new_path)
    else:
        print ("Successfully created the directory %s " % new_path)

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
          
          # Window is 8/T seconds (in milliseconds)
          #window = 60000 * 8 / tempo
          window = 19200

          # note: 1385 (1.385s) is the shortest window length that works

          # step is 1/T seconds (in milliseconds)
          #step = 60000 * 1 / tempo

          # setting step = 4/T to make this not 200 iterations, 
          step = 60000 * 8 / tempo

          song_len = len(sound)
          divisions = int((song_len - window) / step) + 1

          # TODO keep track of output
          # keylist should be a list of [start_time, key]
          keylist = []

          # TODO keep track of current key prediction
          #current_key = [start time, key]
          current_key = []

          # TODO split up the file into multiple files
          for i in range(divisions):

            start = step * i
            # Create temporary file
            split_file = split_path[0] + '-{}'.format(i) + split_path[1]
            sound[start:start + window].export(data_path + split_file, format="mp3")

            # Run KeyDetection on each file
            prediction = enharmonic_equiv(predict_cnn(key_path, data_path, split_file))
            print(prediction, k2v[prediction])

            if not current_key:
              current_key = [start / 1000, k2v[prediction], prediction]
              #current_key = [start / 1000, prediction]
            elif current_key[-1] != prediction:
              keylist.append(current_key)
              current_key = [start / 1000, k2v[prediction], prediction]
              #current_key = [start / 1000, prediction]

            # Remove Temporary file
            os.remove(data_path + split_file)

          if keylist[-1] != current_key:
            keylist.append(current_key)

          print(keylist)
          f = open(new_path + split_path[0]+'.csv', 'w')
          with f:
              writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
              writer.writerows(keylist)
          f.close

          file = open(new_path + split_path[0] +'_time.txt', "w") 
          file.write("{}".format(song_len / 1000)) 
          file.close() 

          # Step 6: Calculate the running MIREX score
          #run evaluate.py

if __name__ == '__main__':
    main()
