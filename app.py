import dash
import numpy as np
from dash import dcc
from dash import html,Output,Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from bs4 import BeautifulSoup
import requests
import matplotlib.pyplot as plt
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
navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink("Home", href="/",active="exact",className="bi bi-house-door-fill p-2")),
        dbc.NavItem(dbc.NavLink("Page 1",active="exact", href="/Page1")),

        
    ],
    brand="JobAssist",
    brand_href="#",
    color="LimeGreen",
    dark=True,style={'font-weight':'bold'}
)


CONTENT_STYLE = {
    "padding": "0rem 0rem",
    "background-color":"black"
}
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP,dbc.icons.BOOTSTRAP])
content = html.Div(id="page-content",children=[] ,style=CONTENT_STYLE)

#components
table=dbc.Table.from_dataframe(jobdf, striped=True, bordered=True, hover=True,dark=True)
jobpiegraph=html.Div(dcc.Graph(figure=px.pie(piearraydf,values="Count",color="Jobs",names="Jobs",hole=0.5,color_discrete_map={'Easy Apply':'#1D741B','Not Easy Apply':'LimeGreen'}).update_layout({'font_color':'white','plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)'})),className="card bg-dark")
Locationgraph=html.Div(dcc.Graph(figure=px.scatter(jobdf,y='Companies',x="Location").update_xaxes(showgrid=False).update_yaxes(showgrid=False).update_layout({'font_color':'white','plot_bgcolor': 'rgba(0, 0, 0, 0)',
'paper_bgcolor': 'rgba(0, 0, 0, 0)'})),className="card bg-dark")

app.layout = html.Div([dcc.Location(id="url"),navbar,content])
                              
@app.callback(Output("page-content", "children"), [Input("url", "pathname")])
def render_page_content(pathname):
    if pathname=="/":
        return [dbc.Container([dbc.Row([dbc.Col([html.H4("Jobs Posted 24 Hrs Ago",style={'font-weight':'bold','color':'LimeGreen'},className="bi bi-clock-fill p-2"),table]),dbc.Col([html.H5("Easy Apply V/S Non Easy Apply Jobs",style={'font-weight':'bold','color':'LimeGreen'},className="p-2"),jobpiegraph,html.H5("Jobs Location Distribution",style={'font-weight':'bold','color':'DodgerBlue'},className="p-2"),Locationgraph,html.H5("Average Company Rating Today",style={'font-weight':'bold','color':'Gold'},className="p-2"),html.Div(html.H5(f"{'%.2f'%meanrating}",style={'font-weight':'bold','color':'Gold','margin-left':'20px'},className="p-3 bi bi-star-fill"),className="card bg-dark")])])]
                              
                              )]
if __name__=="__main__":
    app.run_server(port=8050)

