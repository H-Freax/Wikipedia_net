import json
from urllib import request, parse 
from multiprocessing import Pool #多进程处理
from itertools import chain
import networkx as nx

def link_to_title(link): #记录名称
  return link["title"]

def clean_if_key(page,key): #如果链接存在获取title
    if key in page.keys():
        return map(link_to_title,page[key])
    else: return []

def get_Wiki_links(pageTitle):
    safe_title = parse.quote(pageTitle) #编码 确保安全
    url = "https://en.wikipedia.org/w/api.php?action=query&\
prop=links|linkshere&pllimit=500&lhlimit=500&titles={}&\
format=json&formatversion=2".format(safe_title)
    page = request.urlopen(url).read()
    j = json.loads(page)
    jpage = j['query']['pages'][0]
    inbound = clean_if_key(jpage,"links")
    outbound = clean_if_key(jpage,"linkshere")
    return {"title": pageTitle,
            "in-links":list(inbound),
            "out-links":list(outbound)}

def flatten_network(page):
    return page["in-links"]+page["out-links"]

def page_to_edges(page):
    a = [(page['title'],p) for p in page['out-links']]
    b = [(p,page['title']) for p in page['in-links']]
    return a+b

if __name__ == "__main__":
    root = get_Wiki_links("Parallel_computing")
    initial_network = flatten_network(root)
    with Pool() as P:  #并行处理
        all_pages = P.map(get_Wiki_links, initial_network)
        edges = P.map(page_to_edges, all_pages)
    edges = chain.from_iterable(edges) #连接

    G = nx.DiGraph() #绘图
    for e in edges:
        G.add_edge(*e)
    nx.readwrite.gexf.write_gexf(G,"./MyGraph.gexf")
