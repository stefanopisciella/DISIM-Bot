"""
        detail_page = get_webpage(link_to_detail_page)('#wrapper > div:nth-child(1) > div:nth-child(3) > div:nth-child(3) > div.twelve.columns')
        announcement_content = detail_page.find('div.post_description > p')
        print(announcement_content)
        """

# #main > div.container > div > div.col-lg-8.col-md-8.col-sm-12.col-xs-12 > div > div > ul
#           In Evidenza, News, Residenze

"""s = ""
print(s.split(', '))"""

"""# START debug the results
        print_prettified_json("disim", title, link_to_detail_page, publication_date, reformatted_publication_date, announcement_tags, preview_of_the_announcement_content)
        # print(f"website: disim, title: {title}, publication date: {publication_date}, reformatted publication date: {reformatted_publication_date}, tags: {announcement_tags}, content preview: {preview_of_the_announcement_content}, link to detail page: {link_to_detail_page}")
        # END debug the results"""