from enum import Enum


class DealTypesForQueryEnum(Enum):
    DEAL = "매매"
    JEONSE_MONTHLY_RENT = "전월세"

    @staticmethod
    def get_deal_types() -> list[str]:
        return [e.value for e in DealTypesForQueryEnum]


class DealTypesForDBEnum(Enum):
    DEAL = "DEAL"
    JEONSE = "JEONSE"
    MONTHLY_RENT = "MONTHLY_RENT"

    @staticmethod
    def get_deal_types() -> list[str]:
        return [e.value for e in DealTypesForDBEnum]


DEAL_TYPES = (
    (DealTypesForDBEnum.DEAL.value, DealTypesForDBEnum.DEAL.value),
    (DealTypesForDBEnum.JEONSE.value, DealTypesForDBEnum.JEONSE.value),
    (
        DealTypesForDBEnum.MONTHLY_RENT.value,
        DealTypesForDBEnum.MONTHLY_RENT.value,
    ),
)


class BrokerageTypesEnum(Enum):
    BROKERAGE = "BROKERAGE"
    DIRECT = "DIRECT"


BROKERAGE_TYPES = (
    (BrokerageTypesEnum.BROKERAGE.value, BrokerageTypesEnum.BROKERAGE.value),
    (BrokerageTypesEnum.DIRECT.value, BrokerageTypesEnum.DIRECT.value),
)


class DealPerPageEnum(Enum):
    PER_PAGE = 10
