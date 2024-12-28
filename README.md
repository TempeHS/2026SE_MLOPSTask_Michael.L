# Practical Application of NESA Software Engineering MLOps

This Jupyter Notebook collection is designed to support students understand Machine learning operations (MLOps) and it's practical processes as defined in the [NESA Software Engineering Course Specifications](https://library.curriculum.nsw.edu.au/341419dc-8ec2-0289-7225-6db7f2d751ef/94e1eb0a-0df7-4dbe-9b72-5d5e0d17143a/software-engineering-11-12-higher-school-certificate-course-specifications.PDF) pg 27.

![Course Specification MLOps Model](/images/MLOPS_Model.png)

> [!TIP]
> This a corrected version of the MLOps course specification. It is important that students see this model as an omnidirectional multi loop cycle. Particularly in the 'Model Development' stage, students should expect to loop through the cycle many times before having a model ready for the operations stage. Or that it is likely they will identify a design problem and cycle back in to the 'Design' stage, loop through it, then move forward and again loop repeatedly through the 'Model Development' stage.

## 1. Design

https://www.wisdomgeek.com/development/data-science/converting-business-problem-machine-learning/

1. Defining the business problem to be solved

   - Doctors often under estimate the progress of type II adult onset diabetes after diagnosis. Often resulting in the insufficient medical interventions and reduced health outcomes for patients.

   - Doctors would like a valid and reliable tool for doctors to be able to enter an individuals health data and be provided with a valid and reliable prediction of the disease progression over the patients next 12 months.

2. Refactoring the business problem into a machine learning problem

   - _Students to refactor the provided business problem_

3. Defining success metrics

   - _Students to define success metrics_

