import uuid
from datetime import timezone, date

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Employee,Tabyouin,Patient,Medicine,Treatment
import logging
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password,check_password
from django.db import IntegrityError
from uuid import uuid4

logger = logging.getLogger(__name__)

def login_home(request):
    return render(request, 'kadai1/login.html')

def login_view(request):
    if request.method == 'POST':
        userid = request.POST.get('userid')
        password = request.POST.get('password')

        if not userid or not password:
            logger.debug('ユーザーIDまたはパスワードが入力されていません。')
            messages.error(request, 'ユーザーIDとパスワードは必須です。')
            return render(request, 'kadai1/login.html')

        if len(userid) > 20 or len(password) > 128:
            logger.debug('ユーザーIDまたはパスワードの長さが不正です。')
            messages.error(request, 'ユーザーIDまたはパスワードの長さが不正です。')
            return render(request, 'kadai1/login.html')

        try:
            employee = Employee.objects.get(empid=userid)
            logger.debug(f'従業員が見つかりました: {employee.empid}')

            if employee.emprole == 1:  # 管理者の場合は平文のパスワードを使用
                if password == employee.emppasswd:
                    logger.debug('管理者のパスワードチェックに成功しました。')
                    request.session['employee_id'] = employee.empid
                    request.session['employee_role'] = employee.emprole
                    return redirect('admin_home')
                else:
                    logger.debug('管理者のパスワードチェックに失敗しました。')
                    messages.error(request, 'ユーザーIDまたはパスワードが無効です。')
            else:
                if check_password(password, employee.emppasswd):
                    logger.debug('パスワードチェックに成功しました。')
                    request.session['employee_id'] = employee.empid
                    request.session['employee_role'] = employee.emprole

                    if employee.emprole == 2:  # 医師
                        return redirect('doctor_home')
                    elif employee.emprole == 3:  # 受付
                        return redirect('reception_home')
                    else:
                        logger.debug('無効な役割です。')
                        messages.error(request, '無効な役割です。')
                else:
                    logger.debug('パスワードチェックに失敗しました。')
                    messages.error(request, 'ユーザーIDまたはパスワードが無効です。')

        except Employee.DoesNotExist:
            logger.debug('従業員が存在しません。')
            messages.error(request, 'ユーザーIDまたはパスワードが無効です。')

        except Exception as e:
            logger.error(f'ログイン中に予期しないエラーが発生しました: {e}')
            messages.error(request, '予期しないエラーが発生しました。もう一度お試しください。')

    return render(request, 'kadai1/login.html')

def admin_home(request):
    if request.session.get('employee_role') == 1:
        return render(request, 'kadai1/administrator/administrator.html')
    else:
        return redirect('login')

def doctor_home(request):
    if request.session.get('employee_role') == 2:
        return render(request, 'kadai1/doctor/doctor.html')
    else:
        return redirect('login')

def reception_home(request):
    if request.session.get('employee_role') == 3:
        return render(request, 'kadai1/reception/reception.html')
    else:
        return redirect('login')

def register_view(request):
    if request.method == 'POST':
        empid = request.POST.get('empid')
        emplname = request.POST.get('emplname')
        empfname = request.POST.get('empfname')
        emppasswd = request.POST.get('emppasswd')
        emppasswd_confirm = request.POST.get('emppasswd_confirm')
        emprole = request.POST.get('emprole')

        if emppasswd != emppasswd_confirm:
            messages.error(request, 'パスワードが一致しません。')
            return render(request, 'kadai1/administrator/EmployeeRegistration.html')

        if Employee.objects.filter(empid=empid).exists():
            messages.error(request, 'ユーザーIDが既に存在します。')
            return render(request, 'kadai1/administrator/EmployeeRegistration.html')

        # 確認画面にデータを渡す
        context = {
            'empid': empid,
            'emplname': emplname,
            'empfname': empfname,
            'emppasswd': emppasswd,
            'emprole': emprole,
        }
        return render(request, 'kadai1/administrator/EmployeeRegistrationConfirm.html', context)

    return render(request, 'kadai1/administrator/EmployeeRegistration.html')

