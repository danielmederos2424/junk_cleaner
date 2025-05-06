# Gmail Junk Cleaner

This script automatically connects to a Gmail IMAP account, searches for unwanted emails, and deletes them from the Spam folder. The criteria for unwanted emails include specific keywords and the sender’s email address. The script is designed to run periodically, checking for junk emails every hour.

## Features

* Connects to Gmail IMAP server using credentials.
* Deletes emails from the Spam folder based on predefined keywords and sender whitelist.
* Uses `schedule` to run the script every hour.
* Logs actions to a file (`junk_cleaner.log`).

## Prerequisites

* Python 3.x
* Gmail account with IMAP enabled.
* App password if two-factor authentication (2FA) is enabled for Gmail.

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/danielmederos2424/junk_cleaner.git
   cd junk_cleaner
   ```

2. Install the required dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Configure the script with your Gmail credentials:

   * Open the script and set your Gmail username and app password in the script.

   ```python
   EMAIL = 'your-email@gmail.com'
   PASSWORD = 'your-app-password'  # App password if 2FA is enabled
   ```

4. Run the script manually or schedule it using `schedule` to run every hour.

   ```bash
   python junk_cleaner.py
   ```

## Running the Script in the Background

To keep the script running in the background on your Linux VPS, you have several options:

### Option 1: Using `screen` or `tmux`

You can use `screen` or `tmux` to run the script in the background.

1. Start a new `screen` session:

   ```bash
   screen -S junk_cleaner
   ```

2. Run your script inside the screen session:

   ```bash
   python junk_cleaner.py
   ```

3. Detach from the screen session (without stopping the script):

   Press `Ctrl + A` then `D`.

4. Reattach to the session later:

   ```bash
   screen -r junk_cleaner
   ```

### Option 2: Using `nohup`

You can run the script with `nohup` so it continues running even if you disconnect from your VPS.

```bash
nohup python junk_cleaner.py &
```

This will run the script in the background and store any output in a file called `nohup.out`.

### Option 3: Using `cron`

To run the script periodically using `cron`, follow these steps:

1. Open your crontab configuration:

   ```bash
   crontab -e
   ```

2. Add the following line to run your script every hour:

   ```bash
   0 * * * * /usr/bin/python3 /path/to/your/script/junk_cleaner.py >> /path/to/your/logs/junk_cleaner.log 2>&1
   ```

   This will execute the script every hour and log the output to `junk_cleaner.log`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---