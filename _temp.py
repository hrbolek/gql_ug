import asyncio
import os
import uuid
import datetime
import typing
from typing import List, Optional

import strawberry
from strawberry.fastapi import GraphQLRouter

from fastapi import FastAPI
from fastapi.responses import FileResponse

IDType = uuid.UUID
# ============================================================
# 0. Systémové prvky
# ============================================================

@strawberry.federation.interface(
    keys=["id"], description="""Entity representing an interface"""
)
class BaseGQLModel:
      
    id: typing.Optional[IDType] = strawberry.field(
        description="primary key", 
        default=None
        )
    lastchange: typing.Optional[datetime.datetime] = strawberry.field(
        description="timestamp", 
        default=None
        )
    created: typing.Optional[datetime.datetime] = strawberry.field(
        description="date & time of unit born", 
        default=None
        )
    createdby_id: typing.Optional[IDType] = strawberry.field(
        description="who created this entity", 
        default=None
        )
    changedby_id: typing.Optional[IDType] = strawberry.field(
        description="who changed this entity", 
        default=None
        )
    rbacobject_id: typing.Optional[IDType] = strawberry.field(
        description="rbac ruling object", 
        default=None
        )

T = typing.TypeVar("T")
@strawberry.type(description="""Represents an type category.
Reprezentuje categorii typu.""")
class Category(BaseGQLModel, typing.Generic[T]):
    name: Optional[str] = strawberry.field(description="""Name of the category
    Název kategorie""", default=None)

    types: List[T] = strawberry.field(description="types", default_factory=list)


@strawberry.type(description="""Represents an type.
Reprezentuje typ entity.""")
class Type(BaseGQLModel, typing.Generic[T]):
    name: Optional[str] = strawberry.field(description="""Name of the type
    Název typu""", default=None)
    description: Optional[str] = strawberry.field(description="""Description of the type
    Popis typu""", default=None)

    category: Optional[Category[T]] = strawberry.field(description="""Category""")
    entities: List[T] = strawberry.field(description="""Entities of this type
    Seznam entit tohoto typu""")

class MaterializedPath(typing.Generic[T]):
    async def parents_all(self) -> List[T]:
        path = self.path
        ids = [IDType(id) for id in path.split(";")]
        loader = T.getLoader()
        futures = (loader.load(id) for id in ids)
        values = await asyncio.gather(*futures)
        results = (T.from_dataclass(value) for value in values)
        return results
    
    async def descendads_all(self) -> List[T]:
        path = self.path
        loader = T.getLoader()
        rows = loader.load()
        results = (T.from_dataclass(row) for row in rows)
        return results

# ============================================================
# 1. Organizační struktura
# ============================================================

@strawberry.type(description="""Represents an organizational unit (e.g., university, faculty, department) with a hierarchical structure.
Reprezentuje organizační jednotku (např. univerzitu, fakultu, katedru) s hierarchickou strukturou.""")
class Group(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the group
    Unikátní identifikátor skupiny""")

    name: Optional[str] = strawberry.field(description="""Name of the group
    Název skupiny""", default=None)

    description: Optional[str] = strawberry.field(description="""Brief description of the group
    Krátký popis skupiny""", default=None)

    path: Optional[str] = strawberry.field(description="""Materialized path representing the hierarchy (e.g., '/University/Faculty/Department')
    Materializovaná cesta reprezentující hierarchii (např. '/Univerzita/Fakulta/Katedra')""", default=None)

    abbreviation: Optional[str] = strawberry.field(description="""Abbreviation of the group
    Zkratka skupiny""", default=None)

    parent: Optional["Group"] = strawberry.field(description="""Reference to the parent group
    Odkaz na nadřazenou skupinu""", default=None)

    groupType: Optional[Type["Group"]] = strawberry.field(description="""Reference to the group type
    Odkaz na typ skupiny""", default=None)

    memberships: List["Membership"] = strawberry.field(description="""List of memberships in the group
    Seznam členství ve skupině""", default_factory=list)

    subgroups: List["Group"] = strawberry.field(description="""List of subordinate groups
    Seznam podřízených skupin""", default_factory=list)

    roles: List["Role"] = strawberry.field(description="""List of roles assigned to the group
    Seznam rolí přiřazených ke skupině""", default_factory=list)

@strawberry.type(description="""Represents a physical person (e.g., student, teacher, administrator).
Reprezentuje fyzickou osobu (např. studenta, učitele, administrátora).""")
class User(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the person
    Unikátní identifikátor osoby""")

    firstName: Optional[str] = strawberry.field(description="""First name of the person
    Křestní jméno osoby""", default=None)

    familyName: Optional[str] = strawberry.field(description="""Last name of the person
    Příjmení osoby""", default=None)

    middleName: Optional[str] = strawberry.field(description="""Middle name of the person
    Prostřední jméno osoby""", default=None)

    email: Optional[str] = strawberry.field(description="""Email address of the person
    Emailová adresa osoby""", default=None)

    memberships: List["Membership"] = strawberry.field(description="""Memberships associated with the person
    Členství spojená s osobou""", default_factory=list)

    roles: List["Role"] = strawberry.field(description="""Roles assigned to the person
    Role přiřazené osobě""", default_factory=list)

    studies: List["StudyProgram"] = strawberry.field(description="""Study programs the person is involved in
    Studijní programy, ve kterých je osoba zapojena""", default_factory=list)


