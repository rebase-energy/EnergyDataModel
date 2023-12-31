from dataclasses import dataclass, field
from typing import List, Optional, Union
import pandas as pd
from shapely.geometry import Point
import pytz
from uuid import uuid4




@dataclass
class EnergySystem:
    sites: List[Site] = field(default_factory=list)
    assets: List[EnergyAsset] = field(default_factory=list)

    def add_sites(self, sites: Union[Site, List[Site]]):
        if isinstance(sites, list):
            self.sites.extend(sites)
        else:
            self.sites.append(sites)

    def add_assets(self, assets: Union[EnergyAsset, List[EnergyAsset]]):
        if isinstance(assets, list):
            self.assets.extend(assets)
        else:
            self.assets.append(assets)

    def remove_site(self, site: Site):
        self.sites.remove(site)

    def remove_asset(self, asset: EnergyAsset):
        self.assets.remove(asset)

    def get_summary(self):
        def recursive_summary(site, level=0):
            summary = "  " * level + f"- {site.name}\n"
            for asset in site.assets:
                summary += "  " * (level + 1) + f"- {asset.name}\n"
            return summary

        summary = "=====================\n"
        summary += "Energy System Summary\n"
        summary += "====================="
        summary += "\nSites:\n"
        for site in self.sites:
            summary += f"- {site.name}\n"
            summary += "  " + f"{site.location}\n"

            for asset in site.assets:
                summary += "  " + f"- {asset.name}\n"
        summary += "\nNon-site assets:\n"
        for asset in self.assets:
            summary += f"- {asset.name}\n"
        summary += "=====================\n"
        return summary


# Example Usage
if __name__ == "__main__":
    site = Site(longitude=15, latitude=55, name="My Site")
    asset1 = EnergyAsset("Asset 1")
    asset2 = EnergyAsset("Asset 2")

    site.add_assets(asset1)
    site.add_assets(asset2)

    # Get and print the site summary
    site_summary = site.get_summary()
    print(site_summary)

    energy_system = EnergySystem()

    site1 = Site(longitude=15, latitude=55, name="Site 1")
    site2 = Site(longitude=25, latitude=65, name="Site 2")
    site1.add_assets([EnergyAsset("Asset 1"), EnergyAsset("Asset 2")])
    site2.add_assets(EnergyAsset("Asset 3"))

    energy_system.add_site(site1)
    energy_system.add_site(site2)
    energy_system.add_asset(EnergyAsset("Asset 4"))

    # Get and print the energy system summary
    system_summary = energy_system.get_summary()
    print(system_summary)
    print(site1)