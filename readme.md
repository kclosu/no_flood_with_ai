# An example solution to the no_flood_with_ai_2020 contest

### What information is contained in this repository?
* [Jupyter notebook](https://github.com/kclosu/no_flood_with_ai/blob/main/no_floods_with_ai.ipynb)  that contains the steps of implementing a predictive model and has any descriptive comments that would help explain the working of the submitted solution
* [Dockerfile](https://github.com/kclosu/no_flood_with_ai/blob/main/Dockerfile) and [forecast.py](https://github.com/kclosu/no_flood_with_ai/blob/main/forecast.py) that are needed to run your machine learning code
*  [Abstracts](https://github.com/kclosu/no_flood_with_ai/blob/main/abstracts.pdf) describing the approach


### The testing process
```
docker build -t no_flood_with_ai .
docker run --volume $(pwd)/datasets:/usr/src/app/datasets no_flood_with_ai 2020-10-11 2020-10-21
```
Note, you don't need to include datasets in a docker image.

As you can see, docker container runs with command line parameters that specifies the start and end of the period of data forecasts.
