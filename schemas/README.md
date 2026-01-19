To create a PyDantic model from openapi schema:

Install `datamodel-code.generatore`
```bash
pip3 install datamodel-code-generator
```

I.e. for `aggiornamento_interni.yml`

```bash
datamodel-codegen --input aggiornamento_interni.yml --input-file-type openapi --output aggiornamentointerni.py
```

