"""Marker replacement and preview regression checks without Fusion."""
import ast
from pathlib import Path
from types import SimpleNamespace as NS
from unittest import TestCase, main
from unittest.mock import Mock


SOURCE = (Path(__file__).resolve().parents[1] / 'fusion_addin'
          / 'SegmentJoinPilot' / 'commands' / 'commandDialog' / 'entry.py')


class MarkerTests(TestCase):
    def setUp(self):
        self.groups = []
        self.drawn = []

        def add():
            group = NS(isValid=True, isVisible=True, name='', id='')
            def delete():
                group.isValid = False
                self.groups.remove(group)
                return True
            group.deleteMe = delete
            group.addLines = lambda coordinates, indices, strip: self.lines(coordinates)
            self.groups.append(group)
            return group

        class Groups:
            @property
            def count(inner):
                return len(self.groups)
            def item(inner, index):
                return self.groups[index]

        groups = Groups()
        groups.add = add
        self.design = NS(rootComponent=NS(customGraphicsGroups=groups))
        self.app = NS(activeProduct=self.design, activeViewport=Mock())
        point = lambda x, y, z: NS(x=x, y=y, z=z)
        adsk = NS(core=NS(Point3D=NS(create=point), Color=NS(create=Mock()),
                          CommandEventArgs=object),
                  fusion=NS(Design=NS(cast=lambda product: product),
                            CustomGraphicsCoordinates=NS(create=lambda coords: coords),
                            CustomGraphicsShowThroughColorEffect=NS(create=Mock())))
        self.ns = dict(adsk=adsk, app=self.app, _position_marker_group=None,
                       POSITION_MARKER_GRAPHICS_NAME='SJP_SelectedPositionMarkers')
        names = {'_delete_position_markers', '_update_position_markers', 'command_preview'}
        tree = ast.parse(SOURCE.read_text(encoding='utf-8-sig'))
        nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in names]
        exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), 'exec'), self.ns)
        self.sketch = NS(sketchToModelSpace=lambda p: p)
        self.points = [NS(geometry=point(x, 0, 0)) for x in range(4)]

    def lines(self, coords):
        self.drawn.append(coords)
        return NS()

    def test_deselect_replaces_four_crosses_with_two_then_none(self):
        update = self.ns['_update_position_markers']
        update(self.sketch, self.points)
        old = self.groups[0]
        update(self.sketch, [self.points[0], self.points[2]])
        self.assertFalse(old.isVisible)
        self.assertFalse(old.isValid)
        self.assertEqual(len(self.groups), 1)
        # Four endpoints with three coordinates per cross.
        self.assertEqual(len(self.drawn[-1]), 24)
        self.assertAlmostEqual(self.drawn[-1][0], -0.18)
        self.assertAlmostEqual(self.drawn[-1][12], 1.82)
        update(self.sketch, [])
        self.assertEqual(self.groups, [])

    def test_cleanup_preserves_unrelated_graphics(self):
        groups = self.design.rootComponent.customGraphicsGroups
        unrelated = groups.add()
        unrelated.name = 'Other add-in'
        stale = groups.add()
        stale.id = self.ns['POSITION_MARKER_GRAPHICS_NAME']
        self.ns['_delete_position_markers']()
        self.assertEqual(self.groups, [unrelated])

    def test_preview_uses_current_selection_and_keeps_execute_enabled(self):
        update = Mock()
        self.ns.update(_update_position_markers=update,
                       _is_inspect_mode=lambda inputs: True,
                       _selected_position_sketch=lambda value: self.sketch,
                       _selected_position_points=lambda inputs: [self.points[2]])
        args = NS(firingEvent=NS(sender=NS(commandInputs=NS(itemById=lambda key: None))))
        self.ns['command_preview'](args)
        update.assert_called_once_with(self.sketch, [self.points[2]])
        self.assertFalse(args.isValidResult)


if __name__ == '__main__':
    main()
