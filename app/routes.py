from flask import render_template, flash, redirect, url_for, request, jsonify, json
from app import app, db, mail, csrf
from app.forms import LoginForm, CreateAppointmentForm, SearchAppointmentForm, ClientForm, MessageInput, NoteInput, SearchClientForm, \
MyAppointmentSearch, NewClientDisplayOptions, SendAgreementSearch, DataSelection, AddInteractionForm, ClientStatusForm, \
ClientManualAdd
from flask_login import current_user, login_user, login_required, logout_user
from app.models import Marketer, Appointment, Memo, Note, Client, Interaction, ClientNote
from werkzeug.urls import url_parse
import datetime
from flask_mail import Message 
import sqlalchemy
from MyTools.EmailTool.email_parser import EmailParserTool
from MyTools.DateTool.date_tools import MyDateTools


date_tool = MyDateTools()
years = date_tool.get_posyears_set()
pretty_date = date_tool.get_currentpretty_date()

# @app.route('/', methods=['GET', 'POST'])
# @app.route('/index', methods=['GET', 'POST'])
# @login_required
# def index():
# 	"""
# 	Test Client sign up page. Probably will be deleted. Client enters information 
# 	and is logged into database table Client.
# 	"""

# 	client_form = ClientForm()

# 	if client_form.validate_on_submit():
# 		try:
# 			client = Client(first_name=client_form.first_name.data,
# 							last_name=client_form.last_name.data,
# 							phone=client_form.phone.data,
# 							email=client_form.email.data,
# 							credit_score=client_form.credit_score.data,
# 							desired_funding=client_form.desired_funding.data, 
# 							signup_date=str(datetime.date.today()))
# 			db.session.add(client)
# 			db.session.commit()
# 		except (sqlalchemy.exc.SQLAlchemyError, sqlalchemy.exc.InvalidRequestError) as e:
# 			db.session.rollback()
# 			return render_template('bad_email.html')
# 	return render_template('clients.html', client_form=client_form)

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

@csrf.exempt
@app.route('/', methods=['GET', 'POST'])
@app.route('/manager', methods=['GET', 'POST'])
@login_required
def manager():
	"""
	Main dashboard page for authenticated employees. New and uncontacted clients are displayed.
	Also, there is a global message board as well as a personal notepad.
	"""

	mssgs = db.session.query(Memo).order_by(Memo.id.desc()).limit(20)
	notes = db.session.query(Note).order_by(Note.id.desc()).limit(20)
	appts = Appointment.query.filter_by(date=str(datetime.date.today())).all()
	new_clients = Client.query.filter_by(signup_date=str(datetime.date.today())).all()
	num_of_appts = len(appts)

	# if mssg_in.validate_on_submit():
	# 	mssg = Memo(author=str(current_user), 
	# 				body=mssg_in.message_in.data, 
	# 				date=str(datetime.date.today()))
	# 	db.session.add(mssg)
	# 	db.session.commit()

	# if note_in.validate_on_submit():
	# 	note = Note(author=str(current_user), 
	# 				body=note_in.note_in.data, 
	# 				date=str(datetime.date.today()))
	# 	db.session.add(note)
	# 	db.session.commit()

	return render_template('dashboard.html', mssgs=mssgs, 
						   notes=notes, appts=num_of_appts,
						   new_clients=new_clients, pretty_date=pretty_date)

@csrf.exempt
@app.route('/jmrfunding/api/global-msg', methods=['POST'])
@login_required
def add_global_msg():
	try:
		data = request.get_json()
		msg_content = data['msg']
		msg = Memo(author=str(current_user), 
				   body=msg_content, 
				   date=str(datetime.date.today()))

		db.session.add(msg)
		db.session.commit()
 
		return jsonify("Successful")
	except Exception as e:
		return jsonify("Unsuccessful")

@csrf.exempt
@app.route('/jmrfunding/api/note', methods=['POST'])
@login_required
def add_notepad():
	try:
		data = request.get_json()
		note_content = data['note']
		note = Note(author=str(current_user), 
				   body=note_content, 
				   date=str(datetime.date.today()))

		db.session.add(note)
		db.session.commit()
 
		return jsonify("Successful")
	except Exception as e:
		return jsonify("Unsuccessful")

