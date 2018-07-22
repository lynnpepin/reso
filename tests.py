from PIL import Image
import unittest as ut
import numpy as np
from resoboard import pR, pr, pY, py, pG, pg, pC, pc, pB, pb, pM, pm, _rgb_to_resel, _resel_to_rgb, ResoBoard

class DefaultPaletteTests(ut.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
        
    def test_bidirectionality(self):
        for rgb in _rgb_to_resel.keys():
            self.assertEqual(_resel_to_rgb[_rgb_to_resel[rgb]], rgb)
        for resel in _resel_to_rgb.keys():
            self.assertEqual(_rgb_to_resel[_resel_to_rgb[resel]], resel)

class ResoBoardInitTest(ut.TestCase):
    def setUp(self):
        pass
    
    def tearDown(self):
        pass
    
    def test_resel_map(self):
        RB = ResoBoard("testing/test_01.png")
        self.assertEqual(RB._resel_map[0,0], pR)
        self.assertEqual(RB._resel_map[1,1], pR)
        self.assertEqual(RB._resel_map[2,2], pb)
        self.assertEqual(RB._resel_map[1,0], pm)
        self.assertEqual(RB._resel_map[2,0], 0)
        self.assertEqual(RB._resel_map[0,1], pG)
        self.assertEqual(RB._resel_map[2,4], pr)

    def test_region_map(self):
        RB = ResoBoard("testing/test_02.png")
        self.assertEqual(len(RB._RM._regions), 12)
        self.assertEqual(len(RB._RM.regions_with_class(pR)), 2)
        self.assertEqual(len(RB._RM.regions_with_class(pB)), 2)
        self.assertEqual(len(RB._RM.adjacent_regions(RB._RM.region_at_pixel(4,3))), 2)

    def test_object_lists(self):
        RB = ResoBoard("testing/test_02.png")
        self.assertEqual(len(RB._inputs),  4)
        self.assertEqual(len(RB._outputs), 4)
        self.assertEqual(len(RB._xors), 0)
        self.assertEqual(len(RB._ands), 0)
    

    def test_wires(self):
        RB = ResoBoard("testing/test_02.png")
        self.assertEqual(len(RB._red_wires),  2)
        self.assertEqual(len(RB._blue_wires), 2)
        self.assertEqual(RB._red_wires[0].state,  True)
        self.assertEqual(RB._red_wires[1].state,  True)
        self.assertEqual(RB._blue_wires[0].state, False)
        self.assertEqual(RB._blue_wires[1].state, False)
        

all_tests = [DefaultPaletteTests,
             ResoBoardInitTest]

for test in all_tests:
    ut.TextTestRunner(verbosity=2).run(ut.TestLoader().loadTestsFromTestCase(test))
