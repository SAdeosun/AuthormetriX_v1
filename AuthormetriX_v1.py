import streamlit as st

#Page Setup

Home = st.Page(
    page = "Features/Home.py",
    title = "Home",
    icon  = ":material/home:",
    default = True
)

AuthormetriX = st.Page(
    page = "Features/Main.py",
    title = "Main",
    icon  = ":material/analytics:", 
)

Credit_calculator_by_author_count = st.Page(
    page = "Features/Credit_calculator_by_author_count.py",
    title = "Credit Calculator by Author Count",
    icon  = ":material/group_add:",
)
    
Credit_calculator_by_schema = st.Page(
    page = "Features/Credit_calculator_by_schema.py",
    title = "Credit Calculator by Schema",
    icon  = ":material/modeling:",
)

pg = st.navigation(pages=[Home, AuthormetriX, Credit_calculator_by_author_count, Credit_calculator_by_schema ])
pg.run()

