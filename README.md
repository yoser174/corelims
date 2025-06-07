# corelims

coreLIS is a Laboratory Information Management Systems

DEMO:
http://corelims.xyz
user: lab
pass: lab

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

- atau: django-admin loaddata corelims/fixtures/parameters.json

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

# Ubuntu install

# 1. install jasper

Step 1. Login to the server

You can check whether you have the proper Ubuntu version installed on your server with the following command:

# lsb_release -a

You should get this output:

No LSB modules are available.
Distributor ID: Ubuntu
Description: Ubuntu 22.04.2 LTS
Release: 22.04
Codename: jammy
Before starting, you have to make sure that all Ubuntu OS packages installed on the server are up to date. You can do this by running the following commands:

# apt update -y

Step 2. Create a System User

There is an option to install Jasper Reports on an Ubuntu 22.04 machine without using the installer; we are going to install it manually. First, we need to install Tomcat, and we will install Tomcat under a new system user. Let’s execute the command below to add a new system user.

# useradd -r tomcat -m -d /opt/tomcat --shell /bin/bash

Step 3. Install Tomcat
We created a new system user in the previous step. And now, we are going to install Tomcat in this step. But first, we need to install Java. Let’s run the command below to install default JDK version 11, which is available on the built-in Ubuntu 22.04 repositories by using the following command:

# apt install default-jdk unzip wget nano -y

When writing this tutorial, the latest stable Tomcat version to download is version 9.0.76. You can go to hand check if they release the more recent version. To proceed with the installation, let’s download the binary distribution file first.

# su - tomcat

$ wget https://dlcdn.apache.org/tomcat/tomcat-9/v9.0.105/bin/apache-tomcat-9.0.105.tar.gz -O tomcat-9.0.105.tar.gz
Our user ‘tomcat’ home directory is /opt/tomcat, and the directory was created when we added that user. And, we will install Tomcat under this directory. Let’s extract the downloaded file now.

$ tar -xzvf tomcat-9.0.105.tar.gz -C /opt/tomcat --strip-components=1
Now, the directory /opt/tomcat contains all Tomcat files. You can verify this with this command.

$ ls -lh /opt/tomcat
The command will return an output like this:

tomcat@ubuntu22:~$ ls -lh /opt/tomcat/
total 13M
drwxr-x--- 2 tomcat tomcat 4.0K May 24 21:40 bin
-rw-r----- 1 tomcat tomcat 24K May 8 01:36 BUILDING.txt
drwx------ 2 tomcat tomcat 4.0K May 8 01:36 conf
-rw-r----- 1 tomcat tomcat 6.1K May 8 01:36 CONTRIBUTING.md
drwxr-x--- 2 tomcat tomcat 4.0K May 24 21:40 lib
-rw-r----- 1 tomcat tomcat 56K May 8 01:36 LICENSE
drwxr-x--- 2 tomcat tomcat 4.0K May 8 01:36 logs
-rw-r----- 1 tomcat tomcat 2.3K May 8 01:36 NOTICE
-rw-r----- 1 tomcat tomcat 3.3K May 8 01:36 README.md
-rw-r----- 1 tomcat tomcat 6.8K May 8 01:36 RELEASE-NOTES
-rw-r----- 1 tomcat tomcat 17K May 8 01:36 RUNNING.txt
drwxr-x--- 2 tomcat tomcat 4.0K May 24 21:40 temp
-rw-rw-r-- 1 tomcat tomcat 13M May 8 01:58 tomcat-9.0.105.tar.gz
drwxr-x--- 7 tomcat tomcat 4.0K May 8 01:36 webapps
drwxr-x--- 2 tomcat tomcat 4.0K May 8 01:36 work

Now, exit from user ‘tomcat’ and go back to the root or your sudo user.

$ exit
We need to create a systemd file to manage our Tomcat service. Let’s create systemd service file for Tomcat.

# nano /etc/systemd/system/tomcat.service

Paste the following into the systemd service file, then save it.

[Unit]
Description=Apache Tomcat
After=network.target

[Service]
Type=forking

User=tomcat
Group=tomcat

Environment=JAVA_HOME=/usr/lib/jvm/java-1.17.0-openjdk-amd64
Environment=CATALINA_PID=/opt/tomcat/tomcat.pid
Environment=CATALINA_HOME=/opt/tomcat
Environment=CATALINA_BASE=/opt/tomcat
Environment="CATALINA_OPTS=-Xms1024M -Xmx1024M -server -XX:+UseParallelGC"

