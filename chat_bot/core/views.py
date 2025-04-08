from django.shortcuts import render
from django.http import HttpResponse
from django.conf import settings
import os

def my_html_view(request):
    return render(request, 'core/swagger-ui.html')

def swagger_yaml(request):
    # Caminho absoluto para o arquivo YAML
    yaml_path = os.path.join(settings.BASE_DIR, 'core/static/swagger/swagger.yaml')
    
    # Abrir e ler o conteúdo do arquivo YAML
    with open(yaml_path, 'r') as yaml_file:
        yaml_content = yaml_file.read()
    
    # Retornar o conteúdo do YAML como uma resposta HTTP
    return HttpResponse(yaml_content, content_type = 'application/x-yaml')
