from app import app, db
from app.models import Marketer, Client, Appointment, Memo, Note


@app.shell_context_processor
def make_shell_context():
	return {'db': db, 'Marketer': Marketer, 'Client': Client, 'Appointment': Appointment, 'Memo': Memo,
			'Note': Note}