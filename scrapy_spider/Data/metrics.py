from scrapy_spider.models import db_connect, Sites, WebPages, ExternalLinks
from sqlalchemy.orm import sessionmaker
from sqlalchemy import desc, asc, func, distinct
from math import ceil
from statistics import mean, median


def metrics_update():
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    session = Session()

    site_ids = session.query(Sites.id).filter(Sites.crawl_status == "CRAWELING").order_by(
        asc(Sites.last_crawl_date)).limit(100).all()

    for site_id in site_ids:
        try:
            publication_median, publication_mean, last_pub_date, pages_count, trending_section = site_pub_metrics(
                site_id)
            new_ext_links_median, new_ext_links_mean, pages_new_links = ext_links_metrics(site_id)

            new_ext_links_score = _new_ext_links_score(new_ext_links_median)
            pub_median_score = _pub_median_score(publication_median, pages_count)

            links_opp, links_opp_score_percent = _weighted_score([[new_ext_links_score, 30], [pub_median_score, 70]])

            session.query(Sites).filter(Sites.id == site_id).update({Sites.pub_median_indays: publication_median,
                                                                     Sites.pub_avg_indays: publication_mean,
                                                                     Sites.pages_count: pages_count,
                                                                     Sites.new_ext_links_median_indays: new_ext_links_median,
                                                                     Sites.new_ext_links_mean_indays: new_ext_links_mean,
                                                                     Sites.links_opp: links_opp,
                                                                     Sites.links_opp_score_percent: links_opp_score_percent,
                                                                     Sites.trending_section: trending_section})

            for page_id in pages_new_links.keys():
                try:

                    session.query(WebPages).filter(WebPages.id == page_id).update(
                        {WebPages.new_ext_domains: pages_new_links.get(page_id)})

                except Exception as error:
                    print(error)

            session.commit()

        except Exception as error:
            print(error)
            session.rollback()

        finally:
            session.close()


def site_pub_metrics(site_id):
    publication_mean = -1
    publication_median = -1

    engine = db_connect()
    Session = sessionmaker(bind=engine)
    session = Session()

    pages = session.query(WebPages.publication_date).filter(
        WebPages.publication_date.isnot(None)).filter(
        WebPages.site_id == site_id).group_by(WebPages.publication_date).order_by(desc(WebPages.publication_date)).all()

    last_pub_date = pages[0]
    pages_count = len(pages)

    pages_copy = pages
    deltas = []

    for index, page in enumerate(pages, 0):
        if index + 1 < len(pages_copy):

            cur_page_dt = page[0]
            nxt_page_dt = pages_copy[index + 1][0]

            delta = cur_page_dt - nxt_page_dt
            if delta.days > 0:
                deltas.append(delta.days)

    if deltas:
        publication_mean = ceil(mean(deltas))
        publication_median = median(deltas)

    latest_sections = session.query(WebPages.section).filter(
        WebPages.publication_date.isnot(None)).filter(WebPages.section != "Uncategorized").filter(
        WebPages.site_id == site_id).order_by(desc(WebPages.publication_date)).limit(20).all()

    sec_dict = dict()

    for page_section in latest_sections:

        count = sec_dict.get(page_section.section)
        if count is not None:
            sec_dict[page_section.section] = count + 1
        else:
            sec_dict[page_section.section] = 1

    if not sec_dict:
        trending_section = "Uncategorized"
    else:
        trending_section = max(sec_dict, key=sec_dict.get)

    return publication_median, publication_mean, last_pub_date, pages_count, trending_section


def ext_links_metrics(site_id):
    engine = db_connect()
    Session = sessionmaker(bind=engine)
    session = Session()

    site_links = dict()
    pages_new_links = dict()
    site_new_links_count = []

    new_links_median = -1
    new_links_mean = -1

    for page in session.query(WebPages.id).filter(WebPages.site_id == site_id).order_by(
            asc(WebPages.modification_date)).all():

        page_id = page.id
        page_links = dict()

        for extlink in session.query(ExternalLinks.ext_domain, func.count(distinct(ExternalLinks.ext_domain))).filter(
                ExternalLinks.page_id == page_id).group_by(ExternalLinks.ext_domain).all():

            link_count = page_links.get(extlink.ext_domain)
            if link_count is not None:
                page_links[extlink.ext_domain] = link_count + 1
            else:
                page_links[extlink.ext_domain] = 1

        new_links_count, new_links = _new_ext_links(site_links, page_links)
        pages_new_links[page_id] = new_links_count
        site_new_links_count.append(new_links_count)
        site_links.update(page_links)

    if site_new_links_count:
        new_links_mean = mean(site_new_links_count)
        new_links_median = median(site_new_links_count)

    return new_links_median, new_links_mean, pages_new_links


def _pub_median_score(site_pub_median, site_pages_count):
    pub_score = 0

    if site_pub_median is not None:
        pub_score = site_pages_count / site_pub_median

    if pub_score > 50:
        pub_ratio = 100
    elif 30 < pub_score <= 50:
        pub_ratio = 50
    elif 10 < pub_score <= 30:
        pub_ratio = 30
    else:
        pub_ratio = 10

    return pub_ratio


def _new_ext_links_score(new_ext_links_median):
    new_ext_links_score = 0

    if new_ext_links_median is not None:

        if new_ext_links_median == 1:
            new_ext_links_score = 50
        elif new_ext_links_median == 2:
            new_ext_links_score = 70
        elif new_ext_links_median >= 3:
            new_ext_links_score = 100

    return new_ext_links_score


def _weighted_score(metrics):
    w_grade_list = []
    score = "UNKNOWN"

    for metric in metrics:
        grade = metric[0] / 100
        w_grade = metric[1] * grade

        w_grade_list.append(w_grade)

        grades_percent = sum(w_grade_list)

    if 80 < grades_percent <= 100:
        score = "MOST PROBABLY"
    elif 50 < grades_percent <= 80:
        score = "VERY POSSIBLE"
    elif 30 < grades_percent <= 50:
        score = "STILL POSSIBLE"
    elif 10 < grades_percent <= 30:
        score = "WEAK"
    elif 0 <= grades_percent <= 10:
        score = "VERY WEAK"

    return score, grades_percent


def _new_ext_links(previous_links, current_links):
    new_links_count = 0

    intersec = dict(set(current_links.items()) - set(previous_links.items()))
    if intersec is not None:
        new_links_count += len(intersec)

    return new_links_count, intersec


if __name__ == "__main__":
    metrics_update()
    # site_pub_metrics(50)
    #ext_links_metrics(50)
