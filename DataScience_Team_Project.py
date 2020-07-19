#!/usr/bin/env python
# coding: utf-8

# In[4]:


import pandas as pd
import numpy as np
import io
import warnings
from sklearn import linear_model
from sklearn import preprocessing
warnings.filterwarnings(action='ignore')
from matplotlib import pyplot as plt
from sklearn.tree import DecisionTreeClassifier, export_graphviz
from sklearn.model_selection import train_test_split
import pydot
import xlsxwriter
from sklearn.tree import DecisionTreeClassifier
from math import log

from sklearn.ensemble import AdaBoostClassifier
from sklearn import datasets
from sklearn import metrics
import sklearn.linear_model as lm
from sklearn.neighbors import KNeighborsClassifier

df= pd.read_csv('C:\\Users\\Jaewook_Cha\\Desktop\\Electronic_Police_Report_2018.csv', encoding='utf-8')

##Drop the not using column
del df['Hate_Crime']## has no meaning all empty value
del df['Signal_Type']## not usnig signal type relations with crime
del df['Location']## using District Column instead of location
del df['Item_Number']##Not using because not relations the crime it just report number
del df['Charge_Code']## not usnig analysist the crime
##df=df[::][df['Offender_Race']!=NaN]
df=df[::][df["Offender_Race"].isnull()==False][df['Offender_Age'].isnull()==False][df['Offender_Gender'].isnull()==False]
df=df[::][df["Victim_Race"].isnull()==False][df['Victim_Age'].isnull()==False][df['Victim_Gender'].isnull()==False]
df=df[::][df['Offender_Age']>=10][df['Offender_Age']<100]
df=df[::][df['Victim_Age']>=10][df['Victim_Age']<100]
#df['Victim_Age'][df['Victim_Age']>0]=np.mean(df['Victim_Age'])
df['Offender_Race'][df['Offender_Race']=='UNKNOWN']=df['Offender_Race'].mode()[0]
df['Victim_Race'][df['Victim_Race']=='UNKNOWN']=df['Victim_Race'].mode()[0]
# Add columns for decision tree
df['Offender_Race'][df['Offender_Race']=='UNKNOWN']=df['Offender_Race'].mode()[0]
df['Victim_Race'][df['Victim_Race']=='UNKNOWN']=df['Victim_Race'].mode()[0]
df['THEFT_OR_NOT']=df['Signal_Description'][df['Signal_Description']=='THEFT']
df['THEFT_OR_NOT']=df['THEFT_OR_NOT']=='THEFT'



# Separate Occured_Date_Time by month
test = df['Occurred_Date_Time']
data_jan=test[test.str.match('2018-01')]
data_feb=test[test.str.match('2018-02')]
data_march=test[test.str.match('2018-03')]
data_april=test[test.str.match('2018-04')]
data_may=test[test.str.match('2018-05')]
data_june=test[test.str.match('2018-06')]
data_july=test[test.str.match('2018-07')]
data_aug=test[test.str.match('2018-08')]
data_sep=test[test.str.match('2018-09')]
data_oct=test[test.str.match('2018-10')]
data_nov=test[test.str.match('2018-11')]
data_dec=test[test.str.match('2018-12')]

# Make data to the categorical data(Race, Gender, Report type, Fatal)
enc=preprocessing.OrdinalEncoder()
enc2=preprocessing.OrdinalEncoder()
enc3=preprocessing.OrdinalEncoder()
enc4=preprocessing.OrdinalEncoder()
R=[['BLACK'],['ASIAN'],['HISPANIC'],['WHITE'], ['AMER. IND.']]
enc.fit(R)
G=[['MALE'],['FEMALE']]
enc2.fit(G)
F=[['Non-fatal'],['Fatal']]
enc3.fit(F)
T=[['Incident Report'],['Supplemental Report']]
enc4.fit(T)

# Apply categorical data to original dataset
df.at[:,['Offender_Race']]=enc.transform(df.loc[:,['Offender_Race']])
df.at[:,'Victim_Race']=enc.transform(df.loc[:,['Victim_Race']])
df.at[:,['Offender_Gender']]=enc2.transform(df.loc[:,['Offender_Gender']])
df.at[:,'Victim_Gender']=enc2.transform(df.loc[:,['Victim_Gender']])
df.at[:,'Victim_Fatal_Status']=enc3.transform(df.loc[:,['Victim_Fatal_Status']])
df.at[:,'Report_Type']=enc4.transform(df.loc[:,['Report_Type']])

