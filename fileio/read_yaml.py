import yaml
import pandas as pd

class Reader:
    def __init__(self,
                 filename_generator: str = 'config/generate.yaml'):
        self._attributes = dict()
        self._attributes_order = list()
        with open(filename_generator, 'r') as fin:
            d = yaml.safe_load(fin)['attributes']
            for attr in d:
                self._attributes_order.append(attr)
                r = AttrReader(f'config/{attr}.yaml')
                r.attr_read()
                self._attributes[attr] = r

    def get_attributes(self):
        return self._attributes

    def get_attributes_order(self):
        return self._attributes_order

class AttrReader:
    def __init__(self,
                 filename_attr):
        self._filename_attr = filename_attr
        self._attr_type = None

    def attr_read(self):
        with open(self._filename_attr, 'r') as fin:
            d = yaml.safe_load(fin)
            type = d['type']
            self._attr_type = type

            def check_integrity(df: pd.DataFrame, depend_value: str):
                """
                检查读取的attributes分布概率加和为1
                """
                if df[(df['depend_value'] == depend_value) | (depend_value is None) & (pd.isna(df['depend_value']))]['attr_value'].sum() != 1:
                    raise Exception(f'{self._filename_attr}: {depend_value} sum not equal to 1')

            def attr_read_integer(yaml_dict: dict, depend_key: str) -> pd.DataFrame:
                """
                读取integer类别attributes的分布
                """
                # attr_开头的是变量自身的信息，depend开头的是和变量相关的变量的信息
                df = pd.DataFrame(columns = ['attr_lower', 'attr_upper', 'depend_key', 'depend_value', 'attr_value'])
                for depend_value in yaml_dict:
                    keys = list(yaml_dict[depend_value].keys())
                    keys.sort()
                    for i in range(len(keys) - 1): # integer类型的最后一行为取值上限，分布概率恒为0，所以不需要处理
                        df.loc[len(df)] = [keys[i], keys[i + 1], depend_key, depend_value, yaml_dict[depend_value][keys[i]]]
                    check_integrity(df, depend_value)
                return df

            def attr_read_category(yaml_dict: dict, depend_key: str) -> pd.DataFrame:
                """
                读取category类别attributes的分布
                """
                df = pd.DataFrame(columns=['attr_category', 'depend_key', 'depend_value', 'attr_value'])
                for depend_value in yaml_dict:
                    keys = list(yaml_dict[depend_value].keys())
                    for i in range(len(keys)):
                        df.loc[len(df)] = [keys[i], depend_key, depend_value, yaml_dict[depend_value][keys[i]]]
                    check_integrity(df, depend_value)
                return df


            if type == 'integer':
                self._df_initial = attr_read_integer(d['initial'], d['depend'])
                self._df_incidence = attr_read_integer(d['incidence'], d['depend'])

            elif type == 'category':
                self._df_initial = attr_read_category(d['initial'], d['depend'])
                self._df_incidence = attr_read_category(d['incidence'], d['depend'])

            else:
                raise Exception(f'Attributes {self._filename_attr} type unknown')

            # print(self._df_initial)
            # print(self._df_incidence)

    def get_initial(self):
        return self._df_initial

    def get_incidence(self):
        return self._df_incidence

    def get_attr_type(self):
        return self._attr_type

if __name__ == "__main__":
    r = Reader()
    for k, v in r.get_attributes().items():
        print(k, v.get_incidence())
        print()