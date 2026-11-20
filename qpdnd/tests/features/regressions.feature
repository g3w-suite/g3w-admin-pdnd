@backend
Feature: PDND plugin regression coverage

  Scenario Outline: Preserve <case> assertions
    Given the "<module>" Django case "<test_class>.<test_method>"
    When the regression case is run
    Then all original assertions pass

    Examples:
      | case | module | test_class | test_method |
      | Accesso accepts complete coordinate data | api_models | TestAccessoGestioneCoordinate | test_accesso_valid_data |
      | Accesso accepts lowercase municipality codes | api_models | TestAccessoGestioneCoordinate | test_accesso_valid_codcom_lowercase |
      | Accesso accepts numeric civic identifiers | api_models | TestAccessoGestioneCoordinate | test_accesso_valid_progr_civico_numeric_string |
      | Accesso rejects malformed municipality codes | api_models | TestAccessoGestioneCoordinate | test_accesso_invalid_codcom_format |
      | Accesso rejects municipality codes without a letter prefix | api_models | TestAccessoGestioneCoordinate | test_accesso_invalid_codcom_no_alpha_prefix |
      | Accesso rejects short municipality codes | api_models | TestAccessoGestioneCoordinate | test_accesso_invalid_codcom_too_short |
      | Accesso rejects nonnumeric civic identifiers | api_models | TestAccessoGestioneCoordinate | test_accesso_invalid_progr_civico_non_numeric |
      | Accesso rejects alphanumeric civic identifiers | api_models | TestAccessoGestioneCoordinate | test_accesso_invalid_progr_civico_alphanumeric |
      | Accesso requires a municipality code | api_models | TestAccessoGestioneCoordinate | test_accesso_missing_codcom |
      | Accesso requires a civic identifier | api_models | TestAccessoGestioneCoordinate | test_accesso_missing_progr_civico |
      | Accesso requires coordinates | api_models | TestAccessoGestioneCoordinate | test_accesso_missing_coordinate |
      | Accesso allows minimal coordinates | api_models | TestAccessoGestioneCoordinate | test_accesso_with_minimal_coordinates |
      | Accesso accepts a Coordinate instance | api_models | TestAccessoGestioneCoordinate | test_accesso_with_coordinate_object |
      | Accesso serializes to JSON-compatible data | api_models | TestAccessoGestioneCoordinate | test_accesso_json_serialization |
      | Accesso deserializes JSON | api_models | TestAccessoGestioneCoordinate | test_accesso_json_deserialization |
      | Updated access accepts complete data | api_models | TestAccessoAggiornamento | test_accesso_valid_data_complete |
      | Updated access permits omitted optional data | api_models | TestAccessoAggiornamento | test_accesso_minimal_data |
      | Updated access accepts insertion operations | api_models | TestAccessoAggiornamento | test_accesso_operazione_inserimento |
      | Updated access accepts suppression operations | api_models | TestAccessoAggiornamento | test_accesso_operazione_soppressione |
      | Updated access permits metric-only identification | api_models | TestAccessoAggiornamento | test_accesso_with_metrico_no_numero |
      | Updated access accepts maximum field lengths | api_models | TestAccessoAggiornamento | test_accesso_max_length_validation |
      | Updated access permits missing coordinates | api_models | TestAccessoAggiornamento | test_accesso_coordinate_optional |
      | Updated access requires civic identifiers for replacement | api_models | TestAccessoAggiornamento | test_accesso_validator_progr_civico_required_for_R |
      | Updated access requires civic identifiers for suppression | api_models | TestAccessoAggiornamento | test_accesso_validator_progr_civico_required_for_S |
      | Updated access rejects civic numbers for suppression | api_models | TestAccessoAggiornamento | test_accesso_validator_numero_not_allowed_for_S |
      | Updated access rejects simultaneous number and metric values | api_models | TestAccessoAggiornamento | test_accesso_validator_numero_metrico_exclusive |
      | Updated access rejects metric values for suppression | api_models | TestAccessoAggiornamento | test_accesso_validator_metrico_not_allowed_for_S |
      | Updated access limits census-section data to insert and replace | api_models | TestAccessoAggiornamento | test_accesso_validator_sezione_censimento_only_for_I_R |
      | Updated access limits block data to insert and replace | api_models | TestAccessoAggiornamento | test_accesso_validator_isolato_only_for_I_R |
      | Updated access accepts valid insert operations | api_models | TestAccessoAggiornamento | test_accesso_validator_valid_I_operation |
      | Updated access accepts valid suppression operations | api_models | TestAccessoAggiornamento | test_accesso_validator_valid_S_operation |
      | Operation values remain stable | api_models | TestTipoOperazione | test_tipo_operazione_values |
      | Operation enum has only its supported members | api_models | TestTipoOperazione | test_tipo_operazione_members |
      | A provision accepts valid data | api_models | TestProvvedimento | test_provvedimento_valid_data |
      | A provision permits all optional values to be omitted | api_models | TestProvvedimento | test_provvedimento_all_none |
      | A zero flag requires provision data | api_models | TestProvvedimento | test_provvedimento_flag_delibera_0_requires_data_and_protocollo |
      | A one flag requires provision data | api_models | TestProvvedimento | test_provvedimento_flag_delibera_1_requires_data_and_protocollo |
      | A zero flag accepts complete provision data | api_models | TestProvvedimento | test_provvedimento_flag_delibera_0_with_data_and_protocollo |
      | A one flag accepts complete provision data | api_models | TestProvvedimento | test_provvedimento_flag_delibera_1_with_data_and_protocollo |
      | Provision flags reject out-of-range values | api_models | TestProvvedimento | test_provvedimento_flag_delibera_out_of_range |
      | Provision flags reject negative values | api_models | TestProvvedimento | test_provvedimento_flag_delibera_negative |
      | Provision protocol numbers enforce maximum length | api_models | TestProvvedimento | test_provvedimento_protocollo_max_length |
      | Provision protocol numbers allow maximum length | api_models | TestProvvedimento | test_provvedimento_protocollo_max_length_valid |
      | Prefecture authorizations accept valid data | api_models | TestAutPrefettura | test_aut_prefettura_valid_data |
      | Prefecture authorizations permit omitted values | api_models | TestAutPrefettura | test_aut_prefettura_all_none |
      | Prefecture authorization protocol numbers enforce maximum length | api_models | TestAutPrefettura | test_aut_prefettura_protocollo_max_length |
      | Prefecture authorization protocol numbers allow maximum length | api_models | TestAutPrefettura | test_aut_prefettura_protocollo_max_length_valid |
      | Project and client-setting forms preserve validation and update behavior | forms | TestQPDNDForms | test_projects |
      | Client-setting forms preserve validation and update behavior | forms | TestQPDNDForms | test_client_setting |
      | Projects preserve API identifiers across updates | models | TestQPDNDModels | test_project |
      | Client settings persist their PDND configuration | models | TestQPDNDModels | test_client_setting |
      | OGC API status is available | pdnd_auth | TestQPDNDModels | test_status |
      | OGC API authentication and voucher-cache behavior are preserved | pdnd_auth | TestQPDNDModels | test_auth |
      | Project administration supports create, update and delete | views | TestQPDNDViews | test_projects |
      | OGC API responses match the published schemas | views | TestQPDNDViews | test_ocg_api |
      | OpenAPI schema download behavior is preserved | views | TestQPDNDViews | test_download_openapi_schema |
      | Project information API permission behavior is preserved | views | TestQPDNDViews | test_projectinfo_api |
