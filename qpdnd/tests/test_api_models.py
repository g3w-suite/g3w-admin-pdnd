# coding=utf-8
""""
Test for gestionecoordinate API models
.. note:: This program is free software; you can redistribute it and/or modify
    it under the terms of the Mozilla Public License 2.0.

"""

__author__ = 'lorenzetti@gis3w.it'
__date__ = '2025-12-23'
__copyright__ = 'Copyright Gis3w'


import unittest
from pydantic import ValidationError
from qpdnd.api.models.gestionecoordinate import Accesso
from qpdnd.api.models.coordinate import Coordinate
from qpdnd.api.models.aggiornamentoaccessi import (
    Accesso as AccessoAggiornamento,
    Richiesta,
    RichiestaOperazione
)


class TestAccesso(unittest.TestCase):
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


class TestAccessoAggiornamento(unittest.TestCase):
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


class TestRichiesta(unittest.TestCase):
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


class TestRichiestaOperazione(unittest.TestCase):
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


if __name__ == '__main__':
    unittest.main()
