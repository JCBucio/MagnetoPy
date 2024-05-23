import pandas as pd
from datetime import datetime
from logging import getLogger

from src.magnetopy.magnetopy_utils.magnetopy_logging import MagnetopyLogging


class MagnetoPyConversionsHelper:
    @staticmethod
    def convert_date_to_decimal_date(date_str):
        """
        This function converts the date string to decimal date.

        :param date_str: str
        """
        magnetopy_logging: getLogger = MagnetopyLogging().create_magnetopy_logging(logger='MagnetoPyConversionsHelper: convert_date_to_decimal_date')
        date_formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y/%m/%d",
            "%Y-%m-%d",
            "%d %B %Y",
            "%d %b %Y",
            "%B %d, %Y",
            "%b %d, %Y"
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                pass
        else:
            raise ValueError(f"Date format not recognized: {date_str}")
        
        year = date_obj.year
        start_of_year = datetime(year, 1, 1)
        days_in_year = (datetime(year + 1, 1, 1) - start_of_year).days
        day_of_year = (date_obj - start_of_year).days + 1
        
        decimal_date = year + (day_of_year - 1) / days_in_year
        
        return decimal_date