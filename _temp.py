import uuid
from datetime import datetime
from typing import List, Optional

from strawberry.fastapi import GraphQLRouter
import strawberry
from fastapi import FastAPI

IDType = uuid.UUID
# ============================================================
# 1. Organizační struktura
# ============================================================

@strawberry.type(description="Represents an organizational unit (e.g., university, faculty, department) with a hierarchical structure.")
class Group:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the group")
    name: str = strawberry.field(description="Name of the group")
    description: str = strawberry.field(description="Brief description of the group")
    path: str = strawberry.field(description="Materialized path representing the hierarchy (e.g., '/University/Faculty/Department')")
    abbreviation: str = strawberry.field(description="Abbreviation of the group")

    # scalars
    parent: Optional["Group"] = strawberry.field(description="Reference to the parent group", default=None)
    groupType: Optional["GroupType"] = strawberry.field(description="Reference to the group type", default=None)

    # vectors
    memberships: List["Membership"] = strawberry.field(description="List of memberships in the group")
    subgroups: List["Group"] = strawberry.field(description="List of subordinate groups")
    roles: List["Role"] = strawberry.field(description="List of roles assigned to the group")


@strawberry.type(description="Defines the type/category of a group (e.g., 'academic', 'administrative').")
class GroupType:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the group type")
    name: str = strawberry.field(description="Name of the group type")
    # scalars

    # vectors


@strawberry.type(description="Represents a physical person (e.g., student, teacher, administrator).")
class Person:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the person")
    firstName: str = strawberry.field(description="First name of the person")
    familyName: str = strawberry.field(description="Last name of the person")
    middleName: str = strawberry.field(description="Last name of the person")
    email: str = strawberry.field(description="Email address of the person")
    # scalars

    # vectors
    memberships: List["Membership"] = strawberry.field(description="Memberships associated with the person")
    roles: List["Role"] = strawberry.field(description="Roles assigned to the person")
    studies: List["StudyProgram"] = strawberry.field(description="Study programs the person is involved in")


@strawberry.type(description="Associates a person with a group, including the validity interval of the membership.")
class Membership:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the membership")
    startDate: datetime = strawberry.field(description="Start date of membership validity")
    endDate: datetime = strawberry.field(description="End date of membership validity")

    # scalars
    person: "Person" = strawberry.field(description="Reference to the associated person")
    group: "Group" = strawberry.field(description="Reference to the associated group")

    # vectors


@strawberry.type(description="Represents a role assignment to a person within a group. The role details (name, description) come from RoleType.")
class Role:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the role")
    startDate: datetime = strawberry.field(description="Start date of the role validity")
    endDate: datetime = strawberry.field(description="End date of the role validity")

    # scalars
    group: "Group" = strawberry.field(description="Group in which the role is assigned")
    person: "Person" = strawberry.field(description="Person to whom the role is assigned")
    roleType: "RoleType" = strawberry.field(description="Reference to the type of role")


@strawberry.type(description="Defines a type of role (e.g., 'Rector', 'Dean', 'Manager', 'Examiner') and is further classified by a Category.")
class RoleType:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the role type")
    name: str = strawberry.field(description="Name of the role type")
    description: str = strawberry.field(description="Description of the role type")

    # scalars
    category: "Category" = strawberry.field(description="Category of the role type")

    # vectors
    roles: List[Role] = strawberry.field(description="List of roles of this type")


@strawberry.type(description="Represents a category for role types (e.g., 'administrative').")
class Category:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the category")
    name: str = strawberry.field(description="Name of the category")
    # scalars
    # vectors


# ============================================================
# 2. Události, lokality, dokumenty a administrativní úkoly
# ============================================================

@strawberry.type(description="Represents an event. It may be a general event or an exam term. The event includes a time interval, a materialized path, and an optional textual location.")
class Event:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the event")
    name: str = strawberry.field(description="Name of the event")
    description: str = strawberry.field(description="Description of the event")
    eventType: "EventType" = strawberry.field(description="Reference to the event type")
    startDate: datetime = strawberry.field(description="Start date/time of the event")
    endDate: datetime = strawberry.field(description="End date/time of the event")
    path: str = strawberry.field(description="Materialized path in the event hierarchy (e.g., '/Semester/Week1/Lesson3')")
    location: str = strawberry.field(description="Textual description of the location if Facility is not defined", default="")

    # scalars
    facility: Optional["Facility"] = strawberry.field(description="Reference to the facility where the event takes place", default=None)
    parent: Optional["Event"] = strawberry.field(description="Reference to the parent event", default=None)

    # vectors
    documents: List["Document"] = strawberry.field(description="Documents associated with the event")
    subevents: List["Event"] = strawberry.field(description="List of subevents")
    invitations: List["Invitation"] = strawberry.field(description="List of invitations for the event")


