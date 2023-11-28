# Python script to create text files and directories for the Cyberia project

import os
import random
import openai
from icecream import ic
ic.enable()


api_key = ic(os.environ.get('OPENAI_KEY'))

def generate_gpt_text(prompt, api_key, num_lines=10):
    openai.api_key = api_key
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=50 * num_lines,  # Adjust tokens as needed
            n=1,
            stop=None,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return str(e)


# Function to generate a detailed bank system log
def generate_bank_system_log(filename, num_entries=30, malicious_entries=5):
    with open(filename, 'w') as file:
        for i in range(num_entries):
            account_id = "AC" + str(random.randint(100, 999))
            amount = random.randint(100, 10000)
            if i < malicious_entries:
                account_id = "AC_MALICIOUS"
            file.write(f"Transaction ID: {i:05} | Account ID: {account_id} | Debit: ${amount} | Date: 2023-{random.randint(1, 12):02}-{random.randint(1, 28):02}\n")


# Directory structure
directories = {
    "Government_Affairs": ["Policies", "Public_Statements", "Classified_Information"],
    "Cyberia_National_Bank": ["Transaction_Logs", "Account_Details", "Security_Protocols"],
    "FSB_Cybercrime_Investigation_Department": ["Agent_Reports", "Mission_Briefings", "Encrypted_Communications"],
    "Hacker_Groups": ["Plans", "Communication_Logs", "Exploits_and_Tools"],
    "Cyberia_News_Network": ["Articles", "Interviews", "Leaked_Information"],
    "Underground_Forums": ["Trade", "Messages", "Covert_Operations"],
    "Tech_Giants": ["Product_Launches", "Internal_Memos", "Research_and_Development"]
}
topics = ["Кибербезопасность", "Хакерская атака", "Цифровая разведка", "Банковские операции", "Тайная миссия"]

# Base path for the directories
base_path = os.getcwd()

# Create directories and subdirectories
for main_dir, sub_dirs in directories.items():
    main_dir_path = os.path.join(base_path, main_dir)
    os.makedirs(main_dir_path, exist_ok=True)
    for sub_dir in sub_dirs:
        os.makedirs(os.path.join(main_dir_path, sub_dir), exist_ok=True)


# Create random text files in each subdirectory
for main_dir, sub_dirs in directories.items():
    for sub_dir in sub_dirs:
        dir_path = os.path.join(base_path, main_dir, sub_dir)
        for i in range(3):  # Generate 3 files per subdirectory
            file_path = os.path.join(dir_path, f"file_{i}.txt")
            with open(file_path, 'w') as file:
                prompt = f"Напишите статью о кибербезопасности в цифровом городе 'Киберия'. На тему: {random.choice(topics)}"
                file.write(generate_gpt_text(prompt, api_key))


# Path for the bank_system_log.txt file
bank_log_path = os.path.join(base_path, "Cyberia_National_Bank", "Transaction_Logs", "dfdf.log")

# Write the bank system log file
generate_bank_system_log(bank_log_path)


