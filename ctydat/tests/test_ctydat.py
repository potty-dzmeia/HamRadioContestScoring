import unittest

from ctydat import parser


class TestCQZoneClassification(unittest.TestCase):

    def setUp(self):
        # Load cty.dat data
        self.ctydat_parser = parser.Parser("data/cty_wt.dat")


    def test_callsign_to_cqzone_classification(self):
        test_data_path = 'data/callsign_to_cqzone.txt'  # Replace with your test data file path
        with open(test_data_path, 'r') as file:
            test_data_lines = file.readlines()

        for line in test_data_lines:
            callsign, expected_cq_zone = line.strip().split(',')
            expected_cq_zone = int(expected_cq_zone)

            # Get CQ zone based on callsign from parsed cty.dat data
            country = self.ctydat_parser.find_country(callsign)
            self.assertIsNot(country, None, f"The {callsign}, couldn't be classified")

            cq_zone = country["cq_zone"]

            # Assert correctness
            if cq_zone != expected_cq_zone:
                print(f"In log CQ zone is {expected_cq_zone} for callsign {callsign}, classified as {cq_zone}")
            self.assertEqual(cq_zone, expected_cq_zone,
                            f"Expected CQ zone {expected_cq_zone} for callsign {callsign}, classified as {cq_zone}")


    def test_callsign_to_continent_classification(self):
        test_data_path = 'data/callsign_to_continent.txt'  # Replace with your test data file path
        with open(test_data_path, 'r') as file:
            test_data_lines = file.readlines()

        for line in test_data_lines:
            callsign, expected_continent = line.strip().split(',')
            expected_continent = str(expected_continent).upper()

            # Get continent based on callsign from parsed cty_wt.dat data
            country = self.ctydat_parser.find_country(callsign)
            self.assertIsNot(country, None, f"The {callsign}, couldn't be classified")

            continent = country["continent"]

            # Assert correctness
            if continent != expected_continent:
                print(f"In log CQ zone is {expected_continent} for callsign {callsign}, got {continent}")
            self.assertEqual(continent, expected_continent,
                             f"Expected CQ zone {expected_continent} for callsign {callsign}, got {continent}")


    def test_prefix_override_extraction(self):
        test_cases = [
            ("=R8MB/1(17)[20]",
             {"prefix": "=R8MB/1", "cq_zone": "17", "itu_zone": "20","coordinates": None, "time_offset": None}),
            ("=R8XF/1",
             None),
            ("=RP79A[19]",
             {"prefix": "=RP79A", "cq_zone": None, "itu_zone": "19","coordinates": None, "time_offset": None}),
            ("=AA4Q(3)[6]{EU}",
             {"prefix": "=AA4Q", "cq_zone": "3", "itu_zone": "6", "continent": "EU","coordinates": None, "time_offset": None}),
            ("LZ1ABC{AS}",
             {"prefix": "LZ1ABC", "cq_zone": None, "itu_zone": None, "continent": "AS","coordinates": None, "time_offset": None}),
            ("=RN4HFJ",
             None),
            ("=RK80PT[19]",
             {"prefix": "=RK80PT", "cq_zone": None, "itu_zone": "19","coordinates": None, "time_offset": None}),
            ("=AA5UZ(4)[8]",
             {"prefix": "=AA5UZ", "cq_zone": "4", "itu_zone": "8","coordinates": None, "time_offset": None}),
            ("=RC4I",
             None),
            ("=RP79AOS[19]",
             {"prefix": "=RP79AOS", "cq_zone": None, "itu_zone": "19","coordinates": None, "time_offset": None}),
            ("=LZ1ABC[19",
             {"prefix": "=LZ1ABC[19", "cq_zone": None, "itu_zone": None, "coordinates": None, "time_offset": None}),
            ("=LZ1ABC",
             None,
             )
            # Add more test cases as needed
        ]

        for input_str, expected_output in test_cases:
            with self.subTest(input_str=input_str):
                result = self.ctydat_parser.parse_overrides(input_str)
                if result is None:
                    self.assertEqual(expected_output, None)
                    continue
                for key in expected_output:
                    self.assertEqual(result[key], expected_output[key], f"Failed for key: {key} with input: {input_str}")

if __name__ == '__main__':
    unittest.main()
