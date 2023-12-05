from datetime import date

import sqlalchemy
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, ForeignKey, create_engine, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session, relationship, sessionmaker

app = Flask(__name__)

DATABASE_URI = 'postgresql://postgres:1234@localhost/clinic'

engine = create_engine(DATABASE_URI)
Base = sqlalchemy.orm.declarative_base()
Session = sessionmaker(bind=engine)
session = Session()


class Department(Base):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)


class Sex(Base):
    __tablename__ = 'sex'
    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)


class Patient(Base):
    __tablename__ = 'patient'
    id = Column(Integer, primary_key=True)
    surname = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    secondname = Column(String(50))
    sex_id = Column(Integer, ForeignKey('sex.id'))
    dateofbirth = Column(Date, nullable=False)
    sex = relationship("Sex")


class Specialization(Base):
    __tablename__ = 'specialization'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)


class Doctors(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    surname = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    secondname = Column(String(50))
    momentofstartworking = Column(Date, nullable=False)
    sex_id = Column(Integer, ForeignKey('sex.id'))
    specialization_id = Column(Integer, ForeignKey('specialization.id'))
    department_id = Column(Integer, ForeignKey('department.id'))
    sex = relationship("Sex")
    specialization = relationship("Specialization")
    department = relationship("Department")


class Service(Base):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    price = Column(Integer)


class TheActOfRenderingTheService(Base):
    __tablename__ = 'theactofrenderingtheservice'
    id = Column(Integer, primary_key=True)
    dateandtimeofservice = Column(TIMESTAMP, nullable=False)
    price = Column(Integer, nullable=False)
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    patient_id = Column(Integer, ForeignKey('patient.id'))
    service_id = Column(Integer, ForeignKey('service.id'))
    doctor = relationship("Doctors")
    patient = relationship("Patient")
    service = relationship("Service")


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/doctors', methods=['GET'])
def list_doctors():
    doctors = session.query(Doctors).all()
    return render_template('doctors.html', doctors=doctors)


@app.route('/doctors/add', methods=['GET', 'POST'])
def add_doctor():
    if request.method == 'POST':
        surname = request.form['surname']
        name = request.form['name']
        secondname = request.form['secondname']
        momentofstartworking = request.form['momentofstartworking']
        momentofstartworking = date.fromisoformat(momentofstartworking)
        sex_id = request.form['sex']
        specialization_id = request.form['specialization']
        department_id = request.form['department']

        new_doctor = Doctors(surname=surname, name=name, secondname=secondname,
                             momentofstartworking=momentofstartworking, sex_id=sex_id,
                             specialization_id=specialization_id, department_id=department_id)
        session.add(new_doctor)
        session.commit()
        return redirect(url_for('list_doctors'))
    else:
        sexes = session.query(Sex).all()
        specializations = session.query(Specialization).all()
        departments = session.query(Department).all()
        return render_template('add_doctor.html', sexes=sexes, specializations=specializations, departments=departments)


@app.route('/doctors/edit/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor_func(doctor_id):
    doctor = session.query(Doctors).get(doctor_id)
    if request.method == 'POST':
        sexes = session.query(Sex).all()
        specializations = session.query(Specialization).all()
        departments = session.query(Department).all()
        return render_template('edit_doctor.html', doctor=doctor, sexes=sexes, specializations=specializations, departments=departments)
    else:
        return redirect(url_for('list_doctors'))


@app.route('/doctors/edit_result/<int:doctor_id>', methods=['POST'])
def edit_doctor_res(doctor_id):
    doctor = session.query(Doctors).get(doctor_id)
    if request.method == 'POST':
        doctor.surname = request.form['surname']
        doctor.name = request.form['name']
        doctor.secondname = request.form['secondname']
        doctor.momentofstartworking = request.form['momentofstartworking']
        doctor.momentofstartworking = date.fromisoformat(doctor.momentofstartworking)
        doctor.sex_id = request.form['sex']
        doctor.specialization_id = request.form['specialization']
        doctor.department_id = request.form['department']

        session.commit()
        return redirect(url_for('list_doctors'))
    else:
        return redirect(url_for('list_doctors'))


@app.route('/doctors/delete/<int:doctor_id>', methods=['GET', 'POST'])
def delete_doctor(doctor_id):
    related_services = session.query(TheActOfRenderingTheService).filter_by(doctor_id=doctor_id).all()

    for service in related_services:
        session.delete(service)
    doctor = session.query(Doctors).get(doctor_id)
    session.delete(doctor)
    session.commit()
    return redirect(url_for('list_doctors'))


@app.route('/services', methods=['GET'])
def list_services():
    services = session.query(Service).all()
    return render_template('services.html', services=services)


@app.route('/patients', methods=['GET'])
def list_patients():
    patients = session.query(Patient).all()
    return render_template('patients.html', patients=patients)



@app.route('/patients/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        surname = request.form['surname']
        name = request.form['name']
        secondname = request.form['secondname']
        dateofbirth = request.form['dateofbirth']
        dateofbirth = date.fromisoformat(dateofbirth)
        sex_id = request.form['sex']

        new_patient = Patient(surname=surname, name=name, secondname=secondname,
                             dateofbirth=dateofbirth, sex_id=sex_id)
        session.add(new_patient)
        session.commit()
        return redirect(url_for('list_patients'))
    else:
        sexes = session.query(Sex).all()
        return render_template('add_patient.html', sexes=sexes)


@app.route('/patients/edit/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient_func(patient_id):
    patient = session.query(Patient).get(patient_id)
    if request.method == 'POST':
        sexes = session.query(Sex).all()
        return render_template('edit_patient.html', patient=patient, sexes = sexes)
    else:
        return redirect(url_for('list_patients'))


@app.route('/patients/edit_result/<int:patient_id>', methods=['POST'])
def edit_patient_res(patient_id):
    patient = session.query(Patient).get(patient_id)
    if request.method == 'POST':
        patient.surname = request.form['surname']
        patient.name = request.form['name']
        patient.secondname = request.form['secondname']
        patient.dateofbirth = request.form['dateofbirth']
        patient.dateofbirth = date.fromisoformat(patient.dateofbirth)
        patient.sex_id = request.form['sex']

        session.commit()
        return redirect(url_for('list_patients'))
    else:
        return redirect(url_for('list_patients'))


@app.route('/patients/delete/<int:patient_id>', methods=['GET', 'POST'])
def delete_patient(patient_id):
    related_services = session.query(TheActOfRenderingTheService).filter_by(patient_id=patient_id).all()

    for service in related_services:
        session.delete(service)
    patient = session.query(Patient).get(patient_id)
    session.delete(patient)
    session.commit()
    return redirect(url_for('list_patients'))


@app.route('/departments', methods=['GET'])
def list_departments():
    departments = session.query(Department).all()
    return render_template('departments.html', departments=departments)


if __name__ == "__main__":
    app.run(debug=True)