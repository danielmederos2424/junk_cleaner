import imaplib
import email
import logging
import schedule
import time
from email.header import decode_header
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

# Your credentials
EMAIL = 'user@gmail.com' # Replace with your email
PASSWORD = 'your_password'  # Use App Password if 2FA is enabled
IMAP_SERVER = 'imap.gmail.com'

# Whitelisted senders (domains or exact addresses)
WHITELIST = [
    'uber.com',
    'mercadolibre.com',
    'mercadopago.com',
    'no-reply@accounts.google.com',
    'notifications@github.com',
    # Add more trusted sources here
]

# Keywords to search for (case-insensitive substrings)
KEYWORDS = [
    'wickeddeathh', 'lawsuit', 'payment failed', 'icloud', 'romantic', 'love', 'bank', 'money',
    'investment', 'loan', 'credit', 'debt', 'inheritance', 'lottery', 'prize', 'reward',
    'whatsapp', 'telegram', 'gift card', 'bitcoin', 'crypto', 'nigerian prince', '419 scam',
    'advance fee fraud', 'private', 'confidential', 'urgent', 'immediate action required',
    'limited time offer', 'act now', 'risk-free', 'guaranteed', 'no strings attached',
    'once in a lifetime', 'exclusive deal', 'free gift', 'free trial', 'click here', 'subscribe now',
    'buy now', 'order now', 'limited supply', 'while supplies last', 'order confirmation',
    'shipping confirmation', 'account verification', 'password reset', 'security alert',
    'urgent message', 'important information regarding your account', 'update your account',
    'verify your account', 'suspicious activity on your account', 'your invoice is ready',
    'payment confirmation', 'receipt for your payment', 'thank you for your order',
    'your order has been shipped', 'your order has been delivered', 'flirt', 'dating', 'romance',
    'relationship', 'affection', 'passion', 'intimacy', 'attraction', 'chemistry', 'connection',
    'partner', 'soulmate', 'companion', 'date', 'flirtation', 'courtship', 'romantic interest',
    'love letter', 'love note', 'free', 'congrats', 'winner', 'claim your prize', 'you are a winner',
    'you have won', 'congratulations', 'prize winner', 'sweepstakes', 'lottery winner', 'jackpot',
    'cash prize', 'gift card winner', 'reward program', 'loyalty program', 'bonus offer',
    'exclusive offer', 'special promotion', 'discount offer', 'free trial offer', 'payment', 'order', 'ship', 'Your order has shipped'
]

# Logging setup
logging.basicConfig(
    filename='junk_cleaner.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)


def is_whitelisted(sender_email: str) -> bool:
    sender_email = sender_email.lower()
    return any(domain in sender_email for domain in WHITELIST)


def decode_str(s) -> str:
    """Decode any header value to a string, safely handling unknown encodings."""
    try:
        # If it's not a string (e.g. Header object), convert first
        if not isinstance(s, str):
            s = str(s)
        decoded_parts = decode_header(s)
        out = []
        for part, enc in decoded_parts:
            if isinstance(part, bytes):
                charset = enc or 'utf-8'
                if charset.lower() in ('unknown-8bit', 'x-unknown'):
                    charset = 'utf-8'
                try:
                    out.append(part.decode(charset, errors='replace'))
                except Exception:
                    out.append(part.decode('utf-8', errors='replace'))
            else:
                out.append(part)
        return ''.join(out)
    except Exception as e:
        logging.error(f"Decode error: {e}")
        return str(s)


def is_unwanted(msg: email.message.Message) -> bool:
    try:
        subject = decode_str(msg['subject']) if msg['subject'] else ''
        sender = decode_str(msg['from']) if msg['from'] else ''

        # 1) Skip any whitelisted senders
        if is_whitelisted(sender):
            return False

        # 2) Delete if no subject
        if not subject.strip():
            return True

        # 3) Gather plaintext body
        payload = ''
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == 'text/plain' and not part.get('Content-Disposition'):
                    try:
                        raw = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        if charset.lower() in ('unknown-8bit', 'x-unknown'):
                            charset = 'utf-8'
                        payload += raw.decode(charset, errors='replace')
                    except Exception as e:
                        logging.error(f"Failed to decode body part: {e}")
        else:
            try:
                raw = msg.get_payload(decode=True)
                charset = msg.get_content_charset() or 'utf-8'
                if charset.lower() in ('unknown-8bit', 'x-unknown'):
                    charset = 'utf-8'
                payload = raw.decode(charset, errors='replace')
            except Exception as e:
                logging.error(f"Failed to decode singlepart body: {e}")

        # 4) Case‐insensitive substring matching
        full_text = (subject + ' ' + sender + ' ' + payload).lower()
        for kw in KEYWORDS:
            if kw in full_text:
                logging.info(f"Match found ({kw}): {subject}")
                return True

        return False

    except Exception as e:
        logging.error(f"Unexpected error in is_unwanted: {e}")
        return False


def clean_junk():
    try:
        logging.info("Starting email cleaning operation...")
        print(Fore.CYAN + "Connecting to Gmail IMAP server…")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL, PASSWORD)
        mail.select('"[Gmail]/Spam"')

        result, data = mail.search(None, 'ALL')
        mail_ids = data[0].split()
        print(Fore.YELLOW + f"Found {len(mail_ids)} emails in Spam folder.")

        deleted_count = 0
        for mail_id in mail_ids:
            try:
                _, msg_data = mail.fetch(mail_id, '(RFC822)')
                msg = email.message_from_bytes(msg_data[0][1])

                if is_unwanted(msg):
                    subj = decode_str(msg['subject']) or '(no subject)'
                    print(Fore.RED + f"🗑️ Deleting: {subj}")
                    logging.info(f"Deleted: {subj}")
                    mail.store(mail_id, '+FLAGS', '\\Deleted')
                    deleted_count += 1
                else:
                    print(Fore.GREEN + f"✓ Safe: {decode_str(msg['subject']) or '(no subject)'}")
            except Exception as e:
                logging.error(f"Error processing email ID {mail_id}: {e}")

        mail.expunge()
        mail.logout()
        print(Fore.CYAN + f"\n✅ Done. {deleted_count} emails deleted.")
        logging.info(f"Cleaning operation completed. {deleted_count} emails deleted.")
    except imaplib.IMAP4.error as e:
        logging.error(f"IMAP error: {e}")
        print(Fore.RED + f"IMAP error: {e}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(Fore.RED + f"Unexpected error: {e}")


# Schedule the cleaning to run once per hour
schedule.every(1).hour.do(clean_junk)

# Run the script immediately on first run and then schedule the periodic task
logging.info("First run of the email cleaning script.")
clean_junk()

while True:
    schedule.run_pending()
    time.sleep(1)
