# GraphQL API Documentation

## _Any

No description available.


---
## Query

No description available.

### Fields:

- **_service** (`_Service!`): 

    No description available.
- **userById** (`User`): 

    Fetch a person by ID.  
    Získání osoby podle ID.
- **groupById** (`Group`): 

    Fetch a group by ID.  
    Získání skupiny podle ID.
- **studyProgramById** (`StudyProgram`): 

    Fetch a study program by ID.  
    Získání studijního programu podle ID.
- **eventById** (`Event`): 

    Fetch an event by ID.  
    Získání události podle ID.
- **documentById** (`Document`): 

    Fetch a document by ID.  
    Získání dokumentu podle ID.
- **evaluationById** (`Evaluation`): 

    Fetch an evaluation by ID.  
    Získání hodnocení podle ID.

---
## _Service

No description available.

### Fields:

- **sdl** (`String!`): 

    No description available.

---
## String

The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text.


---
## User

Represents a physical person (e.g., student, teacher, administrator).  
Reprezentuje fyzickou osobu (např. studenta, učitele, administrátora).

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the person  
    Unikátní identifikátor osoby
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **firstName** (`String`): 

    First name of the person  
    Křestní jméno osoby
- **familyName** (`String`): 

    Last name of the person  
    Příjmení osoby
- **middleName** (`String`): 

    Middle name of the person  
    Prostřední jméno osoby
- **email** (`String`): 

    Email address of the person  
    Emailová adresa osoby
- **memberships** (`List[Membership!]!`): 

    Memberships associated with the person  
    Členství spojená s osobou
- **roles** (`List[Role!]!`): 

    Roles assigned to the person  
    Role přiřazené osobě
- **studies** (`List[StudyProgram!]!`): 

    Study programs the person is involved in  
    Studijní programy, ve kterých je osoba zapojena

---
## BaseGQLModel

Entity representing an interface

### Fields:

- **id** (`UUID`): 

    primary key
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object

---
## UUID

No description available.


---
## DateTime

Date with time (isoformat)


---
## Membership

Associates a person with a group, including the validity interval of the membership.  
Spojuje osobu se skupinou, včetně intervalu platnosti členství.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the membership  
    Unikátní identifikátor členství
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **startDate** (`DateTime`): 

    Start date of membership validity  
    Datum začátku platnosti členství
- **endDate** (`DateTime`): 

    End date of membership validity  
    Datum konce platnosti členství
- **person** (`User`): 

    Reference to the associated person  
    Odkaz na přidruženou osobu
- **group** (`Group`): 

    Reference to the associated group  
    Odkaz na přidruženou skupinu

---
## Group

Represents an organizational unit (e.g., university, faculty, department) with a hierarchical structure.  
Reprezentuje organizační jednotku (např. univerzitu, fakultu, katedru) s hierarchickou strukturou.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the group  
    Unikátní identifikátor skupiny
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the group  
    Název skupiny
- **description** (`String`): 

    Brief description of the group  
    Krátký popis skupiny
- **path** (`String`): 

    Materialized path representing the hierarchy (e.g., '/University/Faculty/Department')  
    Materializovaná cesta reprezentující hierarchii (např. '/Univerzita/Fakulta/Katedra')
- **abbreviation** (`String`): 

    Abbreviation of the group  
    Zkratka skupiny
- **parent** (`Group`): 

    Reference to the parent group  
    Odkaz na nadřazenou skupinu
- **groupType** (`GroupType`): 

    Reference to the group type  
    Odkaz na typ skupiny
- **memberships** (`List[Membership!]!`): 

    List of memberships in the group  
    Seznam členství ve skupině
- **subgroups** (`List[Group!]!`): 

    List of subordinate groups  
    Seznam podřízených skupin
- **roles** (`List[Role!]!`): 

    List of roles assigned to the group  
    Seznam rolí přiřazených ke skupině

---
## GroupType

Represents an type.  
Reprezentuje typ entity.

### Fields:

- **id** (`UUID`): 

    primary key
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the type  
    Název typu
- **description** (`String`): 

    Description of the type  
    Popis typu
- **category** (`GroupCategory`): 

    Category
- **entities** (`List[Group!]!`): 

    Entities of this type  
    Seznam entit tohoto typu

---
## GroupCategory

Represents an type category.  
Reprezentuje categorii typu.

### Fields:

- **id** (`UUID`): 

    primary key
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the category  
    Název kategorie
