from brownie import *

from helpers.constants import *
from helpers.multicall import Call, func, as_wei
from helpers.sett.resolvers.StrategyCoreResolver import StrategyCoreResolver, console

def confirm_harvest_badger_lp(before, after):
    """
    Harvest Should;
    - Increase the balanceOf() underlying asset in the Strategy
    - Reduce the amount of idle BADGER to zero
    - Increase the ppfs on sett
    """

    assert after.strategy.balanceOf >= before.strategy.balanceOf
    if before.sett.pricePerFullShare:
        assert after.sett.pricePerFullShare > before.sett.pricePerFullShare


class StrategySushiBadgerLpOptimizerResolver(StrategyCoreResolver):
    def confirm_harvest(self, before, after):
        super().confirm_harvest(before, after)
        # Strategy want should increase
        before_balance = before.get("strategy.balanceOf")
        assert after.get("strategy.balanceOf") >= before_balance if before_balance else 0

        # PPFS should not decrease
        assert after.get("sett.pricePerFullShare") >= before.get("sett.pricePerFullShare")

        # Sushi in badger tree should increase
        # Strategy should have no sushi
        # Strategy should have no sushi in Chef

    def confirm_tend(self, before, after):
        console.print("=== Compare Tend ===")
        self.manager.printCompare(before, after)
        # Increase xSushi position in strategy
        assert after.balances("xsushi", "strategy") > before.balances("xsushi", "strategy")

    def add_entity_balances_for_tokens(self, calls, tokenKey, token, entities):
        entities['badgerTree'] = self.manager.strategy.badgerTree()
        super().add_entity_balances_for_tokens(calls, tokenKey, token, entities)
        return calls
    
    def add_balances_snap(self, calls, entities):
        super().add_balances_snap(calls, entities)
        strategy = self.manager.strategy

        sushi = interface.IERC20(strategy.sushi())
        xsushi = interface.IERC20(strategy.xsushi())

        calls = self.add_entity_balances_for_tokens(calls, "sushi", sushi, entities)
        calls = self.add_entity_balances_for_tokens(calls, "xsushi", xsushi, entities)
        return calls

    def add_strategy_snap(self, calls):
        super().add_strategy_snap(calls)
        return calls

    def get_strategy_destinations(self):
        strategy = self.manager.strategy
        return {"chef": strategy.chef(), "bar": strategy.xsushi()}