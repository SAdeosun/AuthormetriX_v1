import streamlit as st

st.image("images_and_videos/schema1.jpg")

st.markdown("**Citation**  \n**Adeosun SO.** *AuthormetriX: Automated Calculation of Individual Authors’ Non-Inflationary Credit-Allocation Schemas’ and Collaboration Metrics from a Scopus Corpus.* **bioRxiv** 2025.01.19.633820; doi: https://doi.org/10.1101/2025.01.19.633820")
st.markdown("**Schema modeler function**  \n*Models credit allocation using multiple schemas for a specified total number of authors (authorcount).*")

import pandas as pd
import plotly.express as px

st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)
n = st.number_input("Specify total number of authors", min_value=2, max_value=50, value=2)
st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)

#Schema 1.2  Fractional with last author emphasis (LAE), then equal credits thereafter
def calculate_fractional_LAE (n):
  if n == 1:
    return 1.0
  else:
    last_LAE = 0.5
    other_LAE = [(0.5)/(n-1) for _ in range(n-1)]
    return  other_LAE + [last_LAE]


#Schema 1.3  Fractional with first author emphasis (FAE), then equal credits thereafter
def calculate_fractional_FAE (n):
  if n == 1:
    return 1.0
  else:
    first_FAE = 0.5
    other_FAE = [(0.5)/(n-1) for _ in range(n-1)]
    return [first_FAE] + other_FAE

#Schema 1.4  First and last authors emphasis (FLAE) then equal credits thereafter; first and last author get at least 0.4 credits
#This is exactly consistent with Credit13_Abramo et al 2013 from Xu et al., 2016
def calculate_fractional_FLAE (n):
  if n == 1:
    return 1.0
  elif n == 2:
    first_FLAE = 0.5
    last_FLAE = 0.5
    return [first_FLAE] + [last_FLAE]
  elif n > 2:
    first_FLAE = 0.4
    last_FLAE = 0.4
    other_FLAE = [(0.2)/(n-2) for _ in range(n-2)]
    return [first_FLAE] + other_FLAE + [last_FLAE]
  

#Schema 2  Proportional/arithmetic credit alocation: Credit03_proportional schema in Xu et al., 2016 [arithmetic in Liu and Fand 2023]
def calculate_arithmetic(n):
  credits_arithmetic = [(2 * (1-((i + 1)/(n+1))))/n for i in range(n)]
  return credits_arithmetic

#Schema 3.1  Geometric credit alocation: Credit05_Geometric schema in Xu et al., 2016. The ratio of author i to i+1 is constant down the rank, and remains 2 regardless of total number of authors
def calculate_geometric(n):
  credits_geometric = [(2 ** (n-(i+1)))/((2**n) - 1) for i in range(n)] 
  return credits_geometric

#Schema 3.2  Geometric credit alocation with an adaptive component: Liu and Fang, 2023 [the ratio of author i to i+1 is same down the rank but decreases with increasing total number of authors]
def calculate_geometric_adaptive(n):
  if n == 1:
    return [1.0]
  else:
    adaptive_denominator = (n**(n/(n-1)))-1
    credits_geometric_a = [(n**(1/(n-1))-1)*n**((n-(i+1))/(n-1))/adaptive_denominator for i in range(n)] 
    return credits_geometric_a

#Schema 4.1  Harmonic credit alocation based on the standard schema
def calculate_harmonic_standard(n):
  credits_std = [1 / (i + 1) for i in range(n)] #numerator in formula, i.e 1/r for each position
  total_credits_std = sum(credits_std) # sum of all reciprocals of each position, i.e 1/1 + 1/2 + 1/3 +...1/N, The nature of this formula needs "normalization"
  normalized_credits_std = [credit / total_credits_std for credit in credits_std]
  return normalized_credits_std

#Schema 4.2 TRUE Harmonic parabolic credit alocation based on the correct formula for the harmonic parabolic schema that I came up with since Sundlin 2023 is neither harmonic nor parabolic.
def calculate_harmonic_parabolic(n):
  symetrical_harmonic_credits = [1 / min((i + 1), (n+1-(i+1))) for i in range(n)] #I intentionaly did not further simplify the formula 
  #but kept the standard python i+1 in the second expression inside the min() method; it could have been (n-i)
  total_symetrical_harmonic_credits = sum(symetrical_harmonic_credits) # sum of all credits; needed for normalization to 1
  normalized_credits_par = [credit / total_symetrical_harmonic_credits for credit in symetrical_harmonic_credits]
  return normalized_credits_par