@csrf.exempt
@app.route('/load_client_process', methods=['GET', 'POST'])
@login_required
def load_client_process():
	if request.method == 'POST':
		try:
			load_client = EmailParserTool()
		    
			try:
				load_client.connect()
			except Exception as e:
				return jsonify("Email connect failure")
				
			try:
				email_ = load_client.find_clients()
			except Exception as e:
				return jsonify("Client find failure")

			try:
				client_data = load_client.parse_and_commit(email_)
			except Exception as e:
				return jsonify("Parse failure or No new clients")

			try:
				new_client = Client(first_name=client_data[3], last_name=client_data[4], 
	                        		email=client_data[5], credit_score=client_data[13], 
	                            	signup_date=date_tool.get_current_date(), 
	                            	status='None', loan_type=client_data[0], 
	                            	business_name=client_data[1], 
	                            	business_class=client_data[2], 
	                            	business_phone=client_data[6], 
	                            	mobile_phone=client_data[7], 
	                            	zip_code=client_data[8], 
	                            	business_type=client_data[9], 
	                            	loan_option=client_data[10], 
	                            	loan_amount=client_data[11], 
	                            	avg_monthly_income=client_data[12], 
	                            	retirement=client_data[14], 
	                            	company_type=client_data[15], 
	                            	business_length=client_data[16], 
	                            	company_website=client_data[17], 
	                            	physical_biz_location=client_data[18], 
	                            	business_plan=client_data[19])
				db.session.add(new_client)
				db.session.commit()
			except Exception as e:
				err_msg = str(e)
				return jsonify(err_msg)

			return jsonify("Successfully Added Client")
		except Exception as e:
			return jsonify("Fail")

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
			current_date = date_tool.get_current_date()
			endof_week = date_tool.get_endof_week()
			appointments = db.session.query(Appointment).filter(Appointment.date.between(current_date, 
														 endof_week)).order_by(Appointment.date.asc())
		elif selection == '3':
			start_date, end_date = date_tool.getcurrent_beginend_ofmonth()
			appointments = db.session.query(Appointment).filter(Appointment.date.between(start_date, 
														 end_date)).order_by(Appointment.date.asc())
		else:
			return redirect(url_for('my_appts'))

	return render_template('my_appts.html', form=form, appointments=appointments, pretty_date=pretty_date)

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
										  date=date_tool.get_current_date(),
										  time=date_tool.get_current_time(),
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

	return render_template('create_appt.html', create_form=create_form, pretty_date=pretty_date)

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

	return render_template('search_appt.html', results=appt_results, form=form, pretty_date=pretty_date)

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
		elif selection == '4':
			client_results = db.session.query(Client).order_by(Client.id.desc()).filter_by(appointments=None).all()
		elif selection == '5':
			client_results = Client.query.filter_by(signup_date=str(datetime.date.today())).all()
		elif selection == '6':
			client_results = Client.query.filter_by(status='Contract Sent').all()
		elif selection == '7':
			client_results = Client.query.filter_by(status='Underwriting').all()
		elif selection == '8':
			client_results = Client.query.filter_by(status='Approved').all()
		elif selection == '9':
			client_results = Client.query.filter_by(status='Pulling Credit').all()
		elif selection == '10':
			client_results = Client.query.filter_by(status='Contracted').all()
		elif selection == '11':
			client_results = Client.query.filter_by(status='Apps').all()
		elif selection == '12':
			client_results = Client.query.filter_by(status='Liquidation').all()
		elif selection == '13':
			client_results = Client.query.filter_by(status='Complete').all()
		elif selection == '14':
			client_results = Client.query.filter_by(status='Declined').all()

	return render_template('search_clients.html', client_results=client_results, form=form, 
						   pretty_date=pretty_date)

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
						   client=client_result, email=email, pretty_date=pretty_date)

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

