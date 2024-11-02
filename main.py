import requests
import json

from pyquery import PyQuery as pq


def reformat_url(original_url):
    first_slash = original_url.find('/')
    second_slash = original_url.find('/', first_slash + 1)
    return original_url[:second_slash]


def reformat_date(original_date):
    new_date = original_date.replace(',', '')
    new_date = new_date.split(' ')

    year = new_date[-1]
    month = new_date[-2]
    day = new_date[-3]

    mesi = [
        "Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio",
        "Giugno", "Luglio", "Agosto", "Settembre", "Ottobre",
        "Novembre", "Dicembre"
    ]

    for i in range(12):
        if mesi[i] == month:
            month = i + 1
            break

    month = '0' + str(month) if int(month) < 10 else month
    day = '0' + str(day) if int(day) < 10 else day

    return f"{year}-{month}-{day}"


def get_webpage(url):
    response = requests.get(url)
    return pq(response.content)


def get_announcement_tags(tags):
    text_of_tags = []
    for tag in tags:
        text_of_tags.append(pq(tag).text())

    return text_of_tags


def print_prettified_json(website, title, link_to_detail_page, publication_date, reformatted_publication_date, announcement_tags,
                          preview_of_the_announcement_content):
    announcement = {
        "website": website,
        "title": title,
        "link_to_detail_page": link_to_detail_page,
        "publication_date": publication_date,
        "reformatted_publication_date": reformatted_publication_date,
        "announcement_tags": announcement_tags,
        "preview_of_the_announcement_content": preview_of_the_announcement_content
    }

    print(json.dumps(announcement, indent=4))


def scrape_disim_website():
    domain = "https://www.disim.univaq.it/"

    homepage_url = domain + "index"
    homepage = get_webpage(homepage_url)

    announcements = homepage('#annunci > div.two-thirds.column > div.row')

    for announcement in announcements:
        title = pq(announcement).find("h5 > a").text()
        link_to_detail_page = domain + reformat_url(pq(announcement).find("h5 > a").attr("href"))
        publication_date = pq(announcement).find("p.post_meta > span.calendar").text()
        reformatted_publication_date = reformat_date(publication_date)
        announcement_tags = get_announcement_tags(pq(announcement).find("p.post_meta > span.tags > a"))
        preview_of_the_announcement_content = pq(announcement).find("p:nth-child(2)").text()

        # START debug the results
        print_prettified_json("disim", title, link_to_detail_page, publication_date, reformatted_publication_date, announcement_tags, preview_of_the_announcement_content)
        # print(f"website: disim, title: {title}, publication date: {publication_date}, reformatted publication date: {reformatted_publication_date}, tags: {announcement_tags}, content preview: {preview_of_the_announcement_content}, link to detail page: {link_to_detail_page}")
        # END debug the results


def scrape_adsu_website():
    domain = "https://www.adsuaq.org/"

    news_section_url = domain + "category/news"
    news_section = get_webpage(news_section_url)

    announcements = news_section('#main > div.container > div.row > div.col-lg-8.col-md-8.col-sm-12.col-xs-12 > div.col_in.__padd-right > div.posts_list.with_sidebar > ul.post_list_ul > li')

    for announcement in announcements:
        title = pq(announcement).find("h4 > a").text()
        link_to_detail_page = pq(announcement).find("h4 > a").attr("href")

        publication_date = pq(announcement).find("div.stm_post_details > ul > li.post_date").text()
        reformatted_publication_date = reformat_date(publication_date)

        announcement_tags = pq(announcement).find("div.stm_post_details > ul > li.post_cat > span").text()
        announcement_tags = announcement_tags.split(', ')

        preview_of_the_announcement_content = pq(announcement).find("div.post_excerpt > p").text()

        # START debug the results
        print_prettified_json("adsu", title, link_to_detail_page, publication_date, reformatted_publication_date, announcement_tags, preview_of_the_announcement_content)
        # print(f"website: adsu, title: {title}, publication date: {publication_date}, reformatted publication date: {reformatted_publication_date}, tags: {announcement_tags}, content preview: {preview_of_the_announcement_content}, link to detail page: {link_to_detail_page}")
        # END debug the results



if __name__ == '__main__':
    scrape_disim_website()
    scrape_adsu_website()
