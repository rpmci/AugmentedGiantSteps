from argparse import ArgumentParser
import csv
import os
import json

import mirex

DEFAULT_DATA_PATH = '/content/AugmentedGiantSteps/single_file/csv_out/'

v2k = [
  'C major', 'Db major', 'D major', 'Eb major', 'E major', 'F major', 'Gb major', 'G major', 'Ab major', 'A major', 'Bb major', 'B major',
  'C minor', 'Db minor', 'D minor', 'Eb minor', 'E minor', 'F minor', 'Gb minor', 'G minor', 'Ab minor', 'A minor', 'Bb minor', 'B minor'
]

k2v = { k: i for i, k in enumerate(v2k) }

def parse_qm(rows, song_len):
  # Get (start, end, weight, key value) for each entry in output
  out = []
  
  for i in range(len(rows) - 1):
    out.append((rows[i][0], 
                rows[i + 1][0], 
                (rows[i + 1][0] - rows[i][0]) / song_len, 
                int(rows[i][1])))
  out.append((rows[-1][0], 
              song_len,
              (song_len - rows[-1][0])/song_len, 
              int(rows[-1][1])))

  return out

def parse_ann(ann_json):
  # Get (start, key value) for each entry in annotation
  return [(x['start'], k2v[x['key']]) for x in ann_json]

def full_score(est, ann, song_len):
  '''
  # Compare estimations that have midpoints to annotations that have start points
  scores = []

  for i in range(len(ann)):
    ann_start, ann_kv = ann[i]
    if ann_kv == 0:
      print(ann)
    if i == len(ann) - 1:
      next_start, next_kv = song_len, ann[i-1]
    else:
      next_start, next_kv = ann[i+1]

    for est_start, est_end, est_weight, est_kv in est:
      if est_start > next_start or est_end < ann_start:
        # ignore estimates that don't overlap with the annotation
        continue
      elif est_start >= ann_start:
        if est_end > next_start:
          # if it overlaps with two annotations, add the weighted value
          weight1 =  (next_start - est_start) / song_len
          weight2 = (est_end - next_start) / song_len
          scores.append(mirex.score(est_kv, ann_kv) * weight1)
          scores.append(mirex.score(est_kv, next_kv) * weight2)
        else:
          #if fully contained
          scores.append(mirex.score(est_kv, ann_kv) * est_weight)
  return sum(scores)
  '''
  # Compare estimations that have midpoints to annotations that have start points
  scores = []

  for est_start, est_end, est_weight, est_kv in est:
    mid = est_start + est_end / 2
    to_compare = ann[0][1]

    for start, ann_kv in ann:
      if start > mid:
        break
      else:
        to_compare = ann_kv

    scores.append(mirex.score(est_kv, to_compare) * est_weight)

  return sum(scores)


def main():
  parser = ArgumentParser()
  parser.add_argument('annotations_dir', metavar='ad', type=str, help='input path to find annotations in')
  parser.add_argument('csv_dir', metavar='csvd', type=str, help='input path to find csv files in')

  args = parser.parse_args()
  csv_out = args.csv_dir #DEFAULT_DATA_PATH

  scores = []

  for root, _, files in os.walk(csv_out):
    for fname in files:

      split_path = os.path.splitext(fname)
      #since _time.txt files are in the same location, ignore them
      if split_path[1] == '.txt': 
        continue
      time_file = open(os.path.join(csv_out, split_path[0]+'_time.txt'),"r")
      song_len = float(time_file.read())
      
      with open(os.path.join(root, fname), newline='') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        qm_est = parse_qm(list(row for row in reader), song_len)

      ann_fname = '.'.join(fname.split('.')[:-1] + ['json'])
      with open(os.path.join(args.annotations_dir, ann_fname)) as ann_f:
        ann = parse_ann(json.load(ann_f))
      
      scores.append(full_score(qm_est, ann, song_len))

  print(scores)
  print(sum(scores) / len(scores))


if __name__ == '__main__':
  main()
