import logging
from typing import List

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from geopy.distance import geodesic
from fastapi.params import Query

# Configure logging
logging.basicConfig(filename="app.log", level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# SQLite Database setup
DATABASE_URL = "sqlite:///./addresses.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Define SQLAlchemy model for Address
class Address(Base):
    __tablename__ = "addresses"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)


# Create tables in the database
Base.metadata.create_all(bind=engine)


# Pydantic models for validation
class AddressCreate(BaseModel):
    name: str
    latitude: float = Field(
        ..., description="Latitude of the address. Must be between -90 and 90."
    )
    longitude: float = Field(
        ..., description="Longitude of the address. Must be between -180 and 180."
    )


class AddressUpdate(BaseModel):
    name: str = None
    latitude: float = None
    longitude: float = None


class AddressInDB(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float


# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Endpoint to create a new address
@app.post("/addresses/", response_model=AddressInDB, status_code=201)
def create_address(address: AddressCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating address: {address.name}")
    db_address = Address(**address.model_dump())
    db.add(db_address)
    db.commit()
    db.refresh(db_address)
    return db_address


# Endpoint to update an existing address
@app.put("/addresses/{address_id}", response_model=AddressInDB)
def update_address(
    address_id: int, address: AddressUpdate, db: Session = Depends(get_db)
):
    logger.info(f"Updating address with ID {address_id}: {address}")
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    update_data = address.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_address, key, value)
    db.commit()
    db.refresh(db_address)
    return db_address


# Endpoint to delete an address
@app.delete("/addresses/{address_id}", response_model=dict)
def delete_address(address_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting address with ID {address_id}")
    db_address = db.query(Address).filter(Address.id == address_id).first()
    if not db_address:
        raise HTTPException(status_code=404, detail="Address not found")
    db.delete(db_address)
    db.commit()
    return {"detail": "Address deleted"}


# Endpoint to get all addresses
@app.get("/addresses/", response_model=List[AddressInDB])
def get_addresses(db: Session = Depends(get_db)):
    logger.info("Fetching all addresses")
    return db.query(Address).all()


# Endpoint to get addresses within a certain distance from a location
@app.get("/addresses/within_distance/", response_model=List[AddressInDB])
def get_addresses_within_distance(latitude: float = Query(..., description="Latitude of the location"),
                                  longitude: float = Query(..., description="Longitude of the location"),
                                  distance: float = Query(..., description="Distance in kilometers"),
                                  db: Session = Depends(get_db)):
    logger.info(f"Fetching addresses within {distance} km from ({latitude}, {longitude})")
    addresses = db.query(Address).all()
    within_distance = [
        address for address in addresses
        if geodesic((latitude, longitude), (address.latitude, address.longitude)).km <= distance
    ]
    return within_distance
