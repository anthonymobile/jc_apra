# jc_apra

## running 
`streamlit run app.py`

## creating the environment.yml

1. use `apra_deploy` conda env with python=3.9
e.g. `mamba create -n apra_deploy python=3.9`

2. install requirements
`conda activate apra_deploy
pip3 install streamlit folium geopandas altair streamlit-folium openpyxl rtree`

3. update environment.yml

`conda env export -f environment.yml --no-build`
