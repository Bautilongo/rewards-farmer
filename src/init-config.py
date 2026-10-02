from pathlib import Path
import sys
from typing import TextIO

def one_of_with_default(prompt: str, options: list[str], default: str) -> str:
	while True:
		user_input = input(f"{prompt} ({'/'.join(options)}) [Default: {default}]: ").strip() or default

		if user_input in options:
			return user_input
		else:
			print(f"Invalid choice.")

def positive_integer_with_default(prompt: str, default: int) -> int:
	while True:
		user_input = input(f"{prompt} [Default: {default}]: ").strip() or str(default)

		try:
			value = int(user_input)
			if value > 0:
				return value
			else:
				print("Please enter a positive integer.")
		except ValueError:
			print("Invalid input. Please enter a positive integer.")

def boolean_with_default(prompt: str, default: bool) -> bool:
	while True:
		default_str = "yes" if default else "no"
		user_input = input(f"{prompt} (yes/no) [Default: {default_str}]: ").strip().lower() or default_str

		if user_input in ("yes", "y"):
			return True
		elif user_input in ("no", "n"):
			return False
		else:
			print("Invalid input. Please enter 'yes' or 'no'.")

def nonempty_input(prompt: str) -> str:
	while True:
		user_input = input(prompt).strip()
		if user_input:
			return user_input
		else:
			print("Input cannot be empty. Please try again.")

def configure_variables(f: TextIO):
	search_backend = one_of_with_default("Which search backend would you like to use?", ["trends", "llm"], "trends")

	if search_backend == "trends":
		f.write("SEARCH_BACKEND=trends\n")

	else:
		f.write("SEARCH_BACKEND=llm\n")

		llm_setup_type = one_of_with_default("Which LLM setup would you like to use? (Select 'local' for custom endpoints)", ["openrouter", "local"], "openrouter")

		if llm_setup_type == "openrouter":
			f.write("LLM_PROVIDER=openrouter\n")
			llm_api_key = input("Enter your OpenRouter API key: ").strip()
			llm_model = input("Enter the model name (default: openrouter/free): ").strip() or "openrouter/free"

			f.write(f"OPENROUTER_API_KEY={llm_api_key}\n")
			f.write(f"OPENROUTER_MODEL={llm_model}\n")
		else:
			f.write("LLM_PROVIDER=local\n")
			local_llm_base_url = input("Enter the custom endpoint base URL (default: http://localhost:11434/v1): ").strip() or "http://localhost:11434/v1"
			local_llm_model = input("Enter the model name (default: gemma4:cloud): ").strip() or "gemma4:cloud"
			local_llm_api_key = input("Enter the custom endpoint LLM API key (if required, otherwise leave blank): ").strip()

			f.write(f"LOCAL_LLM_BASE_URL={local_llm_base_url}\n")
			f.write(f"LOCAL_LLM_MODEL={local_llm_model}\n")
			f.write(f"LOCAL_LLM_API_KEY={local_llm_api_key}\n")


		llm_request_timeout_int = positive_integer_with_default("Enter the LLM request timeout in seconds", 60)

		f.write(f"LLM_REQUEST_TIMEOUT={llm_request_timeout_int}\n")

	print()

	number_of_accounts = positive_integer_with_default("Enter the number of accounts to configure", 1)

	if number_of_accounts > 1:
		accounts = []

		for i in range(1, number_of_accounts + 1):
			print(f"\nConfiguring account {i}:")
			if i == 1:
				profile_dir = nonempty_input("Enter a profile directory name (usually 'Default'): ").strip()
			else:
				profile_dir = nonempty_input(f"Enter a profile directory name for account {i}: ").strip()

			accounts.append(profile_dir)
	else:
		accounts = ["Default"]

	f.write(f"REWARDS_ACCOUNTS={','.join(accounts)}\n")

	print()

	headless = boolean_with_default("Do you want to run the browser in headless mode?", False)

	f.write(f"HEADLESS={str(headless).lower()}\n")

	print()

	custom_paths = boolean_with_default("Do you want to specify custom paths for msedgedriver.exe and msedge.exe?", False)

	if custom_paths:
		msedgedriver_path = input("Enter custom path to msedgedriver.exe (default: unset): ").strip()

		if msedgedriver_path:
			f.write(f"MSEDGEDRIVER_PATH={msedgedriver_path}\n")

		edge_binary_path = input("Enter custom path to msedge.exe (default: unset): ").strip()

		if edge_binary_path:
			f.write(f"EDGE_BINARY={edge_binary_path}\n")

	setup_logging = boolean_with_default("Do you want to set up logging for the driver and rewards farmer?", False)

	if setup_logging:
		driver_log_path = input("Enter path for driver log file (default: unset): ").strip()

		if driver_log_path:
			f.write(f"REWARDS_DRIVER_LOG={driver_log_path}\n")

		farmer_log_file = input("Enter path for rewards farmer log file (default: unset): ").strip()

		if farmer_log_file:
			f.write(f"REWARDS_FARMER_LOG_FILE={farmer_log_file}\n")

		farmer_log_level = one_of_with_default("Enter log level for rewards farmer", ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], "INFO")
		f.write(f"REWARDS_FARMER_LOG_LEVEL={farmer_log_level}\n")

	print()

	if sys.platform.startswith("win"):
		print("Windows-specific configuration options:")

		create_virtual_desktop = boolean_with_default("Do you want the script to automatically run the browser on a separate virtual desktop?", False)

		f.write(f"USE_VIRTUAL_DESKTOP={str(create_virtual_desktop).lower()}\n")

		if create_virtual_desktop:
			switch_back_to_main_desktop = boolean_with_default("Do you want to switch back to the main desktop after launching the browser?", True)
			f.write(f"SWITCH_BACK_TO_MAIN_DESKTOP={str(switch_back_to_main_desktop).lower()}\n")

			if switch_back_to_main_desktop:
				switch_back_delay_seconds = positive_integer_with_default("Enter the delay in seconds before switching back to the main desktop", 1)
				f.write(f"SWITCH_BACK_DELAY_SECONDS={switch_back_delay_seconds}\n")

			cleanup_virtual_desktop = boolean_with_default("Do you want to clean up (close) the extra virtual desktop after the script finishes?", True)
			f.write(f"CLEANUP_VIRTUAL_DESKTOP={str(cleanup_virtual_desktop).lower()}\n")

	print("\nConfiguration finished!\nYou are ready to run rewards-farmer with the new configuration.\n\nYou may edit these settings at any time by modifying the .env file directly.")

def main():
	path_to_dotenv = Path(__file__).parent / ".env"

	path_input = input(f"Path to .env file: (Default: {path_to_dotenv}): ").strip()

	if path_input:
		path_to_dotenv = Path(path_input)

	print("WARNING: This script will overwrite any existing configuration in the .env file.")

	cont = boolean_with_default("Do you want to continue?", True)

	if not cont:
		print("Exiting without making changes.")
		return

	try:
		with open(path_to_dotenv, "w") as f:
			configure_variables(f)
	except OSError as e:
		print(f"Error creating or clearing the .env file: {e}")

if __name__ == "__main__":
	main()
