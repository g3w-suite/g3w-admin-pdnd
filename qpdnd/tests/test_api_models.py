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
from qpdnd.api.models.gestionecoordinate import Accesso
from qpdnd.api.models.coordinate import Coordinate
from qpdnd.api.models.aggiornamentoaccessi import (
    Accesso as AccessoAggiornamento,
    Richiesta,
    RichiestaOperazione
)
from qpdnd.api.models.aggiornamentointerni import (
    RichiestaOperazione as RichiestaOperazioneInterni
)
from qpdnd.api.models.aggiornamentoodonimi import (
    TipoOperazione,
    Provvedimento,
    AutPrefettura,
    Richiesta as RichiestaOdonimi,
    RichiestaOperazione as RichiestaOperazioneOdonimi
)


class TestAccesso(TestCase):
    """Test suite for Accesso model from gestionecoordinate"""

    def test_accesso_valid_data(self):
        """Test Accesso creation with valid data"""
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
        accesso = Accesso(**data)
        
        self.assertEqual(accesso.codcom, "B432")
        self.assertEqual(accesso.progr_civico, "123")
        self.assertEqual(accesso.coordinate.x, "13.1022000")
        self.assertEqual(accesso.coordinate.y, "41.8847600")
        self.assertEqual(accesso.coordinate.z, "150")
        self.assertEqual(accesso.coordinate.metodo, "3")

    def test_accesso_valid_codcom_lowercase(self):
        """Test Accesso with lowercase codcom"""
        data = {
            "codcom": "a123",
            "progr_civico": "456",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        accesso = Accesso(**data)
        self.assertEqual(accesso.codcom, "a123")

    def test_accesso_valid_progr_civico_numeric_string(self):
        """Test Accesso with numeric progr_civico as string"""
        data = {
            "codcom": "Z999",
            "progr_civico": "789",
            "coordinate": {
                "x": "12.5",
                "y": "42.0"
            }
        }
        accesso = Accesso(**data)
        self.assertEqual(accesso.progr_civico, "789")

    def test_accesso_invalid_codcom_format(self):
        """Test Accesso with invalid codcom format (too many digits)"""
        data = {
            "codcom": "A1234",  # 4 digits instead of 3
            "progr_civico": "123",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            Accesso(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('codcom' in str(e) for e in errors))

    def test_accesso_invalid_codcom_no_alpha_prefix(self):
        """Test Accesso with invalid codcom (no alphabetic character at start)"""
        data = {
            "codcom": "1234",  # No alpha character
            "progr_civico": "123",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            Accesso(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('codcom' in str(e) for e in errors))

    def test_accesso_invalid_codcom_too_short(self):
        """Test Accesso with invalid codcom (too short)"""
        data = {
            "codcom": "A12",  # Only 2 digits
            "progr_civico": "123",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            Accesso(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('codcom' in str(e) for e in errors))

    def test_accesso_invalid_progr_civico_non_numeric(self):
        """Test Accesso with invalid progr_civico (non-numeric string)"""
        data = {
            "codcom": "B432",
            "progr_civico": "abc",  # Non-numeric
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            Accesso(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('prog_civico' in str(e) for e in errors))

    def test_accesso_invalid_progr_civico_alphanumeric(self):
        """Test Accesso with invalid progr_civico (alphanumeric)"""
        data = {
            "codcom": "B432",
            "progr_civico": "123abc",  # Alphanumeric
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            Accesso(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('prog_civico' in str(e) for e in errors))

    def test_accesso_missing_codcom(self):
        """Test Accesso with missing required field codcom"""
        data = {
            "progr_civico": "123",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            Accesso(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('codcom' in str(e) for e in errors))

    def test_accesso_missing_progr_civico(self):
        """Test Accesso with missing required field progr_civico"""
        data = {
            "codcom": "B432",
            "coordinate": {
                "x": "13.1022000",
                "y": "41.8847600"
            }
        }
        with self.assertRaises(ValidationError) as context:
            Accesso(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('progr_civico' in str(e) for e in errors))

    def test_accesso_missing_coordinate(self):
        """Test Accesso with missing required field coordinate"""
        data = {
            "codcom": "B432",
            "progr_civico": "123"
        }
        with self.assertRaises(ValidationError) as context:
            Accesso(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('coordinate' in str(e) for e in errors))

    def test_accesso_with_minimal_coordinates(self):
        """Test Accesso with minimal coordinate data (only x and y)"""
        data = {
            "codcom": "C123",
            "progr_civico": "999",
            "coordinate": {
                "x": "15.0",
                "y": "45.0"
            }
        }
        accesso = Accesso(**data)
        
        self.assertEqual(accesso.coordinate.x, "15.0")
        self.assertEqual(accesso.coordinate.y, "45.0")
        self.assertIsNone(accesso.coordinate.z)
        self.assertIsNone(accesso.coordinate.metodo)

    def test_accesso_with_coordinate_object(self):
        """Test Accesso creation using Coordinate object directly"""
        coordinate = Coordinate(
            x="13.1022000",
            y="41.8847600",
            z="150",
            metodo="3"
        )
        
        accesso = Accesso(
            codcom="D456",
            progr_civico="555",
            coordinate=coordinate
        )
        
        self.assertEqual(accesso.codcom, "D456")
        self.assertEqual(accesso.progr_civico, "555")
        self.assertEqual(accesso.coordinate, coordinate)

    def test_accesso_json_serialization(self):
        """Test Accesso JSON serialization"""
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
        accesso = Accesso(**data)
        
        # Test model_dump (Pydantic v2)
        json_data = accesso.model_dump()
        
        self.assertEqual(json_data["codcom"], "E789")
        self.assertEqual(json_data["progr_civico"], "321")
        self.assertEqual(json_data["coordinate"]["x"], "14.5")
        self.assertEqual(json_data["coordinate"]["y"], "43.2")
        self.assertEqual(json_data["coordinate"]["z"], "200")
        self.assertEqual(json_data["coordinate"]["metodo"], "1")

    def test_accesso_json_deserialization(self):
        """Test Accesso JSON deserialization"""
        json_str = '{"codcom": "F012", "progr_civico": "111", "coordinate": {"x": "16.0", "y": "44.0"}}'
        accesso = Accesso.model_validate_json(json_str)
        
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
        self.assertEqual(accesso.operazione_civico, "R")
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
            "operazione_civico": "I",
            "coordinate": {
                "x": "12.5",
                "y": "42.0"
            },
            "sezione_censimento": "5"
        }
        accesso = AccessoAggiornamento(**data)
        
        self.assertEqual(accesso.operazione_civico, "I")
        self.assertEqual(accesso.numero, "15")
        self.assertEqual(accesso.esponente, "B")

    def test_accesso_operazione_soppressione(self):
        """Test Accesso with operazione_civico='S' (soppressione)"""
        data = {
            "progr_civico": "1370588",
            "operazione_civico": "S",
            "data_valid_amm": "08/10/2024"
        }
        accesso = AccessoAggiornamento(**data)
        
        self.assertEqual(accesso.operazione_civico, "S")
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
        self.assertEqual(accesso.operazione_civico, "I")
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
        self.assertEqual(accesso.operazione_civico, "S")
        self.assertIsNone(accesso.numero)
        self.assertIsNone(accesso.metrico)


class TestRichiesta(TestCase):
    """Test suite for Richiesta model"""

    def test_richiesta_valid_complete(self):
        """Test Richiesta with all fields"""
        data = {
            "codcom": "A062",
            "progr_nazionale": "2000449",
            "accesso": {
                "progr_civico": "1370588",
                "numero": "12",
                "operazione_civico": "R",
                "coordinate": {
                    "x": "13.1022000",
                    "y": "41.8847600"
                }
            }
        }
        richiesta = Richiesta(**data)
        
        self.assertEqual(richiesta.codcom, "A062")
        self.assertEqual(richiesta.progr_nazionale, "2000449")
        self.assertIsNotNone(richiesta.accesso)
        self.assertEqual(richiesta.accesso.progr_civico, "1370588")

    def test_richiesta_minimal(self):
        """Test Richiesta with minimal data (all fields optional)"""
        data = {}
        richiesta = Richiesta(**data)
        
        self.assertIsNone(richiesta.codcom)
        self.assertIsNone(richiesta.progr_nazionale)
        self.assertIsNone(richiesta.accesso)

    def test_richiesta_with_accesso_object(self):
        """Test Richiesta with Accesso object"""
        accesso = AccessoAggiornamento(
            numero="25",
            operazione_civico="I"
        )
        
        richiesta = Richiesta(
            codcom="B123",
            progr_nazionale="3000555",
            accesso=accesso
        )
        
        self.assertEqual(richiesta.codcom, "B123")
        self.assertEqual(richiesta.accesso.numero, "25")

    def test_richiesta_without_accesso(self):
        """Test Richiesta without accesso"""
        data = {
            "codcom": "C456",
            "progr_nazionale": "4000123"
        }
        richiesta = Richiesta(**data)
        
        self.assertEqual(richiesta.codcom, "C456")
        self.assertEqual(richiesta.progr_nazionale, "4000123")
        self.assertIsNone(richiesta.accesso)

    def test_richiesta_progr_nazionale_max_length(self):
        """Test Richiesta with progr_nazionale at max length"""
        data = {
            "codcom": "D789",
            "progr_nazionale": "1234567890"  # max 10
        }
        richiesta = Richiesta(**data)
        
        self.assertEqual(len(richiesta.progr_nazionale), 10)

    def test_richiesta_json_serialization(self):
        """Test Richiesta JSON serialization"""
        data = {
            "codcom": "E012",
            "progr_nazionale": "5000789",
            "accesso": {
                "numero": "30",
                "operazione_civico": "I"
            }
        }
        richiesta = Richiesta(**data)
        json_data = richiesta.model_dump()
        
        self.assertEqual(json_data["codcom"], "E012")
        self.assertEqual(json_data["progr_nazionale"], "5000789")
        self.assertEqual(json_data["accesso"]["numero"], "30")


class TestRichiestaOperazione(TestCase):
    """Test suite for RichiestaOperazione model"""

    def test_richiesta_operazione_complete(self):
        """Test RichiestaOperazione with complete data"""
        data = {
            "richiesta": {
                "codcom": "A062",
                "progr_nazionale": "2000449",
                "accesso": {
                    "progr_civico": "1370588",
                    "numero": "12",
                    "operazione_civico": "R",
                    "coordinate": {
                        "x": "13.1022000",
                        "y": "41.8847600",
                        "z": "150",
                        "metodo": "3"
                    },
                    "data_valid_amm": "08/10/2024"
                }
            }
        }
        richiesta_op = RichiestaOperazione(**data)
        
        self.assertIsNotNone(richiesta_op.richiesta)
        self.assertEqual(richiesta_op.richiesta.codcom, "A062")
        self.assertEqual(richiesta_op.richiesta.progr_nazionale, "2000449")
        self.assertEqual(richiesta_op.richiesta.accesso.numero, "12")

    def test_richiesta_operazione_minimal(self):
        """Test RichiestaOperazione with no data"""
        data = {}
        richiesta_op = RichiestaOperazione(**data)
        
        self.assertIsNone(richiesta_op.richiesta)

    def test_richiesta_operazione_with_richiesta_object(self):
        """Test RichiestaOperazione with Richiesta object"""
        accesso = AccessoAggiornamento(
            numero="40",
            operazione_civico="I"
        )
        
        richiesta = Richiesta(
            codcom="F345",
            progr_nazionale="6000111",
            accesso=accesso
        )
        
        richiesta_op = RichiestaOperazione(richiesta=richiesta)
        
        self.assertIsNotNone(richiesta_op.richiesta)
        self.assertEqual(richiesta_op.richiesta.codcom, "F345")
        self.assertEqual(richiesta_op.richiesta.accesso.numero, "40")

    def test_richiesta_operazione_nested_creation(self):
        """Test RichiestaOperazione with nested dict creation"""
        data = {
            "richiesta": {
                "codcom": "G678",
                "progr_nazionale": "7000222"
            }
        }
        richiesta_op = RichiestaOperazione(**data)
        
        self.assertEqual(richiesta_op.richiesta.codcom, "G678")
        self.assertEqual(richiesta_op.richiesta.progr_nazionale, "7000222")

    def test_richiesta_operazione_json_serialization(self):
        """Test RichiestaOperazione JSON serialization"""
        data = {
            "richiesta": {
                "codcom": "H901",
                "progr_nazionale": "8000333",
                "accesso": {
                    "progr_civico": "1370588",
                    "operazione_civico": "S",
                    "data_valid_amm": "15/11/2024"
                }
            }
        }
        richiesta_op = RichiestaOperazione(**data)
        json_data = richiesta_op.model_dump()
        
        self.assertEqual(json_data["richiesta"]["codcom"], "H901")
        self.assertEqual(json_data["richiesta"]["accesso"]["progr_civico"], "1370588")
        self.assertEqual(json_data["richiesta"]["accesso"]["operazione_civico"], "S")

    def test_richiesta_operazione_json_deserialization(self):
        """Test RichiestaOperazione JSON deserialization"""
        json_str = '{"richiesta": {"codcom": "I234", "progr_nazionale": "9000444"}}'
        richiesta_op = RichiestaOperazione.model_validate_json(json_str)
        
        self.assertEqual(richiesta_op.richiesta.codcom, "I234")
        self.assertEqual(richiesta_op.richiesta.progr_nazionale, "9000444")


class TestRichiestaOperazioneInterni(TestCase):
    """Test suite for RichiestaOperazione model from aggiornamentointerni"""

    def test_richiesta_operazione_interni_valid_complete(self):
        """Test RichiestaOperazioneInterni with all fields"""
        data = {
            "codcom": "A062",
            "progr_civico": "1370588",
            "progr_interno": "12345",
            "interno": "A1",
            "tipo_operazione": "I",
            "codice_interno_comunale": "INT001",
            "cortile": "C1",
            "edificio": "ED1",
            "scala": "S1",
            "piano": "2",
            "esponente_interno": "B"
        }
        richiesta_op = RichiestaOperazioneInterni(**data)
        
        self.assertEqual(richiesta_op.codcom, "A062")
        self.assertEqual(richiesta_op.progr_civico, "1370588")
        self.assertEqual(richiesta_op.progr_interno, "12345")
        self.assertEqual(richiesta_op.interno, "A1")
        self.assertEqual(richiesta_op.tipo_operazione, "I")
        self.assertEqual(richiesta_op.codice_interno_comunale, "INT001")
        self.assertEqual(richiesta_op.cortile, "C1")
        self.assertEqual(richiesta_op.edificio, "ED1")
        self.assertEqual(richiesta_op.scala, "S1")
        self.assertEqual(richiesta_op.piano, "2")
        self.assertEqual(richiesta_op.esponente_interno, "B")

    def test_richiesta_operazione_interni_minimal(self):
        """Test RichiestaOperazioneInterni with no data (all fields optional)"""
        data = {}
        richiesta_op = RichiestaOperazioneInterni(**data)
        
        self.assertIsNone(richiesta_op.codcom)
        self.assertIsNone(richiesta_op.progr_civico)
        self.assertIsNone(richiesta_op.progr_interno)
        self.assertIsNone(richiesta_op.interno)
        self.assertIsNone(richiesta_op.tipo_operazione)
        self.assertIsNone(richiesta_op.codice_interno_comunale)
        self.assertIsNone(richiesta_op.cortile)
        self.assertIsNone(richiesta_op.edificio)
        self.assertIsNone(richiesta_op.scala)
        self.assertIsNone(richiesta_op.piano)
        self.assertIsNone(richiesta_op.esponente_interno)

    def test_richiesta_operazione_interni_partial(self):
        """Test RichiestaOperazioneInterni with partial data"""
        data = {
            "codcom": "B123",
            "progr_civico": "2000111",
            "interno": "5",
            "tipo_operazione": "U"
        }
        richiesta_op = RichiestaOperazioneInterni(**data)
        
        self.assertEqual(richiesta_op.codcom, "B123")
        self.assertEqual(richiesta_op.progr_civico, "2000111")
        self.assertEqual(richiesta_op.interno, "5")
        self.assertEqual(richiesta_op.tipo_operazione, "U")
        self.assertIsNone(richiesta_op.progr_interno)
        self.assertIsNone(richiesta_op.cortile)

    def test_richiesta_operazione_interni_insert_operation(self):
        """Test RichiestaOperazioneInterni for insert operation"""
        data = {
            "codcom": "C456",
            "progr_civico": "3000222",
            "interno": "10A",
            "tipo_operazione": "I",
            "edificio": "B",
            "scala": "1",
            "piano": "3"
        }
        richiesta_op = RichiestaOperazioneInterni(**data)
        
        self.assertEqual(richiesta_op.tipo_operazione, "I")
        self.assertEqual(richiesta_op.interno, "10A")
        self.assertEqual(richiesta_op.edificio, "B")
        self.assertEqual(richiesta_op.scala, "1")
        self.assertEqual(richiesta_op.piano, "3")

    def test_richiesta_operazione_interni_delete_operation(self):
        """Test RichiestaOperazioneInterni for delete operation"""
        data = {
            "codcom": "D789",
            "progr_civico": "4000333",
            "progr_interno": "99999",
            "tipo_operazione": "D"
        }
        richiesta_op = RichiestaOperazioneInterni(**data)
        
        self.assertEqual(richiesta_op.tipo_operazione, "D")
        self.assertEqual(richiesta_op.progr_interno, "99999")

    def test_richiesta_operazione_interni_json_serialization(self):
        """Test RichiestaOperazioneInterni JSON serialization"""
        data = {
            "codcom": "E012",
            "progr_civico": "5000444",
            "interno": "15",
            "tipo_operazione": "I",
            "piano": "1",
            "scala": "A"
        }
        richiesta_op = RichiestaOperazioneInterni(**data)
        json_data = richiesta_op.model_dump()
        
        self.assertEqual(json_data["codcom"], "E012")
        self.assertEqual(json_data["progr_civico"], "5000444")
        self.assertEqual(json_data["interno"], "15")
        self.assertEqual(json_data["tipo_operazione"], "I")
        self.assertEqual(json_data["piano"], "1")
        self.assertEqual(json_data["scala"], "A")

    def test_richiesta_operazione_interni_json_deserialization(self):
        """Test RichiestaOperazioneInterni JSON deserialization"""
        json_str = '{"codcom": "F345", "progr_civico": "6000555", "interno": "20", "tipo_operazione": "U"}'
        richiesta_op = RichiestaOperazioneInterni.model_validate_json(json_str)
        
        self.assertEqual(richiesta_op.codcom, "F345")
        self.assertEqual(richiesta_op.progr_civico, "6000555")
        self.assertEqual(richiesta_op.interno, "20")
        self.assertEqual(richiesta_op.tipo_operazione, "U")

    def test_richiesta_operazione_interni_with_esponente(self):
        """Test RichiestaOperazioneInterni with esponente_interno"""
        data = {
            "codcom": "G678",
            "progr_civico": "7000666",
            "interno": "25",
            "esponente_interno": "bis",
            "tipo_operazione": "I"
        }
        richiesta_op = RichiestaOperazioneInterni(**data)
        
        self.assertEqual(richiesta_op.interno, "25")
        self.assertEqual(richiesta_op.esponente_interno, "bis")

    def test_richiesta_operazione_interni_full_address(self):
        """Test RichiestaOperazioneInterni with full address details"""
        data = {
            "codcom": "H901",
            "progr_civico": "8000777",
            "interno": "30",
            "cortile": "Principale",
            "edificio": "A",
            "scala": "2",
            "piano": "4",
            "tipo_operazione": "I"
        }
        richiesta_op = RichiestaOperazioneInterni(**data)
        
        self.assertEqual(richiesta_op.cortile, "Principale")
        self.assertEqual(richiesta_op.edificio, "A")
        self.assertEqual(richiesta_op.scala, "2")
        self.assertEqual(richiesta_op.piano, "4")


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


class TestRichiestaOdonimi(TestCase):
    """Test suite for Richiesta model from aggiornamentoodonimi"""

    def test_richiesta_odonimi_minimal_data(self):
        """Test Richiesta creation with minimal required data"""
        data = {
            "codcom": "A062"
        }
        richiesta = RichiestaOdonimi(**data)
        
        self.assertEqual(richiesta.codcom, "A062")
        self.assertIsNone(richiesta.tipo_operazione)

    def test_richiesta_odonimi_insert_operation(self):
        """Test Richiesta with insert operation requires dug"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.I,
            "dug": "VIA",
            "denom_delibera": "DELLE ORCHIDEE"
        }
        richiesta = RichiestaOdonimi(**data)
        
        self.assertEqual(richiesta.tipo_operazione, TipoOperazione.I)
        self.assertEqual(richiesta.dug, "VIA")
        self.assertEqual(richiesta.denom_delibera, "DELLE ORCHIDEE")

    def test_richiesta_odonimi_insert_without_dug_fails(self):
        """Test that insert operation requires dug"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.I
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('dug è obbligatorio' in str(e) for e in errors))

    def test_richiesta_odonimi_update_operation(self):
        """Test Richiesta with update operation requires progr_nazionale and dug"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.R,
            "progr_nazionale": "2000449",
            "dug": "PIAZZA"
        }
        richiesta = RichiestaOdonimi(**data)
        
        self.assertEqual(richiesta.tipo_operazione, TipoOperazione.R)
        self.assertEqual(richiesta.progr_nazionale, "2000449")
        self.assertEqual(richiesta.dug, "PIAZZA")

    def test_richiesta_odonimi_update_without_progr_nazionale_fails(self):
        """Test that update operation requires progr_nazionale"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.R,
            "dug": "VIA"
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('progr_nazionale è obbligatorio' in str(e) for e in errors))

    def test_richiesta_odonimi_update_without_dug_fails(self):
        """Test that update operation requires dug"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.R,
            "progr_nazionale": "2000449"
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('dug è obbligatorio' in str(e) for e in errors))

    def test_richiesta_odonimi_suppression_operation(self):
        """Test Richiesta with suppression operation requires progr_nazionale"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.S,
            "progr_nazionale": "2000449"
        }
        richiesta = RichiestaOdonimi(**data)
        
        self.assertEqual(richiesta.tipo_operazione, TipoOperazione.S)
        self.assertEqual(richiesta.progr_nazionale, "2000449")
        self.assertIsNone(richiesta.dug)

    def test_richiesta_odonimi_suppression_without_progr_nazionale_fails(self):
        """Test that suppression operation requires progr_nazionale"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.S
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('progr_nazionale è obbligatorio' in str(e) for e in errors))

    def test_richiesta_odonimi_suppression_with_dug_fails(self):
        """Test that suppression operation does not allow dug"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.S,
            "progr_nazionale": "2000449",
            "dug": "VIA"
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('dug non è ammesso' in str(e) for e in errors))

    def test_richiesta_odonimi_missing_codcom_fails(self):
        """Test that codcom is required"""
        data = {
            "tipo_operazione": TipoOperazione.I,
            "dug": "VIA"
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('codcom' in str(e) for e in errors))

    def test_richiesta_odonimi_with_provvedimento(self):
        """Test Richiesta with nested Provvedimento"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.I,
            "dug": "VIA",
            "provvedimento": {
                "data": "10/10/2023",
                "protocollo": "1234/abc",
                "flag_delibera": 2
            }
        }
        richiesta = RichiestaOdonimi(**data)
        
        self.assertIsNotNone(richiesta.provvedimento)
        self.assertEqual(richiesta.provvedimento.data, "10/10/2023")
        self.assertEqual(richiesta.provvedimento.protocollo, "1234/abc")
        self.assertEqual(richiesta.provvedimento.flag_delibera, 2)

    def test_richiesta_odonimi_with_aut_prefettura(self):
        """Test Richiesta with nested AutPrefettura"""
        data = {
            "codcom": "A062",
            "aut_prefettura": {
                "data_pref": "10/10/2023",
                "protocollo_pref": "Prot.Gen.123"
            }
        }
        richiesta = RichiestaOdonimi(**data)
        
        self.assertIsNotNone(richiesta.aut_prefettura)
        self.assertEqual(richiesta.aut_prefettura.data_pref, "10/10/2023")
        self.assertEqual(richiesta.aut_prefettura.protocollo_pref, "Prot.Gen.123")

    def test_richiesta_odonimi_full_data(self):
        """Test Richiesta with all fields populated"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.I,
            "codice_comunale": "75439 d",
            "dug": "VIA",
            "denom_delibera": "DELLE ORCHIDEE",
            "denom_in_lingua_1": "ODONIMO LINGUA 1",
            "denom_in_lingua_2": "ODONIMO LINGUA 2",
            "denom_localita": "CASAL PALOCCO",
            "provvedimento": {
                "data": "10/10/2023",
                "protocollo": "1234/abc",
                "flag_delibera": 2
            },
            "aut_prefettura": {
                "data_pref": "15/10/2023",
                "protocollo_pref": "Prot.Gen.567"
            },
            "data_valid_amm": "08/10/2024"
        }
        richiesta = RichiestaOdonimi(**data)
        
        self.assertEqual(richiesta.codcom, "A062")
        self.assertEqual(richiesta.tipo_operazione, TipoOperazione.I)
        self.assertEqual(richiesta.codice_comunale, "75439 d")
        self.assertEqual(richiesta.dug, "VIA")
        self.assertEqual(richiesta.denom_delibera, "DELLE ORCHIDEE")
        self.assertEqual(richiesta.denom_in_lingua_1, "ODONIMO LINGUA 1")
        self.assertEqual(richiesta.denom_in_lingua_2, "ODONIMO LINGUA 2")
        self.assertEqual(richiesta.denom_localita, "CASAL PALOCCO")
        self.assertEqual(richiesta.data_valid_amm, "08/10/2024")
        self.assertIsNotNone(richiesta.provvedimento)
        self.assertIsNotNone(richiesta.aut_prefettura)

    def test_richiesta_odonimi_progr_nazionale_max_length(self):
        """Test Richiesta progr_nazionale max length constraint"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.R,
            "progr_nazionale": "a" * 11,  # Exceeds max_length=10
            "dug": "VIA"
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('progr_nazionale' in str(e) for e in errors))

    def test_richiesta_odonimi_codice_comunale_max_length(self):
        """Test Richiesta codice_comunale max length constraint"""
        data = {
            "codcom": "A062",
            "codice_comunale": "a" * 31  # Exceeds max_length=30
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('codice_comunale' in str(e) for e in errors))

    def test_richiesta_odonimi_dug_max_length(self):
        """Test Richiesta dug max length constraint"""
        data = {
            "codcom": "A062",
            "tipo_operazione": TipoOperazione.I,
            "dug": "a" * 31  # Exceeds max_length=30
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('dug' in str(e) for e in errors))

    def test_richiesta_odonimi_denom_delibera_max_length(self):
        """Test Richiesta denom_delibera max length constraint"""
        data = {
            "codcom": "A062",
            "denom_delibera": "a" * 121  # Exceeds max_length=120
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('denom_delibera' in str(e) for e in errors))

    def test_richiesta_odonimi_denom_in_lingua_1_max_length(self):
        """Test Richiesta denom_in_lingua_1 max length constraint"""
        data = {
            "codcom": "A062",
            "denom_in_lingua_1": "a" * 151  # Exceeds max_length=150
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('denom_in_lingua_1' in str(e) for e in errors))

    def test_richiesta_odonimi_denom_in_lingua_2_max_length(self):
        """Test Richiesta denom_in_lingua_2 max length constraint"""
        data = {
            "codcom": "A062",
            "denom_in_lingua_2": "a" * 151  # Exceeds max_length=150
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('denom_in_lingua_2' in str(e) for e in errors))

    def test_richiesta_odonimi_denom_localita_max_length(self):
        """Test Richiesta denom_localita max length constraint"""
        data = {
            "codcom": "A062",
            "denom_localita": "a" * 152  # Exceeds max_length=151
        }
        with self.assertRaises(ValidationError) as context:
            RichiestaOdonimi(**data)
        
        errors = context.exception.errors()
        self.assertTrue(any('denom_localita' in str(e) for e in errors))


class TestRichiestaOperazioneOdonimi(TestCase):
    """Test suite for RichiestaOperazione model from aggiornamentoodonimi"""

    def test_richiesta_operazione_odonimi_valid_data(self):
        """Test RichiestaOperazione creation with valid data"""
        data = {
            "richiesta": {
                "codcom": "A062",
                "tipo_operazione": TipoOperazione.I,
                "dug": "VIA",
                "denom_delibera": "DELLE ORCHIDEE"
            }
        }
        richiesta_op = RichiestaOperazioneOdonimi(**data)
        
        self.assertIsNotNone(richiesta_op.richiesta)
        self.assertEqual(richiesta_op.richiesta.codcom, "A062")
        self.assertEqual(richiesta_op.richiesta.tipo_operazione, TipoOperazione.I)

    def test_richiesta_operazione_odonimi_none_richiesta(self):
        """Test RichiestaOperazione with None richiesta"""
        richiesta_op = RichiestaOperazioneOdonimi()
        
        self.assertIsNone(richiesta_op.richiesta)

    def test_richiesta_operazione_odonimi_with_full_richiesta(self):
        """Test RichiestaOperazione with fully populated nested Richiesta"""
        data = {
            "richiesta": {
                "codcom": "A062",
                "tipo_operazione": TipoOperazione.R,
                "progr_nazionale": "2000449",
                "codice_comunale": "75439 d",
                "dug": "PIAZZA",
                "denom_delibera": "GARIBALDI",
                "provvedimento": {
                    "data": "10/10/2023",
                    "protocollo": "1234/abc",
                    "flag_delibera": 1
                },
                "data_valid_amm": "08/10/2024"
            }
        }
        richiesta_op = RichiestaOperazioneOdonimi(**data)
        
        self.assertIsNotNone(richiesta_op.richiesta)
        self.assertEqual(richiesta_op.richiesta.tipo_operazione, TipoOperazione.R)
        self.assertEqual(richiesta_op.richiesta.progr_nazionale, "2000449")
        self.assertEqual(richiesta_op.richiesta.dug, "PIAZZA")
        self.assertIsNotNone(richiesta_op.richiesta.provvedimento)

