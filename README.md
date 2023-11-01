# Text-to-SQL
This project explores the **text-to-SQL** task, which focuses on the development of natural language interfaces for querying relational databases.

# Table of contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Experiments and Results](#experiments_results)
    1. [WikiSQL Benchmark](#wikisql_benchmark)
    2. [Evaluation](#evaluation)
    3. [Train and Evaluate](#train_evaluate)
4. [Text-to-SQL Website](#website)

# Overview <a name="overview"></a>

A **natural language interface to a database (NLIDB)** is a system having as input a query of a user expressed in a natural language (e.g., English), and as output the 
corresponding query expressed in a database query language (e.g., SQL). A NLIDB system enables users to retrieve information from a database, without requiring technical 
expertise or prior knowledge of database query languages. **Text-to-SQL** is a specific application of the NLIDB problem, where the goal is to convert the query of a user 
expressed in a natural language (usually English) into the corresponding query expressed in the Structured Query Language (SQL).

To achieve this objective, this project introduces six machine learning models specifically designed for text-to-SQL tasks. These models are built upon two large-language 
text-to-text models, namely [Google T5](https://arxiv.org/abs/1910.10683) and [Google CodeT5](https://arxiv.org/pdf/2109.00859.pdf). The proposed models are trained on 
[WikiSQL](https://github.com/salesforce/WikiSQL), a widely used benchmark dataset for the text-to-SQL task.

In order to evaluate the proposed text-to-SQL models, the **logical form accuracy** and **execution accuracy**, which are WikiSQL specific evaluation metrics, in addition to the 
[ROUGE-2](https://www.researchgate.net/publication/224890821_ROUGE_A_Package_for_Automatic_Evaluation_of_summaries) metrics (i.e., precision, recall, and f-measure), are 
computed. The top-performing model achieves a ROUGE-2 precision of **91.25%**, with a logical form accuracy of **74.20%** and an execution accuracy of **81.66%**.

# Architecture <a name="architecture"></a>

As already mentioned, the six machine learning models that are proposed in this project are built upon two large-language text-to-text models, namely [Google T5](https://arxiv.org/abs/1910.10683) 
and [Google CodeT5](https://arxiv.org/pdf/2109.00859.pdf). The main idea here is recognizing the importance of the table schema during the translation and comprehension of natural 
language queries. The project proposes the incorporation of additional table-related features into the models, namely the table column names and data types. Consequently, the models exhibit an 
enhanced ability to comprehend the underlying structure of the table associated with a given natural language question. This improved understanding empowers them to generate SQL queries that more 
effectively align with the intended meaning of the query.

 <p align="center"> <img src="https://github.com/EmanuelPutura/Text-to-SQL/blob/main/assets/architecture_diagram.png" height="500"/> </p>

The proposed system will comprise of two distinct modules, namely a web application and a Python module, called the text-to-SQL module. The web application, which serves as the main module, 
will provide features related to the text-to-SQL task outlined in this project. The text-to-SQL module will consist of the architectures of the machine learning models, experiments and metrics.
This module consists of several other submodules, including a model training module, a model predictions storage module, a WikiSQL evaluation module, and a query encoding and decoding module. 

# Experiments and Results <a name="experiments_results"></a>

## WikiSQL Benchmark <a name="wikisql_benchmark"></a>

The evaluation strategy proposed in the original [WikiSQL paper](https://arxiv.org/abs/1709.00103) relies mainly on two metrics: **logical form accuracy** and **execution accuracy**.

Let ***N*** be the size of the WikiSQL dataset, i.e., the total number of natural language queries that have to be translated to their corresponding SQL query. Additionally, consider ***N<sub>lf</sub>*** 
to be the number of generated SQL queries that have an exact string match with the corresponding ground truth query, and let ***N<sub>ex</sub>*** be the number of generated SQL queries that, when 
executed, result in the correct result. Then, the **logical form accuracy** is defined as

$$
Acc_{lf} = \frac{N_{lf}}{N}
$$

and the execution accuracy formula is given by 

$$
Acc_{ex} = \frac{N_{ex}}{N}
$$

A drawback of the logical form accuracy is that it incorrectly penalizes queries that yield correct results, but do not precisely match the ground truth query in string format. Obviously, 
for a given natural language query, there might exist multiple corresponding SQL queries that could be generated. However, a limitation of the execution accuracy metric is that it is possible 
to generate a query that does not accurately reflect the meaning of the question, yet still produces the correct result. The logical form accuracy and the execution accuracy are employed in 
the evaluation strategies used for the models proposed in this thesis. While both of these metrics have several downsides, when used together they offer a good understanding of the performance 
of a specific text-to-SQL model.

## Evaluation <a name="evaluation"></a>

The below table presents the ROUGE-2 and WikiSQL accuracy metrics for each of these models. The metrics encompass precision, recall, f-measure, logical form accuracy, and execution accuracy, 
offering a detailed assessment of the models’ capabilities across multiple evaluation criteria.

| **Model** | **Precision** | **Recall** | **F-measure** | **Acc<sub>lf</sub>** | **Acc<sub>ex</sub>** |
|---|---|---|---|---|---|
| CodeT5-ColNameAware | 0.9125 | 0.8541 | 0.8777 | 0.7420 | 0.8166 |
| CodeT5-ColNameTypeAware | 0.9051 | 0.8482 | 0.8711 | 0.7315 | 0.8050 |
| T5-ColNameTypeAware | 0.8827 | 0.7914 | 0.8274 | 0.5841 | 0.6436 |
| T5-ColNameAware | 0.8635 | 0.7717 | 0.8079 | 0.5337 | 0.5876 |
| CodeT5-Baseline | 0.8449 | 0.7846 | 0.8087 | 0.4688 | 0.5238 |
| T5-Baseline | 0.8184 | 0.7261 | 0.7624 | 0.3494 | 0.3909 |

The results indicate that models incorporating table schema-related features, such as column names
and types, exhibit superior performance. The models are arranged in descending order based on their execution accuracy.

## Train and Evaluate <a name="train_evaluate"></a>

The model training script can be executed using the following command, where the ```–base-model``` argument represents the base model used for fine-tuning, ```–input-format-class``` represents 
the class name of the specific pretrained model input format, and ```–pretrained-path``` is the path where the resulted model is stored after the training:

```sh
 $ python train.py −−base−model {t5, code−t5} −−input−format−class INPUT FORMAT CLASS −−pretrained−path PRETRAINED PATH
```

The predictions storage module script can be executed using the following command, where the ```–input-format-class``` argument represents the class name of the specific pretrained model input 
format, ```–file-path``` represents the path of the file where to store the predictions, and ```–pretrained-path``` is the path where the resulted model is stored after the training:

```sh
 $ python store predictions.py −−input−format−class INPUT FORMAT CLASS −−file−path FILE PATH −−pretrained−path PRETRAINED PATH
```

The model evaluation script can be executed using the following command, where the ```–predictions-path``` argument represents the path to the predictions file used for evaluating the model:

```sh
 $ python wikisql_eval.py −−predictions−path PREDICTIONS PATH
```

# Text-to-SQL Website <a name="website"></a>

A simple website is developed to showcase the models, using a **Flask** backend and an **Angular** frontend.

 <p align="center"> <img src="https://github.com/EmanuelPutura/Text-to-SQL/blob/main/assets/website.png" height="500"/> </p>
