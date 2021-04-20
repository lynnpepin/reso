from PIL import Image
import unittest as ut
import numpy as np

from regionmapper import RegionMapper, ortho_map, diag_map

class RegionMapperTest_OrthoNbhd_NoWrap(ut.TestCase):
    def setUp(self):
        self.pic = np.swapaxes(np.array(Image.open("test_image.png")), 0, 1)
        self.classes = { (255,0,0) : 1, (0,255,0) : 2, (0,0,255) : 3 }
        self.contiguity_map = { 1 : ortho_map + diag_map, 2 : ortho_map, 3 : diag_map }
            # Red is ortho and diag contiguous,
            # green is only ortho contiguous,
            # blue is only diag contiguous 
        self.Mapped = \
                RegionMapper(image          = self.pic,
                             class_dict     = self.classes,
                             contiguities   = self.contiguity_map)
        # No neighborhood map; they are all ortho contiguous (default)
        pass
    
    def tearDown(self):
        pass

    def test_image(self):
        # Make sure image is properly mapped according to self.classes
        # Shoudl be x then y!
        image = self.Mapped._image
        self.assertEqual(image[0,0], 1)
        self.assertEqual(image[1,0], 0)
        self.assertEqual(image[2,0], 0)
        self.assertEqual(image[3,0], 1)
        self.assertEqual(image[0,1], 1)
        self.assertEqual(image[0,2], 0)
        self.assertEqual(image[0,3], 0)
        self.assertEqual(image[0,4], 3)
        self.assertEqual(image[0,5], 0)
        self.assertEqual(image[0,6], 2)

    def test_contiguous(self):
        # Make sure the contiguous regions all have the right values.
        # Does not wrap
        
        # Red pixels - ortho and diag nbhd
        reg1 = self.Mapped.region_at_pixel(0,0)
        self.assertEqual(self.Mapped.region_at_pixel(0,1), reg1)
        self.assertEqual(self.Mapped.region_at_pixel(1,2), reg1)
        self.assertNotEqual(self.Mapped.region_at_pixel(3,0), reg1)
        
        # Blue pixels - only diag continuous!
        reg2 = self.Mapped.region_at_pixel(2,2)
        self.assertEqual(self.Mapped.region_at_pixel(1,3), reg2)
        self.assertEqual(self.Mapped.region_at_pixel(0,4), reg2)
        self.assertNotEqual(self.Mapped.region_at_pixel(2,3), reg2)
        
        # Green pixels
        reg3 = self.Mapped.region_at_pixel(3,1)
        self.assertEqual(self.Mapped.region_at_pixel(3,2), reg3)
        self.assertEqual(self.Mapped.region_at_pixel(3,3), reg3)
        self.assertEqual(self.Mapped.region_at_pixel(3,4), reg3)
        self.assertEqual(self.Mapped.region_at_pixel(3,5), reg3)
        reg4 = self.Mapped.region_at_pixel(0,6)
        self.assertEqual(self.Mapped.region_at_pixel(1,6), reg4)
        self.assertEqual(self.Mapped.region_at_pixel(2,6), reg4)
        # They should not be the same region
        self.assertNotEqual(reg3, reg4)
        
        # TODO: Also test regions(), regions_with_class, and then adjacent_regions here

    def test_regions(self):
        # Make sure 'regions' works right
        reg1 = self.Mapped.region_at_pixel(0,0) # Top-left red splotch
        reg2 = self.Mapped.region_at_pixel(2,2) # Blue diagonal line
        reg6 = self.Mapped.region_at_pixel(3,0) # Top-right single red pixel

        class_number, list_of_pixels = self.Mapped.regions(reg1)
        self.assertEqual(class_number, 1)
        self.assertEqual(set(list_of_pixels), set(((0,0),(0,1),(1,2))))
        class_number, list_of_pixels = self.Mapped.regions(reg6)
        self.assertEqual(class_number, 1)
        self.assertEqual(list_of_pixels, [(3,0)])
        class_number, list_of_pixels = self.Mapped.regions(reg2)
        self.assertEqual(class_number, 3)
        self.assertEqual(set(list_of_pixels), set(((0,4),(1,3),(2,2))))

    def test_regions_with_class(self):
        reg1 = self.Mapped.region_at_pixel(0,0) # Top-left red splotch
        reg2 = self.Mapped.region_at_pixel(2,2) # Blue diagonal line
        reg3 = self.Mapped.region_at_pixel(3,1) # Vertical green line
        reg4 = self.Mapped.region_at_pixel(0,6) # Horizontal green line
        reg5 = self.Mapped.region_at_pixel(2,3) # Single blue pixel
        reg6 = self.Mapped.region_at_pixel(3,0) # Top-right single red pixel
        
        reds = self.Mapped.regions_with_class(1)
        grns = self.Mapped.regions_with_class(2)
        blus = self.Mapped.regions_with_class(3)
        
        self.assertEqual(set(reds), set((reg1,reg6)))
        self.assertEqual(set(grns), set((reg3,reg4)))
        self.assertEqual(set(blus), set((reg2,reg5)))
        

    def test_adjacent_regions(self):
        reg1 = self.Mapped.region_at_pixel(0,0) # Top-left red splotch
        reg2 = self.Mapped.region_at_pixel(2,2) # Blue diagonal line
        reg3 = self.Mapped.region_at_pixel(3,1) # Vertical green line
        reg4 = self.Mapped.region_at_pixel(0,6) # Horizontal green line
        reg5 = self.Mapped.region_at_pixel(2,3) # Single blue pixel
        reg6 = self.Mapped.region_at_pixel(3,0) # Top-right single red pixel
        
        self.assertEqual(self.Mapped.adjacent_regions(reg1), [reg2])
        self.assertEqual(set(self.Mapped.adjacent_regions(reg2)), set([reg1, reg5, reg3]))
        self.assertEqual(set(self.Mapped.adjacent_regions(reg3)), set([reg6,reg2,reg5]))
        self.assertEqual(self.Mapped.adjacent_regions(reg4), [])
        self.assertEqual(set(self.Mapped.adjacent_regions(reg5)), set([reg2,reg3]))
        self.assertEqual(self.Mapped.adjacent_regions(reg6), [reg3])



all_tests = [RegionMapperTest_OrthoNbhd_NoWrap]

for test in all_tests:
    ut.TextTestRunner(verbosity=2).run(ut.TestLoader().loadTestsFromTestCase(test))
