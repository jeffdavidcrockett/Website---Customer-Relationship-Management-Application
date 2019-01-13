from flask import render_template, flash, redirect, url_for, request, jsonify
from app import app, db, mail
from app.forms import LoginForm, CreateAppointmentForm, SearchAppointmentForm, ClientForm, MessageInput, NoteInput, SearchClientForm, \
MyAppointmentSearch, NewClientDisplayOptions, SendAgreementSearch, SendEmail
from flask_login import current_user, login_user, login_required, logout_user
from app.models import Marketer, Appointment, Memo, Note, Client
from app.tables import SearchResults
from werkzeug.urls import url_parse
import datetime
from sqlalchemy import desc
from flask_mail import Message 


@app.route('/test2', methods=['GET', 'POST'])
def test2():
	return render_template('test2.html')

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
	client_form = ClientForm()

	if client_form.validate_on_submit():
		client = Client(first_name=client_form.first_name.data,
						last_name=client_form.last_name.data,
						phone=client_form.phone.data,
						email=client_form.email.data,
						credit_score=client_form.credit_score.data,
						desired_funding=client_form.desired_funding.data, 
						signup_date=str(datetime.date.today()))
		db.session.add(client)
		db.session.commit()
	return render_template('clients.html', client_form=client_form)

@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
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

	return render_template('login_mine.html', form=form)

@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/manager', methods=['GET', 'POST'])
@login_required
def manager():
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
		# return redirect(url_for('manager'))

	if mssg_in.validate_on_submit():
		mssg = Memo(author=str(current_user), 
					body=mssg_in.message_in.data, 
					date=str(datetime.date.today()))
		db.session.add(mssg)
		db.session.commit()
		return redirect(url_for('manager'))

	if note_in.validate_on_submit():
		note = Note(author=str(current_user), 
					body=note_in.note_in.data, 
					date=str(datetime.date.today()))
		db.session.add(note)
		db.session.commit()
		return redirect(url_for('manager'))

	return render_template('dashboard.html', mssg_in=mssg_in, mssgs=mssgs, 
						   note_in=note_in, notes=notes, appts=appts,
						   results=results, clients_display_form=clients_display_form)

@app.route('/my-appts', methods=['GET', 'POST'])
@login_required
def my_appts():
	form = MyAppointmentSearch()
	appointments = Appointment.query.filter_by(date=str(datetime.date.today())).all()

	if form.validate_on_submit():
		if form.filter_menu.data == '1':
			appointments = Appointment.query.filter_by(date=str(datetime.date.today())).all()
		elif form.filter_menu.data == '2':
			pass
		else:
			# appointments = Appointment.query.filter()
			pass
		return redirect(url_for('my_appts'))

	return render_template('my_appts.html', form=form, appointments=appointments)

@app.route('/createappt', methods=['GET', 'POST'])
@login_required
def create_appt():
	create_form = CreateAppointmentForm()

	if create_form.validate_on_submit():
		date = create_form.year.data + '-' + create_form.month.data + '-' + create_form.day.data
		time = create_form.hour.data + ':' + create_form.minute.data + ' ' + create_form.ampm.data
		
		if create_form.client_id1.data == create_form.client_id2.data:
			client = Client.query.filter_by(id=create_form.client_id1.data).first()

			if client:
				appt = Appointment(client_first=client.first_name, 
								   client_last=client.last_name, 
								   date=date, 
								   time=time, 
								   notes=create_form.notes.data, 
								   creator=current_user, 
								   client=client)
				db.session.add(appt)
				db.session.commit()
				flash('Appointment added')
			else:
				flash('No clients exists under that ID!')
		else:
			flash('ID fields do not match!')

		return redirect(url_for('create_appt'))

	return render_template('create_appt.html', create_form=create_form)

@app.route('/search-appt', methods=['GET', 'POST'])
@login_required
def search_appt():
	form = SearchAppointmentForm()
	appt_results = db.session.query(Appointment).order_by(Appointment.id.desc()).limit(15)

	if form.validate_on_submit():
		selection = form.search_by.data
		
		if selection == '1':
			chars = '!@#$%^&*()_-+|\\}]{[;:/?.>,<`~='
			state = True

			while state:
				for char in chars:
					if char in form.search_field.data:
						state = False
				break

			if state:
				raw_results = Appointment.query.filter_by(marketer_id=int(form.search_field.data)).all()
				results = list(reversed(raw_results))
			else:
				results = db.session.query(Appointment).order_by(Appointment.id.desc()).limit(15)
				flash('Please enter only integers')
		elif selection == '2':
			results = Appointment.query.filter_by(client_first=form.search_field.data).all()
		elif selection == '3':
			results = Appointment.query.filter_by(client_last=form.search_field.data).all()
		elif selection == '4':
			results = Appointment.query.filter_by(date=form.search_field.data).all()
		return render_template('search_appt.html', results=results, form=form)

	return render_template('search_appt.html', results=appt_results, form=form)

@app.route('/search-clients', methods=['GET', 'POST'])
@login_required
def search_clients():
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
		# return render_template('search_clients.html', results=client_results, form=form)

	return render_template('search_clients.html', results=client_results, form=form)

@app.route('/send-agreement', methods=['GET', 'POST'])
@login_required
def send_agreement():
	client_result = ['', '', '', '', '']
	search_form = SendAgreementSearch()

	if search_form.validate_on_submit():
		client_result = Client.query.filter_by(id=int(search_form.id_in.data)).all()
		if client_result:
			return render_template('send_agreement.html', search_form=search_form, 
								   client=client_result, email=client_result[0].email)
		else:
			flash('No client found with that ID')

	return render_template('send_agreement.html', search_form=search_form, 
						   client=client_result, email='')

@app.route('/email_process', methods=['GET', 'POST'])
@login_required
def email_process():
	try:
		email = request.args.get('email')
		msg = Message("JMR Funding Contract", sender="jmrtestsend@gmail.com", recipients=[email])
		with app.open_resource("JMR Merchant Agreement_encrypted_.pdf") as fp:
			msg.attach("JMR Merchant Agreement_encrypted_.pdf", "application/pdf", fp.read())
		mail.send(msg)
		
		return jsonify(success=1)
	except Exception:
		return jsonify(success=0)
