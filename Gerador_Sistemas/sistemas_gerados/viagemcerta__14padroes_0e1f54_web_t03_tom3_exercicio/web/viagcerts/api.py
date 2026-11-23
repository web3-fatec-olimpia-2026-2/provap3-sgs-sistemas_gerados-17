"""
API REST da app viagcerts (JSON, só com Django — sem pacote extra):

    GET    api/v1/          lista (?limite=N; no máximo VIAGCERTS_API_LIMITE)   → 200
    POST   api/v1/          cria (corpo JSON)                                 → 201 | 400
    GET    api/v1/<pk>/     um registro                                       → 200 | 404
    PUT    api/v1/<pk>/     troca TODOS os campos                             → 200 | 400
    PATCH  api/v1/<pk>/     troca só os campos enviados                       → 200 | 400
    DELETE api/v1/<pk>/     apaga                                             → 204
    GET    api/v1/campos/   os campos de cada endpoint (disponíveis e expostos)  → 200
    GET    api/             RESUMO do painel (o link "API" do site): itens + total → 200

CAMPOS DE CADA ENDPOINT: cada endpoint ("v1" e "resumo") mostra só os campos EXPOSTOS. O projeto escolhe
campo a campo em config/settings.py (VIAGCERTS_API_CAMPOS — o que o `sgs api config` escreve), e quem
chama ainda pode pedir só alguns, entre os expostos: ?campos=a,b (campo oculto não aparece nem pedindo).

A validação é a MESMA das telas: o ViagcertForm (ModelForm com os validators do model). O valor final
vem do ViagcertService (Strategy do núcleo). O CSRF continua ligado: quem chama de fora manda o cookie
csrftoken e o cabeçalho X-CSRFToken (como o fetch() de uma página do próprio site).
"""
import json

from django.forms.models import model_to_dict
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse

from . import settings as config_app
from .forms import ViagcertForm
from .models import Viagcert
from .services import ViagcertService
from .viewmodels import ItemVM, PainelVM

ENDPOINTS = ("v1", "resumo")
CALCULADOS = ("total", "valor_final", "codigo", "titulo", "valor")
PADRAO_RESUMO = ("id", "codigo", "titulo", "valor")


def campos_disponiveis():
    """Tudo o que um endpoint PODE mostrar: o id, os campos do model e os valores calculados."""
    return ["id"] + [c.name for c in Viagcert._meta.fields if not c.primary_key] + list(CALCULADOS)


def exposto_por_padrao(endpoint, campo):
    if endpoint == "resumo":
        return campo in PADRAO_RESUMO
    return campo not in ("codigo", "titulo", "valor")   # v1: o registro inteiro + total e valor_final


def campos_expostos(endpoint, request=None):
    """Os campos do endpoint: o padrão + o que o projeto mudou (API_CAMPOS) e, com ?campos=, só os pedidos."""
    escolhas = (config_app.valor("API_CAMPOS") or {}).get(endpoint, {})
    campos = [c for c in campos_disponiveis() if escolhas.get(c, exposto_por_padrao(endpoint, c))]
    pedidos = request.GET.get("campos") if request is not None else None
    if pedidos:
        quer = {c.strip() for c in pedidos.split(",") if c.strip()}
        campos = [c for c in campos if c in quer]
    return campos


def serializar(obj, campos=None):
    """Model → dict pronto para JSON (decimal, data e UUID viram texto), só com os campos expostos."""
    campos = campos_expostos("v1") if campos is None else campos
    dados, calculado = {}, None
    for campo in campos:
        if campo == "id":
            dados["id"] = obj.pk if isinstance(obj.pk, int) else str(obj.pk)
        elif campo == "total":
            dados["total"] = str(obj.total)
        elif campo in ("valor_final", "valor", "codigo", "titulo"):
            if calculado is None:                     # calcula uma vez só (Strategy do núcleo)
                final = ViagcertService().valor_final(obj)
                calculado = (ItemVM(obj, final), round(final, 2))
            vm, final = calculado
            dados[campo] = {"valor_final": final, "valor": vm.valor_formatado, "codigo": vm.codigo,
                            "titulo": vm.titulo}[campo]
        else:
            valor = getattr(obj, obj._meta.get_field(campo).attname)
            dados[campo] = valor if valor is None or isinstance(valor, (bool, int, str)) else str(valor)
    return dados


