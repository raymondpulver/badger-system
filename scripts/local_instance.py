from helpers.gnosis_safe import GnosisSafe, MultisigTxMetadata
import os
from scripts.systems.sushiswap_system import SushiswapSystem
from scripts.systems.digg_system import connect_digg
from scripts.systems.uniswap_system import UniswapSystem
from scripts.systems.claw_minimal import deploy_claw_minimal
import time

from brownie import *
import decouple
from config.badger_config import badger_config
from helpers.constants import *
from helpers.time_utils import days
from helpers.token_utils import (
    distribute_from_whales,
    distribute_meme_nfts,
    distribute_test_ether,
)
from rich.console import Console
from scripts.deploy.deploy_digg import (
    deploy_digg_with_existing_badger,
    digg_deploy_flow,
)
from scripts.systems.badger_system import connect_badger
from helpers.registry import token_registry
from config.badger_config import digg_config
console = Console()


def main():
    """
    Connect to badger, distribute assets to specified test user, and keep ganache open.
    Ganache will run with your default brownie settings for mainnet-fork
    """

    # The address to test with
    user = accounts.at(decouple.config("TEST_ACCOUNT"), force=True)

    badger = connect_badger("deploy-final.json", load_deployer=True, load_keeper=True, load_guardian=True)
    digg = connect_digg("deploy-final.json")
    digg.token = digg.uFragments

    badger.add_existing_digg(digg)

    # TODO: After prod deployment, just connect instead.
    deploy_claw_minimal(badger.deployer, printToFile=True)

    console.print("[blue]=== 🦡 Test ENV for account {} 🦡 ===[/blue]".format(user))

    distribute_test_ether(user, Wei("20 ether"))
    distribute_from_whales(user)

    console.print("[green]=== ✅ Test ENV Setup Complete ✅ ===[/green]")
    # Keep ganache open until closed
    time.sleep(days(365))

