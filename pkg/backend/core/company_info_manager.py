from .storage import Storage

class CompanyInfoManager:
    def __init__(self, storage: Storage):
        self.storage = storage

    def get_company_info(self):
        return self.storage.get_company_info()

    def set_company_info(self, info: dict):
        self.storage.set_company_info(info)

    def get_products(self):
        return self.storage.get_products()

    def set_products(self, products: list):
        self.storage.set_products(products)

    def get_responsible_person(self, product_name: str):
        return self.storage.get_responsible_person(product_name)

    def set_responsible_person(self, product_name: str, person: dict):
        self.storage.set_responsible_person(product_name, person) 