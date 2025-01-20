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

AuthormetriX_authorcount_modeler = st.Page(
    page = "Features/Authorcount_modeler.py",
    title = "Authorcount modeler",
    icon  = ":material/group_add:",
)
    
AuthormetriX_schema_modeler = st.Page(
    page = "Features/Schema_modeler.py",
    title = "Schema modeler",
    icon  = ":material/modeling:",
)

pg = st.navigation(pages=[Home, AuthormetriX, AuthormetriX_authorcount_modeler, AuthormetriX_schema_modeler ])
pg.run()