def resumo(request):
    """GET api/: o RESUMO do painel (o link "API" do site) — itens com os campos do endpoint resumo + total."""
    if request.method != "GET":
        return HttpResponseNotAllowed(["GET"])
    objetos = Viagcert.objects.order_by("pk")
    campos = campos_expostos("resumo", request)
    painel = PainelVM(objetos, ViagcertService())
    return JsonResponse({"itens": [serializar(o, campos) for o in objetos], "total": painel.total_formatado})


def campos(request):
    """GET api/v1/campos/: o que cada endpoint PODE mostrar e o que mostra agora."""
    return JsonResponse({"disponiveis": campos_disponiveis(),
                         "expostos": {endpoint: campos_expostos(endpoint) for endpoint in ENDPOINTS}})


def ler_corpo(request):
    """O corpo JSON (um objeto) ou None se não for JSON válido."""
    try:
        dados = json.loads(request.body or b"{}")
    except (ValueError, UnicodeDecodeError):
        return None
    return dados if isinstance(dados, dict) else None


def para_form(dados):
    """JSON → dados de formulário: sim/não vira "on"/ausente (exatamente o que o navegador manda)."""
    convertidos = {}
    for chave, valor in dados.items():
        if isinstance(valor, bool):
            if valor:
                convertidos[chave] = "on"
            continue
        convertidos[chave] = "" if valor is None else str(valor)
    return convertidos


def erros(form):
    return {campo: [e["message"] for e in lista] for campo, lista in form.errors.get_json_data().items()}


def metodos_permitidos(*todos):
    """Com VIAGCERTS_API_ESCRITA = False, só o GET continua valendo."""
    return list(todos) if config_app.valor("API_ESCRITA") else ["GET"]


def colecao(request):
    """GET lista · POST cria."""
    permitidos = metodos_permitidos("GET", "POST")
    if request.method not in permitidos:
        return HttpResponseNotAllowed(permitidos)
    if request.method == "GET":
        maximo = config_app.valor("API_LIMITE")
        try:
            limite = int(request.GET.get("limite", maximo))
        except ValueError:
            limite = maximo
        limite = max(1, min(limite, maximo))
        objetos = Viagcert.objects.order_by("pk")[:limite]
        campos_v1 = campos_expostos("v1", request)
        return JsonResponse({"itens": [serializar(o, campos_v1) for o in objetos], "limite": limite,
                             "total_registros": Viagcert.objects.count()})
    dados = ler_corpo(request)
    if dados is None:
        return JsonResponse({"erro": "envie um objeto JSON no corpo"}, status=400)
    form = ViagcertForm(para_form(dados))
    if not form.is_valid():  # os validators do model valem aqui também
        return JsonResponse({"erros": erros(form)}, status=400)
    return JsonResponse(serializar(form.save()), status=201)


def item(request, pk):
    """GET um · PUT troca tudo · PATCH troca parte · DELETE apaga."""
    permitidos = metodos_permitidos("GET", "PUT", "PATCH", "DELETE")
    if request.method not in permitidos:
        return HttpResponseNotAllowed(permitidos)
    obj = Viagcert.objects.filter(pk=pk).first()
    if obj is None:
        return JsonResponse({"erro": "registro não encontrado"}, status=404)
    if request.method == "GET":
        return JsonResponse(serializar(obj, campos_expostos("v1", request)))
    if request.method == "DELETE":
        obj.delete()
        return HttpResponse(status=204)
    dados = ler_corpo(request)
    if dados is None:
        return JsonResponse({"erro": "envie um objeto JSON no corpo"}, status=400)
    if request.method == "PATCH":  # parte: completa com o que o registro já tem
        atuais = model_to_dict(obj, fields=ViagcertForm._meta.fields)
        dados = {**{k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in atuais.items()}, **dados}
    form = ViagcertForm(para_form(dados), instance=obj)
    if not form.is_valid():
        return JsonResponse({"erros": erros(form)}, status=400)
    return JsonResponse(serializar(form.save()))