# Dicritizatoin Age by group( 10 period)
df['Victim_AgeGroup']=0
df.loc[(df['Victim_Age']>=10)&(df['Victim_Age']<20),'Victim_AgeGroup']=10
df.loc[(df['Victim_Age']>=20)&(df['Victim_Age']<30),'Victim_AgeGroup']=20
df.loc[(df['Victim_Age']>=30)&(df['Victim_Age']<40),'Victim_AgeGroup']=30
df.loc[(df['Victim_Age']>=40)&(df['Victim_Age']<50),'Victim_AgeGroup']=40
df.loc[(df['Victim_Age']>=50)&(df['Victim_Age']<60),'Victim_AgeGroup']=50
df.loc[(df['Victim_Age']>=60)&(df['Victim_Age']<70),'Victim_AgeGroup']=60
df.loc[(df['Victim_Age']>=70)&(df['Victim_Age']<80),'Victim_AgeGroup']=70
df.loc[(df['Victim_Age']>=80)&(df['Victim_Age']<90),'Victim_AgeGroup']=80
df.loc[(df['Victim_Age']>=90)&(df['Victim_Age']<100),'Victim_AgeGroup']=90

df['Offender_AgeGroup']=0
df.loc[(df['Offender_Age']>=10)&(df['Offender_Age']<20),'Offender_AgeGroup']=10
df.loc[(df['Offender_Age']>=20)&(df['Offender_Age']<30),'Offender_AgeGroup']=20
df.loc[(df['Offender_Age']>=30)&(df['Offender_Age']<40),'Offender_AgeGroup']=30
df.loc[(df['Offender_Age']>=40)&(df['Offender_Age']<50),'Offender_AgeGroup']=40
df.loc[(df['Offender_Age']>=50)&(df['Offender_Age']<60),'Offender_AgeGroup']=50
df.loc[(df['Offender_Age']>=60)&(df['Offender_Age']<70),'Offender_AgeGroup']=60
df.loc[(df['Offender_Age']>=70)&(df['Offender_Age']<80),'Offender_AgeGroup']=70
df.loc[(df['Offender_Age']>=80)&(df['Offender_Age']<90),'Offender_AgeGroup']=80
df.loc[(df['Offender_Age']>=90)&(df['Offender_Age']<100),'Offender_AgeGroup']=90


base=df['Signal_Description'][df['Signal_Description']=='THEFT'].count()

##Select 2 columns(Offender_Age & Victime_Age) because we want to know these relationship and detect outlier
X = df['Offender_Age'].values[:,np.newaxis]
Y = df['Victim_Age'].values
##Create object for linear regression
E = lm.LinearRegression()
##Set x,y label
plt.xlabel("Offender age")
plt.ylabel("Victim age")
##Fit linear model
E.fit(X,Y)
plt.scatter(X,Y,color='red')
##When drawing line, E.predict(X) means prediction using the linear model
plt.plot(X,E.predict(X),color='blue')
plt.show()

test1 = df[['Occurred_Date_Time','Victim_Fatal_Status']]
##change the Date XXXX-XX-XX-> just get month.
test1.loc[df.Occurred_Date_Time.str.contains('2018-01',na=False)]=1
test1.loc[df.Occurred_Date_Time.str.contains('2018-02',na=False)]=2
test1.loc[df.Occurred_Date_Time.str.contains('2018-03',na=False)]=3
test1.loc[df.Occurred_Date_Time.str.contains('2018-04',na=False)]=4
test1.loc[df.Occurred_Date_Time.str.contains('2018-05',na=False)]=5
test1.loc[df.Occurred_Date_Time.str.contains('2018-06',na=False)]=6
test1.loc[df.Occurred_Date_Time.str.contains('2018-07',na=False)]=7
test1.loc[df.Occurred_Date_Time.str.contains('2018-08',na=False)]=8
test1.loc[df.Occurred_Date_Time.str.contains('2018-09',na=False)]=9
test1.loc[df.Occurred_Date_Time.str.contains('2018-10',na=False)]=10
test1.loc[df.Occurred_Date_Time.str.contains('2018-11',na=False)]=11
test1.loc[df.Occurred_Date_Time.str.contains('2018-12',na=False)]=12