@strawberry.type(description="""Associates a person with a group, including the validity interval of the membership.
Spojuje osobu se skupinou, včetně intervalu platnosti členství.""")
class Membership(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the membership
    Unikátní identifikátor členství""")

    startDate: Optional[datetime.datetime] = strawberry.field(description="""Start date of membership validity
    Datum začátku platnosti členství""", default=None)

    endDate: Optional[datetime.datetime] = strawberry.field(description="""End date of membership validity
    Datum konce platnosti členství""", default=None)

    person: Optional["User"] = strawberry.field(description="""Reference to the associated person
    Odkaz na přidruženou osobu""", default=None)

    group: Optional["Group"] = strawberry.field(description="""Reference to the associated group
    Odkaz na přidruženou skupinu""", default=None)

@strawberry.type(description="""Represents a role assignment to a person within a group.
Reprezentuje přiřazení role osobě ve skupině.""")
class Role(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the role
    Unikátní identifikátor role""")

    startDate: Optional[datetime.datetime] = strawberry.field(description="""Start date of the role validity
    Datum začátku platnosti role""", default=None)

    endDate: Optional[datetime.datetime] = strawberry.field(description="""End date of the role validity
    Datum konce platnosti role""", default=None)

    group: Optional["Group"] = strawberry.field(description="""Group in which the role is assigned
    Skupina, ve které je role přiřazena""", default=None)

    person: Optional["User"] = strawberry.field(description="""Person to whom the role is assigned
    Osoba, které je role přiřazena""", default=None)

    roleType: Optional[Type["Role"]] = strawberry.field(description="""Reference to the type of role
    Odkaz na typ role""", default=None)


# @strawberry.type(description="""Defines a type of role (e.g., 'Rector', 'Dean', 'Manager', 'Examiner') and is further classified by a Category.
# Definuje typ role (např. 'Rektor', 'Děkan', 'Manažer', 'Zkoušející') a je dále klasifikován kategorií.""")
# class RoleType(BaseGQLModel):
#     id: IDType = strawberry.field(description="""Unique identifier of the role type
#     Unikátní identifikátor typu role""")

#     name: Optional[str] = strawberry.field(description="""Name of the role type
#     Název typu role""", default=None)

#     description: Optional[str] = strawberry.field(description="""Description of the role type
#     Popis typu role""", default=None)

#     category: Optional["RoleCategory"] = strawberry.field(description="""Category of the role type
#     Kategorie typu role""", default=None)

#     roles: List["Role"] = strawberry.field(description="""List of roles of this type
#     Seznam rolí tohoto typu""", default_factory=list)


@strawberry.type(description="""Represents a category for role types (e.g., 'administrative').
Reprezentuje kategorii pro typy rolí (např. 'administrativní').""")
class RoleCategory(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the category
    Unikátní identifikátor kategorie""")

    name: Optional[str] = strawberry.field(description="""Name of the category
    Název kategorie""", default=None)


# ============================================================
# 2. Události, lokality, dokumenty a administrativní úkoly
# ============================================================

@strawberry.type(description="""Represents an event. It may be a general event or an exam term.
The event includes a time interval, a materialized path, and an optional textual location.
Reprezentuje událost. Může se jednat o obecnou událost nebo zkouškový termín.
Událost obsahuje časový interval, materializovanou cestu a volitelnou textovou lokalitu.""")
class Event(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the event
    Unikátní identifikátor události""")

    name: Optional[str] = strawberry.field(description="""Name of the event
    Název události""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the event
    Popis události""", default=None)

    eventType: Optional["EventType"] = strawberry.field(description="""Reference to the event type
    Odkaz na typ události""", default=None)

    startDate: Optional[datetime.datetime] = strawberry.field(description="""Start date/time of the event
    Datum a čas začátku události""", default=None)

    endDate: Optional[datetime.datetime] = strawberry.field(description="""End date/time of the event
    Datum a čas konce události""", default=None)

    path: Optional[str] = strawberry.field(description="""Materialized path in the event hierarchy (e.g., '/Semester/Week1/Lesson3')
    Materializovaná cesta v hierarchii událostí (např. '/Semestr/Týden1/Lekce3')""", default=None)

    location: Optional[str] = strawberry.field(description="""Textual description of the location if Facility is not defined
    Textový popis lokality, pokud není definováno zařízení""", default=None)

    facility: Optional["Facility"] = strawberry.field(description="""Reference to the facility where the event takes place
    Odkaz na zařízení, kde se událost koná""", default=None)

    parent: Optional["Event"] = strawberry.field(description="""Reference to the parent event
    Odkaz na nadřazenou událost""", default=None)

    documents: List["Document"] = strawberry.field(description="""Documents associated with the event
    Dokumenty spojené s událostí""", default_factory=list)

    subevents: List["Event"] = strawberry.field(description="""List of subevents
    Seznam podudálostí""", default_factory=list)

    invitations: List["Invitation"] = strawberry.field(description="""List of invitations for the event
    Seznam pozvánek na událost""", default_factory=list)


