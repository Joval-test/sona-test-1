from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import os

Base = declarative_base()
DB_PATH = 'sqlite:///data/companyinfo.db'

class CompanyInfo(Base):
    __tablename__ = 'company_info'
    id = Column(Integer, primary_key=True)
    info = Column(Text)
    # One-to-many: products
    products = relationship('Product', back_populates='company')

class Product(Base):
    __tablename__ = 'product'
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    company_id = Column(Integer, ForeignKey('company_info.id'))
    company = relationship('CompanyInfo', back_populates='products')
    responsible_person = relationship('ResponsiblePerson', uselist=False, back_populates='product')

class ResponsiblePerson(Base):
    __tablename__ = 'responsible_person'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    product_id = Column(Integer, ForeignKey('product.id'))
    product = relationship('Product', back_populates='responsible_person')

engine = create_engine(DB_PATH, echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

class Storage:
    def __init__(self):
        self.session = Session()

    def get_company_info(self) -> dict:
        info = self.session.query(CompanyInfo).first()
        return {"info": info.info if info else ""}

    def set_company_info(self, info: dict):
        ci = self.session.query(CompanyInfo).first()
        if not ci:
            ci = CompanyInfo(info=info.get("info", ""))
            self.session.add(ci)
        else:
            ci.info = info.get("info", "")
        self.session.commit()

    def get_products(self) -> list:
        products = self.session.query(Product).all()
        return [p.name for p in products]

    def set_products(self, products: list):
        # Remove all and add new
        self.session.query(Product).delete()
        ci = self.session.query(CompanyInfo).first()
        for name in products:
            p = Product(name=name, company=ci)
            self.session.add(p)
        self.session.commit()

    def get_responsible_person(self, product_name: str) -> dict:
        product = self.session.query(Product).filter_by(name=product_name).first()
        if product and product.responsible_person:
            rp = product.responsible_person
            return {"name": rp.name, "email": rp.email}
        return {}

    def set_responsible_person(self, product_name: str, person: dict):
        product = self.session.query(Product).filter_by(name=product_name).first()
        if not product:
            return
        rp = product.responsible_person
        if not rp:
            rp = ResponsiblePerson(name=person.get("name", ""), email=person.get("email", ""), product=product)
            self.session.add(rp)
        else:
            rp.name = person.get("name", "")
            rp.email = person.get("email", "")
        self.session.commit() 