## using the histogram library to check the when crime happens
plt.hist(test1['Occurred_Date_Time'],bins=[1,2,3,4,5,6,7,8,9,10,11,12])
plt.title("histogram of result")
plt.xticks([1,2,3,4,5,6,7,8,9,10,11,12])## January~December
plt.xlabel('Date')
plt.ylabel('Crime')
plt.show()## display the histogram

##Make test frame to compare the after the clearing data
test = df[['Occurred_Date_Time','Victim_Fatal_Status']]
test.loc[df.Occurred_Date_Time.str.contains('2018-01',na=False)]=1
test.loc[df.Occurred_Date_Time.str.contains('2018-02',na=False)]=2
test.loc[df.Occurred_Date_Time.str.contains('2018-03',na=False)]=3
test.loc[df.Occurred_Date_Time.str.contains('2018-04',na=False)]=4
test.loc[df.Occurred_Date_Time.str.contains('2018-05',na=False)]=5
test.loc[df.Occurred_Date_Time.str.contains('2018-06',na=False)]=6
test.loc[df.Occurred_Date_Time.str.contains('2018-07',na=False)]=7
test.loc[df.Occurred_Date_Time.str.contains('2018-08',na=False)]=8
test.loc[df.Occurred_Date_Time.str.contains('2018-09',na=False)]=9
test.loc[df.Occurred_Date_Time.str.contains('2018-10',na=False)]=10
test.loc[df.Occurred_Date_Time.str.contains('2018-11',na=False)]=11
test.loc[df.Occurred_Date_Time.str.contains('2018-12',na=False)]=12


## make histogram x has date and y is bin value of crime
plt.hist(test['Occurred_Date_Time'],bins=[1,2,3,4,5,6,7,8,9,10,11,12])
plt.title("histogram of result")
plt.xticks([1,2,3,4,5,6,7,8,9,10,11,12])
plt.xlabel('Date')
plt.ylabel('Crime')
plt.show()


##make the histogram to analysis relationship beween age and crime
a=np.array(df['Victim_Age'])
plt.hist(a,bins=[10,15,20,25,30,35,40,45,50,55,60,65,70,75])
plt.title("histogram of Victim")
plt.xticks([10,15,20,25,30,35,40,45,50,55,60,65,70,75])
plt.xlabel('Age')
plt.ylabel('number Victims')
plt.show()

##make the histogram to analysis relationship between Distrct and crime
c=np.array(df['District'])
plt.hist(c,bins=[1,2,3,4,5,6,7,8])
plt.title("District criminal")
plt.xticks([1,2,3,4,5,6,7,8])
plt.xlabel('District')
plt.ylabel('number Victims')
plt.show()

##make the Offender_Age and Victim_Age for make boxplot graph
dataSet1=df['Offender_Age']
dataSet2=df['Victim_Age']
plotData=[dataSet1,dataSet2]
plt.boxplot(plotData)
plt.show()




###################################################  Inspectoin & Preprocessing   #########################################################################





######################################################### Analysis & Evaluation Start ########################################################################

# Calculate Entropy
def Entropy(percent):
    non_percent = 1 - percent
    if percent==0:
        entropy=0
    elif percent>0:
        entropy=-((percent*log(percent,2))+(non_percent*log(non_percent,2)))
    return round(entropy,2)

# Entropy of Root node ( THEFT)
df_THEF=df['Signal_Description'][df['Signal_Description']=='THEFT']
base=df['Signal_Description'][df['Signal_Description']=='THEFT'].count()
length=len(df)
THEF_percent=base/length
THEF_percent=round(THEF_percent,2)
no_THEF_percent=1-THEF_percent
THEF_root_entropy=Entropy(THEF_percent)

