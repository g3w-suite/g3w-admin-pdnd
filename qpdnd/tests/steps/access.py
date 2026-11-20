from behave import then, when
from django.urls import reverse


@when('an anonymous visitor opens the PDND project form')
def open_project_form(context):
    context.response = context.test.client.get(reverse('qpdnd-project-add'))


@then('they are redirected to the login page')
def check_login_redirect(context):
    assert context.response.status_code == 302
    assert '/login/' in context.response.headers['Location']
