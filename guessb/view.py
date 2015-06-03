# coding= utf-8
'''Created on 20/03/2015

@author: felipexw
'''
from django.shortcuts import render
from DAO import DAOFactory
import math
from django.http.response import HttpResponse


QUANTIDADE_PUBLICACOES_PAGINA = 5
ACCESS_TOKEN = None

def showAbout(request):
    html = '<div id="jumbotron" class="jumbotron"> <h1>Seja bem-vindo ao Guessb!</h1><p>Este webapp é o Trabalho de Conclusão apresentado ao Curso de Sistemas de Informação, da Universidade do Estado de Santa Catarina, como requisito parcial para obtenção do grau de Bacharel em Sistemas de Informação.</p></div></div>'
    return HttpResponse(html)

def getPaginationIndexes(numero_pagina):
    if  numero_pagina == None:
        numero_pagina = 1
    
    ultimo_indice = math.fabs((QUANTIDADE_PUBLICACOES_PAGINA * int(numero_pagina)))
    primeiro_indice = math.fabs(ultimo_indice - QUANTIDADE_PUBLICACOES_PAGINA)
    return primeiro_indice, ultimo_indice

def __checkCookie(request):
    if not 'ACCESS_TOKEN' in request.session._session:
        request.session['ACCESS_TOKEN'] = request.GET.get('ACCESS_TOKEN')
        request.session.set_expiry(3600)    

def __checkAccessTokenPostId(content, request):
    for data in content:
        if 'accessToken' in data:
            if  data.get('postId') not in request.session:
                request.session[data.get('postId')] = data.get('accessToken')
           
def showPosts(request):
    firstIndex, lastIndex = getPaginationIndexes(request.GET.get('page'))
    html = '<div class="container theme-showcase" role="main"> <div class="row">  <div class="bs-example" data-example-id="panel-without-body-with-table"> <div class="panel panel-default"><div class="panel-heading"><h4>Publicacoes no Facebook</h4></div><table class="table table-hover"> <thead>  <tr><th> Perfil </th> <th> Autor </th> <th> Publicacao</th> <th> Link </th> <th> Acao </th> </tr> </thead> <tbody id="tbody_conteudo">'
    
    response = HttpResponse()
    
    __checkCookie(request)
    
    content = []
        
    try:
        factory = DAOFactory.getDAOFactory()
        content = factory.getGenericDAO(request.session.get('ACCESS_TOKEN')).getFeed(firstIndex, lastIndex)
        
        __checkAccessTokenPostId(content, request)
    except Exception as e:
        html = '<div id="jumbotron" class="jumbotron"> <p>Sua sessão no Facebook expirou. Por favor, conecte-se novamente.</p></div>'
        try:
            request.session.__delitem__('ACCESS_TOKEN')
        except Exception as ec:
            print ec
    else:
        j = 0
        
        for i in xrange(0, len(content)):
            if i >= firstIndex and i < lastIndex:
                profileImg = '<img  src="//graph.facebook.com/' + content[i].get('profileId') + '/picture?type=large"' + ' style="width: 45px; height: 45px;" class="img-circle"/>' 
                img = '<img  src="//graph.facebook.com/' + content[i].get('authorId') + '/picture?type=large"' + ' style="width: 75px; height: 75px;" class="img-circle"/>'
                postId = "'%s'" % content[i]['postId']
                st = "showCommentsFromPosts(%s,%s)" % ('1', postId)
            
                html += '<tr><td>' + profileImg + '<p style="text-align: center">' + content[i]['profileName'] + '</p>  </td><td>' + img + '<p style="text-align: center">' + content[i]['authorName'] + '</p>  </td><td><p>' + content[i]['messageContent'] + '</p></td><td><p><a href="%s' % content[i]['link'] + '">Link</a></p></td><td><p><button type="button" onclick=%s' % st + ' role="button" class="btn btn-md btn-success"><i class="glyphicon glyphicon-tag icon-th"></i></a></p></td></tr>'
                j += 1
                if j == QUANTIDADE_PUBLICACOES_PAGINA:
                    break        
    
        html += ' <tbody id="tbody_conteudo"> </tbody> </table> </div> </div> '                        
        html += __get_html_paginacao(len(content), QUANTIDADE_PUBLICACOES_PAGINA, "'posts'", '', request.GET.get('page'))

    response.write(html)
    return response    

