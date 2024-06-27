import json
import re


class Parser:
    """
    1. Create an object specifying the location of the cty.dat ot the cty_wt.dat file.
    2. Use the function find_country() in order to determine the country (incl. zones and the continent) of the callsign
    """

    def __init__(self, file_path, file_obj=None):

        self.countries_by_prefix = {} # {'prefix': { country} }    Exmple : {'LZ1ABC : {'name': 'Spratly Islands', 'cq_zone': 26, 'itu_zone': 50, 'continent': 'AS', 'latitude': 9.88, 'longitude': -114.23, 'time_offset': -8.0, 'primary_prefix': '1S'}}

        if file_path:
            with open(file_path, 'r') as cty_file:
                cty_dat_content = cty_file.read()
                self.__parse_cty_dat(cty_dat_content)
        elif file_obj:
            cty_dat_content = file_obj.read()
            self.__parse_cty_dat(cty_dat_content)

    def __parse_cty_dat(self, cty_dat_content):
        lines = cty_dat_content.strip().split('\n')
        country = None

        for line in lines:
            if line.startswith('#'):  # Skip
                continue
            elif line.startswith(' '):  # This is a prefix line
                prefixes = line.strip().split(',')

                for prefix in prefixes:
                    pr = prefix.replace(";", '')

                    overrides = self.parse_overrides(pr)
                    if overrides is None:
                        self.countries_by_prefix[pr] = country
                    else:
                        self.countries_by_prefix[overrides["prefix"]] = dict(country)  # deepcopy is not needed
                        if overrides["cq_zone"] is not None:
                            self.countries_by_prefix[overrides["prefix"]]["cq_zone"] = int(overrides["cq_zone"])
                        if overrides["itu_zone"] is not None:
                            self.countries_by_prefix[overrides["prefix"]]["itu_zone"] = int(overrides["itu_zone"])
                        if overrides["continent"] is not None:
                            self.countries_by_prefix[overrides["prefix"]]["continent"] = overrides["continent"]
                        if overrides["time_offset"] is not None:
                            self.countries_by_prefix[overrides["prefix"]]["time_offset"] = float(overrides["time_offset"])

            else: # This is a country information line
                parts = line.split(':')
                country = {
                    'name': parts[0].strip(),
                    'cq_zone': int(parts[1].strip()),
                    'itu_zone': int(parts[2].strip()),
                    'continent': parts[3].strip(),
                    'latitude': float(parts[4].strip()),
                    'longitude': float(parts[5].strip()),
                    'time_offset': float(parts[6].strip()),
                    'primary_prefix': parts[7].strip()
                }

        return self.countries_by_prefix

    def find_country(self, callsign : str) -> dict:
        """
        Will try to determine the country (including cq zone, itu zone, continent and others) of the callsign.

        :param callsign: Example input: "lz1abc"
        :return: Returns dictionary of the type:
                 {'name': 'Spratly Islands', 'cq_zone': 26, 'itu_zone': 50, 'continent': 'AS', 'latitude': 9.88, 'longitude': -114.23, 'time_offset': -8.0, 'primary_prefix': '1S'}
        """
        # Check for exact matches within the prefix keys that start with '='
        exact_match_key = f'={callsign.strip()}'.upper()

        if exact_match_key in self.countries_by_prefix:
            return self.countries_by_prefix[exact_match_key]

        # Start removing characters from the right of the callsign and check for availability in the prefix keys (disregard the first character '=')
        for i in range(len(exact_match_key), 1, -1):
            if exact_match_key[1:i] in self.countries_by_prefix:
                return self.countries_by_prefix[exact_match_key[1:i]]

        # If no match is found, return None
        return None

    @staticmethod
    def parse_overrides(input_prefix : str) -> dict:
        """
        This function will extract any overriding values contained in the prefix/callsign: cq, itu zones, continent and others.
        The following special characters can be applied after an alias prefix:
        (#) 	Override CQ Zone
        [#] 	Override ITU Zone
        <#/#> 	Override latitude/longitude
        {aa} 	Override Continent
        ~#~ 	Override local time offset from GMT

        :param input_prefix: The input prefix from which the overriding values will be extracted.
                             Examples: "=RP79GPF(18)[32]", "CZ1(1)[2]"
        :return: dictionary containing the clean prefix and the cq, itu zones, continent, coord, gmt_offset
                 Example 1: {"prefix": "=AA5UZ", "cq_zone": "4", "itu_zone": "8","coordinates": None, "time_offset": None}
                 Example 2: None,  in case no overriding characters were found
        """
        # Regular expressions for the patterns
        override_patterns = {
            'cq_zone': r'\((.*?)\)',
            'itu_zone': r'\[(.*?)\]',
            'coordinates': r'<(.*?)>',
            'continent': r'\{(.*?)\}',
            'time_offset': r'~(.*?)~'
        }

        # Initialize an empty dictionary to store results
        extracted_data = {}

        # check if there are overriding
        if not any(char in input_prefix for char in "([<}~"):  # Only check for overrides if the prefix contains any of the special characters
            return None

        # Loop through each pattern and find matches
        for key, pattern in override_patterns.items():
            match = re.search(pattern, input_prefix)
            if match:
                extracted_data[key] = match.group(1)
            else:
                extracted_data[key] = None

        # Remove extracted parts from the original string
        for key, pattern in override_patterns.items():
            input_prefix = re.sub(pattern, '', input_prefix)

        # Cleaned string is stored in 'original_string' key
        extracted_data['prefix'] = input_prefix.strip()

        return extracted_data

    # def printAllPrefixes(self):
    #     print(json.dumps(self.countries_by_prefix, indent=4, sort_keys=True))
