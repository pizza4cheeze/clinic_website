from datetime import date, datetime, timedelta

from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String, Date, TIMESTAMP, ForeignKey, func
from sqlalchemy.orm import relationship

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1234@localhost/clinic'

Base = SQLAlchemy(app)


class Department(Base.Model):
    __tablename__ = 'department'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)


class Sex(Base.Model):
    __tablename__ = 'sex'
    id = Column(Integer, primary_key=True)
    name = Column(String(10), nullable=False)


class Patient(Base.Model):
    __tablename__ = 'patient'
    id = Column(Integer, primary_key=True)
    surname = Column(String(50), nullable=False)
    name = Column(String(50), nullable=False)
    secondname = Column(String(50))
    sex_id = Column(Integer, ForeignKey('sex.id'))
    dateofbirth = Column(Date, nullable=False)
    sex = relationship("Sex")


class Specialization(Base.Model):
    __tablename__ = 'specialization'
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)


class Doctors(Base.Model):
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


class Service(Base.Model):
    __tablename__ = 'service'
    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    price = Column(Integer)


class TheActOfRenderingTheService(Base.Model):
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


# Doctors
@app.route('/doctors', methods=['GET'])
def list_doctors():
    doctors = Doctors.query.all()
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
        Base.session.add(new_doctor)
        Base.session.commit()
        return redirect(url_for('list_doctors'))
    else:
        sexes = Sex.query.all()
        specializations = Specialization.query.all()
        departments = Department.query.all()
        return render_template('add_doctor.html', sexes=sexes, specializations=specializations, departments=departments)


@app.route('/doctors/edit/<int:doctor_id>', methods=['GET', 'POST'])
def edit_doctor_func(doctor_id):
    doctor = Doctors.query.get(doctor_id)
    if request.method == 'POST':
        sexes = Sex.query.all()
        specializations = Specialization.query.all()
        departments = Department.query.all()
        return render_template('edit_doctor.html', doctor=doctor, sexes=sexes, specializations=specializations,
                               departments=departments)
    else:
        return redirect(url_for('list_doctors'))


@app.route('/doctors/edit_result/<int:doctor_id>', methods=['POST'])
def edit_doctor_res(doctor_id):
    doctor = Doctors.query.get(doctor_id)
    if request.method == 'POST':
        doctor.surname = request.form['surname']
        doctor.name = request.form['name']
        doctor.secondname = request.form['secondname']
        doctor.momentofstartworking = request.form['momentofstartworking']
        doctor.momentofstartworking = date.fromisoformat(doctor.momentofstartworking)
        doctor.sex_id = request.form['sex']
        doctor.specialization_id = request.form['specialization']
        doctor.department_id = request.form['department']

        Base.session.commit()
        return redirect(url_for('list_doctors'))
    else:
        return redirect(url_for('list_doctors'))


@app.route('/doctors/delete/<int:doctor_id>', methods=['GET', 'POST'])
def delete_doctor(doctor_id):
    related_services = TheActOfRenderingTheService.query.filter_by(doctor_id=doctor_id).all()

    for service in related_services:
        Base.session.delete(service)
    doctor = Doctors.query.get(doctor_id)
    Base.session.delete(doctor)
    Base.session.commit()
    return redirect(url_for('list_doctors'))


# Services
@app.route('/services', methods=['GET'])
def list_services():
    services = Service.query.all()
    return render_template('services.html', services=services)


@app.route('/services/add', methods=['GET', 'POST'])
def add_service():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']

        new_service = Service(name=name, price=price)
        Base.session.add(new_service)
        Base.session.commit()
        return redirect(url_for('list_services'))
    else:
        return render_template('add_service.html')


@app.route('/services/edit/<int:service_id>', methods=['GET', 'POST'])
def edit_service_func(service_id):
    service = Service.query.get(service_id)
    if request.method == 'POST':
        return render_template('edit_service.html', service=service)
    else:
        return redirect(url_for('list_services'))