def __get_html_paginacao(tamanho, quantidade_comentarios=5, redirect_page="'posts'", postId='', page='0'):
    html = '<ul id="paginacao" class="pagination pagination-lg">'
    
    limite = int(math.ceil(float(tamanho) / quantidade_comentarios)) 
    functionName = ''
    
    for i in xrange(0, limite):
        className = ''
        if page == str(i + 1):
            className = 'active' 
        
        if redirect_page == "'posts'":
            functionName = 'showPosts(%s, %i)' % ('1', int(i + 1))
        
        else:
            functionName = "showCommentsFromPosts(%i, '%s')" % (int(i+1), postId) 
        
        if postId == 0:
            html += '<li class=%s' % className + '" id="%i' % int(i + 1) + '"><a onclick="%s" ' % functionName + 'href="javascript:void(0)">%i' % int(i + 1) + '</a></li>'
        else:
            html += '<li class="%s' % className + '" id="%i' % int(i + 1) + '"><a onclick="%s" ' % functionName + 'href="javascript:void(0)">%i' % (int(i) + 1) + '</a></li>'
    html += '</ul>' 
    return html    

def showHome(request):
    html = '<div id="jumbotron" class="jumbotron"> <h1>Seja bem-vindo ao Guessb!</h1><p>Este webapp faz análise de sentimentos (positivo, negativo ou neutro) em comentários escrito em português do Brasil, compartilhados por seguidores timeline do usuário dessa ferramenta. O classificador utilizado é o Multinomial Naive Bayes.</p></div></div>'
    return render(request, 'base.html', {'conteudo_dinamico':html})

def __getAccessTokenPostIt(request, postId):
    if postId in request.session:
        return request.session.get(postId)
    
    return request.session.get('ACCESS_TOKEN')

def showComments(request):
    firstIndex, lastIndex = getPaginationIndexes(request.GET.get('page'))
    
    html = '<div class="container theme-showcase" role="main"> <div class="row"> <div class="bs-example" data-example-id="panel-without-body-with-table"> <div class="panel panel-default"> <div class="panel-heading">  <div class="pull-right">  <div id="div_btn_group" onclick="showFilters(this)";class="btn-group"><button type="button" class="multiselect dropdown-toggle btn btn-default" data-toggle="dropdown" title=""><i class="glyphicon glyphicon-th icon-th"></i> <b class="caret"></b></button><ul class="multiselect-container dropdown-menu"><li>  <a tabindex="0">    <label class="checkbox">      <input onclick="filter();"type="checkbox" checked="true" value="Positivo" name="check_box" checked>Positivo</label> </a></li> <li><a tabindex="0"> <label class="checkbox"> <input type="checkbox" onclick="filter();" value="Negativo" name="check_box" checked>Negativo </label></a></li><li><a tabindex="0"><label class="checkbox"> <input type="checkbox"  onclick="filter();" value="Neutro" name="check_box" checked>Neutro</label></a></li></ul></div></div><h4>Publicacoes no Facebook</h4></div><table class="table table-hover"> <thead>  <tr> <th> Autor </th> <th> Publicacao</th> <th> Classificacao     </th> </tr> </thead> <tbody id="tbody_conteudo">'
    
    response = HttpResponse()
    
    __checkCookie(request)
    content = []
    
    try:
        factory = DAOFactory.getDAOFactory()
        accessToken = __getAccessTokenPostIt(request, request.GET.get('postId'))
        content, contentLength = factory.getGenericDAO(accessToken).getCommentsFeed(request.GET.get('postId'), firstIndex, lastIndex)
        
    except:
        html = '<div id="jumbotron" class="jumbotron"> <p>Sua sessão no Facebook expirou. Por favor, conecte-se novamente.</p></div>'
    
    else:
        for i in xrange(0, len(content)):
            html += '<tr><td> <img  src="//graph.facebook.com/' + content[i]['authorId'] + '/picture?type=large" style="width: 75px; height: 75px;" class="img-circle "/><p style="text-align: center">' + content[i]['authorName'] + '</p></td><td>' + content[i]['messageContent'] + '</td>' + '<td>' + content[i]['polarity'] + '</td></tr>'
        
        html += '</tbody> </table> </div> </div> '                        
        html += __get_html_paginacao(contentLength, QUANTIDADE_PUBLICACOES_PAGINA, "'comments'", request.GET.get('postId'), request.GET.get('page'))
    
    response.write(html)
    return response

