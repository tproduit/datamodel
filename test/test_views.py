import unittest
import os

import psycopg2
import psycopg2.extras
import decimal
import copy

from utils import DbTestBase

class TestViews(unittest.TestCase, DbTestBase):

    @classmethod
    def tearDownClass(cls):
        cls.conn.rollback()

    @classmethod
    def setUpClass(cls):
        pgservice=os.environ.get('PGSERVICE')
        if not pgservice:
          pgservice='pg_qgep'
        cls.conn = psycopg2.connect("service={service}".format(service=pgservice))


    def test_vw_reach(self):
        row = {
                'clear_height': 100,
                'coefficient_of_friction': 10,
                'identifier': '20'
        }

        obj_id = self.insert_check('vw_reach', row)

        row = {
                'clear_height': 200,
                'coefficient_of_friction': 20,
                'identifier': '10'
        }

        self.update_check('vw_reach', row, obj_id)

    def test_vw_overflow_prank_weir(self):
        row = {
                'identifier': 'STAR20',
                'level_max': decimal.Decimal('300.123')
        }

        obj_id = self.insert_check('vw_overflow_prank_weir', row)

        row = {
                'identifier': '30',
                'level_max': decimal.Decimal('400.321')
        }

        self.update_check('vw_overflow_prank_weir', row, obj_id)

    def test_vw_qgep_reach(self):
        row = {
                'clear_height': 100,
                'coefficient_of_friction': 10,
                'ws_identifier': 'pra',
                'ch_usage_current': 4514
        }

        obj_id = self.insert_check('vw_qgep_reach', row)

        row = {
                'clear_height': 200,
                'coefficient_of_friction': 20,
                'ws_identifier': '10',
                'ch_usage_current': 4516
        }

        self.update_check('vw_qgep_reach', row, obj_id)

    def test_vw_qgep_wastewater_structure(self):
        row = {
                'identifier': '20',
                'ws_type': 'manhole',
                                'situation_geometry': '01040000A0080800000100000001010000800000000020D6434100000000804F324100000000004CCD40', # SELECT ST_SetSRID(ST_GeomFromText('MULTIPOINTZ(2600000 1200000 15000)'), 2056)
                'co_material': 5355,
                'wn_backflow_level': decimal.Decimal('100.000')
        }

        expected_row = copy.deepcopy(row)
        # be aware the Z variable is overwritten by NaN because co_level is NULL
        expected_row['situation_geometry'] = '01040000A0080800000100000001010000800000000020D6434100000000804F3241000000000000F87F' # SELECT ST_SetSRID(ST_Collect(ST_MakePoint(2600000, 1200000, 'NaN')), 2056)
        
        obj_id = self.insert_check('vw_qgep_wastewater_structure', row, expected_row)

        row = {
                'identifier': '10',
                'ws_type': 'special_structure',
                'co_material': 233,
                'ss_upper_elevation': decimal.Decimal('405.000'),
        }

        self.update_check('vw_qgep_wastewater_structure', row, obj_id)

        cur = self.cursor()

        cur.execute("SELECT * FROM qgep_od.wastewater_networkelement NE LEFT JOIN qgep_od.wastewater_node NO ON NO.obj_id = NE.obj_id WHERE fk_wastewater_structure='{obj_id}' ".format(obj_id=obj_id))
        row = cur.fetchone()

        assert row['backflow_level'] == decimal.Decimal('100.000')

if __name__ == '__main__':
    unittest.main()