@app.route('/services/edit_result/<int:service_id>', methods=['POST'])
def edit_service_res(service_id):
    service = Service.query.get(service_id)
    if request.method == 'POST':
        service.name = request.form['name']
        service.price = request.form['price']

        Base.session.commit()
        return redirect(url_for('list_services'))
    else:
        return redirect(url_for('list_services'))


@app.route('/services/delete/<int:service_id>', methods=['GET', 'POST'])
def delete_service(service_id):
    related_services = TheActOfRenderingTheService.query.filter_by(service_id=service_id).all()

    for service in related_services:
        Base.session.delete(service)

    service = Service.query.get(service_id)
    Base.session.delete(service)
    Base.session.commit()
    return redirect(url_for('list_services'))


# Patients
@app.route('/patients', methods=['GET'])
def list_patients():
    patients = Patient.query.all()

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
        Base.session.add(new_patient)
        Base.session.commit()
        return redirect(url_for('list_patients'))
    else:
        sexes = Sex.query.all()
        return render_template('add_patient.html', sexes=sexes)


@app.route('/patients/edit/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient_func(patient_id):
    patient = Patient.query.get(patient_id)
    if request.method == 'POST':
        sexes = Sex.query.all()
        return render_template('edit_patient.html', patient=patient, sexes=sexes)
    else:
        return redirect(url_for('list_patients'))


@app.route('/patients/edit_result/<int:patient_id>', methods=['POST'])
def edit_patient_res(patient_id):
    patient = Patient.query.get(patient_id)
    if request.method == 'POST':
        patient.surname = request.form['surname']
        patient.name = request.form['name']
        patient.secondname = request.form['secondname']
        patient.dateofbirth = request.form['dateofbirth']
        patient.dateofbirth = date.fromisoformat(patient.dateofbirth)
        patient.sex_id = request.form['sex']

        Base.session.commit()
        return redirect(url_for('list_patients'))
    else:
        return redirect(url_for('list_patients'))


@app.route('/patients/delete/<int:patient_id>', methods=['GET', 'POST'])
def delete_patient(patient_id):
    related_services = TheActOfRenderingTheService.query.filter_by(patient_id=patient_id).all()

    for service in related_services:
        Base.session.delete(service)
    patient = Patient.query.get(patient_id)
    Base.session.delete(patient)
    Base.session.commit()
    return redirect(url_for('list_patients'))


@app.route('/departments', methods=['GET'])
def list_departments():
    departments = Department.query.all()
    return render_template('departments.html', departments=departments)


@app.route('/departments/add', methods=['GET', 'POST'])
def add_department():
    if request.method == 'POST':
        name = request.form['name']

        new_department = Department(name=name)
        Base.session.add(new_department)
        Base.session.commit()
        return redirect(url_for('list_departments'))
    else:
        return render_template('add_department.html')


@app.route('/departments/edit/<int:department_id>', methods=['GET', 'POST'])
def edit_department_func(department_id):
    department = Department.query.get(department_id)
    if request.method == 'POST':
        return render_template('edit_department.html', department=department)
    else:
        return redirect(url_for('list_departments'))


@app.route('/departments/edit_result/<int:department_id>', methods=['POST'])
def edit_department_res(department_id):
    department = Department.query.get(department_id)
    if request.method == 'POST':
        department.name = request.form['name']

        Base.session.commit()
        return redirect(url_for('list_departments'))
    else:
        return redirect(url_for('list_departments'))


@app.route('/departments/delete/<int:department_id>', methods=['GET', 'POST'])
def delete_department(department_id):
    related_services = Doctors.query.filter_by(department_id=department_id).all()

    for service in related_services:
        Base.session.delete(service)
    department = Department.query.get(department_id)
    Base.session.delete(department)
    Base.session.commit()
    return redirect(url_for('list_departments'))


# Specializations
@app.route('/specializations', methods=['GET'])
def list_specializations():
    specializations = Specialization.query.all()
    return render_template('specializations.html', specializations=specializations)


@app.route('/specializations/add', methods=['GET', 'POST'])
def add_specialization():
    if request.method == 'POST':
        name = request.form['name']

        new_specialization = Specialization(name=name)
        Base.session.add(new_specialization)
        Base.session.commit()
        return redirect(url_for('list_specializations'))
    else:
        return render_template('add_specialization.html')


@app.route('/specializations/edit/<int:specialization_id>', methods=['GET', 'POST'])
def edit_specialization_func(specialization_id):
    specialization = Specialization.query.get(specialization_id)
    if request.method == 'POST':
        return render_template('edit_specialization.html', specialization=specialization)
    else:
        return redirect(url_for('list_specializations'))


@app.route('/specializations/edit_result/<int:specialization_id>', methods=['POST'])
def edit_specialization_res(specialization_id):
    specialization = Specialization.query.get(specialization_id)
    if request.method == 'POST':
        specialization.name = request.form['name']

        Base.session.commit()
        return redirect(url_for('list_specializations'))
    else:
        return redirect(url_for('list_specializations'))


@app.route('/specializations/delete/<int:specialization_id>', methods=['GET', 'POST'])
def delete_specialization(specialization_id):
    related_services = Doctors.query.filter_by(specialization_id=specialization_id).all()

    for service in related_services:
        Base.session.delete(service)
    specialization = Specialization.query.get(specialization_id)
    Base.session.delete(specialization)
    Base.session.commit()
    return redirect(url_for('list_specializations'))


# acts
@app.route('/acts', methods=['GET'])
def list_acts():
    acts = TheActOfRenderingTheService.query.all()
    return render_template('acts.html', acts=acts)


@app.route('/acts/add', methods=['GET', 'POST'])
def add_act():
    if request.method == 'POST':
        dateandtimeofservice = request.form['dateandtimeofservice']
        iso_datetime = datetime.fromisoformat(dateandtimeofservice)
        formatted_date = iso_datetime.strftime('%Y-%m-%dT%H:%M')
        price = request.form['price']

        doctor_id = request.form['doctor_id']
        if not check_id_exists(Doctors, doctor_id):
            return render_template('id_error.html')

        patient_id = request.form['patient_id']
        if not check_id_exists(Patient, patient_id):
            return render_template('id_error.html')

        service_id = request.form['service_id']
        if not check_id_exists(Service, service_id):
            return render_template('id_error.html')

        new_act = TheActOfRenderingTheService(dateandtimeofservice=formatted_date, price=price, doctor_id=doctor_id, patient_id=patient_id, service_id=service_id)
        Base.session.add(new_act)
        Base.session.commit()
        return redirect(url_for('list_acts'))
    else:
        return render_template('add_act.html')


@app.route('/acts/edit/<int:act_id>', methods=['GET', 'POST'])
def edit_act_func(act_id):
    act = TheActOfRenderingTheService.query.get(act_id)
    if request.method == 'POST':
        return render_template('edit_act.html', act=act)
    else:
        return redirect(url_for('list_acts'))


def check_id_exists(table, id):
    return Base.session.query(table).filter_by(id=id).first() is not None


@app.route('/acts/edit_result/<int:act_id>', methods=['POST'])
def edit_act_res(act_id):
    act = TheActOfRenderingTheService.query.get(act_id)
    if request.method == 'POST':
        date_to_format = request.form['dateandtimeofservice']
        iso_datetime = datetime.fromisoformat(date_to_format)
        act.dateandtimeofservice = iso_datetime.strftime('%Y-%m-%dT%H:%M')
        act.price = request.form['price']

        doctor_id = request.form['doctor_id']
        if check_id_exists(Doctors, doctor_id):
            act.doctor_id = doctor_id
        else:
            return render_template('id_error.html')

        patient_id = request.form['patient_id']
        if check_id_exists(Patient, patient_id):
            act.patient_id = patient_id
        else:
            return render_template('id_error.html')

        service_id = request.form['service_id']
        if check_id_exists(Service, service_id):
            act.service_id = service_id
        else:
            return render_template('id_error.html')

        Base.session.commit()
        return redirect(url_for('list_acts'))
    else:
        return redirect(url_for('list_acts'))


@app.route('/acts/delete/<int:act_id>', methods=['GET', 'POST'])
def delete_act(act_id):
    act = TheActOfRenderingTheService.query.get(act_id)
    Base.session.delete(act)
    Base.session.commit()
    return redirect(url_for('list_acts'))


@app.route('/month_choice', methods=['GET', 'POST'])
def choose():
    return render_template('month_results.html')


@app.route('/summary', methods=['POST'])
def calculate_summary():
    if request.method == 'POST':
        start_date_str = request.form['startDate']
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')

        # Вычисление конечной даты - начальная дата + 30 дней
        end_date = start_date + timedelta(days=30)

        # Общее количество услуг и общая сумма за период для клиники
        total_services_clinic = TheActOfRenderingTheService.query.filter(
            TheActOfRenderingTheService.dateandtimeofservice >= start_date,
            TheActOfRenderingTheService.dateandtimeofservice <= end_date
        ).count()

        total_amount_clinic = Base.session.query(func.sum(TheActOfRenderingTheService.price)).filter(
            TheActOfRenderingTheService.dateandtimeofservice >= start_date,
            TheActOfRenderingTheService.dateandtimeofservice <= end_date
        ).scalar()

        # Статистика по отделениям с учетом врачей и услуг
        department_stats = {}

        # Получаем все записи TheActOfRenderingTheService для выбранного периода
        services = TheActOfRenderingTheService.query.filter(
            TheActOfRenderingTheService.dateandtimeofservice >= start_date,
            TheActOfRenderingTheService.dateandtimeofservice <= end_date
        ).all()

        for service in services:
            # Получаем информацию о враче, оказавшем услугу
            doctor = Doctors.query.get(service.doctor_id)

            if doctor:
                # Если врач найден, получаем отделение врача
                doctor_department_id = doctor.department_id

                # Получаем текущее значение статистики по отделению
                current_count = department_stats.get(doctor_department_id, {'service_count': 0, 'total_amount': 0})

                # Увеличиваем количество услуг и сумму по отделению на данные из услуги
                current_count['service_count'] += 1
                current_count['total_amount'] += service.price

                # Обновляем статистику по отделению
                department_stats[doctor_department_id] = current_count

        # Статистика по врачам
        doctor_stats = Base.session.query(
            TheActOfRenderingTheService.doctor_id,
            func.count(TheActOfRenderingTheService.id).label('service_count'),
            func.sum(TheActOfRenderingTheService.price).label('total_amount')
        ).filter(
            TheActOfRenderingTheService.dateandtimeofservice >= start_date,
            TheActOfRenderingTheService.dateandtimeofservice <= end_date
        ).group_by(TheActOfRenderingTheService.doctor_id).all()

        return render_template('summary.html', total_services_clinic=total_services_clinic,
                               total_amount_clinic=total_amount_clinic, department_stats=department_stats,
                               doctor_stats=doctor_stats)


@app.route('/search', methods=['GET', 'POST'])
def search_doctor():
    if request.method == 'POST':
        specialization_id = request.form['specialization']
        sex_id = request.form['sex']
        doctors = Doctors.query.filter_by(specialization_id=specialization_id, sex_id=sex_id).paginate(per_page=20)
        return render_template('search_doctor_results.html', doctors=doctors)

    specializations = Specialization.query.all()
    sexes = Sex.query.all()
    return render_template('search_doctor.html', specializations=specializations, sexes=sexes)


if __name__ == "__main__":
    app.run(debug=True)