def register_complete(request):
    if request.method == 'POST':
        empid = request.POST['empid']
        emplname = request.POST['emplname']
        empfname = request.POST['empfname']
        emppasswd = request.POST['emppasswd']
        emprole = request.POST['emprole']

        try:
            if emprole == 1:
                Employee.objects.create(
                    empid=empid,
                    emplname=emplname,
                    empfname=empfname,
                    emppasswd=emppasswd,  # パスワードをハッシュ化
                    emprole=emprole
                )
                messages.success(request, '従業員が正常に登録されました。')
                return redirect('admin_home')
            else:
                Employee.objects.create(
                    empid=empid,
                    emplname=emplname,
                    empfname=empfname,
                    emppasswd=make_password(emppasswd),  # パスワードをハッシュ化
                    emprole=emprole
                )
                messages.success(request, '従業員が正常に登録されました。')
                return redirect('admin_home')
        except IntegrityError:
            messages.error(request, 'ユーザーIDが既に存在します。')
            return render(request, 'kadai1/administrator/EmployeeRegistration.html')
    return redirect('register')

def namechange_view(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        if user_id:
            try:
                employee = Employee.objects.get(empid=user_id)
                return render(request, 'kadai1/administrator/NameChange.html', {'employee': employee})
            except Employee.DoesNotExist:
                messages.error(request, 'ユーザーIDが見つかりません。')
                return render(request, 'kadai1/administrator/NameChange.html')
        else:
            last_name = request.POST.get('last_name')
            first_name = request.POST.get('first_name')
            if not last_name or not first_name:
                messages.error(request, '姓もしくは名が空欄です。')
                return render(request, 'kadai1/administrator/NameChange.html', {'employee': None})
            else:
                user_id = request.POST.get('employee_user_id')
                employee = get_object_or_404(Employee, empid=user_id)
                employee.emplname = last_name
                employee.empfname = first_name
                try:
                    employee.save()
                    messages.success(request, '従業員情報が更新されました。')
                    return redirect('namechange')
                except IntegrityError:
                    messages.error(request, '更新中にエラーが発生しました。')

    return render(request, 'kadai1/administrator/NameChange.html')

def namechange_success(request):
    return HttpResponse("Name changed successfully")


def other_hospital_register_view(request):
    if request.method == 'POST':
        tabyouinid = request.POST.get('tabyouinid')
        tabyouinmei = request.POST.get('tabyouinmei')
        tabyouinaddress = request.POST.get('tabyouinaddress')
        tabyouintel = request.POST.get('tabyouintel')
        tabyouinshihonkin = request.POST.get('tabyouinshihonkin')
        kyukyu = request.POST.get('kyukyu')

        # 入力データの検証
        if not tabyouinid or not tabyouinmei or not tabyouinaddress or not tabyouintel or not tabyouinshihonkin or kyukyu is None:
            messages.error(request, '全てのフィールドを正しく入力してください。')
            return render(request, 'kadai1/administrator/OtherHospitalRegistration.html')

        if not tabyouinid.isdigit():
            messages.error(request, '他病院IDは数値を入力してください。')
            return render(request, 'kadai1/administrator/OtherHospitalRegistration.html')

        if not tabyouintel.isdigit():
            messages.error(request, '他病院電話番号は数字、（）、-を入力してください。')
            return render(request, 'kadai1/administrator/OtherHospitalRegistration.html')

        try:
            tabyouinshihonkin_value = float(tabyouinshihonkin)
        except ValueError:
            messages.error(request, '資本金は数値を入力してください。')
            return render(request, 'kadai1/administrator/OtherHospitalRegistration.html')

        if kyukyu not in ['0', '1']:
            messages.error(request, '救急フラグは0または1を入力してください。')
            return render(request, 'kadai1/administrator/OtherHospitalRegistration.html')

        try:
            # 他病院の登録
            Tabyouin.objects.create(
                tabyouinid=tabyouinid,
                tabyouinmei=tabyouinmei,
                tabyouinaddress=tabyouinaddress,
                tabyouintel=tabyouintel,
                tabyouinshihonkin=tabyouinshihonkin_value,
                kyukyu=kyukyu
            )
            messages.success(request, '他病院登録が成功しました。')
        except IntegrityError:
            messages.error(request, 'IDが既に登録されています。')
        except Exception as e:
            messages.error(request, 'エラーが発生しました。再試行してください。')

    return render(request, 'kadai1/administrator/OtherHospitalRegistration.html')


def other_hospital_list(request):
    try:
        hospitals = Tabyouin.objects.all()
        if not hospitals.exists():
            messages.warning(request, '表示する病院がありません。')
    except Exception as e:
        messages.error(request, f'エラーが発生しました: {e}')
        hospitals = []

    return render(request, 'kadai1/administrator/ListofOtherHospitals.html', {'hospitals': hospitals})

def search_hospital_by_address(request):
    hospitals = None
    if request.method == 'POST':
        address = request.POST.get('address')
        hospitals = Tabyouin.objects.filter(tabyouinaddress__icontains=address)
    return render(request, 'kadai1/administrator/OtherHospitalAddressSearch.html', {'hospitals': hospitals})

def change_password_view(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if new_password != confirm_password:
            messages.error(request, '新しいパスワードが一致しません。')
            return render(request, 'kadai1/reception/PassChange.html')

        employee_id = request.session.get('employee_id')
        if not employee_id:
            messages.error(request, 'セッションが期限切れです。再度ログインしてください。')
            return redirect('login')

        employee = get_object_or_404(Employee, empid=employee_id)

        # 新しいパスワードをハッシュ化して保存
        employee.emppasswd = make_password(new_password)
        employee.save()
        messages.success(request, 'パスワードが正常に変更されました。')
        return redirect('reception_home')  # ホーム画面にリダイレクト（URLは適宜調整してください）

    return render(request, 'kadai1/reception/PassChange.html')


def patient_register_view(request):
    if request.method == 'POST':
        patid = request.POST.get('patient_id')
        patlname = request.POST.get('last_name')
        patfname = request.POST.get('first_name')
        hokenmei = request.POST.get('insurance_number')
        hokenexp = request.POST.get('expiration_date')

        # 確認画面にデータを渡す
        context = {
            'patid': patid,
            'patlname': patlname,
            'patfname': patfname,
            'hokenmei': hokenmei,
            'hokenexp': hokenexp,
        }
        return render(request, 'kadai1/reception/PatientRegisterConfirm.html', context)

    return render(request, 'kadai1/reception/PatiantRagist.html')


def patient_register_confirm_view(request):
    if request.method == 'POST':
        patid = request.POST.get('patient_id')
        patlname = request.POST.get('last_name')
        patfname = request.POST.get('first_name')
        hokenmei = request.POST.get('insurance_number')
        hokenexp = request.POST.get('expiration_date')

        try:
            Patient.objects.create(
                patid=patid,
                patlname=patlname,
                patfname=patfname,
                hokenmei=hokenmei,
                hokenexp=hokenexp
            )
            messages.success(request, '患者が正常に登録されました。')
            return redirect('reception_home')
        except IntegrityError:
            messages.error(request, '患者IDが既に存在します。')
            return redirect('patient_register')

    return redirect('patient_register')


def insurance_card_change_view(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        patient = get_object_or_404(Patient, patid=patient_id)
        insurance_number = request.POST.get('insurance_number')
        expiration_date = request.POST.get('expiration_date')

        if not insurance_number and not expiration_date:
            messages.error(request, '保険証記号番号か有効期限のいずれかを入力してください。')
            return render(request, 'kadai1/reception/PatientInsuranceCardChange.html', {'patient': patient})

        context = {
            'patient_id': patient.patid,
            'patient_lname': patient.patlname,
            'patient_fname': patient.patfname,
            'insurance_number': insurance_number,
            'expiration_date': expiration_date,
        }
        return render(request, 'kadai1/reception/PatientInsuranceCardChangeConfirm.html', context)

    return render(request, 'kadai1/reception/PatientInsuranceCardChange.html')


def insurance_card_change_confirm_view(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        insurance_number = request.POST.get('insurance_number')
        expiration_date = request.POST.get('expiration_date')

        patient = get_object_or_404(Patient, patid=patient_id)

        if insurance_number:
            patient.hokenmei = insurance_number
        if expiration_date:
            patient.hokenexp = expiration_date

        try:
            patient.save()
            messages.success(request, '保険証情報が正常に変更されました。')
            return redirect('reception_home')
        except IntegrityError:
            messages.error(request, '更新中にエラーが発生しました。')
            return redirect('insurance_card_change')

    return redirect('insurance_card_change')


def search_patient_by_name(request):
    patients = None
    user_role = request.session.get('employee_role')  # ロールをセッションから取得

    if request.method == 'POST':
        last_name = request.POST.get('last_name')
        first_name = request.POST.get('first_name')

        if last_name or first_name:
            query = Patient.objects.all()
            if last_name:
                query = query.filter(patlname__icontains=last_name)
            if first_name:
                query = query.filter(patfname__icontains=first_name)
            patients = query

            if not patients.exists():
                messages.error(request, '該当する患者が見つかりません。')
        else:
            messages.error(request, '姓または名のいずれかを入力してください。')

        if patients:
            if user_role == 2:  # 医師の場合
                return render(request, 'kadai1/doctor/PatientNameSearchDoctor.html', {'patients': patients})
            elif user_role == 3:  # 受付の場合
                return render(request, 'kadai1/reception/PatientNameSearchReception.html', {'patients': patients})

    if user_role == 2:
        template_name = 'kadai1/doctor/PatientNameSearchDoctor.html'
    else:
        template_name = 'kadai1/reception/PatientNameSearchReception.html'

    return render(request, template_name, {'patients': patients, 'user_role': user_role})

def search_patient_by_id(request):
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        if patient_id:
            try:
                patient = Patient.objects.get(patid=patient_id)
                # 患者が見つかった場合、投薬指示画面へリダイレクト
                return redirect('medication_instruction', patient_id=patient.patid)
            except Patient.DoesNotExist:
                messages.error(request, '該当する患者が見つかりません。')

    return render(request, 'kadai1/doctor/PatientIDSearch.html')

from django.shortcuts import redirect, render, get_object_or_404
from django.contrib import messages
from .models import Patient, Medicine, Treatment
from uuid import uuid4
from datetime import date

def medication_instruction(request, patient_id):
    patient = get_object_or_404(Patient, patid=patient_id)
    medicines = Medicine.objects.all()
    request.session['current_patient_id'] = patient_id  # 現在の患者IDをセッションに保存

    if request.method == 'POST':
        if 'confirm' in request.POST:
            return redirect('medication_confirmation')

        if 'delete_medication_id' in request.POST:
            delete_medication_id = request.POST.get('delete_medication_id')
            medication_list = request.session.get('medication_list', [])
            medication_list = [item for item in medication_list if item['unique_id'] != delete_medication_id]
            request.session['medication_list'] = medication_list
        else:
            medication_id = request.POST.get('medication')
            quantity = request.POST.get('quantity')

            if not medication_id:
                messages.error(request, '薬剤を選択してください。')
                return render(request, 'kadai1/doctor/MedicationInstruction.html', {
                    'patient': patient,
                    'medicines': medicines,
                    'medication_details': [],
                    'session_data': request.session.items(),
                })

            if not quantity or int(quantity) <= 0:
                messages.error(request, '数量は1以上の数値を入力してください。')
                return render(request, 'kadai1/doctor/MedicationInstruction.html', {
                    'patient': patient,
                    'medicines': medicines,
                    'medication_details': [],
                    'session_data': request.session.items(),
                })

            try:
                medicine = Medicine.objects.get(medicineid=medication_id)
                medication_list = request.session.get('medication_list', [])
                medication_list.append({
                    'unique_id': str(uuid4()),
                    'patient_id': patient_id,
                    'medication_id': medication_id,
                    'medication_name': medicine.medicinename,
                    'quantity': quantity,
                })
                request.session['medication_list'] = medication_list
            except Medicine.DoesNotExist:
                messages.error(request, '指定された薬剤が見つかりません。')

    medication_list = request.session.get('medication_list', [])
    medication_details = [item for item in medication_list if item['patient_id'] == patient_id]

    return render(request, 'kadai1/doctor/MedicationInstruction.html', {
        'patient': patient,
        'medicines': medicines,
        'medication_details': medication_details,
    })

def medication_confirmation(request):
    medication_list = request.session.get('medication_list', [])
    medication_list = [item for item in medication_list if 'patient_id' in item]

    if not medication_list:
        messages.error(request, '薬剤が追加されていません。薬剤を選択してください。')
        return redirect('medication_instruction', patient_id=request.session.get('current_patient_id'))

    patient_id = medication_list[0]['patient_id']
    patient = get_object_or_404(Patient, patid=patient_id)

    if request.method == 'POST':
        if 'confirm_final' in request.POST:
            for item in medication_list:
                Treatment.objects.create(
                    treatmentid=str(uuid4())[:8],
                    patid=patient,
                    medicineid=Medicine.objects.get(medicineid=item['medication_id']),
                    quantity=item['quantity'],
                    treatmentdate=date.today()
                )
            # messages.success(request, f'{patient.patfname} {patient.patlname}に対する薬剤投与指示が正常に登録されました。')
            messages.success(request,
                             f'処置完了しました')
            del request.session['medication_list']
            # 処置完了後、再度薬剤投与指示画面に戻る
            return redirect('medication_instruction', patient_id=patient.patid)
        elif 'delete' in request.POST:
            delete_medication_id = request.POST.get('delete')
            medication_list = [item for item in medication_list if item['unique_id'] != delete_medication_id]
            request.session['medication_list'] = medication_list
            if not medication_list:
                messages.error(request, '薬剤がありません。薬剤を追加してください。')
                return render(request, 'kadai1/doctor/MedicationConfirmation.html', {
                    'medication_details': [],
                    'patient': patient,
                })
        elif 'back' in request.POST:
            if medication_list:
                return redirect('medication_instruction', patient_id=patient.patid)
            else:
                messages.error(request, '薬剤がありません。薬剤を追加してください。')
                return redirect('medication_instruction', patient_id=patient_id)

    medication_details = [
        item for item in medication_list
    ]

    return render(request, 'kadai1/doctor/MedicationConfirmation.html', {
        'patient': patient,
        'medication_details': medication_details,
    })


def treatment_history(request):
    if request.session.get('employee_role') != 2:
        return redirect('login')

    treatments = None
    patient = None

    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')
        if patient_id:
            try:
                patient = Patient.objects.get(patid=patient_id)
                treatments = Treatment.objects.filter(patid=patient).order_by('-treatmentdate')

                if not treatments.exists():
                    messages.error(request, 'この患者に処置を行ったことはありません。')
                    treatments = None
            except Patient.DoesNotExist:
                messages.error(request, '未登録の患者IDです。')

    return render(request, 'kadai1/doctor/TreatmentHistory.html', {
        'treatments': treatments
    })

