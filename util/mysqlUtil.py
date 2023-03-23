# pip install mysql-connector-python
import mysql.connector

class MySQLTool:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        self.conn = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.conn.cursor()

    def disconnect(self):
        self.cursor.close()
        self.conn.close()

    def insert_journal(self, journal_id, ISSN, journal_name, Impact_factor, seif_c_r, h_index, cite_score, cs_m_cate, cs_s_cate, cs_division, cs_rank,
         cs_percent, j_intro, j_web, j_contribute, isOA, research_dirction, country, language, period, wos_district,
         cas_warn, major_cate, sub_cate, cas_district, isTop, isSummarize, r_speed, em_rate):
        j_intro = j_intro.replace("'", "''")
        self.cursor.execute(f"SELECT * FROM journalinfo WHERE journal_id='{journal_id}'")
        result = self.cursor.fetchall()
        if len(result) == 0:
            sql = """
                        INSERT INTO journalinfo (
                            journal_id,ISSN, journal_name, Impact_factor, seif_c_r, h_index, cite_score, 
                            cs_m_cate, cs_s_cate, cs_division, cs_rank, cs_percent, j_intro, 
                            j_web, j_contribute, isOA, research_dirction, country, language, period, 
                            wos_district, cas_warn, major_cate, sub_cate, cas_district, isTop, 
                            isSummarize, r_speed, em_rate
                        )
                        VALUES ('%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')
                    """ % (
            journal_id, ISSN, journal_name, Impact_factor, seif_c_r, h_index, cite_score, cs_m_cate, cs_s_cate,
            cs_division, cs_rank,
            cs_percent, j_intro, j_web, j_contribute, isOA, research_dirction, country, language, period, wos_district,
            cas_warn, major_cate, sub_cate, cas_district, isTop, isSummarize, r_speed, em_rate)
            self.cursor.execute(sql)
            self.conn.commit()
        else:
            self.update_journal(journal_id, ISSN, journal_name, Impact_factor, seif_c_r, h_index, cite_score, cs_m_cate, cs_s_cate, cs_division, cs_rank,
         cs_percent, j_intro, j_web, j_contribute, isOA, research_dirction, country, language, period, wos_district,
         cas_warn, major_cate, sub_cate, cas_district, isTop, isSummarize, r_speed, em_rate)


    def update_journal(self, journal_id, ISSN, journal_name, Impact_factor, seif_c_r, h_index, cite_score, cs_m_cate, cs_s_cate,
            cs_division, cs_rank,
            cs_percent, j_intro, j_web, j_contribute, isOA, research_dirction, country, language, period, wos_district,
            cas_warn, major_cate, sub_cate, cas_district, isTop, isSummarize, r_speed, em_rate):
        sql = """
            UPDATE journalinfo SET 
                ISSN = '%s', journal_name = '%s', Impact_factor = '%s', seif_c_r = '%s', 
                h_index = '%s', cite_score = '%s', cs_m_cate = '%s', cs_s_cate = '%s', 
                cs_division = '%s', cs_rank = '%s', cs_percent = '%s', j_intro = '%s', j_web = '%s', 
                j_contribute = '%s', isOA = '%s', research_dirction = '%s', country = '%s', 
                language = '%s', period = '%s', wos_district = '%s', cas_warn = '%s', 
                major_cate = '%s', sub_cate = '%s', cas_district = '%s', isTop = '%s', 
                isSummarize = '%s', r_speed = '%s', em_rate = '%s'
            WHERE journal_id = '%s'
        """% (ISSN, journal_name, Impact_factor, seif_c_r, h_index, cite_score, cs_m_cate, cs_s_cate,
            cs_division, cs_rank,
            cs_percent, j_intro, j_web, j_contribute, isOA, research_dirction, country, language, period, wos_district,
            cas_warn, major_cate, sub_cate, cas_district, isTop, isSummarize, r_speed, em_rate,journal_id)

        self.cursor.execute(sql)
        self.conn.commit()

    def select_journal_id(self):
        self.cursor.execute("""
            SELECT journal_id FROM journalinfo
        """)
        return self.cursor.fetchall()
