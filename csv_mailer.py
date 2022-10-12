import smtplib
import csv
import time
from datetime import datetime, timedelta

# CONFIG
CSVFILE = "recipients.csv"
TEMPLATE = "mail_template.txt"

SENDER = ''
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587

USE_TLS = 1  # connessione criptata con SMTP server (1/si 0/no)
AUTH_REQUIRED = 1  # autorizzazione SMTP
SMTP_USER = ''  # per autorizzazione,  SMTP mail
SMTP_PASS = ''  # per autorizzazione,  SMTP psw

# TEST
DRY_RUN = 0  # non invia mail ma stampa errori nel caso in cui ce ne sarebbero potuti essere
SAFE_MODE = 0  # invia mail al recipients al posto di csv
RECIPIENTS = ['alberto.tomasin@gmail.com']

template = open(TEMPLATE, "r")
csvfile = open(CSVFILE, "r")

mail_template = template.read()
csv_reader = csv.DictReader(csvfile)  # add 'dialect="semicolon"' if necessary
lines = len(list(csv_reader))

now = datetime.today()
print("Ora attuale: "+ str(now))
result_2 = now + timedelta(seconds=(lines * 1.8 + (lines/50*120)))
print("Ora stimata di fine esecuzione: " + str(result_2))

csvfile = open(CSVFILE, "r")
csv_reader = csv.DictReader(csvfile)  # add 'dialect="semicolon"' if necessary
# Inizia sessione SMTP
smtpresult = 0
if not DRY_RUN:
    print("Sessione SMTP aperta")
    session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    # session.set_debuglevel(1)
    session.ehlo()
    if USE_TLS and session.has_extn("STARTTLS"):  # not tested!
        session.starttls()
        session.ehlo()
    if AUTH_REQUIRED:
        session.login(SMTP_USER, SMTP_PASS)
counter = 1
# Invio mail
for row in csv_reader:
    if counter % 50 == 0:
        print("Chiudo sessione SMTP")
        session.close()
        print("E' tempo di dormire")
        time.sleep(120);
        print("Riapro la sessione SMTP")
        if not DRY_RUN:
            print("Sessione SMTP aperta")
            session = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            # session.set_debuglevel(1)
            session.ehlo()
            if USE_TLS and session.has_extn("STARTTLS"):  # not tested!
                session.starttls()
                session.ehlo()
            if AUTH_REQUIRED:
                session.login(SMTP_USER, SMTP_PASS)

    counter += 1

    # prendo dati da csv
    surname = ""
    givenname = ""
    email = row["email"]
    id = "Questionario yeswork - lavoro in un tocco"
    recipient = "\"" + givenname + " " + surname + "\" " + "<" + email + ">"
    time.sleep(1)
    print(str(counter) + " - Invio mail a " + email)
    mssg = mail_template.replace("$NAME$", givenname)
    #mssg = mssg.replace("$SENDER$", SENDER)
    #mssg = mssg.replace("$RECIPIENT$", recipient)
    #mssg = mssg.replace("$EMAIL$", email)
    mssg = mssg.replace("$ID$", id)

    if SAFE_MODE:
        recipients = RECIPIENTS
        print("[SAFE MODE] Invio mail a " + recipients[0])
        mssg = mssg + "\r\nquesto mess sarebbe dovuto andare a: " + email
    else:
        recipients = [email]

    if DRY_RUN:
        print("[DRY RUN] Invio mail a  " + recipients[0])
        print()
        print(mssg)
        print()
        print("################################################################################")
    else:
        print(mssg)
        smtpresult = session.sendmail(SENDER, recipients, mssg.encode('UTF-8'))

    if smtpresult:
        errstr = ""
        for recip in smtpresult.keys():
            errstr = """Errore nell'invio della mail a: %s

    L'errore e': %s
    %s

    %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
        raise smtplib.SMTPException(errstr)