@strawberry.type(description="""Defines the type of an event (e.g., 'general', 'examTerm').
Definuje typ události (např. 'obecná', 'zkouškový termín').""")
class EventType(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the event type
    Unikátní identifikátor typu události""")

    name: Optional[str] = strawberry.field(description="""Name of the event type
    Název typu události""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the event type
    Popis typu události""", default=None)

@strawberry.type(description="""Represents an invitation to an event, recording the status and sent timestamp.
Reprezentuje pozvánku na událost, zaznamenává stav a čas odeslání.""")
class Invitation(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the invitation
    Unikátní identifikátor pozvánky""")

    status: Optional[str] = strawberry.field(description="""Status of the invitation (e.g., accepted, declined, excused)
    Stav pozvánky (např. přijatá, odmítnutá, omluvená)""", default=None)

    sentAt: Optional[datetime.datetime] = strawberry.field(description="""Timestamp when the invitation was sent
    Časové razítko odeslání pozvánky""", default=None)

    event: Optional["Event"] = strawberry.field(description="""Reference to the event
    Odkaz na událost""", default=None)

    person: Optional["User"] = strawberry.field(description="""Reference to the person receiving the invitation
    Odkaz na osobu, která pozvánku obdržela""", default=None)


@strawberry.type(description="""Represents a facility (physical or virtual location) with a full label and managed by an organizational group.
Reprezentuje zařízení (fyzické nebo virtuální místo) s úplným označením, spravované organizační skupinou.""")
class Facility(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the facility
    Unikátní identifikátor zařízení""")

    name: Optional[str] = strawberry.field(description="""Name of the facility
    Název zařízení""", default=None)

    address: Optional[str] = strawberry.field(description="""Address or description of the facility
    Adresa nebo popis zařízení""", default=None)

    label: Optional[str] = strawberry.field(description="""Full name of the facility (e.g., 'Učebna 101')
    Úplné označení zařízení (např. 'Učebna 101')""", default=None)

    parent: Optional["Facility"] = strawberry.field(description="""Reference to the parent facility
    Odkaz na nadřazené zařízení""", default=None)

    subfacilities: List["Facility"] = strawberry.field(description="""List of subordinate facilities
    Seznam podřízených zařízení""", default_factory=list)

    facilityType: Optional[Type["Facility"]] = strawberry.field(description="""Facility type
    typ zařízení""", default=None)

    events: List["Event"] = strawberry.field(description="""List of events taking place at this facility
    Seznam událostí konaných v tomto zařízení""", default_factory=list)

    group: Optional["Group"] = strawberry.field(description="""Organizational group responsible for managing the facility
    Organizační skupina odpovědná za správu zařízení""", default=None)


@strawberry.type(description="""Represents a document with hierarchical organization, stored content and MIME type.
Reprezentuje dokument s hierarchickou organizací, uloženým obsahem a typem MIME.""")
class Document(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the document
    Unikátní identifikátor dokumentu""")

    title: Optional[str] = strawberry.field(description="""Title of the document
    Název dokumentu""", default=None)

    content: Optional[str] = strawberry.field(description="""Textual content of the document
    Textový obsah dokumentu""", default=None)

    created: Optional[datetime.datetime] = strawberry.field(description="""Creation datetime of the document
    Datum a čas vytvoření dokumentu""", default=None)

    path: Optional[str] = strawberry.field(description="""Materialized path of the document in the hierarchy
    Materializovaná cesta dokumentu v hierarchii""", default=None)

    fileContent: Optional[str] = strawberry.field(description="""Stored file content (e.g., base64 encoded)
    Uložený obsah souboru (např. kódovaný v base64)""", default=None)

    mimeType: Optional[str] = strawberry.field(description="""MIME type of the document
    MIME typ dokumentu""", default=None)

    event: Optional["Event"] = strawberry.field(description="""Reference to the associated event
    Odkaz na přidruženou událost""", default=None)

    parent: Optional["Document"] = strawberry.field(description="""Reference to the parent document
    Odkaz na nadřazený dokument""", default=None)

    subdocuments: List["Document"] = strawberry.field(description="""List of subordinate documents
    Seznam podřízených dokumentů""", default_factory=list)

    documentType: Optional[Type["Facility"]] = strawberry.field(description="""Document type
    typ dokumentu""", default=None)


