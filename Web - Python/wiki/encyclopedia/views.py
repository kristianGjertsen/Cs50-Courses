from django.shortcuts import render
from django.urls import reverse
from . import util
import markdown


def index(request):
    list = [e for e in util.list_entries() if e != ""]
    return render(request, "encyclopedia/index.html", {"entries": list})


# Site to reach all sites
def site(request, name):
    print("trying to show site", name, "-- -- -- -- -- -- -- --")
    current_site = util.get_entry(name)
    if current_site is None:
        return render(
            request,
            "encyclopedia/wiki_site.html",
            {
                "title": "404 Not found",
                "html_content": f"<h1> {name} does not exist in wiki</h1>",
                "exist": False,
            },
        )

    h_text = markdown.markdown(current_site)
    return render(
        request,
        "encyclopedia/wiki_site.html",
        {"title": name.capitalize(), "html_content": h_text, "exist": True},
    )


def search(request):
    print("Starting Search ---- --- --- --- -")
    if request.method == "POST":
        search_input = request.POST.get("q", "").lower()
    else:
        print("Not a post submitt --- --- --- ")
        return render(
            request, "encyclopedia/index.html", {"entries": util.list_entries()}
        )

    if search_input:
        all_pages = util.list_entries()
        print("All pages *** **@ ", all_pages)
        for page in all_pages:
            if search_input == page.lower():
                return site(request, search_input)

        subsr_pages = []
        for page in all_pages:
            if search_input in page.lower():
                subsr_pages.append(page)

        print("Trying to find substring -- --- --- -- ")
        print(subsr_pages)
        return render(
            request,
            "encyclopedia/search.html",
            {"entries": subsr_pages, "search": search_input},
        )
    else:
        return render(
            request, "encyclopedia/index.html", {"entries": util.list_entries()}
        )


def add(request):
    if request.method == "POST":
        title = request.POST.get("title", "").lower()
        # If page exist display it
        for page in util.list_entries():
            if title == page.lower():
                return render(
                    request,
                    "encyclopedia/wiki_site.html",
                    {
                        "title": "Page Alredy Exists",
                        "html_content": f"<h1>Page Alredy Exists</h1>",
                    },
                )

        if title == "":
            return render(request, "encyclopedia/add.html")

        # Create new filere
        filename = f"{title.capitalize()}.md"
        page_content = request.POST.get("text", "")  # Get data
        with open(f"entries/{filename}", "w") as file:
            file.write(f"#{title.capitalize()}\n\n")
            file.write(page_content)

        return site(request, title)
    return render(request, "encyclopedia/add.html")


def edit(request, title):
    filename = f"entries/{title}.md"
    # Open file and replace all text with text from user
    if request.method == "POST":
        content = request.POST.get("text", "")
        with open(filename, "w") as file:
            file.write(content)
        return site(request, title)
    # Display the site-text in textarea for user to edit and send
    else:
        wiki_page = ""
        with open(filename, "r") as file:
            wiki_page = file.read()
        return render(
            request,
            "encyclopedia/edit.html",
            {"text_before": wiki_page, "title": title},
        )


import random


def random_page(request):
    li = [e for e in util.list_entries() if e != ""]
    page = li[random.randint(0, len(li) - 1)]
    return site(request, page)
