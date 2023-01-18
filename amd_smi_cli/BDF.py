import logging
import platform
import re


class BDF(object):
    """ BDF Class to cast and compare BDF objects using built-in python comparators

    Useful for validating a BDF string and converting it to a BDF object
    This allows us to handle BDF objects in a pythonic way

    Attributes:
        __eq__: The equals comparator
        __: An integer count of the eggs we have laid.
    """

    def __init__(self, bdf):
        """Init a BDF object"""
        if isinstance(bdf, BDF):
            self.segment, self.bus, self.device, self.function = tuple(bdf)
        else:
            if bdf.startswith("BDF("):
                bdf = bdf.replace('BDF(', '').replace(')', '')
            # Tell if this is baremetal vs Virtualization
            self.operating_system = platform.system()

            try:
                bdf_components = [int(x, 16) for x in re.split('[:.]', bdf)]
            except ValueError as e:
                logging.error(f"Invalid string passed: {bdf}")
                raise e

            self.segment = bdf_components[0] if len(bdf_components) == 4 else 0
            self.bus, self.device, self.function = bdf_components[-3:]
            if self.segment > 65535:
                raise ValueError("BDF Segment can't be greater than 65535")
            if self.bus > 255:
                raise ValueError("BDF Bus can't be greater than 255")
            if self.device > 31:
                raise ValueError("BDF Device can't be greater than 31")
            if self.function > 7:
                raise ValueError("BDF Function can't be greater than 7")

    def __eq__(self, passed_bdf):
        """Overrides the == operator and allows for BDF objects to be compared to BDF strings"""

        # Only accept strings and BDF objects
        if isinstance(passed_bdf, str):
            if passed_bdf == '':
                return False
            passed_bdf = BDF(passed_bdf)
        elif not isinstance(passed_bdf, BDF):
            return False

        if self.segment   == passed_bdf.segment and \
            self.bus      == passed_bdf.bus and \
            self.device   == passed_bdf.device and \
            self.function == passed_bdf.function:
            return True
        else:
            return False

    def __ne__(self, passed_bdf):
        """Overrides the != operator and allows for BDF objects to be compared to BDF strings"""
        # Since we overrided the == operator we can use that to make this simple
        return not self == passed_bdf

    def __add__(self, passed_bdf):
        """Overrides the + operator and allows for concatenation"""
        return str(self) + passed_bdf

    def __radd__(self, passed_bdf):
        """Overrides the + operator and allows for concatenation"""
        return passed_bdf + str(self)

    def __str__(self):
        """Cast BDF object to a string"""
        return "{:04X}:{:02X}:{:02X}:{}".format(self.segment, self.bus, self.device, self.function)

    def __repr__(self):
        """How the BDF object is represented"""
        return f"BDF({self})"

    def __iter__(self):
        """Make the BDF object iterable over its 4 values"""
        yield from (self.segment, self.bus, self.device, self.function)

    def __contains__(self, passed_bdf):
        """Overrided the 'in' comparator in python"""
        passed_bdf = str(BDF(passed_bdf))

        bdf_regex = "(?:[0-6]?[0-9a-fA-F]{1,4}:)?[0-2]?[0-9a-fA-F]{1,2}:[0-9a-fA-F]{1,2}\.[0-7]"
        for match in re.findall(bdf_regex, passed_bdf):
            if self == match:
                return True
        return False