# ============================================================
# 3. Studium
# ============================================================

@strawberry.type(description="""Represents a study program (e.g., Cybersecurity).
Reprezentuje studijní program (např. Kybernetická bezpečnost).""")
class StudyProgram(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the study program
    Unikátní identifikátor studijního programu""")

    name: Optional[str] = strawberry.field(description="""Title of the study program
    Název studijního programu""", default=None)

    level: Optional[str] = strawberry.field(description="""Level of study (e.g., Bachelor's, Master's)
    Úroveň studia (např. bakalářské, magisterské)""", default=None)

    qualification: Optional[str] = strawberry.field(description="""Awarded qualification
    Udělovaná kvalifikace""", default=None)

    duration: Optional[float] = strawberry.field(description="""Duration of the program in years
    Délka programu v letech""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the study program
    Popis studijního programu""", default=None)

    university: Optional["Group"] = strawberry.field(description="""University offering the program
    Univerzita nabízející program""", default=None)

    group: Optional["Group"] = strawberry.field(description="""Organizational group responsible for the program
    Organizační skupina odpovědná za program""", default=None)

    accreditations: List["Accreditation"] = strawberry.field(description="""List of accreditation decisions
    Seznam akreditačních rozhodnutí""", default_factory=list)

    subjects: List["Subject"] = strawberry.field(description="""List of subjects in the program
    Seznam předmětů v programu""", default_factory=list)


@strawberry.type(description="""Represents an accreditation decision for a study program.
Reprezentuje akreditační rozhodnutí pro studijní program.""")
class Accreditation(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the accreditation
    Unikátní identifikátor akreditace""")

    decisionNumber: Optional[str] = strawberry.field(description="""Accreditation decision number
    Číslo akreditačního rozhodnutí""", default=None)

    decisionDate: Optional[datetime.datetime] = strawberry.field(description="""Date of the decision
    Datum rozhodnutí""", default=None)

    validFrom: Optional[datetime.datetime] = strawberry.field(description="""Validity start date
    Datum začátku platnosti""", default=None)

    validTo: Optional[datetime.datetime] = strawberry.field(description="""Validity end date
    Datum konce platnosti""", default=None)

    notes: Optional[str] = strawberry.field(description="""Additional notes
    Další poznámky""", default=None)

    studyProgram: Optional["StudyProgram"] = strawberry.field(description="""Reference to the study program
    Odkaz na studijní program""", default=None)

    accreditationBody: Optional["AccreditationBody"] = strawberry.field(description="""Reference to the accreditation body
    Odkaz na akreditační orgán""", default=None)


@strawberry.type(description="""Represents the accreditation body.
Reprezentuje akreditační orgán.""")
class AccreditationBody(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the accreditation body
    Unikátní identifikátor akreditačního orgánu""")

    name: Optional[str] = strawberry.field(description="""Name of the accreditation body
    Název akreditačního orgánu""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the accreditation body
    Popis akreditačního orgánu""", default=None)

    accreditations: List["Accreditation"] = strawberry.field(description="""List of accreditation decisions granted by this body
    Seznam akreditačních rozhodnutí udělených tímto orgánem""", default_factory=list)


@strawberry.type(description="""Represents a subject within a study program.
Reprezentuje předmět v rámci studijního programu.""")
class Subject(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the subject
    Unikátní identifikátor předmětu""")

    name: Optional[str] = strawberry.field(description="""Name of the subject
    Název předmětu""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the subject
    Popis předmětu""", default=None)

    type: Optional[str] = strawberry.field(description="""Category of the subject (e.g., 'regular', 'admission', 'stateFinal')
    Kategorie předmětu (např. 'běžný', 'přijímací', 'státní závěrečná zkouška')""", default=None)

    studyProgram: Optional["StudyProgram"] = strawberry.field(description="""Reference to the study program
    Odkaz na studijní program""", default=None)

    group: Optional["Group"] = strawberry.field(description="""Organizational group responsible for the subject
    Organizační skupina odpovědná za předmět""", default=None)

    semesters: List["Semester"] = strawberry.field(description="""List of semesters in which the subject is taught
    Seznam semestrů, ve kterých je předmět vyučován""", default_factory=list)