- **types** (`List[Group!]!`): 

    types

---
## Role

Represents a role assignment to a person within a group.  
Reprezentuje přiřazení role osobě ve skupině.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the role  
    Unikátní identifikátor role
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **startDate** (`DateTime`): 

    Start date of the role validity  
    Datum začátku platnosti role
- **endDate** (`DateTime`): 

    End date of the role validity  
    Datum konce platnosti role
- **group** (`Group`): 

    Group in which the role is assigned  
    Skupina, ve které je role přiřazena
- **person** (`User`): 

    Person to whom the role is assigned  
    Osoba, které je role přiřazena
- **roleType** (`RoleType`): 

    Reference to the type of role  
    Odkaz na typ role

---
## RoleType

Represents an type.  
Reprezentuje typ entity.

### Fields:

- **id** (`UUID`): 

    primary key
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the type  
    Název typu
- **description** (`String`): 

    Description of the type  
    Popis typu
- **category** (`RoleCategory`): 

    Category
- **entities** (`List[Role!]!`): 

    Entities of this type  
    Seznam entit tohoto typu

---
## RoleCategory

Represents an type category.  
Reprezentuje categorii typu.

### Fields:

- **id** (`UUID`): 

    primary key
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the category  
    Název kategorie
- **types** (`List[Role!]!`): 

    types

---
## StudyProgram

Represents a study program (e.g., Cybersecurity).  
Reprezentuje studijní program (např. Kybernetická bezpečnost).

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the study program  
    Unikátní identifikátor studijního programu
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Title of the study program  
    Název studijního programu
- **level** (`String`): 

    Level of study (e.g., Bachelor's, Master's)  
    Úroveň studia (např. bakalářské, magisterské)
- **qualification** (`String`): 

    Awarded qualification  
    Udělovaná kvalifikace
- **duration** (`Float`): 

    Duration of the program in years  
    Délka programu v letech
- **description** (`String`): 

    Description of the study program  
    Popis studijního programu
- **university** (`Group`): 

    University offering the program  
    Univerzita nabízející program
- **group** (`Group`): 

    Organizational group responsible for the program  
    Organizační skupina odpovědná za program
- **accreditations** (`List[Accreditation!]!`): 

    List of accreditation decisions  
    Seznam akreditačních rozhodnutí
- **subjects** (`List[Subject!]!`): 

    List of subjects in the program  
    Seznam předmětů v programu

---
## Float