@csrf.exempt
@app.route('/view_client', methods=['GET', 'POST'])
@login_required
def view_client():
	"""
	Detailed view of client. Can change status here. Status change is done through AJAX, look 
	in HTML file. Route that gets activated is update_client().
	"""

	client_id = request.args.get('client_id')
	client_result = Client.query.filter_by(id=client_id).first()
	interaction_results = db.session.query(Interaction).filter_by(client_id=client_id)[:-30:-1]
	note_results = db.session.query(ClientNote).filter_by(client_id=client_id)[:-30:-1]

	return render_template('specific_client.html', client=client_result, 
						   interactions=interaction_results, yearsList = years, 
						   notes=note_results, pretty_date=pretty_date)

@app.route('/manual-add', methods=['GET', 'POST'])
@login_required
def manual_add():
	"""
	Marketer can manually add client
	"""

	manual_form = ClientManualAdd()

	return render_template('manual-add-client.html', manual_form=manual_form, pretty_date=pretty_date)

@csrf.exempt
@app.route('/jmrfunding/api/clients/<int:client_id>', methods=['PUT'])
@login_required
def update_client_status(client_id):
	"""
	Route that updates the client status, as well as adding an interaction.
	"""

	try:
		data = request.get_json()
		status_to = data['statusTo']

		client = Client.query.filter_by(id=client_id).first()
		client.status = status_to
		interaction = Interaction(client_id=client_id,
		 						  marketer=str(current_user),
		 						  date=date_tool.get_current_date(),
		 						  time=date_tool.get_current_time(),
								  type_of='Status Change',
								  about='Changed status to ' + status_to)
		db.session.add(interaction)
		db.session.commit()
		client_updated = Client.query.filter_by(id=client_id).first()
		
		return jsonify({'clientStatus': client_updated.status})
	except Exception as e:
		return jsonify("Unsuccessful")

@csrf.exempt
@app.route('/jmrfunding/api/clients', methods=['POST'])
@login_required
def create_client():
	"""
	API access for creating new clients manually
	"""

	try:
		data = request.get_json()
		new_client = Client(first_name=data['firstName'], last_name=data['lastName'], 
		                    email=data['email'], credit_score=data['creditScore'], 
		                    signup_date=date_tool.get_current_date(), 
		                    status='None', 
		                    business_name=data['bizName'], 
		                    business_class=data['bizClass'], 
		                    business_phone=data['bizPhone'], 
		                    mobile_phone=data['mobilePhone'], 
		                    zip_code=data['zipCode'], 
		                    business_type=data['bizType'], 
		                    loan_option=data['loanPurpose'], 
		                    loan_amount=data['loanAmount'], 
		                    avg_monthly_income=data['avgMonthlyInc'], 
		                    retirement=data['retirement'], 
		                    company_type=data['companyType'], 
		                    business_length=data['bizLength'], 
		                    company_website=data['website'], 
		                    physical_biz_location=data['physicalLocation'], 
		                    business_plan=data['bizPlan'])
		db.session.add(new_client)
		db.session.commit()
		return jsonify("Successfully added Client")
	except Exception as e:
		return jsonify("Unsuccessful")

@csrf.exempt
@app.route('/jmrfunding/api/appointments', methods=['POST'])
@login_required
def create_appt_process():
	"""
	API access for creating appointments
	"""
	
	try:
		data = request.get_json()
		client_id = data['clientId']
		appt_date = data['apptDate']
		appt_time = data['apptTime']
		appt_notes = data['apptNotes']
		date_obj = datetime.datetime.strptime(appt_date, '%Y-%m-%d').date()

		client = Client.query.filter_by(id=client_id).first()
		appointment = Appointment(client_first=client.first_name, 
								  client_last=client.last_name, 
								  date=date_obj, 
								  time=appt_time, 
								  notes=appt_notes, 
								  creator=current_user, 
								  client=client)
		interaction = Interaction(client_id=client_id,
		 						  marketer=str(current_user),
		 						  date=date_tool.get_current_date(),
		 						  time=date_tool.get_current_time(),
								  type_of='Appointment Created',
							      about=appt_notes)
		db.session.add(appointment)
		db.session.add(interaction)
		db.session.commit()

		return jsonify("Appointment successfully created")
	except Exception as e:
		return jsonify("Unsuccessful")