#Called Arithmetic_V because this formular (originally from Aziz and Rozing, 2003) named harmonic parabolic by Sundling, 2023 turns out to be neither harmonic nor parabolic.
def calculate_arithmetic_V(n):
    if n == 1:
        return [1.0]
    authors = [ i+1 for i in range (n)]
    # Calculate the harmonic series for the middle authors
    h_par_denominator_even = (0.5*(n**2)) + (n)
    h_par_denominator_odd = (0.5*(n**2)) + (n*(1-(1/(2*n))))
    if n % 2 == 0:
      normalized_credits_par = [(1 + abs(n+1-(2*(i+1))))/h_par_denominator_even for i in range (n)]
    else:
      normalized_credits_par = [(1 + abs(n+1-(2*(i+1))))/h_par_denominator_odd for i in range (n)]
    return normalized_credits_par

#Schema 4.3 Harmonic credit alocation with first and last author emphasis.
#This is different from parabolic which is symmetric around the middle; here, first and last authors get more credits than in harmonic_parabolic
def calculate_harmonic_FLAE(n):
    if n == 1:
        return [1.0]
    FLAE_credits = [1 / (i + 1) for i in range(n)]
    FLAE_denominator = sum(FLAE_credits)
    first_FLAE = [1.5/(2*FLAE_denominator)]
    last_FLAE = [1.5/(2*FLAE_denominator)]
    middle_FLAE = [(1 / (i + 2))/FLAE_denominator for i in range(1, n - 1)]
    all_normalized_credits_FLAE = first_FLAE + middle_FLAE + last_FLAE
    return all_normalized_credits_FLAE

#Schema 4.4  Golden share credit alocation (this one gives the highest credit proportion [0.62] to the first author.) Assimakis & Adam 2010 eq #28; 
# another simpler formula(which I initially used) is available in Xu et al., J. Infor Sci. 2022 eq#11)
def calculate_golden_share(n):
  if n == 1:
    return [1]
  elif n > 1:
    credits_gold = [0.618**(2*(i+1)-1) for i in range(n-1)]
    credits_gold_last = [0.618**(2*(n)-2)]
    return credits_gold + credits_gold_last



def model_credit_allocations (n):
  df = pd.DataFrame ({'author': [ i+1 for i in range (n)]})
  df['fractional_equal'] = [1/n for i in range (n)] #Function 1.1
  df['fractional_LAE'] = calculate_fractional_LAE(n)
  df['fractional_FAE'] = calculate_fractional_FAE(n)
  df['fractional_FLAE'] = calculate_fractional_FLAE(n)
  df['arithmetic_standard'] = calculate_arithmetic(n)
  df['arithmetic_V'] = calculate_arithmetic_V(n)
  df['golden_share'] = calculate_golden_share(n)
  df['geometric_standard'] = calculate_geometric(n)
  df['geometric_adaptive'] = calculate_geometric_adaptive(n)
  df['harmonic_standard'] = calculate_harmonic_standard(n)
  df['harmonic_FLAE'] = calculate_harmonic_FLAE(n)
  df['harmonic_parabolic'] = calculate_harmonic_parabolic(n)
  
  
  
  return df


df = model_credit_allocations (n)
st.write ("#####  Credit-allocation Data Table")
#st.markdown ("*To download the table from which the credit allocations plot is derived, toggle the 'Show credit-allocation data table' on, then hover over the top right corner of the table, and click the download button.*")
table_on = st.toggle("Show credit-allocation data table")
if table_on:
   st.write(df)
   #st.download_button('Download data as CSV', df.to_csv(index=False).encode('utf-8'), file_name='credit_allocation_data.csv', mime='text/csv')
   st.markdown("**NOTE:** *Very low numbers (<0.0001) are displayed as 0 in the table. Double-click the cell to see the full number. Numbers are shown in full in the downloaded table.*")

st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)

df_melt = pd.melt(df, id_vars=['author'], var_name='Schema', value_name='Credit_allocated')
df_melt['Author'] = df_melt['author'].astype(str)

#st.write (df_melt)
schemas = df.columns.tolist()[1:]
default_schemas = ['fractional_equal', 'arithmetic_standard', 'geometric_standard', 'harmonic_standard']
st.write ("#####  Credit-allocation Plot")
schemas_to_plot = st.multiselect('Select schemas to display in the plot (add from the drop down list)', schemas, default=default_schemas)

df_melt_filtered = df_melt[df_melt['Schema'].isin(schemas_to_plot)]
fig = px.line(df_melt_filtered, x='Author', y='Credit_allocated', color='Schema', markers = True)
fig.update_yaxes(title_text = 'Author Credit', tick0=0, dtick=0.1, range=[0,0.7])
st.plotly_chart(fig, use_container_width=True)

st.markdown("""<hr style="height:4px;border:none;color:#fe8100;background-color:#fe8100;" />""", unsafe_allow_html=True)
st.markdown ("*Thank you for using ***AuthormetriX***.    Kindly remember to cite the publication (full citation above).*",unsafe_allow_html=True)