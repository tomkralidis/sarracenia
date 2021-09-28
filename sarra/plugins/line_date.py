#!/usr/bin/env python3
"""comments:
    This plugin modifies the date of parent.line to a standard date fomrat: year-month-date hours:minutes:seconds
    An example of this date format is : 2021-09-06 11:09:00, which is Septemebr 6th, 2021 11:09PM
    Ten formats are acceptd so far, more can be added if needed (format on https://strftime.org/ ).
    FIXME: french input like Fev will not work - only Feb is accepted for the month
    If year is not provided, this means that the file is < 6 months old, so depending on todays date, assign
    appropriate year (for todays year: jan-jun -> assign prev year, for jul-dec assign current year)
    Note: is it possible for a file to be more than 6 months old and have the format Mo Day TIME ? (problematic)
"""

class Line_date(object):
    def __init__(self, parent):
        pass

    def normalize_date_format(self, parent):
        line_split = parent.line.split()
        # specify input for this routine, line format could change
        # line_mode.py format "-rwxrwxr-x 1 1000 1000 8123 24 Mar 22:54 2017-03-25-0254-CL2D-AUTO-minute-swob.xml"
        file_date = line_split[5] + " " + line_split[6] + " " + line_split[7]
        current_date = datetime.datetime.now()
        # case 1: the date contains '-' implies the date is in 1 string not 3 seperate ones, and H:M is also provided
        if "-" in file_date: file_date = line_split[5] + " " + line_split[6]
        for i in parent.accepted_date_formats:
            try:
                standard_date_format = datetime.datetime.strptime(file_date, i)
                # case 2: the year was not given, it is defaulted to 1900. Must find which year (this one or last one).
                if standard_date_format.year == 1900:
                    if standard_date_format.month - current_date.month >= 6:
                        standard_date_format = standard_date_format.replace(year=(current_date.year - 1))
                    else:
                        standard_date_format = standard_date_format.replace(year=current_date.year)
                parent.logger.debug("Oldline is: " + parent.line)
                parent.line = parent.line.replace(file_date, str(standard_date_format))
                parent.logger.debug("Newline is: " + parent.line)
                return
            except Exception as e:
                # try another date format
                pass

    def perform(self,parent):
        if hasattr(parent, 'line'):
            self.normalize_date_format(parent)
        return True

line_date = Line_date(self)
self.on_line = line_date.perform