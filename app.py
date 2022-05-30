from flask import Flask, request, jsonify, make_response
from distanceCalc import DistanceCalculation
import pyproj
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)

#Data Pre-processing
counties = pd.read_csv("data/Counties_-_OSi_National_Placenames_Gazetteer.csv")
townlands = pd.read_csv("data/Townlands_-_OSi_National_Placenames_Gazetteer.csv")
townlands = townlands[['County', 'English_Name', 'Alternative_Name','ITM_E','ITM_N']]
counties = counties[['County', 'English_Name','Alternative_Name', 'ITM_E','ITM_N']]
townlands['County'] = townlands['County'].str.lower()
townlands['English_Name'] = townlands['English_Name'].str.lower()
counties['County'] = counties['County'].str.lower()
counties['English_Name'] = counties['English_Name'].str.lower()



@app.errorhandler(500)
def handle_500_error(error):
    """Retrun a 500 http status code"""
    return make_response(jsonify({"error":{"code":"500",
                                            "message": "Internal Server Error"}}), 500) 
                                            
@app.errorhandler(404)
def handle_404_error(error):
    """Return a 404 http status code"""
    return make_response(jsonify({"error":{"code":"404",
                                            "message": "Page Not Found"}}), 404) 

@app.route('/geocoder', methods=['GET'])
def geocoder(): 
    """Returns latitude and longitude for the input address
        Params - address"""  
    address = request.args.get('address')
    if (not address) or (len(address)==0):
        return make_response(jsonify({"error":{"code":"400",
                                        "message": "Bad Request - Enter Valid Address"}}), 400)  
    d = DistanceCalculation() 
    townland=''
    county = ''
    temp=''
    addresssplit = address.lower().split(',')
    if(len(addresssplit))<2:
        addresssplit = address.lower().split(' ')
    iplist = []
    ratio = 0
    res = pd.DataFrame()
    for i in addresssplit:
        iplist.append(i.strip())
    for c in counties['English_Name']:
        for i in iplist:
            if(d.levenshteinDistanceRatio(c,i)>ratio and d.levenshteinDistanceRatio(c,i)>0.8):
                county = c
                temp = i

    if (not county) or (len(county)==0):
        return make_response(jsonify({"error":{"code":"400",
                                            "message": "Bad Request - Enter Valid Address"}}), 400)  
    if county:
        iplist.remove(temp)
        townland_df = townlands.loc[(townlands['County'] == county)]
        for a in townland_df['English_Name']:
            for i in iplist:
                if(d.levenshteinDistanceRatio(i,a)>ratio):
                    ratio = d.levenshteinDistanceRatio(i,a)
                    townland=a
    if (not townland) or (len(townland)==0):
        for a in townland_df['Alternate_Name']:
            for i in iplist:
                if(d.levenshteinDistanceRatio(i,a)>ratio):
                    ratio = d.levenshteinDistanceRatio(i,a)
                    townland=a
    if townland:
        res = townland_df[townland_df['English_Name']==townland].head(1)
    if (not townland) or (len(townland)==0):
        res = counties[counties['English_Name']==county].head(1)
    wgs84 = pyproj.Proj(projparams = 'epsg:4326')
    InputGrid = pyproj.Proj(projparams = 'epsg:2157')
    latlong = pyproj.transform(InputGrid, wgs84,res.ITM_E.item(), res.ITM_N.item())
    return make_response(jsonify({"data":
                    {"address": address,
                    "ITM_N" : res.ITM_N.item(),
                    "ITM_E" : res.ITM_E.item(),
                    "Latitude" : latlong[0],
                    "Longitude": latlong[1]
                    }}),200)


if __name__ == "__main__":
    app.run(debug=True)