@strawberry.type(description="""Represents a semester for a subject, including classification method and credits.
Reprezentuje semestr pro předmět, včetně metody klasifikace a kreditů.""")
class Semester(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the semester
    Unikátní identifikátor semestru""")

    term: Optional[str] = strawberry.field(description="""Semester term (e.g., Fall, Spring)
    Období semestru (např. podzim, jaro)""", default=None)

    absoluteOrder: Optional[int] = strawberry.field(description="""Expected semester of teaching
    Očekávaný semestr vyučování""", default=None)

    order: Optional[int] = strawberry.field(description="""Order of the semester
    Rok semestru""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the semester
    Popis semestru""", default=None)

    classificationMethod: Optional[str] = strawberry.field(description="""Method of classification (e.g., weighted)
    Metoda klasifikace (např. vážená)""", default=None)

    credits: Optional[float] = strawberry.field(description="""Number of credits
    Počet kreditů""", default=None)

    subject: Optional["Subject"] = strawberry.field(description="""Reference to the subject
    Odkaz na předmět""", default=None)

    studyPlans: List["StudyPlan"] = strawberry.field(description="""List of study plans for this semester
    Seznam studijních plánů pro tento semestr""", default_factory=list)

    prerequisiteSemesters: List["Semester"] = strawberry.field(
        description="""Semesters that must precede this semester.
    Semestry, které musí předcházet tomuto semestru.""",
        default_factory=list
    )

    dependentSemesters: List["Semester"] = strawberry.field(
        description="""Semesters for which this semester is a prerequisite.
    Semestry, pro které je tento semestr prerekvizitou.""",
        default_factory=list
    )    

@strawberry.type(description="""Represents a thematic block within a semester, grouping lessons.
Reprezentuje tematický blok v rámci semestru, sdružující lekce.""")
class Topic(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the topic
    Unikátní identifikátor tématu""")

    name: Optional[str] = strawberry.field(description="""Name of the topic
    Název tématu""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the topic
    Popis tématu""", default=None)

    semester: Optional["Semester"] = strawberry.field(description="""Reference to the semester
    Odkaz na semestr""", default=None)

    lessons: List["Lesson"] = strawberry.field(description="""List of lessons in this topic
    Seznam lekcí v tomto tématu""", default_factory=list)


@strawberry.type(description="""Represents a study plan for a subject in a given semester, including a schedule and a classification scheme.
Reprezentuje studijní plán pro předmět v daném semestru, včetně rozvrhu a klasifikačního schématu.""")
class StudyPlan(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the study plan
    Unikátní identifikátor studijního plánu""")

    description: Optional[str] = strawberry.field(description="""Description or title of the study plan
    Popis nebo název studijního plánu""", default=None)

    semester: Optional["Semester"] = strawberry.field(description="""Reference to the semester
    Odkaz na semestr""", default=None)

    classificationScheme: Optional["ClassificationScheme"] = strawberry.field(description="""Classification scheme for this study plan
    Klasifikační schéma pro tento studijní plán""", default=None)

    scheduledLessons: List["Lesson"] = strawberry.field(description="""List of scheduled lessons
    Seznam naplánovaných lekcí""", default_factory=list)


@strawberry.type(description="""Defines the classification scheme for a subject in a given semester.
Definuje klasifikační schéma pro předmět v daném semestru.""")
class ClassificationScheme(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the classification scheme
    Unikátní identifikátor klasifikačního schématu""")

    name: Optional[str] = strawberry.field(description="""Name of the classification scheme
    Název klasifikačního schématu""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the classification scheme
    Popis klasifikačního schématu""", default=None)

    semester: Optional["Semester"] = strawberry.field(description="""Reference to the semester
    Odkaz na semestr""", default=None)

    parts: List["ClassificationPart"] = strawberry.field(description="""List of classification parts in the scheme
    Seznam klasifikačních částí v tomto schématu""", default_factory=list)


