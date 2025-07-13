import os
import ssl
import smtplib
import requests
from email.message import EmailMessage

# ── 环境变量 ──────────────────────────────────────────
IDS  = [v.strip() for v in os.environ["VAULT_IDS"].split(",")]
TH   = float(os.getenv("APY_TH", "0.99"))           # 默认 8 %
USER = os.environ["EMAIL_USER"]                    # Gmail 地址
PWD  = os.environ["EMAIL_PASS"]                    # 16 位 App Password
TO   = [m.strip() for m in os.environ["EMAIL_TO"].split(",")]

# ── 拉取 APY ─────────────────────────────────────────
def fetch_apys() -> dict[str, float]:
    """
    调用 https://api.beefy.finance/apy
    返回 {vault_id: apy_decimal}
    """
    return requests.get("https://api.beefy.finance/apy", timeout=20).json()

# ── 发送邮件 ─────────────────────────────────────────
def send_mail(rows: list[tuple[str, float]]) -> None:
    body = "\n".join(f"{vid}: {apy*100:.2f} %" for vid, apy in rows)
    msg  = EmailMessage()
    msg["Subject"] = "⚠ Beefy APY Alert"
    msg["From"], msg["To"] = USER, ", ".join(TO)
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465,
                          context=ssl.create_default_context()) as smtp:
        smtp.login(USER, PWD)
        smtp.send_message(msg)

# ── 主流程 ───────────────────────────────────────────
if __name__ == "__main__":
    apys = fetch_apys()
    lows = [(vid, apys.get(vid, 0.0)) for vid in IDS if apys.get(vid, 0.0) < TH]
    if lows:                       # 只有低于阈值才发警报
        send_mail(lows)
