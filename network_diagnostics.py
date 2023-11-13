# --- Package Installation ---
import subprocess
import sys
import os
import json

def install_required_packages():
    packages = ["art", "requests", "speedtest-cli", "plyer", "colorama", "rich", "pyshortcuts", "pywin32"]
    for package in packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        else:
            print(f"Requirement already satisfied: {package}")
install_required_packages()

print("Package installation completed. Running the script...")

# --- Imports ---
from datetime import datetime, timedelta
from art import text2art
import requests
from plyer import notification
import speedtest
import colorama
from colorama import Fore, Style
import time
from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn
import threading
import rich
import art
from pyshortcuts import make_shortcut
from pathlib import Path
   
# --- Initialize colorama ---
colorama.init(autoreset=True)

# --- Clear Screen Function ---
def clear_screen():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')
    display_script_name()
        
# --- Create Shortcut ---
def create_shortcut(shortcut_name):
    try:
        script_path = Path(__file__).resolve()
        icon_path = script_path.parent / "icon.ico"

        # Use the make_shortcut function to create the shortcut on the desktop
        make_shortcut(
            script=str(script_path),
            name=shortcut_name,
            icon=str(icon_path),
            terminal=False,  # Set to True if you want to open a terminal
            desktop=True,  # This will ensure the shortcut is created on the desktop
        )
        print(f"Shortcut '{shortcut_name}' created successfully on the desktop.")

    except Exception as e:
        print(f"Error in shortcut creation process: {e}")

# --- Display Script Name ---
def display_script_name():
    title_color = colorama.Fore.LIGHTYELLOW_EX
    author_color = colorama.Fore.MAGENTA
    print(title_color + text2art("Network Diagnostics"), end='')
    print(author_color + "By AztecViper\n")
    
# --- Progress Function ---
def run_command_with_progress(command, progress_task, progress, update_interval=0.5):
    """
    Runs a command in a separate thread and updates the progress bar periodically.
    :param command: Command to be executed as a list.
    :param progress_task: Task ID for the progress bar.
    :param progress: Progress object from Rich library.
    :param update_interval: Time interval (in seconds) for progress updates.
    """
    def command_thread():
        subprocess.run(command, capture_output=True, text=True)
        progress.update(progress_task, completed=100)  # Mark as completed when command finishes

    # Start the command execution in a separate thread
    thread = threading.Thread(target=command_thread)
    thread.start()

    # Update progress in the main thread until the command thread completes
    while thread.is_alive():
        time.sleep(update_interval)
        progress.advance(progress_task)
    
