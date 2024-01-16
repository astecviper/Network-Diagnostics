README for Network Diagnostics Tool
-----------------------------------

This document provides instructions on setting up and running the Network Diagnostics Tool.

Requirements:
- Python 3.12 should be installed on your system and added to the system's PATH environment variable.

Initial Setup:
1. Install Python 3.12:
   - Download Python 3.12 from the official website: [https://www.python.org/downloads/](https://www.python.org/ftp/python/3.12.0/python-3.12.0-amd64.exe)
   - During installation, ensure to check the option 'Add Python 3.12 to PATH'.

2. Download and Extract the Network Diagnostics Tool:
   - Download the ZIP file from the GitHub repository or clone it using Git.
   - Extract the files to a folder of your choice (make sure that it is located in a local directory not managed by a cloud service like OneDrive).

Running the Test for the First Time:
1. Open the Command Prompt or Terminal in the folder where you extracted the Network Diagnostics Tool.
2. Run the script by typing `python network_diagnostics.py` and press Enter.
3. The script will install required packages, run initial tests, and create a desktop shortcut named 'Network Diagnostics'.

Setting Up the Desktop Shortcut:
1. Locate the 'Network Diagnostics' shortcut on your desktop.
2. Right-click on the shortcut and select 'Properties'.
3. In the Properties window, go to the 'Shortcut' tab.
4. Click on 'Advanced...' and then check the box for 'Run as administrator'.
5. Click OK and Apply to save these settings.

You're all set! You can now run network diagnostics tests directly from the desktop shortcut with administrative privileges.

Note: Running the tool with administrative privileges ensures more accurate test results and allows certain tests to run correctly.

For any issues or questions, please refer to the GitHub repository's 'Issues' section.

Thank you for using the Network Diagnostics Tool.
