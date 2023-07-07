###
#
# Fix:
#   20181002    - update search for mapping test to make query faster
#   20181114    - insert result got more than one mapping, try to search each mapping per sample
#   20190309    - fix if rounding 0, will xx.0 fix with add int(xx) if decimal pace is 0
#   20190330    - add result conversion based on script SQL from mapping test
#   20190413    - fix error when convert decimal place
#   20190608    - fix jika SQL Script untuk convert hasil error, kembalikan aslinya ke awal
#   20190713    - fix rule engine, dengan tambahkan str untuk hasil variabel
#   20190720    - jika tidak terima nilai normal dari alat, maka generate dari master nilai normal
#   20230708    - fix query python 3

import logging
import MySQLdb
from datetime import datetime
import time,sys
from dateutil.relativedelta import relativedelta

VERSION  = '0.0.10'


class my_db(object):
    username = 'corelab_comm'
    password = 'corelab_comm'

    def __init__(self,server,db):
        logging.debug('start my_db host[%s] db[%s]' % (server,db))
        # mysql connection
        self.my_conn = None
        self.server = server
        self.db = db
        logging.info('my_db version [%s]' % VERSION)
        self.last_insert_id = ''

    def connect(self):
        self.my_conn = MySQLdb.connect(host=self.server,
                  user=self.username,
                  passwd=self.password,
                  db=self.db)

    def close(self):
        self.my_conn.close()


    def is_float(self,res_value):
        logging.info('check is float [%s]' % res_value)
        try:
            fl = float(str(res_value))
            logging.info('True')
            return True
        except:
            logging.info('False')
            return False


    def costum_flag_range(self,tes_ref,tes_unit,tes_flag):
        tes_ref = str(tes_ref).replace('-',' - ')
        tes_unit = str(tes_unit).replace('*','^')
        tes_flag = tes_flag
        return tes_ref,tes_unit,tes_flag


    def my_select(self,sql):
        my_conn = MySQLdb.connect(host=self.server,
                  user=self.username,
                  passwd=self.password,
                  db=self.db)
        logging.info(sql)
        cursor = my_conn.cursor()
        try:
            cursor.execute(sql)
            res = cursor.fetchall()
            logging.info(res)
            my_conn.close()
            return res
        except MySQLdb.Error as e:
            logging.error(e)
            my_conn.close()


    def my_insert(self,sql):
        insert_id = '0'
        
        my_conn = MySQLdb.connect(host=self.server,
                  user=self.username,
                  passwd=self.password,
                  db=self.db)
        logging.info(sql)
        cursor = my_conn.cursor()
        try:
            cursor.execute(sql)
            
            cr_last = my_conn.cursor()
            logging.info('get last insert id')

            insert_id = my_conn.insert_id()
            my_conn.commit()
            my_conn.close()
            logging.info('insert_id [%s]' % str(insert_id))
            self.last_insert_id = insert_id
            return insert_id
        except MySQLdb.Error as e:
            logging.error(e)
            self.my_conn.rollback()
            my_conn.close()

    def my_update(self,sql):
        my_conn = MySQLdb.connect(host=self.server,
                  user=self.username,
                  passwd=self.password,
                  db=self.db)
        logging.info(sql)
        cursor = my_conn.cursor()
        try:
            cursor.execute(sql)
            my_conn.commit()
            my_conn.close()
            return cursor.lastrowid
        except MySQLdb.Error as e:
            logging.error(e)
            my_conn.rollback()
            my_conn.close()


    def insert_order_hist(self,order_id,test_id,tes_result,tes_ref,tes_unit,tes_flag):
        inst_name = '<?>'
        test_name = '<?>'
        q_data = self.my_select(" SELECT name FROM corelab_instruments WHERE id = '%s' " % self.instrument_id)
        if len(q_data)>0:
            inst_name = q_data[0][0]
        q_data = self.my_select(" SELECT name FROM corelab_tests WHERE id = '%s' " % test_id)
        if len(q_data)>0:
            test_name = q_data[0][0]

        act_txt = "Result %s with ref.range[%s], unit[%s] and flag[%s] set for analyt %s " % (tes_result,tes_ref,tes_unit,tes_flag,test_name)
                    
        self.my_insert(" INSERT corelab_historyorders (action_code,action_user,action_text,action_date,lastmodification,order_id,test_id)\
                       VALUES ('RESENTRY','%s','%s',NOW(),NOW(),'%s','%s') " %
                       (inst_name,act_txt,order_id,test_id))
        

    def get_test_array(self,sample_no,instrument_id):
        try:
            logging.debug('check if sample exist')
            SQL = """select count(*)
            from corelab_ordersamples
            where
            sample_no = '{sample_no}'"""
            SQL = SQL.format(sample_no=sample_no)
            logging.debug(SQL)
            g_or_id = self.my_select(SQL)
            or_id = g_or_id[0][0]

            if or_id == 0:
                logging.warning('Sample id [%s] does not exists.' % sample_no)
                return False,[]
            
            logging.info('order found [%s]' % or_id)
            SQL = """select order_id
            from corelab_ordersamples
            where
            sample_no = '{sample_no}'"""
            SQL = SQL.format(sample_no=sample_no)
            logging.debug(SQL)
            g_or_id = self.my_select(SQL)
            or_id = g_or_id[0][0]

            logging.debug('checking test order.id[%s] for instrument.id[%s]...' % (or_id,instrument_id))
            SQL = """SELECT DISTINCT corelab_instrumenttests.test_code
            FROM corelab_orderresults
            LEFT JOIN corelab_ordersamples ON corelab_orderresults.sample_id = corelab_ordersamples.id
            LEFT JOIN corelab_instrumenttests ON corelab_orderresults.test_id = corelab_instrumenttests.test_id
            WHERE
            corelab_ordersamples.order_id = '{or_id}' 
            AND corelab_orderresults.validation_status = 0
            AND corelab_instrumenttests.instrument_id = {instrument_id}"""
            SQL = SQL.format(or_id,instrument_id)
            logging.debug(SQL)            
            data = self.my_select(SQL)
            return True,data
        except Exception as e:
            logging.error('Error [%s]' % str(e))
            return []


    def set_status_batch(self,sample_no,status):
        try:
            logging.info('trying to get tests..')
            g_or_id = self.my_select(" select id \
                        from corelab_ordersamples \
                        where \
                        sample_no = '%s' " % sample_no)

            for os_id in g_or_id:
                self.my_update(" update corelab_instrumentbatch set status = '%s' where order_sample_id = '%s' " % (status,os_id[0]))
            return True
        except Exception as e:
            logging.error('Error [%s]' % str(e))
            return False
        
        


    def get_sample_batch(self,instrument_id,status=0):
        try:
            logging.info('trying to get samples..')
            data = self.my_select(" select os.sample_no \
from corelab_instrumentbatch ib \
left join corelab_ordersamples os on ib.order_sample_id = os.id \
where \
ib.instrument_id = %s \
and ib.status = %s " % (instrument_id,status))
            return data
        except Exception as e:
            logging.error('Error [%s]' % str(e))
            return []

    def get_barcode_id(self,sample_no):
        try:
            data = self.my_select(" SELECT corelab_ordersamples.id,corelab_ordersamples.order_id,corelab_ordersamples.specimen_id,corelab_specimens.name \
                    FROM corelab_ordersamples \
                    LEFT JOIN corelab_specimens ON corelab_ordersamples.specimen_id = corelab_specimens.id \
                    WHERE corelab_ordersamples.sample_no =  '%s' " %
                                  sample_no)

            sid = ''
            ordid = ''
            specid = ''
            specname = ''

            logging.debug(data[0][0])

            if len(data)>0:
                sid = data[0][0]
                ordid = data[0][1]
                specid = data[0][2]
                specname = data[0][3]

            logging.debug('(%s,%s,%s,%s)' % (sid,ordid,specid,specname))
            
            return sid,ordid,specid,specname
        except Exception as e:
            logging.error('Error [%s]' % str(e))
            return None,None,None,None
        
    def get_patient_id(self,sample_no):
        SQL = """SELECT corelab_patients.patient_id,corelab_patients.name,corelab_patients.dob,corelab_genders.inst_code,corelab_origins.name, 
 corelab_doctors.name,corelab_diagnosis.name, TIMESTAMPDIFF(YEAR, corelab_patients.dob, CURDATE())
FROM 
 corelab_ordersamples
LEFT JOIN corelab_orders ON corelab_ordersamples.order_id = corelab_orders.id
LEFT JOIN corelab_patients ON corelab_orders.patient_id = corelab_patients.id
LEFT JOIN corelab_genders ON corelab_patients.gender_id = corelab_genders.id
LEFT JOIN corelab_doctors ON corelab_orders.doctor_id = corelab_doctors.id
LEFT JOIN corelab_diagnosis ON corelab_orders.diagnosis_id = corelab_diagnosis.id
LEFT JOIN corelab_origins ON corelab_orders.origin_id = corelab_origins.id
WHERE
corelab_ordersamples.sample_no = '{sample_no}'
"""
        SQL = SQL.format(sample_no=sample_no)
        logging.debug(SQL)
        data = self.my_select(SQL)
        pat_id = ''
        name = ''
        dob = ''
        sex = ''
        doctor = ''
        diagnosis = ''
        origin  = ''
        age_year = ''
        if len(data)>0:
            pat_id = data[0][0]
            name = data[0][1]
            dob = str(data[0][2]).replace('-','')
            sex = data[0][3]
            doctor = data[0][4] or ''
            diagnosis = data[0][5] or ''
            origin = data[0][6] or ''
            age_year = data[0][7]

        return pat_id,name,dob,sex,doctor,diagnosis,origin,age_year
        


    def get_order_id(self,sample_no):
        data = self.my_select(" SELECT order_id FROM corelab_ordersamples WHERE sample_no = '%s' " % sample_no )
        if len(data)>0:
            return data[0][0]
        else:
            logging.warning("sample no [%s] not found." % sample_no)
            return 0

    def create_pantologi_mark(self,result_id):
        flag = None
        
        data_res = self.my_select(" SELECT corelab_results.alfa_result,corelab_orderresults.ref_range,corelab_orderresults.id \
            FROM corelab_results \
            LEFT JOIN corelab_orderresults ON corelab_orderresults.result_id = corelab_results.id \
            WHERE  \
            corelab_results.id = '%s' " %
                                  (result_id))

        
        logging.info(data_res)
        alfa_res = data_res[0][0]
        ref_range = data_res[0][1]
        ordres_id = data_res[0][2]

        # test_id
        data_res = self.my_select("select test_id from corelab_results where id = "+str(result_id))
        test_id = data_res[0][0]
        # gender_id
        data_res = self.my_select("select corelab_patients.gender_id,corelab_patients.dob,corelab_orders.order_date from \
            corelab_results left join corelab_orders on corelab_results.order_id = corelab_orders.id \
            left join corelab_patients on corelab_orders.patient_id = corelab_patients.id  where corelab_results.id = " +str(result_id))
        gender_id = data_res[0][0]
        dob = data_res[0][1]
        order_date = data_res[0][2]

        panic_lower = None
        panic_upper = None

        ref_range = None
        
        if not ref_range:
            lower = ''
            upper = ''
            operator = ''
            operator_value = ''
            ref_range_value = ''
            logging.info('ref reange not found, generate it.')
            ref_range = self.my_select("select count(*) from corelab_testrefranges where any_age = 1 and gender_id is null and  test_id =  "+str(test_id))
            have_data = False
            if ref_range[0][0] > 0:
                logging.info('have data')
                have_data = True
            ref_range = self.my_select("select lower,upper,operator,operator_value,panic_lower,panic_upper from corelab_testrefranges where any_age = 1 and gender_id is null and  test_id =  "+str(test_id))            
            logging.info(have_data)
            if have_data:
                logging.info('got data for any age and gender null')
                lower = ref_range[0][0]
                upper = ref_range[0][1]
                operator = ref_range[0][2]
                operator_value = ref_range[0][3]
                panic_lower = ref_range[0][4]
                panic_upper = ref_range[0][5]
                
                if not operator :
                    ref_range_value = str(lower)+' - '+str(upper) 
                else:
                    ref_range_value = str(operator)+' '+str(operator_value)

                logging.info('ref_range_value [%s]' % ref_range_value)
                ref_range = ref_range_value

            else:
                tmp_ref_range = self.my_select("select count(*) from corelab_testrefranges where any_age = 0 and gender_id = "+str(gender_id)+" and  test_id =  "+str(test_id))
                have_data = False
                if tmp_ref_range[0][0] > 0:
                    logging.info('have data')
                    have_data = True
                tmp_ref_range = self.my_select("select lower,upper,operator,operator_value,panic_lower,panic_upper,age_from,age_from_type,age_to,age_to_type from corelab_testrefranges where any_age = 0 and gender_id = "+str(gender_id)+" and  test_id =  "+str(test_id))                
                if have_data:
                    logging.info('cek maching ref_range based on gender and age..')
                    for ref_data in tmp_ref_range:
                        logging.info(ref_data)
                        lower = ref_data[0]
                        upper = ref_data[1]
                        operator = ref_data[2]
                        operator_value = ref_data[3]
                        tmp_panic_lower = ref_data[4]
                        tmp_panic_upper = ref_data[5]
                        age_from = ref_data[6]
                        age_from_type = ref_data[7]
                        age_to = ref_data[8]
                        age_to_type = ref_data[9]

                        if age_from_type == 'D':
                            logging.info('age from type is Day')
                            if age_from <= relativedelta(order_date,dob).days <= age_to :
                                if not operator :
                                    ref_range_value = str(lower)+' - '+str(upper)
                                else:
                                    ref_range_value = str(operator)+' '+str(operator_value)
                                panic_lower = tmp_panic_lower
                                panic_upper = tmp_panic_upper
                                ref_range = ref_range_value
                                
                        elif age_from_type == 'M':
                            logging.info('age from type is Month')
                            if age_from <= relativedelta(order_date,dob).days <= age_to :
                                if not operator :
                                    ref_range_value = str(lower)+' - '+str(upper)
                                else:
                                    ref_range_value = str(operator)+' '+str(operator_value)
                                panic_lower = tmp_panic_lower
                                panic_upper = tmp_panic_upper
                                ref_range = ref_range_value
                        elif age_from_type == 'Y':
                            logging.info('age from type is Year')
                            if age_from <= relativedelta(order_date,dob).days <= age_to :
                                if not operator :
                                    ref_range_value = str(lower)+' - '+str(upper)
                                else:
                                    ref_range_value = str(operator)+' '+str(operator_value)

                                panic_lower = tmp_panic_lower
                                panic_upper = tmp_panic_upper
                                ref_range = ref_range_value
                        else:
                            logging.info('no matching ref ranges found.')
                            

        
        if self.is_float(alfa_res) and ref_range:
            logging.info('ref_range is [%s]' % ref_range)
            if str(ref_range).find(' - ') > 0:
                logging.info('ref range is range "-" ')
                # range
                range = str(ref_range).split(' - ')
                logging.info(range)
                logging.info(str(float(range[0])))
                logging.info(str(float(range[1])))
                logging.info(str(float(alfa_res)))
                if float(range[0])  <= float(alfa_res) <= float(range[1]):
                    flag = 'N'
                elif float(alfa_res) >= float(range[1]):
                    flag = 'H'
                else:
                    flag = 'L'

                logging.info('flag [%s]' % flag)
            elif '<' in str(ref_range) or '>' in str(ref_range):
                logging.info('ref range has operator.')
                range = str(ref_range).split(' ')
                if str(range[0]) == '>':
                    if float(alfa_res) > float(range[1]):
                        flag = 'N'
                    else:
                        flag = 'L'
                elif str(range[0]) == '<':
                    if float(alfa_res) < float(range[1]):
                        flag = 'N'
                    else:
                        flag = 'H'
                elif str(range[0]) == '>=':
                    if float(alfa_res) >= float(range[1]):
                        flag = 'N'
                    else:
                        flag = 'H'
                elif str(range[0]) == '<=':
                    if float(alfa_res) <= float(range[1]):
                        flag = 'N'
                    else:
                        flag = 'H'

            # checking panic
            logging.info('checking panic value [%s] [%s]' % (str(panic_lower),str(panic_upper)))
            if panic_lower:
                if float(alfa_res) <= panic_lower:
                    flag = 'LL'
            if panic_upper:
                if float(alfa_res) >= panic_upper:
                    flag = 'HH'
                

            # update patologi_mark
            self.my_update(" UPDATE corelab_orderresults SET patologi_mark = '%s', ref_range = '%s'  WHERE id = '%s' " % (flag,ref_range,ordres_id))


    def get_mapping_code_attribut(self,instrument_id,tes_code):
        data = self.my_select(" SELECT id,test_code,result_selection,sql_script,instrument_id,test_id FROM corelab_instrumenttests where instrument_id = %s and test_code = '%s' " % (instrument_id,tes_code) )
        if len(data)>0:
            return True,data[0]
        else:
            logging.warning("test_code [%s] for instrument_id [%s] not found." % (tes_code,instrument_id))
            return False,0
        

    def insert_result(self,sample_no,tes_code,tes_result,tes_ref,tes_unit,tes_flag,instrument_id):
        last_insert_id = 0
        # result conversion
        found,test_attr = self.get_mapping_code_attribut(instrument_id,tes_code)
        if found :
            logging.info('found attribut test [%s]' % str(test_attr))
            # result conversion
            sql_script = str(test_attr[3]).strip()
            if sql_script != 'None':
                try:
                    tmp_tes_result = tes_result
                    logging.info('found SQL script for transform the result [%s]' % sql_script)
                    logging.info('replace <test_result> with [%s]' % str(tes_result))
                    sql_script = str(sql_script).replace('<test_result>',str(tes_result))
                    logging.info('sql_script [%s]' % str(sql_script))
                    res_conv = self.my_select("SELECT %s FROM DUAL" % sql_script)
                    tes_result = str(res_conv[0][0])
                    logging.info('result final [%s]' % str(tes_result))
                except Exception as e:
                    logging.error('Failed when executing SQL script [%s] error [%s]' % (str(sql_script),str(e)))
                    tes_result = tmp_tes_result
                    pass
                    
        ####
        
        order_id = self.get_order_id(sample_no)
        if order_id > 0:
            self.instrument_id = instrument_id
            ts = time.time()
            timestamp = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            # 1. cek mapping instrument
            mapp_inst = self.my_select(" SELECT test_id FROM corelab_instrumenttests WHERE instrument_id = '%s' AND test_code = '%s' " % (self.instrument_id,tes_code))
            # check apakah receive flag and ref_range from instrument
            logging.info('checking if instrument recive flag and ref range from instrument..')
            res = self.my_select(' select receive_ref_ranges from corelab_instruments where id = ' + str(self.instrument_id))
            receive_ref_range = res[0][0]
            logging.info(receive_ref_range)
            logging.info(str(receive_ref_range) == '0')
            if len(mapp_inst)<1:
                logging.warning(' No mapped for test_code [%s] ' % (tes_code))
                return False
            # looping untuk ambil mapping ganda
            for m_test_id in mapp_inst:
                #m_test_id = mapp_inst[0][0]
                # 2. cek sampleid
                mapp_sample_id = self.my_select(" SELECT id FROM corelab_ordersamples WHERE sample_no = '%s' " % sample_no)
                if len(mapp_sample_id)<1:
                    logging.warning(' sample_no [%s] not found ' % (sample_no))
                    return False
                m_sample_id = mapp_sample_id[0][0]
                # 3. test_id vs sample_id for update result
                for m_test_id in mapp_inst:
                    logging.info('searching for test_id [%s]...' % str(m_test_id[0]))
                    data_tes = self.my_select(" SELECT test_id FROM corelab_orderresults WHERE sample_id = '%s' and test_id = '%s' " % (str(m_sample_id),str(m_test_id[0])))
                        
                    if len(data_tes)>0:
                        test_id = data_tes[0][0]
                        logging.info(' Got mapped test_id [%s] for test_code [%s] with result [%s]' % (test_id,tes_code,tes_result))
                        
                        # check decimal place if result is float
                        if self.is_float(tes_result):
                            logging.info('rouding based on decimal place...')
                            try:
                                decimal_place = self.my_select(" SELECT decimal_place FROM corelab_testparameters WHERE test_id = '%s' " % (test_id))
                                if len(decimal_place)>0:
                                    decimal_place = decimal_place[0][0]
                                    logging.info('got decimal_place [%s] try to round from [%s] to [%s]' % (decimal_place,tes_result,round(float(str(tes_result)),int(str(decimal_place)))))
                                    if str(decimal_place) == '0': # interger
                                        tes_result = int(round(float(str(tes_result))))
                                    else:
                                        tes_result = round(float(str(tes_result)),int(str(decimal_place)))
                                    logging.info('rounding to [%s]' % str(tes_result))
                            except Exception as e:
                                logging.error('Error:[%s]' % str(e))
                        # check if order result created
                        d_order_result = self.my_select(" SELECT id FROM corelab_orderresults WHERE order_id = '%s' AND test_id = '%s' " % (order_id,test_id))
                        if len(d_order_result)>0:
                            order_res_id = d_order_result[0][0]
                        else:
                            logging.info('Create new row for insert value.')
                            order_res_id = self.my_insert(" INSERT INTO corelab_orderresults (order_id,test_id,is_header,lastmodification,validation_status,print_status) \
                                VALUES ('%s','%s','%s','%s','%s','%s') " % (order_id,test_id,'0',timestamp,'1','0'))
                        
                        # check mapped flag
                        flag_id = None
                        if tes_flag  !=  '' :
                            logging.info(' check flag mapping [%s]' % tes_flag)
                            data_flag = self.my_select(" SELECT id FROM corelab_instrumentflags WHERE flag_code = '%s' AND instrument_id = '%s' " % (tes_flag,self.instrument_id))
                            logging.info(data_flag)
                            
                            if len(data_flag)>0:
                                logging.info('flag exist, process insert data')
                                #logging.info(data_flag)
                                flag_id = data_flag[0][0]
                                # insert with flag
                                logging.info(" insert result (alfa_result,instrument_id,order_id,test_id,flag_id,lastmodification) values ('%s','%s','%s','%s','%s','%s') " % (tes_result,self.instrument_id,order_id,test_id,flag_id,timestamp)) 
                                last_id = self.my_insert(" INSERT INTO corelab_results (alfa_result,instrument_id,order_id,test_id,flag_id,lastmodification) VALUES ('%s','%s','%s','%s','%s','%s') " % (tes_result,self.instrument_id,order_id,test_id,flag_id,timestamp))
                            else:
                                logging.info('No flag found for [%s]' % tes_flag)
                                # insert without flag
                                logging.info(" insert result (alfa_result,instrument_id,order_id,test_id,lastmodification) values ('%s','%s','%s','%s','%s') " %
                                             (tes_result,self.instrument_id,order_id,test_id,timestamp)) 
                                last_id = self.my_insert(" INSERT INTO corelab_results (alfa_result,instrument_id,order_id,test_id,lastmodification) VALUES ('%s','%s','%s','%s','%s') " %
                                                         (tes_result,self.instrument_id,order_id,test_id,timestamp))


                        else:
                            # insert without flag
                            logging.info(" insert result (alfa_result,instrument_id,order_id,test_id,lastmodification) values ('%s','%s','%s','%s','%s') " %
                                         (tes_result,self.instrument_id,order_id,test_id,timestamp)) 
                            last_id = self.my_insert(" INSERT INTO corelab_results (alfa_result,instrument_id,order_id,test_id,lastmodification) VALUES ('%s','%s','%s','%s','%s') " %
                                                     (tes_result,self.instrument_id,order_id,test_id,timestamp))


                        last_insert_id = self.last_insert_id


                        # update result to inserted value
                        logging.info('last inserted id [%s]' % last_id)
                        logging.info('checking ref range[%s] & flag[%s] ' % (tes_ref,tes_flag))
                        logging.info('Receive ref range from instrument [%s]' % str(receive_ref_range))
                        if (not tes_ref) and str(receive_ref_range) == '1':
                            logging.warning('have ref.renge from insrument but receive_ref_range value is 1. we skip it and generate automaticaly from db.')
                            receive_ref_range = '0'
                        try:
                            b_fail = False
                            if str(receive_ref_range) == '0':
                                logging.info(' we not receive ref_ranges and flag from instrument ')
                                self.my_update(" UPDATE corelab_orderresults SET result_id = '%s', \
                                    validation_status = '1', techval_user = NULL , techval_date = NULL, medval_user = NULL, medval_date = NULL WHERE order_id = '%s' AND test_id = '%s' "
                                           % (last_id,order_id,test_id))

                                # generate patologi_mark
                                logging.info('generate patologi mark...')
                                self.create_pantologi_mark(last_id)

                            elif tes_ref ==  '' and tes_flag  !=  '' and str(receive_ref_range) == '1':
                                logging.info(' instrument not send reference range and flag for result.')
                                self.my_update(" UPDATE corelab_orderresults SET result_id = '%s', unit = '%s',patologi_mark = '%s', \
                                    validation_status = '1', techval_user = NULL , techval_date = NULL, medval_user = NULL, medval_date = NULL WHERE order_id = '%s' AND test_id = '%s' "
                                           % (last_id,tes_unit,tes_flag,order_id,test_id))
                                
                            elif tes_ref  !=   '' and tes_flag == '' and str(receive_ref_range) == '1' :
                                self.my_update(" UPDATE corelab_orderresults SET result_id = '%s', ref_range = '%s', unit = '%s', \
                                    validation_status = '1', techval_user = NULL , techval_date = NULL, medval_user = NULL, medval_date = NULL WHERE order_id = '%s' AND test_id = '%s' "
                                           % (last_id,tes_ref,tes_unit,order_id,test_id))
                                # generate patologi_mark
                                self.create_pantologi_mark(last_id)
                                
                            elif tes_ref  !=   '' and tes_flag  !=  ''  and str(receive_ref_range) == '1':
                                tes_ref,tes_unit,tes_flag = self.costum_flag_range(tes_ref,tes_unit,tes_flag)
                                self.my_update(" UPDATE corelab_orderresults SET result_id = '%s', unit = '%s', ref_range = '%s', patologi_mark = '%s' , \
                                    validation_status = '1', techval_user = NULL , techval_date = NULL, medval_user = NULL, medval_date = NULL WHERE order_id = '%s' AND test_id = '%s' "
                                           % (last_id,tes_unit,tes_ref,tes_flag,order_id,test_id))
                                
                            else:
                                b_fail = True
                                logging.error('Failed update.')

                            if not b_fail:
                                # update history
                                self.insert_order_hist(order_id,test_id,tes_result,tes_ref,tes_unit,tes_flag)
                                return last_insert_id
                        except Exception as e:
                            logging.info('Error:[%s]' % (str(e)))
                            return last_insert_id

            else:
                logging.warning(' No mapped for sample_id [%s] with test_id [%s] at order' % (m_sample_id,m_test_id))
                return last_insert_id
