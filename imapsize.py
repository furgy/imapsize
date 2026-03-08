import re
import imaplib

SPACE = 'Total Mailbox Size'

mail = imaplib.IMAP4_SSL('imap.1and1.com')
mail.login('shawn@furgason.com','tRb8obc7CvFMgnUvsp}q')

mail.select()

# resp,data = mail.uid('FETCH', '1:*', '(RFC822.SIZE)')
# print(data)

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
    # print(f'Mailbox: {mailbox_name:60}: {mailbox_size:>13,}')
    box_dict[mailbox_name] = mailbox_size
    total_mailbox_size = total_mailbox_size + mailbox_size

# print(f'{SPACE:69}: {total_mailbox_size:>13,}')
sorted_box_dict = sorted(box_dict.items(), key=lambda x: x[1], reverse=True)
for box in sorted_box_dict:
    print(f'Box: {box[0]:60}: {box[1]:>13,}')