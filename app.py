import dash
import numpy as np
from dash import dcc
from dash import html,Output,Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from bs4 import BeautifulSoup
import requests
from statistics import mean
#Data Scraping
url="https://www.glassdoor.co.in/Job/jobs.htm?fromAge=1"
r=requests.get(url)
htmlcontent=r.content
soup = BeautifulSoup(htmlcontent, 'html.parser')
jobdata=[]
payamt=[]
spantxt=[]
comname=[]
locname=[]
easycount=[]
nonreview=[]
reviewscore=[]
#Easy Apply
easyapply=soup.find_all("div",class_="css-pxdlb2")
for ezapply in easyapply:
    easycount.append(ezapply.find("div").get_text())

#job titles
companyname=soup.find_all("a",class_="css-l2wjgv e1n63ojh0 jobLink")
for name in companyname:
    comname.append(name.find("span").get_text())
    jobdata.append({'Company Name':comname})



#salaries today
payscale=soup.find_all("div",class_="css-3g3psg pr-xxsm")
for txt in payscale:
    payamt.append(txt.find("span",class_="css-1xe2xww e1wijj242").get_text())
    # jobdata.append({'payscale':payamt})


#job titles today
jobtodaytxt=soup.find_all("a",class_="jobLink css-1rd3saf eigr9kq2")
for jobtodaytxt in jobtodaytxt:
    spantxt.append(jobtodaytxt.find("span").get_text())
    # jobdata.append({'jobtitles':spantxt})#getting job titles

#job location
location=soup.find_all("div",class_="d-flex flex-wrap css-11d3uq0 e1rrn5ka2")
for loc in location:
    locname.append(loc.find("span",class_="css-3g3psg pr-xxsm css-iii9i8 e1rrn5ka0").get_text())





for i in payamt:
    jobdf=pd.DataFrame(data={'Companies':comname,'Job Titles':spantxt,'Location':locname}) #dataframe for bootstrap table

#getting total count of easy apply
counttotaleasyapply=easycount.count('Easy Apply')
remcount=len(jobdf)-counttotaleasyapply
piearray=np.array([counttotaleasyapply,remcount])
piearraydf=pd.DataFrame(data={'Jobs':['Easy Apply','Not Easy Apply'],'Count':[counttotaleasyapply,remcount]})


#scraping google search and calculating average company reviews
for i in comname:
    googleurl=f"https://www.google.com/search?q={i}"
    r=requests.get(googleurl,headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) '\
           'AppleWebKit/537.36 (KHTML, like Gecko) '\
           'Chrome/75.0.3770.80 Safari/537.36'})
    htmlcontent=r.content
    soup = BeautifulSoup(htmlcontent, 'html.parser')
    reviewrating=soup.find("span",class_="Aq14fc")
    if reviewrating is None:
       nonreview.append(reviewrating)
    elif reviewrating is not None:
        reviewscore.append(reviewrating.get_text())

reviewscore=list(map(float,reviewscore))
meanrating=mean(reviewscore)        



CONTENT_STYLE = {
    "padding": "0rem 0rem",
    "background-color":"black"
}
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.icons.BOOTSTRAP])
content = html.Div(id="page-content",children=[] ,style=CONTENT_STYLE)
server=app.server
#components
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/",active="exact",className="bi bi-house-door-fill p-2")),
        dbc.NavItem(dbc.NavLink("Upskill",active="exact", href="/upskill",className="bi bi-book-fill p-2")),

        
    ],
    brand="JobAssist",
    brand_href="#",
    color="LimeGreen",
    dark=True,style={'font-weight':'bold'}
)

table=dbc.Table.from_dataframe(jobdf, striped=True, bordered=True, hover=True,dark=True)


jobpiegraph=html.Div(dcc.Graph(figure=px.pie(piearraydf,values="Count",color="Jobs",names="Jobs",hole=0.5,color_discrete_map={'Easy Apply':'#1D741B','Not Easy Apply':'LimeGreen'}).update_layout({'font_color':'white','plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)'})),className="card bg-dark")


Locationgraph=html.Div(dcc.Graph(figure=px.scatter(jobdf,y='Companies',x="Location").update_xaxes(showgrid=False).update_yaxes(showgrid=False).update_layout({'font_color':'white','plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)'})),className="card bg-dark")

searchbar=dbc.Input(id="input",debounce=True, placeholder="Type the skills you wanna learn (your search term should end with course)", type="text",className="bi bi-search"),dbc.FormText("SkillAssist helps you with finding online courses",color="LimeGreen",style={'font-weight':'600'})

