def same(kv1, kv2):
  return kv1 == kv2

def perfect_fifth(kv1, kv2):
  # 7 apart in same mode
  m1 = kv1 < 12
  kv1_base = kv1 % 12
  m2 = kv2 < 12
  kv2_base = kv2 % 12

  if m1 != m2:
    return False

  return abs(kv2_base - kv1_base) == 7

def relative_mode(kv1, kv2):
  m1 = kv1 < 12
  kv1_base = kv1 % 12
  m2 = kv2 < 12
  kv2_base = kv2 % 12

  if m1 == m2:
    return False
  elif m1 < m2:
    return kv2_base == kv1_base + 3
  elif m1 > m2:
    return kv1_base == kv2_base + 3

def parallel_mode(kv1, kv2):
  m1 = kv1 < 12
  kv1_base = kv1 % 12
  m2 = kv2 < 12
  kv2_base = kv2 % 12

  if m1 == m2:
    return False

  return kv1_base == kv2_base

def score(kv1, kv2):
  if same(kv1, kv2):
    return 1.
  elif perfect_fifth(kv1, kv2):
    return 0.5
  elif relative_mode(kv1, kv2):
    return 0.3
  elif parallel_mode(kv1, kv2):
    return 0.2
  else:
    return 0.
