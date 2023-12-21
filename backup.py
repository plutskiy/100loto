import subprocess
import os
import datetime

def backup_db(db_name):
    backup_name = f"{db_name}_backup_{datetime.datetime.now().strftime('%Y %m %d %H:%M')}.sqlite"
    command = f"cp {db_name} {backup_name}"
    process = subprocess.Popen(command, shell=True)
    process.wait()
    if process.returncode != 0:
        print("Backup failed.")
    else:
        print(f"Backup successful. Backup saved as {backup_name}")