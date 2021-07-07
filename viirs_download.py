
import urllib

viirs = "https://e4ftl01.cr.usgs.gov/VIIRS/VNP09GA.001/2021.07.05/"

name = "VNP09GA.A2021186.h10v04.001.2021187084506.h5"
url = viirs + name

from pathlib import Path
from download import Downloader
import io
import h5py
import requests

downloader = Downloader()

save_folder = Path("G:/PyProjects/nasa-viirs-modis-nrt/VNP09GA")
# downloader.download(url=url, save_folder=save_folder)

url_test = "https://e4ftl01.cr.usgs.gov/VIIRS/VNP09GA.001/2021.07.05/VNP09GA.A2021186.h01v11.001.2021187081245.h5"
# url_test = 'https://firms.modaps.eosdis.nasa.gov/data/active_fire/modis-c6.1/shapes/zips/MODIS_C6_1_Global_24h.zip'
# downloader.download(url=url_test, save_folder=save_folder)


# auth=('puzhao_agb', 'kth10044NASA!')
# urllib.request.urlretrieve(url_test, save_folder)

# r = requests.get(url_test, allow_redirects=True, auth=auth)
# f= h5py.File('weights_btc.h5', 'w')
# f.create_dataset(name ="Test", data = r.content)
# f.close()

# if not h5py.is_hdf5('weights_btc.h5'):
#     raise ValueError('Not an hdf5 file')
# html = open(local_filename)
# print(html)


# import subprocess
# # url = 'http://url/to/file.h5' 
# res = subprocess.getstatusoutput(['wget', '--proxy=off', url_test])
# print(res)



# import urllib as urllib2
# # proxy_handler = urllib2.ProxyHandler({})
# # opener = urllib2.build_opener(proxy_handler)
# # urllib2.install_opener(opener)

# url = url_test

# req = urllib2.Request(url)
# r = opener.open(req)
# result = r.read()

# with open('my_file.h5', 'wb') as f:
#     f.write(result)

import os, wget

wget.download(url_test)