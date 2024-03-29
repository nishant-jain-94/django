from django.shortcuts import render

import os 

import requests
import json

CMS_CONTENTFUL=1
CMS_STORYBLOK=2


PROD_WEBSITE = "https://historyofjainism.com"

AMP = '⚡'

def context_processor( request ):
    data = { }
    data['APP_ENVIRONMENT'] = os.environ['APP_ENVIRONMENT']
    data['prod_url'] = PROD_WEBSITE + request.path
    return data

def ampstory( request, name ):
    query = """
query($name : String! ) {
    ampStoryCollection(limit: 1, where: {name: $name}) {
                items {
                    sys {
                        id
                    }
                    title,
                    subtitle
                    description,
                    story {
                        json
                        links {
                            assets {
                                block {
                                    url
                                    sys {
                                        id
                                    }
                                }
                            }
                        }
                    },
                    cover,
                    template
                }
            }
        }
    """
    res_json = get_content_as_json(query, { "name" : name })
    context = res_json['data']['ampStoryCollection']['items'][0]
    context['AMP'] = AMP
    context['theme'] = "theme/black.css"

    image_blocks = context['story']['links']['assets']['block']
    image_urls = { }
    for image_block in image_blocks:
        image_urls[image_block['sys']['id']] = image_block['url']

    pages = [ ]
    page = [ ]
    for element in context['story']['json']['content']:
        if element['nodeType'] == 'hr':
            pages.append(page)
            page = [ ]
        elif element['nodeType'] == 'paragraph':
            page.append({
                "type" : "paragraph",
                "value" : element['content'][0]['value']
            })
        elif element['nodeType'] == 'embedded-asset-block':
            page.append({
                "type" : "image",
                "src" : image_urls[element['data']['target']['sys']['id']]
            })
        elif element['nodeType'] == 'heading-3':
            page.append({
                "type" : "heading-3",
                "value" : element['content'][0]['value']
            })
        elif element['nodeType'] == 'heading-2':
            page.append({
                "type" : "heading-2",
                "value" : element['content'][0]['value']
            })
        elif element['nodeType'] == 'heading-1':
            page.append({
                "type" : "heading-1",
                "value" : element['content'][0]['value']
            })
        elif element['nodeType'] == 'unordered-list':
            page.append({
                "type" : "unordered-list",
                "list_items" : [ listitem['content'][0]['content'][0]['value'] for listitem in element['content'] ]
            })
        elif element['nodeType'] == 'ordered-list':
            page.append({
                "type" : "ordered-list",
                "list_items" : [ listitem['content'][0]['content'][0]['value'] for listitem in element['content'] ]
            })
    #print("Pages: ")
    #print(pages)
    context['pages'] = pages
    return render( request, context['template'], context )

def binder( request, lang, name ):

    query = """
       query {
            binderCollection(limit:1, where: {name:\"""" + name + """\", language:\"""" + lang + """\"}) {
                items {
                    title     
                    subtitle
                    cover
                    description
                    clipsCollection {
                        items {
                            sys {
                                id
                            }
                            title
                            abstract
                            source {
                                    type
                                    title
                                    author
                                cover {
                                  url
                                }
                                serial
                            }
                            document {
                                url
                            }
                            pages
                            author
                        }
                    }
                }
            }
        }   
    """
    res_json = get_content_as_json(query)
    binder = res_json['data']['binderCollection']['items'][0]
    return render( request, 'binder.html', {
            'lang' : lang,
            'name' : name,
            'binder' : binder,
            'title' : binder['title'],
            'subtitle' : binder['subtitle'],
            'description' : binder['subtitle'],
            'prod_url' : PROD_WEBSITE + request.path,
            'linkpreview_img' : binder['cover'][0]['url']
        } )

def blog( request, lang, name ):
    query = """
        query {
            blogCollection(limit:1, where: {name:\"""" + name + """\", language:\"""" + lang + """\"}) {
                items {
                    title
                    subtitle
                    cover
                    description
                    article
                    articleMore
                    translator
                    compiler
                    sourcesCollection {
                        items {
                            title
                            author
                        }
                    }
                }
            }
        }
    """
    res_json = get_content_as_json(query)
    blog = res_json['data']['blogCollection']['items'][0]
    return render( request, 'blog.html', {
            'lang' : lang,
            'name' : name,
            'blog' : blog,
            'title' : blog['title'],
            'subtitle' : blog['subtitle'],
            'description' : blog['subtitle'],
            'prod_url' : PROD_WEBSITE + request.path,
            'linkpreview_img' : blog['cover'][0]['url']
        } )

