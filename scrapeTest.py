
import requests
from bs4 import BeautifulSoup
import csv
import pandas as pd

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

sydneyMainUrl = "https://www.booking.com/searchresults.html?label=bdot-Os1*aFx2GVFdW3rxGd0MYQS461500239550%3Apl%3Ata%3Ap1%3Ap22%2C563%2C000%3Aac%3Aap%3Aneg%3Afi%3Atikwd-334108349%3Alp9302486%3Ali%3Adec%3Adm%3Appccp%3DUmFuZG9tSVYkc2RlIyh9YYriJK-Ikd_dLBPOo0BdMww&sid=34bc06df5a0c2086848fc573f6044baf&aid=378266&sb_lp=1&src=index&error_url=https%3A%2F%2Fwww.booking.com%2Findex.html%3Faid%3D378266%26label%3Dbdot-Os1%252AaFx2GVFdW3rxGd0MYQS461500239550%253Apl%253Ata%253Ap1%253Ap22%252C563%252C000%253Aac%253Aap%253Aneg%253Afi%253Atikwd-334108349%253Alp9302486%253Ali%253Adec%253Adm%253Appccp%253DUmFuZG9tSVYkc2RlIyh9YYriJK-Ikd_dLBPOo0BdMww%26sid%3D34bc06df5a0c2086848fc573f6044baf%26sb_price_type%3Dtotal%26%26&ss=Sydney%2C+New+South+Wales%2C+Australia&is_ski_area=0&checkin_year=&checkin_month=&checkout_year=&checkout_month=&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1&ss_raw=sydney&ac_position=0&ac_langcode=en&ac_click_type=b&dest_id=-1603135&dest_type=city&iata=SYD&place_id_lat=-33.870457&place_id_lon=151.20901&search_pageview_id=ed3d29217cc80124&search_selected=true&nflt=class%3D4%3Bclass%3D3%3Bclass%3D5%3Bht_id%3D201"
hotelReviewsUrlFirstPart = "https://www.booking.com/reviewlist.html?aid=378266&label=bdot-Os1%2AaFx2GVFdW3rxGd0MYQS461500239550%3Apl%3Ata%3Ap1%3Ap22%2C563%2C000%3Aac%3Aap%3Aneg%3Afi%3Atikwd-334108349%3Alp1007740%3Ali%3Adec%3Adm%3Appccp%3DUmFuZG9tSVYkc2RlIyh9YYriJK-Ikd_dLBPOo0BdMww&sid=34bc06df5a0c2086848fc573f6044baf&cc1=au;dist=1;pagename="
hotelReviewsUrlSecondPart = ";srpvid=4f1d297ee9370098;type=total&&offset="
hotelReviewsUrlThirdPart = ";rows=10"

def scrapeProperties(url, offset, threshold, totalPages):

    data = []

    for i in range(0, totalPages):
        newUrl = url + "&offset="+str(i * offset)

        r = requests.get("http://localhost:8050/render.html", params={"url":newUrl, "wait":2}, headers=HEADERS)
        soup = BeautifulSoup(r.content, "html.parser")

        properties = soup.find_all("div", {"data-testid": "property-card"})

        for property in properties:
            list1 = []

            try:
                ogr = property.find("div", class_="b5cd09854e d10a6220b4").text
            except:
                continue

            try:
                revs = property.find("div", class_="d8eab2cf7f c90c0a70d3 db63693c62").text
            except:
                continue

            revs = int(revs.split(" ")[0].replace(",",""))
            if (int(revs) < threshold):
                continue

            name = property.find("div", {"data-testid": "title"}).text
            list1.append(name)
            address = property.find("span", {"data-testid": "address"}).text.split(", ")
            if (len(address) == 1):
                list1.append(None)
                list1.append(address[0])
            else:
                list1.append(address[0])
                list1.append(address[1])

            stars = list(property.find_all("span", class_="b6dc9a9e69 adc357e4f1 fe621d6382"))
            lastStar = int(stars[-1].find("svg").get("viewbox").split(" ")[-1]);

            if (lastStar == 128):
                list1.append(len(stars) - 1 + 0.5)
            else:
                list1.append(len(stars))

            list1.append(ogr)
            
            reviewName = property.find('a',{"data-testid":"title-link"}).get('href')    
            reviewName = reviewName.split("/")[5].split(".")[0]
            list1.append(reviewName)

            list1.append(revs)
            
            data.append(list1)
    
        print("Page " + str(i) + " done")
    
    with open("properties.csv", 'w') as csvfile:
        fields = ["Name","Suburb","city","Star Rating","Overall Guest rating","reviewName","count_rev"]

        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(fields)
        csvwriter.writerows(data) 
    
    print(len(data))