# --- Network Diagnostics Tests ---
def run_network_tests(settings):
    clear_screen()
    print("Starting network tests...")
    results = {}
    tests = settings.get('test_preferences', {})  # Retrieve enabled tests from settings

    with Progress(
        TextColumn("{task.description}", justify="right"),
        BarColumn(bar_width=20),
        TextColumn("{task.percentage:>3.0f}%"),
        TimeElapsedColumn()
    ) as progress:
        
        # Ping Test
        if tests.get('Ping', 'Disabled') == 'Enabled':
            ping_task = progress.add_task("Running Ping Test...", total=100)
            start_time = time.time()
            run_command_with_progress(["ping", "-n", "4", "8.8.8.8"], ping_task, progress)
            ping_response = subprocess.run(["ping", "-n", "4", "8.8.8.8"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['Ping Test'] = {'result': 'Passed' if ping_response.returncode == 0 else 'Failed',
                                    'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "Ping Test completed.")

        # Traceroute Test
        if tests.get('Traceroute', 'Disabled') == 'Enabled':
            traceroute_task = progress.add_task("Running Traceroute Test...", total=100)
            start_time = time.time()
            run_command_with_progress(["tracert", "8.8.8.8"], traceroute_task, progress)
            traceroute_response = subprocess.run(["tracert", "8.8.8.8"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['Traceroute Test'] = {'result': 'Passed' if traceroute_response.returncode == 0 else 'Failed',
                                          'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "Traceroute Test completed.")

        # IP Configuration Test
        if tests.get('IP Configuration', 'Disabled') == 'Enabled':
            ipconfig_task = progress.add_task("Running IP Configuration Test...", total=100)
            start_time = time.time()
            run_command_with_progress(["ipconfig", "/all"], ipconfig_task, progress)
            ipconfig_response = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['IP Configuration'] = {'result': 'Passed' if ipconfig_response.returncode == 0 else 'Failed',
                                           'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "IP Configuration Test completed.")

        # Current Public IP Test
        if tests.get('Current Public IP', 'Disabled') == 'Enabled':
            current_ip_task = progress.add_task("Retrieving Current Public IP...", total=100)
            start_time = time.time()
            run_command_with_progress(["curl", "https://api.ipify.org"], current_ip_task, progress)
            try:
                public_ip = requests.get('https://api.ipify.org').text
                duration = time.time() - start_time
                results['Current Public IP'] = {'result': 'Completed', 'IP': public_ip,
                                                'duration': str(datetime.timedelta(seconds=duration))}
                print(Fore.GREEN + "Current Public IP Test completed.")
            except Exception as e:
                duration = time.time() - start_time
                results['Current Public IP'] = {'result': 'Failed', 'Error': str(e),
                                                'duration': str(timedelta(seconds=duration))}
                print(Fore.LIGHTRED_EX + "Failed to retrieve Current Public IP.")

        # DNS Flush Test
        if tests.get('DNS Flush', 'Disabled') == 'Enabled':
            dnsflush_task = progress.add_task("Running DNS Flush...", total=100)
            start_time = time.time()
            run_command_with_progress(["ipconfig", "/flushdns"], dnsflush_task, progress)
            dns_flush_response = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['DNS Flush'] = {'result': 'Passed' if dns_flush_response.returncode == 0 else 'Failed',
                                    'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "DNS Flush completed.")

        # Nslookup Test
        if tests.get('Nslookup', 'Disabled') == 'Enabled':
            nslookup_task = progress.add_task("Running Nslookup Test...", total=100)
            start_time = time.time()
            run_command_with_progress(["nslookup", "google.com"], nslookup_task, progress)
            nslookup_response = subprocess.run(["nslookup", "google.com"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['Nslookup Test'] = {'result': 'Passed' if nslookup_response.returncode == 0 else 'Failed',
                                        'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "Nslookup Test completed.")

        # Netstat Test
        if tests.get('Netstat', 'Disabled') == 'Enabled':
            netstat_task = progress.add_task("Running Netstat...", total=100)
            start_time = time.time()
            run_command_with_progress(["netstat"], netstat_task, progress)
            netstat_response = subprocess.run(["netstat"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['Netstat'] = {'result': 'Passed' if netstat_response.returncode == 0 else 'Failed',
                                  'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "Netstat completed.")

       # Speedtest
        if tests.get('Speedtest', 'Disabled') == 'Enabled':
            speedtest_task = progress.add_task("Running Speedtest...", total=100)

            st = speedtest.Speedtest()
            st.get_best_server()
            progress.update(speedtest_task, advance=10, description="Preparing Speedtest...")

            start_time = time.time()  # Start time measurement

            # Perform download test
            st.download(threads=None)
            progress.update(speedtest_task, advance=45, description="Running Speedtest: Download")  # Update after download

            # Perform upload test
            st.upload(threads=None)
            progress.update(speedtest_task, advance=45, description="Running Speedtest: Upload")  # Update after upload

            end_time = time.time()  # End time measurement
            duration = end_time - start_time  # Calculate total duration

            progress.update(speedtest_task, completed=100, description="Speedtest completed")  # Update to full after upload

            speedtest_results = st.results.dict()
            results['Speedtest'] = {
                "result": "Completed",
                "Download": speedtest_results['download'] / (1024 * 1024),  # Convert to Mbps
                "Upload": speedtest_results['upload'] / (1024 * 1024),  # Convert to Mbps
                "Ping": speedtest_results['ping'],
                'duration': str(timedelta(seconds=duration))
            }
            print(Fore.GREEN + "Speedtest completed.")
    if results:
        show_completion_notification(results)
    return results

# --- Display Summary Management ---
def display_summary(results):
    print("\n===== Network Diagnostic Summary =====")
    for test, data in results.items():
        if isinstance(data, dict):
            # For both simple and complex tests
            result = data.get('result', 'N/A')
            duration = data.get('duration', 'N/A')
            print(f"{test}: {result}")
            print(f"Execution Time: {duration}")
            
            # If this is the Speedtest, include additional details
            if test == 'Speedtest' and result == "Completed":
                download_speed = data.get('Download', 'N/A')
                upload_speed = data.get('Upload', 'N/A')
                ping = data.get('Ping', 'N/A')
                print(f"Download Speed: {download_speed:.2f} Mbps")
                print(f"Upload Speed: {upload_speed:.2f} Mbps")
                print(f"Ping: {ping} ms")

        else:
            # Fallback for unexpected formats
            print(f"{test}: {data}")
        print("---------------------------------------")
    print("=========== End of Summary ===========\n")

# --- Post-Test Menu ---
def post_test_menu():
    while True:
        print("\n============ Results Menu ============")
        print("1. Return to Main Menu")
        print("2. Show Results")
        choice = input("Enter your choice: ")
        if choice == '1':
            return True  # Return to Main Menu
        elif choice == '2':
            return False  # Exit the script

# --- Save Results ---
from datetime import datetime  # Import the datetime class from the datetime module

def save_results(results):
    results_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Results')
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)
    file_name = os.path.join(results_folder, f"Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    with open(file_name, 'w') as file:
        for test, data in results.items():
            file.write(f"{test}:\n")
            if isinstance(data, dict):
                for key, value in data.items():
                    file.write(f"  - {key}: {value}\n")
            else:
                file.write(f"  Result: {data}\n")
            file.write("--------------------------------------\n")
        file.write("\n===== End of Results =====\n")
    
    print(f"Results successfully saved.\n")
    
# --- Display Notifications ---
def show_completion_notification(results):
    # Load the notification settings
    settings = load_settings()
    notification_enabled = settings.get('notification_settings', {}).get('enabled', False)

    if notification_enabled:
        message_parts = []
        
        # Handling Speedtest results
        if 'Speedtest' in results:
            speedtest_results = results['Speedtest']
            message_parts.append(f"Speedtest: {speedtest_results['result']}")
            if speedtest_results['result'] == "Completed":
                download_speed = speedtest_results['Download']
                upload_speed = speedtest_results['Upload']
                ping = speedtest_results['Ping']
                message_parts.append(f"Download: {download_speed:.2f} Mbps, Upload: {upload_speed:.2f} Mbps, Ping: {ping} ms")

        # Add similar blocks for other tests if needed

        notification_message = "\n".join(message_parts)

        notification.notify(
            title="Network Diagnostics Completed",
            message=notification_message,
            app_name="Network Diagnostics"
        )

# Note: The `before_download`, `before_upload`, `after_download`, and `after_upload` are placeholders here and should be replaced with actual speed values from the speedtest results.

# --- Settings Management ---
def manage_settings():
    settings = load_settings()
    while True:
        clear_screen()
        print("\n==================== Settings Menu ====================")
        # Options for Test Preferences and Notification Settings
        print("1. Test Preferences")
        print("2. Notification Settings")
        print("3. Back")
        choice = input("Enter your choice: ")
        if choice == '1':
            settings['test_preferences'] = manage_test_preferences(settings.get('test_preferences', {}))
        elif choice == '2':
            settings['notification_settings'] = manage_notification_settings(settings.get('notification_settings', {}))
        elif choice == '3':
            break
    save_settings(settings)

# --- Load Settings ---
def load_settings():
    settings_file = 'settings.json'
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as file:
            return json.load(file)
    return {}

# --- Save Settings ---
def save_settings(settings):
    with open('settings.json', 'w') as file:
        json.dump(settings, file, indent=4)

# --- Test Preferences Management ---
def manage_test_preferences(current_preferences):
    tests = ['Ping', 'Traceroute', 'IP Configuration', 'DNS Flush', 'Nslookup', 'Netstat', 'Speedtest']
    while True:
        clear_screen()
        print("\n==================== Test Preferences ====================")
        for i, test in enumerate(tests, start=1):
            enabled_status = current_preferences.get(test, 'Disabled') == 'Enabled'
            color = colorama.Fore.GREEN if enabled_status else colorama.Fore.RED
            status = 'Enabled' if enabled_status else 'Disabled'
            print(f"{color}{i}. {test} - {status}")
        print("0. Back")

        test_choice = input("Enter test number to toggle or 0 to go back: ")
        if test_choice.isdigit():
            choice = int(test_choice)
            if 0 < choice <= len(tests):
                selected_test = tests[choice - 1]
                current_preferences[selected_test] = 'Enabled' if current_preferences.get(selected_test, 'Disabled') == 'Disabled' else 'Disabled'
            elif choice == 0:
                break

    return current_preferences

def handle_test_preferences_selection(selection, current_preferences):
    # Logic to handle each test preference option
    # This function needs to be implemented
    pass

# --- Notification Settings Management ---
def manage_notification_settings(current_notifications):
    while True:
        clear_screen()
        print("\n==================== Notification Settings ====================")
        enabled_selected = f"{Fore.GREEN}<--{Style.RESET_ALL}" if current_notifications.get('enabled', False) else ""
        disabled_selected = f"{Fore.RED}<--{Style.RESET_ALL}" if not current_notifications.get('enabled', False) else ""

        print(f"1. Enable Notifications{enabled_selected}")
        print(f"2. Disable Notifications{disabled_selected}")
        print("3. Back")

        notification_choice = input("Enter your choice: ")
        if notification_choice == '1':
            current_notifications['enabled'] = True
        elif notification_choice == '2':
            current_notifications['enabled'] = False
        elif notification_choice == '3':
            break

    return current_notifications

# --- Main Menu Logic ---
def main_menu():
    global global_settings
    while True:
        clear_screen()
        print("\n==================== Main Menu ====================")
        print("1. Run Now")
        print("2. Settings")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            settings = load_settings()  # Load current settings
            print("Please wait, running tests...")
            results = run_network_tests(settings)
            # Tests are done, now show the results menu
            continue_to_main = post_test_menu()  # Show post-test menu and capture user's choice
            
            if continue_to_main:
                # The user wants to go back to the main menu
                # No need to clear the screen here, as it will be cleared at the beginning of the loop
                continue
            
            # If the user chooses to exit, we show the summary and wait for input before closing
            clear_screen()  # Clear the screen before showing the summary
            # The script title is assumed to be displayed automatically, so it's not included here
            display_summary(results)  # Display the test summary
            save_results(results)  # Save the test results
            if 'Speedtest' in results:
                show_completion_notification(results['Speedtest'])  # Show speed test notification if available
            input("\nPress Enter to return to the main menu...")  # Wait for user input before returning to the main menu or exiting

        elif choice == '2':
            manage_settings()
        elif choice == '3':
            # Clear screen and show title is handled externally, so just break
            break

# --- Global Variable for Settings ---
global_settings = {}

# --- Main Function ---
def main():
    create_shortcut("Network Diagnostics")
    global global_settings
    global_settings = load_settings()
    display_script_name()
    main_menu()

if __name__ == '__main__':
    main()

