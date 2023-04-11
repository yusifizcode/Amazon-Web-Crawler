import scrapy
from scrapy import Request
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, redirect, request


app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///amazon.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)



class Reviews(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    names = db.Column(db.String(250))
    reviewerLink = db.Column(db.String(250))
    reviewTitles = db.Column(db.String(250))
    reviewBody = db.Column(db.String(250))
    verifiedPurchase = db.Column(db.String(250))
    postDate = db.Column(db.String(250))
    starRating = db.Column(db.String(250))
    helpful = db.Column(db.String(250))
    nextPage = db.Column(db.String(250))

class MyItem(scrapy.Item):
    names = scrapy.Field()
    reviewerLink = scrapy.Field()
    reviewTitles = scrapy.Field()
    reviewBody = scrapy.Field()
    verifiedPurchase = scrapy.Field()
    postDate = scrapy.Field()
    starRating = scrapy.Field()
    helpful = scrapy.Field()
    nextPage = scrapy.Field(default = 'null')
    
    
class ReviewspiderSpider(scrapy.Spider):
    name = 'reviewspider'
    allowed_domains = ["amazon.com"]
    start_urls = [""]
    myBaseUrl = ''
    start_urls = []
    def __init__(self, category='', **kwargs): # The category variable will have the input URL.
        self.myBaseUrl = category
        self.start_urls.append(self.myBaseUrl)
        super().__init__(**kwargs)

    custom_settings = {'FEED_URI': 'tutorial/outputfile.json', 'CLOSESPIDER_TIMEOUT' : 15} # This will tell scrapy to store the scraped data to outputfile.json and for how long the spider should run.

    
    def parse(self, response):
    # This will get the link for the all reviews tag on amazon page.
        all_reviews = response.xpath('//div[@data-hook="reviews-medley-footer"]//a[@data-hook="see-all-reviews-link-foot"]/@href').extract_first()
    # This will tell scrapy to move to all reviews page for further scraping.
        yield response.follow("https://www.amazon.com"+all_reviews, callback=self.parse_page)

    
    def parse_page(self, response):
  
  # Scraping all the items for all the reviewers mentioned on that Page
  
        names=response.xpath('//div[@data-hook="review"]//span[@class="a-profile-name"]/text()').extract()
        print(names)
        reviewerLink=response.xpath('//div[@data-hook="review"]//a[@class="a-profile"]/@href').extract()
        reviewTitles=response.xpath('//a[@data-hook="review-title"]/span/text()').extract()
        reviewBody=response.xpath('//span[@data-hook="review-body"]/span').xpath('normalize-space()').getall()
        verifiedPurchase=response.xpath('//span[@data-hook="avp-badge"]/text()').extract()
        postDate=response.xpath('//span[@data-hook="review-date"]/text()').extract()
        starRating=response.xpath('//i[@data-hook="review-star-rating"]/span[@class="a-icon-alt"]/text()').extract()
        helpful = response.xpath('//span[@class="cr-vote"]//span[@data-hook="helpful-vote-statement"]/text()').extract()
  
  # Extracting details of each reviewer and storing it in in the MyItem object items and then appending it to the JSON file.
  
        for (name, reviewLink, title, Review, Verified, date, rating, helpful_count) in zip(names, reviewerLink, reviewTitles, reviewBody, verifiedPurchase, postDate, starRating, helpful):
            
            
            obj = Reviews(
                names = name,
                reviewerLink = reviewLink,
                reviewTitles = title,
                reviewBody = Review,
                verifiedPurchase = Verified,
                postDate = date,
                starRating = rating,
                helpful = helpful_count
            )
            db.session.add(obj)
            db.session.commit()
      # Getting the Next Page URL for futher scraping.
            next_urls = response.css('.a-last > a::attr(href)').extract_first()
      
            yield MyItem(names=name, reviewerLink = reviewLink, reviewTitles=title, reviewBody=Review, verifiedPurchase=Verified, postDate=date, starRating=rating, helpful=helpful_count, nextPage=next_urls)
            
            next_page = response.css('.a-last > a::attr(href)').extract_first()
  # Checking if next page is not none then loop back in the same function with the next page URL.
            if next_page is not None:
                yield response.follow("https://www.amazon.com"+next_page, callback=self.parse_page)


#         @app.route("/",methods=["GET","POST"])
#         def datatest():
#             obj = Reviews.query.all()
#             if request.method == 'POST':
#                 objj= Reviews(
#                     names =  response.xpath('//div[@data-hook="review"]//span[@class="a-profile-name"]/text()').extract(),
#                     reviewerLink = response.xpath('//div[@data-hook="review"]//a[@class="a-profile"]/@href').extract(),
#                     reviewTitles = response.xpath('//a[@data-hook="review-title"]/span/text()').extract(),
#                     reviewBody = response.xpath('//span[@data-hook="review-body"]/span').xpath('normalize-space()').getall(),
#                     verifiedPurchase = response.xpath('//span[@data-hook="avp-badge"]/text()').extract(),
#                     postDate = response.xpath('//span[@data-hook="review-date"]/text()').extract(),
#                     starRating = response.xpath('//i[@data-hook="review-star-rating"]/span[@class="a-icon-alt"]/text()').extract(),
#                     helpful = response.xpath('//span[@class="cr-vote"]//span[@data-hook="helpful-vote-statement"]/text()').extract()
                        
#                 )
#                 db.session.add(objj)
#                 db.session.commit()
#                 return redirect("/")
#             return render_template("index.html", obj=obj)
        
