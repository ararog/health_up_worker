from database import engine
from sqlmodel import (
    select,
    Session
)
from models import (
    Speciality,
)

def find_specilities_by_office_id(office_id) -> list[Speciality]: 
    with Session(engine) as session:
        statement = select(Speciality)
        statement = statement.where(Speciality.office_id == office_id)
        results = session.exec(statement)
        
        specialities: list[Speciality] = []
        for speciality in results:
            specialities.extend(speciality)
                    
        return specialities  
                
