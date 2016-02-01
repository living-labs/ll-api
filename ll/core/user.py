# This file is part of Living Labs Challenge, see http://living-labs.net.
#
# Living Labs Challenge is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Living Labs Challenge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with Living Labs Challenge. If not, see <http://www.gnu.org/licenses/>.

import random
import string
import hashlib
import datetime
import smtplib
from email.mime.text import MIMEText
from werkzeug import generate_password_hash
from db import db
from config import config


def send_email(user, txt, subject):
    if not config["SEND_EMAIL"]:
        return False
    try:
        msgtxt = "Hi %s,\n\n" % user["teamname"]
        msgtxt += txt
        msgtxt += "\n\n"
        msgtxt += "Some relevant urls:\n"
        msgtxt += "Website: %s\n" % config["URL_WEB"]
        msgtxt += "API: %s\n" % config["URL_API"]
        msgtxt += "Dashboard: %s\n" % config["URL_DASHBOARD"]
        msgtxt += "Documentation: %s\n" % config["URL_DOC"]
        msgtxt += "Code: %s\n" % config["URL_GIT"]
        msgtxt += "\n\n"
        msgtxt += "Please do not hesitate to ask any questions.\n"
        msgtxt += "\n\n"
        msgtxt += "With regards,\n"
        msgtxt += "The organizers"
        msg = MIMEText(msgtxt)
        msg['subject'] = "[Living Labs for %s] %s" % (config["COMPETITION_NAME"],subject)
        email_from = config["EMAIL_FROM"]
        email_to = user['email']
        msg['From'] = email_from
        msg['To'] = email_to
        s = smtplib.SMTP('localhost')
        s.sendmail(email_from, [email_to], msg.as_string())
        s.quit()
        return True
    except:
        raise Exception("Error sending email, either disable or setup properly.")


def notify_organizers(teamname):
    if not config["SEND_EMAIL"]:
        return False
    try:
        msgtxt = "%s just registered." % teamname
        msg = MIMEText(msgtxt)
        msg['subject'] = "[Living Labs] New Registration"
        email_from = config["EMAIL_FROM"]
        email_to = config["EMAIL_ORGANIZERS"]
        msg['From'] = email_from
        msg['To'] = email_to
        s = smtplib.SMTP('localhost')
        s.sendmail(email_from, email_to, msg.as_string())
        s.quit()
    except:
        raise Exception("Error sending email, either disable or setup properly.")


def send_password_email(user, password, subject="Password Reset"):
    txt = "Your password has been reset.\n"
    txt += "These are now your Living Labs account details:\n"
    txt += "API key: %s\n" % user["_id"]
    txt += "teamname: %s\n" % user["teamname"]
    txt += "email: %s\n" % user["email"]
    txt += "password: %s\n" % password
    return send_email(user, txt, subject)


def send_registration_email(user, password, subject="New Account"):
    txt = "Thank you for registering to Living Labs for %s.\n" % config["COMPETITION_NAME"]
    txt += "\n\n"
    txt += "These are your account details:\n"
    txt += "API key: %s\n" % user["_id"]
    txt += "teamname: %s\n" % user["teamname"]
    txt += "email: %s\n" % user["email"]
    txt += "password: %s\n" % password
    txt += "\n\n"
    txt += "Before you can participate, please fill out, scan, and email the form at "
    txt += "this location to us: %s\n" % config["URL_REGISTRATION_FORM"]
    return send_email(user, txt, subject)


def send_verification_email(user):
    txt = "We received and verified your signed registration form, thank you.\n"
    txt += "You are now ready to participate in Living Labs for %s.\n" % config["COMPETITION_NAME"]
    txt += "Please visit the dashboard to sign up for individual sites: %s/user/sites/\n" % config["URL_DASHBOARD"]
    txt += "\n\n"
    txt += "These are your %s account details:\n" % config["COMPETITION_NAME"]
    txt += "API key: %s\n" % user["_id"]
    txt += "teamname: %s\n" % user["teamname"]
    txt += "email: %s\n" % user["email"]
    return send_email(user, txt, "Verified")


def send_form_email(user):
    txt = "A while ago, you registered for Living Labs for %s" % config["COMPETITION_NAME"]
    txt += "The lab has started and clicks are flowing in steadily. "
    txt += "Before you can start using these clicks, we need you to fill out, scan, and email the application form at "
    txt += "this location as a reply to this email: %s\n" % config["URL_REGISTRATION_FORM"]
    txt += "Then, please follow this guide: %s\n\n" % config["URL_WEB"]
    txt += "These are your Living Labs account details:\n"
    txt += "API key: %s\n" % user["_id"]
    txt += "teamname: %s\n" % user["teamname"]
    txt += "email: %s\n" % user["email"]
    return send_email(user, txt, "Please Sign the Application Form")


def random_string(length):
    return ''.join(random.choice(string.ascii_lowercase + string.digits)
                   for _ in range(length))


def new_key(teamname, email):
    rstr = random_string(config["KEY_LENGTH"] / 2)
    hstr = str(hashlib.sha1(teamname + email).hexdigest())[:config["KEY_LENGTH"] / 2]
    return "-".join([hstr, rstr]).upper()


def new_user(teamname, email, password=None):
    if db.user.find({"teamname": teamname}).count():
        raise Exception("Teamname already exists: teamname = '%s'. "
                        "Please choose another name." % teamname)
    if db.user.find({"email": email}).count():
        raise Exception("Email already exists: email = '%s'. "
                        "Please choose another email address." % email)

    if password == None:
        password = random_string(config["PASSWORD_LENGHT"])

    #TODO: check valid email
    #TODO: send email with validation

    user = {
        "_id": new_key(teamname, email),
        "teamname": teamname,
        "email": email,
        "is_participant": True,
        "is_site": False,
        "is_verified": False,
        "signed_up_for": [],
        "is_admin": False,
        "creation_time": datetime.datetime.now(),
        "password": generate_password_hash(password),
    }
    send_registration_email(user, password)
    db.user.insert(user)
    return user


def verify_user(key):
    user = get_user(key)
    user["is_verified"] = True
    send_verification_email(user)
    db.user.save(user)


def unverify_user(key):
    user = get_user(key)
    user["is_verified"] = False
    db.user.save(user)


def reset_password(email):
    user = get_user_by_email(email)
    password = random_string(config["PASSWORD_LENGHT"])
    user["password"] = generate_password_hash(password)
    send_password_email(user, password, subject="Password Reset")
    db.user.save(user)


def set_admin(key):
    user = get_user(key)
    user["is_admin"] = True
    db.user.save(user)


def get_user(key):
    user = db.user.find_one({"_id": key})
    if not user:
        raise Exception("No such user.")
    return user


def get_user_by_email(email):
    user = db.user.find_one({"email": email})
    if not user:
        raise Exception("No such user.")
    return user


def get_users():
    return db.user.find()


def get_participants():
    return [u for u in get_users() if u["is_participant"]]


def delete_user(key):
    user = get_user(key)
    db.user.remove(user)


def set_sites(key, sites):
    user = get_user(key)
    user["signed_up_for"] = sites
    db.user.save(user)


def get_sites(key):
    user = get_user(key)
    if "signed_up_for" in user:
        return user["signed_up_for"]
    return {}
