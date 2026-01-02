import imaplib
import email
from email.header import decode_header
import re
from html.parser import HTMLParser
from io import StringIO

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    
    def handle_data(self, d):
        self.text.write(d)
    
    def get_data(self):
        return self.text.getvalue()

def strip_html_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

class GmailConnector:
    def __init__(self, email_address, app_password):
        self.email_address = email_address
        self.app_password = app_password
        self.imap = None
    
    def connect(self):
        try:
            self.imap = imaplib.IMAP4_SSL("imap.gmail.com")
            self.imap.login(self.email_address, self.app_password)
            return True
        except Exception as e:
            raise Exception(f"Failed to connect to Gmail: {str(e)}")
    
    def get_recent_emails(self, folder="INBOX", num_emails=10):
        if not self.imap:
            self.connect()
        
        self.imap.select(folder)
        status, messages = self.imap.search(None, "ALL")
        email_ids = messages[0].split()
        email_ids = email_ids[-num_emails:]
        
        emails = []
        for email_id in reversed(email_ids):
            try:
                status, msg_data = self.imap.fetch(email_id, "(RFC822)")
                msg = email.message_from_bytes(msg_data[0][1])
                
                subject = self._decode_header(msg["Subject"])
                sender = msg.get("From", "")
                date = msg.get("Date", "")
                body = self._get_email_body(msg)
                
                if body and len(body.strip()) > 10:
                    emails.append({
                        "id": email_id.decode(),
                        "subject": subject,
                        "sender": sender,
                        "date": date,
                        "body": body[:1500],
                        "body_full": body
                    })
            except Exception as e:
                print(f"Error processing email {email_id}: {e}")
                continue
        
        return emails
    
    def _decode_header(self, header):
        if header is None:
            return ""
        
        decoded = decode_header(header)
        header_text = ""
        
        for text, encoding in decoded:
            if isinstance(text, bytes):
                try:
                    header_text += text.decode(encoding or "utf-8")
                except:
                    header_text += text.decode("utf-8", errors="ignore")
            else:
                header_text += str(text) if text else ""
        
        return header_text
    
    def _get_email_body(self, msg):
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))
                
                if content_type == "text/plain" and "attachment" not in content_disposition:
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        if body and len(body.strip()) > 50:
                            break
                    except:
                        pass
            
            if not body or len(body.strip()) < 50:
                for part in msg.walk():
                    content_type = part.get_content_type()
                    content_disposition = str(part.get("Content-Disposition"))
                    
                    if content_type == "text/html" and "attachment" not in content_disposition:
                        try:
                            html_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            body = strip_html_tags(html_body)
                            break
                        except:
                            pass
        else:
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    body = payload.decode('utf-8', errors='ignore')
                else:
                    body = str(msg.get_payload())
                
                if '<html' in body.lower() or '<body' in body.lower():
                    body = strip_html_tags(body)
            except:
                body = str(msg.get_payload())
        
        body = self._clean_text_light(body)
        return body
    
    def _clean_text_light(self, text):
        if not text:
            return ""
        
        text = re.sub(r'http[s]?://\S+', '[URL]', text)
        text = re.sub(r'\S+@\S+', '[EMAIL]', text)
        
        text = re.sub(r'\[image:.*?\]', '', text)
        text = re.sub(r'\[cid:.*?\]', '', text)
        
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r' {3,}', ' ', text)
        
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            if len(line) > 2: 
                cleaned_lines.append(line)
        
        text = '\n'.join(cleaned_lines)
        return text.strip()
    
    def disconnect(self):
        if self.imap:
            try:
                self.imap.close()
                self.imap.logout()
            except:
                pass
