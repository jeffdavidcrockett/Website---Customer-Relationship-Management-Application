from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from MyTools.DateTool.date_tools import MyDateTools

date_tools = MyDateTools()
years = date_tools.get_posyears_set()

default_year = str(date_tools.get_current_year())
default_month = str(date_tools.get_current_month())
if len(default_month) == 1:
	default_month = '0' + default_month
default_day = str(date_tools.get_current_day())
if len(default_day) == 1:
	default_day = '0' + default_day

years_ = [(str(years[0]), str(years[0])), (str(years[1]), str(years[1])),
	      (str(years[2]), str(years[2])), (str(years[3]), str(years[3])),
		  (str(years[4]), str(years[4])), (str(years[5]), str(years[5]))]

months = [('01', 'Jan'), ('02', 'Feb'), ('03', 'Mar'), 
		  ('04', 'Apr'), ('05', 'May'), ('06', 'Jun'), 
		  ('07', 'Jul'), ('08', 'Aug'), ('09', 'Sep'),
		  ('10', 'Oct'), ('11', 'Nov'), ('12', 'Dec')]

days = [('01', '01'), ('02', '02'), ('03', '03'), ('04', '04'), 
		('05', '05'), ('06', '06'), ('07', '07'), ('08', '08'), 
	    ('09', '09'), ('10', '10'), ('11', '11'), ('12', '12'), 
		('13', '13'), ('14', '14'), ('15', '15'), ('16', '16'), 
		('17', '17'), ('18', '18'), ('19', '19'), ('20', '20'), 
		('21', '21'), ('22', '22'), ('23', '23'), ('24', '24'), 
		('25', '25'), ('26', '26'), ('27', '27'), ('28', '28'), 
		('29', '29'), ('30', '30'), ('31', '31')]

hours = [('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), 
		 ('5', '5'), ('6', '6'), ('7', '7'), ('8', '8'), 
		 ('9', '9'), ('10', '10'), ('11', '11'), ('12', '12')]

minutes = [('00', '00'), ('05', '05'), ('10', '10'), ('15', '15'), 
		   ('20', '20'), ('25', '25'), ('30', '30'), ('35', '35'),
		   ('40', '40'), ('45', '45'), ('50', '50'), ('55', '55')]

ampm = [('AM', 'AM'), ('PM', 'PM')]


class ClientForm(FlaskForm):
	credit_menu = [('720+', '720+'), 
				   ('680 - 719', '680 - 719'), 
				   ('650 - 679', '650 - 679'), 
				   ('600 - 649', '600 - 649'), 
				   ('599 - less', '599 - less')]

	funding_menu = [('$10,000 - $24,999', '$10,000 - $24,999'), 
					('$25,000 - $49,999', '$25,000 - $49,999'), 
					('$50,000 - $99,999', '$50,000 - $99,999'),
					('$100,000+', '$100,000+')]

	first_name = StringField('First Name', validators=[DataRequired()])
	last_name = StringField('Last Name', validators=[DataRequired()])
	phone = StringField('Phone', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired()])
	credit_score = SelectField('Credit Score', choices=credit_menu, default=1)
	desired_funding = SelectField('Desired Funding', choices=funding_menu, default=1)
	submit = SubmitField('Get Started')


class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()], render_kw={"placeholder": "Username"})
	password = PasswordField('Password', validators=[DataRequired()], render_kw={"placeholder": "Password"})
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In')


class CreateAppointmentForm(FlaskForm):
	client_id1 = StringField('Client ID', validators=[DataRequired()])
	client_id2 = StringField('Client ID again', validators=[DataRequired()])
	year_menu = SelectField('Year', choices=years_, default=default_year)
	month_menu = SelectField('Month', choices=months, default=default_month)
	day_menu = SelectField('Day', choices=days, default=default_day)
	hour_menu = SelectField('Hour', choices=hours, default='1')
	minute_menu = SelectField('Min.', choices=minutes, default='00')
	ampm_menu = SelectField('', choices=ampm, default='AM')
	notes = StringField('Notes', validators=[DataRequired()])
	create = SubmitField('Create Appt')