@strawberry.type(description="""Defines an individual part of the classification scheme with a maximum point value.
Definuje jednotlivou část klasifikačního schématu s maximální bodovou hodnotou.""")
class ClassificationPart(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the classification part
    Unikátní identifikátor klasifikační části""")

    name: Optional[str] = strawberry.field(description="""Name of the classification part
    Název klasifikační části""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the classification part
    Popis klasifikační části""", default=None)

    maxPoints: Optional[float] = strawberry.field(description="""Maximum points achievable
    Maximální dosažitelný počet bodů""", default=None)

    classificationScheme: Optional["ClassificationScheme"] = strawberry.field(description="""Reference to the classification scheme
    Odkaz na klasifikační schéma""", default=None)

    responsible: Optional["User"] = strawberry.field(description="""Responsible person for this part
    Odpovědná osoba za tuto část""", default=None)

@strawberry.type(description="""Represents a lesson scheduled in a study plan.
Reprezentuje lekci naplánovanou ve studijním plánu.""")
class Lesson(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the lesson
    Unikátní identifikátor lekce""")

    content: Optional[str] = strawberry.field(description="""Content of the lesson
    Obsah lekce""", default=None)

    length: Optional[float] = strawberry.field(description="""Length of the lesson in arbitrary units
    Délka lekce v libovolných jednotkách""", default=None)

    lessonType: Optional[Type["Lesson"]] = strawberry.field(description="""Type of lesson (e.g., lecture, exercise)
    Typ lekce (např. přednáška, cvičení)""", default=None)

    event: Optional["Event"] = strawberry.field(description="""Event representing the lesson instance
    Událost reprezentující instanci lekce""", default=None)

    studyPlan: Optional["StudyPlan"] = strawberry.field(description="""Reference to the study plan
    Odkaz na studijní plán""", default=None)

    instructors: List["User"] = strawberry.field(description="""List of instructors for the lesson
    Seznam vyučujících pro tuto lekci""", default_factory=list)

    groups: List["Group"] = strawberry.field(description="""List of groups involved in the lesson
    Seznam skupin zapojených do lekce""", default_factory=list)

    relatedLessons: List["Lesson"] = strawberry.field(description="""List of related lessons
    Seznam souvisejících lekcí""", default_factory=list)


@strawberry.type(description="""Represents a student enrolled in a study program.
Reprezentuje studenta zapsaného do studijního programu.""")
class Student(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the student record
    Unikátní identifikátor studijního záznamu""")

    person: Optional["User"] = strawberry.field(description="""Reference to the person
    Odkaz na osobu""", default=None)

    studyProgram: Optional["StudyProgram"] = strawberry.field(description="""Reference to the study program
    Odkaz na studijní program""", default=None)

    state: Optional["State"] = strawberry.field(description="""State of the student
    Stav studenta""", default=None)


@strawberry.type(description="""Represents the state (e.g. of a student: active, interrupted, applicant).
Reprezentuje stav (např. studenta: aktivní, přerušené, uchazeč).""")
class State(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the student state
    Unikátní identifikátor stavu""")

    name: Optional[str] = strawberry.field(description="""Name of the state
    Název stavu""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the state
    Popis stavu""", default=None)


@strawberry.type(description="""Represents an evaluation given to a student.
Reprezentuje hodnocení udělené studentovi.""")
class Evaluation(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the evaluation
    Unikátní identifikátor hodnocení""")

    grade: Optional[str] = strawberry.field(description="""Grade value (e.g., A–F, pass/fail)
    Hodnota známky (např. A–F, prospěl/neprospěl)""", default=None)

    attempt: Optional[int] = strawberry.field(description="""Attempt number
    Číslo pokusu""", default=None)

    points: Optional[float] = strawberry.field(description="""Points achieved
    Počet dosažených bodů""", default=None)

    passed: Optional[bool] = strawberry.field(description="""Whether the evaluation is passing
    Zda je hodnocení úspěšné""", default=None)

    student: Optional["Student"] = strawberry.field(description="""Reference to the student
    Odkaz na studenta""", default=None)

    subject: Optional["Subject"] = strawberry.field(description="""Reference to the subject
    Odkaz na předmět""", default=None)

    semester: Optional["Semester"] = strawberry.field(description="""Reference to the semester
    Odkaz na semestr""", default=None)

    classificationPart: Optional["ClassificationPart"] = strawberry.field(description="""Reference to the classification part
    Odkaz na klasifikační část""", default=None)

    examEvent: Optional["Event"] = strawberry.field(description="""Event representing the evaluation term
    Událost reprezentující termín hodnocení""", default=None)

    admissionProcess: Optional["AdmissionProcess"] = strawberry.field(description="""Reference to the admission process
    Odkaz na přijímací řízení""", default=None)

    evaluationType: Optional["EvaluationType"] = strawberry.field(description="""Reference to the evaluation type
    Odkaz na typ hodnocení""", default=None)

    examComponents: List["ExamComponent"] = strawberry.field(description="""List of exam components
    Seznam složek zkoušky""", default_factory=list)

@strawberry.type(description="""Defines the evaluation type or context (e.g., 'semester', 'admission', 'stateFinal').
Definuje typ nebo kontext hodnocení (např. 'semestrální', 'přijímací', 'státní závěrečná').""")
class EvaluationType(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the evaluation type
    Unikátní identifikátor typu hodnocení""")

    name: Optional[str] = strawberry.field(description="""Name of the evaluation type
    Název typu hodnocení""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the evaluation type
    Popis typu hodnocení""", default=None)

    evaluations: List["Evaluation"] = strawberry.field(description="""List of evaluations of this type
    Seznam hodnocení tohoto typu""", default_factory=list)


