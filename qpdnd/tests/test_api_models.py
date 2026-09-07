# coding=utf-8
""""
Test for gestionecoordinate API models
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-12-23'
__copyright__ = 'Copyright Gis3w'


from django.test import TestCase
from pydantic import ValidationError
from qpdnd.api.models.gestionecoordinate import AccessoGestioneCoordinate
from qpdnd.api.models.coordinate import Coordinate
from qpdnd.api.models.aggiornamentoaccessi import (
    AccessoAggiornamentiAccessi as AccessoAggiornamento,
)
from qpdnd.api.models.aggiornamentointerni import (
    RichiestaOperazione as RichiestaOperazioneInterni
)
from qpdnd.api.models.aggiornamentoodonimi import (
    TipoOperazione,
    Provvedimento,
    AutPrefettura
)


class TestAccessoGestioneCoordinate(TestCase):
    """Test suite for AccessoGestioneCoordinate model from gestionecoordinate"""

    def test_accesso_valid_data(self):
        """Test AccessoGestioneCoordinate creation with valid data"""
        data = {
            "codcom": "B432",
            "progr_civico": "123",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600",
                "z": "150",
                "metodo": "3"
            }
        }
        accesso = AccessoGestioneCoordinate(**data)
        
        self.assertEqual(accesso.codcom, "B432")
        self.assertEqual(accesso.progr_civico, "123")
        self.assertEqual(accesso.coordinate.x, "13.1022000")
        self.assertEqual(accesso.coordinate.y, "41.8847600")
        self.assertEqual(accesso.coordinate.z, "150")
        self.assertEqual(accesso.coordinate.metodo, "3")

    def test_accesso_valid_codcom_lowercase(self):
        """Test AccessoGestioneCoordinate with lowercase codcom"""
        data = {
            "codcom": "a123",
            "progr_civico": "456",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        accesso = AccessoGestioneCoordinate(**data)
        self.assertEqual(accesso.codcom, "a123")

    def test_accesso_valid_progr_civico_numeric_string(self):
        """Test AccessoGestioneCoordinate with numeric progr_civico as string"""
        data = {
            "codcom": "Z999",
            "progr_civico": "789",
            "coordinate": {
                "x": "12.5",
                "y": "42.0"
            }
        }
        accesso = AccessoGestioneCoordinate(**data)
        self.assertEqual(accesso.progr_civico, "789")

    def test_accesso_invalid_codcom_format(self):
        """Test AccessoGestioneCoordinate with invalid codcom format (too many digits)"""
        data = {
            "codcom": "A1234",  # 4 digits instead of 3
            "progr_civico": "123",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            AccessoGestioneCoordinate(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('codcom' in str(e) for e in errors))

    def test_accesso_invalid_codcom_no_alpha_prefix(self):
        """Test AccessoGestioneCoordinate with invalid codcom (no alphabetic character at start)"""
        data = {
            "codcom": "1234",  # No alpha character
            "progr_civico": "123",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            AccessoGestioneCoordinate(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('codcom' in str(e) for e in errors))

    def test_accesso_invalid_codcom_too_short(self):
        """Test AccessoGestioneCoordinate with invalid codcom (too short)"""
        data = {
            "codcom": "A12",  # Only 2 digits
            "progr_civico": "123",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            AccessoGestioneCoordinate(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('codcom' in str(e) for e in errors))

    def test_accesso_invalid_progr_civico_non_numeric(self):
        """Test AccessoGestioneCoordinate with invalid progr_civico (non-numeric string)"""
        data = {
            "codcom": "B432",
            "progr_civico": "abc",  # Non-numeric
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            AccessoGestioneCoordinate(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('prog_civico' in str(e) for e in errors))

    def test_accesso_invalid_progr_civico_alphanumeric(self):
        """Test AccessoGestioneCoordinate with invalid progr_civico (alphanumeric)"""
        data = {
            "codcom": "B432",
            "progr_civico": "123abc",  # Alphanumeric
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            AccessoGestioneCoordinate(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('prog_civico' in str(e) for e in errors))

    def test_accesso_missing_codcom(self):
        """Test AccessoGestioneCoordinate with missing required field codcom"""
        data = {
            "progr_civico": "123",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            AccessoGestioneCoordinate(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('codcom' in str(e) for e in errors))

    def test_accesso_missing_progr_civico(self):
        """Test AccessoGestioneCoordinate with missing required field progr_civico"""
        data = {
            "codcom": "B432",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            AccessoGestioneCoordinate(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('progr_civico' in str(e) for e in errors))

    def test_accesso_missing_coordinate(self):
        """Test AccessoGestioneCoordinate with missing required field coordinate"""
        data = {
            "codcom": "B432",
            "progr_civico": "123"
        }
        with self.assertRaises(ValidationError) as context:
            AccessoGestioneCoordinate(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('coordinate' in str(e) for e in errors))

    def test_accesso_with_minimal_coordinates(self):
        """Test AccessoGestioneCoordinate with minimal coordinate data (only x and y)"""
        data = {
            "codcom": "C123",
            "progr_civico": "999",
            "coordinate": {
                "x": "15.0",
                "y": "45.0"
            }
        }
        accesso = AccessoGestioneCoordinate(**data)
        
        self.assertEqual(accesso.coordinate.x, "15.0")
        self.assertEqual(accesso.coordinate.y, "45.0")
        self.assertIsNone(accesso.coordinate.z)
        self.assertIsNone(accesso.coordinate.metodo)

    def test_accesso_with_coordinate_object(self):
        """Test AccessoGestioneCoordinate creation using Coordinate object directly"""
        coordinate = Coordinate(
            x="13.1022000",
            y="41.8847600",
            z="150",
            metodo="3"
        )
        
        accesso = AccessoGestioneCoordinate(
            codcom="D456",
            progr_civico="555",
            coordinate=coordinate
        )
        
        self.assertEqual(accesso.codcom, "D456")
        self.assertEqual(accesso.progr_civico, "555")
        self.assertEqual(accesso.coordinate, coordinate)

    def test_accesso_json_serialization(self):
        """Test AccessoGestioneCoordinate JSON serialization"""
        data = {
            "codcom": "E789",
            "progr_civico": "321",
            "coordinate": {
                "x": "14.5",
                "y": "43.2",
                "z": "200",
                "metodo": "1"
            }
        }
        accesso = AccessoGestioneCoordinate(**data)
        
        # Test model_dump (Pydantic v2)
        json_data = accesso.model_dump()
        
        self.assertEqual(json_data["codcom"], "E789")
        self.assertEqual(json_data["progr_civico"], "321")
        self.assertEqual(json_data["coordinate"]["x"], "14.5")
        self.assertEqual(json_data["coordinate"]["y"], "43.2")
        self.assertEqual(json_data["coordinate"]["z"], "200")
        self.assertEqual(json_data["coordinate"]["metodo"], "1")

    def test_accesso_json_deserialization(self):
        """Test AccessoGestioneCoordinate JSON deserialization"""
        json_str = '{"codcom": "F012", "progr_civico": "111", "coordinate": {"x": "16.0", "y": "44.0"}}'
        accesso = AccessoGestioneCoordinate.model_validate_json(json_str)
        
        self.assertEqual(accesso.codcom, "F012")
        self.assertEqual(accesso.progr_civico, "111")
        self.assertEqual(accesso.coordinate.x, "16.0")
        self.assertEqual(accesso.coordinate.y, "44.0")


class TestAccessoAggiornamento(TestCase):
    """Test suite for Accesso model from aggiornamentoaccessi"""

    def test_accesso_valid_data_complete(self):
        """Test Accesso creation with all fields - using only numero without metrico"""
        data = {
            "progr_civico": "1370588",
            "codice_civico_comunale": "7569A",
            "numero": "12",
            "esponente": "A",
            "specificita": "ROSSO",
            "sezione_censimento": "9",
            "operazione_civico": "R",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600",
                "z": "150",
                "metodo": "3"
            },
            "data_valid_amm": "08/10/2024",
            "isolato": "101"
        }
        accesso = AccessoAggiornamento(**data)
        
        self.assertEqual(accesso.progr_civico, "1370588")
        self.assertEqual(accesso.codice_civico_comunale, "7569A")
        self.assertEqual(accesso.numero, "12")
        self.assertEqual(accesso.esponente, "A")
        self.assertEqual(accesso.specificita, "ROSSO")
        self.assertIsNone(accesso.metrico)
        self.assertEqual(accesso.sezione_censimento, "9")
        self.assertEqual(accesso.operazione_civico, TipoOperazione.R)
        self.assertEqual(accesso.coordinate.x, "13.1022000")
        self.assertEqual(accesso.data_valid_amm, "08/10/2024")
        self.assertEqual(accesso.isolato, "101")

    def test_accesso_minimal_data(self):
        """Test Accesso with minimal/no required fields (all optional)"""
        data = {}
        accesso = AccessoAggiornamento(**data)
        
        self.assertIsNone(accesso.progr_civico)
        self.assertIsNone(accesso.codice_civico_comunale)
        self.assertIsNone(accesso.numero)
        self.assertIsNone(accesso.coordinate)

    def test_accesso_operazione_inserimento(self):
        """Test Accesso with operazione_civico='I' (inserimento)"""
        data = {
            "numero": "15",
            "esponente": "B",
            "operazione_civico": TipoOperazione.I,
            "coordinate": {
                "x": "12.5",
                "y": "42.0"
            },
            "sezione_censimento": "5"
        }
        accesso = AccessoAggiornamento(**data)
        
        self.assertEqual(accesso.operazione_civico, TipoOperazione.I)
        self.assertEqual(accesso.numero, "15")
        self.assertEqual(accesso.esponente, "B")

    def test_accesso_operazione_soppressione(self):
        """Test Accesso with operazione_civico='S' (soppressione)"""
        data = {
            "progr_civico": "1370588",
            "operazione_civico": TipoOperazione.S,
            "data_valid_amm": "08/10/2024"
        }
        accesso = AccessoAggiornamento(**data)
        
        self.assertEqual(accesso.operazione_civico, TipoOperazione.S)
        self.assertEqual(accesso.progr_civico, "1370588")

    def test_accesso_with_metrico_no_numero(self):
        """Test Accesso identified by metrico without numero"""
        data = {
            "progr_civico": "999999",
            "metrico": "450",
            "operazione_civico": "R",
            "coordinate": {
                "x": "14.0",
                "y": "43.0"
            }
        }
        accesso = AccessoAggiornamento(**data)
        
        self.assertEqual(accesso.metrico, "450")
        self.assertIsNone(accesso.numero)

    def test_accesso_max_length_validation(self):
        """Test Accesso with fields at max length"""
        data = {
            "progr_civico": "123456789012345",  # max 15
            "codice_civico_comunale": "A" * 30,  # max 30
            "numero": "12345",  # max 5
            "esponente": "A" * 15,  # max 15
            "specificita": "ROSSO",  # max 5
            "sezione_censimento": "1234567890123",  # max 13
            "operazione_civico": "I",  # max 1
            "isolato": "9999"  # max 4
        }
        accesso = AccessoAggiornamento(**data)
        
        self.assertEqual(len(accesso.progr_civico), 15)
        self.assertEqual(len(accesso.codice_civico_comunale), 30)

    def test_accesso_coordinate_optional(self):
        """Test Accesso with None coordinate"""
        data = {
            "numero": "10",
            "operazione_civico": "I"
        }
        accesso = AccessoAggiornamento(**data)
        
        self.assertIsNone(accesso.coordinate)

    # Test validatori model_validator

    def test_accesso_validator_progr_civico_required_for_R(self):
        """Test progr_civico required when operazione_civico='R'"""
        data = {
            "numero": "12",
            "operazione_civico": "R"
        }
        with self.assertRaises(ValidationError) as context:
            AccessoAggiornamento(**data)
        
        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['type'], 'value_error')
        self.assertIn("progr_civico è obbligatorio quando operazione_civico è 'R' o 'S'", str(errors[0]['ctx']['error']))

    def test_accesso_validator_progr_civico_required_for_S(self):
        """Test progr_civico required when operazione_civico='S'"""
        data = {
            "operazione_civico": "S",
            "data_valid_amm": "08/10/2024"
        }
        with self.assertRaises(ValidationError) as context:
            AccessoAggiornamento(**data)
        
        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['type'], 'value_error')
        self.assertIn("progr_civico è obbligatorio quando operazione_civico è 'R' o 'S'", str(errors[0]['ctx']['error']))

    def test_accesso_validator_numero_not_allowed_for_S(self):
        """Test numero cannot be set when operazione_civico='S'"""
        data = {
            "progr_civico": "1370588",
            "numero": "12",
            "operazione_civico": "S"
        }
        with self.assertRaises(ValidationError) as context:
            AccessoAggiornamento(**data)
        
        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['type'], 'value_error')
        self.assertIn("numero non deve essere valorizzato quando operazione_civico è 'S'", str(errors[0]['ctx']['error']))

    def test_accesso_validator_numero_metrico_exclusive(self):
        """Test numero and metrico cannot both be set"""
        data = {
            "progr_civico": "1370588",
            "numero": "12",
            "metrico": "300",
            "operazione_civico": "R"
        }
        with self.assertRaises(ValidationError) as context:
            AccessoAggiornamento(**data)
        
        errors = context.exception.errors()
        # One of the two validators will fire first
        self.assertGreaterEqual(len(errors), 1)
        error_messages = ' '.join([str(e['ctx']['error']) for e in errors])
        # Check that at least one of the expected error messages is present
        self.assertTrue(
            "numero non deve essere valorizzato quando l'accesso è identificato con il sistema metrico" in error_messages or
            "metrico non deve essere valorizzato quando l'accesso è identificato con il numero civico" in error_messages
        )

    def test_accesso_validator_metrico_not_allowed_for_S(self):
        """Test metrico cannot be set when operazione_civico='S'"""
        data = {
            "progr_civico": "1370588",
            "metrico": "300",
            "operazione_civico": "S"
        }
        with self.assertRaises(ValidationError) as context:
            AccessoAggiornamento(**data)
        
        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['type'], 'value_error')
        self.assertIn("metrico non deve essere valorizzato quando operazione_civico è 'S'", str(errors[0]['ctx']['error']))

    def test_accesso_validator_sezione_censimento_only_for_I_R(self):
        """Test sezione_censimento can only be set for I or R operations"""
        data = {
            "progr_civico": "1370588",
            "sezione_censimento": "9",
            "operazione_civico": "S"
        }
        with self.assertRaises(ValidationError) as context:
            AccessoAggiornamento(**data)
        
        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['type'], 'value_error')
        self.assertIn("sezione_censimento può essere valorizzato solo quando operazione_civico è 'I' o 'R'", str(errors[0]['ctx']['error']))

    def test_accesso_validator_isolato_only_for_I_R(self):
        """Test isolato can only be set for I or R operations"""
        data = {
            "progr_civico": "1370588",
            "isolato": "101",
            "operazione_civico": "S"
        }
        with self.assertRaises(ValidationError) as context:
            AccessoAggiornamento(**data)
        
        errors = context.exception.errors()
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]['type'], 'value_error')
        self.assertIn("isolato può essere valorizzato solo quando operazione_civico è 'I' o 'R'", str(errors[0]['ctx']['error']))

    def test_accesso_validator_valid_I_operation(self):
        """Test valid Accesso for I (insert) operation"""
        data = {
            "numero": "15",
            "sezione_censimento": "5",
            "isolato": "102",
            "operazione_civico": "I",
            "coordinate": {
                "x": "13.0",
                "y": "42.0"
            }
        }
        accesso = AccessoAggiornamento(**data)
        self.assertEqual(accesso.operazione_civico, TipoOperazione.I)
        self.assertEqual(accesso.sezione_censimento, "5")
        self.assertEqual(accesso.isolato, "102")

    def test_accesso_validator_valid_S_operation(self):
        """Test valid Accesso for S (delete) operation - only progr_civico"""
        data = {
            "progr_civico": "1370588",
            "operazione_civico": "S",
            "data_valid_amm": "08/10/2024"
        }
        accesso = AccessoAggiornamento(**data)
        self.assertEqual(accesso.operazione_civico, TipoOperazione.S)
        self.assertIsNone(accesso.numero)
        self.assertIsNone(accesso.metrico)


class TestTipoOperazione(TestCase):
    """Test suite for TipoOperazione enum"""

    def test_tipo_operazione_values(self):
        """Test that TipoOperazione enum has the expected values"""
        self.assertEqual(TipoOperazione.I.value, 'I')
        self.assertEqual(TipoOperazione.R.value, 'R')
        self.assertEqual(TipoOperazione.S.value, 'S')

    def test_tipo_operazione_members(self):
        """Test that TipoOperazione enum has exactly three members"""
        self.assertEqual(len(TipoOperazione), 3)
        self.assertIn(TipoOperazione.I, TipoOperazione)
        self.assertIn(TipoOperazione.R, TipoOperazione)
        self.assertIn(TipoOperazione.S, TipoOperazione)


class TestProvvedimento(TestCase):
    """Test suite for Provvedimento model"""

    def test_provvedimento_valid_data(self):
        """Test Provvedimento creation with valid data"""
        data = {
            "data": "10/10/2023",
            "protocollo": "1234567/abc",
            "flag_delibera": 2
        }
        provvedimento = Provvedimento(**data)
        
        self.assertEqual(provvedimento.data, "10/10/2023")
        self.assertEqual(provvedimento.protocollo, "1234567/abc")
        self.assertEqual(provvedimento.flag_delibera, 2)

    def test_provvedimento_all_none(self):
        """Test Provvedimento with all fields as None"""
        provvedimento = Provvedimento()
        
        self.assertIsNone(provvedimento.data)
        self.assertIsNone(provvedimento.protocollo)
        self.assertIsNone(provvedimento.flag_delibera)

    def test_provvedimento_flag_delibera_0_requires_data_and_protocollo(self):
        """Test that flag_delibera=0 requires data and protocollo"""
        data = {
            "flag_delibera": 0
        }
        with self.assertRaises(ValidationError) as context:
            Provvedimento(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('data e protocollo sono obbligatori' in str(e) for e in errors))

    def test_provvedimento_flag_delibera_1_requires_data_and_protocollo(self):
        """Test that flag_delibera=1 requires data and protocollo"""
        data = {
            "flag_delibera": 1,
            "data": "10/10/2023"
        }
        with self.assertRaises(ValidationError) as context:
            Provvedimento(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('data e protocollo sono obbligatori' in str(e) for e in errors))

    def test_provvedimento_flag_delibera_0_with_data_and_protocollo(self):
        """Test that flag_delibera=0 is valid with data and protocollo"""
        data = {
            "data": "10/10/2023",
            "protocollo": "1234/abc",
            "flag_delibera": 0
        }
        provvedimento = Provvedimento(**data)
        self.assertEqual(provvedimento.flag_delibera, 0)

    def test_provvedimento_flag_delibera_1_with_data_and_protocollo(self):
        """Test that flag_delibera=1 is valid with data and protocollo"""
        data = {
            "data": "10/10/2023",
            "protocollo": "1234/abc",
            "flag_delibera": 1
        }
        provvedimento = Provvedimento(**data)
        self.assertEqual(provvedimento.flag_delibera, 1)

    def test_provvedimento_flag_delibera_out_of_range(self):
        """Test that flag_delibera must be between 0 and 4"""
        data = {
            "data": "10/10/2023",
            "protocollo": "1234/abc",
            "flag_delibera": 5
        }
        with self.assertRaises(ValidationError) as context:
            Provvedimento(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('flag_delibera' in str(e) for e in errors))

    def test_provvedimento_flag_delibera_negative(self):
        """Test that flag_delibera cannot be negative"""
        data = {
            "data": "10/10/2023",
            "protocollo": "1234/abc",
            "flag_delibera": -1
        }
        with self.assertRaises(ValidationError) as context:
            Provvedimento(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('flag_delibera' in str(e) for e in errors))

    def test_provvedimento_protocollo_max_length(self):
        """Test Provvedimento protocollo max length constraint"""
        data = {
            "protocollo": "a" * 71,  # Exceeds max_length=70
            "flag_delibera": 2
        }
        with self.assertRaises(ValidationError) as context:
            Provvedimento(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('protocollo' in str(e) for e in errors))

    def test_provvedimento_protocollo_max_length_valid(self):
        """Test Provvedimento protocollo at max length"""
        data = {
            "protocollo": "a" * 70,
            "flag_delibera": 2
        }
        provvedimento = Provvedimento(**data)
        self.assertEqual(len(provvedimento.protocollo), 70)


class TestAutPrefettura(TestCase):
    """Test suite for AutPrefettura model"""

    def test_aut_prefettura_valid_data(self):
        """Test AutPrefettura creation with valid data"""
        data = {
            "data_pref": "10/10/2023",
            "protocollo_pref": "Prot.Gen.1234567"
        }
        aut_pref = AutPrefettura(**data)
        
        self.assertEqual(aut_pref.data_pref, "10/10/2023")
        self.assertEqual(aut_pref.protocollo_pref, "Prot.Gen.1234567")

    def test_aut_prefettura_all_none(self):
        """Test AutPrefettura with all fields as None"""
        aut_pref = AutPrefettura()
        
        self.assertIsNone(aut_pref.data_pref)
        self.assertIsNone(aut_pref.protocollo_pref)

    def test_aut_prefettura_protocollo_max_length(self):
        """Test AutPrefettura protocollo_pref max length constraint"""
        data = {
            "data_pref": "10/10/2023",
            "protocollo_pref": "a" * 71  # Exceeds max_length=70
        }
        with self.assertRaises(ValidationError) as context:
            AutPrefettura(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('protocollo_pref' in str(e) for e in errors))

    def test_aut_prefettura_protocollo_max_length_valid(self):
        """Test AutPrefettura protocollo_pref at max length"""
        data = {
            "data_pref": "10/10/2023",
            "protocollo_pref": "a" * 70
        }
        aut_pref = AutPrefettura(**data)
        self.assertEqual(len(aut_pref.protocollo_pref), 70)

