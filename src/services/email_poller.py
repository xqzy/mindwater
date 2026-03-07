import imaplib
import email
from sqlalchemy.orm import Session
from src.database import crud

def poll_email_inbox(db: Session, user: str, password: str, host: str):
    mail = imaplib.IMAP4_SSL(host)
    mail.login(user, password)
    mail.select("inbox")
    
    status, messages = mail.search(None, 'UNSEEN')
    items = []
    
    if status == 'OK':
        for num in messages[0].split():
            status, data = mail.fetch(num, '(RFC822)')
            if status == 'OK':
                raw_email = data[0][1]
                msg = email.message_from_bytes(raw_email)
                
                subject = msg['Subject']
                body = ""
                
                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()
                
                raw_text = f"Subject: {subject} - {body.strip()}"
                inbox_item = crud.create_inbox_item(db, raw_text=raw_text, source_tag="email")
                items.append(inbox_item)
                
                # Mark as read/deleted or move (for now just store as read)
                mail.store(num, '+FLAGS', '\\Seen')
                
    mail.logout()
    return items
