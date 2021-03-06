# Copyright 2018 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
"""Tests for checkpointing the MatchingFilesDataset."""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import shutil
import tempfile

from absl.testing import parameterized

from tensorflow.python.data.experimental.ops import matching_files
from tensorflow.python.data.kernel_tests import checkpoint_test_base
from tensorflow.python.data.kernel_tests import test_base
from tensorflow.python.framework import combinations
from tensorflow.python.platform import test


class MatchingFilesDatasetCheckpointTest(
    checkpoint_test_base.CheckpointTestBase, parameterized.TestCase):

  def _build_iterator_graph(self, test_patterns):
    return matching_files.MatchingFilesDataset(test_patterns)

  @combinations.generate(test_base.default_test_combinations())
  def testMatchingFilesCore(self):
    tmp_dir = tempfile.mkdtemp()
    width = 16
    depth = 8
    for i in range(width):
      for j in range(depth):
        new_base = os.path.join(tmp_dir, str(i),
                                *[str(dir_name) for dir_name in range(j)])
        if not os.path.exists(new_base):
          os.makedirs(new_base)
        child_files = ['a.py', 'b.pyc'] if j < depth - 1 else ['c.txt', 'd.log']
        for f in child_files:
          filename = os.path.join(new_base, f)
          open(filename, 'w').close()

    patterns = [
        os.path.join(tmp_dir, os.path.join(*['**'
                                             for _ in range(depth)]), suffix)
        for suffix in ['*.txt', '*.log']
    ]

    num_outputs = width * len(patterns)
    self.run_core_tests(lambda: self._build_iterator_graph(patterns),
                        num_outputs)

    shutil.rmtree(tmp_dir, ignore_errors=True)


if __name__ == '__main__':
  test.main()
