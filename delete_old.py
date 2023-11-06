import os, time

directory = "/app/downloads"
# Age in days of the files to be deleted.
days = 1
now = time.time()
deleted_files = []
for root, dirs, files in os.walk(directory):
    dirs = [dir for dir in dirs if dir]
    for file in files:
        file_path = os.path.join(root, *dirs, file)
        creation_time = os.path.getctime(file_path)
        if now - creation_time > days * 24 * 60 * 60:
            os.remove(file_path)
            deleted_files.append(file_path)