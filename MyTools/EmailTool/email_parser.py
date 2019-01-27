import imaplib
import email


class EmailParserTool:
    def __init__(self):
        self.EMAIL_DOMAIN = ""
        self.EMAIL_USRNME = "" + self.EMAIL_DOMAIN
        self.EMAIL_PASSWD = ""
        self.MAIL_SERVER = 'smtp.gmail.com'
        self.FROM_CONDITION = ''
        self.SUBJECT_CONDITION = ''
        self.EMAIL_STATE = 'UNSEEN'
        self.mail = ''

    def connect(self):
        self.mail = imaplib.IMAP4_SSL(self.MAIL_SERVER)
        self.mail.login(self.EMAIL_USRNME, self.EMAIL_PASSWD)

    def find_clients(self):
        # Select inbox and get all messages
        self.mail.select('INBOX')
        status, messages = self.mail.search(None, self.EMAIL_STATE)

        if status == 'OK':
            for msg_num in messages[0].split():
                typ, data = self.mail.fetch(msg_num, '(RFC822)')
                for raw_msg in data:
                    if isinstance(raw_msg, tuple):
                        new_email = email.message_from_bytes(raw_msg[1])
                        if self.FROM_CONDITION in new_email['From']:
                            if new_email['Subject'][0:2] == self.SUBJECT_CONDITION:
                                msg = new_email.get_payload()
                                self.mail.close()
                                return msg

    def parse_and_commit(self, email_):
        formatted_email = email_.splitlines()

        loan_type = formatted_email[0]
        business_name = formatted_email[1]
        business_class = formatted_email[2]
        first_name = formatted_email[4].split(' ')[0]
        last_name = formatted_email[4].split(' ')[1]
        email = formatted_email[5]
        business_phone = formatted_email[6]
        mobile_phone = formatted_email[7]
        zip_code = formatted_email[8]
        business_type = formatted_email[10]
        loan_option = formatted_email[13]
        loan_amount = formatted_email[14]
        avg_monthly_income = formatted_email[16]
        credit_score = formatted_email[17]
        retirement = formatted_email[18]
        company_type = formatted_email[20]
        business_length = formatted_email[21]
        company_website = formatted_email[22]
        physical_biz_location = formatted_email[23]
        business_plan = formatted_email[24]

        return loan_type, business_name, business_class, first_name, last_name, email, \
        business_phone, mobile_phone, zip_code, business_type, loan_option, \
        loan_amount, avg_monthly_income, credit_score, retirement, company_type, \
        business_length, company_website, physical_biz_location, business_plan