4. Researching available data.

   - Your have sourced a validated raw data set. The data is saved in the CSV file [2.1.2.Diabeties_Sample_Data.csv](/2.Model_Development/2.1.Data_Wrangling/2.1.2.Diabeties_Sample_Data.csv).

     > [!Important]
     > The information and ranges provided below are to help students understand the domain of the data, it is not intended as medical or diagnostic advice.

   - The data columns are:

     | Column | Data                                                                                                                                                                                                                                                                                                 |
     | ------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
     | DoB    | The patients Date of Birth recorded as D/MM/YYYY                                                                                                                                                                                                                                                     |
     | DoT    | The patients date of testing records as D/MM/YYYY                                                                                                                                                                                                                                                    |
     | SEX    | Patients gender ---                                                                                                                                                                                                                                                                                  |
     | BMI,   | Patients body mass index, which gives an indication of the patients body size and is calculated using their weight and height ---                                                                                                                                                                    |
     | BP     | Diastole blood pressure which is the pressure of blood on the walls of the patients arteries when their heart was relaxed. <80 is desirable, 80-95 is high >95 is very high.                                                                                                                         |
     | TC     | Total cholesterol is a measure of the cholesterol in the patients body. Cholesterol is essential in order for your body to continue building healthy cells, however having high cholesterol can increase your risk of heart disease. <5.5 is desirable 5.5-6.6 is borderline and >6.5 is undesirable |
     | BGU    | Patients fasting blood glucose levels. 75-99 is desirable and 100+ is undesirable.                                                                                                                                                                                                                   |
     | FDR    | The number of family members in the individuals direct bloodline who have developed type 2 adult onset diabetes.                                                                                                                                                                                     |
     | Target | A quantitative measure of disease progression one year after baseline. Patients should aim towards `0` as this means the condition has not progressed further.                                                                                                                                       |

     > [!Note]
     > This is a [real data set](https://www4.stat.ncsu.edu/~boos/var.select/diabetes.html) used in [real statistical medical research](https://imjohnstone.su.domains/WEBLIST/2004/LarsAnnStat04.pdf) that has been modified for the purposes of teaching data wrangling and feature engineering.

## 2. Model Development

### 2.1 Data Wrangling

1. The [Understand The Data Demonstration](/2.Model_Development/2.1.Data_Wrangling/2.1.1.data_preview.ipynb) provides a demonstration of a basic data wrangling (also called data preprocessing) using the Pandas library and Matplotlib. To understand your dataset using snapshots, data summaries, graphs and descriptive statistics.
2. The [Data Wrangling Demonstration](/2.Model_Development/2.1.Data_Wrangling/2.1.2.data_wranglish.ipynb) provides a demonstration of more advanced data wrangling. To clean and prepare the data for feature engineering and model training, ensuring that it is in a usable format.

### 2.2 Feature Engineering

1. The [Feature Engineering Demonstration](/2.Model_Development/2.2.Feature_Engineering/2.2.1.feature_engineering.ipynb) provides a demonstration on enhancing the data set by creating new features or modifying existing ones to improve model performance.

### 2.3 Model Training

1. The [Raw Demonstration](/2.Model_Development/2.3.Model_Training/2.3.1.raw_course_specification.ipynb) of the course specification provides a direct application (after debugging) of each step of the algorithm.

   > [!Note]
   > There are some variations from the NESA course specifications to address syntax errors, missing methods and readability.

2. The [Graphical Demonstration](/2.Model_Development/2.3.Model_Training/2.3.2.graphical_course_specification.ipynb) of the course specifications provides graphs visualising each step of the algorithm.
3. The [CSV Demonstration](/2.Model_Development/2.3.Model_Training/2.3.3.CSV_course_specification.ipynb) of the course specifications uses a CSV upload of the data so larger model training data sets can be used.
4. The [SQL Demonstration](/2.Model_Development/2.3.Model_Training/2.3.4.SQL_course_specification.ipynb) of the course specifications imports the data from a SQL database so the data can be managed in a database.

### 2.4 Model Testing and Validation

1. The [Model Testing and Validation Demonstration](/2.Model_Development/2.4.Model_Testing_and_Validation/2.4.1.model_test_and_validate.ipynb) provides a number of ways to evaluate, test and validate your model using a second set of test data and then refine your model. This demonstration uses a different regression algorithm to the course specifications.

## Operations

### Deploying a Model

1. The [Model Deployment](/3.Operations/3.1.Deploy_Model/3.1.1.Basic_Model_Depolyment.ipynb) exports the model so a separate Python implementation can use it to make predictions. The demonstration also includes how to save a Matplotlib image so it can be used in a UI or served by an API.

   - Versioning
   - Continuous Deployment (CD)

2. Supporting operations/use

   - Continuous Integration (CI)

3. Monitoring model performance.

   - Continuous Testing (CT)

## Metalanguage

| Metalanguage        | Definition |
| ------------------- | ---------- |
| Linear Regression   | ----       |
| Feature             | ----       |
| Target              | ----       |
| Prediction          | ----       |
| Data wrangling      | ----       |
| Data preprocessing  | ----       |
| Feature Engineering | ----       |
| Cost                | ----       |
| Mean                | ----       |
| Mode                | ----       |
| Range               | ----       |
| Standard Deviation  | ----       |

<p xmlns:cc="http://creativecommons.org/ns#" xmlns:dct="http://purl.org/dc/terms/"><a property="dct:title" rel="cc:attributionURL" href="https://github.com/TempeHS/Practical-Application-of-NESA-Software-Engineering-MLOps">Practical Application of NESA Software Engineering MLOps</a> by <a rel="cc:attributionURL dct:creator" property="cc:attributionName" href="https://github.com/benpaddlejones">Ben Jones</a> is licensed under <a href="https://creativecommons.org/licenses/by-nc-sa/4.0/?ref=chooser-v1" target="_blank" rel="license noopener noreferrer" style="display:inline-block; ">Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International<img style="height:22px!important; margin-left:3px; vertical-align:text-bottom; " src="https://mirrors.creativecommons.org/presskit/icons/cc.svg?ref=chooser-v1" alt=""><img style="height:22px!important; margin-left:3px; vertical-align:text-bottom; " src="https://mirrors.creativecommons.org/presskit/icons/by.svg?ref=chooser-v1" alt=""><img style="height:22px!important; margin-left:3px; vertical-align:text-bottom; " src="https://mirrors.creativecommons.org/presskit/icons/nc.svg?ref=chooser-v1" alt=""><img style="height:22px!important; margin-left:3px; vertical-align:text-bottom; " src="https://mirrors.creativecommons.org/presskit/icons/sa.svg?ref=chooser-v1" alt=""></a></p>
