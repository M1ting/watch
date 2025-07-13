import os, ssl, smtplib, requests
from email.message import EmailMessage

IDS   = [v.strip() for v in os.environ["VAULT_IDS"].split(",")]
TH    = float(os.environ["APY_TH"])
USER  = os.environ["EMAIL_USER"]
PWD   = os.environ["EMAIL_PASS"]
TO    = [m.strip() for m in os.environ["EMAIL_TO"].split(",")]

def fetch_apys():
    return requests.get("https://api.beefy.finance/apy", timeout=20).json()

def send_mail(rows):
    body = "\n".join(f"{vid}: {apy*100:.2f} %" for vid, apy in rows)
    msg = EmailMessage()
    msg["Subject"], msg["From"], msg["To"] = "⚠ Beefy APY Alert", USER, ", ".join(TO)
    msg.set_content(body)
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=ssl.create_default_context()) as s:
        s.login(USER, PWD)
        s.send_message(msg)

if __name__ == "__main__":
    apys = fetch_apys()
    lows = [(vid, apys.get(vid, 0)) for vid in IDS if apys.get(vid, 0) < TH]
    if lows:
        send_mail(lows)
