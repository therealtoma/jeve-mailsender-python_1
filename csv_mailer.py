import smtplib
import csv

# CONFIG
CSVFILE = "recipients.csv"
TEMPLATE = "mail_template.txt"

SENDER = 'andre.ramolivaz@jeve.it'
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

# Invio mail
for row in csv_reader:
    # prendo dati da csv
    surname = row["Nome"]
    givenname = row["Cognome"]
    email = row["Email"]
    id = row["ID"]
    recipient = "\"" + givenname + " " + surname + "\" " + "<" + email + ">"

    print("Sending mail to " + email)
    mssg = mail_template.replace("$NAME$", givenname + " " + surname)
    mssg = mssg.replace("$SENDER$", SENDER)
    mssg = mssg.replace("$RECIPIENT$", recipient)
    mssg = mssg.replace("$EMAIL$", email)
    mssg = mssg.replace("$ID$", id)

    if SAFE_MODE:
        recipients = RECIPIENTS
        print("[SAFE MODE] Sto inviando la mail a " + recipients[0])
        mssg = mssg + "\r\nquesto mess sarebbe dovuto andare a: " + email
    else:
        recipients = [email]

    if DRY_RUN:
        print("[DRY RUN] Sto inviando la mail a  " + recipients[0])
        print()
        print(mssg)
        print()
        print("################################################################################")
    else:
        smtpresult = session.sendmail(SENDER, recipients, mssg)

    if smtpresult:
        errstr = ""
        for recip in smtpresult.keys():
            errstr = """Non bestemmiare ma non sono riuscito ad inviare la mail a: %s

    Sto cazzo di server lancia errori del tipo: %s
    %s

    %s""" % (recip, smtpresult[recip][0], smtpresult[recip][1], errstr)
        raise smtplib.SMTPException(errstr)
