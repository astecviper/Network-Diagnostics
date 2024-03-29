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
   
# --- Logging Setup ---
import logging
from pathlib import Path
from datetime import datetime

# Disable logging
logging.disable(logging.CRITICAL)

# Get the directory of the current script
script_directory = Path(__file__).parent

# Create a Logs directory in the same directory as the script if not exists
logs_directory = script_directory / 'Logs'
if not logs_directory.exists():
    logs_directory.mkdir()

# Get current date and time for the log file name
current_time = datetime.now()
log_filename = current_time.strftime("log-%m-%d-%Y-%H-%M.txt")  # Replaced ':' with '-'

# Full path for the log file
full_log_path = logs_directory / log_filename

# Check if logging is enabled for the DEBUG level
if logging.getLogger().isEnabledFor(logging.DEBUG):
    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.FileHandler(full_log_path, mode='a')  # Corrected to use the full_log_path variable
        ]
    )

# --- Initialize colorama ---
colorama.init(autoreset=True)

# --- Clear Screen Function ---
def clear_screen():
    logging.debug("Clearing the screen")
    try:
        if os.name == 'nt':
            _ = os.system('cls')
        else:
            _ = os.system('clear')
    except Exception as e:
        logging.error(f"Error clearing screen: {e}")
    finally:
        display_script_name()
        
# --- Create Shortcut ---
def create_shortcut(shortcut_name):
    logging.info(f"Creating shortcut: {shortcut_name}")
    try:
        script_path = Path(__file__).resolve()
        icon_path = script_path.parent / "icon.ico"

        make_shortcut(
            script=str(script_path),
            name=shortcut_name,
            icon=str(icon_path),
            terminal=False,  
            desktop=True,  
        )
        logging.info(f"Shortcut '{shortcut_name}' created successfully on the desktop.")
    except Exception as e:
        logging.error(f"Error in shortcut creation process: {e}")

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
        try:
            response = subprocess.run(command, capture_output=True, text=True)
            if response.returncode != 0:
                logging.warning(f"Command '{' '.join(command)}' returned a non-zero exit status: {response.returncode}")
            else:
                logging.debug(f"Command executed successfully: {' '.join(command)}")
            progress.update(progress_task, completed=100)  # Mark as completed when command finishes
        except Exception as e:
            logging.error(f"Error occurred while executing command: {' '.join(command)}. Error: {e}")
            progress.update(progress_task, completed=100)  # Mark as completed even if there's an error

    # Start the command execution in a separate thread
    thread = threading.Thread(target=command_thread)
    thread.start()

    # Update progress in the main thread until the command thread completes
    logging.info(f"Starting command: {' '.join(command)}")
    while thread.is_alive():
        time.sleep(update_interval)
        progress.advance(progress_task)

    logging.info(f"Command completed: {' '.join(command)}")
    
