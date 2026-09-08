"""Regression checks for current section-face resolution without Fusion."""
import ast
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import Mock

SOURCE = (Path(__file__).resolve().parents[1] / 'fusion_addin'
          / 'SegmentJoinPilot' / 'commands' / 'commandDialog' / 'entry.py')
tree = ast.parse(SOURCE.read_text(encoding='utf-8-sig'))
helper = next(node for node in tree.body
              if isinstance(node, ast.FunctionDef)
              and node.name == '_position_sketch_reference_plane')


class ReferencePlaneTests(TestCase):
    def setUp(self):
        self.normal = Mock()
        self.normal.normalize.return_value = True
        self.origin = Mock()
        self.origin.vectorTo.return_value = self.normal
        self.component = object()
        # No timeline/referencePlane attributes: any historical access fails.
        self.sketch = SimpleNamespace(
            parentComponent=self.component,
            sketchToModelSpace=Mock(side_effect=[self.origin, object()]))
        self.body = object()
        self.small = SimpleNamespace(area=2)
        self.large = SimpleNamespace(area=10)
        self.find_body = Mock(return_value=self.body)
        self.find_faces = Mock(return_value=[self.small, self.large])
        self.core = Mock()
        namespace = dict(adsk=SimpleNamespace(core=self.core),
                         _body_by_name=self.find_body,
                         _find_section_faces=self.find_faces)
        exec(compile(ast.Module(body=[helper], type_ignores=[]), str(SOURCE), 'exec'), namespace)
        self.read_reference = namespace[helper.name]

    def test_current_operation_face_without_history_access(self):
        self.assertIs(self.read_reference(self.sketch, '002'), self.large)
        self.find_body.assert_called_once_with(self.component, 'SJP_Segment_A_002')
        self.find_faces.assert_called_once_with(self.body, self.core.Plane.create.return_value)
        self.core.Plane.create.assert_called_once_with(self.origin, self.normal)
        self.assertEqual(self.core.Point3D.create.call_args_list[0].args, (0, 0, 0))
        self.assertEqual(self.core.Point3D.create.call_args_list[1].args, (0, 0, 1))

    def test_missing_segment_is_reported(self):
        self.find_body.return_value = None
        with self.assertRaisesRegex(RuntimeError, 'segment body'):
            self.read_reference(self.sketch, '002')
        self.find_faces.assert_not_called()

    def test_missing_coplanar_face_is_reported(self):
        self.find_faces.return_value = []
        with self.assertRaisesRegex(RuntimeError, 'current face'):
            self.read_reference(self.sketch, '002')

    def test_invalid_transform_is_reported(self):
        self.sketch.sketchToModelSpace.side_effect = [None, None]
        with self.assertRaisesRegex(RuntimeError, 'determine'):
            self.read_reference(self.sketch, '002')
        self.find_body.assert_not_called()

    def test_invalid_normal_is_reported(self):
        self.normal.normalize.return_value = False
        with self.assertRaisesRegex(RuntimeError, 'normal'):
            self.read_reference(self.sketch, '002')
        self.find_body.assert_not_called()


if __name__ == '__main__':
    main()
