import imaplib
import email
from email.header import decode_header

import os

def decode_filename(filename):
    decoded_parts = []
    for part, encoding in decode_header(filename):
        if isinstance(part, bytes):
            if encoding:
                decoded_parts.append(part.decode(encoding))
            else:
                decoded_parts.append(part.decode('utf-8'))
        else:
            decoded_parts.append(part)
    decoded_string = ' '.join(decoded_parts)
    return decoded_string

# Email account credentials
email_address = "Your Gmail Address"
password = "Your App Password"

# IMAP server settings (cho Gmail)
imap_server = "imap.gmail.com"
imap_port = 993

imap = imaplib.IMAP4_SSL(imap_server, imap_port)
imap.login(email_address, password)

imap.select("INBOX")

# Search for all emails in the inbox
status, email_ids = imap.search(None, "ALL")
email_ids = email_ids[0].split()

for i, email_id in enumerate(email_ids):
    status, msg_data = imap.fetch(email_id, "(RFC822)")
    msg = email.message_from_bytes(msg_data[0][1])

    if msg.get_content_subtype() != "mixed":
        continue
    subject, encoding = decode_header(msg["Subject"])[0]
    if isinstance(subject, bytes):
            subject = subject.decode(encoding or "utf-8")
    sender = decode_filename(msg["From"])
    date = msg.get("Date")

    if 'text' in msg.get_content_type():
        body = msg.get_payload(decode=True).decode()
    if 'multipart' in msg.get_content_type():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode()

    parent_dir = "/content/mails"
    dirname = subject
    save_directory = os.path.join(parent_dir, dirname)
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # write file content
    with open(os.path.join(save_directory, 'content.txt'), 'w') as f:
        f.write(f"Subject: {subject}\n")
        f.write(f"From: {sender}\n")
        f.write(f"Date: {date}\n")
        f.write(f"Body: {body}\n")
    # write attachment files
    for part in msg.walk():
        content_disposition = part.get("Content-Disposition")
        if content_disposition and "attachment" in content_disposition:
            filename = part.get_filename()
            if filename:
                filename = decode_filename(filename)
                file_path = os.path.join(save_directory, filename)
                with open(file_path, "wb") as attachment_file:
                    attachment_file.write(part.get_payload(decode=True))

imap.logout()