@strawberry.type(description="Defines the type of an event (e.g., 'general', 'examTerm').")
class EventType:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the event type")
    name: str = strawberry.field(description="Name of the event type")
    description: str = strawberry.field(description="Description of the event type")
    # scalars
    # vectors


@strawberry.type(description="Represents an invitation to an event, recording the status and sent timestamp.")
class Invitation:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the invitation")
    status: str = strawberry.field(description="Status of the invitation (e.g., accepted, declined, excused)")
    sentAt: datetime = strawberry.field(description="Timestamp when the invitation was sent")

    # scalars
    event: Event = strawberry.field(description="Reference to the event")
    person: Person = strawberry.field(description="Reference to the person receiving the invitation")
    # vectors


@strawberry.type(description="Represents a facility (physical or virtual location) with a full label and managed by an organizational group.")
class Facility:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the facility")
    name: str = strawberry.field(description="Name of the facility")
    address: str = strawberry.field(description="Address or description of the facility")
    label: str = strawberry.field(description="Full name of the facility (e.g., 'Učebna 101')")

    # scalars
    parent: Optional["Facility"] = strawberry.field(description="Reference to the parent facility", default=None)
    group: Group = strawberry.field(description="Organizational group responsible for managing the facility")

    # vectors
    subfacilities: List["Facility"] = strawberry.field(description="List of subordinate facilities")
    events: List[Event] = strawberry.field(description="List of events taking place at this facility")


@strawberry.type(description="Represents an administrative task defined within the administrative group")
class Task:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the task")
    description: str = strawberry.field(description="Description of the task")
    definitionEvent: Event = strawberry.field(description="Event when the task was defined")
    dueEvent: Event = strawberry.field(description="Event representing the due date for the task")

    # scalars
    assigneePerson: Optional[Person] = strawberry.field(description="Person assigned to the task", default=None)
    assigneeRole: Optional[Role] = strawberry.field(description="Role for which the task is assigned", default=None)
    group: Group = strawberry.field(description="Administrative group to which the task belongs")
    # vectors


@strawberry.type(description="Represents a document with hierarchical organization, stored content and MIME type")
class Document:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the document")
    title: str = strawberry.field(description="Title of the document")
    content: str = strawberry.field(description="Textual content of the document")
    created: datetime = strawberry.field(description="Creation datetime of the document")
    path: str = strawberry.field(description="Materialized path of the document in the hierarchy")
    fileContent: Optional[str] = strawberry.field(description="Stored file content (e.g., base64 encoded)", default=None)
    mimeType: Optional[str] = strawberry.field(description="MIME type of the document", default=None)

    # scalars
    event: Optional[Event] = strawberry.field(description="Reference to the associated event", default=None)
    parent: Optional["Document"] = strawberry.field(description="Reference to the parent document", default=None)

    # vectors
    subdocuments: List["Document"] = strawberry.field(description="List of subordinate documents", default_factory=list)


# ============================================================
# 3. Studium
# ============================================================

@strawberry.type(description="Represents a study program (e.g., Cybersecurity)")
class StudyProgram:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the study program")
    title: str = strawberry.field(description="Title of the study program")
    level: str = strawberry.field(description="Level of study (e.g., Bachelor's, Master's)")
    qualification: str = strawberry.field(description="Awarded qualification")
    duration: float = strawberry.field(description="Duration of the program in years")
    description: str = strawberry.field(description="Description of the study program")

    # scalars
    university: Group = strawberry.field(description="University offering the program")
    group: Group = strawberry.field(description="Organizational group responsible for the program")

    # vectors
    accreditations: List["Accreditation"] = strawberry.field(description="List of accreditation decisions")
    subjects: List["Subject"] = strawberry.field(description="List of subjects in the program")


@strawberry.type(description="Represents an accreditation decision for a study program")
class Accreditation:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the accreditation")
    decisionNumber: str = strawberry.field(description="Accreditation decision number")
    decisionDate: datetime = strawberry.field(description="Date of the decision")
    validFrom: datetime = strawberry.field(description="Validity start date")
    validTo: datetime = strawberry.field(description="Validity end date")
    notes: str = strawberry.field(description="Additional notes")

    # scalars
    studyProgram: StudyProgram = strawberry.field(description="Reference to the study program")
    accreditationBody: "AccreditationBody" = strawberry.field(description="Reference to the accreditation body")
    # vectors