def get_content_as_json( query, variables=None, CMS=CMS_CONTENTFUL ):
    CONTENTFUL_URL= "https://graphql.contentful.com/content/v1/spaces/skavkfrlakjq/environments/master"
    STORYBLOK_URL = "https://gapi.storyblok.com/v1/api"
    #print(query, variables)
    if CMS==CMS_CONTENTFUL:
        headers = {
            "Authorization": "Bearer px87wXacTSetoV42SIP1YlO5Ace7MZMGAx9bMjDAJ3I",
            "Content-Type": "application/json"
        }
        url=CONTENTFUL_URL
    else: #CMS==CMS_STORYBLOK
        headers = {
            "Token" : "VSsin0zNORBSREiD6IQ6ewtt",
            "Version" : "published" if os.environ['APP_ENVIRONMENT'] == "production" else "draft"
        }
        url=STORYBLOK_URL
    r = requests.post( 
        url, 
        headers=headers,
        json={"query": query, "variables" : variables }
    )
    return json.loads(r.text)

def appdynamic( request ):
    return render( request, 'menu-share.html')


def appkit( request ):
    name="tirthankarmahaveer1"
    query = """
query($name : ID! ) {
  BookItem( id : $name ) {
      id,
      name,
      slug,
      full_slug,
      content {
        title,
        author,
        subtitle,
        description,
        language,
        cover {
          filename
        },
        body
      }
  }
}
    """
    res_json = get_content_as_json(query, { "name" : "book/" + name }, CMS_STORYBLOK )
    print(res_json)
    #compatibility with contentful
    res_json['data']['BookItem']['content']['cover']['0'] = { 'secure_url' : res_json['data']['BookItem']['content']['cover']['filename']}
    return render( request, 'appkitdemo.html', res_json['data']['BookItem']['content'] )

def home( request, generate_site=False ):
    query = """
        query {
            externalCollection {
                items {
                    typename : __typename
                    title
                    subtitle
                    url
                    cover
                    type
                    updated
                }    
            }
            binderCollection {
                items {
                    typename : __typename
                    name
                    language
                    title
                    subtitle
                    cover
                    updated
                }
            }
            blogCollection {
                items {
                    typename : __typename
                    name
                    language
                    title
                    subtitle
                    cover
                    updated
                }
            }
            ampStoryCollection {
                items {
                    typename : __typename
                    name
                    title
                    subtitle
                    cover
                    updated
                }
            }            
        }
    """
    res_json = get_content_as_json( query )
    #print(res_json)
    if generate_site:
        return res_json
    all_items = res_json['data']['externalCollection']['items'] \
                + res_json['data']['binderCollection']['items'] \
                + res_json['data']['blogCollection']['items'] \
                + res_json['data']['ampStoryCollection']['items']
    print("sorted: ", all_items)
    content = {
        'title' : "History of Jainism",
        'subtitle' : "It's time Real Jain History be told!!",
        'description' : "It's time Real Jain History be told!!",
        'prod_url' : PROD_WEBSITE + request.path,
        'cards' : sorted(all_items, key=lambda x:x['updated'], reverse=True)
        #'linkpreview_img' : binder['cover'][0]['url']
        }
    return render( request, 'home.html', content )




def book( request, name ):
    query = """
query($name : ID! ) {
  BookItem( id : $name ) {
      id,
      name,
      slug,
      full_slug,
      content {
        title,
        author,
        subtitle,
        description,
        language,
        cover {
          filename
        },
        body
      }
  }
}
    """
    res_json = get_content_as_json(query, { "name" : "book/" + name }, CMS_STORYBLOK )
    print(res_json)
    #compatibility with contentful
    res_json['data']['BookItem']['content']['cover']['0'] = { 'secure_url' : res_json['data']['BookItem']['content']['cover']['filename']}
    return render( request, 'book.html', res_json['data']['BookItem']['content'] )


