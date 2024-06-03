from django.db import models
from django.contrib.auth.models import User

class Tabyouin(models.Model):  # 他病院表
    # 他病院ID（主キー）
    tabyouinid = models.CharField(max_length=8, primary_key=True)
    # 他病院名
    tabyouinmei = models.CharField(max_length=64)
    # 他病院住所
    tabyouinaddress = models.CharField(max_length=64)
    # 他病院電話番号
    tabyouintel = models.CharField(max_length=13)
    # 資本金
    tabyouinshihonkin = models.IntegerField()
    # 救急フラグ
    kyukyu = models.IntegerField()

class Employee(models.Model):
    empid = models.CharField(max_length=8, primary_key=True)
    empfname = models.CharField(max_length=64)
    emplname = models.CharField(max_length=64)
    emppasswd = models.CharField(max_length=256)
    emprole = models.IntegerField()


class Patient(models.Model):  # 患者表
    # 患者ID（主キー）
    patid = models.CharField(max_length=8, primary_key=True)
    # 患者名（名）
    patfname = models.CharField(max_length=64)
    # 患者名（姓）
    patlname = models.CharField(max_length=64)
    # 保険証名記号番号
    hokenmei = models.CharField(max_length=64)
    # 保険証有効期限
    hokenexp = models.DateField()

class Medicine(models.Model):  # 薬剤表
    # 薬剤ID（主キー）
    medicineid = models.CharField(max_length=8, primary_key=True)
    # 薬剤名
    medicinename = models.CharField(max_length=64)
    # 単位
    unit = models.CharField(max_length=8)

class Treatment(models.Model):  # 処置表
    # 処置ID（主キー）
    treatmentid = models.CharField(max_length=8, primary_key=True)
    # 患者ID（外部キー）
    patid = models.ForeignKey(Patient, on_delete=models.CASCADE)
    # 薬剤ID（外部キー）
    medicineid = models.ForeignKey(Medicine, on_delete=models.CASCADE)
    # 投薬量
    quantity = models.IntegerField()
    # 処置日
    treatmentdate = models.DateField()
