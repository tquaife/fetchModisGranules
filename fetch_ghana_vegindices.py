#!/usr/bin/python

from fetch_modis_granules import *

if __name__=="__main__":

    for product in ["MOD13A1.006", "MYD13A1.006"]:
        dates=get_date_list(product)
        dates=subset_date_list(dates,'2016.01.01','2016.02.01')
        tiles=['h17v07','h17v08','h18v07','h18v08']
        url_list=get_granule_urls(product, dates, tiles)
        fetch_modis_granules(url_list)

