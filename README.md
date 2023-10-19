# Text-to-SQL
This project explores the **text-to-SQL** task, which focuses on the development of natural language interfaces for querying relational databases.

A natural language interface to a database (NLIDB) is a system having as input a query of a user expressed in a natural language (e.g., English), and as output the 
corresponding query expressed in a database query language (e.g., SQL). A NLIDB system enables users to retrieve information from a database, without requiring technical 
expertise or prior knowledge of database query languages. Text-to-SQL is a specific application of the NLIDB problem, where the goal is to convert the query of a user 
expressed in a natural language (usually English) into the corresponding query expressed in the Structured Query Language (SQL).

To achieve this objective, this project introduces six machine learning models specifically designed for text-to-SQL tasks. These models are built upon two large-language 
text-to-text models, namely [Google T5](https://arxiv.org/abs/1910.10683) and [Google CodeT5](https://arxiv.org/pdf/2109.00859.pdf). The proposed models are trained on 
[WikiSQL](https://github.com/salesforce/WikiSQL), a widely used benchmark dataset for the text-to-SQL task.

In order to evaluate the proposed text-to-SQL models, the **logical form accuracy** and **execution accuracy**, which are WikiSQL specific evaluation metrics, in addition to the 
[ROUGE-2](https://www.researchgate.net/publication/224890821_ROUGE_A_Package_for_Automatic_Evaluation_of_summaries) metrics (i.e., precision, recall, and f-measure), are 
computed. The top-performing model achieves a ROUGE-2 precision of **91.25%**, with a logical form accuracy of **74.20%** and an execution accuracy of **81.66%**.

# Architecture

As already mentioned, the six machine learning models that are proposed in this project are built upon two large-language text-to-text models, namely [Google T5](https://arxiv.org/abs/1910.10683) 
and [Google CodeT5](https://arxiv.org/pdf/2109.00859.pdf). The main idea here is recognizing the importance of the table schema during the translation and comprehension of natural 
language queries. The project proposes the incorporation of additional table-related features into the models, namely the table column names and data types. Consequently, the models exhibit an 
enhanced ability to comprehend the underlying structure of the table associated with a given natural language question. This improved understanding empowers them to generate SQL queries that more 
effectively align with the intended meaning of the query.

The proposed system will comprise of two distinct modules, namely a web application and a Python module, called the text-to-SQL module. The web application, which serves as the main module, 
will provide features related to the text-to-SQL task outlined in this project. The text-to-SQL module will consist of the architectures of the machine learning models, experiments and metrics.
This module consists of several other submodules, including a model training module, a model predictions storage module, a WikiSQL evaluation module, and a query encoding and decoding module. 

 <p align="center"> <img src="https://github.com/EmanuelPutura/Text-to-SQL/blob/main/assets/architecture_diagram.png" height="500"/> </p>
