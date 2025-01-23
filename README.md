The application can be found here https://sadeosun-a-uthormetrix-v1.streamlit.app/

The accompanying publication can be found here: https://www.biorxiv.org/content/10.1101/2025.01.19.633820v1

**Overview**
  
**Background**: Publication count is the currency in academia, but the most widely used whole count method is considered unfair and inflationary. Several non-inflationary author credit-allocation schemas (NIACAS) have been proposed, but none is widely adopted in practice (e.g., in evaluating faculty scholarly productivity) or in bibliometric research. This low adoption and implementation rate may be due to the complexity in operationalizing the schemas. 

**Aim**: To develop an application that automates the calculation of individual authors' scholarly output metrics based on multiple NIACAS. 

**Method**: Published formulas of NIACAS were written as Python functions wrapped in a Streamlit user interface that takes *.csv* files of the relevant corpus, and a list of author's Scopus IDs as inputs. The functions calculate the authors' output metrics based on NIACAS including first- and last-author straight counts, arithmetic, golden share, and multiple variations of fractional, geometric, and harmonic schemas. Collaboration metrics are also calculated. Secondary features include modelers for author counts and schemas. In a use-case, absolute rank displacement (ARD) and actual contribution proportions (ACP) were compared between highly cited clinical medicine researchers and high h-index pharmacy practice faculty populations. 

**Results**: AuthormetriX accurately calculates individual authors' aggregate scholarly output based on 14 NIACAS, from the file inputs. There were schema and population differences in ACP, but only schema differences in ARD within the populations studied. 

**Conclusions**: AuthormetriX simplifies the implementation of non-inflationary author credit-allocation schemas and will facilitate their broader adoption in practice and bibliometric research.