The `Float` scalar type represents signed double-precision fractional values as specified by [IEEE 754](https://en.wikipedia.org/wiki/IEEE_floating_point).


---
## Accreditation

Represents an accreditation decision for a study program.  
Reprezentuje akreditační rozhodnutí pro studijní program.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the accreditation  
    Unikátní identifikátor akreditace
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **decisionNumber** (`String`): 

    Accreditation decision number  
    Číslo akreditačního rozhodnutí
- **decisionDate** (`DateTime`): 

    Date of the decision  
    Datum rozhodnutí
- **validFrom** (`DateTime`): 

    Validity start date  
    Datum začátku platnosti
- **validTo** (`DateTime`): 

    Validity end date  
    Datum konce platnosti
- **notes** (`String`): 

    Additional notes  
    Další poznámky
- **studyProgram** (`StudyProgram`): 

    Reference to the study program  
    Odkaz na studijní program
- **accreditationBody** (`AccreditationBody`): 

    Reference to the accreditation body  
    Odkaz na akreditační orgán

---
## AccreditationBody

Represents the accreditation body.  
Reprezentuje akreditační orgán.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the accreditation body  
    Unikátní identifikátor akreditačního orgánu
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the accreditation body  
    Název akreditačního orgánu
- **description** (`String`): 

    Description of the accreditation body  
    Popis akreditačního orgánu
- **accreditations** (`List[Accreditation!]!`): 

    List of accreditation decisions granted by this body  
    Seznam akreditačních rozhodnutí udělených tímto orgánem

---
## Subject

Represents a subject within a study program.  
Reprezentuje předmět v rámci studijního programu.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the subject  
    Unikátní identifikátor předmětu
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the subject  
    Název předmětu
- **description** (`String`): 

    Description of the subject  
    Popis předmětu
- **type** (`String`): 

    Category of the subject (e.g., 'regular', 'admission', 'stateFinal')  
    Kategorie předmětu (např. 'běžný', 'přijímací', 'státní závěrečná zkouška')
- **studyProgram** (`StudyProgram`): 

    Reference to the study program  
    Odkaz na studijní program
- **group** (`Group`): 

    Organizational group responsible for the subject  
    Organizační skupina odpovědná za předmět
- **semesters** (`List[Semester!]!`): 

    List of semesters in which the subject is taught  
    Seznam semestrů, ve kterých je předmět vyučován

---
## Semester

Represents a semester for a subject, including classification method and credits.  
Reprezentuje semestr pro předmět, včetně metody klasifikace a kreditů.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the semester  
    Unikátní identifikátor semestru
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **term** (`String`): 

    Semester term (e.g., Fall, Spring)  
    Období semestru (např. podzim, jaro)
- **absoluteOrder** (`Int`): 

    Expected semester of teaching  
    Očekávaný semestr vyučování
- **order** (`Int`): 

    Order of the semester  
    Rok semestru
- **description** (`String`): 

    Description of the semester  
    Popis semestru
- **classificationMethod** (`String`): 

    Method of classification (e.g., weighted)  
    Metoda klasifikace (např. vážená)
- **credits** (`Float`): 

    Number of credits  
    Počet kreditů
- **subject** (`Subject`): 

    Reference to the subject  
    Odkaz na předmět
- **studyPlans** (`List[StudyPlan!]!`): 

    List of study plans for this semester  
    Seznam studijních plánů pro tento semestr
- **prerequisiteSemesters** (`List[Semester!]!`): 

    Semesters that must precede this semester.  
    Semestry, které musí předcházet tomuto semestru.
- **dependentSemesters** (`List[Semester!]!`): 

    Semesters for which this semester is a prerequisite.  
    Semestry, pro které je tento semestr prerekvizitou.

---
## Int

The `Int` scalar type represents non-fractional signed whole numeric values. Int can represent values between -(2^31) and 2^31 - 1.


---
## StudyPlan

Represents a study plan for a subject in a given semester, including a schedule and a classification scheme.  
Reprezentuje studijní plán pro předmět v daném semestru, včetně rozvrhu a klasifikačního schématu.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the study plan  
    Unikátní identifikátor studijního plánu
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **description** (`String`): 

    Description or title of the study plan  
    Popis nebo název studijního plánu
- **semester** (`Semester`): 

    Reference to the semester  
    Odkaz na semestr
- **classificationScheme** (`ClassificationScheme`): 

    Classification scheme for this study plan  
    Klasifikační schéma pro tento studijní plán
- **scheduledLessons** (`List[Lesson!]!`): 

    List of scheduled lessons  
    Seznam naplánovaných lekcí

---
## ClassificationScheme

Defines the classification scheme for a subject in a given semester.  
Definuje klasifikační schéma pro předmět v daném semestru.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the classification scheme  
    Unikátní identifikátor klasifikačního schématu
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the classification scheme  
    Název klasifikačního schématu
- **description** (`String`): 

    Description of the classification scheme  
    Popis klasifikačního schématu
- **semester** (`Semester`): 

    Reference to the semester  
    Odkaz na semestr
- **parts** (`List[ClassificationPart!]!`): 

    List of classification parts in the scheme  
    Seznam klasifikačních částí v tomto schématu

---
## ClassificationPart

Defines an individual part of the classification scheme with a maximum point value.  
Definuje jednotlivou část klasifikačního schématu s maximální bodovou hodnotou.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the classification part  
    Unikátní identifikátor klasifikační části
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the classification part  
    Název klasifikační části
- **description** (`String`): 

    Description of the classification part  
    Popis klasifikační části
- **maxPoints** (`Float`): 

    Maximum points achievable  
    Maximální dosažitelný počet bodů
- **classificationScheme** (`ClassificationScheme`): 

    Reference to the classification scheme  
    Odkaz na klasifikační schéma
- **responsible** (`User`): 

    Responsible person for this part  
    Odpovědná osoba za tuto část

---
## Lesson

Represents a lesson scheduled in a study plan.  
Reprezentuje lekci naplánovanou ve studijním plánu.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the lesson  
    Unikátní identifikátor lekce
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **content** (`String`): 

    Content of the lesson  
    Obsah lekce
- **length** (`Float`): 

    Length of the lesson in arbitrary units  
    Délka lekce v libovolných jednotkách
- **lessonType** (`LessonType`): 

    Type of lesson (e.g., lecture, exercise)  
    Typ lekce (např. přednáška, cvičení)
- **event** (`Event`): 

    Event representing the lesson instance  
    Událost reprezentující instanci lekce
- **studyPlan** (`StudyPlan`): 

    Reference to the study plan  
    Odkaz na studijní plán
- **instructors** (`List[User!]!`): 

    List of instructors for the lesson  
    Seznam vyučujících pro tuto lekci
- **groups** (`List[Group!]!`): 

    List of groups involved in the lesson  
    Seznam skupin zapojených do lekce
- **relatedLessons** (`List[Lesson!]!`): 

    List of related lessons  
    Seznam souvisejících lekcí

---
## LessonType

Represents an type.  
Reprezentuje typ entity.

### Fields:

- **id** (`UUID`): 

    primary key
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the type  
    Název typu
- **description** (`String`): 

    Description of the type  
    Popis typu
- **category** (`LessonCategory`): 

    Category
- **entities** (`List[Lesson!]!`): 

    Entities of this type  
    Seznam entit tohoto typu

---
## LessonCategory

Represents an type category.  
Reprezentuje categorii typu.

### Fields:

- **id** (`UUID`): 

    primary key
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the category  
    Název kategorie
- **types** (`List[Lesson!]!`): 

    types

---
## Event

Represents an event. It may be a general event or an exam term.  
The event includes a time interval, a materialized path, and an optional textual location.  
Reprezentuje událost. Může se jednat o obecnou událost nebo zkouškový termín.  
Událost obsahuje časový interval, materializovanou cestu a volitelnou textovou lokalitu.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the event  
    Unikátní identifikátor události
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the event  
    Název události
- **description** (`String`): 

    Description of the event  
    Popis události
- **eventType** (`EventType`): 

    Reference to the event type  
    Odkaz na typ události
- **startDate** (`DateTime`): 

    Start date/time of the event  
    Datum a čas začátku události
- **endDate** (`DateTime`): 

    End date/time of the event  
    Datum a čas konce události
- **path** (`String`): 

    Materialized path in the event hierarchy (e.g., '/Semester/Week1/Lesson3')  
    Materializovaná cesta v hierarchii událostí (např. '/Semestr/Týden1/Lekce3')
- **location** (`String`): 

    Textual description of the location if Facility is not defined  
    Textový popis lokality, pokud není definováno zařízení
- **facility** (`Facility`): 

    Reference to the facility where the event takes place  
    Odkaz na zařízení, kde se událost koná
- **parent** (`Event`): 

    Reference to the parent event  
    Odkaz na nadřazenou událost
- **documents** (`List[Document!]!`): 

    Documents associated with the event  
    Dokumenty spojené s událostí
- **subevents** (`List[Event!]!`): 

    List of subevents  
    Seznam podudálostí
- **invitations** (`List[Invitation!]!`): 

    List of invitations for the event  
    Seznam pozvánek na událost

---
## EventType

Defines the type of an event (e.g., 'general', 'examTerm').  
Definuje typ události (např. 'obecná', 'zkouškový termín').

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the event type  
    Unikátní identifikátor typu události
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the event type  
    Název typu události
- **description** (`String`): 

    Description of the event type  
    Popis typu události

---
## Facility

Represents a facility (physical or virtual location) with a full label and managed by an organizational group.  
Reprezentuje zařízení (fyzické nebo virtuální místo) s úplným označením, spravované organizační skupinou.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the facility  
    Unikátní identifikátor zařízení
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the facility  
    Název zařízení
- **address** (`String`): 

    Address or description of the facility  
    Adresa nebo popis zařízení
- **label** (`String`): 

    Full name of the facility (e.g., 'Učebna 101')  
    Úplné označení zařízení (např. 'Učebna 101')
- **parent** (`Facility`): 

    Reference to the parent facility  
    Odkaz na nadřazené zařízení
- **subfacilities** (`List[Facility!]!`): 

    List of subordinate facilities  
    Seznam podřízených zařízení
- **facilityType** (`FacilityType`): 

    Facility type  
    typ zařízení
- **events** (`List[Event!]!`): 

    List of events taking place at this facility  
    Seznam událostí konaných v tomto zařízení
- **group** (`Group`): 

    Organizational group responsible for managing the facility  
    Organizační skupina odpovědná za správu zařízení

---
## FacilityType

Represents an type.  
Reprezentuje typ entity.

### Fields:

- **id** (`UUID`): 

    primary key
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the type  
    Název typu
- **description** (`String`): 

    Description of the type  
    Popis typu
- **category** (`FacilityCategory`): 

    Category
- **entities** (`List[Facility!]!`): 

    Entities of this type  
    Seznam entit tohoto typu

---
## FacilityCategory

Represents an type category.  
Reprezentuje categorii typu.

### Fields:

- **id** (`UUID`): 

    primary key
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the category  
    Název kategorie
- **types** (`List[Facility!]!`): 

    types

---
## Document

Represents a document with hierarchical organization, stored content and MIME type.  
Reprezentuje dokument s hierarchickou organizací, uloženým obsahem a typem MIME.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the document  
    Unikátní identifikátor dokumentu
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    Creation datetime of the document  
    Datum a čas vytvoření dokumentu
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **title** (`String`): 

    Title of the document  
    Název dokumentu
- **content** (`String`): 

    Textual content of the document  
    Textový obsah dokumentu
- **path** (`String`): 

    Materialized path of the document in the hierarchy  
    Materializovaná cesta dokumentu v hierarchii
- **fileContent** (`String`): 

    Stored file content (e.g., base64 encoded)  
    Uložený obsah souboru (např. kódovaný v base64)
- **mimeType** (`String`): 

    MIME type of the document  
    MIME typ dokumentu
- **event** (`Event`): 

    Reference to the associated event  
    Odkaz na přidruženou událost
- **parent** (`Document`): 

    Reference to the parent document  
    Odkaz na nadřazený dokument
- **subdocuments** (`List[Document!]!`): 

    List of subordinate documents  
    Seznam podřízených dokumentů
- **documentType** (`FacilityType`): 

    Document type  
    typ dokumentu

---
## Invitation

Represents an invitation to an event, recording the status and sent timestamp.  
Reprezentuje pozvánku na událost, zaznamenává stav a čas odeslání.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the invitation  
    Unikátní identifikátor pozvánky
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **status** (`String`): 

    Status of the invitation (e.g., accepted, declined, excused)  
    Stav pozvánky (např. přijatá, odmítnutá, omluvená)
- **sentAt** (`DateTime`): 

    Timestamp when the invitation was sent  
    Časové razítko odeslání pozvánky
- **event** (`Event`): 

    Reference to the event  
    Odkaz na událost
- **person** (`User`): 

    Reference to the person receiving the invitation  
    Odkaz na osobu, která pozvánku obdržela

---
## Evaluation

Represents an evaluation given to a student.  
Reprezentuje hodnocení udělené studentovi.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the evaluation  
    Unikátní identifikátor hodnocení
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **grade** (`String`): 

    Grade value (e.g., A–F, pass/fail)  
    Hodnota známky (např. A–F, prospěl/neprospěl)
- **attempt** (`Int`): 

    Attempt number  
    Číslo pokusu
- **points** (`Float`): 

    Points achieved  
    Počet dosažených bodů
- **passed** (`Boolean`): 

    Whether the evaluation is passing  
    Zda je hodnocení úspěšné
- **student** (`Student`): 

    Reference to the student  
    Odkaz na studenta
- **subject** (`Subject`): 

    Reference to the subject  
    Odkaz na předmět
- **semester** (`Semester`): 

    Reference to the semester  
    Odkaz na semestr
- **classificationPart** (`ClassificationPart`): 

    Reference to the classification part  
    Odkaz na klasifikační část
- **examEvent** (`Event`): 

    Event representing the evaluation term  
    Událost reprezentující termín hodnocení
- **admissionProcess** (`AdmissionProcess`): 

    Reference to the admission process  
    Odkaz na přijímací řízení
- **evaluationType** (`EvaluationType`): 

    Reference to the evaluation type  
    Odkaz na typ hodnocení
- **examComponents** (`List[ExamComponent!]!`): 

    List of exam components  
    Seznam složek zkoušky

---
## Boolean

The `Boolean` scalar type represents `true` or `false`.


---
## Student

Represents a student enrolled in a study program.  
Reprezentuje studenta zapsaného do studijního programu.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the student record  
    Unikátní identifikátor studijního záznamu
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **person** (`User`): 

    Reference to the person  
    Odkaz na osobu
- **studyProgram** (`StudyProgram`): 

    Reference to the study program  
    Odkaz na studijní program
- **state** (`State`): 

    State of the student  
    Stav studenta

---
## State

Represents the state (e.g. of a student: active, interrupted, applicant).  
Reprezentuje stav (např. studenta: aktivní, přerušené, uchazeč).

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the student state  
    Unikátní identifikátor stavu
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the state  
    Název stavu
- **description** (`String`): 

    Description of the state  
    Popis stavu

---
## AdmissionProcess

Represents the admission process for a study program.  
Reprezentuje přijímací řízení pro studijní program.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the admission process  
    Unikátní identifikátor přijímacího řízení
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **applicationStart** (`DateTime`): 

    Start date of the admission process  
    Datum zahájení přijímacího řízení
- **applicationDeadline** (`DateTime`): 

    Deadline for applications  
    Termín pro podání přihlášek
- **resultsAnnouncement** (`DateTime`): 

    Date when results are announced  
    Datum zveřejnění výsledků
- **description** (`String`): 

    Description of the admission process  
    Popis přijímacího řízení
- **studyProgram** (`StudyProgram`): 

    Reference to the study program  
    Odkaz na studijní program
- **admissionExams** (`List[Exam!]!`): 

    List of exams in the admission process  
    Seznam zkoušek v přijímacím řízení
- **requiredDocuments** (`List[Document!]!`): 

    List of documents required for the process  
    Seznam dokumentů vyžadovaných v procesu
- **admissionApplications** (`List[AdmissionApplication!]!`): 

    List of submitted applications  
    Seznam podaných přihlášek

---
## Exam

Unifies exam entities for special subjects (admission, state finals) as an event.  
Sjednocuje zkouškové entity pro speciální předměty (přijímací, státní závěrečné) jako událost.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the exam  
    Unikátní identifikátor zkoušky
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the exam  
    Název zkoušky
- **description** (`String`): 

    Description of the exam  
    Popis zkoušky
- **event** (`Event`): 

    Reference to the related event  
    Odkaz na související událost

---
## AdmissionApplication

Represents an application submitted by a candidate for admission.  
Reprezentuje přihlášku podanou uchazečem o přijetí.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the admission application  
    Unikátní identifikátor přihlášky
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **applicationDate** (`DateTime`): 

    Date of application submission  
    Datum podání přihlášky
- **status** (`String`): 

    Status of the application  
    Stav přihlášky
- **comments** (`String`): 

    Additional comments  
    Další poznámky
- **student** (`Student`): 

    Reference to the applicant  
    Odkaz na uchazeče
- **admissionProcess** (`AdmissionProcess`): 

    Reference to the admission process  
    Odkaz na přijímací řízení
- **submittedDocuments** (`List[Document!]!`): 

    List of documents submitted with the application  
    Seznam dokumentů podaných s přihláškou

---
## EvaluationType

Defines the evaluation type or context (e.g., 'semester', 'admission', 'stateFinal').  
Definuje typ nebo kontext hodnocení (např. 'semestrální', 'přijímací', 'státní závěrečná').

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the evaluation type  
    Unikátní identifikátor typu hodnocení
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the evaluation type  
    Název typu hodnocení
- **description** (`String`): 

    Description of the evaluation type  
    Popis typu hodnocení
- **evaluations** (`List[Evaluation!]!`): 

    List of evaluations of this type  
    Seznam hodnocení tohoto typu

---
## ExamComponent

Defines a component of an exam with min/max score values and provides results for all students.  
Definuje složku zkoušky s minimální/maximální bodovou hodnotou a poskytuje výsledky pro všechny studenty.

### Fields:

- **id** (`UUID!`): 

    Unique identifier of the exam component  
    Unikátní identifikátor složky zkoušky
- **lastchange** (`DateTime`): 

    timestamp
- **created** (`DateTime`): 

    date & time of unit born
- **createdbyId** (`UUID`): 

    who created this entity
- **changedbyId** (`UUID`): 

    who changed this entity
- **rbacobjectId** (`UUID`): 

    rbac ruling object
- **name** (`String`): 

    Name of the exam component  
    Název složky zkoušky
- **description** (`String`): 

    Description of the exam component  
    Popis složky zkoušky
- **minScore** (`Float`): 

    Minimum required score  
    Minimální požadovaný počet bodů
- **maxScore** (`Float`): 

    Maximum achievable score  
    Maximální dosažitelný počet bodů
- **exam** (`Exam`): 

    Reference to the exam  
    Odkaz na zkoušku
- **results** (`List[Evaluation!]!`): 

    List of evaluation results for this component  
    Seznam výsledků hodnocení pro tuto složku

---
