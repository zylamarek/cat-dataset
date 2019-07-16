import os
import shutil
import json

from utils import download_file, extract_file, copy_directory

with open('config.json', 'r') as f:
    config = json.load(f)

data_dir = config['data_dir']
downloads_path = os.path.join(data_dir, config['downloads_dir'])
original_path = os.path.join(data_dir, config['original_dir'])
clean_path = os.path.join(data_dir, config['clean_dir'])
removed_path = os.path.join(data_dir, config['removed_dir'])
os.makedirs(data_dir, exist_ok=True)

# Download all
os.makedirs(downloads_path, exist_ok=True)
for filename, meta in config['dataset_urls'].items():
    file_path = os.path.join(downloads_path, filename)
    download_file(meta['url'], file_path, meta['md5'])

# Extract all
for filename in config['dataset_urls'].keys():
    if filename.endswith('.zip'):
        file_path = os.path.join(downloads_path, filename)
        extract_file(file_path, original_path)

# Replace incorrect file
for replace_file in config['replace']:
    print('Replacing "%s" with "%s"' % (os.path.join(replace_file['dir'], replace_file['filename_from']),
                                        os.path.join(replace_file['dir'], replace_file['filename_to'])))
    os.remove(os.path.join(original_path, replace_file['dir'], replace_file['filename_from']))
    shutil.copyfile(os.path.join(downloads_path, replace_file['filename_to']),
                    os.path.join(original_path, replace_file['dir'], replace_file['filename_to']))
print('done.')

# Make a copy of the original dataset
copy_directory(original_path, clean_path)

# Remove duplicates, pictures depicting more than one cat, etc...
print('Cleaning...')
os.makedirs(removed_path)
for subdir in config['remove']:
    for filename in config['remove'][subdir]:
        path_from = os.path.join(clean_path, subdir, filename)
        path_to = os.path.join(removed_path, subdir + '_' + filename)
        os.rename(path_from, path_to)
        os.rename(path_from + '.cat', path_to + '.cat')
print('done.')
