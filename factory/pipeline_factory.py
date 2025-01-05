import os
from database import Database
from .processor_factory import ProcessorFactory
from .querier_factory import QuerierFactory
from pipelines import AerodromePipeline, UniswapV2Pipeline, UniswapV3Pipeline

class PipelineFactory:
    @staticmethod
    def get_pipeline(dex_name, db):
        pipelines = {
            "uniswap_v3": UniswapV3Pipeline,
            "uniswap_v2": UniswapV2Pipeline,
            "aerodrome": AerodromePipeline
        }
        if dex_name in pipelines:
            querier = QuerierFactory.get_querier(dex_name)
            processor = ProcessorFactory.get_processor(dex_name)
            return pipelines[dex_name](db, querier, processor)
        raise ValueError(f"No pipeline available for DEX: {dex_name}")

    @staticmethod
    def load_pipelines(db, dexes):
        pipelines = {}
        for dex_name in dexes:
            dex_name = dex_name.strip()
            if dex_name:
                try:
                    pipelines[dex_name] = PipelineFactory.get_pipeline(dex_name, db)
                except ValueError as e:
                    print(e)  # Log unavailable DEX pipelines
        return pipelines
