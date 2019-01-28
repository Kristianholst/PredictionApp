# PredictionApp

## Intro

This is an example of end to end machine learning project. The project shows how quick you can train a machine learning model and then host 
in production by using the flask framework as backend. I have used the income prediction dataset which is widely know open dataset used for 
teaching prediction and machine learning modelling. The data set contains data on different indivuduals like education,race, marrital status
and so on, and a label if the individual earns more or less than 50k. Using the data I have trained a model to predict how likely it is 
based on data provided if the person earns more than 50K usd.
The  dataset “adult” is found in the UCI machine learning repository http://www.cs.toronto.edu/~delve/data/adult/desc.html
and the description is located here http://www.cs.toronto.edu/~delve/data/adult/adultDetail.html. 

## SET UP:

Based on experience I have from analytics in an commercial setting(Speficially banking and insurance),
prediction models always takes input from different data sources. Some are self reported by the individual, others are supplied from internal databases and
thirdly some are fetched by third party data suppliers through for example through apis.
Therefore I have taken the typical commercial set up and aimed to create a model that takes input from different sources, with of course
the complexity that arises with this set up. To do this I looked at the variables available in the income dataset and choosen with some
thought what is usually self reported and what might be available in a database(public information or tax info supplied with the
consent of the individual)

The self reported variables are:

| Self reported|
|--------------|
|"pid" (personal id)|
|"hours-per-week" |
|"relationship"|
|"occupation":|
|workclass| 

WORK IN PROGRESS

