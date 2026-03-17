import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta, UTC
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

def get_flagged_emails(db: Session, user: str, password: str, host: str, days: int = 14):
    """
    Fetches flagged emails.
    Includes standard FLAGGED (Starred) and Gmail's Important markers.
    """
    mail = imaplib.IMAP4_SSL(host)
    try:
        mail.login(user, password)
        mail.select("inbox", readonly=True)
        
        since_date = (datetime.now() - timedelta(days=days)).strftime("%d-%b-%Y")
        
        if "gmail.com" in host.lower():
            search_criterion = f'(SINCE "{since_date}" OR FLAGGED (X-GM-RAW "is:important"))'
        else:
            search_criterion = f'(SINCE "{since_date}" FLAGGED)'
        
        status, messages = mail.search(None, search_criterion)
        
        if status != 'OK' or not messages[0]:
             status, messages = mail.search(None, 'FLAGGED')

        emails = []
        
        if status == 'OK' and messages[0]:
            nums = messages[0].split()
            nums.reverse() 
            
            for num in nums[:50]: 
                # Fetch headers AND body
                status, data = mail.fetch(num, '(RFC822)')
                if status == 'OK':
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    
                    def decode_mime_header(s):
                        if not s: return ""
                        parts = decode_header(s)
                        return "".join(
                            str(p[0], p[1] or "utf-8") if isinstance(p[0], bytes) else str(p[0])
                            for p in parts
                        )

                    subject = decode_mime_header(msg['Subject'])
                    from_ = decode_mime_header(msg['From'])
                    date = msg['Date']
                    message_id = msg['Message-ID'] or str(num.decode())
                    
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode(errors='replace')
                                break
                    else:
                        body = msg.get_payload(decode=True).decode(errors='replace')

                    if not crud.is_email_dismissed(db, message_id):
                        emails.append({
                            "id": message_id,
                            "subject": subject,
                            "from": from_,
                            "date": date,
                            "body": body.strip(),
                            "raw_num": num
                        })
        return emails
    finally:
        mail.logout()