app.layout = html.Div([dcc.Location(id="url"),navbar,content])
                              
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname=="/":
        return [dbc.Container([dbc.Row([dbc.Col([html.H4("Jobs Posted 24 Hrs Ago",style={'font-weight':'bold','color':'LimeGreen'},className="bi bi-clock-fill p-2"),table]),dbc.Col([html.H5("Easy Apply V/S Non Easy Apply Jobs",style={'font-weight':'bold','color':'LimeGreen'},className="p-2"),jobpiegraph,html.H5("Jobs Location Distribution",style={'font-weight':'bold','color':'DodgerBlue'},className="p-2"),Locationgraph,html.H5("Average Company Rating Today",style={'font-weight':'bold','color':'Gold'},className="p-2"),html.Div(html.H5(f"{'%.2f'%meanrating}",style={'font-weight':'bold','color':'Gold','margin-left':'20px'},className="p-3 bi bi-star-fill"),className="card bg-dark")])])]
                              
                              )]
    elif pathname=="/upskill":
        return [dbc.Container([dbc.Col([html.Div(searchbar),dbc.Row([dbc.Col([html.H2("Youtube Courses & Infotainment",style={'color':'Crimson','margin-top':'20px'}),html.Div(id="output")]),dbc.Col([html.Div([html.H5("Average Views for this course",style={'font-weight':'bold'},className="p-2"),html.H5(id='views',style={'font-weight':'bold','color':'Crimson'},className="p-2 bi bi-bar-chart-line-fill")],className="card"),html.H5("View Distribution",style={'font-weight':'bold','color':'Crimson','margin-top':'30px'}),dcc.Graph(figure={},id="tmp")])])])])]

#plotting graphs
@app.callback([Output("views", "children"),Output("tmp", "figure")], [Input("input", "value")])
def update_figure(value):
    if value is not None:
     urllist=[]
    uploadlist=[]
    viewlist=[]
    titlelist=[]
    url = "https://simple-youtube-search.p.rapidapi.com/search"

    querystring = {"query":f"{value}","safesearch":"false"}

    headers = {
	"X-RapidAPI-Key": "3cf87b7362mshb0aa4e5238acaaep139e9ajsn60193dcabdd2",
	"X-RapidAPI-Host": "simple-youtube-search.p.rapidapi.com"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    data=response.json()

    for i in data['results']:
     urllinks=i["url"] #get urls
     urllist.append(urllinks)
     uploaddate=i["uploadedAt"]#upload date
     uploadlist.append(uploaddate)
     views=i["views"]#get no of views
     viewlist.append(views)
     title=i["title"]#get title
     titlelist.append(title)
    df=pd.DataFrame({'links':urllinks,'date':uploaddate,'views':viewlist,'videotitle':titlelist})
    print(df)
    
    views=df["views"].mean()
    return '%.2f'%views,px.treemap(df,path=["videotitle","views"],values="views",color="views",color_continuous_scale='reds',template="plotly_dark")

    
#searchbar and data scrape
@app.callback(Output("output", "children"), [Input("input", "value")])
def output_text(value):
    if value is not None:
     urllist=[]
    uploadlist=[]
    viewlist=[]
    titlelist=[]
    url = "https://simple-youtube-search.p.rapidapi.com/search"

    querystring = {"query":f"{value}","safesearch":"false"}

    headers = {
	"X-RapidAPI-Key": "3cf87b7362mshb0aa4e5238acaaep139e9ajsn60193dcabdd2",
	"X-RapidAPI-Host": "simple-youtube-search.p.rapidapi.com"}

    response = requests.request("GET", url, headers=headers, params=querystring)
    data=response.json()

    for i in data['results']:
     urllinks=i["url"] #get urls
     urllist.append(urllinks)
     uploaddate=i["uploadedAt"]#upload date
     uploadlist.append(uploaddate)
     views=i["views"]#get no of views
     viewlist.append(views)
     title=i["title"]#get title
     titlelist.append(title)
    df=pd.DataFrame({'links':urllinks,'date':uploaddate,'views':viewlist,'videotitle':titlelist})
    print(df) 
    
    return [dbc.Card(
    [
        dbc.CardBody(
            [
                html.H4(row['videotitle'], className="card-title"),
                dbc.Row([html.H6(row['views'],className="bi bi-eye-fill",style={'color':'Crimson'}),html.H6(row['date'],className="bi bi-calendar-fill",style={'color':'Crimson'})]),
                dbc.Button("Start the course", color="danger",href=row['links']),
            ]
        ),
    ],
    style={"width": "18rem",'padding':'5px','margin-top':'30px'},
)  for index,row in df.iterrows()
]            
if __name__=="__main__":
    app.run_server(port=8050)

# dbc.Card(
#     [
#         dbc.CardImg(src="/static/images/placeholder286x180.png", top=True),
#         dbc.CardBody(
#             [
#                 html.H4("Card title", className="card-title"),
#                 html.P(
#                     "Some quick example text to build on the card title and "
#                     "make up the bulk of the card's content.",
#                     className="card-text",
#                 ),
#                 dbc.Button("Go somewhere", color="primary"),
#             ]
#         ),
#     ],
#     style={"width": "18rem"},
# )