# Number of people THEFT each races
df_b=df.loc[df['Signal_Description']=='THEFT',:]
#black_p=df_b.loc[df_b['Victim_Race']==1.0].count()
asian_p=df_b['Victim_Race'][df_b['Victim_Race']==0.0].count()
black_p=df_b['Victim_Race'][df_b['Victim_Race']==1.0].count()
hispanic_p=df_b['Victim_Race'][df_b['Victim_Race']==2.0].count()
ind_p=df_b['Victim_Race'][df_b['Victim_Race']==3.0].count()
white_p=df_b['Victim_Race'][df_b['Victim_Race']==4.0].count()

asian_op=df_b['Offender_Race'][df_b['Offender_Race']==0.0].count()
black_op=df_b['Offender_Race'][df_b['Offender_Race']==1.0].count()
hispanic_op=df_b['Offender_Race'][df_b['Offender_Race']==2.0].count()
ind_op=df_b['Offender_Race'][df_b['Offender_Race']==3.0].count()
white_op=df_b['Offender_Race'][df_b['Offender_Race']==4.0].count()
print()

## Get entropy(Victim_Race)
black_percent=black_p/base
black_percent=round(black_percent,2)
non_black_percent=1-black_percent
black_entropy=Entropy(black_percent)

ind_percent=ind_p/base
ind_percent=round(ind_percent,2)
non_ind_percent=1-ind_percent
ind_entropy=Entropy(ind_percent)

white_percent=white_p/base
white_percent=round(white_percent,2)
non_white_percent=1-white_percent
white_entropy=Entropy(white_percent)

asian_percent=asian_p/base
asian_percent=round(asian_percent,3)
non_asian_percent=1-asian_percent
asian_entropy=Entropy(asian_percent)

hispanic_percent=hispanic_p/base
hispanic_percent=round(hispanic_percent,2)
non_hispanic_percent=1-hispanic_percent
hispanic_entropy=Entropy(hispanic_percent)

print("Victim_Race Entorpy")
print('Asian entropy ',asian_entropy)
print('Black entropy ',black_entropy)
print('Hispanic entropy ',hispanic_entropy)
print('Ind entropy ',ind_entropy)
print('White entropy ',white_entropy)

list2=['Asian','Black','Hispanic','Indian','White']
gain2=[asian_entropy, black_entropy, hispanic_entropy, ind_entropy, white_entropy]
plt.bar(list2,gain2)
plt.show()

THEF_info_gain=THEF_root_entropy-((asian_p*asian_entropy)+(black_p*black_entropy)+(hispanic_p*hispanic_entropy)+(ind_p*ind_entropy)+(white_p*white_entropy))/base
percent=round(base/length,2)  ## THEFT percent



print("==============================================")
## Get entropy(Offender_Race)
asian_percent_o=asian_op/base
asian_percent_o=round(asian_percent_o,2)
non_asian_percent_o=1-asian_percent_o
asian_entropy_o=Entropy(asian_percent_o)

black_percent_o=black_op/base
black_percent_o=round(black_percent_o,2)
non_black_percent_o=1-black_percent_o
black_entropy_o=Entropy(black_percent_o)

hispanic_percent_o=hispanic_op/base
hispanic_percent_o=round(hispanic_percent_o,2)
non_hispanic_percent_o=1-hispanic_percent_o
hispanic_entropy_o=Entropy(hispanic_percent_o)

ind_percent_o=ind_op/base
ind_percent_o=round(ind_percent_o,2)
non_ind_percent_o=1-ind_percent_o
ind_entropy_o=Entropy(ind_percent_o)

white_percent_o=white_op/base
white_percent_o=round(white_percent_o,2)
non_white_percent_o=1-white_percent_o
white_entropy_o=Entropy(white_percent_o)

print("Offender_Race entropy")
print("Asian entropy",asian_entropy_o)
print("Black entropy",black_percent_o)
print('Hispanic entropy',hispanic_entropy_o)
print('Ind entropy',ind_entropy_o)
print('White entropy',white_entropy_o)

Offender_Race_info=THEF_root_entropy-((asian_op*asian_entropy_o)+(black_op*black_percent_o)+(hispanic_op*hispanic_entropy_o)+(ind_op*ind_entropy_o)
                                      +(white_op*white_entropy_o))/base

