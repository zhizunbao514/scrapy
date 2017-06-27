# -*- coding: utf-8 -*-
import scrapy
import re
import json
import datetime
from scrapy.loader import ItemLoader
from ArticleSpider.items  import ZhihuQuestionItem,ZhihuAnswerItem

try:
    import urlparse as parse
except:
    from urllib import parse


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com']

    cookies = {'q_c1': 'f6dfb8b0139741aca84c4a798558a6c0|1497868067000|1497868067000',
               'd_c0': '"AEACfuQM8AuPTlpwdnrcvSTPxkBsr0tj7UI=|1497868068"',
               '_zap': '3660fc94-fe81-47f8-b056-6c3d6b2c1914',
               '_xsrf': 'f249e814da8ea9a7bef393f697022a3a',
               'aliyungf_tc': 'AQAAAGuYRCLougcAadKJceZIAggi2Pro',
               'r_cap_id': '"NzZiNGYxMTQ0YjRjNDQ4OGFjYmUxNWI1NDIxOWZhYTg=|1498289926|93eeb7bc194f34e73584246ee00628bef00499ac"',
               'cap_id': '"YWJjYzJiNmJkYjcyNGYyZTkwYjU5NmI1NjcyZTA5MDA=|1498289926|92e021d48bbf2c3552afa6ff73a96c10f9658524"',
               '__utma': '51854390.196302598.1497946826.1497946826.1498289928.2',
               '__utmb': '51854390.0.10.1498289928',
               '__utmc=51854390': ' __utmz=51854390.1498289928.2.2.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/',
               '__utmv': '51854390.000--|2=registration_date=20160618=1^3=entry_date=20170619=1'}

    # question的第一页answer的请求url(这里用的是知乎的接口)
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    headers = {
        "Cookie": 'q_c1=f6dfb8b0139741aca84c4a798558a6c0|1497868067000|1497868067000; d_c0="AEACfuQM8AuPTlpwdnrcvSTPxkBsr0tj7UI=|1497868068"; _zap=3660fc94-fe81-47f8-b056-6c3d6b2c1914; _xsrf=f249e814da8ea9a7bef393f697022a3a; capsion_ticket="2|1:0|10:1498293852|14:capsion_ticket|44:ZjdjOWE2MDQ2NDE1NDA4ZGI2YTdiMDE1Mjk4MzkwNGE=|f47d53e2fefe2ea4196e224ad412e43976713bdbbc36bf982b12f4cd69ac26e0"; aliyungf_tc=AQAAAFRWhWrr8QoAadKJcaL+B3M5j5z9; r_cap_id="Zjg1MGI4MzE4MWRhNDMxNmI2MTcwNGVhM2IxNzdlZmI=|1498356809|893a820fb6058c6b8ad538329a89ca3c3d4986f5"; cap_id="YzdmNGI0M2M3ODY5NDYxYWJhY2RlMWVjY2FkY2UzMWM=|1498356809|96796d6822ffbaf2d9ada4ec906c49fd101e486d"; __utma=51854390.549617014.1498290484.1498298338.1498356808.4; __utmb=51854390.0.10.1498356808; __utmc=51854390; __utmz=51854390.1498298338.3.2.utmcsr=zhihu.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmv=51854390.000--|2=registration_date=20160618=1^3=entry_date=20170619=1',
        "HOST": "www.zhihu.com",
        "Origin": "https://www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest",
        "X-Xsrftoken": "f249e814da8ea9a7bef393f697022a3a"
    }

    headers2 = {
        "HOST": "www.zhihu.com",
        "Origin": "https://www.zhihu.com",
        "Referer": "https://www.zhihu.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
        "X-Requested-With": "XMLHttpRequest"
    }

    custom_settings = {
        "COOKIES_ENABLED": True
    }

    def parse(self, response):
        # # print(response.text)
        """
               提取出html页面中的所有url 并跟踪这些url进行一步爬取
               如果提取的url中格式为 /question/xxx 就下载之后直接进入解析函数
        """
        all_urls = response.css("a::attr(href)").extract()

        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)
        for url in all_urls:
            match_obj = re.match("(.*zhihu.com/question/(\d+)(/|$).*)", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
            else:
                # 如果不是question页面则直接进一步跟踪
                yield scrapy.Request(url, headers=self.headers, callback=self.parse)

    def parse_question(self, response):
        # 处理question页面， 从页面中提取出具体的question item
        if "QuestionHeader-title" in response.text:
            # 处理新版本
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))

            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            item_loader.add_css("title", "h1.QuestionHeader-title::text")
            item_loader.add_css("content", ".QuestionHeader-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", ".Question-mainColumn .QuestionMainAction::text")
            item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
            item_loader.add_css("watch_user_num", ".NumberBoard-value::text")
            item_loader.add_css("topics", ".QuestionHeader-topics .Popover div::text")
            question_item = item_loader.load_item()
        else:
            # 处理老版本请求
            match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
            if match_obj:
                question_id = int(match_obj.group(2))
            item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
            # item_loader.add_css("title", ".zh-question-title h2 a::text")
            item_loader.add_xpath("title",
                                  "//*[@id='zh-question-title']/h2/a/text()|//*[@id='zh-question-title']/h2/span/text()")
            item_loader.add_css("content", "#zh-question-detail")
            item_loader.add_value("url", response.url)
            item_loader.add_value("zhihu_id", question_id)
            item_loader.add_css("answer_num", "#zh-question-answer-num::text")
            item_loader.add_css("comments_num", "#zh-question-meta-wrap a[name='addcomment']::text")
            # item_loader.add_css("watch_user_num","#zh-question-side-header-wrap::text")
            item_loader.add_xpath("watch_user_num",
                                  "//*[@id='zh-question-side-header-wrap']/text()|//*[@class='zh-question-followers-sidebar']/div/a/strong/text()")
            item_loader.add_css("topics", ".zm-tag-editor-labels a::text")
            question_item = item_loader.load_item()

        yield scrapy.Request(url=self.start_answer_url.format(question_id, 20, 0), headers=self.headers2,callback=self.parse_answer)
        yield question_item


    def parse_answer(self, reponse):
        # 处理question的answer 这里用的是知乎的接口
        ans_json = json.loads(reponse.text)
        is_end=ans_json["paging"]["is_end"]
        next_url=ans_json["paging"]["next"]

        #提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item=ZhihuAnswerItem()
            answer_item["zhihu_id"]=answer["id"]
            answer_item["url"]=answer["url"]
            answer_item["question_id"]=answer["question"]["id"]
            answer_item["author_id"]=answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["content"]=answer["content"] if "content" in answer else None
            answer_item["parise_num"]=answer["voteup_count"]
            answer_item["comments_num"]=answer["comments_num"]  if "comments_num" in answer else None
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.datetime.now()
            yield answer_item
        if not is_end:
            yield scrapy.Request(next_url,headers=self.headers,callback=self.parse_answer)


    def start_requests(self):
        return [scrapy.Request(url='https://www.zhihu.com/#signin', cookies=self.cookies, headers=self.headers,
                               callback=self.login)]


    def login(self, response):
        response_text = response.text
        match_obj = re.match('.*name="_xsrf" value="(.*?)"', response_text, re.DOTALL)
        xsrf = ''
        if match_obj:
            xsrf = match_obj.group(1)
        if xsrf:
            post_url = "https://www.zhihu.com/login/phone_num"
            pot_data = {
                "_xsrf": "f249e814da8ea9a7bef393f697022a3a",
                "phone_num": "",
                "password": "",
                "captcha_type": "cn"
            }
        return [scrapy.FormRequest(
            url=post_url,
            formdata=pot_data,
            headers=self.headers,
            cookies=self.cookies,
            callback=self.check_login
        )]


    def check_login(self, response):
        text_json = json.loads(response.text)
        if "msg" in text_json and text_json["msg"] == "登录成功":
            for url in self.start_urls:
                yield scrapy.Request(url, dont_filter=True, headers=self.headers)
