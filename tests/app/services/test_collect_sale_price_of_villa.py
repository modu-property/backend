
from app.services.collect_sale_price_of_villa_service import CollectSalePriceOfVillaService
import os

def test_collect_sale_price_of_villa():
    CollectSalePriceOfVillaService().execute()
    