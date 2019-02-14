import datetime
from datetime import date
import calendar
import pytz


class MyDateTools:
    def get_current_year(self):
        """
        Returns the current year.
        """

        return int(date.today().year)

    def get_current_month(self):
        """
        Returns the current month in string format. If the month val's length is
        one, a zero is concatenated to the front month val.
        """

        return datetime.date.today().month

    def get_current_day(self):

        return datetime.date.today().day

    def get_current_date(self):
        """
        Returns the current date formatted as year-month-day.
        """
        
        return datetime.datetime.today().strftime('%Y-%m-%d')

    def get_currentpretty_date(self):
        month = self.get_current_month()
        day = self.get_current_day()
        year = self.get_current_year()
        month_str = calendar.month_name[month]

        return month_str + ' ' + str(day) + ', ' + str(year)

    def get_endof_week(self):
        """
        Returns the full date of the last day of the current week
        """

        current_date = datetime.date.today()
        current_day = current_date.day
        day_val = current_date.weekday()
        end_day = 0
        increment_vals = {0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1, 6: 1}

        if day_val == 7:
            end_day = current_day
        else:
            for i in range(7):
                if day_val == i:
                    end_day = current_day + increment_vals[i]
                    break

        date_str = str(current_date.year) + '-' + str(current_date.month) + '-' + str(end_day)
        date_obj = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()

        return date_obj

    def getcurrent_beginend_ofmonth(self):
        """
        Returns the beginning and end dates of the current month
        """

        year = self.get_current_year()
        month = self.get_current_month()
        num_of_days = calendar.monthrange(year, month)[1]
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, num_of_days)

        return start_date, end_date

    def get_begin_endof_month(self, month, year):
        """
        Return the beginning and end dates of desired month and year
        :param month: The desired month
        :param year: The desired year
        """

        num_of_days = calendar.monthrange(year, month)[1]
        start_date = datetime.date(year, month, 1)
        end_date = datetime.date(year, month, num_of_days)
        
        return str(start_date), str(end_date)

    def get_posyears_set(self):
        """
        Returns a list of future years, starting with the current year.
        """

        current_year = self.get_current_year()
        year_list = []
        year = 0

        for i in range(6):
            year = current_year + i
            year_list.append(year)

        return year_list

    def get_current_time(self):
        """
        Returns the current Utah time in 12hr format.
        """

        our_zone = pytz.timezone('US/Arizona')
        current_time = datetime.datetime.now(our_zone)

        return str(current_time.strftime('%I:%M %p'))
