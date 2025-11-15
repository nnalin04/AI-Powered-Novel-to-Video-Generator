# AI-Powered Novel-to-Video Generator

## Setup Instructions

1.  Install Python 3.10 or higher.
2.  Create a virtual environment: `python3 -m venv venv`
3.  Activate the virtual environment:
    *   macOS/Linux: `source venv/bin/activate`
    *   Windows: `venv\Scripts\activate`
4.  Install the required packages: `pip install -r requirements.txt`
5.  Create a `.env` file and add your API keys:

    ```
    GOOGLE_API_KEY="your_gemini_api_key"
    YOUTUBE_CLIENT_SECRET="your_youtube_secret.json"
    ```
6.  Run the Flask web server: `python app.py`

## Firewall Instructions

If you are having trouble accessing the Flask web server, you may need to check your firewall settings.

### macOS

1.  Go to System Preferences > Security & Privacy > Firewall.
2.  Click the lock icon to make changes.
3.  If the firewall is enabled, click Firewall Options.
4.  Click the "+" button to add an exception for Python.
5.  Select the Python executable in your virtual environment (e.g., `ai_novel_to_video/venv/bin/python`).
6.  Ensure that "Allow incoming connections" is selected.

### Linux

The instructions for Linux will vary depending on the distribution and firewall software being used. Some common firewall tools include `ufw` and `firewalld`.

#### ufw

1.  Check the status of ufw: `sudo ufw status`
2.  If ufw is enabled, allow access to port 5000: `sudo ufw allow 5000`

#### firewalld

1.  Check the status of firewalld: `sudo firewall-cmd --state`
2.  If firewalld is enabled, allow access to port 5000: `sudo firewall-cmd --zone=public --add-port=5000/tcp --permanent`
3.  Reload firewalld: `sudo firewall-cmd --reload`

### Windows

1.  Open "Windows Defender Firewall with Advanced Security".
2.  In the left pane, click "Inbound Rules".
3.  In the right pane, click "New Rule...".
4.  Select "Port" and click "Next".
5.  Select "TCP" and enter "5000" in the "Specific local ports" field. Click "Next".
6.  Select "Allow the connection" and click "Next".
7.  Select the network types that apply (e.g., "Domain", "Private", "Public") and click "Next".
8.  Enter a name for the rule (e.g., "Allow Flask Port 5000") and click "Finish".