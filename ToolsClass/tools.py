from datetime import date

class MyTools:
	def get_current_year(self):
		current_year = int(date.today().year) 

		return current_year

	def get_posyears_set(self):
		current_year = self.get_current_year()
		year_list = []
		year = 0

		for i in range(6):
			year = current_year + i
			year_list.append(year)

		return year_list
