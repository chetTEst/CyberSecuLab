# -*- cuding: utf-8 -*-
import os

# Create the directory
os.makedirs('files', exist_ok=True)

# Create the files
for i in range(1, 11):
    with open(f'files/file{i}.txt', 'w', encoding='utf-8') as f:
        f.write(f'Это просто файл" {i}')
