from etl.base_pipeline import BaseETLPipeline
from etl.extraction.extractor import DataExtractor
from etl.transformation.transformer import DataTransformer
from etl.loading.loader import DataLoader
from config.settings import Settings


class EcommerceSalesAnalyticsPipeline(BaseETLPipeline):
    def __init__(
        self,
        extractor_class=DataExtractor,
        transformer_class=DataTransformer,
        loader_class=DataLoader,
    ):
        super().__init__("EcommerceSalesAnalytics")
        self._extractor_class = extractor_class
        self._transformer_class = transformer_class
        self._loader_class = loader_class

    def extract(self) -> dict:
        extractor = self._extractor_class(self.spark, self.logger)
        raw_df = extractor.extract_raw_data(Settings.LOCAL_RAW_PATH)
        return extractor.split_extracts(raw_df)

    def transform(self, dataframes: dict) -> dict:
        transformer = self._transformer_class(self.logger)
        return transformer.transform_all(dataframes)

    def load(self, transformed_dfs: dict) -> None:
        loader = self._loader_class(self.spark, self.logger)
        loader.save_to_s3(transformed_dfs, Settings.LOCAL_CURATED_PATH)
        loader.load_pipeline_data(transformed_dfs)