@strawberry.type(description="""Represents the admission process for a study program.
Reprezentuje přijímací řízení pro studijní program.""")
class AdmissionProcess(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the admission process
    Unikátní identifikátor přijímacího řízení""")

    applicationStart: Optional[datetime.datetime] = strawberry.field(description="""Start date of the admission process
    Datum zahájení přijímacího řízení""", default=None)

    applicationDeadline: Optional[datetime.datetime] = strawberry.field(description="""Deadline for applications
    Termín pro podání přihlášek""", default=None)

    resultsAnnouncement: Optional[datetime.datetime] = strawberry.field(description="""Date when results are announced
    Datum zveřejnění výsledků""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the admission process
    Popis přijímacího řízení""", default=None)

    studyProgram: Optional["StudyProgram"] = strawberry.field(description="""Reference to the study program
    Odkaz na studijní program""", default=None)

    admissionExams: List["Exam"] = strawberry.field(description="""List of exams in the admission process
    Seznam zkoušek v přijímacím řízení""", default_factory=list)

    requiredDocuments: List["Document"] = strawberry.field(description="""List of documents required for the process
    Seznam dokumentů vyžadovaných v procesu""", default_factory=list)

    admissionApplications: List["AdmissionApplication"] = strawberry.field(description="""List of submitted applications
    Seznam podaných přihlášek""", default_factory=list)


@strawberry.type(description="""Represents an application submitted by a candidate for admission.
Reprezentuje přihlášku podanou uchazečem o přijetí.""")
class AdmissionApplication(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the admission application
    Unikátní identifikátor přihlášky""")

    applicationDate: Optional[datetime.datetime] = strawberry.field(description="""Date of application submission
    Datum podání přihlášky""", default=None)

    status: Optional[str] = strawberry.field(description="""Status of the application
    Stav přihlášky""", default=None)

    comments: Optional[str] = strawberry.field(description="""Additional comments
    Další poznámky""", default=None)

    student: Optional["Student"] = strawberry.field(description="""Reference to the applicant
    Odkaz na uchazeče""", default=None)

    admissionProcess: Optional["AdmissionProcess"] = strawberry.field(description="""Reference to the admission process
    Odkaz na přijímací řízení""", default=None)

    submittedDocuments: List["Document"] = strawberry.field(description="""List of documents submitted with the application
    Seznam dokumentů podaných s přihláškou""", default_factory=list)


