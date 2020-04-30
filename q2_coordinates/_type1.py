from qiime2.plugin import SemanticType

from ..plugin_setup import plugin
from . import QuadTreeDirectoryFormat


SampleData = SemanticType('SampleData', field_names='type')

QuadTree = SemanticType('QuadTree',
                              variant_of=SampleData.field['type'])

plugin.register_semantic_types(SampleData, QuadTree)

plugin.register_semantic_type_to_format(
    SampleData[QuadTree],
    artifact_format=QuadTreeDirectoryFormat
)
