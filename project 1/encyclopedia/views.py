from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
import markdown2
try:
    from urllib.parse import urlparse  # Python 3 
except ImportError:
    from urlparse import urlparse  # Python 2
from random import choice

from . import util


def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def content(request, title):
    content = util.get_entry(title)  
    if content == None:
        return HttpResponse(f"Error: Page not found! {title}")
    else:
        return render(request, "encyclopedia/content.html", {
            "contents": markdown2.markdown(content), "title": title
        })
        
def search(request):
    if request.method == 'POST':
        query = request.POST.get("query")
    result = util.get_entry(query)
    
    # if get_entry returns a search result, redirect to url for that page
    if result != None:
        return redirect(reverse('content', args=[query]))
    
    # if get_entry does not return a result, see if query exists as a substring in list of entries
    else:
        list = util.list_entries()
        search_list = []
        for i in list:
            if query.lower() in i.lower():
                search_list.append(i)
                
        # if query does exist as one or multiple substrings, then return search result page
        if len(search_list) > 0:
            return render(request, "encyclopedia/search.html", {
                "entries": search_list
            })
        else:
            return HttpResponse("No matching results!")

def add(request):
    if request.method == "POST":
        new_title = request.POST.get("title")
        new_content = request.POST.get("content")
        
        # if entry with same title name already exists, display error message
        if util.get_entry(new_title) != None:
            return HttpResponse("Entry already exists!")
        
        util.save_entry(new_title, new_content)
        return redirect(reverse('content', args=[new_title]))
    return render(request, "encyclopedia/add.html")

def edit(request):
    pre_url = request.META.get('HTTP_REFERER')
    parsed = urlparse(pre_url)
    title = parsed.path[1:]
    content = util.get_entry(title)

    if request.method == "POST":
        new_content = request.POST.get("edited_content").encode()
        new_title = request.POST.get("title")
        util.save_entry(new_title, new_content)
        return redirect(reverse('content', args=[new_title]))               

    return render(request, "encyclopedia/edit.html", {
        "contents": content, "title": title
    })

def random(request):
    entries_list = util.list_entries()
    random_entry = choice(entries_list)
    return redirect(reverse('content', args=[random_entry]))
    
    
    

    
    
        

