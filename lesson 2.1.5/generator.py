# -*- cuding: utf-8 -*-
import os
import random
import string

def random_word(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for _ in range(length))

def random_extension():
    extensions = ['txt', 'log', 'bin', 'dat', 'bak']
    return random.choice(extensions)

def random_bits(length):
    return bytes([random.getrandbits(8) for _ in range(length)])

def create_file(filename, content):
    with open(filename, 'wb') as file:
        file.write(content)

# Create 20 random files
for _ in range(20):
    filename = os.path.join("AdaptiveAntivirus", "normal_files", f"{random_word(5)}.{random_extension()}")
    content = random_bits(2)  # 2 bytes
    create_file(filename, content)


for i in range(1, 4):
    filename = os.path.join("AdaptiveAntivirus", "suspects", f"suspect{i}.bin")
    random_sequence = random.getrandbits(7)
    virus_sequence = random_sequence << 9 | 0x1FF  # Shift left by 9 bits and add 9 '1's
    content = virus_sequence.to_bytes(2, 'big')  # Convert to 2-byte array
    create_file(filename, content)

for i in range(10):
    is_virus = random.choice([True, False])
    file_name = os.path.join("AdaptiveAntivirus", "internet_files", f"{random_word(10)}.{random_extension()}")
    if is_virus:
        start_length = random.randint(5, 8)
        random_sequence = random.getrandbits(start_length)
        virus_sequence = random_sequence << start_length | 0x1FF  # Shift left by 9 bits and add 9 '1's
        content = virus_sequence.to_bytes(2, 'big')  # Convert to 2-byte array
        create_file(file_name, content)
        print(f"Virus file created: {file_name}")
    else:
        content = random_bits(2)  # 2 bytes
        create_file(file_name, content)
        print(f"Normal file created: {file_name}")


create_file(os.path.join("AdaptiveAntivirus", "viruses", "viruses1.bin"), b'\x03\xff')
create_file(os.path.join("AdaptiveAntivirus", "viruses", "viruses2.bin"), b'\x0f\xff')
create_file(os.path.join("AdaptiveAntivirus", "viruses", "viruses3.bin"), b'\x3f\xff')
create_file(os.path.join("AdaptiveAntivirus", "viruses", "viruses4.bin"), b'\x5f\xff')
create_file(os.path.join("AdaptiveAntivirus", "viruses", "viruses5.bin"), b'\x1f\xff')
create_file(os.path.join("AdaptiveAntivirus", "viruses", "viruses6.bin"), b'\x6f\xff')
print("Files created successfully.")
