from argparse import ArgumentParser
import csv
import os
import json

import mirex

v2k = [
  'C major', 'Db major', 'D major', 'Eb major', 'E major', 'F major', 'Gb major', 'G major', 'Ab major', 'A major', 'Bb major', 'B major',
  'C minor', 'Db minor', 'D minor', 'Eb minor', 'E minor', 'F minor', 'Gb minor', 'G minor', 'Ab minor', 'A minor', 'Bb minor', 'B minor'
]

k2v = { k: i for i, k in enumerate(v2k) }

def parse_qm(rows):
  # Get (midpoint, key value) for each entry in qm output
  out = []
  for i in range(len(rows) - 1):
    out.append(((rows[i][0] + rows[i + 1][0]) / 2, int(rows[i][1]) - 1))
  out.append(((rows[-1][0] + 120.) / 2, int(rows[-1][1]) - 1))

  return out

def parse_ann(ann_json):
  # Get (start, key value) for each entry in annotation
  return [(x['start'], k2v[x['key']]) for x in ann_json]

def full_score(est, ann):
  # Compare estimations that have midpoints to annotations that have start points
  scores = []

  for mid, est_kv in est:
    to_compare = ann[0][1]

    for start, ann_kv in ann:
      if start > mid:
        break
      else:
        to_compare = ann_kv

    scores.append(mirex.score(est_kv, to_compare))

  print(scores)
  return sum(scores) / len(scores)

def main():
  parser = ArgumentParser()
  parser.add_argument('annotations_dir', metavar='ad', type=str, help='input path to find annotations in')

  args = parser.parse_args()

  scores = []

  for root, _, files in os.walk('qm_key_out'):
    for fname in files:
      with open(os.path.join(root, fname), newline='') as f:
        reader = csv.reader(f, quoting=csv.QUOTE_NONNUMERIC)
        qm_est = parse_qm(list(row for row in reader))

      ann_fname = '.'.join(fname.split('.')[:-1] + ['json'])
      with open(os.path.join(args.annotations_dir, ann_fname)) as ann_f:
        ann = parse_ann(json.load(ann_f))

      scores.append(full_score(qm_est, ann))

  print(sum(scores) / len(scores))


if __name__ == '__main__':
  main()
