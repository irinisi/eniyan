from fastapi import APIRouter, HTTPException

from app.models.schemas import Person
from app.services import people as people_service

router = APIRouter(prefix="/api/people", tags=["people"])


@router.get("", response_model=list[Person])
def list_people():
    return people_service.list_people()


@router.get("/{person_id}", response_model=Person)
def get_person(person_id: str):
    person = people_service.get_person(person_id)
    if person is None:
        raise HTTPException(status_code=404, detail="Person not found")
    return person
