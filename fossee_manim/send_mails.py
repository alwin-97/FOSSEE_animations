from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
from django.utils.crypto import get_random_string
from os import listdir, path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from time import sleep
from textwrap import dedent
from random import randint
from smtplib import SMTP
from string import punctuation, digits
from hashlib import sha256
import logging.config
import re
try:
	from string import letters
except ImportError:
	from string import ascii_letters as letters
from fossee_anime.settings import (
					EMAIL_HOST,
					EMAIL_PORT,
					EMAIL_HOST_USER,
					EMAIL_HOST_PASSWORD,
					EMAIL_USE_TLS,
					PRODUCTION_URL,
					SENDER_EMAIL,
					ADMIN_EMAIL
					)


__author__ = "Akshen Doke"


def validateEmail(email):
	if len(email) > 7:
		if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$",
					email) is not None:
			return 1
		return 0


def generate_activation_key(username):
	"""Generates hashed secret key for email activation"""
	chars = letters + digits + punctuation
	secret_key = get_random_string(randint(10, 40), chars)
	return sha256((secret_key + username).encode('utf-8')).hexdigest()


def send_email(request, call_on, contributor=None, key=None, proposal=None):
	'''
	'''

	try:
		with open(path.join(settings.LOG_FOLDER,
				  'emailconfig.yaml'), 'r') as configfile:
			config_dict = yaml.load(configfile)
		logging.config.dictConfig(config_dict)
	except:
		print('File Not Found and Configuration Error')

	if call_on == "Registration":
		message = dedent("""\
					Thank you for registering as a contributor at FOSSEE Animations.
					Please click on the below link to activate your account {0}/activate_user/{1}
					Once you've activated your account, you can go ahead and submit a proposal.

					In case you have any queries regarding submition of proposal(s),
					revert to this email.

					Best regards,
					FOSSEE Animations Team""".format(PRODUCTION_URL, key))

		logging.info("New Registration from: %s", request.user.email)
		try:
			send_mail(
				"User/Contributor Registration at FOSSEE, IIT Bombay", message,
				SENDER_EMAIL, [request.user.email], fail_silently=True)

		except Exception:
			send_smtp_email(request=request,
				subject="User/Contributor Registration - FOSSEE, IIT Bombay",
				message=message, other_email=request.user.email,
				)
	elif call_on == 'released':
		message = dedent("""\
					Hey {0},

					Congratulations! your animation has been published on the FOSSEE animation website.
					People will be able to search for your animation within 72 working hours.

					Please start with your honorarium process. Visit https://animations.fossee.in/honorarium/ for more details.

					In case of queries, please revert to this
					email.

					Best regards,
					FOSSEE Animations Team""".format(contributor.profile.user.username))

		logging.info("Released Animation: %s", request.user.email)
		send_mail(
			"Congratulations! Your Animation has been Accepted!", message, SENDER_EMAIL,
				[contributor.profile.user.email], fail_silently=True
				)
		"""create a table and add the status as mail send"""
	elif call_on == 'rejected':
		message = dedent("""\
					Dear {0},

					Thank you for your patience. We're sorry to inform that your proposal was unsuccessful.
					However, do not be discouraged. You can work on the feedback given by the reviewer or send us another proposal on a different topic!

					If you have any queries or if you think there has been some mistake, please revert back to this email.

					Best regards,
					FOSSEE Animations Team""".format(contributor.profile.user.username))

		logging.info("FOSSEE Animations | Proposal Outcome: %s", request.user.email)
		send_mail(
			"FOSSEE Animations Status Update", message, SENDER_EMAIL,
			[contributor.profile.user.email], fail_silently=True
				)
	elif call_on == 'changes':
		message = dedent("""\
					Hey {0},

					Please check your proposal {1} for comments by our reviewers
					Follow this link to login {2}/login

					In case of queries, please revert to this
					email.

					Best regards,
					FOSSEE Animations Team""".format(contributor.profile.user.username,
								    proposal.title, PRODUCTION_URL))

		logging.info("Comment by Reviewer: %s", request.user.email)
		send_mail(
			"FOSSEE Animations Comment by Reviewer", message, SENDER_EMAIL,
			[contributor.profile.user.email], fail_silently=True)
	elif call_on == 'proposal_form':
		message = dedent("""\
					Hey {0},

					Thank you for submitting the Proposal for stage 1.
					Please find the attachment, fill the form and reply to this e-mail.

					In case of queries, please revert to this
					email.

					Best regards,
					FOSSEE Animations Team""".format(contributor.profile.user.username))

		logging.info("Animation Proposal Form 2: %s", request.user.email)
		subject = "FOSSEE Animations Proposal Form 2"
		msg = EmailMultiAlternatives(subject, message, SENDER_EMAIL,
				[contributor.profile.user.email])
		attachment_paths = path.join(settings.MEDIA_ROOT, "Proposal_Form")
		files = listdir(attachment_paths)
		for f in files:
			attachment = open(path.join(attachment_paths, f), 'rb')
			part = MIMEBase('application', 'octet-stream')
			part.set_payload((attachment).read())
			encoders.encode_base64(part)
			part.add_header('Content-Disposition', "attachment; filename= %s " % f)
			msg.attach(part)
		msg.send()