@strawberry.type(description="""Unifies exam entities for special subjects (admission, state finals) as an event.
Sjednocuje zkouškové entity pro speciální předměty (přijímací, státní závěrečné) jako událost.""")
class Exam(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the exam
    Unikátní identifikátor zkoušky""")

    name: Optional[str] = strawberry.field(description="""Name of the exam
    Název zkoušky""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the exam
    Popis zkoušky""", default=None)

    event: Optional["Event"] = strawberry.field(description="""Reference to the related event
    Odkaz na související událost""", default=None)


@strawberry.type(description="""Defines a component of an exam with min/max score values and provides results for all students.
Definuje složku zkoušky s minimální/maximální bodovou hodnotou a poskytuje výsledky pro všechny studenty.""")
class ExamComponent(BaseGQLModel):
    id: IDType = strawberry.field(description="""Unique identifier of the exam component
    Unikátní identifikátor složky zkoušky""")

    name: Optional[str] = strawberry.field(description="""Name of the exam component
    Název složky zkoušky""", default=None)

    description: Optional[str] = strawberry.field(description="""Description of the exam component
    Popis složky zkoušky""", default=None)

    minScore: Optional[float] = strawberry.field(description="""Minimum required score
    Minimální požadovaný počet bodů""", default=None)

    maxScore: Optional[float] = strawberry.field(description="""Maximum achievable score
    Maximální dosažitelný počet bodů""", default=None)

    exam: Optional["Exam"] = strawberry.field(description="""Reference to the exam
    Odkaz na zkoušku""", default=None)

    results: List["Evaluation"] = strawberry.field(description="""List of evaluation results for this component
    Seznam výsledků hodnocení pro tuto složku""", default_factory=list)
# ============================================================
# 4. GraphQL API a konfigurace FastAPI
# ============================================================

@strawberry.type(description="""Root query for accessing various entities.
Kořenový dotaz pro přístup k různým entitám.""")
class Query:
    user_by_id: Optional["User"] = strawberry.field(description="""Fetch a person by ID.
    Získání osoby podle ID.""", default=None)

    group_by_id: Optional["Group"] = strawberry.field(description="""Fetch a group by ID.
    Získání skupiny podle ID.""", default=None)

    study_program_by_id: Optional["StudyProgram"] = strawberry.field(description="""Fetch a study program by ID.
    Získání studijního programu podle ID.""", default=None)

    event_by_id: Optional["Event"] = strawberry.field(description="""Fetch an event by ID.
    Získání události podle ID.""", default=None)

    document_by_id: Optional["Document"] = strawberry.field(description="""Fetch a document by ID.
    Získání dokumentu podle ID.""", default=None)

    evaluation_by_id: Optional["Evaluation"] = strawberry.field(description="""Fetch an evaluation by ID.
    Získání hodnocení podle ID.""", default=None)


# Vytvoření GraphQL schématu
schema = strawberry.federation.Schema(query=Query)

# Inicializace FastAPI aplikace
app = FastAPI()

# Připojení GraphQL endpointu
graphql_app = GraphQLRouter(schema)
app.include_router(graphql_app, prefix="/gql")


# Endpoint pro Voyager GraphQL vizualizaci
@app.get("/voyager", response_class=FileResponse)
async def graphiql():
    """Returns the Voyager GraphQL visualization tool.
    Vrací nástroj Voyager pro vizualizaci GraphQL schématu."""
    realpath = os.path.realpath("./voyager.html")
    return realpath

MD_FILE_PATH = "./graphql_schema.md"

@app.get("/md")
async def get_markdown():
    """Vrací vygenerovanou GraphQL dokumentaci jako Markdown soubor.
    Returns the generated GraphQL schema documentation in Markdown format."""
    return FileResponse(MD_FILE_PATH, media_type="text/markdown", filename="graphql_schema.md")


def extract_type_name(field_type):
    """Vrátí správný název typu včetně podpory List[], NonNull! a dalších.
    Returns the correct type name, including support for List[], NonNull!, and more."""

    while field_type:
        kind = field_type.get("kind", "")
        name = field_type.get("name")

        if kind == "LIST" and field_type.get("ofType"):
            return f"List[{extract_type_name(field_type['ofType'])}]"

        if kind == "NON_NULL" and field_type.get("ofType"):
            return f"{extract_type_name(field_type['ofType'])}!"

        if name:
            return name  # Jakmile najdeme platný název, vrátíme ho

        field_type = field_type.get("ofType")  # Posuneme se hlouběji

    return "Unknown"

def generate_markdown_from_schema():   
    """Generuje Markdown dokumentaci z introspektovaného GraphQL schématu.
    Generates Markdown documentation from the introspected GraphQL schema."""

    INTROSPECTION_QUERY = """
query IntrospectionQuery {
  __schema {
    types {
      name
      description
      fields {
        name
        description
        type {
          name
          kind
          ofType {
            name
            kind
            ofType {
              name
              kind
              ofType {
                name
                kind
                ofType {
                  name
                  kind
                }
              }
            }
          }
        }
      }
    }
  }
}
    """    

    # Spustíme introspekční dotaz přímo nad objektem `schema`
    result = schema.execute_sync(INTROSPECTION_QUERY)
    
    if result.errors:
        raise Exception(f"GraphQL introspection failed: {result.errors}")

    schema_data = result.data

    markdown_content = "# GraphQL API Documentation\n\n"

    for gql_type in schema_data["__schema"]["types"]:
        if gql_type["name"].startswith("__"):  # Přeskakujeme interní GraphQL typy
            continue

        description = gql_type["description"] or "No description available."
        markdown_content += f"## {gql_type['name']}\n\n"
        markdown_content += description.replace("\n", "  \n") + "\n\n"  # Zachování zalomení řádků

        if gql_type.get("fields"):
            markdown_content += "### Fields:\n\n"
            for field in gql_type["fields"]:
                field_name = field["name"]
                field_desc = (field["description"] or "No description available.").replace("\n", "  \n")
                field_type = extract_type_name(field["type"])
                
                markdown_content += f"- **{field_name}** (`{field_type}`): \n\n    {field_desc}\n"

        markdown_content += "\n---\n"

    return markdown_content

markdown_content = generate_markdown_from_schema()
with open(MD_FILE_PATH, "w", encoding="utf-8") as md_file:
    md_file.write(markdown_content)