# Number of Victim agegroup for decision tree
v_10=df_b['Victim_AgeGroup'][df_b['Victim_AgeGroup']==10].count()
v_20=df_b['Victim_AgeGroup'][df_b['Victim_AgeGroup']==20].count()
v_30=df_b['Victim_AgeGroup'][df_b['Victim_AgeGroup']==30].count()
v_40=df_b['Victim_AgeGroup'][df_b['Victim_AgeGroup']==40].count()
v_50=df_b['Victim_AgeGroup'][df_b['Victim_AgeGroup']==50].count()
v_60=df_b['Victim_AgeGroup'][df_b['Victim_AgeGroup']==60].count()
v_70=df_b['Victim_AgeGroup'][df_b['Victim_AgeGroup']==70].count()
v_80=df_b['Victim_AgeGroup'][df_b['Victim_AgeGroup']==80].count()
v_90=df_b['Victim_AgeGroup'][df_b['Victim_AgeGroup']==90].count()
# Get entropy of Victim
v_10_ent=Entropy(v_10/base)
v_20_ent=Entropy(v_20/base)
v_30_ent=Entropy(v_30/base)
v_40_ent=Entropy(v_40/base)
v_50_ent=Entropy(v_50/base)
v_60_ent = Entropy(v_60 / base)
v_70_ent = Entropy(v_70 / base)
v_80_ent = Entropy(v_80 / base)
v_90_ent = Entropy(v_90 / base)

Victim_Age_info=THEF_root_entropy-(((v_10*v_10_ent)+(v_20*v_20_ent)+(v_30*v_30_ent)+(v_40*v_40_ent)+(v_50*v_50_ent)+(v_60*v_60_ent)+(v_70*v_70_ent)+(v_80*v_80_ent)+(v_90*v_90_ent))/base)

# Number of Offender agegroup for decision tree
o_10=df_b['Offender_AgeGroup'][df_b['Offender_AgeGroup']==10].count()
o_20=df_b['Offender_AgeGroup'][df_b['Offender_AgeGroup']==20].count()
o_30=df_b['Offender_AgeGroup'][df_b['Offender_AgeGroup']==30].count()
o_40=df_b['Offender_AgeGroup'][df_b['Offender_AgeGroup']==40].count()
o_50=df_b['Offender_AgeGroup'][df_b['Offender_AgeGroup']==50].count()
o_60=df_b['Offender_AgeGroup'][df_b['Offender_AgeGroup']==60].count()
o_70=df_b['Offender_AgeGroup'][df_b['Offender_AgeGroup']==70].count()
o_80=df_b['Offender_AgeGroup'][df_b['Offender_AgeGroup']==80].count()
o_90=df_b['Offender_AgeGroup'][df_b['Offender_AgeGroup']==90].count()

o_10_ent=Entropy(o_10/base)
o_20_ent=Entropy(o_20/base)
o_30_ent=Entropy(o_30/base)
o_40_ent=Entropy(o_40/base)
o_50_ent=Entropy(o_50/base)
o_60_ent = Entropy(o_60 / base)
o_70_ent = Entropy(o_70 / base)
o_80_ent = Entropy(o_80 / base)
o_90_ent = Entropy(o_90 / base)
Offender_Age_info=(THEF_root_entropy)-(((o_10*o_10_ent)+(o_20*o_20_ent)+(o_30*o_30_ent)+(o_40*o_40_ent)+(o_50*o_50_ent)+(o_60*o_60_ent)+(o_70*o_70_ent)+(o_80*o_80_ent)+(o_90*o_90_ent))/base)
Offender_Age_info= -Offender_Age_info
Offender_Race_info= -Offender_Race_info
Victim_Age_info= -Victim_Age_info
THEF_info_gain= -THEF_info_gain
tail=int(length*0.3)
df_test=df.tail(tail)

print("=======================THEFT Information Gain=============================")
print('Offender_Age Information gain: ',Offender_Age_info)
print('Offender_Race Information gain: ',Offender_Race_info)
print('Victim_Age Information gain: ',Victim_Age_info)
print('VIctim_Race Information gain: ',THEF_info_gain)