def scrapeReviews(url, totalPages, offset):
    
    list2 = []

    for i in range(totalPages):

        newUrl = url+ str(i * offset) + hotelReviewsUrlThirdPart
        r = requests.get("http://localhost:8050/render.html", params={"url":newUrl, "wait":2}, headers=HEADERS)
        soup = BeautifulSoup(r.content, "html.parser")

        people = soup.find_all("li", class_="review_list_new_item_block")
        
        for person in people:
            
            curList = []
            
            name = person.find("span", class_="bui-avatar-block__title").text.strip()
            try:
                nationality = person.find("span", class_="bui-avatar-block__subtitle").text.strip()
            except:
                continue
            
            try:
                room = person.find("a", class_="c-review-block__room-link").text.strip()
            except:
                room = None

            left = person.find("div", class_="bui-grid__column-3 c-review-block__left")
            right = person.find("div", class_="bui-grid__column-9 c-review-block__right")

            try:
                stayDuration = left.find("ul", class_="bui-list bui-list--text bui-list--icon bui_font_caption c-review-block__row c-review-block__stay-date").find("div", class_="bui-list__body").find(text=True, recursive=False)
                stayDuration = stayDuration.split(" ")
                stayDuration = stayDuration[0].strip() + " " + stayDuration[1].strip()
            except:
                continue

            try:
                checkInMonth, checkInYear = left.find("span", class_="c-review-block__date").text.split(" ")
            except:
                continue
            
            try:
                igr = right.find("div", class_="bui-review-score__badge").text
            except:
                continue

            reviews = right.find_all("span", class_="bui-u-sr-only")

            if (len(reviews) == 0):
                continue

            elif (len(reviews) == 1):
                if (reviews[0].text == "Liked"):
                    positiveReview = right.find("span", class_="c-review__body").text
                    negativeReview = "None"
                else:
                    positiveReview = "None"
                    negativeReview = right.find("span", class_="c-review__body").text
            
            else:
                reviews = right.find_all("span", class_="c-review__body")
                positiveReview = reviews[0].text
                negativeReview = reviews[1].text

            language = right.find("span", class_="c-review__body").get("lang");
            
            curList.append(name)
            curList.append(nationality)
            curList.append(room)
            curList.append(stayDuration)
            curList.append(checkInMonth)
            curList.append(checkInYear)
            curList.append(igr)
            curList.append(positiveReview)
            curList.append(negativeReview)
            curList.append(language)

            list2.append(curList)
        
        print(str(totalPages - i - 1) + "pages to go...")
    
    return list2
    
    


def scrapePropertiesHelper(url): # Give the main city url after applying filters if any.

    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.content, "html.parser")
    buttons = soup.find_all("button", class_="fc63351294 f9c5690c58")
    maxi = 0
    for button in buttons:
        try:
            maxi = max(int(button.text), maxi)
        except:
            continue

    scrapeProperties(url, 25, 50, maxi)




def scrapeReviewsHelper(fileName):
    df = pd.read_csv(fileName)
    df.columns = ["Name","Suburb","city","Star Rating","Overall Guest rating","reviewName","count_rev"]

    for i in range(0, df.shape[0]):

        url = hotelReviewsUrlFirstPart + df.loc[i, ['reviewName']].to_string(index=False) + hotelReviewsUrlSecondPart + str(0) + hotelReviewsUrlThirdPart
        r = requests.get("http://localhost:8050/render.html", params={"url":url, "wait":2}, headers=HEADERS)
        soup = BeautifulSoup(r.content, "html.parser")

        spans =  soup.find_all("span", class_="bui-u-sr-only")

        totalpages = int(spans[len(spans) - 1].text.split(" ")[1])

        list2 = scrapeReviews(hotelReviewsUrlFirstPart + df.loc[i, ['reviewName']].to_string(index=False) + hotelReviewsUrlSecondPart, totalpages, 10)

        list1 = list(df.loc[i])
        # print(url)
        for i in range(len(list2)):
            list2[i] = list1 + list2[i]

        with open(fileName[0:-5] + "Reviews.csv", "a") as csvfile:

            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(list2)

