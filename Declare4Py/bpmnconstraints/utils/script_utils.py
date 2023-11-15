import json
import os
import pandas as pd


class Setup:
    def __init__(self, dir_path) -> None:
        self.dir_path = dir_path
        self.chunk_size = 8**2

    def get_files(self):
        return os.listdir(self.dir_path)

    def get_file(self, filename):
        return os.path.join(self.dir_path, filename)

    def is_file(self, file):
        return os.path.isfile(file)

    def is_directory(self, dir_path):
        return os.path.isdir(dir_path)

    def read_csv_chunk(self, file):
        return pd.read_csv(file, chunksize=self.chunk_size)

    def load_models(self, chunk):
        return chunk["Model JSON"].apply(json.loads)

    def load_dataframe(self, file):
        return pd.read_pickle(file)
