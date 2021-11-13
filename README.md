# jc_apra



# heroku deployment

n.b. this app requires the https://github.com/heroku/heroku-geo-buildpack.git buildpack

`heroku buildpacks:set https://github.com/heroku/heroku-geo-buildpack.git`


1. update requirements.txt

`pip3 list --format=freeze > requirements.txt`

2. add to commit and commit and push to git

'git add requirements.txt
git commit -m 'updated requirements'
git push'

3. deploy to heroku also
`git push heroku main`

