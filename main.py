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
    dateOfBirth = Column(Date, nullable=False)
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
    dateAndTimeOfService = Column(TIMESTAMP, nullable=False)
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


@app.route('/doctors/delete/<int:doctor_id>', methods=['POST', 'GET'])
def delete_doctor(doctor_id):
    doctor = session.query(Doctors).get(doctor_id)

    if doctor:
        session.query(TheActOfRenderingTheService).filter_by(doctor_id=doctor_id).delete()
        session.delete(doctor)
        session.commit()
        return redirect(url_for('doctors'))
    else:
        return "Врач не найден"


@app.route('/doctors/edit/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor(doctor_id):
    if request.method == 'POST':

        # Получение данных из формы
        surname = request.form['surname']
        name = request.form['name']
        secondname = request.form['secondname']
        momentofstartworking = request.form['momentofstartworking']
        sex = request.form['sex']
        specialization = request.form['specialization']
        department = request.form['department']

        # Создание нового объекта доктора
        new_doctor = Doctors(
            id=doctor_id,
            surname=surname,
            name=name,
            secondname=secondname,
            momentofstartworking=momentofstartworking,
            sex=sex,
            specialization=specialization,
            department=department,
        )



        # Добавление доктора в базу данных
        session.add(new_doctor)

        return session.query(Doctors).get(new_doctor)
        #session.commit()

        # Перенаправление на страницу с таблицей всех докторов
        #return redirect(url_for('doctors'))
    else:
        sexes = session.query(Sex).all()
        specializations = session.query(Specialization).all()
        departments = session.query(Department).all()
        doctor = session.query(Doctors).get(doctor_id)

        return render_template('edit_doctor.html', doctor=doctor, sexes=sexes, specializations=specializations,
                               departments=departments)


@app.route('/doctors')
def doctors():
    doctors_table = session.query(Doctors).all()
    return render_template('doctors.html', doctors=doctors_table)


@app.route('/services')
def services():
    return render_template('services.html')


@app.route('/patients')
def patients():
    return render_template('patients.html')


@app.route('/departments')
def departments():
    return render_template('departments.html')


if __name__ == "__main__":
    app.run(debug=True)