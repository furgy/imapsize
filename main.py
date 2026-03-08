# Importing flask module in the project is mandatory 
# An object of Flask class is our WSGI application. 
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user, UserMixin, LoginManager, login_user, logout_user
from flask_caching import Cache
import re
import imaplib
import json
import email
  
class User(UserMixin):
    id = ''
    password = ''
    server = ''

    def __init__(self, id, password, server):
        self.id = id
        self.password = password
        self.server = server
    
cuser = None

cache = Cache()
app = Flask(__name__)

app.config['CACHE_TYPE'] = 'simple'
app.config['USE_SESSION_FOR_NEXT'] = True
app.secret_key = 'aflkjlkj383owtjoinslf38433thio;'
login_manager = LoginManager(app)
login_manager.login_view = "login"
cache.init_app(app)

@app.route('/favicon.ico')
def favicon():
    return redirect(url_for('static',filename='img/favicon.ico'))

@login_manager.user_loader
def user_loader(email):
    print(f'In user_loader...')
    if cuser is None:
        return

    return cuser

def login_imap_user(email, password, server='imap.1and1.com'):
    mail = imaplib.IMAP4_SSL(server)
    try:
        print(f'IMAP SSL Login Attempt to: {server}, with credentials {email}')
        result, msg = mail.login(email,password)
        if result == 'OK':
            return True
        else:
            return False
    except:
        return False

@app.route('/login', methods=['GET','POST'])
def login():
    global cuser
    if request.method == 'GET':
        return render_template('login.html')

    email = request.form['email']
    password = request.form['password']
    server = request.form['server']
    print(f'Server: {server}')
    if login_imap_user(email, password, server):
        user = User(email, password, server)
        # user.password = password
        # print(f'cuser in login: {cuser}')
        cuser = user
        # print(f'User object: {user.id}, password: {user.password}')
        login_user(user)
        flash('You have successfully logged in.','primary')
        # print(f'Current User: {current_user.id} with {current_user.password}')
        return redirect(url_for('index'))

    flash('Invalid Login. You must login to access this site.  Please check your credentials and try again!')
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    global cuser
    logout_user()
    cuser = None
    cache.clear()
    flash('Logout successful.','warning')
    return redirect(url_for('index'))

# The route() function of the Flask class is a decorator,  
# which tells the application which URL should call  
# the associated function. 
@app.route('/')
@login_required 
@cache.cached(timeout=1200)
def index(): 

    # print(f'(In Index) Current User: {current_user.id} with {current_user.password}')
           
    # mail = imaplib.IMAP4_SSL('imap.1and1.com')
    mail = imaplib.IMAP4_SSL(current_user.server)
    mail.login(current_user.id,current_user.password)

    mail.select()

    mailboxes = mail.list()

    list_response_pattern = re.compile('\\((?P<flags>.*?)\\) "(?P<delimiter>.*)" (?P<name>.*)')
    msg_pattern = re.compile( r'\d+ \(UID (\d+) RFC822.SIZE (\d+)\)')

    box_dict = {}
    total_mailbox_size = 0
    for mailbox in mailboxes[1]:
        flags, delimiter, mailbox_name = list_response_pattern.match(mailbox.decode('utf-8')).groups()
        mail.select(mailbox_name)
        resp,data = mail.uid('FETCH', '1:*', '(RFC822.SIZE)')
        mailbox_size = 0
        for message in data:
            if message is not None:
                msg_uid, msg_size = msg_pattern.match(message.decode('utf-8')).groups() 
                mailbox_size = mailbox_size + int(msg_size)
        box_dict[mailbox_name] = int(mailbox_size)
        total_mailbox_size = total_mailbox_size + mailbox_size

    sorted_box_dict = sorted(box_dict.items(), key=lambda x: x[1], reverse=True)

    result, msg = mail.close()
    result, msg = mail.logout()

    return render_template('index.html', sbd=sorted_box_dict, tms=total_mailbox_size)

@app.route('/listmail')
@login_required
def listmail():
    
    mb = request.args.get('mb')
    if mb is not None:
        mail_messages, total_mailbox_size = retrieve_mailbox(mb)
    
    return render_template('listmail.html', mm=mail_messages, tms=total_mailbox_size, mb=mb)

@cache.memoize(1200)
def retrieve_mailbox(mb):
    print(f'Mailbox to retrieve: {mb}')

    mail_messages = []
    mail = imaplib.IMAP4_SSL(current_user.server)
    mail.login(current_user.id,current_user.password)

    mail.select(mb)

    result, data = mail.uid('search', None, "ALL")

    mb_item_list = data[0].split()

    size_pattern = re.compile('\d+ \(UID \d+ RFC822.SIZE (\d+)')
    total_mailbox_size = 0

    for item in mb_item_list:
        result2, email_data = mail.uid('fetch', item, '(RFC822.SIZE BODY.PEEK[HEADER] FLAGS)')
        raw_email = email_data[0][1].decode('utf-8')
        email_message = email.message_from_string(raw_email)
        msg_size = size_pattern.match(email_data[0][0].decode('utf-8')).groups()
        size_ = msg_size[0]
        to_ = email_message['To']
        from_ = email_message['From']
        subject_ = email_message['Subject']
        date_ = email_message['Date']
        msg_id_ = email_message['Message-ID']

        mail_message = {
            'id': msg_id_,
            'date': date_,
            'to': to_,
            'from': from_,
            'size': int(size_),
            'subject': subject_
        }

        mail_messages.append(mail_message)
        total_mailbox_size = total_mailbox_size + int(size_)

    result, msg = mail.close()
    result, msg = mail.logout()
    
    return mail_messages, total_mailbox_size

@app.route('/clearcache')
@login_required 
def clearcache():
    cache.clear()
    flash('Cache cleared successfully','primary')
    return redirect(url_for('index'))

if __name__ == '__main__': 
    app.run(host='0.0.0.0',port='5000')