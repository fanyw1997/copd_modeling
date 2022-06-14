import os
from enum import Enum

import yaml
import pandas as pd

from enums import *

class AttributeReader:
    def __init__(self,
                 filename_generator: str = 'config/generate.yaml'):
        self._attributes = dict()
        self._attributes_order = list()
        with open(filename_generator, 'r') as fin:
            d = yaml.safe_load(fin)['attributes']
            for attr in d:
                self._attributes_order.append(attr)
                r = AttributeParser(f'config/{attr}.yaml')
                r.attribute_parse()
                self._attributes[attr] = r

    def get_attribute_list(self):
        return self._attributes

    def get_attribute_order(self):
        return self._attributes_order

class AttributeParser:
    def __init__(self,
                 filename_attr):
        self._filename_attr = filename_attr
        self._attribute_name = os.path.splitext(os.path.basename(filename_attr))[0]
        self._attr_type = None

    def attribute_parse(self):
        with open(self._filename_attr, 'r') as fin:
            d = yaml.safe_load(fin)
            type = d['type']
            self._attr_type = type

            def attribute_check_integrity(df: pd.DataFrame, depend_value: Enum):
                """
                检查读取的attributes分布概率加和为1
                """
                if df[(df['depend_value'] == depend_value) | (depend_value is None) & (pd.isna(df['depend_value']))]['attr_value'].sum() != 1:
                    raise Exception(f'{self._filename_attr}: {depend_value} sum not equal to 1')

            def attribute_parse_integer(yaml_dict: dict, depend_attr: str) -> pd.DataFrame:
                """
                读取integer类别attributes的分布
                """
                # attr_开头的是变量自身的信息，depend开头的是和变量相关的变量的信息
                # depend_attr 是该变量对应的枚举类字符串， depend_value 是该变量对应的枚举类型的元素
                df = pd.DataFrame(columns = ['attr_lower', 'attr_upper', 'depend_attr', 'depend_value', 'attr_value'])
                # 'attr_lower': int, 'attr_upper': int, 'depend_attr': str, 'depend_value': Enum, 'attr_value': float

                for depend_value in yaml_dict:
                    depend_element = get_enum_element(depend_attr, depend_value) \
                        if depend_attr is not None else None
                    keys = list(yaml_dict[depend_value].keys())
                    keys.sort()
                    for i in range(len(keys) - 1): # integer类型的最后一行为取值上限，分布概率恒为0，所以不需要处理
                        df.loc[len(df)] = [keys[i], keys[i + 1], depend_attr, depend_element, yaml_dict[depend_value][keys[i]]]
                    attribute_check_integrity(df, depend_element)
                return df

            def attribute_parse_category(yaml_dict: dict, attr: str, depend_attr: str) -> pd.DataFrame:
                """
                读取category类别attributes的分布
                """
                df = pd.DataFrame(columns=['attr_category', 'depend_attr', 'depend_value', 'attr_value'])
                # 'attr_category': Enum, 'depend_attr': str, 'depend_value': Enum, 'attr_value': float

                for depend_value in yaml_dict:
                    depend_element = get_enum_element(depend_attr, depend_value) \
                        if depend_attr is not None else None
                    keys = list(yaml_dict[depend_value].keys())
                    for i in range(len(keys)):
                        df.loc[len(df)] = [get_enum_element(attr, keys[i]), depend_attr, depend_element, yaml_dict[depend_value][keys[i]]]
                    attribute_check_integrity(df, depend_element)
                return df


            if type == 'integer':
                self._df_initial = attribute_parse_integer(d['initial'], d['depend'])
                self._df_incidence = attribute_parse_integer(d['incidence'], d['depend'])

            elif type == 'category':
                self._df_initial = attribute_parse_category(d['initial'], self._attribute_name, d['depend'])
                self._df_incidence = attribute_parse_category(d['incidence'], self._attribute_name, d['depend'])

            else:
                raise Exception(f'Attributes {self._filename_attr} type unknown')

            # print(self._df_initial)
            # print(self._df_incidence)

    def get_attribute_initial(self):
        return self._df_initial

    def get_attribute_incidence(self):
        return self._df_incidence

    def get_attribute_type(self):
        return self._attr_type

if __name__ == "__main__":
    r = AttributeReader()
    for k, v in r.get_attribute_list().items():
        print(k)
        print(v.get_attribute_incidence())
        print()