@csrf.exempt
@app.route('/jmrfunding/api/notes/<int:client_id>', methods=['POST'])
@login_required
def create_client_note(client_id):
	try:
		data = request.get_json()
		note_contents = data['noteContents']
		note = ClientNote(client_id=client_id, 
						  marketer=str(current_user), 
						  body=note_contents)
		db.session.add(note)
		db.session.commit()
		updated_notes = db.session.query(ClientNote).filter_by(client_id=client_id)[:-30:-1]
		marketer_list = []
		body_list = []

		for i in range(len(updated_notes)):
			marketer_list.append(updated_notes[i].marketer)
			body_list.append(updated_notes[i].body)

		return jsonify({"marketers": marketer_list, "bodies": body_list})
	except Exception as e:
		return jsonify("Unsuccessful")

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

	return render_template('add_interact.html', client=client_result, interact_form=interact_form, 
						   pretty_date=pretty_date)

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

	marketers = Marketer.query.all()
	curr_month = date_tool.get_current_month()
	curr_year = date_tool.get_current_year()

	jan_start, jan_end = date_tool.get_begin_endof_month(1, curr_year)
	jan_clients = db.session.query(Client).filter(Client.signup_date.between(jan_start, 
												  jan_end)).count()
	feb_start, feb_end = date_tool.get_begin_endof_month(2, curr_year)
	feb_clients = db.session.query(Client).filter(Client.signup_date.between(feb_start, 
												  feb_end)).count()
	mar_start, mar_end = date_tool.get_begin_endof_month(3, curr_year)
	mar_clients = db.session.query(Client).filter(Client.signup_date.between(mar_start, 
												  mar_end)).count()
	apr_start, apr_end = date_tool.get_begin_endof_month(4, curr_year)
	apr_clients = db.session.query(Client).filter(Client.signup_date.between(apr_start, 
												  apr_end)).count()
	may_start, may_end = date_tool.get_begin_endof_month(5, curr_year)
	may_clients = db.session.query(Client).filter(Client.signup_date.between(may_start, 
												  may_end)).count()
	jun_start, jun_end = date_tool.get_begin_endof_month(6, curr_year)
	jun_clients = db.session.query(Client).filter(Client.signup_date.between(jun_start, 
												  jun_end)).count()
	jul_start, jul_end = date_tool.get_begin_endof_month(7, curr_year)
	jul_clients = db.session.query(Client).filter(Client.signup_date.between(jul_start, 
												  jul_end)).count()
	aug_start, aug_end = date_tool.get_begin_endof_month(8, curr_year)
	aug_clients = db.session.query(Client).filter(Client.signup_date.between(aug_start, 
												  aug_end)).count()
	sep_start, sep_end = date_tool.get_begin_endof_month(9, curr_year)
	sep_clients = db.session.query(Client).filter(Client.signup_date.between(sep_start, 
												  sep_end)).count()
	oct_start, oct_end = date_tool.get_begin_endof_month(10, curr_year)
	oct_clients = db.session.query(Client).filter(Client.signup_date.between(oct_start, 
												  oct_end)).count()
	nov_start, nov_end = date_tool.get_begin_endof_month(11, curr_year)
	nov_clients = db.session.query(Client).filter(Client.signup_date.between(nov_start, 
												  nov_end)).count()
	dec_start, dec_end = date_tool.get_begin_endof_month(12, curr_year)
	dec_clients = db.session.query(Client).filter(Client.signup_date.between(dec_start, 
												  dec_end)).count()

	month_list = [jan_clients, feb_clients, mar_clients, apr_clients, may_clients, jun_clients, 
			      jul_clients, aug_clients, sep_clients, oct_clients, nov_clients, dec_clients]

	if curr_month < 12:
		for i in range(curr_month, 12):
			month_list[i] = None

	return render_template('data.html', marketers=marketers, pretty_date=pretty_date, 
						   jan_clients=month_list[0], feb_clients=month_list[1], 
						   mar_clients=month_list[2], apr_clients=month_list[3],
						   may_clients=month_list[4], jun_clients=month_list[5],
						   jul_clients=month_list[6], aug_clients=month_list[7],
						   sep_clients=month_list[8], oct_clients=month_list[9],
						   nov_clients=month_list[10], dec_clients=month_list[11])
