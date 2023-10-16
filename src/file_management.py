import os

def sync_local_to_private_s3():
    cmd = 'aws s3 sync /home/bgillman/cloning_booth_media/ s3://cloningboothmedia/'
    os.system(cmd)

def sync_private_to_public_s3():
    cmd = 'aws s3 sync s3://cloningboothmedia/ s3://cloningboothmediapublic/'
    os.system(cmd)

def remove_all_public_s3():
    cmd = 'aws s3 rm s3://cloningboothmediapublic --recursive'
    os.system(cmd)