class SearchAppointmentForm(FlaskForm):
	search_menu = [('1', 'Marketer ID'), 
				   ('2', 'Client First'),
				   ('3', 'Client Last'), 
				   ('4', 'Date')]

	search_by = SelectField('Filter by', choices=search_menu, default=1)
	search_field = StringField('Input', validators=[DataRequired()])
	search = SubmitField('Search')


class MyAppointmentSearch(FlaskForm):
	filters = [('1', 'Today'),
			   ('2', 'This Week'),
			   ('3', 'This Month')]

	filter_menu = SelectField('Filter by', choices=filters, default='1')
	search = SubmitField('Search')


class SearchClientForm(FlaskForm):
	search_menu = [('1', 'First name (Input Rqrd)'),
				   ('2', 'Last name (Input Rqrd)'),
				   ('3', 'ID (Input Rqrd)'), 
				   ('4', 'Uncontacted'), 
				   ('5', 'Today'), 
				   ('6', 'Contract Sent'), 
				   ('7', 'Underwriting'),
				   ('8', 'Approved'), 
				   ('9', 'Pulling Credit'), 
				   ('10', 'Contracted'), 
				   ('11', 'Apps'), 
				   ('12', 'Liquidation'), 
				   ('13', 'Complete'), 
				   ('14', 'Declined')]
	search_by = SelectField('Filter by', choices=search_menu, default=1)
	search_field = StringField('Input')
	search = SubmitField('Search')


class MessageInput(FlaskForm):
	message_in = StringField('Type...', validators=[DataRequired()])
	submit = SubmitField('Submit')


class NoteInput(FlaskForm):
	note_in = StringField('Type...', validators=[DataRequired()])
	submit = SubmitField('Submit')


class NewClientDisplayOptions(FlaskForm):
	choices = [('1', 'Uncontacted'), 
			   ('2', 'Today')]
	display_by = SelectField('Filter by', choices=choices, default=1)
	refresh = SubmitField('Refresh')


class SendAgreementSearch(FlaskForm):
	id_in = StringField('Enter Client ID:', validators=[DataRequired()])
	lookup = SubmitField('Lookup Client')


class PreInteractButton(FlaskForm):
	add_btn = SubmitField('Add Interaction')


class DataSelection(FlaskForm):
	choices = [('1', 'Today'), 
			   ('2', 'This Month'),
			   ('3', 'This Year')]
	drop_menu = SelectField('Filter by', choices=choices, default=1)
	submit = SubmitField('Refresh')


class AddInteractionForm(FlaskForm):
	choices = [('Applied for credit cards', 'Applied for credit cards'),
			   ('Credit Card Approval', 'Credit Card Approval'), 
			   ('Appointment', 'Appointment'),
			   ('Received contract from', 'Received contract from')]

	year_menu = SelectField('Year', choices=years_, default=default_year)
	month_menu = SelectField('Month', choices=months, default=default_month)
	day_menu = SelectField('Day', choices=days, default=default_day)
	hour_menu = SelectField('Hour', choices=hours, default='1')
	minute_menu = SelectField('Minutes', choices=minutes, default='00')
	ampm_menu = SelectField('', choices=ampm, default='AM')
	choices_menu = SelectField('Interaction Type', choices=choices, default=1)
	details = StringField('Details', validators=[DataRequired()])
	submit = SubmitField('Submit')


class ClientStatusForm(FlaskForm):
	choices = [('Contract Sent', 'Contract Sent'), 
			   ('Underwriting', 'Underwriting'), 
			   ('Approved', 'Approved')]

	status_menu = SelectField('Status', choices=choices, default='Contract Sent')
	why = StringField('Why', validators=[DataRequired()])
	submit = SubmitField('Submit Status Change')
