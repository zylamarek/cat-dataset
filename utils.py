from urllib.request import urlretrieve
import zipfile
import os
import shutil
import hashlib


def download_file(url, file_path, checksum):
    if os.path.isfile(file_path):
        if checksum == md5_checksum(file_path):
            print('File "%s" already exists - skipping' % file_path)
            return

    def reporthook(blocknum, bs, size):
        if size > 0:
            percent = min(blocknum * bs / size * 100, 100)
            print('\r%.2f%% of %.2fMB' % (percent, size / 1024 / 1024), end='')
        else:
            print(blocknum * bs)

    print('Downloading "%s" to "%s"...' % (url, file_path))
    urlretrieve(url, file_path, reporthook)
    print()


def md5_checksum(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def extract_file(zip_path, extraction_dir):
    print('Extracting "%s" to "%s"...' % (zip_path, extraction_dir))
    zf = zipfile.ZipFile(zip_path)
    size = sum((file.file_size for file in zf.infolist()))
    extracted_size = 0

    for cnt, file in enumerate(zf.infolist()):
        extracted_size += file.file_size
        percent = min(extracted_size / size * 100, 100)
        if not cnt % 10:
            print('\r%.2f%% of %.2fMB' % (percent, size / 1024 / 1024), end='')
        zf.extract(file, extraction_dir)

    print('\r100.00%% of %.2fMB' % (size / 1024 / 1024))


def copy_directory(src, dst):
    print('Copying contents of "%s" to "%s"...' % (src, dst))

    total = 0
    tree = []
    for root, dirs, files in os.walk(src):
        sizes = []
        for file in files:
            file_path = os.path.join(root, file)
            size = os.path.getsize(file_path)
            sizes.append(size)
            total += size
        tree.append((root, dirs, files, sizes))

    cnt = 0
    copied_size = 0
    for root, dirs, files, sizes in tree:
        for dir_name in dirs:
            path_from = os.path.join(root, dir_name)
            dir_path_rel = os.path.relpath(path_from, src)
            dir_path_to = os.path.join(dst, dir_path_rel)
            os.makedirs(dir_path_to)

        for file_name, size in zip(files, sizes):
            path_from = os.path.join(root, file_name)
            file_path_rel = os.path.relpath(path_from, src)
            path_to = os.path.join(dst, file_path_rel)
            shutil.copyfile(path_from, path_to)

            copied_size += size
            cnt += 1
            if not cnt % 100:
                percent = min(copied_size / total * 100, 100)
                print('\r%.2f%% of %.2fMB' % (percent, total / 1024 / 1024), end='')

    print('\r100.00%% of %.2fMB' % (total / 1024 / 1024))


def remove_inner_ear_landmarks(file_path):
    with open(file_path, 'r') as cat_file:
        landmarks = cat_file.readline().split()
    del (landmarks[17:])
    del (landmarks[11:15])
    del (landmarks[7:9])
    landmarks[0] = '5'
    with open(file_path, 'w') as cat_file:
        cat_file.write(' '.join(landmarks))
