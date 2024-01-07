from enum import Enum


class TradeType(Enum):
    DEAL = "매매"
    # JEONSE_MONTHLY_RENT = "전월세"

    @classmethod
    def get_trade_types(self):
        return [e.value for e in TradeType]
