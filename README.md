# corelims

coreLIS is a Laboratory Information Management Systems

# hardware requirement

Server

Client

Barcode Printer
Zebra Printer 

# cara install

1. install Python 3.6 64bit ke c:\python36
   1.a setup virtual envirtoment

- install virtual env: python install virtualenv
- buat venv baru: virtualenv -p c:\python36\python.exe venv
- activate virtualenv: venv\script\activate

  1.b install pip package

- intall requirements: pip install -r requirements.txt

2. install MySQL community 5.7 64bit
   2.a buat login mysql corelism pass: corelism (full access insert, delete, create,...)

- lakukan migrate: python manage.py migrate

  2.b buat login admin

- create login admin: python manage.py makesuperuser
- buat username dan password

3. collect statics dan running web app

- run python manage.py collectstatic
- run python manage.py runserver
- buka applikasi ke http://localhost:8000/

4. Penggunaan

- tambahkan master data minimum di Administrasi: http://localhost:8000/admin

  4.1 Gender

- tambahkan Gender pasien, misalkan Laki-Laki kode: L, external kode: L

  4.2 Service

- untuk tipe jenis pasien, misalkan Rawat inap

  4.3 Origin

- untuk asal pasien misalkan atau ruangan, misalkan Melati

  4.4 Priority

- untuk prioritas order, misalkan Rutin, Cito, ..

  4.4 Insurance

- untuk ansuransi pasien, misalkan BPJS

  4.5 Doctor

- masukan data dokter perujuk pasien, misalkan: dr.Test

  4.5 Diagnosis

- tambahkan daftar diagnosa pasien, misalkan: Anemia, DBD, dll..

  4.6 Specimen

- tambahkan specimen sampel, mislakan: EDTA, Serum ..

  4.7 Super group

- tambahkan super group untuk grouping test, misakan Hematologi

  4.8 Group

- tambahkan grouping untuk group test, misalkan darah rutin

  4.9 Test

- tambahkan test pemeriksaan, contohnya: hematologi, isi tarif nya berdasarkan prioiry, dan isi medical.service unntuk medical service rate (biaya jasa)
- tambahkan test parameter untuk mengisi metod, dan decimal place
- tambahkan test ref.ranges untuk nilai rujukan

  4.10 Parameter

- tambahkan parameter minimum
  name char_value ket.
  ORG_LAB_NAME Lab test nama lab
  ORG_LAB_ADDRESS jl. test alamat jalan lab
  ORG_LAB_CITY Jakarta kota

numeric parameter
name num_value ket.
MENU_BTN_PRINT_RECEIPT 1 1: aktif print receipt, 0: non-aktif
MENU_BTN_PRINT_BILL 1 1: aktif print nota, 0: non-aktif
MENU_BTN_PRINT_WORKLIST 1 1: aktif print worklist, 0: non-aktif
MENU_BTN_PRINT_BARCODE 1 1: akifkan menu print barcode, 0: non-aktif

4.11 Label printer

- tambahkan minimal satu label printer, misal: Label Rutin, com serial: COM10

5. Penggunaan

5.1 Billing > Patient

- untuk mebuat Pasien, buat pasien baru

  5.2 Billing > Order

- untuk membuat order pasien

  5.2 Print Label

- agar sample bisa di receive, wajib klik print label

  5.3 Sample Receive

- untuk receive sampel, untuk mencatat waktu sample sampai di lab, atau memberikan catatan terhadap kondisi sampel

  5.4 Workarea

- area kerja laboratorium, misalkan area hema, akan mucul order yang ada pemeriksaan hematologi saja, dst.

  5.5 All area

- semua order test akan dimunculkan di menu ini

6. Reporting

6.1 Reporting menggunakan Jasper Server dan designer menggunakan jasper studio

- download jasper Studio dari: `https://onboardcloud.dl.sourceforge.net/project/jasperstudio/JaspersoftStudio-6.20.3/js-studiocomm_6.20.3_windows_x86_64.exe`
- download jasper Server dari: `https://onboardcloud.dl.sourceforge.net/project/jasperserver/JasperServer/JasperReports%20Server%20Community%20Edition%208.2.0/TIB_js-jrs-cp_8.2.0_win_x86_64.exe`

  6.2 install

- install jasper server dan jasper studio
- koneksikan jasper studio ke jasper server
- import backup jasper server dari export.zip

# PRODUCTION

install IIS pada windows

link : `https://blog.nonstopio.com/deploy-django-application-on-windows-iis-server-93aee2864c41?gi=3c411d623842`

Change setttings.py

- DEBUG = False
- change SECRET_KEY
  running: python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ganti output dengan generate screte_key ke SECRET_KEY