@strawberry.type(description="Represents the accreditation body")
class AccreditationBody:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the accreditation body")
    name: str = strawberry.field(description="Name of the accreditation body")
    description: str = strawberry.field(description="Description of the accreditation body")

    # scalars
    accreditations: List[Accreditation] = strawberry.field(description="List of accreditation decisions granted by this body")
    # vectors


@strawberry.type(description="Represents a subject within a study program")
class Subject:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the subject")
    name: str = strawberry.field(description="Name of the subject")
    description: str = strawberry.field(description="Description of the subject")
    type: str = strawberry.field(description="Category of the subject (e.g., 'regular', 'admission', 'stateFinal')")

    # scalars
    studyProgram: StudyProgram = strawberry.field(description="Reference to the study program")
    group: Group = strawberry.field(description="Organizational group responsible for the subject")

    # vectors
    semesters: List["Semester"] = strawberry.field(description="List of semesters in which the subject is taught")


@strawberry.type(description="Represents a semester for a subject, including classification method and credits")
class Semester:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the semester")
    term: str = strawberry.field(description="Semester term (e.g., Fall, Spring)")
    year: int = strawberry.field(description="Year of the semester")
    description: str = strawberry.field(description="Description of the semester")
    classificationMethod: str = strawberry.field(description="Method of classification (e.g., weighted)")
    credits: float = strawberry.field(description="Number of credits")

    # scalars
    subject: Subject = strawberry.field(description="Reference to the subject")

    # vectors
    studyPlans: List["StudyPlan"] = strawberry.field(description="List of study plans for this semester")


@strawberry.type(description="Represents a thematic block within a semester, grouping lessons")
class Topic:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the topic")
    name: str = strawberry.field(description="Name of the topic")
    description: str = strawberry.field(description="Description of the topic")

    # scalars
    semester: Semester = strawberry.field(description="Reference to the semester")

    # vectors
    lessons: List["Lesson"] = strawberry.field(description="List of lessons in this topic")


@strawberry.type(description="Represents a study plan for a subject in a given semester, including a schedule and a classification scheme")
class StudyPlan:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the study plan")
    description: str = strawberry.field(description="Description or title of the study plan")

    # scalars
    semester: Semester = strawberry.field(description="Reference to the semester")
    classificationScheme: "ClassificationScheme" = strawberry.field(description="Classification scheme for this study plan")

    # vectors
    scheduledLessons: List["Lesson"] = strawberry.field(description="List of scheduled lessons")


@strawberry.type(description="Defines the classification scheme for a subject in a given semester")
class ClassificationScheme:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the classification scheme")
    name: str = strawberry.field(description="Name of the classification scheme")
    description: str = strawberry.field(description="Description of the classification scheme")

    # scalars
    responsible: Person = strawberry.field(description="Responsible person (e.g., subject guarantor)")
    semester: Semester = strawberry.field(description="Reference to the semester")

    # vectors
    parts: List["ClassificationPart"] = strawberry.field(description="List of classification parts in the scheme")


@strawberry.type(description="Defines an individual part of the classification scheme with a maximum point value")
class ClassificationPart:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the classification part")
    name: str = strawberry.field(description="Name of the classification part")
    description: str = strawberry.field(description="Description of the classification part")
    maxPoints: float = strawberry.field(description="Maximum points achievable")

    # scalars
    classificationScheme: ClassificationScheme = strawberry.field(description="Reference to the classification scheme")

    # vectors
    responsible: Optional[Person] = strawberry.field(description="Responsible person for this part", default=None)


@strawberry.type(description="Represents a lesson scheduled in a study plan")
class Lesson:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the lesson")
    content: str = strawberry.field(description="Content of the lesson")
    length: float = strawberry.field(description="Length of the lesson in arbitrary units")
    lessonType: str = strawberry.field(description="Type of lesson (e.g., lecture, exercise)")

    # scalars
    event: Event = strawberry.field(description="Event representing the lesson instance")
    studyPlan: StudyPlan = strawberry.field(description="Reference to the study plan")

    # vectors
    instructors: List[Person] = strawberry.field(description="List of instructors for the lesson")
    groups: List[Group] = strawberry.field(description="List of groups involved in the lesson")
    relatedLessons: List["Lesson"] = strawberry.field(description="List of related lessons", default_factory=list)


@strawberry.type(description="Represents a student enrolled in a study program")
class Student:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the student record")

    # scalars
    person: Person = strawberry.field(description="Reference to the person")
    studyProgram: StudyProgram = strawberry.field(description="Reference to the study program")
    state: "StudentState" = strawberry.field(description="State of the student")
    # vectors


