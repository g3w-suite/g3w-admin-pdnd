import importlib
import unittest

from behave import given, then, when


@given('the "{module}" Django case "{test_class}.{test_method}"')
def select_django_case(context, module, test_class, test_method):
    context.case_module = importlib.import_module(f'qpdnd.tests.steps.cases.{module}')
    context.case_class = getattr(context.case_module, test_class)
    context.case_method = test_method


@when('the regression case is run')
def run_django_case(context):
    suite = unittest.TestSuite([
        context.case_class(context.case_method),
    ])
    context.case_result = unittest.TestResult()
    suite.run(context.case_result)


@then('all original assertions pass')
def check_django_case(context):
    result = context.case_result
    details = '\n'.join(
        traceback for _, traceback in result.errors + result.failures
    )
    assert result.testsRun == 1, details or 'The case did not run.'
    assert not result.errors and not result.failures, details
    assert not result.skipped, result.skipped
