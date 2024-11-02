"""
        detail_page = get_webpage(link_to_detail_page)('#wrapper > div:nth-child(1) > div:nth-child(3) > div:nth-child(3) > div.twelve.columns')
        announcement_content = detail_page.find('div.post_description > p')
        print(announcement_content)
        """

# #main > div.container > div > div.col-lg-8.col-md-8.col-sm-12.col-xs-12 > div > div > ul
#           In Evidenza, News, Residenze

s = ""
print(s.split(', '))