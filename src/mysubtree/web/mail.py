import smtplib
import socket
import errno
import unicodedata
from flask import flash
from mysubtree.web.app import app

def ascii(string):
    return unicodedata.normalize('NFKD', string).encode('ascii', 'ignore')

def send_email(email, subject, body):
    #body = ascii(body)
    #subject = ascii(subject)
    
    if app.debug or app.testing:
        flash(body, category="info")
        return
    from_ = app.config["EMAIL_ADDRESS"]
    to = email
    
    try:
        _send_email(from_, to, subject, body)
    except socket.error, err:
        errorcode = err[0]
        if errorcode == errno.ECONNREFUSED:
            flash(body, category="info")
        else:
            raise

#-------------------------------------------------------------------------------
# http://mg.pov.lt/blog/unicode-emails-in-python.html
from smtplib import SMTP
from email.MIMEText import MIMEText
from email.Header import Header
from email.Utils import parseaddr, formataddr

def _send_email(sender, recipient, subject, body):
    """Send an email.

    All arguments should be Unicode strings (plain ASCII works as well).

    Only the real name part of sender and recipient addresses may contain
    non-ASCII characters.

    The email will be properly MIME encoded and delivered though SMTP to
    localhost port 25.  This is easy to change if you want something different.

    The charset of the email will be the first one out of US-ASCII, ISO-8859-1
    and UTF-8 that can represent all the characters occurring in the email.
    """

    # Header class is smart enough to try US-ASCII, then the charset we
    # provide, then fall back to UTF-8.
    header_charset = 'ISO-8859-1'

    # We must choose the body charset manually
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            body.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break

    # Split real name (which is optional) and email address parts
    sender_name, sender_addr = parseaddr(sender)
    recipient_name, recipient_addr = parseaddr(recipient)

    # We must always pass Unicode strings to Header, otherwise it will
    # use RFC 2047 encoding even on plain ASCII strings.
    sender_name = str(Header(unicode(sender_name), header_charset))
    recipient_name = str(Header(unicode(recipient_name), header_charset))

    # Make sure email addresses do not contain non-ASCII characters
    sender_addr = sender_addr.encode('ascii')
    recipient_addr = recipient_addr.encode('ascii')

    # Create the message ('plain' stands for Content-Type: text/plain)
    msg = MIMEText(body.encode(body_charset), 'plain', body_charset)
    msg['From'] = formataddr((sender_name, sender_addr))
    msg['To'] = formataddr((recipient_name, recipient_addr))
    msg['Subject'] = Header(unicode(subject), header_charset)

    # Send the message via SMTP to localhost:25
    smtp = SMTP("localhost")
    smtp.sendmail(sender, recipient, msg.as_string())
    smtp.quit()