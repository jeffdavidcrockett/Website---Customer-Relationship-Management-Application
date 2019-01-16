from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db, mail
from app.forms import LoginForm, CreateAppointmentForm, SearchAppointmentForm, ClientForm, MessageInput, NoteInput, SearchClientForm, \
MyAppointmentSearch, NewClientDisplayOptions, SendAgreementSearch, DataSelection, AddInteractionForm, PreInteractButton
from flask_login import current_user, login_user, login_required, logout_user
from app.models import Marketer, Appointment, Memo, Note, Client, Interaction
from werkzeug.urls import url_parse
import datetime
from sqlalchemy import desc
from flask_mail import Message 
from ToolsClass.tools import MyTools
import sqlalchemy
from sqlalchemy import func, distinct, extract


my_tools = MyTools()

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	"""
	Test Client sign up page. Probably will be deleted. Client enters information 
	and is logged into database table Client.
	"""
	client_form = ClientForm()

	if client_form.validate_on_submit():
		try:
			client = Client(first_name=client_form.first_name.data,
							last_name=client_form.last_name.data,
							phone=client_form.phone.data,
							email=client_form.email.data,
							credit_score=client_form.credit_score.data,
							desired_funding=client_form.desired_funding.data, 
							signup_date=str(datetime.date.today()))
			db.session.add(client)
			db.session.commit()
		except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.InvalidRequestError) as e:
			db.session.rollback()
			return render_template('bad_email.html')
	return render_template('clients.html', client_form=client_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	"""
	Login page for employees. If user is already logged in, they are redirected to 
	the manager dashboard page.
	"""
	if current_user.is_authenticated:
		return redirect(url_for('manager'))
	form = LoginForm()

	if form.validate_on_submit():
		user = Marketer.query.filter_by(username=form.username.data).first()
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('login'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('manager')
		return redirect(next_page)

	return render_template('login.html', form=form)

@app.route('/logout')
def logout():
	"""
	Logs the current user out and redirects to login page.
	"""
	logout_user()
	return redirect(url_for('login'))

@app.route('/manager', methods=['GET', 'POST'])
@login_required
def manager():
	"""
	Main dashboard page for authenticated employees. New and uncontacted clients are displayed.
	Also, there is a global message board as well as a personal notepad.
	"""
	mssgs = db.session.query(Memo).order_by(Memo.id.desc()).limit(20)
	notes = db.session.query(Note).order_by(Note.id.desc()).limit(20)
	appts_query = Appointment.query.filter_by(date=str(datetime.date.today())).all()
	results = db.session.query(Client).order_by(Client.id.desc()).filter_by(appointments=None)
	appts = len(appts_query)
	mssg_in = MessageInput()
	note_in = NoteInput()
	clients_display_form = NewClientDisplayOptions()
	
	if clients_display_form.validate_on_submit():
		if clients_display_form.display_by.data == '1':
			results = db.session.query(Client).order_by(Client.id.desc()).filter_by(appointments=None).limit(7)
		elif clients_display_form.display_by.data == '2':
			results = Client.query.filter_by(signup_date=str(datetime.date.today())).limit(7)

	if mssg_in.validate_on_submit():
		mssg = Memo(author=str(current_user), 
					body=mssg_in.message_in.data, 
					date=str(datetime.date.today()))
		db.session.add(mssg)
		db.session.commit()

	if note_in.validate_on_submit():
		note = Note(author=str(current_user), 
					body=note_in.note_in.data, 
					date=str(datetime.date.today()))
		db.session.add(note)
		db.session.commit()

	return render_template('dashboard.html', mssg_in=mssg_in, mssgs=mssgs, 
						   note_in=note_in, notes=notes, appts=appts,
						   results=results, clients_display_form=clients_display_form)

@app.route('/my-appts', methods=['GET', 'POST'])
@login_required
def my_appts():
	"""
	User's appointments are displayed. Can choose between displaying today's appointments, this 
	weeks's appointments, and this month's appointments. Also, user can delete their appointments. 
	It is done through jQuery/JSON/AJAX, so look on this route's HTML page for script. The route that 
	the AJAX activates is delete_appt(). 
	"""
	form = MyAppointmentSearch()
	appointments = Appointment.query.filter_by(date=str(datetime.date.today())).all()

	if form.validate_on_submit():
		selection = form.filter_menu.data
		if selection == '2':
			current_date = my_tools.get_current_date()
			endof_week = my_tools.get_endof_week()
			appointments = db.session.query(Appointment).filter(Appointment.date.between(current_date, 
														 endof_week)).order_by(Appointment.date.asc())
		elif selection == '3':
			start_date, end_date = my_tools.getcurrent_beginend_ofmonth()
			appointments = db.session.query(Appointment).filter(Appointment.date.between(start_date, 
														 end_date)).order_by(Appointment.date.asc())
		else:
			return redirect(url_for('my_appts'))

	return render_template('my_appts.html', form=form, appointments=appointments)

@app.route('/createappt', methods=['GET', 'POST'])
@login_required
def create_appt():
	"""
	User can create appointments. It will log appointments into database, as well as the 
	interaction of 'Appointment'.
	"""
	create_form = CreateAppointmentForm()

	if create_form.validate_on_submit():
		date = create_form.year_menu.data + '-' + create_form.month_menu.data + '-' + create_form.day_menu.data
		date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date() 
		time = create_form.hour_menu.data + ':' + create_form.minute_menu.data + ' ' + create_form.ampm_menu.data
		
		if create_form.client_id1.data == create_form.client_id2.data:

			client = Client.query.filter_by(id=create_form.client_id1.data).first()

			if client:
				appt = Appointment(client_first=client.first_name, 
								   client_last=client.last_name, 
								   date=date_obj, 
								   time=time, 
								   notes=create_form.notes.data, 
								   creator=current_user, 
								   client=client)
				interaction = Interaction(client_id=create_form.client_id1.data,
										  marketer=str(current_user),
										  date=my_tools.get_current_date(),
										  time=my_tools.get_current_time(),
										  type_of="Appointment",
										  about=create_form.notes.data)

				db.session.add(appt)
				db.session.add(interaction)
				db.session.commit()
				flash('Appointment added')
			else:
				flash('No clients exists under that ID!')
		else:
			flash('ID fields must match!')

		return redirect(url_for('create_appt'))

	return render_template('create_appt.html', create_form=create_form)

@app.route('/search-appt', methods=['GET', 'POST'])
@login_required
def search_appt():
	"""
	User can do a global search of all appointments by all users. Can search by Marketer ID, 
	Client first, Client last, and date. Date must be formatted as example: 2019-03-05.
	"""
	form = SearchAppointmentForm()
	appt_results = db.session.query(Appointment).order_by(Appointment.id.desc()).limit(15)

	if form.validate_on_submit():
		selection = form.search_by.data
		
		if selection == '1':
			chars = '!@#$%^&*()_-+|\\}]{[;:/?.>,<`~='
			state = True
			user_input = form.search_field.data

			while state:
				for char in user_input:
					if char in chars or char.isalpha():
						state = False
				break

			if state:
				raw_results = Appointment.query.filter_by(marketer_id=int(form.search_field.data)).all()
				appt_results = list(reversed(raw_results))
			else:
				appt_results = db.session.query(Appointment).order_by(Appointment.id.desc()).limit(15)
				flash('Please enter only integers')
		elif selection == '2':
			appt_results = Appointment.query.filter_by(client_first=form.search_field.data).all()
		elif selection == '3':
			appt_results = Appointment.query.filter_by(client_last=form.search_field.data).all()
		elif selection == '4':
			appt_results = Appointment.query.filter_by(date=form.search_field.data).all()

	return render_template('search_appt.html', results=appt_results, form=form)

@app.route('/search-clients', methods=['GET', 'POST'])
@login_required
def search_clients():
	"""
	Global search of all clients. Can search by client's first name, last name, and
	client id.
	"""
	form = SearchClientForm()
	client_results = db.session.query(Client).order_by(Client.id.desc()).limit(100)

	if form.validate_on_submit():
		selection = form.search_by.data
		if selection == '1':
			client_results = Client.query.filter_by(first_name=form.search_field.data).all()
		elif selection == '2':
			client_results = Client.query.filter_by(last_name=form.search_field.data).all()
		elif selection == '3':
			if not form.search_field.data.isalpha():
				client_results = Client.query.filter_by(id=form.search_field.data).all()
			else:
				flash("Enter only numbers")

	return render_template('search_clients.html', client_results=client_results, form=form)

@app.route('/send-agreement', methods=['GET', 'POST'])
@login_required
def send_agreement():
	"""
	Allows marketer to send an email to a specific client. jQuery/JSON/AJAX is used, so look for 
	the script at top of send_agreement.html file. The route that is activated by AJAX is 
	email_process().
	"""
	client_result = ['']
	email = ''
	search_form = SendAgreementSearch()

	if search_form.validate_on_submit():
		client_result = Client.query.filter_by(id=int(search_form.id_in.data)).all()
		if client_result:
			email = client_result[0].email
		else:
			flash('No client found with that ID')

	return render_template('send_agreement.html', search_form=search_form, 
						   client=client_result, email=email)

@app.route('/email_process', methods=['GET', 'POST'])
@login_required
def email_process():
	"""
	This is the route that is activated by AJAX that comes from the send_agreement()
	route.
	"""
	try:
		email = request.args.get('email')
		msg = Message("JMR Funding Contract", sender="jmrtestsend@gmail.com", recipients=[email])
		with app.open_resource("JMR Merchant Agreement_encrypted_.pdf") as fp:
			msg.attach("JMR Merchant Agreement_encrypted_.pdf", "application/pdf", fp.read())
		mail.send(msg)
		
		return jsonify("Email was successfully sent to " + email)
	except Exception as e:
		return jsonify("ERROR. EMAIL FAILED TO SEND TO " + email)

@app.route('/view_client', methods=['GET', 'POST'])
@login_required
def view_client():
	"""
	This allows user to view a specific client in more detail, the client ID is used to
	search. They can add interactions when a specific user is pulled up. This is done 
	from the HTML file.
	"""
	client_search = SendAgreementSearch()
	interact_btn = PreInteractButton()
	client_result = ''
	interaction_results = ['']

	if client_search.validate_on_submit():
		client_result = Client.query.filter_by(id=client_search.id_in.data).first()
		interaction_results = Interaction.query.filter_by(client_id=client_search.id_in.data).all()

	return render_template('specific_client.html', client_search=client_search, 
							client=client_result, interactions=interaction_results, 
							interact_btn=interact_btn)

@app.route('/add_interact', methods=['GET', 'POST'])
@login_required
def add_interaction(client=None):
	"""
	Route activated from the specific_client.html file (from JSON?). Details of interaction 
	can be added and is logged to the database in Interaction table.
	"""
	client_id = request.args.get('client_id', None)
	client_result = Client.query.filter_by(id=client_id).first()
	interact_form = AddInteractionForm()

	if interact_form.validate_on_submit():
		date = interact_form.year_menu.data + '-' + interact_form.month_menu.data + '-' + interact_form.day_menu.data
		date_obj = datetime.datetime.strptime(date, '%Y-%m-%d').date()
		time = interact_form.hour_menu.data + ':' + interact_form.minute_menu.data + ' ' + interact_form.ampm_menu.data

		interaction = Interaction(client_id=client_id, 
								  marketer=str(current_user),
								  date=date_obj, 
								  time=time, 
								  type_of=interact_form.choices_menu.data, 
								  about=interact_form.details.data)
		db.session.add(interaction)
		db.session.commit()
		flash("Interaction added")

	return render_template('add_interact.html', client=client_result, interact_form=interact_form)

@app.route('/delete_appt', methods=['GET', 'POST'])
@login_required
def delete_appt():
	"""
	Activated through AJAX from my_appt() route. Will *not* allow a marketer to delete 
	other marketer's appointments, only their own.
	"""
	try:
		appt_id = request.args.get('apptId')
		appt = Appointment.query.filter_by(id=appt_id).first()
		current_marketer = Marketer.query.filter_by(username=str(current_user)).first()
		if appt:
			if appt.marketer_id == current_marketer.id:
				db.session.delete(appt)
				db.session.commit()
				return jsonify("Appointment successfully deleted.")
			else:
				return jsonify("You cannot delete other marketer's appointments.")
		else:
			return jsonify("Appointment does not exist, or was not able to be deleted.")
	except Exception as e:
		return jsonify("Fail")

@app.route('/data', methods=['GET', 'POST'])
@login_required
def our_data():
	"""
	Displays information gathered from database. Under construction.
	"""
	data_form = DataSelection()

	marketers = Marketer.query.all()
	clients = db.session.query(Client).filter_by(signup_date=my_tools.get_current_date())

	num_of_clients = 0
	for c in clients:
		num_of_clients += 1

	if data_form.validate_on_submit():
		selection = data_form.drop_menu.data
		if selection == '2':
			start_date, end_date = my_tools.getcurrent_beginend_ofmonth()
			clients = db.session.query(Client).filter(Client.signup_date >= 
													  start_date).filter(Client.signup_date <= end_date).all()
			num_of_clients = 0
			for c in clients:
				num_of_clients += 1

			return render_template('data.html', marketers=marketers, data_form=data_form, 
						   num_of_clients=num_of_clients)
		elif selection == '3':
			# year = my_tools.get_current_year()
			# # clients = db.session.query(distinct(func.date_part(year, Client.signup_date)))
			# clients = Client.query.filter(Client.signup_date.ilike("%2019%")).all()

			# num_of_clients = 0
			# for c in clients:
			# 	num_of_clients += 1

			# return render_template('data.html', marketers=marketers, data_form=data_form, 
			# 			   num_of_clients=num_of_clients)
			pass
		else:
			return redirect(url_for('our_data'))
	
	return render_template('data.html', marketers=marketers, data_form=data_form, 
						   num_of_clients=num_of_clients)