ExecStart=/opt/tomcat/bin/startup.sh
ExecStop=/opt/tomcat/bin/shutdown.sh

ExecReload=/bin/kill $MAINPID
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
Save the file, exit from nano editor then reload systemd for changes to take effect.

# systemctl daemon-reload

At this point, we are not going to start Tomcat.

## Step 5. Download and Deploy JasperReports

In this step, we will download the Jasper Reports server zipped file and install it manually. When writing this article, the latest available version is 8.2.0. You can check if they have the more recent version at https://sourceforge.net/projects/jasperserver/files/JasperServer/.

# su - tomcat

$ wget https://altushost-swe.dl.sourceforge.net/project/jr-community-installers/Server/TIB_js-jrs-cp_8.2.0_bin.zip?viasf=1 -O jasperreports_8.2.0.zip
Once downloaded, we can extract it directly.

$ unzip jasperreports_8.2.0.zip
Jasper Reports server supports PostgreSQL, MySQL, Oracle, DB2, and SQL servers. In this article, we are going to use MySQL (MariaDB), and we already installed it. To proceed with the Jasper Report configuration file, let’s copy the sample configuration file first.

Let’s copy /opt/jasperreports-server-cp-8.0.0-bin/buildomatic/sampe-conf/mysql.master_properties to buildomatic directory as default_master.properties

$ cp -a jasperreports-server-cp-8.2.0-bin/buildomatic/sample_conf/postgresql_master.properties jasperreports-server-cp-8.2.0-bin/buildomatic/default_master.properties
Now, let’s edit jasperreports-server-cp-8.2.0-bin/buildomatic/default_master.properties

$ nano jasperreports-server-cp-8.2.0-bin/buildomatic/default_master.properties
Add the two lines below

CATALINA_HOME = /opt/tomcat
CATALINA_BASE = /opt/tomcat
Then, replace the database configuration part with the following, and make sure the username and database match with the one we created earlier.

dbHost=localhost
dbUsername=corelims
dbPassword=corelims
And set encrypt to true.

encrypt = true
It should look like this:

CATALINA_HOME = /opt/tomcat
CATALINA_BASE = /opt/tomcat

dbHost=localhost
dbUsername=master
dbPassword=m0d1fyth15

encrypt = true
Save the file then exit.

Next, let’s enter the buildomatic directory and run the js-install-ce.sh executable file. Prior to running this executable file, make sure Tomcat is NOT running.

$ cd jasperreports-server-cp-8.2.0-bin/buildomatic/
$ ./js-install-ce.sh
This will create databases and deploy jasperserver in Tomcat.

Then, let’s edit /opt/tomcat/conf/catalina.policy file.

$ nano /opt/tomcat/conf/catalina.policy
Append the following into the file.

grant codeBase "file:/groovy/script" {
permission java.io.FilePermission "${catalina.home}${file.separator}webapps${file.separator}
jasperserver-pro${file.separator}WEB-INF${file.separator}classes${file.separator}-", "read";
permission java.io.FilePermission "${catalina.home}${file.separator}webapps${file.separator}
jasperserver-pro${file.separator}WEB-INF${file.separator}lib${file.separator}\*", "read";
permission java.util.PropertyPermission "groovy.use.classvalue", "read";
};

Save the file then exit.

Then, we also need to edit applicationContext.xml file.

$ nano /opt/tomcat/webapps/jasperserver/WEB-INF/applicationContext.xml
Insert these into the reportsProtectionDomainProvider list.

    <bean class="java.io.FilePermission">
        <constructor-arg value="${catalina.home}${file.separator}webapps
        ${file.separator}jasperserver-pro${file.separator}
        WEB-INF${file.separator}classes${file.separator}-"/>
        <constructor-arg value="read"/>
    </bean>
    <bean class="java.io.FilePermission">
        <constructor-arg value="${catalina.home}${file.separator}webapps
        ${file.separator}jasperserver-pro${file.separator}WEB-INF
        ${file.separator}lib${file.separator}*"/>
        <constructor-arg value="read"/>
    </bean>

Once completed, you can start Tomcat and wait for a few moments until everything is running.

$ exit

# systemctl start tomcat

Then, you can navigate to http://YOUR_SERVER_IP_ADDRESS:8080/jasperserver/ to access JasperReports Server using the default login credentials.

username: jasperadmin
password: jasperadmin
