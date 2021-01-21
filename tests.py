import os

# Error checking for csv filename
def is_file(filename):
    if(not os.path.isfile(filename) or not filename.endswith('.csv')):
        raise ValueError("You must provide a valid csv filename as parameter")
    return filename

# Prints state of class_data
def test_class_data(class_data):
    print('\n'.join('{}: {}'.format(*k) for k in enumerate(class_data)))