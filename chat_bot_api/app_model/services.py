import os
import re
import pandas as pd
from bs4 import BeautifulSoup

from datasets import load_dataset

class PrepareDataService:

    def clean_html(self, raw_html):
        return BeautifulSoup(raw_html, "html.parser").get_text(separator=" ").strip()

    def clean_whitespace(self, text):
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def clean_and_format_data(self, df: pd.DataFrame) -> pd.DataFrame:
        df['clean_title'] = df['title'].apply(lambda x: self.clean_html(str(x)))
        df['clean_body'] = df['body'].apply(lambda x: self.clean_html(str(x)))

        df['clean_text'] = df['clean_title'] + ". " + df['clean_body']

        df['clean_text'] = df['clean_text'].apply(self.clean_whitespace)

        return df

    @staticmethod
    def get_huggingface_data_and_save(download_dir_path) -> None:
        ''''''

        dataset_file_path = os.path.join(download_dir_path, "stackexchange_full.parquet")
        
        dataset = load_dataset("habedi/stack-exchange-dataset", split = 'train')
        df = dataset.to_pandas()

        df = PrepareDataService.clean_and_format_data(df)

        os.makedirs(download_dir_path, exist_ok = True)

        df.to_parquet(dataset_file_path, index = False)

        