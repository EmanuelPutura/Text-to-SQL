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
