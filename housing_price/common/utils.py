from pyspark.sql import SparkSession
from pyspark import SparkConf, SparkContext
import os
import sys
import editdistance
import numpy as np


class Spark_session_factory(object):
    __instance = None

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = SparkSession \
                .builder \
                .getOrCreate()
        return cls.__instance


def read_csv(sc, src_path, header):
    df = sc.read.option('inferschema', True).option('header',
                                                    header).csv(src_path)
    return df


def sink_to_bigquery(df, dest_path):
    df.write.format('bigquery') \
        .option('table', dest_path) \
        .save()


class Properties(object):
    def __init__(self, filename):
        self.filename = filename
        self.properties = {}

    def __getDict(self, strName, dictName, value):
        if strName.find('.') > 0:
            k = strName.split('.')[0]
            dictName.setdefault(k, {})
            return self.__getDict(strName[len(k) + 1:], dictName[k], value)
        else:
            dictName[strName] = value
            return

    def getProperties(self):
        try:
            pro_file = open(self.filename, 'Ur')
            for line in pro_file.readlines():
                line = line.strip().replace('\n', '')
                if line.find('#') != -1:
                    line = line[0:line.find('#')]
                if line.find('=') > 0:
                    strs = line.split('=')
                    strs[1] = line[len(strs[0]) + 1:]
                    self.__getDict(strs[0].strip(), self.properties,
                                   strs[1].strip())
        except Exception:
            print('Read properties error')
        else:
            pro_file.close()
        return self.properties


class Property_factory(object):
    __instance = None

    def __init__(self) -> None:
        super().__init__()

    @classmethod
    def get_instance(cls):
        if not cls.__instance:
            cls.__instance = Properties(
                'housing_price/sources/housing_config.properties'
            ).getProperties()
        return cls.__instance


class SimilarCityRetriever:
    namemap = {
        'nyc': 'nyc',
        'new york': 'nyc',
        'new york city': 'nyc',
        'la': 'la',
        'los angeles': 'la',
        'chicago': 'chicago',
        'chi': 'chicago'
        # 'sh': 'sh',
        # 'shanghai': 'sh'
        # 'tyo': 'tyo',
        # 'tokyo': 'tyo',
        # 'lon': 'lon',
        # 'lon': 'london'
    }
    namelist = np.array(list(namemap.keys()))

    @staticmethod
    def getSimilarCity(cityname):
        scr = SimilarCityRetriever
        cityname = cityname.lower()
        evalarr = [editdistance.eval(cityname, w) for w in scr.namelist]
        idx = np.argmin(evalarr)
        return scr.namemap[scr.namelist[idx]]


def getPicList(cityname):
    path = 'static/img/citypreview'+cityname
    res = []
    for root, directories, files in os.walk(path):
        for name in files:
            res.append(str(os.path.join(path, name)))
    return res