# --- Network Diagnostics Tests ---
def run_network_tests(settings):
    logging.info("Starting network diagnostics tests")
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
            logging.debug("Ping test enabled, starting test")
            ping_task = progress.add_task("Running Ping Test...", total=100)
            start_time = time.time()
            run_command_with_progress(["ping", "-n", "4", "8.8.8.8"], ping_task, progress)
            ping_response = subprocess.run(["ping", "-n", "4", "8.8.8.8"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['Ping Test'] = {'result': 'Passed' if ping_response.returncode == 0 else 'Failed',
                                    'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "Ping Test completed.")
            if ping_response.returncode == 0:
                logging.info("Ping Test completed successfully")
            else:
                logging.error("Ping Test failed")

        # Traceroute Test
        if tests.get('Traceroute', 'Disabled') == 'Enabled':
            logging.debug("Traceroute test enabled, starting test")
            traceroute_task = progress.add_task("Running Traceroute Test...", total=100)
            start_time = time.time()
            run_command_with_progress(["tracert", "8.8.8.8"], traceroute_task, progress)
            traceroute_response = subprocess.run(["tracert", "8.8.8.8"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['Traceroute Test'] = {'result': 'Passed' if traceroute_response.returncode == 0 else 'Failed',
                                          'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "Traceroute Test completed.")
            if traceroute_response.returncode == 0:
                logging.info("Traceroute Test completed successfully")
            else:
                logging.error("Traceroute Test failed")
    
        # IP Configuration Test
        if tests.get('IP Configuration', 'Disabled') == 'Enabled':
            logging.debug("IP Configuration test enabled, starting test")
            ipconfig_task = progress.add_task("Running IP Configuration Test...", total=100)
            start_time = time.time()
            run_command_with_progress(["ipconfig", "/all"], ipconfig_task, progress)
            ipconfig_response = subprocess.run(["ipconfig", "/all"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['IP Configuration'] = {'result': 'Passed' if ipconfig_response.returncode == 0 else 'Failed',
                                           'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "IP Configuration Test completed.")
            if ipconfig_response.returncode == 0:
                logging.info("IP Configuration Test completed successfully")
            else:
                logging.error("IP Configuration Test failed")

        # Current Public IP Test
        if tests.get('Current Public IP', 'Disabled') == 'Enabled':
            logging.debug("Current Public IP test enabled, starting test")
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
            if 'IP' in results['Current Public IP']:
                logging.info("Current Public IP Test completed successfully")
            else:
                logging.error("Current Public IP Test failed")

        # DNS Flush Test
        if tests.get('DNS Flush', 'Disabled') == 'Enabled':
            logging.debug("DNS Flush test enabled, starting test")
            dnsflush_task = progress.add_task("Running DNS Flush...", total=100)
            start_time = time.time()
            run_command_with_progress(["ipconfig", "/flushdns"], dnsflush_task, progress)
            dns_flush_response = subprocess.run(["ipconfig", "/flushdns"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['DNS Flush'] = {'result': 'Passed' if dns_flush_response.returncode == 0 else 'Failed',
                                    'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "DNS Flush completed.")
            if dns_flush_response.returncode == 0:
                logging.info("DNS Flush completed successfully")
            else:
                logging.error("DNS Flush failed")

        # Nslookup Test
        if tests.get('Nslookup', 'Disabled') == 'Enabled':
            logging.debug("Nslookup test enabled, starting test")
            nslookup_task = progress.add_task("Running Nslookup Test...", total=100)
            start_time = time.time()
            run_command_with_progress(["nslookup", "google.com"], nslookup_task, progress)
            nslookup_response = subprocess.run(["nslookup", "google.com"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['Nslookup Test'] = {'result': 'Passed' if nslookup_response.returncode == 0 else 'Failed',
                                        'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "Nslookup Test completed.")
            if nslookup_response.returncode == 0:
                logging.info("Nslookup Test completed successfully")
            else:
                logging.error("Nslookup Test failed")

        # Netstat Test
        if tests.get('Netstat', 'Disabled') == 'Enabled':
            logging.debug("Netstat test enabled, starting test")
            netstat_task = progress.add_task("Running Netstat...", total=100)
            start_time = time.time()
            run_command_with_progress(["netstat"], netstat_task, progress)
            netstat_response = subprocess.run(["netstat"], capture_output=True, text=True)
            duration = time.time() - start_time
            results['Netstat'] = {'result': 'Passed' if netstat_response.returncode == 0 else 'Failed',
                                  'duration': str(timedelta(seconds=duration))}
            print(Fore.GREEN + "Netstat completed.")
            if netstat_response.returncode == 0:
                logging.info("Netstat completed successfully")
            else:
                logging.error("Netstat failed")

       # Speedtest
        if tests.get('Speedtest', 'Disabled') == 'Enabled':
            logging.debug("Speedtest enabled, starting test")
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
            if 'result' in results['Speedtest'] and results['Speedtest']['result'] == "Completed":
                logging.info("Speedtest completed successfully")
            else:
                logging.error("Speedtest failed")

    if results:
        show_completion_notification(results)
    logging.info("Network diagnostics tests completed")
    return results

# --- Display Summary Management ---
def display_summary(results):
    logging.info("Displaying network diagnostic summary")
    print("\n===== Network Diagnostic Summary =====")
    for index, (test, data) in enumerate(results.items()):
        if isinstance(data, dict):
            # For both simple and complex tests
            result = data.get('result', 'N/A')
            duration = data.get('duration', 'N/A')
            print(f"\n{test}:\n")
            print(f"  Result: {result}\n")
            print(f"  Execution Time: {duration}\n")

            # If this is the Speedtest, include additional details
            if test == 'Speedtest' and result == "Completed":
                download_speed = data.get('Download', 'N/A')
                upload_speed = data.get('Upload', 'N/A')
                ping = data.get('Ping', 'N/A')
                print(f"  Download Speed: {download_speed:.2f} Mbps")
                print(f"  Upload Speed: {upload_speed:.2f} Mbps")
                print(f"  Ping: {ping} ms")

            # Print a divider after each test summary except the last one
            if index < len(results) - 1:
                print("--------------------------------------\n")
        else:
            # Fallback for unexpected formats
            print(f"{test}: {data}")
            if index < len(results) - 1:
                print("--------------------------------------\n")
                
    print("=========== End of Summary ===========\n")
    logging.debug("Network diagnostic summary displayed")

# --- Post-Test Menu ---
def post_test_menu(results):
    logging.info("Displaying post-test menu")
    while True:
        clear_screen()
        print("\n============== Summary ===============")  # Header for the summary
        for index, (test, data) in enumerate(results.items()):
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

                # Print a divider after each test summary except the last one
                if index < len(results) - 1:
                    print("--------------------------------------")
            else:
                # Fallback for unexpected formats
                print(f"{test}: {data}")
                if index < len(results) - 1:
                    print("--------------------------------------")

        # Ensure no newline is printed before the menu header
        print("============ Summary Menu ============")  # Header for the menu
        print("1. Return to Main Menu")
        print("0. Exit")
        choice = input("Enter your choice: ")
        try:
            choice = int(choice)
        except ValueError:
            logging.debug("Invalid input, clearing screen and redisplaying menu")
            continue

        if choice == 1:
            return True  # Return to Main Menu
        elif choice == 0:
            logging.info("Exiting script")
            sys.exit(0)  # Exit the script
        else:
            logging.debug("Invalid input, clearing screen and redisplaying menu")

# --- Post-Summary Menu ---
def post_summary_menu(results):
    logging.info("Displaying post-summary menu")
    while True:
        clear_screen()
        print("\n============ Post-Summary Menu ============")
        print("1. Return to Main Menu")
        print("0. Exit")  # Added an option to exit the script
        choice = input("Enter your choice: ")
        try:
            choice = int(choice)
        except ValueError:
            logging.debug("Invalid input, clearing screen and redisplaying menu")
            continue

        if choice == 1:
            return True  # Return to Main Menu
        elif choice == 0:
            logging.info("Exiting script")
            sys.exit(0)  # Exit the script
        else:
            logging.debug("Invalid input, clearing screen and redisplaying menu")

# --- Save Results ---
def save_results(results, settings):
    save_enabled = settings.get('save_summaries', {}).get('enabled', False)  # Adjust the key as per your settings structure
    logging_enabled = settings.get('logging_settings', {}).get('enabled', True)  # Adjust the key as per your settings structure

    if save_enabled and logging_enabled:
        logging.info("Saving network diagnostic results")
        results_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Results')
        if not os.path.exists(results_folder):
            os.makedirs(results_folder)
        file_name = os.path.join(results_folder, f"Results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        try:
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
            print(f"Results successfully saved at {file_name}\n")
            logging.info("Results saved successfully")
        except Exception as e:
            logging.error(f"Error saving results: {e}")
    elif not logging_enabled:
        logging.info("Logging is disabled, not saving results.")
    else:
        logging.info("Saving results is disabled in settings.")
    
# --- Display Notifications ---
def show_completion_notification(results):
    logging.info("Preparing to display completion notification")
    try:
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

        logging.info("Notification displayed successfully")

    except Exception as e:
        logging.error(f"Error displaying notification: {e}")

# Note: The `before_download`, `before_upload`, `after_download`, and `after_upload` are placeholders here and should be replaced with actual speed values from the speedtest results.

# --- Settings Management ---
def manage_settings():
    logging.info("Entering settings management")
    try:
        settings = load_settings()
        while True:
            clear_screen()
            print("\n==================== Settings Menu ====================")
            print("1. Test Preferences")
            print("2. Notification Settings")
            print("3. Save Summaries")
            print("4. Logging Settings")  # Add this line
            print("0. Back")
            choice = input("Enter your choice: ")
            if choice == '1':
                settings['test_preferences'] = manage_test_preferences(settings.get('test_preferences', {}))
            elif choice == '2':
                settings['notification_settings'] = manage_notification_settings(settings.get('notification_settings', {}))
            elif choice == '3':
                settings['save_summaries'] = manage_save_summaries_settings(settings.get('save_summaries', {}))
            elif choice == '4':  # Add this line
                settings['logging_settings'] = manage_logging_settings(settings.get('logging_settings', {}))
            elif choice == '0':
                break
        save_settings(settings)
        logging.info("Settings management completed successfully")
    except Exception as e:
        logging.error(f"Error in settings management: {e}")
# --- Load Settings ---
def load_settings():
    logging.info("Loading settings")
    try:
        settings_file = 'settings.json'
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as file:
                logging.info("Settings loaded successfully")
                return json.load(file)
        return {}
    except Exception as e:
        logging.error(f"Error loading settings: {e}")
        return {}

# --- Save Settings ---
def save_settings(settings):
    logging.info("Saving settings")
    try:
        with open('settings.json', 'w') as file:
            json.dump(settings, file, indent=4)
        logging.info("Settings saved successfully")
    except Exception as e:
        logging.error(f"Error saving settings: {e}")

# --- Test Preferences Management ---
def manage_test_preferences(current_preferences):
    logging.info("Managing test preferences")
    try:
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

        logging.info("Test preferences updated")
        return current_preferences
    except Exception as e:
        logging.error(f"Error managing test preferences: {e}")
        return current_preferences

# --- Logging Settings Management ---
def manage_logging_settings(current_logging):
    logging.info("Managing logging settings")
    try:
        while True:
            clear_screen()
            print("\n==================== Logging Settings ====================")
            enabled_selected = f"{Fore.GREEN}<--{Style.RESET_ALL}" if current_logging.get('enabled', False) else ""
            disabled_selected = f"{Fore.RED}<--{Style.RESET_ALL}" if not current_logging.get('enabled', False) else ""

            print(f"1. Enable Logging{enabled_selected}")
            print(f"2. Disable Logging{disabled_selected}")
            print("0. Back")

            logging_choice = input("Enter your choice: ")
            if logging_choice == '1':
                current_logging['enabled'] = True
            elif logging_choice == '2':
                current_logging['enabled'] = False
            elif logging_choice == '0':
                break

        logging.info("Logging settings updated")
        save_settings(current_logging)  # Save the updated logging settings
        return current_logging
    except Exception as e:
        logging.error(f"Error managing logging settings: {e}")
        return current_logging
    
# --- Notification Settings Management ---
def manage_notification_settings(current_notifications):
    logging.info("Managing notification settings")
    try:
        while True:
            clear_screen()
            print("\n==================== Notification Settings ====================")
            enabled_selected = f"{Fore.GREEN}<--{Style.RESET_ALL}" if current_notifications.get('enabled', False) else ""
            disabled_selected = f"{Fore.RED}<--{Style.RESET_ALL}" if not current_notifications.get('enabled', False) else ""

            print(f"1. Enable Notifications{enabled_selected}")
            print(f"2. Disable Notifications{disabled_selected}")
            print("0. Back")

            notification_choice = input("Enter your choice: ")
            if notification_choice == '1':
                current_notifications['enabled'] = True
            elif notification_choice == '2':
                current_notifications['enabled'] = False
            elif notification_choice == '0':
                break

        logging.info("Notification settings updated")
        return current_notifications
    except Exception as e:
        logging.error(f"Error managing notification settings: {e}")
        return current_notifications

# --- Save Summaries Management ---
def manage_save_summaries_settings(current_settings):
    logging.info("Managing save summaries settings")
    try:
        while True:
            clear_screen()
            print("\n==================== Save Summaries Settings ====================")
            enabled_selected = f"{Fore.GREEN}<--{Style.RESET_ALL}" if current_settings.get('enabled', False) else ""
            disabled_selected = f"{Fore.RED}<--{Style.RESET_ALL}" if not current_settings.get('enabled', False) else ""

            print(f"1. Enable Save Summaries{enabled_selected}")
            print(f"2. Disable Save Summaries{disabled_selected}")
            print("0. Back")

            choice = input("Enter your choice: ")
            if choice == '1':
                current_settings['enabled'] = True
            elif choice == '2':
                current_settings['enabled'] = False
            elif choice == '0':
                break

        logging.info("Save summaries settings updated")
        return current_settings
    except Exception as e:
        logging.error(f"Error managing save summaries settings: {e}")
        return current_settings
    
# --- Main Menu Logic ---
def main_menu():
    print("main_menu called") # Added this line
    global global_settings
    while True:
        logging.info("Displaying main menu")
        try:
            clear_screen()
            print("\n==================== Main Menu ====================")
            print("1. Run Now")
            print("2. Settings")
            print("0. Exit")
            choice = input("Enter your choice: ")

            if choice == '1':
                logging.info("Running network tests chosen")
                print("Please wait, running tests...")
                results = run_network_tests(global_settings)

                display_summary(results)  # Always display the summary
                save_results(results, global_settings)  # Save results based on settings

                continue_to_main = post_test_menu(results)  # Show post-test menu and capture user's choice

                if continue_to_main:
                    continue  # The user wants to go back to the main menu

                clear_screen()
                input("\nPress Enter to return to the main menu...")  # Wait for user input

            elif choice == '2':
                logging.info("Accessing settings")
                manage_settings()
                global_settings = load_settings()  # Reload settings after managing them
            elif choice == '0':
                logging.info("Exiting main menu")
                break
        except Exception as e:
            logging.error(f"Error in main menu: {e}")

# --- Global Variable for Settings ---
global_settings = {
    'test_preferences': {},
    'notification_settings': {'enabled': False},
    'save_summaries': {'enabled': False},
    'logging_settings': {'enabled': True}
}

# --- Main Function ---
def main(setup=False):
    logging.info("Starting main function")
    if setup:
        create_shortcut("Network Diagnostics")
        install_required_packages()  # Pass setup argument here
    else:
        display_script_name()
        global_settings = load_settings()

        # Configure logging based on settings
        logging_settings = global_settings.get('logging_settings', {})
        logging_enabled = logging_settings.get('enabled', True)
        if logging_enabled:
            logs_directory = Path(__file__).parent / 'Logs'
            if not logs_directory.exists():
                logs_directory.mkdir()

            current_time = datetime.now()
            log_filename = current_time.strftime("log-%m-%d-%Y-%H-%M.txt")  # Replaced ':' with '-'
            full_log_path = logs_directory / log_filename

            logging.basicConfig(
                level=logging.DEBUG,
                format="%(asctime)s %(levelname)s %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                handlers=[
                    logging.FileHandler(full_log_path, mode='a')
                ]
            )
        else:
            logging.basicConfig(level=logging.CRITICAL)  # Disable logging when it's disabled in settings

        main_menu()
    logging.info("Exiting script")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        main(setup=True)
    else:
        global_settings = load_settings()
        display_script_name()
        main()
