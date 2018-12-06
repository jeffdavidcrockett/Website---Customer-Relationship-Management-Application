from flask_table import Table, Col


class SearchResults(Table):
	id = Col('Id', show=False)
	client_first = Col('First name')
	client_last = Col('Last name')
	date = Col('Date')
	time = Col('Time')
	notes = Col('Notes')
