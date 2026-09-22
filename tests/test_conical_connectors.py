"""Geometric boundary checks independent of the Fusion runtime."""
import ast
import math
from pathlib import Path
from types import SimpleNamespace
from unittest import TestCase, main
from unittest.mock import Mock


SOURCE = (Path(__file__).resolve().parents[1] / 'fusion_addin'
          / 'SegmentJoinPilot' / 'commands' / 'commandDialog' / 'entry.py')
tree = ast.parse(SOURCE.read_text(encoding='utf-8-sig'))
names = {'_taper_length_limit', '_taper_validation_message', '_add_connector_profile'}
nodes = [node for node in tree.body
         if isinstance(node, ast.FunctionDef) and node.name in names]
angles = next(node.value for node in tree.body if isinstance(node, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == 'TAPER_ANGLES' for t in node.targets))
namespace = dict(math=math, TAPER_ANGLES=ast.literal_eval(angles),
                 PLANE_DISTANCE_TOLERANCE_CM=1e-6,
                 _selected_connector_shape=lambda inputs: inputs.shape,
                 tr=lambda key, **kwargs: (key, kwargs))
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), namespace)


class ConicalTests(TestCase):
    def limit(self, shape, diameter=0.6, radial=0.02, depth=0.03):
        return namespace['_taper_length_limit'](shape, diameter, radial, depth)

    def message(self, shape, length, radial=0.02, depth=0.03):
        values = dict(connector_diameter=0.6, connector_length=length,
                      radial_clearance=radial, depth_clearance=depth)
        inputs = SimpleNamespace(shape=shape, itemById=lambda key:
                                 SimpleNamespace(value=values[key]))
        return namespace['_taper_validation_message'](inputs)

    def test_known_six_mm_limits(self):
        self.assertAlmostEqual(self.limit('Conical15'), 1.11962, places=4)
        self.assertAlmostEqual(self.limit('Conical30'), 0.51962, places=4)

    def test_ten_mm_length_valid_only_for_15_degrees(self):
        self.assertEqual(self.message('Conical15', 1.0), '')
        self.assertEqual(self.message('Conical30', 1.0)[0], 'taper_too_long')

    def test_half_diameter_allowed_but_smaller_end_rejected(self):
        for shape in namespace['TAPER_ANGLES']:
            limit = self.limit(shape)
            self.assertEqual(self.message(shape, limit - 0.001), '')
            self.assertEqual(self.message(shape, limit), '')
            self.assertTrue(self.message(shape, limit + 0.001))
            slope = math.tan(math.radians(abs(namespace['TAPER_ANGLES'][shape])))
            end_diameter = 0.6 - limit * slope
            self.assertAlmostEqual(end_diameter, 0.3)

    def test_socket_depth_can_be_limiting(self):
        self.assertAlmostEqual(self.limit('Conical30', radial=0, depth=0.4),
                               0.23923, places=4)
        self.assertTrue(self.message('Conical30', 0.4, radial=0, depth=0.4))
        self.assertEqual(self.message('Conical30', 0.4, radial=0.1, depth=0.4), '')

    def test_warning_limit_is_in_mm_and_rounded_down(self):
        for shape, expected in [('Conical15', 11.19), ('Conical30', 5.19)]:
            self.assertEqual(self.message(shape, 1.2)[1]['limit'], expected)
            self.assertEqual(self.message(shape, expected / 10), '')

    def test_impossible_socket_and_nonconical_shapes(self):
        self.assertTrue(self.message('Conical30', 0.1, radial=0, depth=1))
        self.assertEqual(self.message('Round', 100), '')

    def test_hexagonal_limits_and_socket_depth(self):
        for angle in (15, 30):
            for radial, depth in ((0.02, 0.03), (0, 0.4)):
                self.assertEqual(self.limit(f'HexConical{angle}', radial=radial, depth=depth),
                                 self.limit(f'Conical{angle}', radial=radial, depth=depth))

    def test_round_and_hexagonal_profile_routing_for_connector_and_socket(self):
        hexagon = Mock()
        namespace['_add_hexagon_profile'] = hexagon
        sketch = Mock()
        center = object()
        for radius in (0.3, 0.32):
            for angle in (15, 30):
                namespace['_add_connector_profile'](sketch, center, radius, f'HexConical{angle}')
                hexagon.assert_called_with(sketch, center, radius)
                sketch.sketchCurves.sketchCircles.addByCenterRadius.assert_not_called()
            for angle in (15, 30):
                namespace['_add_connector_profile'](sketch, center, radius, f'Conical{angle}')
                sketch.sketchCurves.sketchCircles.addByCenterRadius.assert_called_with(center, radius)
            sketch.reset_mock()


if __name__ == '__main__':
    main()
