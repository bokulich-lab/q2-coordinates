# ----------------------------------------------------------------------------
# Copyright (c) 2020, QIIME 2 development team.
#
# Distributed under the terms of the Modified BSD License.
#
# The full license is in the file LICENSE, distributed with this software.
# ----------------------------------------------------------------------------

from qiime2.plugin import SemanticType
from q2_types.sample_data import SampleData


Coordinates = SemanticType('Coordinates', variant_of=SampleData.field['type'])
QuadTree = SemanticType('QuadTree',
                        variant_of=SampleData.field['type'])
