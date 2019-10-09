import os
import shutil
import json

from utils import download_file, extract_file, copy_directory, remove_inner_ear_landmarks, crop_and_resize_image

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

# Remove landmarks 3, 5, 6, 8 (zero-based) - 2 inner points of each ear
print('Removing inner ear landmarks...')
cnt = 0
total = sum([len([f for f in os.listdir(os.path.join(clean_path, subdir)) if f.endswith('.cat')])
             for subdir in os.listdir(clean_path)])
for i_subdir, subdir in enumerate(os.listdir(clean_path)):
    subdir_path = os.path.join(clean_path, subdir)
    for filename in os.listdir(subdir_path):
        if filename.endswith('.cat'):
            file_path = os.path.join(subdir_path, filename)
            remove_inner_ear_landmarks(file_path)
            cnt += 1
            if not cnt % 100:
                percent = cnt / total * 100
                print('\r%.2f%% of %d' % (percent, total), end='')
print('\r100.00%% of %d' % total)

print('Splitting data into training/validation/test sets...')
cnt = 0
total = sum([len([fn for fn in os.listdir(os.path.join(clean_path, subdir)) if fn[-4:] in ('.cat', '.jpg')])
             for subset in config['split'] for subdir in config['split'][subset]['subdirs']])
for subset in config['split']:
    subset_path = os.path.join(clean_path, subset)
    os.makedirs(subset_path)
    for i_subdir, subdir in enumerate(config['split'][subset]['subdirs']):
        subdir_path = os.path.join(clean_path, subdir)
        operation = config['split'][subset]['operation']
        for filename in os.listdir(subdir_path):
            if filename[-4:] in ('.cat', '.jpg'):
                file_path = os.path.join(subdir_path, filename)
                file_path_subset = os.path.join(subset_path, subdir + '_' + filename)
                if operation == 'move':
                    os.rename(file_path, file_path_subset)
                elif operation == 'copy':
                    shutil.copyfile(file_path, file_path_subset)
                cnt += 1
                if not cnt % 100:
                    percent = cnt / total * 100
                    print('\r%.2f%% of %d' % (percent, total), end='')
        if operation == 'move':
            shutil.rmtree(subdir_path, ignore_errors=True)
print('\r100.00%% of %d' % total)

# Crop images in validation and test datasets to obtain uniformly distributed scales
print('Cropping and resizing subsets...')
cnt = 0
total = sum([len(l) for l in config['crop'].values()])
for subdir in config['crop']:
    for filename, bounding_box in config['crop'][subdir].items():
        file_path = os.path.join(clean_path, subdir, filename)
        crop_and_resize_image(file_path, bounding_box, None, 'jpeg')
        cnt += 1
        if not cnt % 10:
            percent = cnt / total * 100
            print('\r%.2f%% of %d' % (percent, total), end='')
print('\r100.00%% of %d' % total)

# Crop and resize images in validation and test datasets for landmarks in ROI detection
print('Cropping and resizing landmarks subsets...')
cnt = 0
total = sum([len(l) for l in config['crop_landmarks'].values()])
for subdir in config['crop_landmarks']:
    for filename, bounding_box in config['crop_landmarks'][subdir].items():
        file_path = os.path.join(clean_path, subdir, filename)
        crop_and_resize_image(file_path, bounding_box, config['img_size'], 'bmp')
        cnt += 1
        if not cnt % 10:
            percent = cnt / total * 100
            print('\r%.2f%% of %d' % (percent, total), end='')
print('\r100.00%% of %d' % total)

print('done.')