@strawberry.type(description="Represents the state of a student (e.g., active, interrupted, applicant)")
class StudentState:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the student state")
    name: str = strawberry.field(description="Name of the student state")

    # scalars
    description: str = strawberry.field(description="Description of the student state")
    # vectors


@strawberry.type(description="Represents an evaluation given to a student")
class Evaluation:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the evaluation")
    grade: str = strawberry.field(description="Grade value (e.g., A–F, pass/fail)")
    attempt: int = strawberry.field(description="Attempt number")
    points: Optional[float] = strawberry.field(description="Points achieved", default=None)
    passed: Optional[bool] = strawberry.field(description="Whether the evaluation is passing", default=None)

    # scalars
    student: Student = strawberry.field(description="Reference to the student")
    subject: Optional[Subject] = strawberry.field(description="Reference to the subject", default=None)
    semester: Optional[Semester] = strawberry.field(description="Reference to the semester", default=None)
    classificationPart: Optional[ClassificationPart] = strawberry.field(description="Reference to the classification part", default=None)
    examEvent: Optional[Event] = strawberry.field(description="Event representing the evaluation term", default=None)
    admissionProcess: Optional["AdmissionProcess"] = strawberry.field(description="Reference to the admission process", default=None)
    evaluationType: EvaluationType = strawberry.field(description="Reference to the evaluation type")

    # vectors
    examComponents: List["ExamComponent"] = strawberry.field(description="List of exam components", default_factory=list)


@strawberry.type(description="Defines the evaluation type or context (e.g., 'semester', 'admission', 'stateFinal')")
class EvaluationType:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the evaluation type")
    name: str = strawberry.field(description="Name of the evaluation type")
    description: str = strawberry.field(description="Description of the evaluation type")

    # scalars
    # vectors
    evaluations: List[Evaluation] = strawberry.field(description="List of evaluations of this type")


@strawberry.type(description="Represents the admission process for a study program")
class AdmissionProcess:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the admission process")
    applicationStart: datetime = strawberry.field(description="Start date of the admission process")
    applicationDeadline: datetime = strawberry.field(description="Deadline for applications")
    resultsAnnouncement: datetime = strawberry.field(description="Date when results are announced")
    description: str = strawberry.field(description="Description of the admission process")

    # scalars
    studyProgram: StudyProgram = strawberry.field(description="Reference to the study program")
    admissionExams: List[Exam] = strawberry.field(description="List of exams in the admission process")
    requiredDocuments: List[Document] = strawberry.field(description="List of documents required for the process")
    admissionApplications: List["AdmissionApplication"] = strawberry.field(description="List of submitted applications")
    # vectors


@strawberry.type(description="Represents an application submitted by a candidate for admission")
class AdmissionApplication:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the admission application")
    applicationDate: datetime = strawberry.field(description="Date of application submission")
    status: str = strawberry.field(description="Status of the application")
    comments: str = strawberry.field(description="Additional comments", default="")
    student: Student = strawberry.field(description="Reference to the applicant")

    # scalars
    admissionProcess: AdmissionProcess = strawberry.field(description="Reference to the admission process")

    # vectors
    submittedDocuments: List[Document] = strawberry.field(description="List of documents submitted with the application")


@strawberry.type(description="Unifies exam entities for special subjects (admission, state finals) as an event")
class Exam:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the exam")
    name: str = strawberry.field(description="Name of the exam")
    description: str = strawberry.field(description="Description of the exam")
    # Additional inherited fields (e.g., eventType, facility) can be added as needed.
    # scalars
    event = Optional["Event"] = strawberry.field(description="")
    # vectors


@strawberry.type(description="Defines a component of an exam with min/max score values and provides results for all students")
class ExamComponent:
    # base attributes
    id: IDType = strawberry.field(description="Unique identifier of the exam component")
    name: str = strawberry.field(description="Name of the exam component")
    description: str = strawberry.field(description="Description of the exam component")
    minScore: float = strawberry.field(description="Minimum required score")
    maxScore: float = strawberry.field(description="Maximum achievable score")

    # scalars
    exam: Exam = strawberry.field(description="Reference to the exam")

    # vectors
    results: List[Evaluation] = strawberry.field(description="List of evaluation results for this component", default_factory=list)


# ============================================================
# KONEC: Studium
# ============================================================

# Tento výpis entit je připraven k implementaci jako GraphQL schéma pomocí Strawberry.


app = FastAPI()