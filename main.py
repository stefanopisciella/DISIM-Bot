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


def debug_by_printing_prettified_json(announcement):
    print(json.dumps(announcement, indent=4))

def check_if_the_announcement_must_be_scraped(is_a_disim_announcement, announcement_publication_date, announcement_url):
    json_filename = "disim_db.json" if is_a_disim_announcement else "adsu_db.json"

    with open(json_filename, 'r', encoding='utf-8') as json_file:
        json_content = json.load(json_file)

        if announcement_publication_date < json_content["last_scraped_announcement_publication_date"]:
            # the announcement to be checked is older than the last scraped announcement
            return False
        elif announcement_publication_date > json_content["last_scraped_announcement_publication_date"]:
            # the announcement to be checked is newer than the last scraped announcement

            json_content["last_scraped_announcement_publication_date"] = announcement_publication_date
            json_content["announcements_urls"] = [announcement_url]
            write_db_file(json_filename, json_content)
            return True
        elif announcement_publication_date == json_content["last_scraped_announcement_publication_date"]:
            # retrive all the urls relative to all announcement published on the disim website on the day of announcement_publication_date
            announcements_urls = json_content["announcements_urls"]

            if announcement_url in announcements_urls:
                # the announcement to be checked has been already scraped
                return False
            else:
                # the announcement to be checked hasn't been scraped yet

                json_content["announcements_urls"].append(announcement_url)
                write_db_file(json_filename, json_content)
                return True

def write_db_file(json_filename, data):
    with open(json_filename, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=4)

def get_disim_announcements():
    domain = "https://www.disim.univaq.it/"

    homepage_url = domain + "index"
    homepage = get_webpage(homepage_url)

    announcements = homepage('#annunci > div.two-thirds.column > div.row')

    announcements_to_be_published = []
    announcements.reverse()  # order the list of announcements from the least recent to the most recent
    for announcement in announcements:
        publication_date = pq(announcement).find("p.post_meta > span.calendar").text()
        reformatted_publication_date = reformat_date(publication_date)
        link_to_detail_page = domain + reformat_url(pq(announcement).find("h5 > a").attr("href"))

        if not check_if_the_announcement_must_be_scraped(True, reformatted_publication_date, link_to_detail_page):
            # the current announcement has already been scraped ==> don't continue scraping the current announcement
            continue

        title = pq(announcement).find("h5 > a").text()
        announcement_tags = get_announcement_tags(pq(announcement).find("p.post_meta > span.tags > a"))
        preview_of_the_announcement_content = pq(announcement).find("p:nth-child(2)").text()

        announcement_to_be_published = {
            "website": "disim",
            "title": title,
            "link_to_detail_page": link_to_detail_page,
            "publication_date": publication_date,
            "reformatted_publication_date": reformatted_publication_date,
            "announcement_tags": announcement_tags,
            "preview_of_the_announcement_content": preview_of_the_announcement_content
        }
        announcements_to_be_published.append(announcement_to_be_published)

    return announcements_to_be_published

def get_adsu_announcements():
    domain = "https://www.adsuaq.org/"

    news_section_url = domain + "category/news"
    news_section = get_webpage(news_section_url)

    announcements = news_section('ul.post_list_ul > li')

    announcements_to_be_published = []
    announcements.reverse()  # order the list of announcements from the least recent to the most recent
    for announcement in announcements:
        publication_date = pq(announcement).find("div.stm_post_details > ul > li.post_date").text()
        reformatted_publication_date = reformat_date(publication_date)
        link_to_detail_page = pq(announcement).find("h4 > a").attr("href")

        if not check_if_the_announcement_must_be_scraped(False, reformatted_publication_date, link_to_detail_page):
            # the current announcement has already been scraped ==> don't continue scraping the current announcement
            continue

        title = pq(announcement).find("h4 > a").text()

        announcement_tags = pq(announcement).find("div.stm_post_details > ul > li.post_cat > span").text()
        announcement_tags = announcement_tags.split(', ')

        preview_of_the_announcement_content = pq(announcement).find("div.post_excerpt > p").text()

        announcement_to_be_published = {
            "website": "adsu",
            "title": title,
            "link_to_detail_page": link_to_detail_page,
            "publication_date": publication_date,
            "reformatted_publication_date": reformatted_publication_date,
            "announcement_tags": announcement_tags,
            "preview_of_the_announcement_content": preview_of_the_announcement_content
        }
        announcements_to_be_published.append(announcement_to_be_published)

    return announcements_to_be_published

def main():
    announcements_to_be_published = get_disim_announcements()
    announcements_to_be_published.extend(get_adsu_announcements())

    debug_by_printing_prettified_json(announcements_to_be_published)


if __name__ == '__main__':
    main()