# Compare Information gain
list3=['Offender_Age','Offender_Race','Victim_Age','Victim_Race']
gain=[Offender_Age_info,Offender_Race_info,Victim_Age_info, THEF_info_gain]
plt.bar(list3,gain)
plt.show()

###### Decision tree accuracy by importing library#####

# Data rearrange for decision tree library
X = df.drop('THEFT_OR_NOT',axis=1)
Y = df ['THEFT_OR_NOT']
data = pd.get_dummies(X[['Offender_Race','Offender_Age','Victim_Race','Victim_Age']])
X_train, X_test, Y_train, Y_test  =  train_test_split(data,Y, test_size=0.3, random_state=1)
model = DecisionTreeClassifier(criterion='entropy',random_state=1)
model.fit(X_train,Y_train)
prediction = model.predict(X_test)

#calculate accuracy
print("Test set size = 30% ")
print("Decision Tree Accuracy rate : ",model.score(X_test,Y_test),"%")


### Adaboost for decision tree###
X_train,X_test,y_train,y_test=train_test_split(data,Y,test_size=0.3)
abc=AdaBoostClassifier(n_estimators=50, learning_rate=1)
model=abc.fit(X_train,y_train)
y_pred=model.predict(X_test)
print("Ada Boost Accuracy (decision tree) : ",metrics.accuracy_score(y_test,y_pred),'%')

################################################## Decision Tree #################################################################




########################################### KNN  Start  ################################################################################


## make the trainData to analysis the relationships of Persontype, Vicim_Age, Victim_Race with Victim_Gender
trainData=df[['Person_Type','Victim_Age','Victim_Race','Victim_Gender']]
## ordering the index
trainData=trainData.reset_index(drop=True)

##Start of KNN
le=preprocessing.LabelEncoder()

##Fitting the element to training it
Age_encoded=le.fit_transform(trainData['Victim_Age'])
print(Age_encoded)
Type_encoded=le.fit_transform(trainData['Person_Type'])
print(Type_encoded)
Race_encoded=le.fit_transform(trainData['Victim_Race'])
print(Race_encoded)

##make the knn test DataFrame and column has 'Race', 'Type', 'Age'
knn_test={'Race':[0],'Type':[0],'Age':[0]}
knn_test['Race']=Race_encoded
knn_test['Type']=Type_encoded
knn_test['Age']=Age_encoded

##Make the list feautres to train in KNN library
features=list1(zip(Age_encoded,Type_encoded,Race_encoded))
features=pd.DataFrame(features)

##Label to compare the result
label=le.fit_transform(trainData['Victim_Gender'])


##set the size if 5
model=KNeighborsClassifier(n_neighbors=5)
model.fit(features,label)

##set the using column 0,1,2=Race, Type, Age
predicted=model.predict([[0,1,2]])


## Mkae the train set and test set
X_train,X_test,y_train,y_test=train_test_split(features,label,test_size=0.3)


knn=KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train,y_train)
## using the test set then get predict value
y_pred=knn.predict(X_test)

## show the kneignbor is 5

print('KNN is 5')
print("KNN Accuracy:",metrics.accuracy_score(y_test,y_pred))

X_train,X_test,y_train,y_test=train_test_split(features,label,test_size=0.3)
## add the Adat boost and check the accuray addition
abc=AdaBoostClassifier(n_estimators=50, learning_rate=1)
model=abc.fit(X_train,y_train)
y_pred=model.predict(X_test)
print("Ada Boost Accuracy : ",metrics.accuracy_score(y_test,y_pred))


## compare the reuslt with neighbor is 5
knn=KNeighborsClassifier(n_neighbors=7,weights='distance')
knn.fit(X_train,y_train)
y_pred=knn.predict(X_test)

import matplotlib

print('KNN is 7')
print("KNN Accuracy:",metrics.accuracy_score(y_test,y_pred))

X_train,X_test,y_train,y_test=train_test_split(features,label,test_size=0.3)

abc=AdaBoostClassifier(n_estimators=50, learning_rate=1)
model=abc.fit(X_train,y_train)

y_pred=model.predict(X_test)
print("Ada Boost Accuracy : ",metrics.accuracy_score(y_test,y_pred))






# In[ ]:




