# jc_apra

## creating the requirements.txt

1. use `apra_deploy` conda env with python=3.8.12
e.g. `mamba create -n apra_deploy python=3.8.12`

2. install requirements
`source activate apra_deploy
pip3 install streamlit folium geopandas altair streamlit-folium openpyxl rtree`

3. update requirements.txt

`pip3 list --format=freeze > requirements.txt`

4. add to commit and commit and push to git

'git add requirements.txt
git commit -m 'updated requirements'
git push'

5. deploy to heroku also
`git push heroku main`


## heroku deployment

n.b. this app requires the https://github.com/heroku/heroku-geo-buildpack.git buildpack

`heroku buildpacks:set https://github.com/heroku/heroku-geo-buildpack.git`

n.b. GDAL fails to build this way


