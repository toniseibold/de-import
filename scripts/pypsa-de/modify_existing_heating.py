import logging

import pandas as pd

from scripts._helpers import (
    configure_logging,
    set_scenario_config,
    update_config_from_wildcards,
    mock_snakemake,
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    if "snakemake" not in globals():
        snakemake = mock_snakemake(
            "modify_existing_heating",
            run="KN2045_Mix",
        )

    configure_logging(snakemake)
    set_scenario_config(snakemake)
    update_config_from_wildcards(snakemake.config, snakemake.wildcards)

    existing_heating = pd.read_csv(snakemake.input.existing_heating, index_col=0)

    logger.info(
        f"Heating demand before modification:\n{existing_heating.loc['Germany']}"
    )

    new_values = pd.Series()

    logger.warning(
        "Adjusting heating stock towards hard coded values from a\nprevious REMod run. This is only a hotfix."
    )  # Because REMod is not consistent and a better solution takes too long.

    new_values["gas boiler"] = 11.44  # million
    new_values["oil boiler"] = 5.99
    new_values["air heat pump"] = 0.38
    new_values["ground heat pump"] = 0.38
    new_values["biomass boiler"] = 2.8

    total_stock = new_values.sum()
    existing_factor = existing_heating.loc["Germany"].sum() / total_stock

    new_values *= existing_factor

    for tech, peak in new_values.items():
        existing_heating.at["Germany", tech] = peak

    logger.info(
        f"Heating demand after modification:\n{existing_heating.loc['Germany']}"
    )

    existing_heating.to_csv(snakemake.output.existing_heating)
