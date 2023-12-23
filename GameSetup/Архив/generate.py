# Python script to create text files and directories for the Cyberia project
# -*- cuding: utf-8 -*-
from time import time
import os
import random
from icecream import ic
ic.enable()


def uniqid(prefix='Ban', postfix='K'):
    return prefix + hex(int(time()) * random.randint(1000, 100000))[2:10] + hex(
        int(time() * random.randint(1000000, 2000000)) % 0x100000)[2:7]+postfix


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
    "Government_Affairs": ["Policies", "Public_Statements", "Classified_Information", "Legislative_Documents", "International_Agreements"],
    "Cyberia_National_Bank": ["Transaction_Logs", "Account_Details", "Security_Protocols", "Audit_Reports", "Customer_Services"],
    "FSB_Cybercrime_Investigation_Department": ["Agent_Reports", "Mission_Briefings", "Encrypted_Communications", "Surveillance_Data", "Cybercrime_Statistics"],
    "Hacker_Groups": ["Plans", "Communication_Logs", "Exploits_and_Tools", "Member_Identities", "Target_Profiles"],
    "Cyberia_News_Network": ["Articles", "Interviews", "Leaked_Information", "Editorial_Opinions", "Investigative_Reports"],
    "Underground_Forums": ["Trade", "Messages", "Covert_Operations", "Hacking_Tutorials", "Black_Market_Listings"],
    "Tech_Giants": ["Product_Launches", "Internal_Memos", "Research_and_Development", "Employee_Directories", "Strategic_Plans"],
    "Data_Security_Firms": ["Threat_Analysis", "Client_Portfolios", "Incident_Reports", "Vulnerability_Assessments", "Security_Tools"],
    "Educational_Institutions": ["Research_Papers", "Student_Databases", "Curriculum_Guides", "Partnership_Agreements", "Event_Calendars"],
    "Telecom_Networks": ["Infrastructure_Details", "User_Data", "Regulatory_Compliance", "Network_Expansion_Plans", "Service_Outage_Reports"]
}


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
            file_path = os.path.join(dir_path, f"{uniqid()}.txt")
            with open(file_path, 'w') as file:
                file.write(uniqid())


# Path for the bank_system_log.txt file
bank_log_path = os.path.join(base_path, "Cyberia_News_Network", "Articles", f"{uniqid()}.log")

# Write the bank system log file
generate_bank_system_log(bank_log_path)


