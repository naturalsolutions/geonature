# Fonctions génériques permettant l'envoie de mails
import re
import logging

from smtplib import SMTPException
import requests
from flask import current_app
from flask_mail import Message

from geonature.utils.env import MAIL

log = logging.getLogger()

name_address_email_regex = re.compile(r"^([^<]+)<([^>]+)>$", re.IGNORECASE)


def send_mail(recipients, subject, msg_html):
    """Envoi d'un email via SMTP (Flask-Mail) ou Microsoft Graph selon la configuration.

    .. :quickref:  Fonction générique d'envoi d'email.

    Parameters
    ----------
    recipients : str or [str]
        Chaine contenant des emails séparés par des virgules ou liste
        contenant des emails. Un email encadré par des chevrons peut être
        précédé d'un libellé qui sera utilisé lors de l'envoi.

    subject : str
        Sujet de l'email.
    msg_html : str
        Contenu de l'eamil au format HTML.

    Returns
    -------
    void
        L'email est envoyé. Aucun retour.
    """
    cleaned_recipients = clean_recipients(recipients)
    mail_config = current_app.config.get("MAIL_CONFIG", {})
    provider = mail_config.get("PROVIDER", "smtp")

    if provider == "graph":
        _send_mail_via_graph(mail_config, cleaned_recipients, subject, msg_html)
        return

    with MAIL.connect() as conn:
        mail_sender = current_app.config.get("MAIL_DEFAULT_SENDER")
        if not mail_sender:
            mail_sender = current_app.config["MAIL_USERNAME"]
        msg = Message(subject, sender=mail_sender, recipients=cleaned_recipients)
        msg.html = msg_html
        conn.send(msg)


def clean_recipients(recipients):
    """Retourne une liste contenant des emails (str) ou des tuples
    contenant un libelé et l'email correspondant.

    Parameters
    ----------
    recipients : str or [str]
        Chaine contenant des emails séparés par des virgules ou liste
        contenant des emails. Un email encadré par des chevrons peut être
        précédé d'un libellé qui sera utilisé lors de l'envoi.

    Returns
    -------
    [str or tuple]
        Liste contenant des chaines (email) ou des tuples (libellé, email).
    """
    if type(recipients) is list and len(recipients) > 0:
        splited_recipients = recipients
    elif type(recipients) is str and recipients != "":
        splited_recipients = recipients.split(",")
    else:
        raise Exception("Recipients not set")
    trimed_recipients = list(map(str.strip, splited_recipients))
    return list(map(split_name_address, trimed_recipients))


def split_name_address(email):
    """Sépare le libellé de l'email. Le libellé doit précéder l'email qui
    doit être encadré par des chevons. Format : `libellé <email>`. Ex. :
    `Carl von LINNÉ <c.linnaeus@linnaeus.se>`.

    Parameters
    ----------
    email : str
        Chaine contenant un email avec ou sans libellé.

    Returns
    -------
    str or tuple
        L'email simple ou un tuple contenant ("libellé", "email").
    """
    name_address = email
    match = name_address_email_regex.match(email)
    if match:
        name_address = (match.group(1).strip(), match.group(2).strip())
    return name_address


def _send_mail_via_graph(mail_config, recipients, subject, msg_html):
    tenant_id = mail_config.get("GRAPH_TENANT_ID")
    client_id = mail_config.get("GRAPH_CLIENT_ID")
    client_secret = mail_config.get("GRAPH_CLIENT_SECRET")
    scope = mail_config.get("GRAPH_SCOPE", "https://graph.microsoft.com/.default")
    sender = mail_config.get("GRAPH_SENDER")

    token = _get_graph_token(tenant_id, client_id, client_secret, scope)

    url = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "message": {
            "subject": subject,
            "body": {"contentType": "HTML", "content": msg_html},
            "toRecipients": [
                (
                    {"emailAddress": {"address": r[1], "name": r[0]}}
                    if isinstance(r, tuple)
                    else {"emailAddress": {"address": r}}
                )
                for r in recipients
            ],
        },
        "saveToSentItems": True,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=10)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        log.error("Graph mail send failed: %s", exc)
        raise


def _get_graph_token(tenant_id, client_id, client_secret, scope):
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "client_credentials",
        "scope": scope,
    }
    response = requests.post(token_url, data=data, timeout=10)
    response.raise_for_status()
    token_json = response.json()
    if "access_token" not in token_json:
        raise requests.HTTPError("Microsoft Graph token response missing access_token")
    return token_json["access_token"]
